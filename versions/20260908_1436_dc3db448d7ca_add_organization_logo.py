"""add organization logo

Revision ID: dc3db448d7ca
Revises: d351f2d57b83
Create Date: 2026-09-08 14:36:46.166647

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc3db448d7ca'
down_revision: Union[str, None] = 'd351f2d57b83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("logo", sa.String(1024), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "logo")
