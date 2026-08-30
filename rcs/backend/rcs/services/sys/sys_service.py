"""Business logic for the system-administration module.

Routers stay thin: they validate input with the Pydantic models in
:mod:`rcs.sysadmin.schemas`, delegate to a function here, and wrap the result
in an envelope. Everything that touches the database lives in this module so it
can be unit-tested without spinning up an HTTP layer.
"""
from __future__ import annotations
import datetime as dt
from typing import Any, Iterable, Sequence

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from rcs.db.sys_models import (
    SysAuditLog,
    SysDictionary,
    SysDictionaryItem,
    SysMenu,
    SysRole,
    SysRoleMenu,
    SysUser,
    SysUserRole,
)
from rcs.services.sys.sys_schemas import (
    AuditLogRow,
    DictItemRow,
    DictRow,
    DictWithItems,
    MenuNode,
    MenuSimple,
    RoleRow,
    UserInfo,
    UserRow,
    _iso,
)
from rcs.services.sys.sys_security import verify_password

# Role code that, alongside ``is_admin``, grants every permission.
SUPER_ADMIN_ROLE = "super_admin"
WILDCARD_PERMISSION = "*:*"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _own_session(db: AsyncSession | None) -> tuple[AsyncSession, bool]:
    """Return ``(session, we_own_it)`` so callers may pass an existing session."""
    if db is not None:
        return db, False
    from rcs.db.session import get_sessionmaker

    return get_sessionmaker()(), True


def _root_parent_ids() -> tuple[Any, ...]:
    """Values of ``parent_id`` that mean "top level" (schema allows NULL or 0)."""
    return (None, 0)


def _normalise_parent_id(parent_id: int | None) -> int | None:
    """Collapse 0 -> None so tree building has a single sentinel."""
    return None if parent_id in (None, 0) else parent_id


def build_menu_tree(nodes: Sequence[dict[str, Any]], parent_id: int | None = None) -> list[dict[str, Any]]:
    """Turn a flat, already-sorted list of menu dicts into a nested tree.

    Both ``NULL`` and ``0`` are treated as "root" because the seeded data and
    the legacy dump disagree on which sentinel to use.
    """
    tree: list[dict[str, Any]] = []
    for node in nodes:
        node_parent = _normalise_parent_id(node.get("parentId"))
        if node_parent == _normalise_parent_id(parent_id):
            child = dict(node)
            children = build_menu_tree(nodes, node.get("id"))
            if children:
                child["children"] = children
            tree.append(child)
    return tree


def _menu_to_dict(menu: SysMenu) -> dict[str, Any]:
    return {
        "id": menu.id,
        "name": menu.name,
        "i18n": menu.i18n or {},
        "permission": menu.permission,
        "path": menu.path,
        "type": menu.type,
        "parentId": menu.parent_id,
        "icon": menu.icon,
        "component": menu.component,
        "componentName": menu.component_name,
        "sort": menu.sort,
        "status": menu.status,
        "visible": menu.visible,
        "keepAlive": menu.keep_alive,
        "alwaysShow": menu.always_show,
    }


def _tree_to_nodes(
    nodes: Sequence[dict[str, Any]],
    node_by_id: dict[int, MenuNode],
) -> list[MenuNode]:
    """Transfer the nesting computed by `build_menu_tree` onto `MenuNode`s.

    `build_menu_tree` operates on plain dicts (and only sets `children` when a
    node has some), but the API returns `MenuNode` models. Building the models
    straight from those dicts would blow up, so the tree shape is copied back
    onto models built from the ORM rows.
    """
    out: list[MenuNode] = []
    for node in nodes:
        current = node_by_id[node["id"]]
        children = _tree_to_nodes(node.get("children", []), node_by_id)
        out.append(current.model_copy(update={"children": children}) if children else current)
    return out


def _menu_to_node(menu: SysMenu) -> MenuNode:
    return MenuNode(
        id=menu.id,
        name=menu.name,
        i18n=menu.i18n or {},
        permission=menu.permission,
        path=menu.path,
        type=menu.type,
        parentId=menu.parent_id,
        icon=menu.icon,
        component=menu.component,
        componentName=menu.component_name,
        sort=menu.sort,
        status=menu.status,
        visible=menu.visible,
        keepAlive=menu.keep_alive,
        alwaysShow=menu.always_show,
    )


