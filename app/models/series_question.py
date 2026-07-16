"""Ordered association between test series and questions."""

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SeriesQuestion(Base):
    __tablename__ = "series_questions"

    series_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_series.id", ondelete="CASCADE"), primary_key=True
    )
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    series: Mapped["TestSeries"] = relationship(  # noqa: F821
        "TestSeries", back_populates="series_questions"
    )
