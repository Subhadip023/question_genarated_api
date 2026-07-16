"""add organization location and phone number

Revision ID: a73db509e1c4
Revises: f2a8c190b4de
Create Date: 2026-07-16 16:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a73db509e1c4"
down_revision: Union[str, None] = "f2a8c190b4de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("location", sa.String(255), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("phone_number", sa.String(30), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "phone_number")
    op.drop_column("organizations", "location")
