"""REST API for site maps (viewer + import/export; no drag editor)."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from rcs.models.site_map_templates import (
    get_template as get_builtin_template,
    list_templates as list_builtin_templates,
    template_summary,
)
from rcs.services.control import control_maps as map_svc

router = APIRouter()


class MapCreate(BaseModel):
    name: str
    nodes: list = []
    edges: list = []


class MapUpdate(BaseModel):
    name: str | None = None
    nodes: list = []
    edges: list = []


@router.get("/maps")
async def list_maps(include_templates: bool = False):
    """List live maps.

    Templates are hidden by default so management UIs don't offer them as
    editable maps; pass ``?include_templates=true`` to include them.
    """
    return await map_svc.list_maps(include_templates=include_templates)


@router.post("/maps", status_code=201)
async def create_map(body: MapCreate):
    return await map_svc.create(**body.model_dump())


# ── Warehouse templates ──────────────────────────────────────────────────────
#
# NOTE: these must stay registered *above* `/maps/{map_id}`, otherwise FastAPI
# matches the literal "templates"/"from-template" segment as a map_id.


@router.get("/maps/templates", summary="List built-in warehouse map templates")
async def list_map_templates():
    """Summaries of the built-in templates, available without a DB round-trip."""
    return [template_summary(t) for t in list_builtin_templates()]


@router.get("/maps/templates/{key}", summary="Get one template definition")
async def get_map_template(key: str):
    try:
        t = get_builtin_template(key)
    except KeyError:
        raise HTTPException(404, f"template '{key}' not found")
    return {**template_summary(t), "nodes": t.nodes, "edges": t.edges}


@router.post("/maps/templates/seed", summary="Seed built-in templates into the DB")
async def seed_map_templates():
    """Idempotent — re-running refreshes template rows instead of duplicating."""
    return await map_svc.seed_templates()


class MapFromTemplate(BaseModel):
    template_key: str
    name: str | None = None


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
async def update_map(map_id: str, body: MapUpdate):
    updated = await map_svc.update(map_id, name=body.name,
                                    nodes=body.nodes, edges=body.edges)
    if updated is None:
        raise HTTPException(404, "map not found")
    return updated


@router.delete("/maps/{map_id}", status_code=204)
async def delete_map(map_id: str):
    if not await map_svc.delete(map_id):
        raise HTTPException(404, "map not found")


@router.post("/maps/{map_id}/import")
async def import_map(map_id: str, payload: dict):
    updated = await map_svc.import_json(map_id, payload)
    if updated is None:
        raise HTTPException(404, "map not found")
    return updated


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