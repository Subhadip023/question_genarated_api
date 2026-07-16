"""create_topics_table

Revision ID: f37fce218399
Revises: f73ba5d8e2c4
Create Date: 2026-07-17 00:04:07.773571

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'f37fce218399'
down_revision: Union[str, None] = 'f73ba5d8e2c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('topics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('org_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('color', sa.String(length=50), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_topics_id'), 'topics', ['id'], unique=False)
    op.add_column('questions', sa.Column('topic_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_questions_topic_id', 'questions', 'topics', ['topic_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint('fk_questions_topic_id', 'questions', type_='foreignkey')
    op.drop_column('questions', 'topic_id')
    op.drop_index(op.f('ix_topics_id'), table_name='topics')
    op.drop_table('topics')
