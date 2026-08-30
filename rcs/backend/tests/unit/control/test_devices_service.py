"""Tests for device persistence service.

These tests require a live PostgreSQL accessible via ``RCS_DATABASE_URL``.
Default URL: ``postgresql+asyncpg://rcs:rcs@localhost:5432/rcs_test``.

If Postgres is not running, the test session is skipped (not failed) so the
unit suite still works for fast local iteration.
"""
from __future__ import annotations
import os

import pytest
import pytest_asyncio

from rcs.db import session as db_session


# Skip the entire module when no DB is available; otherwise we'd hang or fail.
def _db_reachable() -> bool:
    url = os.environ.get("RCS_DATABASE_URL", "postgresql+asyncpg://rcs:rcs@localhost:5432/rcs_test")
    try:
        import socket
        # crude host/port parse: postgresql+asyncpg://user:pwd@host:port/db
        tail = url.split("@", 1)[-1]
        host_port = tail.split("/", 1)[0]
        host, port = host_port.split(":", 1)
        s = socket.create_connection((host, int(port)), timeout=0.4)
        s.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.asyncio

if not _db_reachable():
    pytest.skip("PostgreSQL not reachable; set RCS_DATABASE_URL or run `docker compose up -d db`", allow_module_level=True)


@pytest_asyncio.fixture(scope="module", autouse=True)
async def _prepare_db():
    await db_session.init_db()
    # Clean slate for the devices table.
    from sqlalchemy import delete
    from rcs.db import models
    async for s in db_session.session():
        await s.execute(delete(models.Device))
        await s.commit()
    yield


async def test_register_and_get():
    from rcs.services.control import control_devices as dev_svc

    dev = await dev_svc.register(
        device_id="dev-x", morphology="arm", num_joints=6, control_hz=1000,
        limits={"pos_lower": [-1] * 6, "pos_upper": [1] * 6, "vel_max": [2.0] * 6, "acc_max": [4.0] * 6},
        home_joints=[0.0] * 6, spec={"a": 1},
    )
    got = await dev_svc.get(dev["device_id"])
    assert got["device_id"] == "dev-x"
    assert got["morphology"] == "arm"
    assert got["limits"]["pos_upper"] == [1] * 6
    assert got["home_joints"] == [0.0] * 6
    assert got["spec"] == {"a": 1}


async def test_list_and_update():
    from rcs.services.control import control_devices as dev_svc

    await dev_svc.register(
        device_id="dev-y", morphology="agv", num_joints=2, control_hz=50,
        limits={"pos_lower": [-2, -2], "pos_upper": [2, 2], "vel_max": [1.0, 1.0], "acc_max": [2.0, 2.0]},
        home_joints=[0.0, 0.0], spec={},
    )
    rows = await dev_svc.list_devices()
    ids = [d["device_id"] for d in rows]
    assert "dev-y" in ids

    updated = await dev_svc.update("dev-y", status="online")
    assert updated is not None and updated["status"] == "online"


async def test_delete():
    from rcs.services.control import control_devices as dev_svc

    await dev_svc.register(
        device_id="dev-z", morphology="stacker", num_joints=2, control_hz=50,
        limits={}, home_joints=[], spec={},
    )
    assert await dev_svc.delete("dev-z") is True
    assert await dev_svc.get("dev-z") is None