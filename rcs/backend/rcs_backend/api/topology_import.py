"""REST endpoints for DXF import."""
from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from rcs_backend.topology.dxf_parser import parse_dxf
from rcs_backend.topology.dxf_to_shell import dxf_to_shell
from rcs_backend.topology.validate import validate_shell
from rcs_backend.services.shell_store import MemoryShellStore, default_memory_store

router = APIRouter()

_store = default_memory_store()


@router.post("/import/dxf", summary="Parse uploaded DXF into FloorShell (no save)")
async def import_dxf_only(file: UploadFile = File(...)) -> dict:
    raw = await file.read()
    try:
        text = raw.decode("utf-8", errors="ignore")
        doc = parse_dxf(text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"DXF parse failed: {exc}")
    shell = dxf_to_shell(doc)
    report = validate_shell(shell)
    return {
        "shell": shell.model_dump(),
        "validation": report.model_dump(),
        "entity_count": len(doc.entities),
    }


@router.post("/import/dxf/{site_id}", summary="Upload + parse + save DXF as shell")
async def import_dxf_save(
    site_id: str,
    file: UploadFile = File(...),
    store: MemoryShellStore = Depends(lambda: _store),
) -> dict:
    raw = await file.read()
    try:
        doc = parse_dxf(raw.decode("utf-8", errors="ignore"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"DXF parse failed: {exc}")
    shell = dxf_to_shell(doc)
    report = validate_shell(shell)
    if not report.ok:
        raise HTTPException(status_code=422, detail={"errors": report.errors})
    shell.metadata["dxf_filename"] = file.filename or "unknown.dxf"
    shell.metadata["imported_at"] = "auto"
    await store.save_shell(site_id, shell)
    return {"site_id": site_id, "ok": True, "shell": shell.model_dump()}
