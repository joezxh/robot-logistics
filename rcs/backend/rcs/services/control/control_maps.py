"""Site map persistence: nodes/edges JSONB + versioning + import/export.

Also owns the built-in warehouse templates: rows flagged ``is_template=True``
are pre-built warehouse-type blueprints (see
``rcs.models.site_map_templates``) rather than live, editable maps.
"""
from __future__ import annotations
import copy
import uuid
from typing import Optional

from sqlalchemy import delete as sa_delete, select

from rcs.db import models, session as db_session
from rcs.models import site_map_templates


async def create(name: str, nodes: list, edges: list,
                 is_template: bool = False,
                 map_id: Optional[str] = None) -> dict:
    """Create a live site map.

    ``map_id`` lets a caller pin the id so it can match a ``robot_topology_shell
    .site_id`` — templates and template-derived sites keep one shared id across
    all three topology tables.
    """
    async for s in db_session.session():
        m = models.SiteMap(map_id=map_id or str(uuid.uuid4()), name=name,
                           nodes_json=nodes or [], edges_json=edges or [],
                           current_version=1, is_template=is_template)
        s.add(m)
        await s.commit()
        await s.refresh(m)
        await _snapshot(s, m, note="initial")
        return _to_dict(m)
    raise RuntimeError("db session closed")


async def get(map_id: str) -> Optional[dict]:
    async for s in db_session.session():
        m = await s.get(models.SiteMap, map_id)
        return _to_dict(m) if m else None
    return None


async def list_maps(include_templates: bool = False) -> list[dict]:
    """List live maps.

    Templates are excluded by default so management UIs never offer them as
    editable maps; pass ``include_templates=True`` to see everything.
    """
    async for s in db_session.session():
        stmt = select(models.SiteMap)
        if not include_templates:
            stmt = stmt.where(models.SiteMap.is_template.is_(False))
        rows = (await s.execute(stmt)).scalars().all()
        return [_to_dict(m) for m in rows]
    return []


async def list_templates() -> list[dict]:
    """List only the warehouse-type template rows (``is_template=True``)."""
    async for s in db_session.session():
        rows = (await s.execute(
            select(models.SiteMap).where(models.SiteMap.is_template.is_(True))
        )).scalars().all()
        return [_to_dict(m) for m in rows]
    return []


async def seed_templates() -> list[dict]:
    """Insert (or refresh) the built-in warehouse templates. Idempotent.

    A template is more than a navigation graph: it also needs a FloorShell (so
    the 2D/3D map can draw it) and one grid row per zone. This writes all three
    tables — ``robot_site_maps``, ``robot_topology_shell`` and
    ``robot_topology_grid`` — sharing the deterministic ``tpl-<key>`` id, so
    re-running refreshes contents in place instead of duplicating rows.

    Templates are not versioned: ``current_version`` stays at 1.
    """
    async for s in db_session.session():
        out = []
        for t in site_map_templates.list_templates():
            # 1. navigation graph
            m = await s.get(models.SiteMap, t.map_id)
            if m is None:
                m = models.SiteMap(map_id=t.map_id)
                s.add(m)
            m.name = t.name
            m.is_template = True
            m.nodes_json = copy.deepcopy(t.nodes)
            m.edges_json = copy.deepcopy(t.edges)
            m.current_version = 1

            # 2. FloorShell geometry
            shell = await s.get(models.TopologyShell, t.site_id)
            if shell is None:
                shell = models.TopologyShell(site_id=t.site_id)
                s.add(shell)
            shell.name = t.name
            shell.is_template = True
            shell.width_m = t.shell.bounds.w
            shell.depth_m = t.shell.bounds.d
            shell.height_m = t.shell.bounds.h
            shell.data = t.shell.model_dump(mode="json")

            # 3. per-zone grid rows — fully derived from the shell, so replace
            #    them wholesale rather than trying to diff them.
            await s.execute(
                sa_delete(models.TopologyGrid).where(
                    models.TopologyGrid.site_id == t.site_id)
            )
            for row in t.grid_rows():
                s.add(models.TopologyGrid(site_id=t.site_id, is_template=True, **row))

            out.append(m)
        await s.commit()
        for m in out:
            await s.refresh(m)
        return [_to_dict(m) for m in out]
    return []


