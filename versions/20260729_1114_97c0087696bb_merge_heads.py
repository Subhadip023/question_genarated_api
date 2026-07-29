"""Merge heads

Revision ID: 97c0087696bb
Revises: 0002modifydiagrams, 3b95e10c39fe
Create Date: 2026-07-29 11:14:38.891491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97c0087696bb'
down_revision: Union[str, None] = ('0002modifydiagrams', '3b95e10c39fe')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
