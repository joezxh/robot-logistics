"""REST endpoints for floor_shell CRUD."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from rcs_backend.config import get_settings, Settings
from rcs_backend.models.floor_shell import FloorShell
from rcs_backend.services.shell_store import MemoryShellStore, default_memory_store
from rcs_backend.topology.validate import validate_shell

router = APIRouter()


def _get_store() -> MemoryShellStore:
    return default_memory_store()


@router.get("/shell", summary="List all stored shells")
async def list_shells(store: MemoryShellStore = Depends(_get_store)) -> list[dict]:
    site_ids = await store.list_sites()
    out = []
    for sid in site_ids:
        shell = await store.get_shell(sid)
        if shell is None:
            continue
        out.append({
            "site_id": sid,
            "bounds": {"w": shell.bounds.w, "d": shell.bounds.d},
            "zone_count": len(shell.zones),
        })
    return out


@router.get("/shell/{site_id}", response_model=FloorShell, summary="Get shell by site_id")
async def get_shell(site_id: str, store: MemoryShellStore = Depends(_get_store)) -> FloorShell:
    shell = await store.get_shell(site_id)
    if shell is None:
        raise HTTPException(status_code=404, detail=f"site_id '{site_id}' not found")
    return shell


@router.put("/shell/{site_id}", summary="Save/replace shell by site_id")
async def put_shell(
    site_id: str,
    shell: FloorShell,
    store: MemoryShellStore = Depends(_get_store),
    settings: Settings = Depends(get_settings),
) -> dict:
    report = validate_shell(shell, max_bounds_m=settings.max_shell_bounds_m)
    if not report.ok:
        raise HTTPException(status_code=422, detail={"errors": report.errors})
    await store.save_shell(site_id, shell)
    return {"site_id": site_id, "ok": True, "warnings": report.warnings}
