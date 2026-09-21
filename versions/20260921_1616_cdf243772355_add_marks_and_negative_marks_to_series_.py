"""add marks and negative marks to series questions

Revision ID: cdf243772355
Revises: b9f8d7e6c5a4
Create Date: 2026-09-21 16:16:53.035890

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cdf243772355'
down_revision: Union[str, None] = 'b9f8d7e6c5a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "series_questions",
        sa.Column("marks", sa.Float(), nullable=True),
    )

    op.add_column(
        "series_questions",
        sa.Column("negative_marks", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("series_questions", "negative_marks")
    op.drop_column("series_questions", "marks")