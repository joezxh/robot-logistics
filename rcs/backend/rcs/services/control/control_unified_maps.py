"""Unified Map persistence for the new UnifiedMap table (Task 3).

Mirrors ``rcs.services.control.control_maps`` (the old ``SiteMap`` CRUD) but
operates on ``UnifiedMap`` / ``MapDynamicState``. Templates are pre-built
blueprint rows flagged ``is_template=True``; this module seeds them from TWO
sources:

* 8 warehouse templates in ``rcs.models.site_map_templates`` (each carries a
  full navigation graph: nodes + edges).
* 6 hardcoded scenarios in ``rcs.models.topology_templates`` (shell + grid +
  metadata only; NO navigation graph).

The two sets use DIFFERENT ``map_id`` namespaces — the DB warehouse templates use
``tpl-<key>`` where keys look like ``ecommerce_large`` / ``theatre_ecommerce`` /
``port_terminal`` / ..., while the scenarios use ``tpl-<scenario_id>`` where ids
look like ``ecommerce`` / ``manufacturing`` / ``port`` / ... So ``tpl-ecommerce``
(scenario) and ``tpl-ecommerce_large`` (warehouse) coexist without collision.
Per spec decision we deliberately do NOT de-duplicate across the two sets.
"""
from __future__ import annotations
import copy
import uuid
from typing import Optional

from sqlalchemy import delete as sa_delete, select

from rcs.db import models, session as db_session


async def create(name: str, geometry: Optional[dict] = None,
                 topology: Optional[dict] = None,
                 semantic: Optional[dict] = None,
                 is_template: bool = False, kind: Optional[str] = None,
                 map_id: Optional[str] = None, name_en: Optional[str] = None,
                 bounds: Optional[dict] = None, data: Optional[dict] = None) -> dict:
    """Create a unified map row (template or live) and return it as a dict."""
    async for s in db_session.session():
        m = models.UnifiedMap(
            map_id=map_id or str(uuid.uuid4()),
            name=name,
            name_en=name_en,
            is_template=is_template,
            kind=kind,
            current_version=1,
            bounds_json=bounds if bounds is not None else {},
            geometry_json=geometry if geometry is not None else {},
            topology_json=topology if topology is not None else {},
            semantic_json=semantic if semantic is not None else {},
            dynamic_json={},
            data=data if data is not None else {},
        )
        s.add(m)
        await s.commit()
        await s.refresh(m)
        return _to_dict(m)
    raise RuntimeError("db session closed")


async def get(map_id: str) -> Optional[dict]:
    async for s in db_session.session():
        m = await s.get(models.UnifiedMap, map_id)
        return _to_dict(m) if m else None
    return None


async def list_maps(include_templates: bool = False) -> list[dict]:
    """List live maps.

    Templates are excluded by default so management UIs never offer them as
    editable maps; pass ``include_templates=True`` to see everything.
    """
    async for s in db_session.session():
        stmt = select(models.UnifiedMap)
        if not include_templates:
            stmt = stmt.where(models.UnifiedMap.is_template.is_(False))
        rows = (await s.execute(stmt)).scalars().all()
        return [_to_dict(m) for m in rows]
    return []


async def list_templates() -> list[dict]:
    """List only the template rows (``is_template=True``)."""
    async for s in db_session.session():
        rows = (await s.execute(
            select(models.UnifiedMap).where(models.UnifiedMap.is_template.is_(True))
        )).scalars().all()
        return [_to_dict(m) for m in rows]
    return []


