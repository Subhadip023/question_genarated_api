"""add student_id to test_access and make batch_id nullable

Revision ID: b9f8d7e6c5a4
Revises: a81c72f9011e
Create Date: 2026-09-18 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b9f8d7e6c5a4'
down_revision: Union[str, None] = 'a81c72f9011e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Allow batch_id to be NULL (when granting access to individual students)
    op.alter_column(
        "test_access",
        "batch_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    # Add student_id column (NULL when granting access to batches)
    op.add_column(
        "test_access",
        sa.Column("student_id", sa.Integer(), nullable=True),
    )

    # Add foreign key constraint to users(id)
    op.create_foreign_key(
        "fk_test_access_student_id",
        "test_access",
        "users",
        ["student_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Add index on student_id
    op.create_index(
        "ix_test_access_student_id",
        "test_access",
        ["student_id"],
    )

    # Add unique constraint on (test_series_id, student_id)
    op.create_unique_constraint(
        "uq_test_access_series_student",
        "test_access",
        ["test_series_id", "student_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_test_access_series_student",
        "test_access",
        type_="unique",
    )
    op.drop_index(
        "ix_test_access_student_id",
        table_name="test_access",
    )
    op.drop_constraint(
        "fk_test_access_student_id",
        "test_access",
        type_="foreignkey",
    )
    op.drop_column("test_access", "student_id")
    op.alter_column(
        "test_access",
        "batch_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
