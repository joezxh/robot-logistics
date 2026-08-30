"""Authentication, session and profile endpoints (``/api/sys/auth``).

All routes here go through :class:`~rcs.sysadmin.audit.AuditRoute`, so a
successful *and* a failed login is persisted to ``sys_audit_log`` with the
password field masked.
"""
from __future__ import annotations
import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from rcs.config import get_settings
from rcs.services.sys.sys_audit import enqueue
from rcs.services.sys.sys_deps import get_current_user, get_db
from rcs.db.sys_models import SysAuditLog, SysUser
from rcs.services.sys.sys_schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    UpdateProfileRequest,
    UserInfo,
)
from rcs.services.sys.sys_security import create_access_token, get_password_hash, verify_password
from rcs.services.sys.sys_service import authenticate, build_user_info, get_user_menu_tree

router = APIRouter(prefix="/auth", tags=["sys-auth"])


def _client_ip(request: Request) -> str:
    for header in ("x-forwarded-for", "x-real-ip"):
        value = request.headers.get(header)
        if value:
            return value.split(",")[0].strip()
    return request.client.host if request.client else ""


def _login_audit(
    request: Request,
    username: str,
    user_id: int | None,
    ok: bool,
) -> None:
    """Write an explicit login record (the generic route audit cannot know
    whether the credentials were accepted)."""
    enqueue(
        SysAuditLog(
            user_id=user_id,
            username=username,
            operation_type="login",
            operation_module="auth",
            operation_desc=f"用户登录{'成功' if ok else '失败'}: {username}",
            request_method="POST",
            request_url=str(request.url),
            request_ip=_client_ip(request),
            user_agent=request.headers.get("user-agent", "")[:500] or None,
            response_status=status.HTTP_200_OK if ok else status.HTTP_401_UNAUTHORIZED,
            response_time_ms=0,
        )
    )


@router.post("/login", response_model=LoginResponse, openapi_extra={"audit_type": "login"})
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Exchange a username/password pair for a JWT."""
    try:
        user = await authenticate(db, payload.username, payload.password)
    except ValueError as exc:
        _login_audit(request, payload.username, None, ok=False)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    settings = get_settings()
    token = create_access_token(user.user_id)

    now = dt.datetime.utcnow()
    user.last_login_at = now
    user.last_login_ip = _client_ip(request)
    await db.commit()

    _login_audit(request, user.username, user.user_id, ok=True)

    return LoginResponse(
        token=token,
        expiresIn=settings.access_token_expire_minutes * 60,
        userId=user.user_id,
        username=user.username,
        realName=user.real_name,
    )


@router.post("/logout", openapi_extra={"audit_type": "logout"})
async def logout(current_user: SysUser = Depends(get_current_user)) -> dict:
    """Client-side logout helper (JWTs are stateless; the record is audit-only)."""
    return {"code": 0, "message": "登出成功"}


@router.get("/me", response_model=UserInfo)
async def me(
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserInfo:
    """Profile + role codes + flattened permission list for the console."""
    return await build_user_info(db, current_user)


@router.put("/me/profile", response_model=UserInfo)
async def update_profile(
    payload: UpdateProfileRequest,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserInfo:
    """Update the editable fields of the caller's own profile."""
    data = payload.model_dump(exclude_none=True)
    for field, column in {
        "realName": "real_name",
        "phone": "phone",
        "email": "email",
        "avatar": "avatar_url",
    }.items():
        if field in data:
            setattr(current_user, column, data[field])
    current_user.updated_at = dt.datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    return await build_user_info(db, current_user)


@router.put("/me/password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Change the caller's own password (requires the current one)."""
    if not verify_password(payload.oldPassword, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码不正确")
    current_user.password_hash = get_password_hash(payload.newPassword)
    current_user.updated_at = dt.datetime.utcnow()
    await db.commit()
    return {"code": 0, "message": "密码修改成功"}


@router.get("/me/menus")
async def my_menus(
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Permission-filtered menu tree driving the console sidebar.

    Each node carries the full ``i18n`` map so the front-end can switch
    language without re-fetching.
    """
    tree = await get_user_menu_tree(db, current_user)
    return {"code": 0, "message": "success", "data": [n.model_dump() for n in tree]}
