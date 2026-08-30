"""REST API for command + event logs."""
from __future__ import annotations
from fastapi import APIRouter, Query

from rcs.services.control import control_logs as logs_svc

router = APIRouter()


@router.get("/logs/commands")
async def list_commands(device_id: str | None = None,
                        limit: int = Query(100, le=500)):
    return await logs_svc.list_commands(device_id=device_id, limit=limit)


@router.get("/logs/events")
async def list_events(level: str | None = None,
                      limit: int = Query(100, le=500)):
    return await logs_svc.list_events(level=level, limit=limit)