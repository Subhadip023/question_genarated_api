"""merge migration heads

Revision ID: 6eb2ff9bde8a
Revises: e1f2a3b4c5d6, 731e31f970b7
Create Date: 2026-09-15 15:59:42.738654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6eb2ff9bde8a'
down_revision: Union[str, None] = ('e1f2a3b4c5d6', '731e31f970b7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
