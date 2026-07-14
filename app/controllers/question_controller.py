"""
Question controller — handles request orchestration between route and model.
This acts as the Controller (C) layer in MVC.
"""

from sqlalchemy.orm import Session, joinedload

from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionResponse


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
    def create_question(data: QuestionCreate, db: Session) -> QuestionResponse:
        """Insert a new question into the database and return it."""
        question = Question(
            question=data.question,
            is_active=data.is_active,
        )
        db.add(question)
        db.commit()
        # Reload with options eagerly so the response includes them (empty on create)
        db.refresh(question)
        question = (
            db.query(Question)
            .options(joinedload(Question.options))
            .filter(Question.id == question.id)
            .first()
        )
        return QuestionResponse.model_validate(question)

    @staticmethod
    def get_all_questions(db: Session) -> list[QuestionResponse]:
        """Fetch all questions with their options in a single query."""
        questions = (
            db.query(Question)
            .options(joinedload(Question.options))
            .all()
        )
        return [QuestionResponse.model_validate(q) for q in questions]

    @staticmethod
    def get_question(question_id: int, db: Session) -> QuestionResponse | None:
        """Fetch a single question by ID, including its options."""
        question = (
            db.query(Question)
            .options(joinedload(Question.options))
            .filter(Question.id == question_id)
            .first()
        )
        if not question:
            return None
        return QuestionResponse.model_validate(question)
