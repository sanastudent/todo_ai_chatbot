from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import create_engine
from sqlmodel import SQLModel

from alembic import context

# Import all models to ensure they're registered with SQLModel
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add backend/ to path

from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata to SQLModel's metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get the database URL from environment variable or config
    db_url = os.getenv("DATABASE_URL", "sqlite:///./todo_chatbot_dev.db")

    # Handle different database types for sync engine
    if db_url.startswith("postgresql+asyncpg://"):
        sync_db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    elif db_url.startswith("sqlite+aiosqlite://"):
        sync_db_url = db_url.replace("sqlite+aiosqlite://", "sqlite://")
    else:
        sync_db_url = db_url

    connectable = create_engine(sync_db_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Force offline mode for autogenerate to avoid needing a database connection
try:
    if context.is_offline_mode() or (hasattr(context.config.cmd_opts, 'autogenerate') and context.config.cmd_opts.autogenerate):
        run_migrations_offline()
    else:
        run_migrations_online()
except AttributeError:
    # Handle case where autogenerate attribute doesn't exist
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
