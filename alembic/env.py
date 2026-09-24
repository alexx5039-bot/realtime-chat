from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from logging.config import fileConfig
from sqlalchemy import create_engine

from sqlalchemy import pool
from chat.config import settings
from alembic import context


from chat.database import Base
from chat.models import (
    User,
    Conversation,
    ConversationMember,
    Message,
)
print("ENV FILE:", Path(__file__).resolve())
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata
print("ALEMBIC TABLES:", target_metadata.tables.keys())
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
    print(">>> RUNNING ONLINE MIGRATIONS")

    connectable = create_engine(
        settings.sync_database_url,
        poolclass=pool.NullPool,
        echo=True,
    )

    with connectable.begin() as connection:
        print(">>> CONNECTED TO DB")
        print("ALEMBIC DB:", connection.engine.url)

        print(
            "ALEMBIC DB TABLES:",
            connection.dialect.get_table_names(connection),
        )

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        print(">>> RUNNING MIGRATIONS")
        context.run_migrations()
        print(">>> MIGRATIONS FINISHED")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()