"""create question sets table

Revision ID: 01c62c474695
Revises: f37fce218399
Create Date: 2026-07-28 12:32:24.313055

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01c62c474695'
down_revision: Union[str, None] = 'f37fce218399'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "question_sets",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            index=True
        ),

        sa.Column(
            "name",
            sa.String(255),
            nullable=False
        ),

        sa.Column(
            "org_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true")
        ),

        sa.Column(
            "visibility",
            sa.SmallInteger(),
            nullable=False,
            server_default="0"
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now()
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now()
        ),

        sa.ForeignKeyConstraint(
            ["org_id"],
            ["organizations.id"]
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"]
        )
    )


def downgrade() -> None:
    op.drop_table("question_sets")
