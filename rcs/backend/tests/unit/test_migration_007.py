"""Tests for migrations/007_unified_map.sql (Part A + Part B + Part C).

Part C (DROP legacy tables) is now ENABLED, because the old ORM models
(TopologyShell / TopologyGrid / SiteMap / SiteMapVersion) have been removed from
``rcs.db.models``. The legacy tables are superseded by ``robot_unified_maps``
(+ ``robot_map_dynamic_state``).

These tests require a reachable PostgreSQL instance. They are skipped at the
module level if Postgres is not reachable.
"""
from __future__ import annotations
import os

import pytest
from sqlalchemy import delete, select

from rcs.db import session as db_session
from rcs.db import init_db, session_scope
from rcs.db.models import UnifiedMap, MapDynamicState


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


if not _db_reachable():
    pytest.skip("PostgreSQL not reachable", allow_module_level=True)


@pytest.fixture(scope="module", autouse=True)
async def _prepare_db():
    # create_all builds the unified-maps tables via ORM metadata.
    await init_db()
    async for s in session_scope():
        await s.execute(delete(MapDynamicState))
        await s.execute(delete(UnifiedMap))
        await s.commit()
    yield


def _load_migration_sql() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(os.path.join(here, "..", "..", "migrations", "007_unified_map.sql"))
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def test_migration_file_has_all_parts():
    sql = _load_migration_sql()
    assert "robot_unified_maps" in sql, "Part A create table missing"
    assert "robot_map_dynamic_state" in sql, "Part A dynamic-state table missing"
    assert 'DROP TABLE IF EXISTS robot_topology_shell' in sql, "Part C DROP missing"
    assert 'DROP TABLE IF EXISTS robot_site_maps' in sql, "Part C DROP missing"
    # Part C must no longer be commented out.
    assert "-- DROP TABLE IF EXISTS robot_topology_shell" not in sql


@pytest.mark.asyncio
async def test_unified_map_roundtrip():
    async for s in session_scope():
        m = UnifiedMap(
            map_id="tpl-check",
            name="Check Map",
            is_template=True,
            kind="warehouse",
            bounds_json={"w": 10, "d": 10, "h": 4},
            geometry_json={"zones": []},
            topology_json={"nodes": [], "edges": []},
            semantic_json={},
            data={"extra": 1},
        )
        s.add(m)
        await s.commit()
        await s.refresh(m)
        assert m.map_id == "tpl-check"
        assert m.geometry_json == {"zones": []}

        d = MapDynamicState(
            map_id="tpl-check", element_id="z1", state="occupied",
            payload={"by": "test"},
        )
        s.add(d)
        await s.commit()
        await s.refresh(d)
        assert d.id is not None

    async for s in session_scope():
        um = (await s.execute(select(UnifiedMap))).scalars().all()
        ds = (await s.execute(select(MapDynamicState))).scalars().all()
        assert len(um) == 1
        assert len(ds) == 1


@pytest.mark.asyncio
async def test_legacy_tables_dropped():
    """Part C of the migration drops the legacy tables; the ORM metadata must no
    longer contain them."""
    from rcs.db import models
    table_names = set(models.Base.metadata.tables.keys())
    for legacy in (
        "robot_topology_shell",
        "robot_topology_grid",
        "robot_site_maps",
        "robot_site_map_versions",
    ):
        assert legacy not in table_names, f"{legacy} should be removed from ORM metadata"
