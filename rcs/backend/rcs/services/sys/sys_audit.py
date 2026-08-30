"""Audit logging for the system-administration module.

Two cooperating pieces:

* :class:`AuditRoute` — an ``APIRoute`` subclass applied to routers via
  ``route_class=``. It times each request, redacts sensitive body fields and
  pushes a :class:`SysAuditLog` onto an in-memory queue. Permission strings
  declared on a route through ``openapi_extra={"permissions": [...]}`` are
  enforced here as well, so authorisation stays declarative.
* :func:`start_audit_writer` / :func:`stop_audit_writer` — a background
  asyncio task that drains the queue in batches. Writes never sit on the
  request's critical path; if the queue is full the entry is dropped with a
  warning rather than blocking the caller.
"""
from __future__ import annotations
import asyncio
import json
import logging
import time
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, Response, status
from fastapi.routing import APIRoute

from rcs.config import get_settings
from rcs.db.sys_models import SysAuditLog
from rcs.services.sys.sys_security import decode_access_token

logger = logging.getLogger(__name__)

# Bounded so a database outage cannot grow the queue without limit.
_MAX_QUEUE = 5000
_queue: asyncio.Queue[SysAuditLog] = asyncio.Queue(maxsize=_MAX_QUEUE)
_writer_task: asyncio.Task | None = None
_writer_running = False


# ---------------------------------------------------------------------------
# Background batch writer
# ---------------------------------------------------------------------------

async def _drain(batch_size: int, flush_interval: float) -> None:
    """Consume the queue until :data:`_writer_running` is cleared."""
    from rcs.db.session import get_sessionmaker

    maker = get_sessionmaker()
    while _writer_running or not _queue.empty():
        batch: list[SysAuditLog] = []
        try:
            try:
                batch.append(await asyncio.wait_for(_queue.get(), timeout=flush_interval))
            except asyncio.TimeoutError:
                pass
            while len(batch) < batch_size:
                try:
                    batch.append(_queue.get_nowait())
                except asyncio.QueueEmpty:
                    break
            if batch:
                async with maker() as session:
                    session.add_all(batch)
                    await session.commit()
        except asyncio.CancelledError:  # pragma: no cover - shutdown path
            raise
        except Exception as exc:  # noqa: BLE001 - never kill the writer loop
            logger.warning("审计日志批量写入失败，丢弃 %d 条: %s", len(batch), exc)


def start_audit_writer() -> asyncio.Task | None:
    """Start the batch writer; call once from the application lifespan."""
    global _writer_task, _writer_running
    settings = get_settings()
    if not settings.audit_log_enabled:
        return None
    _writer_running = True
    _writer_task = asyncio.create_task(
        _drain(settings.audit_log_batch_size, settings.audit_log_flush_interval)
    )
    return _writer_task


async def stop_audit_writer() -> None:
    """Flush pending entries and stop the writer task."""
    global _writer_task, _writer_running
    _writer_running = False
    if _writer_task is None:
        return
    try:
        await asyncio.wait_for(_writer_task, timeout=10.0)
    except asyncio.TimeoutError:  # pragma: no cover - shutdown path
        _writer_task.cancel()
    _writer_task = None


