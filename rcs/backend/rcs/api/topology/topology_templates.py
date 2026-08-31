"""REST endpoints for 6 scenario templates.

Task 4 deleted ``rcs.models.topology_templates``; the 6 scenario blueprints now
live as private builders in ``rcs.services.control.control_unified_maps``. This
route is a thin stopgap that reads them from there so the existing contract
(``shell`` / ``grid`` / ``metadata``) is unchanged. Task 6 rewrites this route to
serve the DB-backed ``UnifiedMap`` template rows.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from rcs.services.control.control_unified_maps import (
    _build_scenario_bundle, _list_scenario_infos,
)

router = APIRouter()


@router.get("/templates", summary="List all 6 scenario templates")
async def list_all() -> list[dict]:
    return [t.model_dump() for t in _list_scenario_infos()]


@router.get("/templates/{scenario_id}", summary="Get one template by scenario_id")
async def get_one(scenario_id: str) -> dict:
    try:
        bundle = _build_scenario_bundle(scenario_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"scenario '{scenario_id}' not found")
    return {
        "scenario_id": scenario_id,
        "shell": bundle.shell.model_dump(),
        "grid": bundle.grid.model_dump(),
        "metadata": bundle.metadata,
    }
