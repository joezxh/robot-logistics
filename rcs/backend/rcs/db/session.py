"""Async PostgreSQL engine + session factory (asyncpg)."""
from __future__ import annotations
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine,
)

from rcs.config import get_settings
from rcs.db import models

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None
_initialized = False


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(get_settings().database_url, echo=False, future=True)
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _sessionmaker


async def init_db() -> None:
    global _initialized
    if _initialized:
        return
    async with get_engine().begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    _initialized = True


async def session() -> AsyncIterator[AsyncSession]:
    async with get_sessionmaker()() as s:
        yield s