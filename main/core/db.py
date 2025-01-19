from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator, AsyncGenerator
import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration with fallbacks
POSTGRES_CONTAINER = os.getenv('POSTGRES_CONTAINER_NAME', 'localhost')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'besb_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'NsJTxYB5VY7hTN3EAulY1Ice132qKhgH')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'besb_db')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

# Connection URLs for both sync and async engines
SYNC_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_CONTAINER}:{POSTGRES_PORT}/{POSTGRES_DB}"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_CONTAINER}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Engine configuration
POOL_SIZE = int(os.getenv('POOL_SIZE', '5'))
MAX_OVERFLOW = int(os.getenv('MAX_OVERFLOW', '10'))
POOL_TIMEOUT = int(os.getenv('POOL_TIMEOUT', '30'))
POOL_RECYCLE = int(os.getenv('POOL_RECYCLE', '1800'))  # 30 minutes
CONNECT_TIMEOUT = int(os.getenv('CONNECT_TIMEOUT', '10'))  # 10 seconds

# Create engines with optimized configurations
engine = create_engine(
    SYNC_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": CONNECT_TIMEOUT,
        "application_name": "fastapi_app"  # Helps identify connections in pg_stat_activity
    }
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,
    connect_args={
        "timeout": CONNECT_TIMEOUT
    }
)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Synchronous database session generator with retry mechanism.
    """
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def _get_session():
        try:
            db = Session(engine)
            return db
        except Exception as e:
            logger.error(f"Failed to create database session: {e}")
            raise

    db = _get_session()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous database session generator with retry mechanism.
    """
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def _get_async_session():
        try:
            async with AsyncSession(async_engine) as session:
                return session
        except Exception as e:
            logger.error(f"Failed to create async database session: {e}")
            raise

    try:
        async_session = await _get_async_session()
        yield async_session
    except Exception as e:
        logger.error(f"Async database session error: {e}")
        await async_session.rollback()
        raise
    finally:
        await async_session.close()

# Helper function to check database health
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def check_database_health() -> bool:
    """
    Check if database is responsive and healthy.
    Returns True if database is healthy, raises exception otherwise.
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise

# Create all tables defined in SQLModel metadata
def init_db():
    """
    Initialize database tables with error handling.
    """
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