async def seed_templates() -> list[dict]:
    """Insert (or refresh) all built-in templates. IDEMPOTENT.

    Writes rows for both the 8 DB warehouse templates and the 6 hardcoded
    scenarios, keyed by their distinct ``map_id`` namespaces (see module doc).
    Re-running refreshes contents in place instead of duplicating rows.

    Returns the seeded template dicts.
    """
    from rcs.models import site_map_templates
    from rcs.models import topology_templates as tt

    async for s in db_session.session():
        out: list[models.UnifiedMap] = []

        # ── 8 warehouse templates (DB source, full nav graph) ──────────────
        for t in site_map_templates.list_templates():
            m = await s.get(models.UnifiedMap, t.map_id)
            if m is None:
                m = models.UnifiedMap(map_id=t.map_id)
                s.add(m)
            m.name = t.name
            m.name_en = t.name_en
            m.is_template = True
            m.kind = "warehouse"
            m.current_version = 1
            m.geometry_json = t.shell.model_dump(mode="json")
            m.topology_json = {
                "nodes": copy.deepcopy(t.nodes),
                "edges": copy.deepcopy(t.edges),
            }
            m.semantic_json = (
                {"category": t.category, "description": t.description}
                if (t.category or t.description) else {}
            )
            # bounds are present on every warehouse shell
            m.bounds_json = {"w": t.shell.bounds.w, "d": t.shell.bounds.d}
            m.dynamic_json = {}
            m.data = {}
            out.append(m)

        # ── 6 hardcoded scenarios (topology_templates, no nav graph) ────────
        # NOTE: two scenario ids (``cold_chain``, ``reverse_logistics``) ALSO
        # exist as warehouse template keys, so their naive ``tpl-<id>`` id would
        # collide with the warehouse row and the upsert below would silently
        # overwrite the warehouse's navigation graph. We namespace those two
        # colliding scenarios as ``tpl-scn-<id>`` so all 14 templates coexist
        # with unique ids and no data is lost. (Spec §4 claimed the two
        # namespaces never collide — that is false for these two keys; this is
        # the minimal fix that preserves both sources.)
        _SCENARIO_COLLISIONS = {"cold_chain", "reverse_logistics"}
        for sid in tt.SCENARIO_IDS:  # noqa: B020 (re-uses frozen set, cheap)
            b = tt.get_template(sid)
            map_id = f"tpl-scn-{sid}" if sid in _SCENARIO_COLLISIONS else f"tpl-{sid}"
            m = await s.get(models.UnifiedMap, map_id)
            if m is None:
                m = models.UnifiedMap(map_id=map_id)
                s.add(m)
            m.name = sid.replace("_", " ").title()
            m.name_en = m.name
            m.is_template = True
            m.kind = "scenario"
            m.current_version = 1
            m.geometry_json = b.shell.model_dump(mode="json")
            m.topology_json = {}  # scenario templates carry no graph
            m.semantic_json = {
                "scenario": b.metadata.get("scenario", sid),
                "alert_types": b.metadata.get("alert_types", []),
                "highlight_color": b.metadata.get("highlight_color", "#888"),
            }
            m.bounds_json = {"w": b.shell.bounds.w, "d": b.shell.bounds.d}
            m.dynamic_json = {}
            m.data = {}
            out.append(m)

        await s.commit()
        for m in out:
            await s.refresh(m)
        return [_to_dict(m) for m in out]
    return []


async def create_from_template(key: str, name: Optional[str] = None,
                               new_id: Optional[str] = None) -> Optional[dict]:
    """Materialise a template into a new, editable (non-template) unified map.

    ``key`` is the template key WITHOUT the ``tpl-`` prefix. For warehouse
    templates it resolves via ``site_map_templates.get_template``; for scenario
    templates it resolves via ``topology_templates.get_template``. Returns None
    when ``key`` is unknown to both sources.
    """
    from rcs.models import site_map_templates
    from rcs.models import topology_templates as tt

    # Warehouse DB template?
    try:
        t = site_map_templates.get_template(key)
        title = name or t.name
        geometry = t.shell.model_dump(mode="json")
        topology = {
            "nodes": copy.deepcopy(t.nodes),
            "edges": copy.deepcopy(t.edges),
        }
        semantic = (
            {"category": t.category, "description": t.description}
            if (t.category or t.description) else {}
        )
        bounds = {"w": t.shell.bounds.w, "d": t.shell.bounds.d}
        kind = "warehouse"
    except KeyError:
        t = None

    # Scenario template? (only if not a warehouse key)
    if t is None:
        if key in tt.SCENARIO_IDS:
            b = tt.get_template(key)
            title = name or key.replace("_", " ").title()
            geometry = b.shell.model_dump(mode="json")
            topology = {}  # scenario templates carry no graph
            semantic = {
                "scenario": b.metadata.get("scenario", key),
                "alert_types": b.metadata.get("alert_types", []),
                "highlight_color": b.metadata.get("highlight_color", "#888"),
            }
            bounds = {"w": b.shell.bounds.w, "d": b.shell.bounds.d}
            kind = "scenario"
            # If this scenario id collides with a warehouse key, a real template
            # row was seeded under ``tpl-scn-<id>``; a materialised copy still
            # gets a fresh live id below, so nothing special is needed here.
        else:
            return None

    return await create(
        name=title, geometry=geometry, topology=topology, semantic=semantic,
        is_template=False, kind=kind, map_id=new_id, bounds=bounds, data={},
    )


