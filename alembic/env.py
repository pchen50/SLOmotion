from logging.config import fileConfig
import sys, os
from sqlalchemy import engine_from_config, pool
from alembic import context

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import Base

# Alembic Config object
config = context.config

# Load DB URI from environment and override config
config.set_main_option(
    "sqlalchemy.url",
    os.getenv(
        "POSTGRES_URI", "postgresql+psycopg2://myuser:mypassword@localhost/mydatabase"
    ),
)

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your metadata (for `--autogenerate`)
# from app.db import Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    if not configuration:
        raise Exception("No config section for Alembic")
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# Entry point
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
