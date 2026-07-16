"""add question ownership

Revision ID: e91c4a72d6f0
Revises: d5837a19c246
Create Date: 2026-07-16 14:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e91c4a72d6f0"
down_revision: Union[str, None] = "d5837a19c246"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "questions",
        sa.Column("organization_id", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "questions",
        sa.Column("user_id", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("questions", "user_id")
    op.drop_column("questions", "organization_id")
