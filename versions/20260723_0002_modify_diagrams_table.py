"""modify_diagrams_table

Revision ID: 0002modifydiagrams
Revises: 0001adddiagrams
Create Date: 2026-07-23 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0002modifydiagrams'
down_revision: Union[str, None] = '0001adddiagrams'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('check_diagrams_id_0_or_1', 'diagrams', type_='check')
    op.create_check_constraint('check_diagrams_type_0_or_1', 'diagrams', 'type IN (0,1)')
    op.alter_column(
        'diagrams',
        'id',
        existing_type=sa.Integer(),
        autoincrement=True,
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'diagrams',
        'id',
        existing_type=sa.Integer(),
        autoincrement=False,
        existing_nullable=False,
    )
    op.drop_constraint('check_diagrams_type_0_or_1', 'diagrams', type_='check')
    op.create_check_constraint('check_diagrams_id_0_or_1', 'diagrams', 'id IN (0,1)')
