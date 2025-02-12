from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os, sys, importlib, glob
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all models - dynamically import all Python files that might contain models
from sqlmodel import SQLModel

# Dynamically import all Python files in the main directory
main_dir = Path(os.path.dirname(os.path.dirname(__file__)))
for file_path in glob.glob(str(main_dir / "*.py")):
    if not file_path.endswith('env.py'):  # Skip this env.py file
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"Warning: Could not import {module_name}: {e}")

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set SQLModel's metadata for Alembic
target_metadata = SQLModel.metadata

def get_url():
    """Get database URL from environment variables."""
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_CONTAINER_NAME')
    db = os.getenv('POSTGRES_DB')
    return f"postgresql://{user}:{password}@{host}:5432/{db}"

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Enhanced migration options
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
        render_as_batch=True,  # Better handling of ALTER TABLE operations
        include_schemas=True,  # Include schema-level operations
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    if configuration is not None:
        configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Enhanced migration options
            compare_type=True,  # Detect column type changes
            compare_server_default=True,  # Detect default value changes
            render_as_batch=True,  # Better handling of ALTER TABLE operations
            include_schemas=True,  # Include schema-level operations
        )

        with context.begin_transaction():
            context.run_migrations()

def run_migrations():
    """Run migrations in either 'online' or 'offline' mode."""
    try:
        if context.is_offline_mode():
            run_migrations_offline()
        else:
            run_migrations_online()
    except Exception as e:
        print(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    run_migrations()
