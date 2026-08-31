"""Tests for migrations/007_unified_map.sql (Part A + Part B only).

Part C (DROP legacy tables) is intentionally commented out and NOT exercised
here, because Tasks 3-7 still reference the old tables/models.

These tests require a reachable PostgreSQL instance. They are skipped at the
module level if Postgres is not reachable.
"""
from __future__ import annotations
import os
import re

import pytest
from sqlalchemy import delete, select, text

from rcs.db import models
from rcs.db import session as db_session
from rcs.db import init_db, session_scope
from rcs.db.models import UnifiedMap, MapDynamicState, TopologyShell, SiteMap, TopologyGrid, SiteMapVersion


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
    # create_all builds ALL tables (new ones + legacy ones) via ORM metadata.
    await init_db()
    # Wipe everything in FK-respecting order.
    async for s in session_scope():
        await s.execute(delete(MapDynamicState))
        await s.execute(delete(UnifiedMap))
        await s.execute(delete(SiteMapVersion))
        await s.execute(delete(SiteMap))
        await s.execute(delete(TopologyGrid))
        await s.execute(delete(TopologyShell))
        await s.commit()
    yield


def _load_part_a_b() -> str:
    """Read the migration SQL and return only Part A + Part B (strip the
    commented-out Part C at the end of the file)."""
    here = os.path.dirname(os.path.abspath(__file__))
    # tests/unit/test_migration_007.py -> migrations/ is two levels up.
    path = os.path.join(here, "..", "..", "migrations", "007_unified_map.sql")
    path = os.path.normpath(path)
    with open(path, "r", encoding="utf-8") as fh:
        sql = fh.read()
    # Cut everything from the OPTIONAL DROP block onward (it is commented out,
    # but we strip it to ensure only Part A + Part B get executed).
    marker = "-- OPTIONAL: run only after Tasks 3-7"
    idx = sql.find(marker)
    if idx != -1:
        sql = sql[:idx]
    return sql


async def _execute_sql_parts(sql: str):
    """Split on ';' and run each non-empty statement individually.

    Handles the `DO $$ ... $$` block (its internal `;` must NOT be split) by
    first stripping SQL `--` line comments, locating every `$$...$$` range, and
    only splitting on `;` that fall outside those ranges.
    """
    import re

    # 1. Strip `-- ...` line comments so comment-only text is never executed.
    cleaned = re.sub(r"--[^\n]*", "", sql)
    # 2. Locate every dollar-quoted block; `;` inside them stays intact.
    dollar_ranges = [
        (m.start(), m.end()) for m in re.finditer(r"\$\$.*?\$\$", cleaned, flags=re.S)
    ]

    def _inside_dollar(pos: int) -> bool:
        return any(s <= pos < e for s, e in dollar_ranges)

    statements: list[str] = []
    buf: list[str] = []
    i = 0
    n = len(cleaned)
    while i < n:
        c = cleaned[i]
        if c == ";" and not _inside_dollar(i):
            stmt = "".join(buf).strip()
            if stmt:
                statements.append(stmt)
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)

    async for s in session_scope():
        for stmt in statements:
            if not stmt:
                continue
            await s.execute(text(stmt))
        await s.commit()


async def test_new_tables_exist_and_match_orm():
    # Insert a UnifiedMap shaped exactly like the ORM and read it back.
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

        # Child row with the unique constraint + FK.
        d = MapDynamicState(
            map_id="tpl-check", element_id="z1", state="occupied",
            payload={"by": "test"},
        )
        s.add(d)
        await s.commit()
        await s.refresh(d)
        assert d.id is not None

    # Verify counts in raw SQL to confirm the tables physically exist.
    async for s in session_scope():
        um = (await s.execute(select(UnifiedMap))).scalars().all()
        ds = (await s.execute(select(MapDynamicState))).scalars().all()
        assert len(um) == 1
        assert len(ds) == 1


async def test_data_migration_sql_applies():
    sql = _load_part_a_b()
    # Apply Part A + Part B against the test DB (tables already exist from
    # create_all + the prior test; the migration is guarded so it is safe).
    await _execute_sql_parts(sql)

    # The prior test inserted a UnifiedMap row, so the Part B guard
    # (`WHERE NOT EXISTS (SELECT 1 FROM robot_unified_maps)`) would now skip.
    # Wipe only the new tables to simulate a fresh target, then seed legacy
    # rows and re-run Part B to exercise the actual merge.
    async for s in session_scope():
        await s.execute(delete(MapDynamicState))
        await s.execute(delete(UnifiedMap))
        await s.commit()

    # Seed a couple of legacy rows: a template pair (shared tpl- key) and a
    # live site (independent keys).
    async for s in session_scope():
        # Template: shell.site_id == site_map.map_id == 'tpl-demo'
        s.add(TopologyShell(
            site_id="tpl-demo", name="Demo Template", is_template=True,
            width_m=12.0, depth_m=8.0, height_m=4.0,
            data={"bounds": {"w": 12, "d": 8}, "semantic": {"level": 1}},
        ))
        s.add(SiteMap(
            map_id="tpl-demo", name="Demo Template", is_template=True,
            current_version=1, nodes_json=[{"id": "A"}], edges_json=[{"from": "A"}],
        ))
        # Live site: independent keys.
        s.add(TopologyShell(
            site_id="site-live", name="Live Shell", is_template=False,
            width_m=20.0, depth_m=10.0, height_m=5.0,
            data={"bounds": {"w": 20, "d": 10}, "semantic": {"level": 2}},
        ))
        s.add(SiteMap(
            map_id="map-live", name="Live Map", is_template=False,
            current_version=1, nodes_json=[{"id": "B"}], edges_json=[],
        ))
        await s.commit()

    # Re-run Part B — must be idempotent (guarded) and not raise.
    await _execute_sql_parts(sql)

    async for s in session_scope():
        rows = (await s.execute(
            select(UnifiedMap).where(UnifiedMap.map_id.in_(["tpl-demo", "map-live"]))
        )).scalars().all()
        by_id = {r.map_id: r for r in rows}

        # Template merged row.
        demo = by_id.get("tpl-demo")
        assert demo is not None, "template merge row missing"
        assert demo.map_id == "tpl-demo"
        assert demo.name == "Demo Template"
        assert demo.is_template is True
        assert demo.kind == "warehouse"
        assert demo.topology_json is not None  # at least one JSON column populated
        assert demo.bounds_json is not None

        # Live site merged row (joined by independent key coincidence? No — they
        # differ, so geometry comes from NULL via LEFT JOIN, but topology from
        # site map must still be present).
        live = by_id.get("map-live")
        assert live is not None, "live merge row missing"
        assert live.map_id == "map-live"
        assert live.name == "Live Map"
        assert live.is_template is False
        assert live.kind == "site"
        assert live.topology_json is not None

        # Exactly two merged rows (no duplication from the re-run).
        assert len(rows) == 2