# ---------------------------------------------------------------------------
# Authentication & authorisation
# ---------------------------------------------------------------------------

async def authenticate(db: AsyncSession, username: str, password: str) -> SysUser:
    """Return the user for a valid credential pair; raise ``ValueError`` otherwise.

    The error message is intentionally identical for unknown accounts, wrong
    passwords and disabled accounts so it cannot be used for enumeration.
    """
    user = (
        await db.execute(
            select(SysUser).where(SysUser.username == username, SysUser.is_deleted.is_(False))
        )
    ).scalar_one_or_none()

    if user is None or not verify_password(password, user.password_hash):
        raise ValueError("用户名或密码错误")
    if user.status != "active":
        raise ValueError("账号已被禁用，请联系管理员")
    return user


async def get_role_codes(db: AsyncSession, user_id: int) -> list[str]:
    """Role codes assigned to ``user_id``."""
    rows = (
        await db.execute(
            select(SysRole.role_code)
            .join(SysUserRole, SysUserRole.role_id == SysRole.role_id)
            .where(SysUserRole.user_id == user_id, SysRole.is_deleted.is_(False))
        )
    ).all()
    return [r[0] for r in rows]


async def get_user_permissions(db: AsyncSession, user_id: int, is_admin: bool = False) -> list[str]:
    """Flatten ``user -> roles -> menus`` into the permission code list.

    Super-admins receive the single wildcard permission ``*:*``.
    """
    if is_admin:
        return [WILDCARD_PERMISSION]

    role_codes = await get_role_codes(db, user_id)
    if SUPER_ADMIN_ROLE in role_codes:
        return [WILDCARD_PERMISSION]

    rows = (
        await db.execute(
            select(SysMenu.permission)
            .join(SysRoleMenu, SysRoleMenu.menu_id == SysMenu.id)
            .join(SysUserRole, SysUserRole.role_id == SysRoleMenu.role_id)
            .where(
                SysUserRole.user_id == user_id,
                SysMenu.is_deleted.is_(False),
                SysMenu.permission.is_not(None),
            )
        )
    ).all()
    return sorted({r[0] for r in rows if r[0]})


async def has_permissions(
    user_id: int,
    required: Iterable[str],
    db: AsyncSession | None = None,
) -> bool:
    """``True`` when the user holds *all* ``required`` permission codes.

    Accepts an optional session; when omitted (the audit middleware calls this
    outside a request-scoped session) a short-lived one is opened and closed.
    """
    required = [p for p in required if p]
    if not required:
        return True

    session, owned = await _own_session(db)
    try:
        user = await session.get(SysUser, user_id)
        if user is None or user.is_deleted or user.status != "active":
            return False
        granted = await get_user_permissions(session, user_id, bool(user.is_admin))
        if WILDCARD_PERMISSION in granted:
            return True
        return set(required).issubset(set(granted))
    finally:
        if owned:
            await session.close()


async def build_user_info(db: AsyncSession, user: SysUser) -> UserInfo:
    """Compose the payload returned by ``/auth/me``."""
    roles = await get_role_codes(db, user.user_id)
    permissions = await get_user_permissions(db, user.user_id, bool(user.is_admin))
    return UserInfo(
        userId=user.user_id,
        username=user.username,
        realName=user.real_name,
        phone=user.phone,
        email=user.email,
        avatar=user.avatar_url,
        status=user.status,
        isAdmin=bool(user.is_admin),
        roles=roles,
        permissions=permissions,
        lastLoginAt=_iso(user.last_login_at),
        createdAt=_iso(user.created_at),
    )


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def _user_to_row(user: SysUser) -> UserRow:
    roles = [ur for ur in (user.user_roles or []) if ur.role is not None]
    return UserRow(
        userId=user.user_id,
        username=user.username,
        realName=user.real_name,
        phone=user.phone,
        email=user.email,
        avatar=user.avatar_url,
        status=user.status,
        isAdmin=bool(user.is_admin),
        roleIds=[ur.role_id for ur in roles],
        roleNames=[ur.role.role_name for ur in roles],
        lastLoginAt=_iso(user.last_login_at),
        lastLoginIp=user.last_login_ip,
        createdAt=_iso(user.created_at),
        updatedAt=_iso(user.updated_at),
    )


