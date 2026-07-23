"""add_diagrams_table

Revision ID: 0001adddiagrams
Revises: f37fce218399
Create Date: 2026-07-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001adddiagrams'
down_revision: Union[str, None] = 'f37fce218399'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
    "diagrams",
    sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
    sa.Column("type", sa.Integer(), nullable=False, server_default="0"),
    sa.Column("ref_id", sa.Integer(), nullable=False, server_default="0"),
    sa.Column(
        "org_id",
        sa.Integer(),
        sa.ForeignKey("organizations.id"),
        nullable=False,
    ),
    sa.Column("user_id", sa.Integer(), nullable=False, server_default="0"),
    sa.Column("path", sa.String(length=1024), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint("id"),
    sa.CheckConstraint("id IN (0, 1)", name="check_diagrams_id_0_or_1"),
    )
    op.create_index(op.f('ix_diagrams_id'), 'diagrams', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_diagrams_id'), table_name='diagrams')
    op.drop_table('diagrams')