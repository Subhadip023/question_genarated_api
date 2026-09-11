"""Business logic for test-series management."""

from collections import defaultdict
import secrets
import hashlib
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.constants.attempt_status import AttemptStatus
from app.controllers.question_controller import QuestionController
from app.models.batch import Batch
from app.models.batch_student import BatchStudent
from app.models.diagram import Diagram
from app.models.organization_user import OrganizationUser
from app.models.question import Question
from app.models.series_question import SeriesQuestion
from app.models.teacher_group import TeacherGroup
from app.models.test_attempt import TestAttempt
from app.models.test_access import TestAccess
from app.models.test_series import TestSeries
from app.models.user import User
from app.schemas.test_series import (
    TestSeriesCreate,
    TestSeriesResponse,
    TestSeriesResultItem,
    TestSeriesResultsResponse,
    TestSeriesUpdate,
)
from app.config import settings




class TestSeriesPermissionError(Exception):
    pass


class TestSeriesQuestionError(Exception):
    pass


class TestSeriesHasAttemptsError(Exception):
    pass


class TestSeriesController:
    @staticmethod
    def create(
        data: TestSeriesCreate,
        user_id: int,
        user_role: int,
        db: Session
    ) -> TestSeriesResponse:
        # Get organization
        if user_role == 0:
            org_id = 0

        elif user_role in (1, 2):
            membership = (
                db.query(OrganizationUser)
                .filter(
                    OrganizationUser.user_id == user_id
                )
                .order_by(OrganizationUser.org_id)
                .first()
            )

            org_id = membership.org_id if membership else 0

        else:
            raise TestSeriesPermissionError(
                "Only roles 0, 1, and 2 can create test series"
            )

        # Validate questions
        question_query = db.query(Question).filter(
            Question.id.in_(data.question_ids),
            Question.is_active.is_(True)
        )

        question_query = QuestionController._apply_visibility_filter(
            question_query,
            user_id,
            user_role,
            db
        )

        allowed_ids = {
            question.id
            for question in question_query.all()
        }

        if allowed_ids != set(data.question_ids):
            raise TestSeriesQuestionError(
                "One or more questions do not exist, are inactive, or are not accessible"
            )

        # Generate invite token only for invite_only tests
        invite_token = (
            secrets.token_urlsafe(24)
            if data.access_type == "invite_only"
            else None
        )

        # Validate teacher_group_id belongs to organization if provided
        if data.teacher_group_id is not None:
            tg = db.query(TeacherGroup).filter(TeacherGroup.id == data.teacher_group_id, TeacherGroup.is_deleted.is_(False)).first()
            if not tg:
                raise TestSeriesPermissionError("Teacher group not found")
            if org_id != 0 and tg.org_id != org_id:
                raise TestSeriesPermissionError("Teacher group must belong to the organization")

        # Validate supervisor_id belongs to organization if provided
        if data.supervisor_id is not None:
            sup = db.query(User).filter(User.id == data.supervisor_id).first()
            if not sup:
                raise TestSeriesPermissionError("Supervisor user not found")
            if org_id != 0:
                membership = db.query(OrganizationUser).filter(OrganizationUser.user_id == data.supervisor_id, OrganizationUser.org_id == org_id).first()
                if not membership:
                    raise TestSeriesPermissionError("Supervisor must belong to the organization")

        # Restrict result publishing to supervisor and admin only
        if data.is_result_show or data.is_score_show:
            is_admin = (user_role == 0) or (user_role == 1)
            is_supervisor = False
            if data.supervisor_id and data.supervisor_id == user_id:
                is_supervisor = True
            elif data.teacher_group_id:
                tg = db.query(TeacherGroup).filter(TeacherGroup.id == data.teacher_group_id, TeacherGroup.is_deleted.is_(False)).first()
                if tg and tg.supervisor == user_id:
                    is_supervisor = True

            if not (is_admin or is_supervisor):
                raise TestSeriesPermissionError("Only supervisor and admin can publish test results")

        # Create test series
        series_code = TestSeriesController._generate_unique_code(db)

        series = TestSeries(
            code=series_code,
            invite_token=invite_token,
            invite_token_hash=(
                hashlib.sha256(
                    invite_token.encode()
                ).hexdigest()
                if invite_token
                else None
            ),

            access_type=data.access_type,
            name=data.name.strip(),

            org_id=org_id,
            created_by=user_id,

            # Newly added columns
            teacher_group_id=data.teacher_group_id,
            supervisor_id=data.supervisor_id,

            valid_until=data.valid_until,
            duration_seconds=data.duration_seconds,

            is_active=data.is_active,
            is_result_show=data.is_result_show,
            is_score_show=data.is_score_show,

            series_questions=[
                SeriesQuestion(
                    question_id=question_id,
                    position=position
                )
                for position, question_id in enumerate(
                    data.question_ids,
                    start=1
                )
            ],
        )

        try:
            db.add(series)

            # Generate series.id before creating test_access
            db.flush()

            # Test access (optional batch_ids / batch_id link)
            target_batch_ids = list(data.batch_ids or [])
            if data.batch_id is not None and data.batch_id not in target_batch_ids:
                target_batch_ids.append(data.batch_id)

            target_batch_id = target_batch_ids[0] if target_batch_ids else None

            if target_batch_id is None and data.student_ids:
                new_batch = Batch(
                    org_id=org_id,
                    name=f"{series.name} Batch",
                    supervisor=user_id,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(new_batch)
                db.flush()
                target_batch_id = new_batch.id
                target_batch_ids.append(target_batch_id)
                series.batch_id = target_batch_id

            for b_id in set(target_batch_ids):
                if b_id and b_id > 0:
                    test_access = TestAccess(
                        test_series_id=series.id,
                        batch_id=b_id,
                        granted_by=user_id,
                    )
                    db.add(test_access)

            if target_batch_id and data.student_ids:
                for sid in set(data.student_ids):
                    db.add(BatchStudent(
                        batch_id=target_batch_id,
                        student_id=sid,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    ))

            db.commit()

        except Exception:
            db.rollback()
            raise

        response = TestSeriesController._get_response(
            series.id,
            db
        )

        response.invite_token = invite_token

        return response

    @staticmethod
    def update(
        series_id: int,
        data: TestSeriesUpdate,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> TestSeriesResponse | None:
        series = db.query(TestSeries).filter(TestSeries.id == series_id).first()
        if not series:
            return None

        # Verify permission
        is_admin = False
        if user_role == 0:
            is_admin = True
        elif user_role == 1:
            membership = (
                db.query(OrganizationUser)
                .filter(OrganizationUser.user_id == user_id)
                .order_by(OrganizationUser.org_id)
                .first()
            )
            if membership and membership.org_id == series.org_id:
                is_admin = True

        is_supervisor = False
        if series.supervisor_id and series.supervisor_id == user_id:
            is_supervisor = True
        elif series.teacher_group_id:
            tg = (
                db.query(TeacherGroup)
                .filter(TeacherGroup.id == series.teacher_group_id, TeacherGroup.is_deleted.is_(False))
                .first()
            )
            if tg and tg.supervisor == user_id:
                is_supervisor = True

        is_authorized = is_admin or is_supervisor or (series.created_by == user_id)

        if not is_authorized:
            raise TestSeriesPermissionError("You do not have permission to edit this test series")

        updates = data.model_dump(exclude_unset=True)

        # Restrict result publication / score visibility changes to supervisor and admin only
        if "is_result_show" in updates or "is_score_show" in updates:
            if not (is_admin or is_supervisor):
                raise TestSeriesPermissionError("Only supervisor and admin can publish or change test results visibility")
        question_ids = updates.pop("question_ids", None)

        if question_ids is not None:
            question_query = db.query(Question).filter(
                Question.id.in_(question_ids), Question.is_active.is_(True)
            )
            question_query = QuestionController._apply_visibility_filter(
                question_query, user_id, user_role, db
            )
            allowed_ids = {question.id for question in question_query.all()}
            if allowed_ids != set(question_ids):
                raise TestSeriesQuestionError(
                    "One or more questions do not exist, are inactive, or are not accessible"
                )

            # Delete existing questions association
            db.query(SeriesQuestion).filter(SeriesQuestion.series_id == series_id).delete()
            
            # Create new association
            series.series_questions = [
                SeriesQuestion(question_id=qid, position=pos)
                for pos, qid in enumerate(question_ids, start=1)
            ]

        # Validate teacher_group_id if updated
        if "teacher_group_id" in updates and updates["teacher_group_id"] is not None:
            tg_id = updates["teacher_group_id"]
            tg = db.query(TeacherGroup).filter(TeacherGroup.id == tg_id, TeacherGroup.is_deleted.is_(False)).first()
            if not tg:
                raise TestSeriesPermissionError("Teacher group not found")
            if series.org_id != 0 and tg.org_id != series.org_id:
                raise TestSeriesPermissionError("Teacher group must belong to the organization")

        # Validate supervisor_id if updated
        if "supervisor_id" in updates and updates["supervisor_id"] is not None:
            sup_id = updates["supervisor_id"]
            sup = db.query(User).filter(User.id == sup_id).first()
            if not sup:
                raise TestSeriesPermissionError("Supervisor user not found")
            if series.org_id != 0:
                membership = db.query(OrganizationUser).filter(OrganizationUser.user_id == sup_id, OrganizationUser.org_id == series.org_id).first()
                if not membership:
                    raise TestSeriesPermissionError("Supervisor must belong to the organization")

        student_ids = updates.pop("student_ids", None)
        has_batch_id_update = "batch_id" in updates
        batch_id_val = updates.pop("batch_id", None) if has_batch_id_update else None

        for field, value in updates.items():
            if field in ("teacher_group_id", "supervisor_id"):
                setattr(series, field, value)
            elif value is not None:
                setattr(series, field, value)

        # Handle batch_ids / batch_id / student_ids updates
        has_batch_update = "batch_ids" in updates or "batch_id" in updates
        if has_batch_update:
            new_batch_ids = []
            if "batch_ids" in updates:
                raw_ids = updates.pop("batch_ids")
                if raw_ids:
                    new_batch_ids.extend([b for b in raw_ids if b and b > 0])
            if "batch_id" in updates:
                b_id = updates.pop("batch_id")
                if b_id and b_id > 0 and b_id not in new_batch_ids:
                    new_batch_ids.append(b_id)

            new_batch_ids = list(set(new_batch_ids))

            db.query(TestAccess).filter(TestAccess.test_series_id == series_id).delete()
            for b_id in new_batch_ids:
                db.add(TestAccess(test_series_id=series_id, batch_id=b_id, granted_by=user_id))

            series.batch_id = new_batch_ids[0] if new_batch_ids else None
            target_batch_id = series.batch_id
        else:
            target_batch_id = getattr(series, "batch_id", None)
            if not target_batch_id:
                access = db.query(TestAccess.batch_id).filter(TestAccess.test_series_id == series_id).first()
                if access:
                    target_batch_id = access[0]

        if student_ids is not None:
            if not target_batch_id:
                new_batch = Batch(
                    org_id=series.org_id,
                    name=f"{series.name} Batch",
                    supervisor=user_id,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(new_batch)
                db.flush()
                target_batch_id = new_batch.id
                series.batch_id = target_batch_id
                db.add(TestAccess(test_series_id=series_id, batch_id=target_batch_id, granted_by=user_id))

            if target_batch_id:
                existing_bs = db.query(BatchStudent).filter(BatchStudent.batch_id == target_batch_id).all()
                existing_student_ids = {bs.student_id for bs in existing_bs}
                target_student_ids = set(student_ids)

                to_remove = existing_student_ids - target_student_ids
                if to_remove:
                    db.query(BatchStudent).filter(
                        BatchStudent.batch_id == target_batch_id,
                        BatchStudent.student_id.in_(to_remove)
                    ).delete(synchronize_session=False)

                to_add = target_student_ids - existing_student_ids
                for sid in to_add:
                    db.add(BatchStudent(
                        batch_id=target_batch_id,
                        student_id=sid,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    ))

        # Handle invite token hash when access type changes or regeneration requested
        invite_token = None
        regenerate = updates.pop("regenerate_invite_token", False)
        next_access_type = updates.get("access_type", series.access_type)

        if next_access_type == "invite_only":
            if not series.invite_token or regenerate or (updates.get("access_type") == "invite_only" and not series.invite_token_hash):
                invite_token = secrets.token_urlsafe(24)
                series.invite_token = invite_token
                series.invite_token_hash = hashlib.sha256(invite_token.encode()).hexdigest()
            else:
                invite_token = series.invite_token
        elif "access_type" in updates and updates["access_type"] != "invite_only":
            series.invite_token = None
            series.invite_token_hash = None

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        response = TestSeriesController._get_response(series.id, db)
        if invite_token:
            response.invite_token = invite_token
        return response

    @staticmethod
    def delete(series_id: int, user_id: int, db: Session) -> bool:
        series = db.query(TestSeries).filter(TestSeries.id == series_id).first()
        if series is None:
            return False

        if series.created_by != user_id:
            raise TestSeriesPermissionError(
                "Only the user who created this test series can delete it"
            )

        has_attempts = (
            db.query(TestAttempt.id)
            .filter(TestAttempt.series_id == series_id)
            .first()
            is not None
        )
        if has_attempts:
            raise TestSeriesHasAttemptsError(
                "Test series with existing attempts cannot be deleted"
            )

        try:
            db.delete(series)
            db.commit()
        except Exception:
            db.rollback()
            raise
        return True

    @staticmethod
    def list_for_user(user_id: int, user_role: int, db: Session) -> list[TestSeriesResponse]:
        query = db.query(TestSeries).options(joinedload(TestSeries.series_questions))
        query = TestSeriesController._apply_visibility(query, user_id, user_role, db)
        items = query.all()
        series_ids = [item.id for item in items]

        attempt_counts = {}
        batch_ids_map = defaultdict(list)
        if series_ids:
            counts = (
                db.query(TestAttempt.series_id, func.count(TestAttempt.id))
                .filter(TestAttempt.series_id.in_(series_ids))
                .group_by(TestAttempt.series_id)
                .all()
            )
            attempt_counts = dict(counts)

            access_records = (
                db.query(TestAccess.test_series_id, TestAccess.batch_id)
                .filter(TestAccess.test_series_id.in_(series_ids))
                .all()
            )
            for s_id, b_id in access_records:
                batch_ids_map[s_id].append(b_id)

        return [
            TestSeriesController._serialize(
                item,
                db=db,
                attempt_count=attempt_counts.get(item.id, 0),
                batch_ids=batch_ids_map.get(item.id, []),
            )
            for item in items
        ]

    @staticmethod
    def get_for_user(
        series_id: int, user_id: int, user_role: int, db: Session
    ) -> TestSeriesResponse | None:
        query = db.query(TestSeries).filter(TestSeries.id == series_id)
        query = TestSeriesController._apply_visibility(query, user_id, user_role, db)
        item = query.options(joinedload(TestSeries.series_questions)).first()
        if not item:
            return None
        count = (
            db.query(func.count(TestAttempt.id))
            .filter(TestAttempt.series_id == series_id)
            .scalar()
            or 0
        )
        return TestSeriesController._serialize(item, db=db, attempt_count=count)

    @staticmethod
    def _apply_visibility(query, user_id: int, user_role: int, db: Session):
        role_int = int(user_role)
        if role_int == 0:
            return query
        elif role_int == 1:
            membership = (
                db.query(OrganizationUser)
                .filter(OrganizationUser.user_id == user_id)
                .order_by(OrganizationUser.org_id)
                .first()
            )
            org_id = membership.org_id if membership else 0
            return query.filter(TestSeries.org_id == org_id)
        elif role_int == 2:
            return query.filter(TestSeries.created_by == user_id)

        return query.filter(False)

    @staticmethod
    def get_results(
        series_id: int, user_id: int, user_role: int, db: Session
    ) -> TestSeriesResultsResponse:
        series = TestSeriesController.get_for_user(series_id, user_id, user_role, db)
        if series is None:
            raise TestSeriesPermissionError("Test series not found or access denied")

        attempts = (
            db.query(TestAttempt, User)
            .join(User, TestAttempt.user_id == User.id)
            .filter(TestAttempt.series_id == series_id)
            .order_by(TestAttempt.started_at.desc())
            .all()
        )

        items = []
        completed_scores = []
        for attempt, user in attempts:
            score_val = float(attempt.score or 0)
            total_val = float(attempt.total_marks or 0)
            pct = (
                round((score_val / total_val) * 100, 2)
                if total_val > 0
                else 0.0
            )

            status_val = str(
                attempt.status.value
                if hasattr(attempt.status, "value")
                else (attempt.status if attempt.status is not None else 0)
            )

            is_completed = (
                attempt.status in (AttemptStatus.SUBMITTED, AttemptStatus.FORCE_SUBMITTED, 2, 3, "2", "3", "submitted", "force_submitted")
                or status_val in ("2", "3", "submitted", "force_submitted")
            )
            if is_completed:
                completed_scores.append(score_val)

            items.append(
                TestSeriesResultItem(
                    attempt_id=attempt.id,
                    user_id=user.id if user else 0,
                    student_name=user.name if user and user.name else "Unknown",
                    student_email=user.email if user and user.email else "",
                    started_at=attempt.started_at,
                    submitted_at=attempt.submitted_at,
                    status=status_val,
                    score=score_val,
                    total_marks=total_val,
                    percentage=pct,
                )
            )

        avg_score = (
            sum(completed_scores) / len(completed_scores)
            if len(completed_scores) > 0
            else 0.0
        )

        base_upload_dir = Path(settings.upload_dir)
        file_path = base_upload_dir / "results" / f"series_{series.id}" / "result.pdf"
        result_file_key = f"uploads/results/series_{series.id}/result.pdf" if file_path.exists() else None

        return TestSeriesResultsResponse(
            series_id=series.id,
            series_name=series.name,
            invite_token=getattr(series, "invite_token", None),
            access_type=series.access_type,
            is_result_show=bool(series.is_result_show),
            is_score_show=bool(series.is_score_show),
            result_file_key=result_file_key,
            total_attempts=len(attempts),
            completed_attempts=len(completed_scores),
            average_score=round(avg_score, 2),
            results=items,
        )

    @staticmethod
    def upload_result_sheet(
        series_id: int,
        file: UploadFile,
        user_id: int,
        user_role: int,
        db: Session
    ) -> dict:
        series = db.query(TestSeries).filter(TestSeries.id == series_id).first()
        if not series:
            raise ValueError("Test series not found")

        # Verify permission
        is_admin = False
        if user_role == 0:
            is_admin = True
        elif user_role == 1:
            membership = (
                db.query(OrganizationUser)
                .filter(OrganizationUser.user_id == user_id)
                .order_by(OrganizationUser.org_id)
                .first()
            )
            if membership and membership.org_id == series.org_id:
                is_admin = True

        is_supervisor = False
        if series.supervisor_id and series.supervisor_id == user_id:
            is_supervisor = True
        elif series.teacher_group_id:
            tg = (
                db.query(TeacherGroup)
                .filter(TeacherGroup.id == series.teacher_group_id, TeacherGroup.is_deleted.is_(False))
                .first()
            )
            if tg and tg.supervisor == user_id:
                is_supervisor = True

        is_authorized = is_admin or is_supervisor or (series.created_by == user_id)

        if not is_authorized:
            raise TestSeriesPermissionError("You do not have permission to upload a result sheet for this test series")

        filename = file.filename or ""
        if not filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are allowed")

        # Construct target directory: uploads/results/series_{series_id}/
        base_upload_dir = Path(settings.upload_dir)
        target_dir = base_upload_dir / "results" / f"series_{series_id}"
        target_dir.mkdir(parents=True, exist_ok=True)

        file_path = target_dir / "result.pdf"

        try:
            content = file.file.read()
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as exc:
            raise RuntimeError(f"Failed to save result sheet: {str(exc)}") from exc
        
        return {"message": "Result sheet uploaded successfully", "path": file_path.as_posix()}

    @staticmethod
    def _generate_unique_code(db: Session) -> str:
        """Generate an unused 8-character test series code."""
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        for _ in range(100):
            code = "".join(secrets.choice(alphabet) for _ in range(8))
            exists = db.query(TestSeries.id).filter(TestSeries.code == code).first()
            if exists is None:
                return code
        raise RuntimeError("Unable to generate a unique test series code")

    @staticmethod
    def _get_response(series_id: int, db: Session) -> TestSeriesResponse:
        item = (
            db.query(TestSeries)
            .options(joinedload(TestSeries.series_questions))
            .filter(TestSeries.id == series_id)
            .first()
        )
        count = (
            db.query(func.count(TestAttempt.id))
            .filter(TestAttempt.series_id == series_id)
            .scalar()
            or 0
        )
        return TestSeriesController._serialize(item, db=db, attempt_count=count)

    @staticmethod
    def _serialize(
        item: TestSeries,
        db: Session | None = None,
        attempt_count: int = 0,
        batch_ids: list[int] | None = None,
    ) -> TestSeriesResponse:
        if batch_ids is None and db is not None:
            records = (
                db.query(TestAccess.batch_id)
                .filter(TestAccess.test_series_id == item.id)
                .all()
            )
            batch_ids = [r[0] for r in records]
        elif batch_ids is None:
            batch_ids = []

        batch_id = batch_ids[0] if batch_ids else getattr(item, "batch_id", None)

        student_ids = []
        if db is not None and batch_id:
            bs_entries = db.query(BatchStudent.student_id).filter(BatchStudent.batch_id == batch_id).all()
            student_ids = [bs[0] for bs in bs_entries]

        invite_tok = getattr(item, "invite_token", None)
        if item.access_type == "invite_only":
            if not invite_tok and db is not None:
                invite_tok = secrets.token_urlsafe(24)
                item.invite_token = invite_tok
                item.invite_token_hash = hashlib.sha256(invite_tok.encode()).hexdigest()
                try:
                    db.commit()
                except Exception:
                    db.rollback()
        else:
            invite_tok = None

        return TestSeriesResponse(
            id=item.id,
            code=item.code,
            invite_token=invite_tok,
            access_type=item.access_type,
            name=item.name,
            org_id=item.org_id,
            created_by=item.created_by,
            teacher_group_id=item.teacher_group_id,
            supervisor_id=item.supervisor_id,
            batch_id=batch_id,
            batch_ids=batch_ids,
            student_ids=student_ids,
            valid_until=item.valid_until,
            duration_seconds=item.duration_seconds,
            is_active=item.is_active,
            is_result_show=bool(item.is_result_show),
            is_score_show=bool(item.is_score_show),
            question_ids=[entry.question_id for entry in item.series_questions],
            created_at=item.created_at,
            updated_at=item.updated_at,
            attempt_count=attempt_count,
        )

    @staticmethod
    def get_questions_with_answers(
        series_id: int,
        user_id: int,
        user_role: int,
        db: Session
    ):

        if user_role == 3:
            raise TestSeriesPermissionError(
                "Students cannot view test series questions and answers"
            )

        test_series = (
            db.query(TestSeries)
            .filter(TestSeries.id == series_id)
            .first()
        )

        if not test_series:
            return None

        if user_role == 0:
            pass

        elif user_role in (1, 2):

            membership = (
                db.query(OrganizationUser)
                .filter(
                    OrganizationUser.user_id == user_id
                )
                .order_by(OrganizationUser.org_id)
                .first()
            )

            if not membership:
                raise TestSeriesPermissionError(
                    "User is not assigned to any organization"
                )

            if membership.org_id != test_series.org_id:
                raise TestSeriesPermissionError(
                    "You do not have permission to view this test series"
                )

        else:
            raise TestSeriesPermissionError(
                "You do not have permission to view this test series"
            )

        series_questions = (
            db.query(SeriesQuestion)
            .options(
                joinedload(SeriesQuestion.question)
                .joinedload(Question.options)
            )
            .filter(
                SeriesQuestion.series_id == series_id
            )
            .order_by(SeriesQuestion.position)
            .all()
        )

        question_ids = [item.question.id for item in series_questions if item.question]
        q_diagrams_map = {}
        if question_ids:
            q_diagrams = (
                db.query(Diagram)
                .filter(Diagram.type == 0, Diagram.ref_id.in_(question_ids))
                .order_by(Diagram.id.asc())
                .all()
            )
            for d in q_diagrams:
                if d.ref_id not in q_diagrams_map:
                    q_diagrams_map[d.ref_id] = []
                q_diagrams_map[d.ref_id].append({"id": d.id, "path": d.path})

        all_option_ids = [opt.id for item in series_questions for opt in item.question.options if opt.id]
        opt_diag_map = {}
        if all_option_ids:
            opt_diagrams = (
                db.query(Diagram)
                .filter(Diagram.type == 1, Diagram.ref_id.in_(all_option_ids))
                .order_by(Diagram.id.desc())
                .all()
            )
            for d in opt_diagrams:
                if d.ref_id not in opt_diag_map:
                    opt_diag_map[d.ref_id] = d.path

        return {
            "series_id": test_series.id,
            "series_name": test_series.name,

            "questions": [
                {
                    "question_id": item.question.id,
                    "question": item.question.question,
                    "marks": float(item.question.marks),
                    "diagrams": q_diagrams_map.get(item.question.id, []),
                    "diagram_path": q_diagrams_map[item.question.id][-1]["path"] if q_diagrams_map.get(item.question.id) else None,
                    "options": [
                        {
                            "id": option.id,
                            "text": option.ans,
                            "is_correct": option.is_correct,
                            "diagram_path": opt_diag_map.get(option.id)
                        }
                        for option in item.question.options
                    ]
                }
                for item in series_questions
            ]
        }


