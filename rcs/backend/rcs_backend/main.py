"""FastAPI application factory."""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from rcs_backend.config import get_settings
from rcs_backend.api import (
    topology_shell, topology_grid, topology_import,
    topology_export, topology_templates, orders,
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

    # Each `topology_*` / `orders` is an APIRouter instance (stub in Task 1,
    # replaced by real routers via re-export in Tasks 11-16). Pass the router
    # itself to include_router, not `.router`.
    app.include_router(topology_shell, prefix="/api/rcs/topology", tags=["shell"])
    app.include_router(topology_grid, prefix="/api/rcs/topology", tags=["grid"])
    app.include_router(topology_import, prefix="/api/rcs/topology", tags=["import"])
    app.include_router(topology_export, prefix="/api/rcs/topology", tags=["export"])
    app.include_router(topology_templates, prefix="/api/rcs/topology", tags=["templates"])
    app.include_router(orders, prefix="/api/rcs", tags=["orders"])
    return app


app = create_app()
