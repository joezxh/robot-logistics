"""REST API for device management (mounted under /api/rcs/devices)."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from rcs.services.control import control_devices as dev_svc

router = APIRouter()


class DeviceCreate(BaseModel):
    device_id: str
    morphology: str
    num_joints: int = 0
    control_hz: int = 0
    limits: dict = {}
    home_joints: list = []
    spec: dict = {}


class DeviceUpdate(BaseModel):
    limits: dict | None = None
    home_joints: list | None = None
    spec: dict | None = None
    status: str | None = None
    mode: str | None = None


@router.get("/devices")
async def list_devices():
    return await dev_svc.list_devices()


@router.post("/devices", status_code=201)
async def create_device(body: DeviceCreate):
    return await dev_svc.register(**body.model_dump())


@router.get("/devices/{device_id}")
async def get_device(device_id: str):
    dev = await dev_svc.get(device_id)
    if dev is None:
        raise HTTPException(404, "device not found")
    return dev


@router.put("/devices/{device_id}")
async def update_device(device_id: str, body: DeviceUpdate):
    updated = await dev_svc.update(device_id, **body.model_dump(exclude_none=True))
    if updated is None:
        raise HTTPException(404, "device not found")
    return updated


@router.delete("/devices/{device_id}", status_code=204)
async def delete_device(device_id: str):
    if not await dev_svc.delete(device_id):
        raise HTTPException(404, "device not found")