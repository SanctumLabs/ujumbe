from logging.config import fileConfig
import re

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from alembic.script import write_hooks

from app.database.models import Base
from app.settings import DatabaseSettings

db_settings = DatabaseSettings()

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

# Automatically audit tables with an updated_by column
create_table = re.compile("op\\.create_table\\('([^']+)'")


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

@write_hooks.register("audit_log")
def add_audit_log(filename, options):
    lines = []
    is_downgrade = False
    tables = []
    current_table = None

    with open(filename) as f:
        for line in f:
            if "def downgrade" in line:
                is_downgrade = True

            if not is_downgrade:
                match = create_table.search(line)
                if match:
                    current_table = match.groups()[0]

                if "sa.Column('updated_by'" in line:
                    # We only audit tables that have a column
                    tables.append(current_table)

                if "### end Alembic commands" in line:
                    if tables:
                        lines.append("    from sqlalchemy.orm import sessionmaker\n")
                        lines.append("    Session = sessionmaker()\n")
                        lines.append("    bind = op.get_bind()\n")
                        lines.append("    session = Session(bind=bind)\n")
                        for table in tables:
                            lines.append(
                                f"    session.execute(\"SELECT audit.audit_table('{table}')\")\n"
                            )

            lines.append(line)

    with open(filename, "w") as f:
        f.writelines(lines)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = db_settings.db_url
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

    # Use the settings URL from our Pydantic settings object
    database_url = context.get_x_argument(as_dictionary=True).get("db_url")

    if database_url:
        config.set_main_option("sqlalchemy.url", database_url)
    else:
        config.set_main_option("sqlalchemy.url", db_settings.db_url)

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
