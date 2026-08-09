"""Standalone RCS service entrypoint.

RCS runs in two modes and both share the exact same router and control loop, so
there is no behavioural drift between them:

* **Embedded** — the simulation backend mounts ``rcs.router()`` and chains
  ``rcs.lifespan()``. This is the historical behaviour.
* **Standalone** — this module's :func:`create_app` builds an independent
  FastAPI application, mounts the same router under ``/api/rcs`` and drives its
  own lifespan.

Run standalone with::

    uvicorn rcs.app:create_app --factory --host 127.0.0.1 --port 8100
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import lifespan as rcs_lifespan, router as rcs_router_factory
from .config import settings


def _cors_origins() -> list[str]:
    raw = settings.cors_origins.strip()
    if not raw or raw == "*":
        return ["*"]
    return [item.strip() for item in raw.split(",") if item.strip()]


@asynccontextmanager
async def _lifespan(app: FastAPI):
    # Chain the RCS control-loop lifespan, then the optional MQTT adapter.
    async with rcs_lifespan():
        adapter = None
        if settings.mqtt_enabled:
            from .mqtt import MqttAdapter

            adapter = MqttAdapter()
            await adapter.start()
        try:
            yield
        finally:
            if adapter is not None:
                await adapter.stop()


def create_app() -> FastAPI:
    """Build the standalone RCS FastAPI application."""
    app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=_lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(rcs_router_factory(), prefix="/api/rcs")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "rcs", "mode": "standalone"}

    return app


app = create_app()
