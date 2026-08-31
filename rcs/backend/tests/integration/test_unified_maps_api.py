"""Integration tests for the unified-map REST API (Task 5).

Mounts ONLY the new ``control_unified_maps`` router at ``/api/rcs`` (so paths
become ``/api/rcs/maps/...``) and exercises the full surface, including the
dynamic-state sub-resource upsert/list/delete. Requires PostgreSQL reachable.
"""
import os
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

_ROOT = Path(__file__).parent.parent.parent  # rcs/backend/
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from rcs.api.control.control_unified_maps import router  # noqa: E402
from rcs.db import session as db_session  # noqa: E402


def _db_reachable() -> bool:
    url = os.environ.get(
        "RCS_DATABASE_URL", "postgresql+asyncpg://rcs:rcs@localhost:5432/rcs_test"
    )
    try:
        import socket
        tail = url.split("@", 1)[-1]
        host, port = tail.split("/", 1)[0].split(":", 1)
        s = socket.create_connection((host, int(port)), timeout=0.4)
        s.close()
        return True
    except Exception:
        return False


if not _db_reachable():
    pytest.skip("PostgreSQL not reachable", allow_module_level=True)


@pytest.fixture(scope="module", autouse=True)
def app_client():
    # Build a minimal app with ONLY the unified-maps router.
    app = FastAPI()
    app.include_router(router, prefix="/api/rcs")

    with TestClient(app) as c:
        yield c


def _wipe_all():
    """Wipe dynamic + unified tables and the legacy tables they touch."""
    import asyncio

    from rcs.db import models as M
    from sqlalchemy import delete

    async def _do():
        await db_session.init_db()
        async for s in db_session.session():
            # Order matters for FK chains.
            await s.execute(delete(M.MapDynamicState))
            await s.execute(delete(M.UnifiedMap))
            await s.commit()

    asyncio.run(_do())


def setup_module(module):
    _wipe_all()


def _seed(client):
    r = client.post("/api/rcs/maps/templates/seed")
    assert r.status_code == 200
    return r


# ── 1. seed templates ────────────────────────────────────────────────────────


def test_seed_templates(app_client):
    rows = _seed(app_client).json()
    assert len(rows) >= 14


# ── 2. list templates ────────────────────────────────────────────────────────


def test_list_templates(app_client):
    _seed(app_client)
    r = app_client.get("/api/rcs/maps/templates")
    assert r.status_code == 200
    assert len(r.json()) >= 14


# ── 3. create from template ───────────────────────────────────────────────────


def test_create_from_template(app_client):
    _seed(app_client)
    r = app_client.post(
        "/api/rcs/maps/from-template",
        json={"template_key": "ecommerce_large", "name": "My WH"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["is_template"] is False
    assert body["kind"] == "warehouse"


# ── 4-12. full lifecycle ──────────────────────────────────────────────────────


def test_full_lifecycle(app_client):
    _seed(app_client)

    # 3. create from template → capture new_id
    r = app_client.post(
        "/api/rcs/maps/from-template",
        json={"template_key": "ecommerce_large", "name": "My WH"},
    )
    assert r.status_code == 201
    new_id = r.json()["map_id"]
    assert r.json()["is_template"] is False
    assert r.json()["kind"] == "warehouse"

    # 4. get map with geometry/topology/semantic keys
    g = app_client.get(f"/api/rcs/maps/{new_id}")
    assert g.status_code == 200
    body = g.json()
    assert "geometry" in body and "topology" in body and "semantic" in body

    # 5. put rename → name updated, version bumped
    v0 = body["current_version"]
    u = app_client.put(f"/api/rcs/maps/{new_id}", json={"name": "Renamed"})
    assert u.status_code == 200
    ub = u.json()
    assert ub["name"] == "Renamed"
    assert ub["current_version"] == v0 + 1

    # 6. dynamic list empty
    d = app_client.get(f"/api/rcs/maps/{new_id}/dynamic")
    assert d.status_code == 200
    assert d.json() == []

    # 7. put dynamic zone-a (create)
    p = app_client.put(
        f"/api/rcs/maps/{new_id}/dynamic/zone-a",
        json={"state": "occupied", "payload": {"by": "agv1"}},
    )
    assert p.status_code == 200
    pb = p.json()
    assert pb["element_id"] == "zone-a"
    assert pb["state"] == "occupied"
    assert pb["payload"] == {"by": "agv1"}

    # 8. put dynamic zone-a again (upsert → update, still 1 row)
    p2 = app_client.put(
        f"/api/rcs/maps/{new_id}/dynamic/zone-a", json={"state": "free"}
    )
    assert p2.status_code == 200
    assert p2.json()["state"] == "free"

    # 9. list dynamic → length 1
    dl = app_client.get(f"/api/rcs/maps/{new_id}/dynamic")
    assert dl.status_code == 200
    assert len(dl.json()) == 1

    # 10. delete dynamic zone-a → 204; then list → 0
    dd = app_client.delete(f"/api/rcs/maps/{new_id}/dynamic/zone-a")
    assert dd.status_code == 204
    dl2 = app_client.get(f"/api/rcs/maps/{new_id}/dynamic")
    assert len(dl2.json()) == 0

    # 11. dynamic on missing parent map → 404
    miss = app_client.get("/api/rcs/maps/does-not-exist/dynamic")
    assert miss.status_code == 404

    # 12. delete map → 204
    dm = app_client.delete(f"/api/rcs/maps/{new_id}")
    assert dm.status_code == 204
