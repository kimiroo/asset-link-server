from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.core.config import get_settings

settings = get_settings()

# Create the async database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.IS_DEBUG,
    future=True,
    pool_pre_ping=True,
    connect_args={
        "statement_cache_size": 0,
        "max_cached_statement_lifetime": 0
    }
)

# Session factory for generating async database sessions
async_session_local = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)