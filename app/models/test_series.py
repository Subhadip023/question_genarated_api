"""Test-series model."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TestSeries(Base):
    __tablename__ = "test_series"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str | None] = mapped_column(
        String(8), unique=True, index=True, nullable=True
    )
    invite_token_hash: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True, nullable=True
    )
    access_type: Mapped[str] = mapped_column(
        String(20), default="invite_only", nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    org_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    series_questions: Mapped[list["SeriesQuestion"]] = relationship(  # noqa: F821
        "SeriesQuestion",
        back_populates="series",
        cascade="all, delete-orphan",
        order_by="SeriesQuestion.position",
    )
