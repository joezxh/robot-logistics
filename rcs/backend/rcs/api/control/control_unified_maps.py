"""REST API for the unified map model (Task 5 of unified-map-model plan).

Mirrors ``rcs.api.control.control_maps`` but operates on the ``UnifiedMap`` /
``MapDynamicState`` tables via ``rcs.services.control.control_unified_maps``.
This router is registered WITHOUT a prefix so Task 6 can mount it at ``/maps``
later; for standalone testing it is mounted at ``/api/rcs`` which yields
``/api/rcs/maps/...``.

The dynamic-state sub-resource (``/maps/{map_id}/dynamic[/...]``) is the core
of this task: the service built in Task 3 has no dynamic get/put, so the
upsert/list/delete queries run directly against ``MapDynamicState`` here using
``_session_cm()`` (a thin async-context-manager wrapper over
``db_session.session()``).
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy import select

from rcs.db import session as db_session
from rcs.db.unified_map import MapDynamicState
from rcs.services.control import control_unified_maps as map_svc
from rcs.services.control.map_mjcf import build_mjcf

router = APIRouter()


@asynccontextmanager
async def _session_cm():
    """Async context manager yielding a session (wraps db_session.session())."""
    async for s in db_session.session():
        yield s


# ── Request models ────────────────────────────────────────────────────────────


class UnifiedMapCreate(BaseModel):
    name: str
    geometry: Optional[dict] = None
    topology: Optional[dict] = None
    semantic: Optional[dict] = None
    is_template: bool = False
    kind: Optional[str] = None
    name_en: Optional[str] = None
    bounds: Optional[dict] = None
    data: Optional[dict] = None


class UnifiedMapUpdate(BaseModel):
    name: Optional[str] = None
    geometry: Optional[dict] = None
    topology: Optional[dict] = None
    semantic: Optional[dict] = None


class DynamicState(BaseModel):
    element_id: str
    state: Optional[str] = None
    payload: Optional[dict] = None


class DynamicStatePut(BaseModel):
    state: Optional[str] = None
    payload: Optional[dict] = None


# ── Helpers ──────────────────────────────────────────────────────────────────


def _dynamic_row_to_dict(row: MapDynamicState) -> dict:
    return {
        "element_id": row.element_id,
        "state": row.state,
        "payload": row.payload,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


# ── Routes ───────────────────────────────────────────────────────────────────
#
# NOTE: the literal-segment routes (/maps/templates, /maps/templates/seed,
# /maps/from-template) are declared ABOVE /maps/{map_id} exactly as the old
# control_maps.py does, so FastAPI matches them before treating "templates" /
# "from-template" as a map_id.


@router.get("/maps")
async def list_maps(include_templates: bool = False):
    """List live maps (templates hidden by default)."""
    return await map_svc.list_maps(include_templates=include_templates)


@router.post("/maps", status_code=201)
async def create_map(body: UnifiedMapCreate):
    return await map_svc.create(**body.model_dump())


@router.get("/maps/templates", summary="List seeded unified map templates")
async def list_unified_templates():
    rows = await map_svc.list_templates()
    return [
        {
            "map_id": r["map_id"],
            "name": r["name"],
            "name_en": r.get("name_en"),
            "kind": r["kind"],
        }
        for r in rows
    ]


@router.post("/maps/templates/seed",
             summary="Seed warehouse + scenario templates into the DB")
async def seed_templates():
    """Idempotent — re-running refreshes template rows instead of duplicating."""
    return await map_svc.seed_templates()


class MapFromTemplate(BaseModel):
    template_key: str
    name: Optional[str] = None


@router.post("/maps/from-template", status_code=201,
             summary="Create an editable map from a template")
async def create_map_from_template(body: MapFromTemplate):
    m = await map_svc.create_from_template(body.template_key, body.name)
    if m is None:
        raise HTTPException(404, f"template '{body.template_key}' not found")
    return m


@router.get("/maps/{map_id}")
async def get_map(map_id: str):
    m = await map_svc.get(map_id)
    if m is None:
        raise HTTPException(404, "map not found")
    return m


@router.put("/maps/{map_id}")
async def update_map(map_id: str, body: UnifiedMapUpdate):
    updated = await map_svc.update(
        map_id, name=body.name, geometry=body.geometry,
        topology=body.topology, semantic=body.semantic,
    )
    if updated is None:
        raise HTTPException(404, "map not found")
    return updated


@router.delete("/maps/{map_id}", status_code=204)
async def delete_map(map_id: str):
    if not await map_svc.delete(map_id):
        raise HTTPException(404, "map not found")
    return Response(status_code=204)


@router.post("/maps/{map_id}/import")
async def import_map(map_id: str, payload: dict):
    updated = await map_svc.import_json(map_id, payload)
    if updated is None:
        raise HTTPException(404, "map not found")
    return updated


@router.get("/maps/{map_id}/mjcf",
             summary="Generate an MJCF scene XML for the 3D map viewer")
async def get_map_mjcf(map_id: str, download: bool = Query(False)):
    """Render the map's ``geometry_json`` (wt_floor_shell) into a mujoco MJCF
    scene. The frontend ``MjcfLoader`` loads this URL directly; ``?download=1``
    returns it as an attachment.
    """
    m = await map_svc.get(map_id)
    if m is None:
        raise HTTPException(404, "map not found")
    # map_svc.get already returns a dict carrying geometry_json (wt_floor_shell)
    xml = build_mjcf(m)
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{map_id}.mjcf.xml"'
    return Response(content=xml, media_type="application/xml", headers=headers)


@router.get("/maps/{map_id}/export")
async def export_map(map_id: str):
    data = await map_svc.export_json(map_id)
    if data is None:
        raise HTTPException(404, "map not found")
    return data


@router.get("/maps/{map_id}/versions")
async def list_versions(map_id: str):
    return await map_svc.list_versions(map_id)


@router.post("/maps/{map_id}/versions/{version_id}/restore")
async def restore_version(map_id: str, version_id: str):
    updated = await map_svc.restore_version(map_id, version_id)
    if updated is None:
        raise HTTPException(404, "version not found")
    return updated


# ── Dynamic state sub-resource ────────────────────────────────────────────────


@router.get("/maps/{map_id}/dynamic")
async def list_dynamic(map_id: str):
    """List all dynamic-state rows for a map.

    404 if the parent map does not exist.
    """
    parent = await map_svc.get(map_id)
    if parent is None:
        raise HTTPException(404, "map not found")

    async with _session_cm() as s:
        rows = (await s.execute(
            select(MapDynamicState)
            .where(MapDynamicState.map_id == map_id)
        )).scalars().all()
        return [_dynamic_row_to_dict(r) for r in rows]


@router.put("/maps/{map_id}/dynamic/{element_id}")
async def put_dynamic(map_id: str, element_id: str, body: DynamicStatePut):
    """Upsert a dynamic-state row for (map_id, element_id).

    Reuses the unique constraint (map_id, element_id): fetch existing first,
    update in place if present, otherwise insert a new row. 404 if the parent
    map does not exist.
    """
    parent = await map_svc.get(map_id)
    if parent is None:
        raise HTTPException(404, "map not found")

    async with _session_cm() as s:
        existing = (await s.execute(
            select(MapDynamicState).where(
                MapDynamicState.map_id == map_id,
                MapDynamicState.element_id == element_id,
            )
        )).scalar_one_or_none()

        if existing is not None:
            if body.state is not None:
                existing.state = body.state
            if body.payload is not None:
                existing.payload = body.payload
            row = existing
        else:
            row = MapDynamicState(
                map_id=map_id,
                element_id=element_id,
                state=body.state if body.state is not None else "",
                payload=body.payload,
            )
            s.add(row)

        await s.commit()
        await s.refresh(row)
        return _dynamic_row_to_dict(row)


@router.delete("/maps/{map_id}/dynamic/{element_id}", status_code=204)
async def delete_dynamic(map_id: str, element_id: str):
    """Delete a single dynamic-state row. 404 if not found."""
    # Parent existence is implied by the row's FK; check the row directly.
    async with _session_cm() as s:
        row = (await s.execute(
            select(MapDynamicState).where(
                MapDynamicState.map_id == map_id,
                MapDynamicState.element_id == element_id,
            )
        )).scalar_one_or_none()
        if row is None:
            raise HTTPException(404, "dynamic state not found")
        await s.delete(row)
        await s.commit()
    return Response(status_code=204)