async def list_users(
    db: AsyncSession,
    *,
    keyword: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[UserRow], int]:
    """Paginated, optionally filtered user listing with role names attached."""
    conditions = [SysUser.is_deleted.is_(False)]
    if keyword:
        like = f"%{keyword}%"
        conditions.append(
            or_(
                SysUser.username.ilike(like),
                SysUser.real_name.ilike(like),
                SysUser.phone.ilike(like),
                SysUser.email.ilike(like),
            )
        )
    if status:
        conditions.append(SysUser.status == status)

    total = (
        await db.execute(select(func.count()).select_from(SysUser).where(*conditions))
    ).scalar_one()

    rows = (
        await db.execute(
            select(SysUser)
            .where(*conditions)
            .order_by(SysUser.user_id.asc())
            .offset(skip)
            .limit(limit)
        )
    ).scalars().unique().all()
    return [_user_to_row(u) for u in rows], int(total)


async def create_user(db: AsyncSession, payload: dict[str, Any], password_hash: str) -> SysUser:
    """Insert a user and (optionally) its role links."""
    role_ids: list[int] = payload.pop("roleIds", []) or []
    user = SysUser(
        username=payload["username"],
        password_hash=password_hash,
        real_name=payload["realName"],
        phone=payload.get("phone"),
        email=payload.get("email"),
        status=payload.get("status", "active"),
        is_admin=bool(payload.get("isAdmin", False)),
    )
    db.add(user)
    await db.flush()
    for role_id in role_ids:
        db.add(SysUserRole(user_id=user.user_id, role_id=role_id))
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: SysUser, payload: dict[str, Any]) -> SysUser:
    """Apply the non-``None`` fields of ``payload`` onto ``user``."""
    mapping = {
        "realName": "real_name",
        "phone": "phone",
        "email": "email",
        "avatar": "avatar_url",
        "status": "status",
        "isAdmin": "is_admin",
    }
    for field, column in mapping.items():
        value = payload.get(field)
        if value is not None:
            setattr(user, column, value)
    user.updated_at = dt.datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: SysUser) -> None:
    """Soft-delete a user and detach its role links."""
    user.is_deleted = True
    user.deleted_at = dt.datetime.utcnow()
    await db.execute(delete(SysUserRole).where(SysUserRole.user_id == user.user_id))
    await db.commit()


async def assign_user_roles(db: AsyncSession, user_id: int, role_ids: list[int]) -> None:
    """Replace the full role set of ``user_id`` (idempotent)."""
    await db.execute(delete(SysUserRole).where(SysUserRole.user_id == user_id))
    for role_id in role_ids:
        db.add(SysUserRole(user_id=user_id, role_id=role_id))
    await db.commit()


async def get_user_role_ids(db: AsyncSession, user_id: int) -> list[int]:
    rows = (
        await db.execute(select(SysUserRole.role_id).where(SysUserRole.user_id == user_id))
    ).all()
    return [r[0] for r in rows]


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

async def list_roles(db: AsyncSession, *, keyword: str | None = None) -> list[RoleRow]:
    conditions = [SysRole.is_deleted.is_(False)]
    if keyword:
        like = f"%{keyword}%"
        conditions.append(or_(SysRole.role_name.ilike(like), SysRole.role_code.ilike(like)))
    roles = (
        await db.execute(select(SysRole).where(*conditions).order_by(SysRole.sort_order, SysRole.role_id))
    ).scalars().unique().all()
    return [
        RoleRow(
            roleId=r.role_id,
            roleName=r.role_name,
            roleCode=r.role_code,
            description=r.description,
            regionCode=r.region_code,
            regionLevel=r.region_level,
            sortOrder=r.sort_order,
            status=r.status,
            menuIds=[rm.menu_id for rm in (r.role_menus or [])],
            createdAt=_iso(r.created_at),
        )
        for r in roles
    ]


