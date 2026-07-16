"""create test attempt tables

Revision ID: e62a94c7d5b1
Revises: d51f7b83a2e6
Create Date: 2026-07-16 19:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e62a94c7d5b1"
down_revision: Union[str, None] = "d51f7b83a2e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    existing_tables = sa.inspect(op.get_bind()).get_table_names()
    if "test_attempts" not in existing_tables:
        op.create_table(
            "test_attempts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("series_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("status", sa.String(20), nullable=False, server_default="in_progress"),
            sa.Column("score", sa.Numeric(10, 2), nullable=False, server_default="0"),
            sa.Column("total_marks", sa.Numeric(10, 2), nullable=False, server_default="0"),
            sa.ForeignKeyConstraint(["series_id"], ["test_series.id"], ondelete="RESTRICT"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_test_attempts_id"), "test_attempts", ["id"], unique=False)
        op.create_index("ix_test_attempts_user_id", "test_attempts", ["user_id"], unique=False)
    op.create_table(
        "attempt_questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attempt_id", sa.Integer(), nullable=False),
        sa.Column("original_question_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("marks", sa.Numeric(10, 2), nullable=False),
        sa.Column("options_snapshot", sa.Text(), nullable=False),
        sa.Column("correct_option_id", sa.Integer(), nullable=True),
        sa.Column("selected_option_id", sa.Integer(), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("marks_awarded", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["attempt_id"], ["test_attempts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("attempt_id", "position", name="uq_attempt_question_position"),
    )
    op.create_index(
        op.f("ix_attempt_questions_id"), "attempt_questions", ["id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_attempt_questions_id"), table_name="attempt_questions")
    op.drop_table("attempt_questions")
    op.drop_index("ix_test_attempts_user_id", table_name="test_attempts")
    op.drop_index(op.f("ix_test_attempts_id"), table_name="test_attempts")
    op.drop_table("test_attempts")
