"""FastAPI application entry point.

Includes the prototype business API (devices / tasks / metrics / logs),
optional API-key auth + rate limiting, an SSE log stream, /metrics for
Prometheus scraping, and a basic task-rollback endpoint.
"""
from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field

from backend.services.runtime import runtime
from backend.services.security import rate_limit_dep, require_api_key
from backend.services import metrics as prom_metrics
from backend.algorithm.scheduler.task import TaskPriority
from backend.data.db import create_tables, init_db
from backend.services.alerts import engine as alert_engine
from backend.config import settings

# RCS is a sibling subproject (../../rcs). It can either be embedded here
# (default, preserves the historical single-port deployment) or run as an
# independent service, in which case the simulation backend does not import it
# at all. Set RCS_EMBEDDED=0 to switch to the standalone topology.
rcs = None
if settings.rcs_embedded:
    try:
        from rcs import rcs  # type: ignore[no-redef]
    except ImportError as exc:  # pragma: no cover - deployment misconfiguration
        raise ImportError(
            "RCS_EMBEDDED is on but the 'rcs' package is not importable. "
            "Either install it (pip install -e ../rcs), add the repo root to "
            "PYTHONPATH, or set RCS_EMBEDDED=0 to run RCS standalone."
        ) from exc


class TaskCreateRequest(BaseModel):
    type: str = Field(..., description="Task type, e.g. dock_loading / agv_transport / warehouse_storage")
    description: str = "task"
    priority: int = Field(3, ge=1, le=4)
    device_id: str


class ControlRequest(BaseModel):
    action: str  # start | stop | reset


class RollbackRequest(BaseModel):
    limit: int = Field(1, ge=1, le=20)


class BulkRollbackRequest(BaseModel):
    device_ids: list[str] = Field(..., min_length=1, max_length=64)
    limit_per_device: int = Field(2, ge=1, le=10)


class SiteCreateRequest(BaseModel):
    id: str = Field(..., min_length=1, max_length=64)
    kind: str = Field(..., pattern="^(dock|warehouse)$")
    name: str = Field(..., min_length=1, max_length=128)
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    width: float = 2.5
    height: float = 1.5
    depth: float = 2.5
    rotation: float = 0.0
    status: str = "active"
    color: str = "#5eb0ff"
    metadata: dict | None = None


class SiteUpdateRequest(BaseModel):
    name: str | None = None
    status: str | None = None
    color: str | None = None
    x: float | None = None
    y: float | None = None
    z: float | None = None
    width: float | None = None
    height: float | None = None
    depth: float | None = None
    rotation: float | None = None
    metadata: dict | None = None


class DeviceCreateRequest(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=64)
    device_type: str = Field(..., pattern="^(container_robot|agv|stacker)$")
    name: str = Field(..., min_length=1, max_length=128)
    x: float = 0.0
    z: float = 0.0


class DeviceUpdateRequest(BaseModel):
    name: str | None = None
    battery: float | None = Field(None, ge=0.0, le=100.0)
    status: str | None = None
    x: float | None = None
    z: float | None = None


