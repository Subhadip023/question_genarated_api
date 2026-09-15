"""create answer keys table

Revision ID: 731e31f970b7
Revises: d351f2d57b83
Create Date: 2026-09-15 12:29:43.487610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '731e31f970b7'
down_revision: Union[str, None] = 'd351f2d57b83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "answer_keys",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False
        ),
        sa.Column(
            "test_series_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "path",
            sa.String(length=500),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["test_series_id"],
            ["test_series.id"],
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "test_series_id",
            name="uq_answer_key_test_series"
        ),
    )

    op.create_index(
        "ix_answer_keys_test_series_id",
        "answer_keys",
        ["test_series_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_answer_keys_test_series_id",
        table_name="answer_keys"
    )

    op.drop_table("answer_keys")
