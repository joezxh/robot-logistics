"""Tests for orders lifecycle: status advance + DAG task monitoring."""
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
        await s.execute(delete(models.OrderTask))
        await s.execute(delete(models.OrderItem))
        await s.execute(delete(models.Order))
        await s.commit()
    yield


async def test_advance_and_list_status():
    from rcs.api import order_repository as repo

    rec = await repo.create(
        scenario_id="e", priority=5, deadline=None,
        items=[{"ref": "SKU:A", "quantity": 1}],
        tasks=[{"node_id": "t1", "task_type": "pick",
                "slo_class": "std", "depends_on": []}],
    )
    assert rec is not None
    oid = rec["order_id"]
    assert await repo.advance_status(oid, "RUNNING") is True
    got = await repo.get(oid)
    assert got is not None
    assert got["status"] == "RUNNING"

    queued = await repo.list_orders(status="RUNNING")
    assert any(o["order_id"] == oid for o in queued)


async def test_set_task_status():
    from rcs.api import order_repository as repo

    rec = await repo.create(
        scenario_id="e", priority=5, deadline=None,
        items=[{"ref": "SKU:B", "quantity": 2}],
        tasks=[{"node_id": "t2", "task_type": "place",
                "slo_class": "std", "depends_on": []}],
    )
    assert rec is not None
    assert await repo.set_task_status(rec["order_id"], "t2", "DONE") is True