"""create question set questions table

Revision ID: 3b95e10c39fe
Revises: 01c62c474695
Create Date: 2026-07-28 12:35:31.962375

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b95e10c39fe'
down_revision: Union[str, None] = '01c62c474695'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "question_set_questions",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            index=True
        ),

        sa.Column(
            "set_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "question_id",
            sa.Integer(),
            nullable=False
        ),


        sa.ForeignKeyConstraint(
            ["set_id"],
            ["question_sets.id"],
            ondelete="CASCADE"
        ),

        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"]
        )
    )


def downgrade() -> None:
    op.drop_table("question_set_questions")
