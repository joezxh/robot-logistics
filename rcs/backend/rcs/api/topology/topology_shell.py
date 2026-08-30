"""REST endpoints for floor_shell CRUD (SQLAlchemy-backed)."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from rcs.config import get_settings, Settings
from rcs.models.floor_shell import FloorShell
from rcs.services.topology.validate import validate_shell
from rcs.db import models, session as db_session

router = APIRouter()


async def _get_shell(site_id: str) -> models.TopologyShell | None:
    async for s in db_session.session():
        return await s.get(models.TopologyShell, site_id)
    return None


@router.get("/shell", summary="List all stored shells")
async def list_shells() -> list[dict]:
    from sqlalchemy import select
    async for s in db_session.session():
        rows = (await s.execute(select(models.TopologyShell))).scalars().all()
        out: list[dict] = []
        for r in rows:
            data = r.data or {}
            bounds = data.get("bounds", {})
            zones = data.get("zones", [])
            out.append({
                "site_id": r.site_id,
                "bounds": {"w": bounds.get("w", r.width_m), "d": bounds.get("d", r.depth_m)},
                "zone_count": len(zones),
            })
        return out


@router.get("/shell/{site_id}", response_model=FloorShell, summary="Get shell by site_id")
async def get_shell(site_id: str) -> FloorShell:
    shell_row = await _get_shell(site_id)
    if shell_row is None:
        raise HTTPException(status_code=404, detail=f"site_id '{site_id}' not found")
    return FloorShell(**(shell_row.data or {}))


@router.put("/shell/{site_id}", summary="Save/replace shell by site_id")
async def put_shell(
    site_id: str,
    shell: FloorShell,
    settings: Settings = Depends(get_settings),
) -> dict:
    report = validate_shell(shell, max_bounds_m=settings.max_shell_bounds_m)
    if not report.ok:
        raise HTTPException(status_code=422, detail={"errors": report.errors})
    async for s in db_session.session():
        row = await s.get(models.TopologyShell, site_id)
        if row is None:
            row = models.TopologyShell(site_id=site_id)
        row.name = shell.metadata.get("name") if shell.metadata else None
        row.width_m = shell.bounds.w
        row.depth_m = shell.bounds.d
        row.height_m = shell.bounds.h
        row.data = shell.model_dump()
        s.add(row)
        await s.commit()
    return {"site_id": site_id, "ok": True, "warnings": report.warnings}