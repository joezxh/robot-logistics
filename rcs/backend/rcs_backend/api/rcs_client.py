"""Async HTTP client to rcs/rcs subproject (service.py endpoints).

Endpoints used (from rcs/rcs/service.py):
- GET  /registry
- POST /{device_id}/command
- GET  /{device_id}/state
- POST /estop
- POST /{device_id}/estop
"""
from __future__ import annotations
import httpx
from rcs_backend.config import get_settings


class RcsClient:
    def __init__(self, base_url: str | None = None, timeout_s: float | None = None) -> None:
        s = get_settings()
        self.base_url = base_url or s.service_url
        self._timeout_s = timeout_s if timeout_s is not None else s.service_timeout_s
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self._timeout_s)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_registry(self) -> dict:
        r = await self._client.get("/registry")
        r.raise_for_status()
        return r.json()

    async def send_command(self, device_id: str, cmd: dict) -> dict:
        r = await self._client.post(f"/{device_id}/command", json=cmd)
        r.raise_for_status()
        return r.json()

    async def get_state(self, device_id: str) -> dict:
        r = await self._client.get(f"/{device_id}/state")
        r.raise_for_status()
        return r.json()

    async def estop(self, device_id: str | None = None) -> dict:
        url = "/estop" if device_id is None else f"/{device_id}/estop"
        r = await self._client.post(url)
        r.raise_for_status()
        return r.json()
