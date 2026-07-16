"""Student test attempt and snapshotted question models."""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    series_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_series.id", ondelete="RESTRICT"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    total_marks: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    questions: Mapped[list["AttemptQuestion"]] = relationship(  # noqa: F821
        "AttemptQuestion",
        back_populates="attempt",
        cascade="all, delete-orphan",
        order_by="AttemptQuestion.position",
    )


class AttemptQuestion(Base):
    __tablename__ = "attempt_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False
    )
    original_question_id: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    marks: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    options_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    correct_option_id: Mapped[int | None] = mapped_column(Integer)
    selected_option_id: Mapped[int | None] = mapped_column(Integer)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    marks_awarded: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    attempt: Mapped[TestAttempt] = relationship(TestAttempt, back_populates="questions")
