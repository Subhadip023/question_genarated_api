"""add teacher group and supervisor to test series

Revision ID: d351f2d57b83
Revises: 621a31b22c49
Create Date: 2026-09-07 15:55:04.652246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd351f2d57b83'
down_revision: Union[str, None] = '621a31b22c49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "test_series",
        sa.Column(
            "teacher_group_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "test_series",
        sa.Column(
            "supervisor_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_test_series_teacher_group_id",
        "test_series",
        ["teacher_group_id"],
    )

    op.create_index(
        "ix_test_series_supervisor_id",
        "test_series",
        ["supervisor_id"],
    )

    op.create_foreign_key(
        "fk_test_series_teacher_group_id",
        "test_series",
        "teacher_groups",
        ["teacher_group_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_test_series_supervisor_id",
        "test_series",
        "users",
        ["supervisor_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_test_series_supervisor_id",
        "test_series",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_test_series_teacher_group_id",
        "test_series",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_test_series_supervisor_id",
        table_name="test_series",
    )

    op.drop_index(
        "ix_test_series_teacher_group_id",
        table_name="test_series",
    )

    op.drop_column("test_series", "supervisor_id")
    op.drop_column("test_series", "teacher_group_id")
