"""Teacher group model."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TeacherGroup(Base):
    """ORM model for teacher_groups table."""

    __tablename__ = "teacher_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    supervisor: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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

    creator: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys=[created_by]
    )
    supervisor_user: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys=[supervisor]
    )
    group_teachers: Mapped[list["GroupTeacher"]] = relationship(  # noqa: F821
        "GroupTeacher", back_populates="group", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TeacherGroup id={self.id} name={self.name!r} org_id={self.org_id}>"