async def create_role(db: AsyncSession, payload: dict[str, Any]) -> SysRole:
    role = SysRole(**payload)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def update_role(db: AsyncSession, role: SysRole, payload: dict[str, Any]) -> SysRole:
    for field, column in {
        "roleName": "role_name",
        "roleCode": "role_code",
        "description": "description",
        "regionCode": "region_code",
        "regionLevel": "region_level",
        "sortOrder": "sort_order",
        "status": "status",
    }.items():
        value = payload.get(field)
        if value is not None:
            setattr(role, column, value)
    role.updated_at = dt.datetime.utcnow()
    await db.commit()
    await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, role: SysRole) -> None:
    """Soft-delete a role and drop its menu grants."""
    role.is_deleted = True
    await db.execute(delete(SysRoleMenu).where(SysRoleMenu.role_id == role.role_id))
    await db.commit()


async def assign_role_menus(db: AsyncSession, role_id: int, menu_ids: list[int]) -> None:
    """Replace the menu grants of a role, keeping menus that still exist."""
    valid = set(
        (
            await db.execute(
                select(SysMenu.id).where(SysMenu.id.in_(menu_ids), SysMenu.is_deleted.is_(False))
            )
        )
        .scalars()
        .all()
    )
    await db.execute(delete(SysRoleMenu).where(SysRoleMenu.role_id == role_id))
    for menu_id in menu_ids:
        if menu_id in valid:
            db.add(SysRoleMenu(role_id=role_id, menu_id=menu_id))
    await db.commit()


# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------

async def _load_menus(
    db: AsyncSession,
    *,
    name: str | None = None,
    status: int | None = None,
    menu_type: int | None = None,
) -> list[SysMenu]:
    conditions = [SysMenu.is_deleted.is_(False)]
    if name:
        conditions.append(SysMenu.name.ilike(f"%{name}%"))
    if status is not None:
        conditions.append(SysMenu.status == status)
    if menu_type is not None:
        conditions.append(SysMenu.type == menu_type)
    return (
        (await db.execute(select(SysMenu).where(*conditions).order_by(SysMenu.sort, SysMenu.id)))
        .scalars()
        .unique()
        .all()
    )


async def get_menu_tree(
    db: AsyncSession,
    *,
    name: str | None = None,
    status: int | None = None,
    menu_type: int | None = None,
) -> list[MenuNode]:
    """Full menu tree for the management screen."""
    menus = await _load_menus(db, name=name, status=status, menu_type=menu_type)
    node_by_id = {m.id: _menu_to_node(m) for m in menus}
    return _tree_to_nodes(
        build_menu_tree([_menu_to_dict(m) for m in menus]), node_by_id
    )


async def get_menu_flat(
    db: AsyncSession,
    *,
    name: str | None = None,
    status: int | None = None,
    menu_type: int | None = None,
) -> list[MenuNode]:
    """Flat menu list, useful for table views and dropdowns."""
    menus = await _load_menus(db, name=name, status=status, menu_type=menu_type)
    return [_menu_to_node(m) for m in menus]


async def get_menu_simple(db: AsyncSession) -> list[MenuSimple]:
    """``id / parentId / name`` projection for parent-menu pickers."""
    menus = await _load_menus(db, status=0, menu_type=None)
    return [
        MenuSimple(id=m.id, parentId=m.parent_id, name=m.name, i18n=m.i18n or {})
        for m in menus
        if m.type in (1, 2)
    ]


