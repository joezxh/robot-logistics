"""DB-backed tests for warehouse site-map templates (seeding + instantiation)."""
from __future__ import annotations
import os

import pytest
import pytest_asyncio

from rcs.db import session as db_session


def _db_reachable() -> bool:
    url = os.environ.get("RCS_DATABASE_URL",
                         "postgresql+asyncpg://rcs:rcs@localhost:5432/rcs_test")
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


async def test_seed_templates_creates_all_of_them():
    from rcs.models import site_map_templates as tpl
    from rcs.services.control import control_maps as map_svc

    seeded = await map_svc.seed_templates()
    assert len(seeded) == len(tpl.TEMPLATE_KEYS)
    assert {m["map_id"] for m in seeded} == {f"tpl-{k}" for k in tpl.TEMPLATE_KEYS}
    assert all(m["is_template"] for m in seeded)


async def test_seed_templates_is_idempotent():
    from rcs.services.control import control_maps as map_svc

    first = await map_svc.seed_templates()
    second = await map_svc.seed_templates()

    assert len(first) == len(second)
    # Same deterministic ids, so no duplicates were inserted.
    assert [m["map_id"] for m in first] == [m["map_id"] for m in second]
    all_maps = await map_svc.list_maps(include_templates=True)
    tpl_ids = {m["map_id"] for m in first}
    assert sum(1 for m in all_maps if m["map_id"] in tpl_ids) == len(first)


async def test_list_maps_excludes_templates_by_default():
    from rcs.services.control import control_maps as map_svc

    await map_svc.seed_templates()
    await map_svc.create(name="live-1", nodes=[{"id": "A", "pos": [0, 0, 0]}], edges=[])

    default = await map_svc.list_maps()
    assert all(not m["is_template"] for m in default)
    assert any(m["name"] == "live-1" for m in default)

    everything = await map_svc.list_maps(include_templates=True)
    assert len(everything) > len(default)
    assert any(m["is_template"] for m in everything)


async def test_list_templates_returns_only_templates():
    from rcs.services.control import control_maps as map_svc

    await map_svc.seed_templates()
    templates = await map_svc.list_templates()
    assert templates
    assert all(m["is_template"] for m in templates)
    assert all(m["nodes"] for m in templates)


async def test_create_from_template_makes_an_editable_copy():
    from rcs.services.control import control_maps as map_svc

    m = await map_svc.create_from_template("factory_warehouse", name="我的工厂仓")
    assert m is not None
    assert m["is_template"] is False
    assert m["name"] == "我的工厂仓"
    assert m["nodes"], "template graph should be copied across"

    # The copy must not be the template row itself.
    assert m["map_id"] != "tpl-factory_warehouse"


async def test_create_from_template_defaults_to_template_name():
    from rcs.models import site_map_templates as tpl
    from rcs.services.control import control_maps as map_svc

    m = await map_svc.create_from_template("port_terminal")
    assert m["name"] == tpl.get_template("port_terminal").name


async def test_create_from_template_is_deep_copied():
    """Editing the instantiated map must not mutate the template definition."""
    from rcs.models import site_map_templates as tpl
    from rcs.services.control import control_maps as map_svc

    before = len(tpl.get_template("ecommerce_large").nodes)
    m = await map_svc.create_from_template("ecommerce_large")
    assert len(m["nodes"]) == before

    await map_svc.update(m["map_id"], m["name"], nodes=[], edges=[])
    assert len(tpl.get_template("ecommerce_large").nodes) == before


async def test_create_from_template_unknown_key_returns_none():
    from rcs.services.control import control_maps as map_svc

    assert await map_svc.create_from_template("does_not_exist") is None


# ── Plan B: templates span shell + grid + site map ───────────────────────────

async def test_seed_writes_all_three_tables():
    from sqlalchemy import select

    from rcs.db import models
    from rcs.models import site_map_templates as tpl
    from rcs.services.control import control_maps as map_svc

    await map_svc.seed_templates()
    async for s in db_session.session():
        shells = (await s.execute(
            select(models.TopologyShell)
            .where(models.TopologyShell.is_template.is_(True))
        )).scalars().all()
        grids = (await s.execute(
            select(models.TopologyGrid)
            .where(models.TopologyGrid.is_template.is_(True))
        )).scalars().all()
        maps = (await s.execute(
            select(models.SiteMap).where(models.SiteMap.is_template.is_(True))
        )).scalars().all()

        assert len(shells) == len(tpl.TEMPLATE_KEYS)
        assert len(maps) == len(tpl.TEMPLATE_KEYS)
        expected_rows = sum(
            len(tpl.get_template(k).shell.zones) for k in tpl.TEMPLATE_KEYS)
        assert len(grids) == expected_rows


async def test_seeded_rows_share_one_deterministic_id():
    from sqlalchemy import select

    from rcs.db import models
    from rcs.models import site_map_templates as tpl
    from rcs.services.control import control_maps as map_svc

    await map_svc.seed_templates()
    async for s in db_session.session():
        shells = (await s.execute(
            select(models.TopologyShell)
            .where(models.TopologyShell.is_template.is_(True))
        )).scalars().all()
        assert {sh.site_id for sh in shells} == {f"tpl-{k}" for k in tpl.TEMPLATE_KEYS}


async def test_reseeding_does_not_duplicate_grid_rows():
    from sqlalchemy import select

    from rcs.db import models
    from rcs.services.control import control_maps as map_svc

    await map_svc.seed_templates()
    await map_svc.seed_templates()
    async for s in db_session.session():
        grids = (await s.execute(
            select(models.TopologyGrid)
            .where(models.TopologyGrid.is_template.is_(True))
        )).scalars().all()
        refs = [(g.site_id, g.zone_id) for g in grids]
        assert len(refs) == len(set(refs)), "grid rows duplicated across seeds"


async def test_seeded_shell_round_trips_into_floor_shell():
    from rcs.db import models
    from rcs.models.floor_shell import FloorShell
    from rcs.services.control import control_maps as map_svc

    await map_svc.seed_templates()
    async for s in db_session.session():
        row = await s.get(models.TopologyShell, "tpl-port_terminal")
        assert row is not None
        shell = FloorShell(**(row.data or {}))
        assert shell.bounds.w == 300 and shell.bounds.d == 180
        assert shell.zones and shell.docks


async def test_create_from_template_clones_shell_and_grid():
    from sqlalchemy import select

    from rcs.db import models
    from rcs.services.control import control_maps as map_svc

    m = await map_svc.create_from_template("factory_warehouse", name="克隆工厂仓")
    site_id = m["map_id"]
    async for s in db_session.session():
        shell = await s.get(models.TopologyShell, site_id)
        assert shell is not None, "shell was not cloned"
        assert shell.is_template is False
        assert shell.name == "克隆工厂仓"

        rows = (await s.execute(
            select(models.TopologyGrid)
            .where(models.TopologyGrid.site_id == site_id)
        )).scalars().all()
        assert rows, "grid rows were not cloned"
        assert all(r.is_template is False for r in rows)
        assert {r.zone_id for r in rows} == {z.id for z in
                                             (await _factory_zone_ids())}


async def _factory_zone_ids():
    from rcs.models import site_map_templates as tpl
    return tpl.get_template("factory_warehouse").shell.zones


async def test_new_site_has_its_own_id_not_the_template_id():
    from rcs.services.control import control_maps as map_svc

    m = await map_svc.create_from_template("port_terminal")
    assert m["map_id"] != "tpl-port_terminal"
    assert m["is_template"] is False
