"""Business logic for test-series management."""

import secrets
import hashlib

from sqlalchemy.orm import Session, joinedload

from app.controllers.question_controller import QuestionController
from app.models.organization_user import OrganizationUser
from app.models.question import Question
from app.models.series_question import SeriesQuestion
from app.models.test_series import TestSeries
from app.schemas.test_series import TestSeriesCreate, TestSeriesResponse


class TestSeriesPermissionError(Exception):
    pass


class TestSeriesQuestionError(Exception):
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
            if membership is None:
                raise TestSeriesPermissionError("User does not belong to an organization")
            org_id = membership.org_id
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
        series = TestSeries(
            code=None,
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
    def list_for_user(user_id: int, user_role: int, db: Session) -> list[TestSeriesResponse]:
        query = db.query(TestSeries).options(joinedload(TestSeries.series_questions))
        query = TestSeriesController._apply_visibility(query, user_id, user_role, db)
        return [TestSeriesController._serialize(item) for item in query.all()]

    @staticmethod
    def get_for_user(
        series_id: int, user_id: int, user_role: int, db: Session
    ) -> TestSeriesResponse | None:
        query = db.query(TestSeries).filter(TestSeries.id == series_id)
        query = TestSeriesController._apply_visibility(query, user_id, user_role, db)
        item = query.options(joinedload(TestSeries.series_questions)).first()
        return TestSeriesController._serialize(item) if item else None

    @staticmethod
    def _apply_visibility(query, user_id: int, user_role: int, db: Session):
        if user_role == 0:
            return query.filter(TestSeries.org_id == 0)
        if user_role == 1:
            org_ids = db.query(OrganizationUser.org_id).filter(
                OrganizationUser.user_id == user_id
            )
            return query.filter(TestSeries.org_id.in_(org_ids))
        if user_role == 2:
            return query.filter(TestSeries.created_by == user_id)
        return query.filter(False)

    @staticmethod
    def _get_response(series_id: int, db: Session) -> TestSeriesResponse:
        item = (
            db.query(TestSeries)
            .options(joinedload(TestSeries.series_questions))
            .filter(TestSeries.id == series_id)
            .first()
        )
        return TestSeriesController._serialize(item)

    @staticmethod
    def _serialize(item: TestSeries) -> TestSeriesResponse:
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
        )
