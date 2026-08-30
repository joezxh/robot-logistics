"""Tests for scheduler config + single-active toggle."""
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
        await s.execute(delete(models.SchedulerConfig))
        await s.commit()
    yield


async def test_activate_config():
    from rcs.services.control import control_scheduler as sch_svc

    c1 = await sch_svc.create(name="w1", strategy="util-weighted",
                              weights={"w1": 1.0, "w2": 0.5, "w3": 0.2, "w4": 0.1})
    c2 = await sch_svc.create(name="w2", strategy="nearest",
                              weights={"w1": 0.5, "w2": 0.5, "w3": 0.0, "w4": 0.0})
    assert await sch_svc.activate(c1["config_id"]) is True
    active = await sch_svc.get_active()
    assert active is not None
    assert active["config_id"] == c1["config_id"]

    # Activating c2 must toggle off c1.
    assert await sch_svc.activate(c2["config_id"]) is True
    active = await sch_svc.get_active()
    assert active["config_id"] == c2["config_id"]

    configs = await sch_svc.list_configs()
    assert sum(1 for c in configs if c["active"]) == 1


async def test_update_weights():
    from rcs.services.control import control_scheduler as sch_svc

    c = await sch_svc.create(name="w3", strategy="util-weighted",
                             weights={"w1": 1, "w2": 0, "w3": 0, "w4": 0})
    upd = await sch_svc.update(c["config_id"], weights={"w1": 0.5, "w2": 0.5, "w3": 0, "w4": 0})
    assert upd is not None
    assert upd["weights"]["w1"] == 0.5