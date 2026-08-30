"""Optional API-key authentication and per-IP sliding window rate limiter.

Activate by setting API_AUTH_ENABLED=1 and API_API_KEYS=key1,key2 in the env.
Auth is bypassed on the safe-by-default prototype so contributors can run the
service locally without ceremony.
"""
from __future__ import annotations

import collections
import time
from typing import Iterable

from fastapi import HTTPException, Request, status

from backend.utils.config import settings


def _parse_keys() -> set[str]:
    raw = settings.api_keys.strip()
    if not raw:
        return set()
    return {item.strip() for item in raw.split(",") if item.strip()}


def require_api_key(request: Request) -> None:
    """FastAPI dependency that enforces the API key when enabled."""
    if not settings.api_auth_enabled:
        return
    expected = _parse_keys()
    if not expected:
        return  # misconfigured: auth enabled but no keys -> allow through
    provided = request.headers.get("x-api-key") or request.headers.get("authorization", "")
    if provided.lower().startswith("bearer "):
        provided = provided[7:]
    if provided not in expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid api key")


class SlidingWindowLimiter:
    """In-memory per-IP token bucket. Resets on restart."""

    def __init__(self, max_requests: int = 120, window_seconds: float = 60.0) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self._buckets: dict[str, collections.deque[float]] = {}

    def check(self, key: str) -> bool:
        now = time.monotonic()
        bucket = self._buckets.setdefault(key, collections.deque())
        cutoff = now - self.window
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= self.max_requests:
            return False
        bucket.append(now)
        return True

    def reset(self, key: str | None = None) -> None:
        if key is None:
            self._buckets.clear()
        else:
            self._buckets.pop(key, None)


limiter = SlidingWindowLimiter(
    max_requests=settings.rate_limit_max,
    window_seconds=settings.rate_limit_window_seconds,
)


def rate_limit_dep(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    if not limiter.check(client):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded")
