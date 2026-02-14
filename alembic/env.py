"""
Alembic environment — loads DATABASE_URL from .env via our Settings,
and points autogenerate at the SQLAlchemy Base.metadata.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure the project root is on sys.path so `src.*` imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.config import get_settings
from src.db.models import Base  # imports ALL models → metadata is complete

# Alembic Config object
config = context.config

# Override sqlalchemy.url from our .env settings (single source of truth)
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

# Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Autogenerate target
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL to stdout)."""
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
    """Run migrations in 'online' mode (connect to DB)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
