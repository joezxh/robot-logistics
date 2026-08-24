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
from rcs.db import init_db


@asynccontextmanager
async def _lifespan(app: FastAPI):
    # Initialise DB (creates tables when storage is postgres/sqlite) and start
    # the embedded control loop inside the control lifespan's context.
    await init_db()
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
    # Embedded control runtime (registry / command / state / estop / WS).
    app.include_router(control_router(), prefix="/api/rcs", tags=["control"])
    return app


app = create_app()
