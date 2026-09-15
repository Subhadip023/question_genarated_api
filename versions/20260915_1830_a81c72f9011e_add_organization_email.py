"""add organization email field

Revision ID: a81c72f9011e
Revises: 6eb2ff9bde8a
Create Date: 2026-09-15 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a81c72f9011e'
down_revision: Union[str, None] = '6eb2ff9bde8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("email", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "email")