async def get_user_menu_tree(db: AsyncSession, user: SysUser) -> list[MenuNode]:
    """Menus the given user may see.

    Super-admins get everything; everyone else is limited to the intersection
    of their roles' grants, filtered to directories and pages (type 1/2) that
    are enabled and visible.
    """
    menus = await _load_menus(db, status=0)
    visible = [m for m in menus if m.type in (1, 2) and m.visible == 1]

    if not user.is_admin:
        role_codes = await get_role_codes(db, user.user_id)
        if SUPER_ADMIN_ROLE not in role_codes:
            granted = set(
                (
                    await db.execute(
                        select(SysRoleMenu.menu_id).join(
                            SysUserRole, SysUserRole.role_id == SysRoleMenu.role_id
                        )
                        .where(SysUserRole.user_id == user.user_id)
                    )
                )
                .scalars()
                .all()
            )
            # Keep a child when it is granted *or* when one of its descendants
            # is — otherwise an explicitly granted leaf under an un-granted
            # directory would be unreachable in the sidebar.
            reachable: set[int] = set()
            by_id = {m.id: m for m in visible}
            for menu_id in granted:
                cursor: int | None = menu_id
                while cursor is not None and cursor not in reachable:
                    reachable.add(cursor)
                    parent = by_id.get(cursor)
                    cursor = _normalise_parent_id(parent.parent_id) if parent else None
            visible = [m for m in visible if m.id in reachable]

    node_by_id = {m.id: _menu_to_node(m) for m in visible}
    flat = [_menu_to_dict(m) for m in visible]
    tree: list[MenuNode] = []

    def _attach(nodes: list[dict[str, Any]]) -> list[MenuNode]:
        out: list[MenuNode] = []
        for node in nodes:
            current = node_by_id[node["id"]]
            children = _attach(node.get("children", []))
            if children:
                current = current.model_copy(update={"children": children})
            out.append(current)
        return out

    for node in build_menu_tree(flat):
        tree.extend(_attach([node]))
    return tree


async def create_menu(db: AsyncSession, payload: dict[str, Any]) -> SysMenu:
    menu = SysMenu(
        name=payload["name"],
        i18n=payload.get("i18n") or {},
        permission=payload.get("permission"),
        path=payload.get("path"),
        type=payload.get("type", 2),
        parent_id=payload.get("parentId") or 0,
        icon=payload.get("icon"),
        component=payload.get("component"),
        component_name=payload.get("componentName"),
        sort=payload.get("sort", 0),
        status=payload.get("status", 0),
        visible=payload.get("visible", 1),
        keep_alive=payload.get("keepAlive", 0),
        always_show=payload.get("alwaysShow", 0),
    )
    db.add(menu)
    await db.commit()
    await db.refresh(menu)
    return menu


async def update_menu(db: AsyncSession, menu: SysMenu, payload: dict[str, Any]) -> SysMenu:
    for field, column in {
        "name": "name",
        "i18n": "i18n",
        "permission": "permission",
        "path": "path",
        "type": "type",
        "icon": "icon",
        "component": "component",
        "componentName": "component_name",
        "sort": "sort",
        "status": "status",
        "visible": "visible",
        "keepAlive": "keep_alive",
        "alwaysShow": "always_show",
    }.items():
        value = payload.get(field)
        if value is not None:
            setattr(menu, column, value)
    if "parentId" in payload and payload["parentId"] is not None:
        menu.parent_id = payload["parentId"]
    menu.updated_at = dt.datetime.utcnow()
    await db.commit()
    await db.refresh(menu)
    return menu


async def delete_menu(db: AsyncSession, menu: SysMenu) -> int:
    """Soft-delete a menu and all of its descendants; returns the row count."""
    all_menus = await _load_menus(db)
    children_by_parent: dict[int | None, list[int]] = {}
    for m in all_menus:
        children_by_parent.setdefault(_normalise_parent_id(m.parent_id), []).append(m.id)

    doomed: set[int] = set()
    stack = [menu.id]
    while stack:
        current = stack.pop()
        if current in doomed:
            continue
        doomed.add(current)
        stack.extend(children_by_parent.get(current, []))

    # Menus are soft-deleted (the audit trail and role grants reference them),
    # but the role-menu links of the removed subtree are purged outright.
    for m in all_menus:
        if m.id in doomed:
            m.is_deleted = True
            m.updated_at = dt.datetime.utcnow()
    await db.execute(delete(SysRoleMenu).where(SysRoleMenu.menu_id.in_(doomed)))
    await db.commit()
    return len(doomed)


