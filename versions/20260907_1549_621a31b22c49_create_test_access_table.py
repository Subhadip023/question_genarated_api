"""create test access table

Revision ID: 621a31b22c49
Revises: 636ca13e1a6e
Create Date: 2026-09-07 15:49:26.620143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '621a31b22c49'
down_revision: Union[str, None] = '636ca13e1a6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "test_access",

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
            "batch_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "granted_by",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["test_series_id"],
            ["test_series.id"],
            ondelete="CASCADE"
        ),

        sa.ForeignKeyConstraint(
            ["batch_id"],
            ["batches.id"],
            ondelete="CASCADE"
        ),

        sa.ForeignKeyConstraint(
            ["granted_by"],
            ["users.id"]
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "test_series_id",
            "batch_id",
            name="uq_test_access_series_batch"
        ),
    )

    op.create_index(
        "ix_test_access_test_series_id",
        "test_access",
        ["test_series_id"]
    )

    op.create_index(
        "ix_test_access_batch_id",
        "test_access",
        ["batch_id"]
    )

    op.create_index(
        "ix_test_access_granted_by",
        "test_access",
        ["granted_by"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_test_access_granted_by",
        table_name="test_access"
    )

    op.drop_index(
        "ix_test_access_batch_id",
        table_name="test_access"
    )

    op.drop_index(
        "ix_test_access_test_series_id",
        table_name="test_access"
    )

    op.drop_table("test_access")