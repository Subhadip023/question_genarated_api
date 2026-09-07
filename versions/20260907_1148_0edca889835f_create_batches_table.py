"""create batches table

Revision ID: 0edca889835f
Revises: 64b7e81714e0
Create Date: 2026-09-07 11:48:47.573364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0edca889835f'
down_revision: Union[str, None] = '64b7e81714e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "batches",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "org_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "supervisor",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
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

        sa.Column(
            "deleted_at",
            sa.DateTime(),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(
            ["org_id"],
            ["organizations.id"],
        ),

        sa.ForeignKeyConstraint(
            ["supervisor"],
            ["users.id"],
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_batches_org_id",
        "batches",
        ["org_id"],
        unique=False,
    )

    op.create_index(
        "ix_batches_supervisor",
        "batches",
        ["supervisor"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_batches_supervisor",
        table_name="batches",
    )

    op.drop_index(
        "ix_batches_org_id",
        table_name="batches",
    )

    op.drop_table("batches")
