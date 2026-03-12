"""Initial schema: Task, Conversation, Message

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-01-05 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create Task table
    op.create_table('task',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_user_id', 'task', ['user_id'])
    op.create_index('ix_task_user_completed', 'task', ['user_id', 'completed'])
    op.create_index('ix_task_user_created', 'task', ['user_id', 'created_at'], postgresql_ops={'created_at': 'DESC'})

    # Create Conversation table
    op.create_table('conversation',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversation_user_id', 'conversation', ['user_id'])
    op.create_index('ix_conversation_user_updated', 'conversation', ['user_id', 'updated_at'], postgresql_ops={'updated_at': 'DESC'})

    # Create Message table
    op.create_table('message',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('conversation_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_message_user_id', 'message', ['user_id'])
    op.create_index('ix_message_conversation_id', 'message', ['conversation_id'])
    op.create_index('ix_message_conversation_created', 'message', ['conversation_id', 'created_at'], postgresql_ops={'created_at': 'ASC'})


def downgrade() -> None:
    # Drop Message table first (due to foreign key constraint)
    op.drop_index('ix_message_conversation_created')
    op.drop_index('ix_message_conversation_id')
    op.drop_index('ix_message_user_id')
    op.drop_table('message')

    # Drop Conversation table
    op.drop_index('ix_conversation_user_updated')
    op.drop_index('ix_conversation_user_id')
    op.drop_table('conversation')

    # Drop Task table
    op.drop_index('ix_task_user_created')
    op.drop_index('ix_task_user_completed')
    op.drop_index('ix_task_user_id')
    op.drop_table('task')