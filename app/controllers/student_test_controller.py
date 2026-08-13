"""Student test discovery, attempts, answers, and scoring."""

import hmac
import json
import hashlib
import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from app.constants.attempt_status import AttemptStatus

from app.models.organization_user import OrganizationUser
from app.models.question import Question
from app.models.series_question import SeriesQuestion
from app.models.topic import Topic
from app.models.test_attempt import AttemptQuestion, TestAttempt
from app.models.test_series import TestSeries
from app.schemas.student_test import (
    AttemptHistoryResponse,
    AttemptOptionResponse,
    AttemptQuestionResponse,
    AttemptResponse,
    AvailableSeriesResponse,
    PaginatedAvailableSeriesResponse,
    StartAttemptRequest,
    SubmitAttemptRequest,
)


class StudentTestPermissionError(Exception):
    """Caller is authenticated but not allowed to perform this action (HTTP 403)."""


class StudentTestValidationError(Exception):
    """Request is well-formed but semantically invalid, e.g. bad option (HTTP 400)."""


class StudentTestNotFoundError(Exception):
    """Requested attempt or attempt-question does not exist / is not visible (HTTP 404)."""


class StudentTestConflictError(Exception):
    """Attempt is in a state that forbids the change, e.g. submitted/expired (HTTP 409)."""


