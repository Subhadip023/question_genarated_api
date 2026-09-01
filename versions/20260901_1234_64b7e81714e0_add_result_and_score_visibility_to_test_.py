"""add result and score visibility to test series

Revision ID: 64b7e81714e0
Revises: b8da4ff8d5eb
Create Date: 2026-09-01 12:34:08.646325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64b7e81714e0'
down_revision: Union[str, None] = 'b8da4ff8d5eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "test_series",
        sa.Column(
            "is_result_show",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "test_series",
        sa.Column(
            "is_score_show",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("test_series", "is_score_show")
    op.drop_column("test_series", "is_result_show")
