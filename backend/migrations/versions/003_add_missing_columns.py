"""Add missing priority and tags columns to task table

Revision ID: 003_add_missing_columns
Revises: 001_initial_schema
Create Date: 2026-01-19 19:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_missing_columns'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add priority column with default value 'medium' if it doesn't exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('task')]

    if 'priority' not in columns:
        op.add_column('task', sa.Column('priority', sa.String(length=10), nullable=False, default='medium'))

    if 'tags' not in columns:
        op.add_column('task', sa.Column('tags', sa.String(length=2000), nullable=False, default='[]'))


def downgrade() -> None:
    # Remove tags column if it exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('task')]

    if 'tags' in columns:
        op.drop_column('task', 'tags')

    # Remove priority column if it exists
    if 'priority' in columns:
        op.drop_column('task', 'priority')