def enqueue(entry: SysAuditLog) -> None:
    """Push an entry onto the queue, dropping it when the queue is saturated."""
    try:
        _queue.put_nowait(entry)
    except asyncio.QueueFull:
        logger.warning("审计日志队列已满（%d），丢弃一条记录", _MAX_QUEUE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_csv(raw: str, fallback: list[str]) -> set[str]:
    values = {v.strip() for v in (raw or "").split(",") if v.strip()}
    return values or set(fallback)


def _derive_module(path: str) -> str:
    """Best-effort module label derived from the URL path.

    ``/api/sys/users/12`` -> ``users``; falls back to ``system``.
    """
    parts = [p for p in path.strip("/").split("/") if p]
    # Skip the leading ``api`` and version/prefix segments.
    for part in parts:
        if part in {"api", "v1", "rcs", "sys"}:
            continue
        return part
    return "system"


def determine_operation_type(method: str, path: str, override: str | None = None) -> str:
    """Map an HTTP method + path onto the ``operation_type`` enum of sys.sql."""
    if override:
        return override
    method = method.upper()
    if method == "POST":
        lowered = path.lower()
        if "login" in lowered:
            return "login"
        if "logout" in lowered:
            return "logout"
        return "create"
    if method in {"PUT", "PATCH"}:
        return "update"
    if method == "DELETE":
        return "delete"
    return "query"


def mask_body(body: Any, mask_fields: set[str]) -> Any:
    """Replace sensitive keys with a fixed mask (non-recursive on purpose)."""
    if not isinstance(body, dict):
        return body
    masked = dict(body)
    for key in mask_fields:
        if key in masked:
            masked[key] = "********"
    return masked


def _client_ip(request: Request) -> str:
    """Honour the de-facto proxy headers before falling back to the peer."""
    for header in ("x-forwarded-for", "x-real-ip"):
        value = request.headers.get(header)
        if value:
            return value.split(",")[0].strip()
    return request.client.host if request.client else ""


# ---------------------------------------------------------------------------
# Route class
# ---------------------------------------------------------------------------

class AuditRoute(APIRoute):
    """Route that enforces declared permissions and emits audit records."""

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        extra = self.openapi_extra or {}
        required_permissions: list[str] = list(extra.get("permissions", []))
        audit_type_override: str | None = extra.get("audit_type")
        route_mask_fields = set(extra.get("audit_mask_fields", []))

        async def custom_route_handler(request: Request) -> Response:
            settings = get_settings()
            skip_methods = _split_csv(settings.audit_log_skip_methods, ["OPTIONS"])
            skip_paths = tuple(
                _split_csv(settings.audit_log_skip_paths, ["/health", "/docs", "/openapi.json"])
            )
            mask_fields = _split_csv(
                settings.audit_log_mask_fields,
                ["password", "oldPassword", "newPassword", "password_hash"],
            ) | route_mask_fields

            # --- Resolve the caller from the Authorization header ---------
            user_id: int | None = None
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                user_id = decode_access_token(auth_header.split(" ", 1)[1].strip())

            # --- Authorisation --------------------------------------------
            if required_permissions:
                if user_id is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="请提供有效的 JWT Token 进行鉴权",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                from rcs.services.sys.sys_service import has_permissions

                if not await has_permissions(user_id, required_permissions):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="没有足够的权限访问此接口",
                    )

            # --- Fast path: auditing disabled or excluded ------------------
            if not settings.audit_log_enabled:
                return await original_route_handler(request)
            method = request.method.upper()
            if method in skip_methods or request.url.path.startswith(skip_paths):
                return await original_route_handler(request)

            # --- Capture the request body (best effort, never fatal) ------
            body: Any = None
            if method in {"POST", "PUT", "PATCH"}:
                content_type = request.headers.get("content-type", "")
                try:
                    raw = await request.body()
                except Exception:  # noqa: BLE001 - body already consumed / stream error
                    raw = b""
                if "application/json" in content_type and raw:
                    try:
                        body = json.loads(raw.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        body = None
                elif "multipart/form-data" in content_type:
                    # Never persist file contents — only the declared filename.
                    head = raw[:1024].decode("utf-8", errors="ignore")
                    import re

                    match = re.search(r'filename="([^"]+)"', head)
                    body = {
                        "_upload": True,
                        "content_length": len(raw),
                        "filename": match.group(1) if match else None,
                    }

            start = time.perf_counter()
            status_code = 500
            try:
                response = await original_route_handler(request)
                status_code = response.status_code
            except HTTPException as exc:
                status_code = exc.status_code
                raise
            except Exception:
                status_code = 500
                raise
            finally:
                elapsed_ms = int((time.perf_counter() - start) * 1000)
                enqueue(
                    SysAuditLog(
                        user_id=user_id,
                        operation_type=determine_operation_type(
                            method, request.url.path, audit_type_override
                        ),
                        operation_module=_derive_module(request.url.path),
                        operation_desc=f"{method} {request.url.path}",
                        request_method=method,
                        request_url=str(request.url),
                        request_params=mask_body(body, mask_fields),
                        request_ip=_client_ip(request),
                        user_agent=request.headers.get("user-agent", "")[:500] or None,
                        response_status=status_code,
                        response_time_ms=elapsed_ms,
                    )
                )
            return response

        return custom_route_handler
