"""Root conftest: add rcs/backend/ to sys.path."""
import sys
from pathlib import Path

import pytest
import pytest_asyncio

_ROOT = Path(__file__).parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "_rcs"))
sys.path.insert(0, str(_ROOT / "_shared"))


@pytest_asyncio.fixture(autouse=True)
async def _dispose_db_engine():
    """Close the per-event-loop DB engine once a test finishes.

    ``rcs.db.session`` caches one async engine per event loop and never closes
    it. pytest-asyncio hands each async test its own loop, so without this the
    suite leaks one asyncpg connection pool per test and PostgreSQL eventually
    refuses connections (``TooManyConnectionsError``).
    """
    yield
    from rcs.db import session as db_session
    await db_session.dispose_engine()
