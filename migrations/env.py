"""Alembic environment configuration — reads DB URL from .env via app.config.settings."""

from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from sqlalchemy.engine import URL

from alembic import context

# Import settings to get the DB URL from .env
from app.config import settings

# Import Base and all models so Alembic can detect schema changes
from app.database import Base
import app.models.question  # noqa: F401
import app.models.topic  # noqa: F401
import app.models.question_option  # noqa: F401
import app.models.user  # noqa: F401
import app.models.organization  # noqa: F401
import app.models.organization_user  # noqa: F401
import app.models.test_series  # noqa: F401
import app.models.series_question  # noqa: F401
import app.models.test_attempt  # noqa: F401

# Alembic Config object
config = context.config

# Build the DB URL object directly — avoids configparser % interpolation errors
db_url = URL.create(
    drivername="mysql+pymysql",
    username=settings.mysql_user,
    password=settings.mysql_password,
    host=settings.mysql_host,
    port=settings.mysql_port,
    database=settings.mysql_database,
)

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Point Alembic at our models' metadata for --autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection needed)."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (live DB connection)."""
    connectable = create_engine(db_url, poolclass=pool.NullPool)
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
