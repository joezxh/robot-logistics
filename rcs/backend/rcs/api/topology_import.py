"""REST endpoints for DXF import (SQLAlchemy-backed)."""
from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, HTTPException
from rcs.topology.dxf_parser import parse_dxf
from rcs.topology.dxf_to_shell import dxf_to_shell
from rcs.topology.validate import validate_shell
from rcs.db import models, session as db_session

router = APIRouter()


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
async def import_dxf_save(site_id: str, file: UploadFile = File(...)) -> dict:
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
    async for s in db_session.session():
        row = await s.get(models.TopologyShell, site_id)
        if row is None:
            row = models.TopologyShell(site_id=site_id)
        row.name = shell.metadata.get("name")
        row.width_m = shell.bounds.w
        row.depth_m = shell.bounds.d
        row.height_m = shell.bounds.h
        row.data = shell.model_dump()
        s.add(row)
        await s.commit()
    return {"site_id": site_id, "ok": True, "shell": shell.model_dump()}