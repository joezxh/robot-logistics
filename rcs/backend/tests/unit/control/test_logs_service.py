"""Tests for command + event log service."""
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
        await s.execute(delete(models.CommandLog))
        await s.execute(delete(models.EventLog))
        await s.commit()
    yield


async def test_issue_and_query_commands():
    from rcs.services.control import control_logs as logs_svc

    await logs_svc.issue_command(device_id="agv-01", cmd_type="MOVE",
                                payload={"x": 1.0}, issued_by="u1", result="ok")
    cmds = await logs_svc.list_commands(device_id="agv-01", limit=10)
    assert any(c["device_id"] == "agv-01" for c in cmds)


async def test_event_log():
    from rcs.services.control import control_logs as logs_svc

    await logs_svc.log_event(level="info", source="scheduler", message="step", meta={"k": 1})
    evs = await logs_svc.list_events(level="info", limit=10)
    assert any(e["source"] == "scheduler" for e in evs)