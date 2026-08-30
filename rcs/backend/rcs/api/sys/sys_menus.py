"""Menu / permission endpoints (``/api/sys/menus``).

``sys_menu`` stores directories (type 1), pages (type 2) and button-level
permissions (type 3) in one table. The ``i18n`` JSONB column holds per-locale
titles::

    {"zh-CN": "设备管理", "zh-TW": "設備管理", "en-US": "Devices", "ja-JP": "デバイス管理"}

``name`` remains the fallback rendered when a locale key is absent, so a menu
added without translations still shows something sensible.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rcs.services.sys.sys_deps import get_current_admin, get_db, require_permissions
from rcs.db.sys_models import SysMenu
from rcs.services.sys.sys_schemas import Envelope, MenuCreate, MenuNode, MenuSimple, MenuUpdate
from rcs.services.sys.sys_service import (
    create_menu,
    delete_menu,
    get_menu_flat,
    get_menu_simple,
    get_menu_tree,
    update_menu,
)

router = APIRouter(prefix="/menus", tags=["sys-menus"])


async def _get_menu_or_404(db: AsyncSession, menu_id: int) -> SysMenu:
    menu = await db.get(SysMenu, menu_id)
    if menu is None or menu.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="菜单不存在")
    return menu


@router.get("", response_model=Envelope[list[MenuNode]])
async def get_menus(
    name: str | None = Query(None, description="菜单名称模糊匹配"),
    status_filter: int | None = Query(None, alias="status", description="0=开启, 1=关闭"),
    type_filter: int | None = Query(None, alias="type", description="1=目录, 2=菜单, 3=按钮"),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[list[MenuNode]]:
    """Menu tree for the management screen."""
    tree = await get_menu_tree(db, name=name, status=status_filter, menu_type=type_filter)
    return Envelope(data=tree)


@router.get("/flat", response_model=Envelope[list[MenuNode]])
async def get_menus_flat(
    name: str | None = Query(None),
    status_filter: int | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[list[MenuNode]]:
    """Flat list (no nesting) — convenient for table rendering."""
    rows = await get_menu_flat(db, name=name, status=status_filter)
    return Envelope(data=rows, total=len(rows))


@router.get("/simple", response_model=Envelope[list[MenuSimple]])
async def get_menus_simple(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[list[MenuSimple]]:
    """``id / parentId / name`` projection used by the parent-menu picker."""
    rows = await get_menu_simple(db)
    return Envelope(data=rows, total=len(rows))


@router.get("/{menu_id}", response_model=Envelope[MenuNode])
async def get_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[MenuNode]:
    """Single menu, including its ``i18n`` map."""
    menu = await _get_menu_or_404(db, menu_id)
    from rcs.services.sys.sys_service import _menu_to_node

    return Envelope(data=_menu_to_node(menu))


@router.post(
    "",
    response_model=Envelope[MenuNode],
    dependencies=[Depends(require_permissions("sys:menu:create"))],
)
async def post_menu(
    payload: MenuCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[MenuNode]:
    """Create a directory / page / button permission."""
    if payload.permission:
        clash = (
            await db.execute(
                select(SysMenu).where(
                    SysMenu.permission == payload.permission, SysMenu.is_deleted.is_(False)
                )
            )
        ).scalar_one_or_none()
        if clash is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="权限标识已存在")

    menu = await create_menu(db, payload.model_dump())
    from rcs.services.sys.sys_service import _menu_to_node

    return Envelope(message="创建成功", data=_menu_to_node(menu))


@router.put(
    "/{menu_id}",
    response_model=Envelope[MenuNode],
    dependencies=[Depends(require_permissions("sys:menu:update"))],
)
async def put_menu(
    menu_id: int,
    payload: MenuUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[MenuNode]:
    """Update a menu. A menu cannot become its own ancestor."""
    menu = await _get_menu_or_404(db, menu_id)
    data = payload.model_dump(exclude_none=True)

    new_parent = data.get("parentId")
    if new_parent:
        if new_parent == menu_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上级菜单不能是自己")
        cursor = await db.get(SysMenu, new_parent)
        while cursor is not None:
            if cursor.id == menu_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="不能将菜单移动到自己的子级下"
                )
            cursor = await db.get(SysMenu, cursor.parent_id) if cursor.parent_id else None

    updated = await update_menu(db, menu, data)
    from rcs.services.sys.sys_service import _menu_to_node

    return Envelope(message="更新成功", data=_menu_to_node(updated))


@router.delete(
    "/{menu_id}",
    dependencies=[Depends(require_permissions("sys:menu:delete"))],
)
async def remove_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[None]:
    """Soft-delete the menu and its whole subtree."""
    menu = await _get_menu_or_404(db, menu_id)
    removed = await delete_menu(db, menu)
    return Envelope(message=f"删除成功，共移除 {removed} 个节点")
