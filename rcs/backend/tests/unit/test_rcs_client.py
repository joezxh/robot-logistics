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
        client._client = httpx.AsyncClient(transport=mock_transport, base_url=client.base_url)  # type: ignore
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
        client._client = httpx.AsyncClient(transport=mock_transport, base_url=client.base_url)  # type: ignore
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
        client._client = httpx.AsyncClient(transport=mock_transport, base_url=client.base_url)  # type: ignore
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
        client._client = httpx.AsyncClient(transport=mock_transport, base_url=client.base_url)  # type: ignore
        out = await client.estop()
        assert out["estopped"] is True
        sent_request = mock_transport.handle_async_request.call_args[0][0]
        assert sent_request.url.path == "/estop"
        assert sent_request.method == "POST"
        await client.aclose()
    asyncio.run(run())
