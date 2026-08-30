"""FastAPI dependencies for the system-administration module.

``get_current_user`` is the single entry point for authentication; every other
dependency in this module is a thin wrapper that adds an authorisation rule on
top of it.
"""
from __future__ import annotations
from collections.abc import AsyncIterator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rcs.db.session import session as db_session
from rcs.db.sys_models import SysUser
from rcs.services.sys.sys_security import decode_access_token

# ``auto_error=False`` so we can emit a 403 with a precise reason when the
# account exists but is disabled, instead of a blanket 401.
_bearer = HTTPBearer(auto_error=False)

WILDCARD_PERMISSION = "*:*"

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="无效的认证凭证",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield an ``AsyncSession`` bound to the running event loop."""
    async for s in db_session():
        yield s


def _extract_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> str | None:
    """Accept the token from the standard header or ``?token=`` for downloads."""
    if credentials is not None and credentials.credentials:
        return credentials.credentials
    return request.query_params.get("token")


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> SysUser:
    """Resolve the authenticated user, or raise 401/403."""
    token = _extract_token(request, credentials)
    if not token:
        raise CREDENTIALS_EXCEPTION

    user_id = decode_access_token(token)
    if user_id is None:
        raise CREDENTIALS_EXCEPTION

    user = await db.get(SysUser, user_id)
    if user is None or user.is_deleted:
        raise CREDENTIALS_EXCEPTION
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用",
        )
    return user


async def get_current_admin(
    current_user: SysUser = Depends(get_current_user),
) -> SysUser:
    """Require the ``is_admin`` flag (or the reserved ``super_admin`` role)."""
    if current_user.is_admin:
        return current_user
    role_codes = {ur.role.role_code for ur in current_user.user_roles if ur.role}
    if "super_admin" in role_codes:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="需要管理员权限",
    )


def require_permissions(*permissions: str):
    """Build a dependency demanding *all* of the given permission codes.

    Super-admins bypass the check entirely. Usage::

        @router.delete("/users/{user_id}", dependencies=[Depends(require_permissions("sys:user:delete"))])
    """
    required = list(permissions)

    async def _dependency(
        current_user: SysUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> SysUser:
        if current_user.is_admin:
            return current_user
        from rcs.services.sys.sys_service import has_permissions

        if not await has_permissions(current_user.user_id, required, db=db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有足够的权限访问此接口",
            )
        return current_user

    return _dependency


async def _optional_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> SysUser | None:
    """Like :func:`get_current_user` but returns ``None`` instead of raising."""
    token = _extract_token(request, credentials)
    if not token:
        return None
    user_id = decode_access_token(token)
    if user_id is None:
        return None
    user = await db.get(SysUser, user_id)
    if user is None or user.is_deleted or user.status != "active":
        return None
    return user


async def count_users(db: AsyncSession) -> int:
    """Number of non-deleted users (used by the dashboard widgets)."""
    result = await db.execute(
        select(SysUser).where(SysUser.is_deleted.is_(False))  # type: ignore[union-attr]
    )
    return len(result.scalars().all())
