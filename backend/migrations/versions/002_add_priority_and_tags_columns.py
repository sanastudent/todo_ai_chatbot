"""Add priority and tags columns to task table

Revision ID: 002_add_priority_and_tags_columns
Revises: 001_initial_schema
Create Date: 2026-01-19 19:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_priority_and_tags_columns'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add priority column with default value 'medium'
    op.add_column('task', sa.Column('priority', sa.String(length=10), nullable=False, default='medium'))

    # Add tags column with default value '[]'
    op.add_column('task', sa.Column('tags', sa.String(length=2000), nullable=False, default='[]'))


def downgrade() -> None:
    # Remove tags column
    op.drop_column('task', 'tags')

    # Remove priority column
    op.drop_column('task', 'priority')