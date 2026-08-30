"""Database layer for RCS Backend."""
from . import models, session

__all__ = ["models", "session", "sys_models", "init_db", "session_scope"]

from .session import init_db

# Imported last so that `rcs.db.models` is fully initialised before sys_models
# (which does `from rcs.db.models import Base`) registers its tables on
# Base.metadata.  Placing it earlier would trigger a circular import.
from . import sys_models  # noqa: F401


async def session_scope():
    """Async context manager yielding an AsyncSession (postgres/sqlite only)."""
    from .session import session as _session

    async for s in _session():
        yield s
