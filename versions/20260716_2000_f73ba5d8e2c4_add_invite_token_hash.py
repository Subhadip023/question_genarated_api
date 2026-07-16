"""replace exposed invite codes with hashed opaque tokens

Revision ID: f73ba5d8e2c4
Revises: e62a94c7d5b1
Create Date: 2026-07-16 20:00:00
"""

import hashlib
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f73ba5d8e2c4"
down_revision: Union[str, None] = "e62a94c7d5b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "test_series",
        sa.Column("invite_token_hash", sa.String(64), nullable=True),
    )
    connection = op.get_bind()
    existing_invites = connection.execute(
        sa.text(
            "SELECT id, code FROM test_series "
            "WHERE access_type = 'invite_only' AND code IS NOT NULL"
        )
    ).all()
    for series_id, code in existing_invites:
        token_hash = hashlib.sha256(code.encode()).hexdigest()
        connection.execute(
            sa.text(
                "UPDATE test_series SET invite_token_hash = :token_hash, code = NULL "
                "WHERE id = :id"
            ),
            {"token_hash": token_hash, "id": series_id},
        )
    op.create_index(
        "ix_test_series_invite_token_hash",
        "test_series",
        ["invite_token_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_test_series_invite_token_hash", table_name="test_series")
    op.drop_column("test_series", "invite_token_hash")
