"""Tests for the UnifiedMap CRUD (Task 3).

Mirrors ``tests/unit/control/test_sitemap_service.py`` but exercises
``rcs.services.control.control_unified_maps`` against the ``UnifiedMap`` table.
"""
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
        await s.execute(delete(models.MapDynamicState))
        await s.execute(delete(models.UnifiedMap))
        await s.commit()
    yield


async def test_seed_templates_creates_fourteen_rows():
    from rcs.services.control import control_unified_maps as svc

    rows = await svc.seed_templates()
    assert len(rows) >= 15

    expected_ids = {
        # 8 DB warehouse templates
        "tpl-ecommerce_large", "tpl-theatre_ecommerce", "tpl-port_terminal",
        "tpl-factory_warehouse", "tpl-highway_freight_hub",
        "tpl-third_party_logistics", "tpl-cold_chain", "tpl-reverse_logistics",
        # 7 hardcoded scenarios (cold_chain / reverse_logistics collide with
        # warehouse keys, so they are namespaced as tpl-scn-<id> to keep all
        # 15 templates distinct and preserve both sources' data).
        "tpl-ecommerce", "tpl-manufacturing", "tpl-port", "tpl-multi_floor",
        "tpl-train_unload", "tpl-scn-cold_chain", "tpl-scn-reverse_logistics",
    }
    got_ids = {r["map_id"] for r in rows}
    assert expected_ids <= got_ids, got_ids - expected_ids
    assert len(got_ids) == 15


async def test_seed_templates_is_idempotent_and_content_ok():
    from rcs.services.control import control_unified_maps as svc

    rows1 = await svc.seed_templates()
    rows2 = await svc.seed_templates()
    assert len(rows2) == 15

    by_id = {r["map_id"]: r for r in rows2}

    # A DB warehouse template carries a navigation graph.
    db_tpl = by_id["tpl-ecommerce_large"]
    assert "nodes" in db_tpl["topology"] and "edges" in db_tpl["topology"]

    # A scenario template carries alert_types in its semantic layer.
    scenario_tpl = by_id["tpl-ecommerce"]
    assert "alert_types" in scenario_tpl["semantic"]
    assert scenario_tpl["kind"] == "scenario"

    # A namespaced (colliding) scenario template also carries its semantic layer.
    scn_tpl = by_id["tpl-scn-cold_chain"]
    assert "alert_types" in scn_tpl["semantic"]
    assert scn_tpl["kind"] == "scenario"


async def test_crud_lifecycle():
    from rcs.services.control import control_unified_maps as svc

    created = await svc.create(name="live-map-1", kind="warehouse",
                               geometry={"bounds": {"w": 10, "d": 10}})
    mid = created["map_id"]
    assert created["is_template"] is False

    fetched = await svc.get(mid)
    assert fetched is not None
    assert fetched["map_id"] == mid

    v0 = fetched["current_version"]
    updated = await svc.update(mid, name="live-map-1-renamed",
                               semantic={"foo": "bar"})
    assert updated["name"] == "live-map-1-renamed"
    assert updated["current_version"] == v0 + 1

    deleted = await svc.delete(mid)
    assert deleted is True
    assert await svc.get(mid) is None


async def test_create_from_template_warehouse():
    from rcs.services.control import control_unified_maps as svc

    await svc.seed_templates()
    new_map = await svc.create_from_template("ecommerce_large")
    assert new_map is not None
    assert new_map["is_template"] is False
    assert new_map["kind"] == "warehouse"
    assert new_map["geometry"] is not None
    assert new_map["geometry"] != {}