# ---------------------------------------------------------------------------
# Dictionaries
# ---------------------------------------------------------------------------

def _dict_to_row(d: SysDictionary) -> DictRow:
    return DictRow(
        dictId=d.dict_id,
        dictCode=d.dict_code,
        dictName=d.dict_name,
        dictType=d.dict_type,
        description=d.description,
        sortOrder=d.sort_order,
        isActive=d.is_active,
        extraData=d.extra_data,
        createdAt=_iso(d.created_at),
        updatedAt=_iso(d.updated_at),
    )


def _item_to_row(i: SysDictionaryItem) -> DictItemRow:
    return DictItemRow(
        itemId=i.item_id,
        dictCode=i.dict_code,
        itemCode=i.item_code,
        itemName=i.item_name,
        itemValue=i.item_value,
        parentCode=i.parent_code,
        level=i.level,
        color=i.color,
        icon=i.icon,
        sortOrder=i.sort_order,
        isActive=i.is_active,
        extraData=i.extra_data,
        remark=i.remark,
        createdAt=_iso(i.created_at),
        updatedAt=_iso(i.updated_at),
    )


async def list_dictionaries(
    db: AsyncSession, *, keyword: str | None = None, dict_type: str | None = None
) -> list[DictRow]:
    conditions = [SysDictionary.is_deleted.is_(False)]
    if keyword:
        like = f"%{keyword}%"
        conditions.append(
            or_(SysDictionary.dict_code.ilike(like), SysDictionary.dict_name.ilike(like))
        )
    if dict_type:
        conditions.append(SysDictionary.dict_type == dict_type)
    rows = (
        await db.execute(
            select(SysDictionary)
            .where(*conditions)
            .order_by(SysDictionary.sort_order, SysDictionary.dict_id)
        )
    ).scalars().all()
    return [_dict_to_row(d) for d in rows]


async def list_dictionary_items(db: AsyncSession, dict_code: str) -> list[DictItemRow]:
    rows = (
        await db.execute(
            select(SysDictionaryItem)
            .where(
                SysDictionaryItem.dict_code == dict_code,
                SysDictionaryItem.is_deleted.is_(False),
            )
            .order_by(SysDictionaryItem.sort_order, SysDictionaryItem.item_id)
        )
    ).scalars().all()
    return [_item_to_row(i) for i in rows]


async def get_dictionary_with_items(db: AsyncSession, dict_code: str) -> DictWithItems | None:
    d = (
        await db.execute(
            select(SysDictionary).where(
                SysDictionary.dict_code == dict_code, SysDictionary.is_deleted.is_(False)
            )
        )
    ).scalar_one_or_none()
    if d is None:
        return None
    return DictWithItems(**_dict_to_row(d).model_dump(), items=await list_dictionary_items(db, dict_code))


async def get_dictionaries_batch(db: AsyncSession, codes: list[str]) -> dict[str, list[DictItemRow]]:
    """Fetch several dictionaries in one round trip (console bootstrap)."""
    if not codes:
        return {}
    rows = (
        await db.execute(
            select(SysDictionaryItem)
            .where(
                SysDictionaryItem.dict_code.in_(codes),
                SysDictionaryItem.is_deleted.is_(False),
                SysDictionaryItem.is_active.is_(True),
            )
            .order_by(SysDictionaryItem.sort_order, SysDictionaryItem.item_id)
        )
    ).scalars().all()
    grouped: dict[str, list[DictItemRow]] = {code: [] for code in codes}
    for item in rows:
        grouped.setdefault(item.dict_code, []).append(_item_to_row(item))
    return grouped


async def create_dictionary(db: AsyncSession, payload: dict[str, Any], created_by: int | None = None) -> SysDictionary:
    items = payload.pop("items", []) or []
    d = SysDictionary(created_by=created_by, **payload)
    db.add(d)
    await db.flush()
    for item in items:
        db.add(SysDictionaryItem(created_by=created_by, **item))
    await db.commit()
    await db.refresh(d)
    return d


