"""add indexes for uncovered foreign-key columns

Revision ID: 91c8b4d2e6f0
Revises: cdf243772355
Create Date: 2026-10-05 16:49:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "91c8b4d2e6f0"
down_revision: Union[str, None] = "cdf243772355"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


INDEXES = {
    "questions": ("topic_id",),
    "organization_users": ("user_id",),
    "test_series": ("created_by",),
    "series_questions": ("question_id",),
    "question_sets": ("org_id", "user_id"),
    "question_set_questions": ("set_id", "question_id"),
    "test_attempts": ("series_id",),
    "attempt_questions": ("attempt_id",),
    "teacher_groups": ("created_by", "supervisor"),
    "group_teachers": ("group_id", "teacher_id"),
}

def _has_leading_column_index(inspector, table_name: str, column_name: str) -> bool:
    return any(
        index.get("column_names")
        and index["column_names"][0] == column_name
        for index in inspector.get_indexes(table_name)
    )


def _index_name(table_name: str, column_name: str) -> str:
    return f"ix_fk_{table_name}_{column_name}"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table_name, columns in INDEXES.items():
        if table_name not in existing_tables:
            continue
        table_columns = {column["name"] for column in inspector.get_columns(table_name)}
        for column_name in columns:
            if column_name in table_columns and not _has_leading_column_index(
                inspector, table_name, column_name
            ):
                op.create_index(
                    _index_name(table_name, column_name),
                    table_name,
                    [column_name],
                )
                inspector = sa.inspect(bind)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table_name, columns in INDEXES.items():
        if table_name not in existing_tables:
            continue
        index_names = {index["name"] for index in inspector.get_indexes(table_name)}
        for column_name in columns:
            index_name = _index_name(table_name, column_name)
            if index_name in index_names:
                op.drop_index(index_name, table_name=table_name)
                inspector = sa.inspect(bind)
                index_names.remove(index_name)
