"""Student test discovery, attempts, answers, and scoring."""

import hmac
import json
import hashlib
import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

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
)


class StudentTestPermissionError(Exception):
    pass


class StudentTestValidationError(Exception):
    pass


class StudentTestController:
    @staticmethod
    def list_public(
        user_role: int,
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
                TestSeries.access_type == "public",
            ).first()
        else:
            token_hash = hashlib.sha256((data.invite_token or "").encode()).hexdigest()
            candidate = query.filter(
                TestSeries.access_type == "invite_only",
                TestSeries.invite_token_hash == token_hash,
            ).first()
            series = (
                candidate
                if candidate
                and candidate.invite_token_hash
                and hmac.compare_digest(candidate.invite_token_hash, token_hash)
                else None
            )
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
            if existing.status == "in_progress":
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
    def save_answer(
        attempt_id: int,
        attempt_question_id: int,
        selected_option_id: int,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> AttemptResponse:
        attempt = StudentTestController._active_attempt(
            attempt_id, user_id, user_role, db
        )
        question = next((q for q in attempt.questions if q.id == attempt_question_id), None)
        if question is None:
            raise StudentTestValidationError("Question does not belong to this attempt")
        options = json.loads(question.options_snapshot)
        if selected_option_id not in {option["id"] for option in options}:
            raise StudentTestValidationError("Selected option is invalid")
        question.selected_option_id = selected_option_id
        question.answered_at = datetime.now(timezone.utc)
        db.commit()
        return StudentTestController.get_attempt(attempt_id, user_id, user_role, db)

    @staticmethod
    def submit(
        attempt_id: int, user_id: int, user_role: int, db: Session
    ) -> AttemptResponse:
        attempt = StudentTestController._owned_attempt(
            attempt_id, user_id, user_role, db
        )
        if attempt.status != "in_progress":
            raise StudentTestValidationError(
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
        attempt.status = (
            "expired" if StudentTestController._as_utc(attempt.expires_at) <= now else "submitted"
        )
        db.commit()
        return StudentTestController.get_attempt(attempt_id, user_id, user_role, db)

    @staticmethod
    def get_attempt(
        attempt_id: int, user_id: int, user_role: int, db: Session
    ) -> AttemptResponse:
        attempt = StudentTestController._owned_attempt(attempt_id, user_id, user_role, db)
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
    def _active_attempt(attempt_id, user_id, user_role, db):
        attempt = StudentTestController._owned_attempt(attempt_id, user_id, user_role, db)
        StudentTestController._mark_expired(attempt, db)
        if attempt.status != "in_progress":
            raise StudentTestPermissionError("Attempt is no longer active")
        return attempt

    @staticmethod
    def _owned_attempt(attempt_id, user_id, user_role, db):
        StudentTestController._require_student(user_role)
        attempt = (
            db.query(TestAttempt)
            .options(joinedload(TestAttempt.questions))
            .filter(TestAttempt.id == attempt_id, TestAttempt.user_id == user_id)
            .first()
        )
        if attempt is None:
            raise StudentTestValidationError("Attempt not found")
        return attempt

    @staticmethod
    def _mark_expired(attempt, db):
        if (
            attempt.status == "in_progress"
            and StudentTestController._as_utc(attempt.expires_at) <= datetime.now(timezone.utc)
        ):
            attempt.status = "expired"
            db.commit()

    @staticmethod
    def _serialize_attempt(attempt, db):
        series = db.query(TestSeries).filter(TestSeries.id == attempt.series_id).first()
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
                    correct_option_id=q.correct_option_id if attempt.status != "in_progress" else None,
                )
                for q in attempt.questions
            ],
        )

    @staticmethod
    def _require_student(user_role):
        if user_role != 3:
            raise StudentTestPermissionError("Only students can use student test endpoints")

    @staticmethod
    def _as_utc(value):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
