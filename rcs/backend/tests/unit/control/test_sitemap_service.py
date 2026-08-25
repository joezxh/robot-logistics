"""Tests for site map persistence + versioning + import/export."""
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
        await s.execute(delete(models.SiteMapVersion))
        await s.execute(delete(models.SiteMap))
        await s.commit()
    yield


async def test_create_import_export_version():
    from rcs.control.topology import service as map_svc

    m = await map_svc.create(name="wh1", nodes=[{"id": "A", "pos": [0, 0, 0]}], edges=[])
    await map_svc.import_json(m["map_id"], {
        "nodes": [{"id": "A", "pos": [0, 0, 0]}, {"id": "B", "pos": [5, 0, 0]}],
        "edges": [{"from": "A", "to": "B", "distance": 5.0}],
    })
    exported = await map_svc.export_json(m["map_id"])
    assert exported is not None
    assert len(exported["nodes"]) == 2
    versions = await map_svc.list_versions(m["map_id"])
    assert len(versions) >= 2  # initial + import


async def test_restore_version():
    from rcs.control.topology import service as map_svc

    m = await map_svc.create(name="wh2", nodes=[{"id": "X", "pos": [0, 0, 0]}], edges=[])
    m2 = await map_svc.update(m["map_id"], name=None,
        nodes=[{"id": "X", "pos": [1, 1, 0]}], edges=[])
    versions = await map_svc.list_versions(m["map_id"])
    initial_vid = [v["version_id"] for v in versions if v["note"] == "initial"][0]
    await map_svc.restore_version(m["map_id"], initial_vid)
    got = await map_svc.get(m["map_id"])
    assert got is not None
    assert got["nodes"][0]["pos"] == [0, 0, 0]