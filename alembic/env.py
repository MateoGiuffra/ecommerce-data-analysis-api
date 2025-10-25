import sys
import os
from os.path import abspath, dirname
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Añade la carpeta 'src' al path para que Alembic pueda encontrar tus módulos
sys.path.insert(0, abspath(dirname(dirname(__file__))))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- INICIO DE CAMBIOS PARA PRODUCCIÓN ---
# Lee la URL de la base de datos desde una variable de entorno si está disponible.
database_url = os.getenv('DATABASE_URL', config.get_main_option("sqlalchemy.url"))
config.set_main_option('sqlalchemy.url', database_url)

# --- INICIO DE CAMBIOS ---
# Importa la Base de tus modelos y los propios modelos
from src.database.base import Base
from src.database.models.user import User
target_metadata = Base.metadata
# --- FIN DE CAMBIOS ---

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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
