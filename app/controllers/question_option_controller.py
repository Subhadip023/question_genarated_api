"""
QuestionOption controller — handles option-related business logic.
Controller (C) layer in MVC.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.question_option import QuestionOption
from app.schemas.question_option import OptionCreate, OptionResponse


class QuestionOptionController:

    @staticmethod
    def add_option(q_id: int, data: OptionCreate, db: Session) -> OptionResponse:
        """Add an option to a question. Validates only one correct answer exists."""
        if data.is_correct:
            existing_correct = (
                db.query(QuestionOption)
                .filter(QuestionOption.q_id == q_id, QuestionOption.is_correct == True)  # noqa: E712
                .first()
            )
            if existing_correct:
                raise HTTPException(
                    status_code=400,
                    detail="A correct answer already exists for this question. Update it instead.",
                )

        option = QuestionOption(q_id=q_id, ans=data.ans, is_correct=data.is_correct)
        db.add(option)
        db.commit()
        db.refresh(option)
        return OptionResponse.model_validate(option)

    @staticmethod
    def get_options(q_id: int, db: Session) -> list[OptionResponse]:
        """Return all options for a given question."""
        options = db.query(QuestionOption).filter(QuestionOption.q_id == q_id).all()
        return [OptionResponse.model_validate(o) for o in options]

    @staticmethod
    def delete_option(option_id: int, db: Session) -> dict:
        """Delete a single option by ID."""
        option = db.query(QuestionOption).filter(QuestionOption.id == option_id).first()
        if not option:
            raise HTTPException(status_code=404, detail="Option not found")
        db.delete(option)
        db.commit()
        return {"detail": "Option deleted"}
