## Task 10: HTTP 客户端 → rcs/rcs 子项目

**Files:**
- Create: `rcs/backend/rcs_backend/api/rcs_client.py`
- Create: `rcs/backend/tests/unit/test_rcs_client.py`

**Interfaces:**
- Produces:
  - `class RcsClient`: async methods to call `rcs/rcs/service.py` REST endpoints
  - `async def get_registry()`, `async def send_command(device_id, cmd)`, `async def get_state(device_id)`, `async def estop(device_id=None)`
  - Default base URL + timeout from `Settings` (`service_url`, `service_timeout_s`)

> **Plan note**: brief has no Step 0. Task 10 doesn't modify `api/__init__.py` (only Task 11 does). Confirmed dependencies:
> - `httpx 0.28.1` installed
> - `Settings.service_url = "http://127.0.0.1:8101"`, `service_timeout_s: float = 5.0`

- [ ] **Step 1: 写失败的测试 `test_rcs_client.py`**

```python
"""HTTP client to rcs/rcs subproject REST endpoints."""
import asyncio
from unittest.mock import AsyncMock
import httpx
from rcs_backend.api.rcs_client import RcsClient


def _mock_response(json_data: dict, status_code: int = 200) -> httpx.Response:
    req = httpx.Request("GET", "http://test")
    return httpx.Response(status_code, json=json_data, request=req)


def test_get_registry_calls_correct_endpoint():
    async def run():
        client = RcsClient(base_url="http://rcs:8101")
        mock_transport = AsyncMock()
        mock_transport.handle_async_request.return_value = _mock_response(
            {"devices": [{"id": "agv-01", "type": "diff_drive"}]}
        )
        client._client = httpx.AsyncClient(transport=mock_transport)  # type: ignore
        out = await client.get_registry()
        assert "devices" in out
        assert out["devices"][0]["id"] == "agv-01"
        # Verify correct URL path was requested
        sent_request = mock_transport.handle_async_request.call_args[0][0]
        assert sent_request.url.path == "/registry"
        await client.aclose()
    asyncio.run(run())


def test_send_command_posts_to_device_id():
    async def run():
        client = RcsClient(base_url="http://rcs:8101")
        mock_transport = AsyncMock()
        mock_transport.handle_async_request.return_value = _mock_response({"ack": True})
        client._client = httpx.AsyncClient(transport=mock_transport)  # type: ignore
        out = await client.send_command("agv-01", {"type": "MOVE_TO", "y": 5.0})
        assert out["ack"] is True
        sent_request = mock_transport.handle_async_request.call_args[0][0]
        assert sent_request.url.path == "/agv-01/command"
        assert sent_request.method == "POST"
        await client.aclose()
    asyncio.run(run())


def test_get_state_calls_device_state_endpoint():
    async def run():
        client = RcsClient(base_url="http://rcs:8101")
        mock_transport = AsyncMock()
        mock_transport.handle_async_request.return_value = _mock_response(
            {"id": "agv-01", "x": 1.0, "y": 2.0}
        )
        client._client = httpx.AsyncClient(transport=mock_transport)  # type: ignore
        out = await client.get_state("agv-01")
        assert out["id"] == "agv-01"
        sent_request = mock_transport.handle_async_request.call_args[0][0]
        assert sent_request.url.path == "/agv-01/state"
        assert sent_request.method == "GET"
        await client.aclose()
    asyncio.run(run())


def test_client_default_url():
    c = RcsClient()
    assert c.base_url  # has default


def test_client_passes_timeout():
    c = RcsClient(base_url="http://x", timeout_s=7.5)
    assert c._timeout_s == 7.5


def test_estop_all_devices():
    async def run():
        client = RcsClient(base_url="http://rcs:8101")
        mock_transport = AsyncMock()
        mock_transport.handle_async_request.return_value = _mock_response({"estopped": True})
        client._client = httpx.AsyncClient(transport=mock_transport)  # type: ignore
        out = await client.estop()
        assert out["estopped"] is True
        sent_request = mock_transport.handle_async_request.call_args[0][0]
        assert sent_request.url.path == "/estop"
        assert sent_request.method == "POST"
        await client.aclose()
    asyncio.run(run())
```

> **Plan patch notes** (3 changes):
> 1. Removed unused `from unittest.mock import AsyncMock, patch` (patch not needed).
> 2. Added URL-path assertions to existing tests so wrong-endpoint regressions are caught (brief only verified response shape).
> 3. Added `test_get_state_calls_device_state_endpoint` (brief has `get_state` interface but no test) and `test_estop_all_devices` (brief has `estop` method but no test). Total 6 tests instead of 4.

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && python -m pytest tests/unit/test_rcs_client.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/api/rcs_client.py`**

```python
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd rcs/backend && python -m pytest tests/unit/test_rcs_client.py -v`
Expected: PASS（6 tests）

- [ ] **Step 5: 跑全 suite 确认无回归**

Run: `cd rcs/backend && python -m pytest -v`
Expected: 45 (prior) + 6 (new) = 51 passed

- [ ] **Step 6: Commit**

```bash
git add rcs/backend/rcs_backend/api/rcs_client.py rcs/backend/tests/unit/test_rcs_client.py
git commit -m "feat(rcs-backend): async HTTP client to rcs/rcs subproject REST endpoints"
```