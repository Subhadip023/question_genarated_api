"""create organization_users table

Revision ID: d5837a19c246
Revises: a4c9e812f730
Create Date: 2026-07-16 12:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d5837a19c246"
down_revision: Union[str, None] = "a4c9e812f730"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organization_users",
        sa.Column("org_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("org_id", "user_id"),
    )


def downgrade() -> None:
    op.drop_table("organization_users")
