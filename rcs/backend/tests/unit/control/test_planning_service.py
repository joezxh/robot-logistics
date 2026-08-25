"""Tests for planning profile library."""
from __future__ import annotations
import os

import pytest
import pytest_asyncio

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


@pytest_asyncio.fixture(scope="module", autouse=True)
async def _prepare_db():
    await db_session.init_db()
    from sqlalchemy import delete
    from rcs.db import models
    async for s in db_session.session():
        await s.execute(delete(models.PlanningProfile))
        await s.commit()
    yield


async def test_crud_profile():
    from rcs.control.planning import service as plan_svc

    p = await plan_svc.create(name="trap6", algo="trapezoidal", axes=6,
                              vel_max=[2.0] * 6, acc_max=[4.0] * 6, created_by="u1")
    got = await plan_svc.get(p["profile_id"])
    assert got is not None
    assert got["algo"] == "trapezoidal"
    profiles = await plan_svc.list_profiles()
    assert len(profiles) >= 1


async def test_delete_profile():
    from rcs.control.planning import service as plan_svc

    p = await plan_svc.create(name="quint6", algo="quintic", axes=6,
                              vel_max=[2.0] * 6, acc_max=[4.0] * 6)
    assert await plan_svc.delete(p["profile_id"]) is True
    assert await plan_svc.get(p["profile_id"]) is None