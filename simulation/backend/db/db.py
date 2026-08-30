"""Database connection and session management."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from backend.utils.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def __getattr__(name: str):
    """Lazy module-level exports for engine and SessionLocal."""
    if name == "engine":
        return _engine
    if name == "SessionLocal":
        return _session_factory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def init_db(url: Optional[str] = None) -> AsyncEngine:
    """Initialize the database engine and create all tables."""
    global _engine, _session_factory
    
    db_url = url or settings.database_url
    _engine = create_async_engine(db_url, echo=False, future=True)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    
    # Import models so SQLAlchemy registers them
    from backend.db import models  # noqa: F401
    
    return _engine


def get_engine() -> Optional[AsyncEngine]:
    """Get the current database engine."""
    return _engine


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session (context manager)."""
    if _session_factory is None:
        init_db()
    assert _session_factory is not None
    session = _session_factory()
    try:
        yield session
    finally:
        await session.close()


async def create_tables() -> None:
    """Create all tables in the database."""
    if _engine is None:
        init_db()
    assert _engine is not None
    from backend.db import models  # noqa: F401
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
