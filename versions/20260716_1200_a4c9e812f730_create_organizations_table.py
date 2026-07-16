"""create organizations table

Revision ID: a4c9e812f730
Revises: b17a737d68a0
Create Date: 2026-07-16 12:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a4c9e812f730"
down_revision: Union[str, None] = "b17a737d68a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_organizations_id"), "organizations", ["id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_organizations_id"), table_name="organizations")
    op.drop_table("organizations")