async def update_dictionary(db: AsyncSession, d: SysDictionary, payload: dict[str, Any]) -> SysDictionary:
    for field, column in {
        "dictName": "dict_name",
        "dictType": "dict_type",
        "description": "description",
        "sortOrder": "sort_order",
        "isActive": "is_active",
        "extraData": "extra_data",
    }.items():
        value = payload.get(field)
        if value is not None:
            setattr(d, column, value)
    d.updated_at = dt.datetime.utcnow()
    await db.commit()
    await db.refresh(d)
    return d


async def delete_dictionary(db: AsyncSession, d: SysDictionary) -> None:
    d.is_deleted = True
    await db.execute(
        delete(SysDictionaryItem).where(SysDictionaryItem.dict_code == d.dict_code)
    )
    await db.commit()


async def create_dictionary_item(
    db: AsyncSession, payload: dict[str, Any], created_by: int | None = None
) -> SysDictionaryItem:
    item = SysDictionaryItem(created_by=created_by, **payload)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update_dictionary_item(
    db: AsyncSession, item: SysDictionaryItem, payload: dict[str, Any]
) -> SysDictionaryItem:
    for field, column in {
        "itemName": "item_name",
        "itemValue": "item_value",
        "parentCode": "parent_code",
        "level": "level",
        "color": "color",
        "icon": "icon",
        "sortOrder": "sort_order",
        "isActive": "is_active",
        "extraData": "extra_data",
        "remark": "remark",
    }.items():
        value = payload.get(field)
        if value is not None:
            setattr(item, column, value)
    item.updated_at = dt.datetime.utcnow()
    await db.commit()
    await db.refresh(item)
    return item


async def delete_dictionary_item(db: AsyncSession, item: SysDictionaryItem) -> None:
    item.is_deleted = True
    await db.commit()


# ---------------------------------------------------------------------------
# Audit logs
# ---------------------------------------------------------------------------

def _audit_to_row(log: SysAuditLog) -> AuditLogRow:
    return AuditLogRow(
        logId=log.log_id,
        userId=log.user_id,
        username=log.username,
        operationType=log.operation_type,
        operationModule=log.operation_module,
        operationDesc=log.operation_desc,
        requestMethod=log.request_method,
        requestUrl=log.request_url,
        requestParams=log.request_params,
        requestIp=log.request_ip,
        userAgent=log.user_agent,
        responseStatus=log.response_status,
        responseTimeMs=log.response_time_ms,
        oldData=log.old_data,
        newData=log.new_data,
        createdAt=_iso(log.created_at),
    )


async def list_audit_logs(
    db: AsyncSession,
    *,
    user_id: int | None = None,
    username: str | None = None,
    operation_type: str | None = None,
    operation_module: str | None = None,
    keyword: str | None = None,
    start_at: dt.datetime | None = None,
    end_at: dt.datetime | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[AuditLogRow], int]:
    """Filtered, newest-first audit log page."""
    conditions = []
    if user_id is not None:
        conditions.append(SysAuditLog.user_id == user_id)
    if username:
        conditions.append(SysAuditLog.username.ilike(f"%{username}%"))
    if operation_type:
        conditions.append(SysAuditLog.operation_type == operation_type)
    if operation_module:
        conditions.append(SysAuditLog.operation_module == operation_module)
    if keyword:
        like = f"%{keyword}%"
        conditions.append(
            or_(
                SysAuditLog.operation_desc.ilike(like),
                SysAuditLog.request_url.ilike(like),
                SysAuditLog.request_ip.ilike(like),
            )
        )
    if start_at is not None:
        conditions.append(SysAuditLog.created_at >= start_at)
    if end_at is not None:
        conditions.append(SysAuditLog.created_at <= end_at)

    where = conditions or [True]  # type: ignore[list-item]
    total = (
        await db.execute(select(func.count()).select_from(SysAuditLog).where(*where))
    ).scalar_one()
    rows = (
        await db.execute(
            select(SysAuditLog)
            .where(*where)
            .order_by(SysAuditLog.created_at.desc(), SysAuditLog.log_id.desc())
            .offset(skip)
            .limit(limit)
        )
    ).scalars().all()
    return [_audit_to_row(r) for r in rows], int(total)
