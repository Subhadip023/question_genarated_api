"""add immutable unique organization code

Revision ID: f2a8c190b4de
Revises: e91c4a72d6f0
Create Date: 2026-07-16 15:00:00
"""

import secrets
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2a8c190b4de"
down_revision: Union[str, None] = "e91c4a72d6f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("code", sa.String(6), nullable=True))

    connection = op.get_bind()
    organization_ids = connection.execute(
        sa.text("SELECT id FROM organizations")
    ).scalars().all()
    used_codes: set[str] = set()
    for organization_id in organization_ids:
        while True:
            code = str(secrets.randbelow(900000) + 100000)
            if code not in used_codes:
                used_codes.add(code)
                break
        connection.execute(
            sa.text("UPDATE organizations SET code = :code WHERE id = :id"),
            {"code": code, "id": organization_id},
        )

    op.alter_column(
        "organizations",
        "code",
        existing_type=sa.String(6),
        nullable=False,
    )
    op.create_unique_constraint("uq_organizations_code", "organizations", ["code"])


def downgrade() -> None:
    op.drop_constraint("uq_organizations_code", "organizations", type_="unique")
    op.drop_column("organizations", "code")