async def update(map_id: str, name: Optional[str] = None,
                 geometry: Optional[dict] = None,
                 topology: Optional[dict] = None,
                 semantic: Optional[dict] = None) -> Optional[dict]:
    async for s in db_session.session():
        m = await s.get(models.UnifiedMap, map_id)
        if m is None:
            return None
        if name is not None:
            m.name = name
        if geometry is not None:
            m.geometry_json = geometry
        if topology is not None:
            m.topology_json = topology
        if semantic is not None:
            m.semantic_json = semantic
        m.current_version += 1
        await s.commit()
        await s.refresh(m)
        return _to_dict(m)
    return None


async def delete(map_id: str) -> bool:
    async for s in db_session.session():
        m = await s.get(models.UnifiedMap, map_id)
        if m is None:
            return False
        await s.delete(m)
        await s.commit()
        return True
    return False


async def import_json(map_id: str, payload: dict) -> Optional[dict]:
    """Merge a JSON payload into a unified map.

    ``payload`` carries ``geometry`` / ``topology`` / ``semantic`` dicts (or a
    flattened form with a subset of those keys). Any missing key is left
    untouched (only provided keys are applied).
    """
    return await update(
        map_id, name=payload.get("name"),
        geometry=payload.get("geometry"),
        topology=payload.get("topology"),
        semantic=payload.get("semantic"),
    )


async def export_json(map_id: str) -> Optional[dict]:
    m = await get(map_id)
    if m is None:
        return None
    return {
        "map_id": m["map_id"],
        "name": m["name"],
        "geometry": m["geometry"],
        "topology": m["topology"],
        "semantic": m["semantic"],
    }


# ── Versioning ────────────────────────────────────────────────────────────────
# The versioning sub-tables (robot_unified_map_versions etc.) are deferred to a
# later task. These stubs keep the public surface stable; they never raise.
# TODO: implement against the deferred versioning sub-tables.

async def list_versions(map_id: str) -> list[dict]:
    return []


async def restore_version(map_id: str, version_id: str) -> Optional[dict]:
    return None


async def seed() -> list[dict]:
    """Alias used by init scripts (``seed_templates``)."""
    return await seed_templates()


def _to_dict(m: models.UnifiedMap) -> dict:
    return {
        "map_id": m.map_id,
        "name": m.name,
        # Coerced to bool: the column is NOT NULL DEFAULT FALSE, but rows created
        # before the migration may still read back as None in a session that
        # predates the DDL.
        "is_template": bool(m.is_template),
        "kind": m.kind,
        "current_version": m.current_version,
        "geometry": m.geometry_json or {},
        "topology": m.topology_json or {},
        "semantic": m.semantic_json or {},
        "bounds": m.bounds_json or {},
        "dynamic": m.dynamic_json or {},
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
    }


# Public namespace mirroring control_maps.py (plain async functions).
class UnifiedMapCRUD:
    create = staticmethod(create)
    get = staticmethod(get)
    list_maps = staticmethod(list_maps)
    list_templates = staticmethod(list_templates)
    seed_templates = staticmethod(seed_templates)
    seed = staticmethod(seed)
    create_from_template = staticmethod(create_from_template)
    update = staticmethod(update)
    delete = staticmethod(delete)
    import_json = staticmethod(import_json)
    export_json = staticmethod(export_json)
    list_versions = staticmethod(list_versions)
    restore_version = staticmethod(restore_version)
    _to_dict = staticmethod(_to_dict)
