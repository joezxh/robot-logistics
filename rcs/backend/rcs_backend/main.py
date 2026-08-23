"""FastAPI application factory."""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from rcs_backend.config import get_settings
from rcs_backend.api import (
    topology_shell,
    topology_grid,
    topology_import,
    topology_export,
    topology_templates,
    orders,
)


@asynccontextmanager
async def _lifespan(app: FastAPI):
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

    app.include_router(topology_shell.router, prefix="/api/rcs/topology", tags=["shell"])
    app.include_router(topology_grid.router, prefix="/api/rcs/topology", tags=["grid"])
    app.include_router(topology_import.router, prefix="/api/rcs/topology", tags=["import"])
    app.include_router(topology_export.router, prefix="/api/rcs/topology", tags=["export"])
    app.include_router(topology_templates.router, prefix="/api/rcs/topology", tags=["templates"])
    app.include_router(orders.router, prefix="/api/rcs", tags=["orders"])
    return app


app = create_app()