def _record_metrics() -> None:
    """Sample gauges on every tick."""
    prom_metrics.set_gauge("robot_logic_devices_total", len(runtime.devices.devices))
    tasks = list(runtime.tasks.values())
    for status_name in ("pending", "running", "completed", "reverted", "failed"):
        prom_metrics.set_gauge(
            f"robot_logic_tasks_{status_name}",
            sum(1 for t in tasks if t["status"] == status_name),
        )
    alerts = alert_engine.snapshot()
    for severity in ("info", "warning", "critical"):
        prom_metrics.set_gauge(
            f"robot_logic_alerts_{severity}",
            sum(1 for a in alerts if a["severity"] == severity),
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = Path("data")
    db_path.mkdir(parents=True, exist_ok=True)
    try:
        init_db()
        await create_tables()
    except Exception as exc:  # pragma: no cover
        print(f"[lifespan] database init failed: {exc}")

    runtime.start()
    print(f"[lifespan] runtime started, devices={list(runtime.devices.devices)}")

    async def tick_loop() -> None:
        while True:
            await asyncio.sleep(0.5)
            try:
                runtime.tick(0.5)
                alert_engine.evaluate(runtime)
                _record_metrics()
            except Exception as exc:  # never let one tick crash the loop
                runtime.log(runtime.trace_id(), None, "tick_error", repr(exc))

    tick_task = asyncio.create_task(tick_loop())
    try:
        if rcs is not None:
            async with rcs.lifespan():
                yield
        else:
            yield
    finally:
        tick_task.cancel()
        try:
            await tick_task
        except asyncio.CancelledError:
            pass
        runtime.stop()


# When auth is enabled, every endpoint requires it. When disabled, this is a
# no-op dependency and rate limiting is still active unless turned off via env.
app = FastAPI(
    title="机器人智能仓储物流系统 API",
    version="1.0.0",
    description="物流装卸机器人系统原型 API",
    lifespan=lifespan,
    dependencies=[Depends(require_api_key)],
)
if rcs is not None:
    app.include_router(rcs.router(), prefix="/api/rcs")


@app.get("/", dependencies=[])
async def root():
    return {"message": "Robot Logic System API", "version": "1.0.0"}


@app.get("/api/devices", dependencies=[])
async def list_devices():
    prom_metrics.inc("robot_logic_api_hits", 1.0)
    return runtime.devices.list()


@app.get("/api/tasks", dependencies=[])
async def list_tasks():
    return list(runtime.tasks.values())


@app.post("/api/tasks", dependencies=[Depends(rate_limit_dep)])
async def create_task(payload: TaskCreateRequest):
    prom_metrics.inc("robot_logic_tasks_created_total", 1.0)
    try:
        priority = TaskPriority(payload.priority)
    except ValueError:
        raise HTTPException(status_code=400, detail="priority must be 1..4")
    if payload.device_id not in runtime.devices.devices:
        raise HTTPException(status_code=400, detail=f"unknown device_id: {payload.device_id}")
    return runtime.create_task(payload.type, payload.description, priority, payload.device_id)


@app.get("/api/metrics", dependencies=[])
async def metrics():
    return runtime.metrics()


@app.get("/api/stats", dependencies=[])
async def stats():
    return runtime.stats()


@app.get("/api/sites", dependencies=[])
async def list_sites():
    return runtime.sites.list()


@app.post("/api/sites", dependencies=[Depends(rate_limit_dep)])
async def create_site(payload: SiteCreateRequest):
    try:
        site = runtime.sites.add(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return site.to_dict()


@app.patch("/api/sites/{site_id}", dependencies=[Depends(rate_limit_dep)])
async def update_site(site_id: str, payload: SiteUpdateRequest):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    try:
        site = runtime.sites.update(site_id, data)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown site_id: {site_id}")
    return site.to_dict()


@app.delete("/api/sites/{site_id}", dependencies=[Depends(rate_limit_dep)])
async def delete_site(site_id: str):
    try:
        site = runtime.sites.remove(site_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown site_id: {site_id}")
    return site.to_dict()


@app.post("/api/devices/register", dependencies=[Depends(rate_limit_dep)])
async def register_device(payload: DeviceCreateRequest):
    """Register a custom device at runtime (used for demo / data import)."""
    from backend.algorithm.simulator.device import Device  # local import to avoid cycles
    if payload.device_id in runtime.devices.devices:
        raise HTTPException(status_code=409, detail=f"device {payload.device_id!r} already exists")
    runtime.devices.devices[payload.device_id] = Device(
        device_id=payload.device_id,
        device_type=payload.device_type,
        name=payload.name,
        position=[payload.x, 0.0, payload.z],
    )
    return runtime.devices.get(payload.device_id).snapshot()


@app.patch("/api/devices/{device_id}", dependencies=[Depends(rate_limit_dep)])
async def update_device(device_id: str, payload: DeviceUpdateRequest):
    if device_id not in runtime.devices.devices:
        raise HTTPException(status_code=404, detail=f"unknown device_id: {device_id}")
    device = runtime.devices.devices[device_id]
    if payload.name is not None:
        device.name = payload.name
    if payload.battery is not None:
        device.battery = float(payload.battery)
    if payload.status is not None:
        from backend.algorithm.simulator.device import DeviceStatus
        try:
            device.status = DeviceStatus(payload.status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"invalid status: {payload.status!r}")
    if payload.x is not None:
        device.position[0] = float(payload.x)
    if payload.z is not None:
        device.position[2] = float(payload.z)
    return device.snapshot()


@app.delete("/api/devices/{device_id}", dependencies=[Depends(rate_limit_dep)])
async def delete_device(device_id: str):
    if device_id not in runtime.devices.devices:
        raise HTTPException(status_code=404, detail=f"unknown device_id: {device_id}")
    device = runtime.devices.devices.pop(device_id)
    return device.snapshot()


@app.get("/api/logs", dependencies=[])
async def logs():
    return runtime.logs[-200:]


@app.post("/api/control", dependencies=[Depends(rate_limit_dep)])
async def control(payload: ControlRequest):
    action = payload.action.lower()
    if action == "start":
        runtime.start()
    elif action == "stop":
        runtime.stop()
    elif action == "reset":
        runtime.stop()
        runtime.tasks.clear()
        runtime.logs.clear()
    else:
        raise HTTPException(status_code=400, detail="action must be start|stop|reset")
    return runtime.status()


@app.get("/api/status", dependencies=[])
async def status():
    return {**runtime.status(), "queue_size": len(runtime.tasks)}


@app.post("/api/tasks/{task_id}/rollback", dependencies=[Depends(rate_limit_dep)])
async def rollback_one(task_id: str):
    try:
        return runtime.rollback_task(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown task_id: {task_id}")
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@app.post("/api/tasks/rollback", dependencies=[Depends(rate_limit_dep)])
async def rollback_recent(payload: RollbackRequest):
    return runtime.rollback_recent(payload.limit)


@app.post("/api/devices/rollback", dependencies=[Depends(rate_limit_dep)])
async def bulk_rollback(payload: BulkRollbackRequest):
    """Roll back recent completed/failed tasks for a list of devices."""
    unknown = [d for d in payload.device_ids if d not in runtime.devices.devices]
    if unknown:
        raise HTTPException(status_code=400, detail=f"unknown device_ids: {unknown}")
    return runtime.rollback_devices(payload.device_ids, payload.limit_per_device)


@app.get("/api/logs/stream", dependencies=[])
async def stream_logs(request: Request) -> StreamingResponse:
    """Server-Sent Events stream of new log entries."""
    queue = runtime.subscribe()

    async def event_source() -> AsyncIterator[bytes]:
        try:
            # Initial retry hint per SSE spec.
            yield b"retry: 5000\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    entry = await asyncio.wait_for(queue.get(), timeout=2.0)
                except asyncio.TimeoutError:
                    # heartbeat keeps the connection alive behind proxies
                    yield b": ping\n\n"
                    continue
                yield f"data: {json.dumps(entry, ensure_ascii=False)}\n\n".encode("utf-8")
        finally:
            runtime.unsubscribe(queue)

    return StreamingResponse(event_source(), media_type="text/event-stream")


@app.get("/api/alerts", dependencies=[])
async def list_alerts():
    prom_metrics.inc("robot_logic_api_hits", 1.0)
    return {
        "firing": alert_engine.snapshot(),
        "count_by_severity": {
            severity: sum(1 for a in alert_engine.snapshot() if a["severity"] == severity)
            for severity in ("info", "warning", "critical")
        },
    }


class AckRequest(BaseModel):
    by: str = "operator"


@app.post("/api/alerts/{alert_id}/ack", dependencies=[Depends(rate_limit_dep)])
async def ack_alert(alert_id: str, payload: AckRequest):
    result = alert_engine.acknowledge(alert_id, by=payload.by)
    if result is None:
        raise HTTPException(status_code=404, detail=f"unknown alert_id: {alert_id}")
    return result.to_dict()


@app.get("/api/alerts/stream", dependencies=[])
async def stream_alerts(request: Request) -> StreamingResponse:
    """SSE stream of alert state transitions (firing / ack / resolved)."""
    queue = alert_engine.subscribe()

    async def event_source() -> AsyncIterator[bytes]:
        try:
            yield b"retry: 5000\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    alert = await asyncio.wait_for(queue.get(), timeout=2.0)
                except asyncio.TimeoutError:
                    yield b": ping\n\n"
                    continue
                yield f"data: {json.dumps(alert, ensure_ascii=False)}\n\n".encode("utf-8")
        finally:
            alert_engine.unsubscribe(queue)

    return StreamingResponse(event_source(), media_type="text/event-stream")


@app.get("/api/devices/{device_id}/joints")
async def device_joints_sse(device_id: str):
    """SSE stream of real-time joint positions for a device."""

    async def event_stream():
        while True:
            data = runtime.get_joint_state(device_id)
            if data is not None:
                yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1.0 / 30)  # 30Hz max

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/metrics", dependencies=[])
async def metrics_endpoint():
    """Prometheus text exposition format."""
    return PlainTextResponse(content=prom_metrics.render(), media_type="text/plain; version=0.0.4")
