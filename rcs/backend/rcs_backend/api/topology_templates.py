"""REST endpoints for 6 scenario templates."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from rcs_backend.topology.templates import list_templates, get_template

router = APIRouter()


@router.get("/templates", summary="List all 6 scenario templates")
async def list_all() -> list[dict]:
    return [t.model_dump() for t in list_templates()]


@router.get("/templates/{scenario_id}", summary="Get one template by scenario_id")
async def get_one(scenario_id: str) -> dict:
    try:
        bundle = get_template(scenario_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"scenario '{scenario_id}' not found")
    return {
        "scenario_id": scenario_id,
        "shell": bundle.shell.model_dump(),
        "grid": bundle.grid.model_dump(),
        "metadata": bundle.metadata,
    }
