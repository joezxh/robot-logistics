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
from rcs.api.warehouse_import_api import router as warehouse_router
from rcs.control import lifespan as control_lifespan
from rcs.control import router as control_router
from rcs.api.control.control_devices import router as devices_router
from rcs.api.control.control_maps import router as maps_router
from rcs.api.control.control_planning import router as planning_router
from rcs.api.control.control_scheduler import router as scheduler_router
from rcs.api.control.control_logs import router as logs_router
from rcs.services.control.control_devices import seed_defaults_if_empty as dev_seed_defaults
from rcs.db import init_db
from rcs.api.sys.sys_routers import router as sys_router
from rcs.services.sys.sys_lifespan import auth_middleware, seed_if_empty, shutdown as sys_shutdown, start as sys_start


@asynccontextmanager
async def _lifespan(app: FastAPI):
    # Initialise DB (creates tables) and seed default device profiles the first
    # time the deployment boots. Then enter the embedded control loop.
    await init_db()
    await dev_seed_defaults()
    # System management bootstrap (menus / roles / default accounts / dicts).
    # Skipped automatically once the tables are populated; failures are logged
    # and never abort startup.
    settings = get_settings()
    if settings.sys_seed_on_startup:
        await seed_if_empty()
    await sys_start()
    try:
        async with control_lifespan():
            yield {"settings": settings}
    finally:
        await sys_shutdown()


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
    # Warehouse Theatre 3D integration
    app.include_router(warehouse_router, prefix="/api/rcs", tags=["warehouse"])
    # Phase C1: persistent device registry (CRUD under /api/rcs/devices).
    app.include_router(devices_router, prefix="/api/rcs", tags=["devices"])
    # Phase C2-C6: site maps, planning profiles, scheduler configs, logs.
    app.include_router(maps_router, prefix="/api/rcs", tags=["maps"])
    app.include_router(planning_router, prefix="/api/rcs", tags=["planning"])
    app.include_router(scheduler_router, prefix="/api/rcs", tags=["scheduler"])
    app.include_router(logs_router, prefix="/api/rcs", tags=["logs"])
    # Embedded control runtime (registry / command / state / estop / WS).
    app.include_router(control_router(), prefix="/api/rcs", tags=["control"])
    # System administration (users / roles / menus / audit / dictionaries).
    # Mounted last and prefix-isolated so the legacy surface keeps its paths.
    app.include_router(sys_router, prefix="/api/sys", tags=["system"])
    # Opt-in JWT gate for /api/rcs/** (see Settings.auth_enabled).
    app.middleware("http")(auth_middleware)
    return app


app = create_app()


if __name__ == "__main__":
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="Run the RCS Backend server.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8100)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    # Pass the app object directly (not the "module:app" string) so uvicorn does
    # not need to re-import via a subprocess — this avoids a FileNotFoundError
    # under PyCharm's pydevd debugger and keeps breakpoints working.
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