async def create_from_template(key: str, name: Optional[str] = None,
                               new_id: Optional[str] = None) -> Optional[dict]:
    """Materialise a template into a new, editable live site.

    Clones all three artefacts — FloorShell geometry, per-zone grid rows and the
    navigation graph — under one fresh id, so the result renders on the map
    straight away. Everything is deep-copied, so editing the new site can never
    mutate the template. Returns ``None`` when ``key`` is unknown.
    """
    try:
        t = site_map_templates.get_template(key)
    except KeyError:
        return None

    site_id = new_id or str(uuid.uuid4())
    title = name or t.name

    shell_data = t.shell.model_dump(mode="json")
    shell_data["metadata"] = {
        **shell_data.get("metadata", {}),
        "name": title,
        "template_key": t.key,
    }

    async for s in db_session.session():
        s.add(models.TopologyShell(
            site_id=site_id, name=title, is_template=False,
            width_m=t.shell.bounds.w, depth_m=t.shell.bounds.d,
            height_m=t.shell.bounds.h, data=shell_data,
        ))
        # Flush the shell first: grid rows carry an FK to it. The ORM
        # relationship now declares that dependency, but the explicit flush
        # keeps the ordering obvious and independent of mapper inference.
        await s.flush()
        for row in t.grid_rows():
            s.add(models.TopologyGrid(site_id=site_id, is_template=False, **row))
        await s.commit()

    return await create(name=title, nodes=copy.deepcopy(t.nodes),
                        edges=copy.deepcopy(t.edges),
                        is_template=False, map_id=site_id)


async def update(map_id: str, name: Optional[str], nodes: list, edges: list) -> Optional[dict]:
    async for s in db_session.session():
        m = await s.get(models.SiteMap, map_id)
        if m is None:
            return None
        if name is not None:
            m.name = name
        m.nodes_json = nodes or []
        m.edges_json = edges or []
        m.current_version += 1
        await s.commit()
        await s.refresh(m)
        await _snapshot(s, m, note=f"v{m.current_version}")
        return _to_dict(m)
    return None


async def delete(map_id: str) -> bool:
    async for s in db_session.session():
        m = await s.get(models.SiteMap, map_id)
        if m is None:
            return False
        await s.delete(m)
        await s.commit()
        return True
    return False


async def import_json(map_id: str, payload: dict) -> Optional[dict]:
    return await update(map_id, name=None,
                        nodes=payload.get("nodes", []),
                        edges=payload.get("edges", []))


async def export_json(map_id: str) -> Optional[dict]:
    m = await get(map_id)
    if m is None:
        return None
    return {"map_id": m["map_id"], "name": m["name"],
            "nodes": m["nodes"], "edges": m["edges"]}


async def list_versions(map_id: str) -> list[dict]:
    async for s in db_session.session():
        rows = (await s.execute(
            select(models.SiteMapVersion).where(models.SiteMapVersion.map_id == map_id)
            .order_by(models.SiteMapVersion.version)
        )).scalars().all()
        return [{"version_id": v.version_id, "version": v.version,
                 "note": v.note,
                 "created_at": v.created_at.isoformat() if v.created_at else None}
                for v in rows]
    return []


async def restore_version(map_id: str, version_id: str) -> Optional[dict]:
    async for s in db_session.session():
        v = await s.get(models.SiteMapVersion, version_id)
        if v is None or v.map_id != map_id:
            return None
        m = await s.get(models.SiteMap, map_id)
        m.nodes_json = v.nodes_json
        m.edges_json = v.edges_json
        m.current_version += 1
        await s.commit()
        await s.refresh(m)
        await _snapshot(s, m, note=f"restore->{version_id}")
        return _to_dict(m)
    return None


async def _snapshot(s, m: models.SiteMap, note: str) -> None:
    s.add(models.SiteMapVersion(
        map_id=m.map_id, version=m.current_version,
        nodes_json=m.nodes_json, edges_json=m.edges_json, note=note,
    ))
    await s.commit()


def _to_dict(m: models.SiteMap) -> dict:
    return {
        "map_id": m.map_id,
        "name": m.name,
        # Coerced to bool: the column is NOT NULL DEFAULT FALSE, but rows
        # created before the migration may still read back as None in a
        # session that predates the DDL.
        "is_template": bool(m.is_template),
        "current_version": m.current_version,
        "nodes": m.nodes_json or [],
        "edges": m.edges_json or [],
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
    }