"""Role management endpoints (``/api/sys/roles``).

A role bundles a set of menu/permission grants (``sys_role_menu``) that are
assigned to users through ``sys_user_role``.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rcs.services.sys.sys_deps import get_current_admin, get_db, require_permissions
from rcs.db.sys_models import SysRole, SysUserRole
from rcs.services.sys.sys_schemas import (
    Envelope,
    RoleCreate,
    RoleMenuAssign,
    RoleRow,
    RoleUpdate,
)
from rcs.services.sys.sys_service import (
    assign_role_menus,
    create_role,
    delete_role,
    get_user_role_ids,
    list_roles,
    update_role,
)

router = APIRouter(prefix="/roles", tags=["sys-roles"])

# Role codes that may not be deleted — removing them would lock everyone out.
PROTECTED_ROLE_CODES = {"super_admin"}


async def _get_role_or_404(db: AsyncSession, role_id: int) -> SysRole:
    role = await db.get(SysRole, role_id)
    if role is None or role.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    return role


@router.get("", response_model=Envelope[list[RoleRow]])
async def get_roles(
    keyword: str | None = Query(None, description="角色名称/编码模糊匹配"),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[list[RoleRow]]:
    """All roles with their granted menu ids (drives the tree checkboxes)."""
    rows = await list_roles(db, keyword=keyword)
    return Envelope(data=rows, total=len(rows))


@router.post(
    "",
    response_model=Envelope[RoleRow],
    dependencies=[Depends(require_permissions("sys:role:create"))],
)
async def post_role(
    payload: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[RoleRow]:
    """Create a role. ``role_code`` is unique and immutable in practice."""
    data = payload.model_dump()
    existing = (
        await db.execute(select(SysRole).where(SysRole.role_code == data["roleCode"]))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色编码已存在")

    role = await create_role(
        db,
        {
            "role_name": data["roleName"],
            "role_code": data["roleCode"],
            "description": data.get("description"),
            "region_code": data.get("regionCode"),
            "region_level": data.get("regionLevel"),
            "sort_order": data.get("sortOrder", 0),
            "status": data.get("status", "active"),
        },
    )
    rows = await list_roles(db, keyword=role.role_code)
    return Envelope(message="创建成功", data=next(r for r in rows if r.roleId == role.role_id))


@router.put(
    "/{role_id}",
    response_model=Envelope[RoleRow],
    dependencies=[Depends(require_permissions("sys:role:update"))],
)
async def put_role(
    role_id: int,
    payload: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[RoleRow]:
    """Update role metadata (does not touch menu grants)."""
    role = await _get_role_or_404(db, role_id)
    data = payload.model_dump(exclude_none=True)

    new_code = data.get("roleCode")
    if new_code and new_code != role.role_code:
        clash = (
            await db.execute(
                select(SysRole).where(SysRole.role_code == new_code, SysRole.role_id != role_id)
            )
        ).scalar_one_or_none()
        if clash is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色编码已存在")

    updated = await update_role(db, role, data)
    rows = await list_roles(db, keyword=updated.role_code)
    return Envelope(message="更新成功", data=next(r for r in rows if r.roleId == updated.role_id))


@router.delete(
    "/{role_id}",
    dependencies=[Depends(require_permissions("sys:role:delete"))],
)
async def remove_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[None]:
    """Soft-delete a role; built-ins and roles still in use are protected."""
    role = await _get_role_or_404(db, role_id)
    if role.role_code in PROTECTED_ROLE_CODES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="内置角色不可删除")

    in_use = (
        await db.execute(select(SysUserRole).where(SysUserRole.role_id == role_id))
    ).scalars().first()
    if in_use is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="角色下仍有用户，请先解除关联")

    await delete_role(db, role)
    return Envelope(message="删除成功")


@router.get("/{role_id}/menus", response_model=Envelope[list[int]])
async def get_role_menus(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[list[int]]:
    """Menu ids granted to the role."""
    role = await _get_role_or_404(db, role_id)
    rows = await list_roles(db, keyword=role.role_code)
    row = next(r for r in rows if r.roleId == role_id)
    return Envelope(data=row.menuIds)


@router.put(
    "/{role_id}/menus",
    dependencies=[Depends(require_permissions("sys:role:assign-menu"))],
)
async def put_role_menus(
    role_id: int,
    payload: RoleMenuAssign,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[None]:
    """Replace the role's menu grants (full set semantics)."""
    await _get_role_or_404(db, role_id)
    await assign_role_menus(db, role_id, payload.menuIds)
    return Envelope(message="菜单分配成功")


@router.get("/{role_id}/users", response_model=Envelope[list[int]])
async def get_role_users(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[list[int]]:
    """Ids of users holding this role (convenience for the console)."""
    await _get_role_or_404(db, role_id)
    from rcs.db.sys_models import SysUserRole

    rows = (
        await db.execute(select(SysUserRole.user_id).where(SysUserRole.role_id == role_id))
    ).all()
    return Envelope(data=[r[0] for r in rows])


@router.get("/user/{user_id}", response_model=Envelope[list[int]])
async def get_roles_of_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[list[int]]:
    """Mirror of ``GET /users/{id}/roles`` kept for the role-picker widget."""
    return Envelope(data=await get_user_role_ids(db, user_id))
