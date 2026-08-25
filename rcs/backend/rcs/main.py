"""FastAPI application factory for RCS Backend.

Single-process deployment: the robot control runtime (``rcs.control``)
is embedded directly — no HTTP hop between the API and the control loop. The
control package exposes ``lifespan()`` (loads registry + starts the control
loop) and ``router()`` (registry/command/state/estop/WS endpoints), which we
mount alongside the topology + orders routers.
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from rcs.config import get_settings
from rcs.api import (
    topology_shell, topology_grid, topology_import,
    topology_export, topology_templates, orders,
)
from rcs.control import lifespan as control_lifespan
from rcs.control import router as control_router
from rcs.control.devices import service as dev_svc
from rcs.control.devices.api import router as devices_router
from rcs.control.topology.api import router as maps_router
from rcs.control.planning.api import router as planning_router
from rcs.control.scheduler.api import router as scheduler_router
from rcs.control.logs.api import router as logs_router
from rcs.db import init_db


@asynccontextmanager
async def _lifespan(app: FastAPI):
    # Initialise DB (creates tables) and seed default device profiles the first
    # time the deployment boots. Then enter the embedded control loop.
    await init_db()
    await dev_svc.seed_defaults_if_empty()
    async with control_lifespan():
        settings = get_settings()
        yield {"settings": settings}


def create_app() -> FastAPI:
    app = FastAPI(
        title="RCS Backend v2.2",
        version="0.1.0",
        lifespan=_lifespan,
    )

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "version": "0.1.0"}

    app.include_router(topology_shell, prefix="/api/rcs/topology", tags=["shell"])
    app.include_router(topology_grid, prefix="/api/rcs/topology", tags=["grid"])
    app.include_router(topology_import, prefix="/api/rcs/topology", tags=["import"])
    app.include_router(topology_export, prefix="/api/rcs/topology", tags=["export"])
    app.include_router(topology_templates, prefix="/api/rcs/topology", tags=["templates"])
    app.include_router(orders, prefix="/api/rcs", tags=["orders"])
    # Phase C1: persistent device registry (CRUD under /api/rcs/devices).
    app.include_router(devices_router, prefix="/api/rcs", tags=["devices"])
    # Phase C2-C6: site maps, planning profiles, scheduler configs, logs.
    app.include_router(maps_router, prefix="/api/rcs", tags=["maps"])
    app.include_router(planning_router, prefix="/api/rcs", tags=["planning"])
    app.include_router(scheduler_router, prefix="/api/rcs", tags=["scheduler"])
    app.include_router(logs_router, prefix="/api/rcs", tags=["logs"])
    # Embedded control runtime (registry / command / state / estop / WS).
    app.include_router(control_router(), prefix="/api/rcs", tags=["control"])
    return app


app = create_app()
