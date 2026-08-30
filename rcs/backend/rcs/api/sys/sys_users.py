"""User management endpoints (``/api/sys/users``).

Administrator-only. Every mutating endpoint is gated by a permission code so
the console can hide/disable the corresponding buttons per role.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rcs.services.sys.sys_deps import get_current_admin, get_db, require_permissions
from rcs.db.sys_models import SysUser
from rcs.services.sys.sys_schemas import (
    Envelope,
    PasswordResetRequest,
    RoleAssignRequest,
    UserCreate,
    UserRow,
    UserStatusUpdate,
    UserUpdate,
)
from rcs.services.sys.sys_security import get_password_hash
from rcs.services.sys.sys_service import (
    _user_to_row,
    assign_user_roles,
    create_user,
    delete_user,
    get_user_role_ids,
    list_users,
    update_user,
)

router = APIRouter(prefix="/users", tags=["sys-users"])


async def _get_user_or_404(db: AsyncSession, user_id: int) -> SysUser:
    user = await db.get(SysUser, user_id)
    if user is None or user.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user


@router.get("", response_model=Envelope[list[UserRow]])
async def get_users(
    keyword: str | None = Query(None, description="账号/姓名/手机/邮箱模糊匹配"),
    status_filter: str | None = Query(None, alias="status", description="active / disabled"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[list[UserRow]]:
    """Paginated user list with resolved role names."""
    rows, total = await list_users(db, keyword=keyword, status=status_filter, skip=skip, limit=limit)
    return Envelope(data=rows, total=total)


@router.get("/{user_id}", response_model=Envelope[UserRow])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[UserRow]:
    """Single user, including its role ids."""
    user = await _get_user_or_404(db, user_id)
    return Envelope(data=_user_to_row(user))


@router.post(
    "",
    response_model=Envelope[UserRow],
    dependencies=[Depends(require_permissions("sys:user:create"))],
)
async def post_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[UserRow]:
    """Create a user (optionally granting roles in the same call)."""
    existing = (
        await db.execute(
            select(SysUser).where(SysUser.username == payload.username)
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    body = payload.model_dump()
    body["roleIds"] = payload.roleIds
    user = await create_user(db, body, get_password_hash(payload.password))
    return Envelope(message="创建成功", data=_user_to_row(user))


@router.put(
    "/{user_id}",
    response_model=Envelope[UserRow],
    dependencies=[Depends(require_permissions("sys:user:update"))],
)
async def put_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
) -> Envelope[UserRow]:
    """Update profile fields / status / admin flag."""
    user = await _get_user_or_404(db, user_id)
    data = payload.model_dump(exclude_none=True)

    # Guard rail: never let the last active administrator demote themselves.
    if "isAdmin" in data and not data["isAdmin"] and user.user_id == current_admin.user_id:
        others = (
            await db.execute(
                select(SysUser).where(
                    SysUser.is_admin.is_(True),
                    SysUser.is_deleted.is_(False),
                    SysUser.user_id != user.user_id,
                )
            )
        ).scalars().all()
        if not others:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="系统至少需要保留一名管理员",
            )

    updated = await update_user(db, user, data)
    return Envelope(message="更新成功", data=_user_to_row(updated))


@router.delete(
    "/{user_id}",
    dependencies=[Depends(require_permissions("sys:user:delete"))],
)
async def remove_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
) -> Envelope[None]:
    """Soft-delete a user (self-deletion is rejected)."""
    if user_id == current_admin.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除当前登录用户")
    user = await _get_user_or_404(db, user_id)
    await delete_user(db, user)
    return Envelope(message="删除成功")


@router.put(
    "/{user_id}/status",
    dependencies=[Depends(require_permissions("sys:user:update"))],
)
async def put_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
) -> Envelope[None]:
    """Enable/disable an account (``active`` / ``disabled``)."""
    if user_id == current_admin.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能禁用当前登录用户")
    user = await _get_user_or_404(db, user_id)
    await update_user(db, user, {"status": payload.status})
    return Envelope(message="更新成功")


@router.post(
    "/{user_id}/reset-password",
    dependencies=[Depends(require_permissions("sys:user:reset-password"))],
)
async def post_reset_password(
    user_id: int,
    payload: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[None]:
    """Administrator-driven password reset (old password not required)."""
    user = await _get_user_or_404(db, user_id)
    user.password_hash = get_password_hash(payload.newPassword)
    await db.commit()
    return Envelope(message="重置成功")


@router.get("/{user_id}/roles", response_model=Envelope[list[int]])
async def get_user_roles(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[list[int]]:
    """Role ids currently assigned to the user."""
    await _get_user_or_404(db, user_id)
    return Envelope(data=await get_user_role_ids(db, user_id))


@router.put(
    "/{user_id}/roles",
    dependencies=[Depends(require_permissions("sys:user:assign-role"))],
)
async def put_user_roles(
    user_id: int,
    payload: RoleAssignRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[None]:
    """Replace the user's role set atomically."""
    await _get_user_or_404(db, user_id)
    await assign_user_roles(db, user_id, payload.roleIds)
    return Envelope(message="分配成功")
