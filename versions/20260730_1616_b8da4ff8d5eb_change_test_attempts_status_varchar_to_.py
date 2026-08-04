"""change test_attempts status varchar to integer

Revision ID: b8da4ff8d5eb
Revises: 97c0087696bb
Create Date: 2026-07-30 16:16:04.425063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8da4ff8d5eb'
down_revision: Union[str, None] = '97c0087696bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    conn = op.get_bind()

    # Convert old string values to integer values
    conn.execute(
        sa.text("""
            UPDATE test_attempts
            SET status = CASE
                WHEN status = 'in_progress' THEN 0
                WHEN status = 'expired' THEN 1
                WHEN status = 'submitted' THEN 2
                WHEN status = 'force_submitted' THEN 3
                ELSE 0
            END
        """)
    )

    # Change column type and default
    op.alter_column(
        "test_attempts",
        "status",
        existing_type=sa.String(length=20),
        type_=sa.Integer(),
        existing_nullable=False,
        server_default=sa.text("0"),
    )


def downgrade() -> None:

    op.alter_column(
        "test_attempts",
        "status",
        existing_type=sa.Integer(),
        type_=sa.String(length=20),
        existing_nullable=False,
    )
