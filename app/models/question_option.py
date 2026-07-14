"""
QuestionOption SQLAlchemy model — maps to the `question_options` table.
Each row is one answer option for a question; one option has is_correct=True.
"""

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QuestionOption(Base):
    """ORM model for the question_options table."""

    __tablename__ = "question_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # FK → questions.id
    q_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Option text — can contain HTML
    ans: Mapped[str] = mapped_column(Text, nullable=False)

    # Only one option per question should have is_correct=True
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Back-reference to the parent question
    question: Mapped["Question"] = relationship("Question", back_populates="options")  # noqa: F821

    def __repr__(self) -> str:
        return f"<QuestionOption id={self.id} q_id={self.q_id} is_correct={self.is_correct}>"
