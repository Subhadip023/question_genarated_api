"""Business logic for test-series management."""

import secrets
import hashlib

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.controllers.question_controller import QuestionController
from app.models.organization_user import OrganizationUser
from app.models.question import Question
from app.models.series_question import SeriesQuestion
from app.models.test_attempt import TestAttempt
from app.models.test_series import TestSeries
from app.models.user import User
from app.schemas.test_series import (
    TestSeriesCreate,
    TestSeriesResponse,
    TestSeriesResultItem,
    TestSeriesResultsResponse,
    TestSeriesUpdate,
)




class TestSeriesPermissionError(Exception):
    pass


class TestSeriesQuestionError(Exception):
    pass


class TestSeriesHasAttemptsError(Exception):
    pass


class TestSeriesController:
    @staticmethod
    def create(
        data: TestSeriesCreate, user_id: int, user_role: int, db: Session
    ) -> TestSeriesResponse:
        if user_role == 0:
            org_id = 0
        elif user_role in (1, 2):
            membership = (
                db.query(OrganizationUser)
                .filter(OrganizationUser.user_id == user_id)
                .order_by(OrganizationUser.org_id)
                .first()
            )
            org_id = membership.org_id if membership else 0
        else:
            raise TestSeriesPermissionError("Only roles 0, 1, and 2 can create test series")


        question_query = db.query(Question).filter(
            Question.id.in_(data.question_ids), Question.is_active.is_(True)
        )
        question_query = QuestionController._apply_visibility_filter(
            question_query, user_id, user_role, db
        )
        allowed_ids = {question.id for question in question_query.all()}
        if allowed_ids != set(data.question_ids):
            raise TestSeriesQuestionError(
                "One or more questions do not exist, are inactive, or are not accessible"
            )

        invite_token = (
            secrets.token_urlsafe(24) if data.access_type == "invite_only" else None
        )
        series_code = secrets.token_hex(4).upper()
        series = TestSeries(
            code=series_code,
            invite_token_hash=(
                hashlib.sha256(invite_token.encode()).hexdigest()
                if invite_token
                else None
            ),

            access_type=data.access_type,
            name=data.name.strip(),
            org_id=org_id,
            created_by=user_id,
            valid_until=data.valid_until,
            duration_seconds=data.duration_seconds,
            is_active=data.is_active,
            series_questions=[
                SeriesQuestion(question_id=question_id, position=position)
                for position, question_id in enumerate(data.question_ids, start=1)
            ],
        )
        try:
            db.add(series)
            db.commit()
        except Exception:
            db.rollback()
            raise
        response = TestSeriesController._get_response(series.id, db)
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
        is_authorized = False
        if user_role == 0 and series.org_id == 0:
            is_authorized = True
        elif user_role == 1:
            membership = (
                db.query(OrganizationUser)
                .filter(OrganizationUser.user_id == user_id)
                .order_by(OrganizationUser.org_id)
                .first()
            )
            if membership and membership.org_id == series.org_id:
                is_authorized = True
        elif series.created_by == user_id:
            is_authorized = True

        if not is_authorized:
            raise TestSeriesPermissionError("You do not have permission to edit this test series")

        updates = data.model_dump(exclude_unset=True)
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

        for field, value in updates.items():
            if value is not None:
                setattr(series, field, value)

        # Handle invite token hash when access type changes
        invite_token = None
        if "access_type" in updates:
            if updates["access_type"] == "invite_only" and not series.invite_token_hash:
                invite_token = secrets.token_urlsafe(24)
                series.invite_token_hash = hashlib.sha256(invite_token.encode()).hexdigest()
            elif updates["access_type"] == "public":
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
        if series_ids:
            counts = (
                db.query(TestAttempt.series_id, func.count(TestAttempt.id))
                .filter(TestAttempt.series_id.in_(series_ids))
                .group_by(TestAttempt.series_id)
                .all()
            )
            attempt_counts = dict(counts)

        return [
            TestSeriesController._serialize(item, attempt_count=attempt_counts.get(item.id, 0))
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
        return TestSeriesController._serialize(item, attempt_count=count)

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
            pct = (
                float((attempt.score / attempt.total_marks) * 100)
                if attempt.total_marks > 0
                else 0.0
            )
            if attempt.status == "submitted":
                completed_scores.append(float(attempt.score))
            items.append(
                TestSeriesResultItem(
                    attempt_id=attempt.id,
                    user_id=user.id,
                    student_name=user.name,
                    student_email=user.email,
                    started_at=attempt.started_at,
                    submitted_at=attempt.submitted_at,
                    status=attempt.status,
                    score=float(attempt.score),
                    total_marks=float(attempt.total_marks),
                    percentage=round(pct, 2),
                )
            )

        avg_score = (
            sum(completed_scores) / len(completed_scores)
            if len(completed_scores) > 0
            else 0.0
        )

        return TestSeriesResultsResponse(
            series_id=series.id,
            series_name=series.name,
            invite_token=getattr(series, "invite_token", None),
            access_type=series.access_type,
            total_attempts=len(attempts),
            completed_attempts=len(completed_scores),
            average_score=round(avg_score, 2),
            results=items,
        )

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
        return TestSeriesController._serialize(item, attempt_count=count)

    @staticmethod
    def _serialize(item: TestSeries, attempt_count: int = 0) -> TestSeriesResponse:
        return TestSeriesResponse(
            id=item.id,
            code=item.code,
            invite_token=None,
            access_type=item.access_type,
            name=item.name,
            org_id=item.org_id,
            created_by=item.created_by,
            valid_until=item.valid_until,
            duration_seconds=item.duration_seconds,
            is_active=item.is_active,
            question_ids=[entry.question_id for entry in item.series_questions],
            created_at=item.created_at,
            updated_at=item.updated_at,
            attempt_count=attempt_count,
        )



