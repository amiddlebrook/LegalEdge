"""Database session management."""
from typing import AsyncIterator

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Provide a DB session for dependency injection."""

    async with SessionLocal() as session:
        yield session


async def maybe_get_session() -> AsyncIterator[AsyncSession | None]:
    """Attempt to provide a DB session but continue gracefully if unavailable."""

    try:
        async with SessionLocal() as session:
            yield session
    except Exception as exc:  # pragma: no cover - defensive log
        logger.debug("Database session unavailable: %s", exc)
        yield None