class StudentTestController:
    @staticmethod
    def list_public(
        user_role: int,
        user_id: int,
        db: Session,
        q: str | None = None,
        topic: str | None = None,
        org_id: int | None = None,
        sort_order: str = "asc",
        page: int = 1,
        limit: int = 10,
    ) -> PaginatedAvailableSeriesResponse:
        StudentTestController._require_student(user_role)
        now = datetime.now(timezone.utc)

        query = (
            db.query(TestSeries)
            .options(
                joinedload(TestSeries.series_questions)
                .joinedload(SeriesQuestion.question)
                .joinedload(Question.topic)
            )
            .filter(
                TestSeries.access_type == "public",
                TestSeries.is_active.is_(True),
                TestSeries.valid_until > now,
                ~db.query(TestAttempt)
                .filter(
                    TestAttempt.series_id == TestSeries.id,
                    TestAttempt.user_id == user_id,
                )
                .exists(),
            )
        )

        if org_id is not None and org_id >= 0:
            query = query.filter(TestSeries.org_id == org_id)

        if topic and topic.strip():
            query = query.filter(
                TestSeries.series_questions.any(
                    SeriesQuestion.question.has(
                        Question.topic.has(Topic.name == topic.strip())
                    )
                )
            )

        if q and q.strip():
            term = f"%{q.strip()}%"
            query = query.filter(
                (TestSeries.name.ilike(term))
                | (
                    TestSeries.series_questions.any(
                        SeriesQuestion.question.has(
                            Question.topic.has(Topic.name.ilike(term))
                        )
                    )
                )
            )

        if sort_order == "desc":
            query = query.order_by(TestSeries.name.desc())
        else:
            query = query.order_by(TestSeries.name.asc())

        total = query.count()
        total_pages = math.ceil(total / limit) if limit > 0 else 1

        offset = max(0, (page - 1) * limit)
        items = query.offset(offset).limit(limit).all()

        results = []
        for item in items:
            topic_names = sorted(
                list(
                    {
                        sq.question.topic.name
                        for sq in item.series_questions
                        if sq.question and sq.question.topic and sq.question.topic.name
                    }
                )
            )
            results.append(
                AvailableSeriesResponse(
                    id=item.id,
                    name=item.name,
                    org_id=item.org_id,
                    valid_until=item.valid_until,
                    duration_seconds=item.duration_seconds,
                    question_count=len(item.series_questions),
                    topics=topic_names,
                )
            )

        return PaginatedAvailableSeriesResponse(
            items=results,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )



    @staticmethod
    def start(
        data: StartAttemptRequest, user_id: int, user_role: int, db: Session
    ) -> AttemptResponse:
        StudentTestController._require_student(user_role)
        now = datetime.now(timezone.utc)
        query = db.query(TestSeries).options(
            joinedload(TestSeries.series_questions)
        )
        if data.series_id is not None:
            series = query.filter(
                TestSeries.id == data.series_id,
            ).first()
        else:
            token = (data.invite_token or "").strip()
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            conditions = [
                TestSeries.invite_token_hash == token_hash,
                TestSeries.code == token,
            ]
            if token.isdigit():
                conditions.append(TestSeries.id == int(token))

            series = query.filter(or_(*conditions)).first()

        if series is None:
            raise StudentTestValidationError("Test series not found or access code is invalid")
        if not series.is_active or StudentTestController._as_utc(series.valid_until) <= now:
            raise StudentTestPermissionError("Test series is inactive or expired")

        # ── Check for an existing attempt for this series ──────────────────────
        existing = (
            db.query(TestAttempt)
            .filter(
                TestAttempt.series_id == series.id,
                TestAttempt.user_id == user_id,
            )
            .order_by(TestAttempt.id.desc())
            .first()
        )
        if existing is not None:
            # Auto-expire if time ran out
            StudentTestController._mark_expired(existing, db)
            if existing.status == AttemptStatus.IN_PROGRESS:
                # Resume the existing attempt
                return StudentTestController.get_attempt(existing.id, user_id, user_role, db)
            # Already submitted or expired — do not allow a second attempt
            raise StudentTestValidationError(
                "You have already completed this test. Check your results in Attempt History."
            )
        # ── No existing attempt — create one ───────────────────────────────────

        question_ids = [entry.question_id for entry in series.series_questions]
        questions = {
            item.id: item
            for item in db.query(Question)
            .options(joinedload(Question.options))
            .filter(Question.id.in_(question_ids))
            .all()
        }
        expires_at = min(
            now + timedelta(seconds=series.duration_seconds),
            StudentTestController._as_utc(series.valid_until),
        )
        snapshots = []
        total_marks = Decimal("0")
        for position, question_id in enumerate(question_ids, start=1):
            question = questions.get(question_id)
            if question is None:
                raise StudentTestValidationError("A test question no longer exists")
            total_marks += question.marks
            snapshots.append(
                AttemptQuestion(
                    original_question_id=question.id,
                    position=position,
                    question_text=question.question,
                    marks=question.marks,
                    options_snapshot=json.dumps(
                        [{"id": o.id, "ans": o.ans} for o in question.options]
                    ),
                    correct_option_id=next(
                        (o.id for o in question.options if o.is_correct), None
                    ),
                )
            )
        attempt = TestAttempt(
            series_id=series.id,
            user_id=user_id,
            started_at=now,
            expires_at=expires_at,
            status=AttemptStatus.IN_PROGRESS,
            total_marks=total_marks,
            questions=snapshots,
        )
        try:
            db.add(attempt)
            db.commit()
        except Exception:
            db.rollback()
            raise
        return StudentTestController.get_attempt(attempt.id, user_id, user_role, db)

    @staticmethod
    def start_timer(
        attempt_id: int, user_id: int, user_role: int, db: Session
    ) -> AttemptResponse:
        attempt = StudentTestController._student_owned_attempt(
            attempt_id, user_id, user_role, db
        )
        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise StudentTestConflictError("Attempt is no longer in progress")

        # Reset start time only if no answers have been saved yet (initial entrance into exam)
        has_answers = any(q.selected_option_id is not None for q in attempt.questions)
        if not has_answers:
            series = db.query(TestSeries).filter(TestSeries.id == attempt.series_id).first()
            if series:
                now = datetime.now(timezone.utc)
                attempt.started_at = now
                attempt.expires_at = min(
                    now + timedelta(seconds=series.duration_seconds),
                    StudentTestController._as_utc(series.valid_until),
                )
                db.commit()

        return StudentTestController.get_attempt(attempt.id, user_id, user_role, db)

    @staticmethod
    def save_answer(
        attempt_id: int,
        attempt_question_id: int,
        selected_option_id: int | None,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> AttemptResponse:
        try:
            # Lock the attempt row for the duration of this transaction so a
            # concurrent submit (or another save) cannot slip between the
            # active-status check and the answer write. On engines without row
            # locks (e.g. SQLite) this degrades to a no-op but the logic holds.
            attempt = StudentTestController._student_owned_attempt(
                attempt_id, user_id, user_role, db, lock=True
            )
            # Active-status + expiry check and the write happen atomically inside
            # the same locked transaction.
            StudentTestController._assert_active(attempt)

            question = (
                db.query(AttemptQuestion)
                .filter(
                    AttemptQuestion.id == attempt_question_id,
                    AttemptQuestion.attempt_id == attempt.id,
                )
                .first()
            )
            if question is None:
                raise StudentTestNotFoundError(
                    "Question does not belong to this attempt"
                )

            if selected_option_id is not None:
                options = json.loads(question.options_snapshot)
                if selected_option_id not in {option["id"] for option in options}:
                    raise StudentTestValidationError("Selected option is invalid")
                question.answered_at = datetime.now(timezone.utc)
            else:
                question.answered_at = None

            question.selected_option_id = selected_option_id
            db.commit()
        except Exception:
            db.rollback()
            raise
        return StudentTestController.get_attempt(attempt_id, user_id, user_role, db)

    @staticmethod
    def submit(
        attempt_id: int, data: SubmitAttemptRequest, user_id: int, user_role: int, db: Session
    ) -> AttemptResponse:
        try:
            # Same lock as save_answer: submit and answer-saving contend for the
            # same attempt row, so exactly one of them can finalize the attempt.
            attempt = StudentTestController._student_owned_attempt(
                attempt_id, user_id, user_role, db, lock=True
            )
            if attempt.status != AttemptStatus.IN_PROGRESS:
                raise StudentTestConflictError(
                    "This attempt has already been submitted or has expired."
                )
            now = datetime.now(timezone.utc)
            score = Decimal("0")
            for question in attempt.questions:
                awarded = (
                    question.marks
                    if question.selected_option_id is not None
                    and question.selected_option_id == question.correct_option_id
                    else Decimal("0")
                )
                question.marks_awarded = awarded
                score += awarded
            attempt.score = score
            attempt.submitted_at = now
            if data.force_submit:
                attempt.status = AttemptStatus.FORCE_SUBMITTED

            elif StudentTestController._as_utc(attempt.expires_at) <= now:
                attempt.status = AttemptStatus.EXPIRED

            else:
                attempt.status = AttemptStatus.SUBMITTED
            db.commit()
        except Exception:
            db.rollback()
            raise
        return StudentTestController.get_attempt(attempt_id, user_id, user_role, db)

    @staticmethod
    def get_attempt(
        attempt_id: int, user_id: int, user_role: int, db: Session
    ) -> AttemptResponse:
        attempt = StudentTestController._viewable_attempt(attempt_id, user_id, user_role, db)
        StudentTestController._mark_expired(attempt, db)
        return StudentTestController._serialize_attempt(attempt, db)

    @staticmethod
    def history(
        user_id: int, user_role: int, db: Session
    ) -> list[AttemptHistoryResponse]:
        StudentTestController._require_student(user_role)
        attempts = (
            db.query(TestAttempt)
            .filter(TestAttempt.user_id == user_id)
            .order_by(TestAttempt.started_at.desc())
            .all()
        )
        result = []
        for attempt in attempts:
            StudentTestController._mark_expired(attempt, db)
            series = db.query(TestSeries).filter(TestSeries.id == attempt.series_id).first()
            result.append(
                AttemptHistoryResponse(
                    id=attempt.id,
                    series_id=attempt.series_id,
                    series_name=series.name if series else "Deleted test series",
                    started_at=StudentTestController._as_utc(attempt.started_at),
                    expires_at=StudentTestController._as_utc(attempt.expires_at),
                    submitted_at=StudentTestController._as_utc(attempt.submitted_at) if attempt.submitted_at else None,
                    status=attempt.status,
                    score=attempt.score,
                    total_marks=attempt.total_marks,
                )
            )
        return result

    @staticmethod
    def _assert_active(attempt):
        """Reject a modification when the attempt is no longer accepting answers.

        Kept side-effect free so it can be called inside a locked transaction:
        the caller decides when (and whether) to commit a state change.
        """
        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise StudentTestConflictError(
                "This attempt has already been submitted or has expired."
            )
        now = datetime.now(timezone.utc)
        if StudentTestController._as_utc(attempt.expires_at) <= now:
            raise StudentTestConflictError(
                "This attempt has expired and can no longer be modified."
            )

    @staticmethod
    def _student_owned_attempt(attempt_id, user_id, user_role, db, *, lock=False):
        """Authorize a *modification*: only the student (role 3) who owns the
        attempt may save answers or submit. Staff roles are rejected outright.

        - Non-student role  -> 403 (StudentTestPermissionError)
        - No such attempt for this user -> 404 (StudentTestNotFoundError)
        """
        if user_role != 3:
            raise StudentTestPermissionError(
                "Only the student who owns this attempt can modify it"
            )

        query = db.query(TestAttempt).filter(
            TestAttempt.id == attempt_id,
            TestAttempt.user_id == user_id,
        )
        if lock:
            # Serialize concurrent save/submit on the same attempt row. Ignored
            # by engines without row-level locking (e.g. SQLite).
            query = query.with_for_update()

        attempt = query.first()
        if attempt is None:
            raise StudentTestNotFoundError("Attempt not found")
        return attempt

    @staticmethod
    def _viewable_attempt(attempt_id, user_id, user_role, db):
        """Authorize a *read*: the owning student, or staff within scope.

        This is intentionally broader than :meth:`_student_owned_attempt` so that
        staff can inspect attempts without ever being able to change them.
        """
        StudentTestController._require_student(user_role)

        query = db.query(TestAttempt).options(
            joinedload(TestAttempt.questions)
        )

        # Student (role 3): only their own attempts
        if user_role == 3:
            attempt = query.filter(
                TestAttempt.id == attempt_id,
                TestAttempt.user_id == user_id
            ).first()

        # Super Admin (role 0): can see all attempts
        elif user_role == 0:
            attempt = query.filter(
                TestAttempt.id == attempt_id
            ).first()

        # Admin / Teacher (role 1,2): only allowed scope
        elif user_role in (1, 2):
            attempt = query.filter(
                TestAttempt.id == attempt_id
            ).first()

            if attempt:
                series = (
                    db.query(TestSeries)
                    .filter(TestSeries.id == attempt.series_id)
                    .first()
                )

                if series:
                    membership = (
                        db.query(OrganizationUser)
                        .filter(
                            OrganizationUser.user_id == user_id
                        )
                        .first()
                    )

                    user_org_id = membership.org_id if membership else None

                    if (
                        series.created_by != user_id
                        and (
                            user_org_id is None
                            or series.org_id != user_org_id
                        )
                    ):
                        attempt = None
        else:
            attempt = None

        if attempt is None:
            raise StudentTestNotFoundError("Attempt not found")

        return attempt

    @staticmethod
    def _mark_expired(attempt, db):

        if attempt.status != AttemptStatus.IN_PROGRESS:
            return

        now = datetime.now(timezone.utc)

        if StudentTestController._as_utc(attempt.expires_at) <= now:

            score = Decimal("0")

            for question in attempt.questions:
                if (
                    question.selected_option_id is not None
                    and question.selected_option_id == question.correct_option_id
                ):
                    question.marks_awarded = question.marks
                    score += question.marks
                else:
                    question.marks_awarded = Decimal("0")

            attempt.score = score
            attempt.submitted_at = now
            attempt.status = AttemptStatus.EXPIRED

            db.commit()

    @staticmethod
    def _serialize_attempt(attempt, db):
        series = db.query(TestSeries).filter(TestSeries.id == attempt.series_id).first()
        is_done = attempt.status != AttemptStatus.IN_PROGRESS
        return AttemptResponse(
            id=attempt.id,
            series_id=attempt.series_id,
            series_name=series.name if series else "Deleted test series",
            started_at=StudentTestController._as_utc(attempt.started_at),
            expires_at=StudentTestController._as_utc(attempt.expires_at),
            submitted_at=StudentTestController._as_utc(attempt.submitted_at) if attempt.submitted_at else None,
            status=attempt.status,
            score=attempt.score,
            total_marks=attempt.total_marks,
            questions=[
                AttemptQuestionResponse(
                    id=q.id,
                    original_question_id=q.original_question_id,
                    position=q.position,
                    question=q.question_text,
                    marks=q.marks,
                    options=[
                        AttemptOptionResponse(**option)
                        for option in json.loads(q.options_snapshot)
                    ],
                    selected_option_id=q.selected_option_id,
                    correct_option_id=q.correct_option_id if is_done else None,
                )
                for q in attempt.questions
            ],
        )

    @staticmethod
    def _require_student(user_role):
        if user_role not in (0, 1, 2, 3):
            raise StudentTestPermissionError("Invalid user role")


    @staticmethod
    def _as_utc(value):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
