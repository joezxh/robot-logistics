"""Site map persistence: nodes/edges JSONB + versioning + import/export."""
from __future__ import annotations
from typing import Optional

from sqlalchemy import select

from rcs.db import models, session as db_session


async def create(name: str, nodes: list, edges: list) -> dict:
    async for s in db_session.session():
        m = models.SiteMap(name=name, nodes_json=nodes or [], edges_json=edges or [],
                           current_version=1)
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


async def list_maps() -> list[dict]:
    async for s in db_session.session():
        rows = (await s.execute(select(models.SiteMap))).scalars().all()
        return [_to_dict(m) for m in rows]
    return []


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
        "current_version": m.current_version,
        "nodes": m.nodes_json or [],
        "edges": m.edges_json or [],
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
    }