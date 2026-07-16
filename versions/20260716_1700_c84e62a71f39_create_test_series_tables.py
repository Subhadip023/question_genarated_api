"""create test series tables

Revision ID: c84e62a71f39
Revises: a73db509e1c4
Create Date: 2026-07-16 17:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c84e62a71f39"
down_revision: Union[str, None] = "a73db509e1c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "test_series",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(8), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("org_id", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_test_series_id"), "test_series", ["id"], unique=False)
    op.create_index(op.f("ix_test_series_code"), "test_series", ["code"], unique=True)
    op.create_table(
        "series_questions",
        sa.Column("series_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["series_id"], ["test_series.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["question_id"], ["questions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("series_id", "question_id"),
        sa.UniqueConstraint("series_id", "position", name="uq_series_question_position"),
    )


def downgrade() -> None:
    op.drop_table("series_questions")
    op.drop_index(op.f("ix_test_series_code"), table_name="test_series")
    op.drop_index(op.f("ix_test_series_id"), table_name="test_series")
    op.drop_table("test_series")
