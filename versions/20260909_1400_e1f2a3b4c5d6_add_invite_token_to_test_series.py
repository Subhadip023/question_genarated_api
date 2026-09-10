"""add invite_token to test_series

Revision ID: e1f2a3b4c5d6
Revises: dc3db448d7ca
Create Date: 2026-09-09 14:00:00.000000

"""
import hashlib
import secrets
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, None] = "dc3db448d7ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    # Check if column already exists to prevent duplicate column errors
    inspector = sa.inspect(connection)
    columns = [c["name"] for c in inspector.get_columns("test_series")]
    if "invite_token" not in columns:
        op.add_column(
            "test_series",
            sa.Column("invite_token", sa.String(255), nullable=True),
        )

    indexes = [idx["name"] for idx in inspector.get_indexes("test_series")]
    if "ix_test_series_invite_token" not in indexes:
        op.create_index(
            "ix_test_series_invite_token",
            "test_series",
            ["invite_token"],
            unique=True,
        )

    # Backfill existing invite_only series without an invite_token
    existing_invites = connection.execute(
        sa.text(
            "SELECT id FROM test_series "
            "WHERE access_type = 'invite_only' AND (invite_token IS NULL OR invite_token = '')"
        )
    ).all()

    for (series_id,) in existing_invites:
        token = secrets.token_urlsafe(24)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        connection.execute(
            sa.text(
                "UPDATE test_series SET invite_token = :token, invite_token_hash = :token_hash "
                "WHERE id = :id"
            ),
            {"token": token, "token_hash": token_hash, "id": series_id},
        )


def downgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    indexes = [idx["name"] for idx in inspector.get_indexes("test_series")]
    if "ix_test_series_invite_token" in indexes:
        op.drop_index("ix_test_series_invite_token", table_name="test_series")

    columns = [c["name"] for c in inspector.get_columns("test_series")]
    if "invite_token" in columns:
        op.drop_column("test_series", "invite_token")
