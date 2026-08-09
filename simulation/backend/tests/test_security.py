"""Tests for the API-key auth dependency and sliding-window rate limiter."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from backend.services import security


@pytest.fixture
def auth_enabled(monkeypatch):
    monkeypatch.setattr(security.settings, "api_auth_enabled", True)
    monkeypatch.setattr(security.settings, "api_keys", "k1,k2")
    yield
    monkeypatch.setattr(security.settings, "api_auth_enabled", False)
    monkeypatch.setattr(security.settings, "api_keys", "")


def make_request(api_key: str | None):
    from fastapi import Request

    class _H:
        def get(self, key: str, default: str = "") -> str:
            auth_value = api_key if (api_key and not api_key.startswith("Bearer ")) else (api_key or "")
            mapping = {
                "x-api-key": api_key if (api_key and not api_key.startswith("Bearer ")) else "",
                "authorization": auth_value,
            }
            return mapping.get(key.lower(), default)

    scope = {"type": "http", "headers": []}
    req = Request(scope)
    req._headers = _H()  # type: ignore[attr-defined]
    return req


def test_auth_disabled_by_default() -> None:
    # Already disabled in conftest.
    security.settings.api_auth_enabled = False
    security.require_api_key(make_request(None))  # should be a no-op


def test_auth_accepts_header_and_bearer(monkeypatch) -> None:
    monkeypatch.setattr(security.settings, "api_auth_enabled", True)
    monkeypatch.setattr(security.settings, "api_keys", "k1")
    security.require_api_key(make_request("k1"))
    security.require_api_key(make_request("Bearer k1"))


def test_auth_rejects_unknown_key(monkeypatch) -> None:
    from fastapi import HTTPException

    monkeypatch.setattr(security.settings, "api_auth_enabled", True)
    monkeypatch.setattr(security.settings, "api_keys", "k1")
    with pytest.raises(HTTPException) as exc:
        security.require_api_key(make_request("nope"))
    assert exc.value.status_code == 401


def test_rate_limiter_caps_requests() -> None:
    limiter = security.SlidingWindowLimiter(max_requests=3, window_seconds=60)
    assert limiter.check("ip1")
    assert limiter.check("ip1")
    assert limiter.check("ip1")
    assert not limiter.check("ip1")


def test_rate_limiter_isolates_ips() -> None:
    limiter = security.SlidingWindowLimiter(max_requests=2, window_seconds=60)
    assert limiter.check("ip1")
    assert limiter.check("ip1")
    assert limiter.check("ip2")
    assert not limiter.check("ip1")
