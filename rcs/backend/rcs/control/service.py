"""FastAPI router + WS handlers for RCS-1."""
from __future__ import annotations
import asyncio
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Optional

from .security import require_api_key
from .state.command import Command, CommandType
from .state.pose import Pose6D
from .registry import registry
from .loop import ControlLoop
from .dispatch import COMMAND_QUEUE_MAXSIZE, DispatchError, dispatch_command

# HTTP status for each transport-agnostic dispatch error code.
_DISPATCH_HTTP_STATUS = {
    "unknown_device": 404,
    "device_locked": 423,
    "queue_full": 503,
}


_loop: ControlLoop | None = None


def bind_loop(loop: ControlLoop) -> None:
    global _loop
    _loop = loop


class CommandRequest(BaseModel):
    command_id: Optional[str] = None
    type: str = Field(..., pattern="^(move_j|move_l|stop|home|estop|recover)$")
    target_pose: Pose6D | None = None
    target_joints: list[float] | None = None
    speed_scale: float = Field(1.0, ge=0.0, le=10.0)
    constraints: dict | None = None


rcs_router = APIRouter()


@rcs_router.get("/registry")
async def list_devices(_: None = Depends(require_api_key)):
    return {"devices": [p.to_dict() for p in registry.list_devices()]}


@rcs_router.post("/{device_id}/command", dependencies=[Depends(require_api_key)])
async def post_command(device_id: str, payload: CommandRequest):
    try:
        result = dispatch_command(
            device_id,
            type=payload.type,
            command_id=payload.command_id,
            target_pose=payload.target_pose,
            target_joints=payload.target_joints,
            speed_scale=payload.speed_scale,
            constraints=payload.constraints,
        )
    except DispatchError as exc:
        headers = {"Retry-After": "1"} if exc.code == "queue_full" else None
        raise HTTPException(
            status_code=_DISPATCH_HTTP_STATUS.get(exc.code, 400),
            detail=exc.detail,
            headers=headers,
        )
    body = {"status": result.status, "device_id": result.device_id}
    if result.command_id is not None:
        body["command_id"] = result.command_id
    return body


@rcs_router.get("/{device_id}/state", dependencies=[Depends(require_api_key)])
async def get_state(device_id: str):
    try:
        ctrl = registry.get_controller(device_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown device_id: {device_id}")
    return {
        "device_id": device_id,
        "mode": ctrl.state.mode.value,
        "active_command_id": ctrl.state.active_command_id,
        "last_error": ctrl.state.last_error,
    }


@rcs_router.post("/{device_id}/estop", dependencies=[Depends(require_api_key)])
async def estop(device_id: str):
    try:
        ctrl = registry.get_controller(device_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown device_id: {device_id}")
    ctrl.estop()
    return {"status": "estop", "device_id": device_id}


@rcs_router.post("/{device_id}/clear_estop", dependencies=[Depends(require_api_key)])
async def clear_estop(device_id: str):
    try:
        ctrl = registry.get_controller(device_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown device_id: {device_id}")
    ctrl.clear_estop()
    return {"status": "cleared", "device_id": device_id}


@rcs_router.get("/_health")
async def health():
    if _loop is None:
        return {"running": False}
    return {"running": True, "loop": _loop.tick_health()}


async def ws_overview(websocket: WebSocket) -> None:
    if _loop is None:
        await websocket.close()
        return
    await websocket.accept()
    q = _loop.stream.subscribe()
    try:
        while True:
            payload = await q.get()
            await websocket.send_bytes(payload)
    except WebSocketDisconnect:
        pass
    finally:
        _loop.stream.unsubscribe(q)


async def ws_device(websocket: WebSocket, device_id: str) -> None:
    if _loop is None:
        await websocket.close()
        return
    await websocket.accept()
    q = _loop.stream.subscribe()
    try:
        while True:
            payload = await q.get()
            try:
                obj = json.loads(payload.decode())
            except Exception:
                continue
            if obj.get("device_id") == device_id:
                await websocket.send_bytes(payload)
    except WebSocketDisconnect:
        pass
    finally:
        _loop.stream.unsubscribe(q)
