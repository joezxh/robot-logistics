"""Tests for the UnifiedMap / MapDynamicState ORM models (Task 1).

Verifies persistence of the new ``robot_unified_maps`` / ``robot_map_dynamic_state``
tables and the unique constraint on (map_id, element_id).

Convention follows ``tests/unit/control/test_sitemap_service.py``: skip the module
if Postgres is unreachable, and use ``async for s in db_session.session()`` to
obtain an ``AsyncSession`` (``rcs.db.session.session`` is an async generator).
"""
from __future__ import annotations
import os

import pytest
from sqlalchemy import delete, select

from rcs.db import session as db_session


def _db_reachable() -> bool:
    url = os.environ.get("RCS_DATABASE_URL", "postgresql+asyncpg://rcs:rcs@localhost:5432/rcs_test")
    try:
        import socket
        tail = url.split("@", 1)[-1]
        host, port = tail.split("/", 1)[0].split(":", 1)
        s = socket.create_connection((host, int(port)), timeout=0.4)
        s.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.asyncio

if not _db_reachable():
    pytest.skip("PostgreSQL not reachable", allow_module_level=True)


@pytest.fixture(scope="module", autouse=True)
async def _prepare_db():
    await db_session.init_db()
    from rcs.db import models
    async for s in db_session.session():
        await s.execute(delete(models.MapDynamicState))
        await s.execute(delete(models.UnifiedMap))
        await s.commit()
    yield


async def test_unified_map_persists():
    from rcs.db.models import UnifiedMap

    async for s in db_session.session():
        s.add(UnifiedMap(map_id="t1", name="Test", geometry_json={"a": 1}))
        await s.commit()

    async for s in db_session.session():
        got = await s.get(UnifiedMap, "t1")
        assert got is not None
        assert got.map_id == "t1"
        assert got.name == "Test"
        assert got.geometry_json == {"a": 1}
        assert got.is_template is False
        assert got.current_version == 1
        assert got.created_at is not None
        assert got.updated_at is not None


async def test_map_dynamic_state_unique_constraint():
    from sqlalchemy.exc import IntegrityError

    from rcs.db.models import MapDynamicState, UnifiedMap

    async for s in db_session.session():
        s.add(UnifiedMap(map_id="t2", name="Test2"))
        s.add(MapDynamicState(map_id="t2", element_id="e1", state="free"))
        await s.commit()

    # Duplicate (map_id, element_id) must raise IntegrityError.
    with pytest.raises(IntegrityError):
        async for s in db_session.session():
            s.add(MapDynamicState(map_id="t2", element_id="e1", state="occupied"))
            await s.commit()

    # Distinct element_id on the same map persists fine.
    async for s in db_session.session():
        s.add(MapDynamicState(map_id="t2", element_id="e2", state="blocked",
                              payload={"why": "maintenance"}))
        await s.commit()

    async for s in db_session.session():
        rows = (
            await s.execute(
                select(MapDynamicState).where(MapDynamicState.map_id == "t2")
            )
        ).scalars().all()
        assert len(rows) == 2
        states = {r.element_id: r.state for r in rows}
        assert states == {"e1": "free", "e2": "blocked"}
