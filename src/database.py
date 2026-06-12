from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from src.core.config import get_settings

settings = get_settings()

# echo=True will print SQLAlchemy's SQL queries to the terminal for debugging purposes.
engine = create_async_engine(settings.DATABASE_URL, echo=settings.IS_DEBUG, future=True)

# Session factory for generating async database sessions
async_session_local = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Declarative base class for all SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Dependency injector to provide async database sessions per request
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_local() as session:
        try:
            yield session
        finally:
            await session.close()