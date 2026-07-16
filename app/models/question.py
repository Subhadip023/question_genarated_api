"""
Question SQLAlchemy model — maps to the `questions` table in the database.
This acts as the Model (M) layer in MVC.
"""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Text,Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Question(Base):
    """ORM model for the questions table."""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Long text field — stores HTML content
    question: Mapped[str] = mapped_column(Text, nullable=False)
    organization_id: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_global: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    marks: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1.00"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # One question has many options
    options: Mapped[list["QuestionOption"]] = relationship(  # noqa: F821
        "QuestionOption", back_populates="question", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Question id={self.id} is_active={self.is_active}>"
