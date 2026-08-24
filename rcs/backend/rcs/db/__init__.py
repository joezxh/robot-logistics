"""Database layer for RCS Backend."""
from . import models, session

__all__ = ["models", "session", "init_db", "session_scope"]

from .session import init_db


async def session_scope():
    """Async context manager yielding an AsyncSession (postgres/sqlite only)."""
    from .session import session as _session

    async for s in _session():
        yield s
