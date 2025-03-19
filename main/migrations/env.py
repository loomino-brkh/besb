from logging.config import fileConfig
import logging
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
import importlib
import glob
from pathlib import Path
from sqlmodel import SQLModel

# Set up custom logger for migration process
logger = logging.getLogger("alembic.migration")

# Add the main directory to the system path for proper module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Dynamically import all Python files that might contain SQLModel models
# This ensures Alembic can detect all model definitions for migration generation
logger.info("Starting dynamic import of model files")
main_dir = Path(os.path.dirname(os.path.dirname(__file__)))

# Use recursive glob to find all Python files including those in subdirectories
for file_path in glob.glob(str(main_dir / "**/*.py"), recursive=True):
    # Skip env.py and any other migration files to avoid circular imports
    if 'migrations' not in file_path and not file_path.endswith('env.py'):
        # Convert file path to proper module path for importing
        rel_path = os.path.relpath(file_path, start=str(main_dir.parent))
        module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')

        try:
            logger.debug(f"Attempting to import: {module_path}")
            importlib.import_module(module_path)
            logger.debug(f"Successfully imported: {module_path}")
        except Exception as e:
            logger.warning(f"Could not import {module_path}: {e}")

# Initialize the Alembic Config object
config = context.config

# Configure Python logging from Alembic config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
    logger.info("Loaded logging configuration from Alembic config file")

# Set SQLModel's metadata for Alembic to use for migrations
target_metadata = SQLModel.metadata
logger.info(f"Loaded metadata with {len(target_metadata.tables)} tables")

def get_url():
    """
    Get database URL from environment variables with validation.

    Returns:
        str: PostgreSQL connection URL

    Raises:
        ValueError: If required environment variables are missing
    """
    # Get database connection parameters with fallback defaults
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_CONTAINER_NAME', 'localhost')
    db = os.getenv('POSTGRES_DB')

    # Validate that required parameters are present
    missing_vars = []
    if not user:
        missing_vars.append('POSTGRES_USER')
    if not password:
        missing_vars.append('POSTGRES_PASSWORD')
    if not db:
        missing_vars.append('POSTGRES_DB')

    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    connection_url = f"postgresql://{user}:{password}@{host}:5432/{db}"
    logger.info(f"Database connection configured for host: {host}, database: {db}")
    return connection_url

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This mode generates SQL scripts rather than executing migrations directly.
    Useful for database administrators to review changes before applying them.
    """
    logger.info("Running migrations in offline mode")
    url = get_url()

    # Configure Alembic context for offline migration
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
        logger.info("Executing offline migrations")
        context.run_migrations()
        logger.info("Offline migrations completed successfully")

def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    This mode directly applies migrations to the connected database.
    """
    logger.info("Running migrations in online mode")

    # Get configuration from Alembic config file
    configuration = config.get_section(config.config_ini_section)

    # Validate configuration
    if configuration is None:
        error_msg = "Alembic configuration section is missing or invalid"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Set the database URL in the configuration
    configuration["sqlalchemy.url"] = get_url()

    # Create a database engine for the migration
    try:
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise

    # Execute migrations with the database connection
    with connectable.connect() as connection:
        logger.info("Database connection established")
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
            logger.info("Executing online migrations")
            context.run_migrations()
            logger.info("Online migrations completed successfully")

def run_migrations():
    """
    Run migrations in either 'online' or 'offline' mode based on Alembic context.

    This function handles the selection of migration mode and provides
    centralized error handling for the migration process.
    """
    logger.info("Starting database migration process")
    try:
        if context.is_offline_mode():
            logger.info("Detected offline mode")
            run_migrations_offline()
        else:
            logger.info("Detected online mode")
            run_migrations_online()
        logger.info("Migration process completed successfully")
    except Exception as e:
        logger.error(f"Error during migration: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    run_migrations()
