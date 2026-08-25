"""REST API for scheduler configurations."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from rcs.control.scheduler import service as sch_svc

router = APIRouter()


class ConfigCreate(BaseModel):
    name: str
    strategy: str = "util-weighted"
    weights: dict = {}


class ConfigUpdate(BaseModel):
    name: str | None = None
    strategy: str | None = None
    weights: dict | None = None


@router.get("/scheduler-configs")
async def list_configs():
    return await sch_svc.list_configs()


@router.get("/scheduler-configs/active")
async def get_active():
    c = await sch_svc.get_active()
    if c is None:
        raise HTTPException(404, "no active config")
    return c


@router.post("/scheduler-configs", status_code=201)
async def create_config(body: ConfigCreate):
    return await sch_svc.create(**body.model_dump())


@router.put("/scheduler-configs/{config_id}")
async def update_config(config_id: str, body: ConfigUpdate):
    u = await sch_svc.update(config_id, **body.model_dump(exclude_none=True))
    if u is None:
        raise HTTPException(404, "config not found")
    return u


@router.post("/scheduler-configs/{config_id}/activate")
async def activate(config_id: str):
    if not await sch_svc.activate(config_id):
        raise HTTPException(404, "config not found")
    return {"activated": config_id}