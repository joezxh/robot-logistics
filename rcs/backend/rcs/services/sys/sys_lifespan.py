"""System-administration lifecycle hooks and the opt-in auth gate.

Mounted at ``/api/sys`` by :func:`rcs.main.create_app`. The public surface is:

* :func:`start` / :func:`shutdown` — lifespan hooks for the audit writer.
* :func:`seed_if_empty` — idempotent bootstrap of menus/roles/users/dictionaries.
* :func:`auth_middleware` — opt-in JWT gate for the legacy ``/api/rcs/**``
  surface (active only when ``RCS_AUTH_ENABLED=true``).
"""
from __future__ import annotations

from rcs.services.sys.sys_audit import start_audit_writer, stop_audit_writer
from rcs.services.sys.sys_seed import seed_if_empty

__all__ = [
    "start",
    "shutdown",
    "seed_if_empty",
    "auth_middleware",
]


async def start() -> None:
    """Start the audit batch writer; no-op when auditing is disabled."""
    start_audit_writer()


async def shutdown() -> None:
    """Flush pending audit entries and stop the writer."""
    await stop_audit_writer()


# ---------------------------------------------------------------------------
# Optional gate for the legacy business API
# ---------------------------------------------------------------------------

# Paths that stay anonymous even with RCS_AUTH_ENABLED=true.
_PUBLIC_PREFIXES = (
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/sys/auth/login",
)


async def auth_middleware(request, call_next):  # type: ignore[no-untyped-def]
    """Reject unauthenticated ``/api/rcs/**`` calls when ``auth_enabled`` is on.

    ``/api/sys/**`` is intentionally *not* handled here: those routers declare
    their own dependencies and always require a token.
    """
    from fastapi import status
    from fastapi.responses import JSONResponse

    from rcs.config import get_settings
    from rcs.services.sys.sys_security import decode_access_token

    settings = get_settings()
    path = request.url.path

    if (
        not settings.auth_enabled
        or not path.startswith("/api/rcs")
        or path.startswith(_PUBLIC_PREFIXES)
        or request.method == "OPTIONS"
    ):
        return await call_next(request)

    # The shared API key (used by machine-to-machine callers) keeps working.
    header_key = request.headers.get("x-api-key") or request.query_params.get("api_key")
    if settings.api_key and header_key and header_key == settings.api_key:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        if decode_access_token(auth_header.split(" ", 1)[1].strip()) is not None:
            return await call_next(request)

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "请先登录或提供有效的 API Key"},
        headers={"WWW-Authenticate": "Bearer"},
    )
