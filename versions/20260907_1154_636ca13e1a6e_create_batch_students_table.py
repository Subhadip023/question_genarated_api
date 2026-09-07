"""create batch_students table

Revision ID: 636ca13e1a6e
Revises: 0edca889835f
Create Date: 2026-09-07 11:54:05.232071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '636ca13e1a6e'
down_revision: Union[str, None] = '0edca889835f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "batch_students",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "batch_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "student_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.ForeignKeyConstraint(
            ["batch_id"],
            ["batches.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "batch_id",
            "student_id",
            name="uq_batch_student",
        ),
    )

    op.create_index(
        "ix_batch_students_batch_id",
        "batch_students",
        ["batch_id"],
        unique=False,
    )

    op.create_index(
        "ix_batch_students_student_id",
        "batch_students",
        ["student_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_batch_students_student_id",
        table_name="batch_students",
    )

    op.drop_index(
        "ix_batch_students_batch_id",
        table_name="batch_students",
    )

    op.drop_table("batch_students")
