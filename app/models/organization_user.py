"""Association model linking organizations and users."""

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OrganizationUser(Base):
    """Membership row for a user in an organization."""

    __tablename__ = "organization_users"

    org_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    def __repr__(self) -> str:
        return f"<OrganizationUser org_id={self.org_id} user_id={self.user_id}>"
