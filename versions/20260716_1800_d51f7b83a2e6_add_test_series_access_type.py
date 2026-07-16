"""add test series access type

Revision ID: d51f7b83a2e6
Revises: c84e62a71f39
Create Date: 2026-07-16 18:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d51f7b83a2e6"
down_revision: Union[str, None] = "c84e62a71f39"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "test_series",
        sa.Column(
            "access_type",
            sa.String(20),
            nullable=False,
            server_default="invite_only",
        ),
    )
    op.alter_column(
        "test_series",
        "code",
        existing_type=sa.String(8),
        nullable=True,
    )


def downgrade() -> None:
    connection = op.get_bind()
    public_ids = connection.execute(
        sa.text("SELECT id FROM test_series WHERE code IS NULL")
    ).scalars().all()
    for series_id in public_ids:
        connection.execute(
            sa.text("UPDATE test_series SET code = :code WHERE id = :id"),
            {"code": f"PUB{series_id:05d}"[-8:], "id": series_id},
        )
    op.alter_column(
        "test_series",
        "code",
        existing_type=sa.String(8),
        nullable=False,
    )
    op.drop_column("test_series", "access_type")
