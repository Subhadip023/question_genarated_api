"""
Question controller — handles request orchestration between route and model.
This acts as the Controller (C) layer in MVC.
"""

from sqlalchemy.orm import Session, joinedload

from app.models.question import Question
from app.models.question_option import QuestionOption
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
        """Insert a question and its options in one transaction."""
        question = Question(
            question=data.question,
            is_global=data.is_global,
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
