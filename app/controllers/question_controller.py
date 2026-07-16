"""
Question controller — handles request orchestration between route and model.
This acts as the Controller (C) layer in MVC.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.organization_user import OrganizationUser
from app.schemas.question import QuestionCreate, QuestionResponse, QuestionUpdate


class QuestionCreatorHasNoOrganizationError(Exception):
    """Raised when a non-superadmin has no organization membership."""


class QuestionController:
    """Controller responsible for handling question-related business logic."""

    @staticmethod
    def get_health() -> dict:
        """Return API health status."""
        return {"status": "ok"}

    @staticmethod
    def get_welcome() -> dict:
        """Return welcome message."""
        return {"message": "Welcome to the Question Generator API"}

    @staticmethod
    def create_question(
        data: QuestionCreate,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> QuestionResponse:
        """Insert a question and its options in one transaction."""
        if user_role == 0:
            organization_id = 0
            is_global = True
        else:
            membership = (
                db.query(OrganizationUser)
                .filter(OrganizationUser.user_id == user_id)
                .order_by(OrganizationUser.org_id)
                .first()
            )
            if membership is None:
                raise QuestionCreatorHasNoOrganizationError
            organization_id = membership.org_id
            is_global = False

        question = Question(
            question=data.question,
            organization_id=organization_id,
            user_id=user_id,
            is_global=is_global,
            marks=data.marks,
            is_active=data.is_active,
            options=[
                QuestionOption(
                    ans=option.ans,
                    is_correct=option.is_correct,
                )
                for option in data.options
            ],
        )

        try:
            db.add(question)
            db.commit()
        except Exception:
            db.rollback()
            raise

        question = (
            db.query(Question)
            .options(joinedload(Question.options))
            .filter(Question.id == question.id)
            .first()
        )
        return QuestionResponse.model_validate(question)

    @staticmethod
    def get_all_questions(
        user_id: int,
        user_role: int,
        db: Session,
    ) -> list[QuestionResponse]:
        """Fetch only questions visible to the authenticated user."""
        query = db.query(Question).options(joinedload(Question.options))
        query = QuestionController._apply_visibility_filter(
            query, user_id, user_role, db
        )
        questions = query.all()
        return [QuestionResponse.model_validate(q) for q in questions]

    @staticmethod
    def get_question(
        question_id: int,
        user_id: int,
        user_role: int,
        db: Session,
    ) -> QuestionResponse | None:
        """Fetch a question only when it is visible to the authenticated user."""
        query = (
            db.query(Question)
            .options(joinedload(Question.options))
            .filter(Question.id == question_id)
        )
        query = QuestionController._apply_visibility_filter(
            query, user_id, user_role, db
        )
        question = query.first()
        if not question:
            return None
        return QuestionResponse.model_validate(question)

    @staticmethod
    def _apply_visibility_filter(query, user_id: int, user_role: int, db: Session):
        """Apply role-based question visibility to a SQLAlchemy query."""
        if user_role == 0:
            return query.filter(Question.is_global.is_(True))

        if user_role == 1:
            organization_ids = (
                select(OrganizationUser.org_id)
                .filter(OrganizationUser.user_id == user_id)
            )
            return query.filter(Question.organization_id.in_(organization_ids))

        if user_role == 2:
            return query.filter(Question.user_id == user_id)

        return query.filter(False)

    @staticmethod
    def update_question(
        question_id: int,
        data: QuestionUpdate,
        db: Session,
    ) -> QuestionResponse | None:
        """Partially update a question and optionally replace all its options."""
        question = (
            db.query(Question)
            .options(joinedload(Question.options))
            .filter(Question.id == question_id)
            .first()
        )
        if question is None:
            return None

        updates = data.model_dump(exclude_unset=True)
        options = updates.pop("options", None)

        for field, value in updates.items():
            if value is not None:
                setattr(question, field, value)

        if options is not None:
            question.options = [QuestionOption(**option) for option in options]

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        question = (
            db.query(Question)
            .options(joinedload(Question.options))
            .filter(Question.id == question_id)
            .first()
        )
        return QuestionResponse.model_validate(question)

    @staticmethod
    def delete_question(question_id: int, db: Session) -> bool:
        """Delete a question and its related options."""
        question = (
            db.query(Question)
            .filter(Question.id == question_id)
            .first()
        )
        if question is None:
            return False

        try:
            db.delete(question)
            db.commit()
        except Exception:
            db.rollback()
            raise

        return True
