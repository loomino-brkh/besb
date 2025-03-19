from logging.config import fileConfig
import logging
from sqlalchemy import engine_from_config, pool, inspect
from alembic import context
import os
import sys
import importlib
import glob
# from pathlib import Path
from sqlmodel import SQLModel

# Set up custom logger for migration process
logger = logging.getLogger("alembic.migration")

# Add the project root to path to ensure proper imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Ensure we can find models in the main package
logger.info("Starting dynamic import of model files")

# Get the path to the main directory within the project
main_dir = os.path.join(project_root, 'main')
if not os.path.exists(main_dir):
    logger.warning(f"Main directory not found at {main_dir}")

# Import all Python modules that might contain SQLModel models
# Structure follows api_besb/main/... pattern with subdirectories
known_packages = ['core', 'endpoints', 'schema']

# Track imported modules to avoid redundant imports
imported_modules = set()
imported_tables = set()

# First import main module and its __init__
try:
    importlib.import_module('main')
    imported_modules.add('main')
    logger.info("Successfully imported main package")
except Exception as e:
    logger.warning(f"Could not import main package: {e}")

# Import modules from known directories
for package in known_packages:
    package_path = f'main.{package}'
    if package_path not in imported_modules:
        try:
            importlib.import_module(package_path)
            imported_modules.add(package_path)
            logger.info(f"Successfully imported package {package_path}")
        except Exception as e:
            logger.warning(f"Could not import package {package_path}: {e}")

# Check if a table name already exists in metadata
def is_table_defined(table_name):
    return table_name in target_metadata.tables

# Use recursive glob to find and import all Python files
for file_path in glob.glob(os.path.join(main_dir, '**', '*.py'), recursive=True):
    # Skip __pycache__ directories and migration files
    if '__pycache__' in file_path or 'migrations' in file_path:
        continue

    # Convert file path to module path for importing
    rel_path = os.path.relpath(file_path, start=project_root)
    module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')

    # Skip already imported __init__ files and modules to avoid duplicate imports
    if module_path.endswith('__init__') or module_path in imported_modules:
        continue

    try:
        logger.debug(f"Attempting to import: {module_path}")

        # Before importing, check the current state of tables
        tables_before = set(SQLModel.metadata.tables.keys())

        # Import the module
        importlib.import_module(module_path)
        imported_modules.add(module_path)

        # Check which new tables were added
        tables_after = set(SQLModel.metadata.tables.keys())
        new_tables = tables_after - tables_before

        # Log the newly added tables
        if new_tables:
            logger.debug(f"Module {module_path} added tables: {', '.join(new_tables)}")
            imported_tables.update(new_tables)

        logger.debug(f"Successfully imported: {module_path}")
    except Exception as e:
        if "already defined for this MetaData instance" in str(e):
            logger.warning(f"Skipping {module_path} due to table redefinition: {e}")
        else:
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

def check_existing_tables(connection):
    """
    Check which tables from our metadata already exist in the database.

    Args:
        connection: SQLAlchemy connection object

    Returns:
        dict: Dictionary of table_name: exists_bool pairs
    """
    inspector = inspect(connection)
    existing_tables = inspector.get_table_names()

    table_status = {}
    for table_name in target_metadata.tables.keys():
        exists = table_name in existing_tables
        table_status[table_name] = exists
        if exists:
            logger.info(f"Table '{table_name}' already exists in the database - will be preserved")

    return table_status

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

        # Check for existing tables
        existing_tables = check_existing_tables(connection)

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Enhanced migration options
            compare_type=True,  # Detect column type changes
            compare_server_default=True,  # Detect default value changes
            render_as_batch=True,  # Better handling of ALTER TABLE operations
            include_schemas=True,  # Include schema-level operations
            # Skip creating tables that already exist
            include_object=lambda obj, name, type_, reflected, compare_to:
                not (type_ == "table" and name in existing_tables and existing_tables[name])
                if type_ == "table" else True
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
