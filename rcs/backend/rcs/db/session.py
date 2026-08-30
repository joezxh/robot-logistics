"""Async PostgreSQL engine + session factory (asyncpg)."""
from __future__ import annotations
import asyncio
from collections.abc import AsyncIterator
from weakref import WeakKeyDictionary

from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine,
)

from rcs.config import get_settings
from rcs.db.models import Base

# asyncpg connection pools are bound to the event loop they were created on.
# Cache one engine per loop so a pool is never reused across loops (pytest
# creates a fresh loop per async test, TestClient runs its own portal loop).
_engines: WeakKeyDictionary[asyncio.AbstractEventLoop, AsyncEngine] = WeakKeyDictionary()
_sessionmakers: WeakKeyDictionary[
    asyncio.AbstractEventLoop, async_sessionmaker[AsyncSession]
] = WeakKeyDictionary()
_initialized = False


def get_engine() -> AsyncEngine:
    loop = asyncio.get_running_loop()
    engine = _engines.get(loop)
    if engine is None:
        engine = create_async_engine(get_settings().database_url, echo=False, future=True)
        _engines[loop] = engine
    return engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    loop = asyncio.get_running_loop()
    maker = _sessionmakers.get(loop)
    if maker is None:
        maker = async_sessionmaker(get_engine(), expire_on_commit=False)
        _sessionmakers[loop] = maker
    return maker


async def init_db() -> None:
    global _initialized
    if _initialized:
        return
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    _initialized = True


async def session() -> AsyncIterator[AsyncSession]:
    async with get_sessionmaker()() as s:
        yield s


async def dispose_engine() -> None:
    """Dispose the engine bound to the running event loop, if there is one.

    Engines are cached per event loop (see ``_engines``) and their asyncpg pools
    are never closed implicitly. Anything that churns through event loops —
    pytest-asyncio creates a fresh loop per async test — must dispose
    explicitly, or every test leaks a connection pool until PostgreSQL refuses
    new connections with ``TooManyConnectionsError``.

    Safe to call when no engine exists for the current loop; it is a no-op.
    """
    loop = asyncio.get_running_loop()
    engine = _engines.pop(loop, None)
    _sessionmakers.pop(loop, None)
    if engine is not None:
        await engine.dispose()