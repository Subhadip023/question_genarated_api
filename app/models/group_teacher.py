"""Group teacher mapping model."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GroupTeacher(Base):
    """ORM model for group_teachers table."""

    __tablename__ = "group_teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teacher_groups.id", ondelete="CASCADE"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
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

    group: Mapped["TeacherGroup"] = relationship(  # noqa: F821
        "TeacherGroup", back_populates="group_teachers"
    )
    teacher: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys=[teacher_id]
    )

    def __repr__(self) -> str:
        return f"<GroupTeacher id={self.id} group_id={self.group_id} teacher_id={self.teacher_id}>"
