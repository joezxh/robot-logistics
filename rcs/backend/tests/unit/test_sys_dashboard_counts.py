"""Tests for the dashboard summary counts (Task 7 of unified-map-model plan).

Confirms the dashboard ``/summary`` endpoint counts real ``UnifiedMap`` records
(via ``is_template.is_(False)``) and that the warehouse counter additionally
filters ``kind == 'warehouse'``. No legacy ``SiteMap`` / ``TopologyShell`` ORM
dependency remains.

Follows the convention in ``tests/unit/test_unified_map_model.py``: skip the
module if Postgres is unreachable, use ``async for s in db_session.session()``.
"""
from __future__ import annotations
import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from rcs.db import session as db_session
from rcs.db.unified_map import UnifiedMap
from rcs.api.sys import sys_dashboard
from rcs.services.sys import sys_deps


class _FakeUser:
    """Minimal stand-in for ``SysUser`` used to satisfy the gated dependency."""
    user_id = 1
    username = "tester"
    is_admin = True
    status = "active"


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
    async for s in db_session.session():
        await s.execute(delete(UnifiedMap))
        await s.commit()
    yield


@pytest.fixture
def client():
    """A minimal app with ONLY the dashboard router and a fake current user."""
    app = FastAPI()
    app.include_router(sys_dashboard.router, prefix="/api/sys")
    app.dependency_overrides[sys_deps.get_current_user] = (
        lambda: _FakeUser()
    )
    return TestClient(app)


async def _seed(rows):
    async for s in db_session.session():
        for r in rows:
            s.add(r)
        await s.commit()


async def test_dashboard_counts_filter_templates_and_warehouse_kind(client):
    await _seed([
        UnifiedMap(map_id="m1", name="Live Site", is_template=False, kind=None),
        UnifiedMap(map_id="m2", name="Scenario", is_template=False, kind="scenario"),
        UnifiedMap(map_id="w1", name="Warehouse A", is_template=False, kind="warehouse"),
        UnifiedMap(map_id="w2", name="Warehouse B", is_template=False, kind="warehouse"),
        UnifiedMap(map_id="t1", name="WH Template", is_template=True, kind="warehouse"),
        UnifiedMap(map_id="t2", name="Site Template", is_template=True, kind=None),
    ])

    resp = client.get("/api/sys/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()["data"]

    # 4 non-template records (m1, m2, w1, w2) -> mapCount
    assert data["mapCount"] == 4
    # 2 non-template warehouse-kind records (w1, w2) -> warehouseCount
    assert data["warehouseCount"] == 2

    async for s in db_session.session():
        await s.execute(delete(UnifiedMap))
        await s.commit()
