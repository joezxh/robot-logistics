"""Idempotent seed data for the system-administration tables.

Run standalone::

    python -m rcs.sysadmin.seed            # seed only
    python -m rcs.sysadmin.seed --force    # also refresh i18n on existing rows

or let :func:`seed_if_empty` run automatically at startup (controlled by the
``RCS_SYS_SEED_ON_STARTUP`` setting).

The seeder is deliberately *additive*: rows are matched by their natural key
(``sys_menu.permission``, ``sys_role.role_code``, ``sys_user.username``,
``sys_dictionary.dict_code``) and left alone when they already exist, so
re-running it never destroys operator edits.
"""
from __future__ import annotations
import argparse
import asyncio
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rcs.db.sys_models import (
    SysDictionary,
    SysDictionaryItem,
    SysMenu,
    SysRole,
    SysRoleMenu,
    SysUser,
    SysUserRole,
)
from rcs.services.sys.sys_security import get_password_hash

logger = logging.getLogger(__name__)


def _button(prefix: str, zh: str, zh_tw: str, en: str, ja: str) -> list[dict[str, Any]]:
    """Expand a resource prefix into its create/update/delete button rows.

    Menus of ``type=3`` are pure permission carriers: they are never rendered in
    the sidebar but are stored in the same table so role assignment stays a
    single tree.
    """
    actions = [
        ("create", "新增", "新增", "Create", "作成"),
        ("update", "修改", "修改", "Update", "更新"),
        ("delete", "删除", "刪除", "Delete", "削除"),
    ]
    return [
        {
            "permission": f"{prefix}:{action}",
            "i18n": {"zh-CN": f"{zh}{zh_label}", "zh-TW": f"{zh_tw}{zh_tw_label}",
                     "en-US": f"{en} {en_label}", "ja-JP": f"{ja}{ja_label}"},
            "type": 3,
            "sort": 80 + index,
            "parent": f"{prefix}:list",
        }
        for index, (action, zh_label, zh_tw_label, en_label, ja_label) in enumerate(actions)
    ]


# ---------------------------------------------------------------------------
# Menu catalogue
# ---------------------------------------------------------------------------
# ``component`` is a path relative to ``src/``; the console resolves it through
# Vite's ``import.meta.glob`` when turning menus into routes.

MENU_SEED: list[dict[str, Any]] = [
    {
        "permission": "dashboard:view",
        "i18n": {"zh-CN": "控制台", "zh-TW": "控制檯", "en-US": "Dashboard", "ja-JP": "ダッシュボード"},
        "path": "/dashboard", "component": "views/DashboardView.vue",
        "component_name": "DashboardView", "icon": "DashboardOutlined",
        "type": 2, "sort": 1, "parent": None,
    },
    # --- 设备管理 -----------------------------------------------------------
    {
        "permission": "device:menu",
        "i18n": {"zh-CN": "设备管理", "zh-TW": "設備管理", "en-US": "Devices", "ja-JP": "デバイス管理"},
        "path": "/devices", "component": None, "component_name": None,
        "icon": "RobotOutlined", "type": 1, "sort": 10, "parent": None,
    },
    {
        "permission": "sys:device:list",
        "i18n": {"zh-CN": "设备列表", "zh-TW": "設備列表", "en-US": "Device List", "ja-JP": "デバイス一覧"},
        "path": "/devices", "component": "views/control/AdminDevicesView.vue",
        "component_name": "AdminDevicesView", "icon": "UnorderedListOutlined",
        "type": 2, "sort": 1, "parent": "device:menu",
    },
    {
        "permission": "sys:device:control",
        "i18n": {"zh-CN": "设备控制", "zh-TW": "設備控制", "en-US": "Device Control", "ja-JP": "デバイス制御"},
        "path": "/control", "component": "views/control/ControlView.vue",
        "component_name": "ControlView", "icon": "ControlOutlined",
        "type": 2, "sort": 2, "parent": "device:menu",
    },
    # --- 仓储作业 -----------------------------------------------------------
    {
        "permission": "wms:menu",
        "i18n": {"zh-CN": "仓储作业", "zh-TW": "倉儲作業", "en-US": "Warehouse Ops", "ja-JP": "倉庫作業"},
        "path": "/wms", "component": None, "component_name": None,
        "icon": "AppstoreOutlined", "type": 1, "sort": 20, "parent": None,
    },

    {
        "permission": "sys:order:list",
        "i18n": {"zh-CN": "订单管理", "zh-TW": "訂單管理", "en-US": "Orders", "ja-JP": "オーダー管理"},
        "path": "/admin/orders", "component": "views/control/AdminOrdersView.vue",
        "component_name": "AdminOrdersView", "icon": "ShoppingOutlined",
        "type": 2, "sort": 2, "parent": "wms:menu",
    },
    {
        "permission": "sys:scheduler:list",
        "i18n": {"zh-CN": "调度策略", "zh-TW": "調度策略", "en-US": "Scheduler", "ja-JP": "スケジューラ"},
        "path": "/admin/scheduler", "component": "views/control/AdminSchedulerView.vue",
        "component_name": "AdminSchedulerView", "icon": "DeploymentUnitOutlined",
        "type": 2, "sort": 3, "parent": "wms:menu",
    },
    {
        "permission": "sys:log:list",
        "i18n": {"zh-CN": "系统日志", "zh-TW": "系統日誌", "en-US": "System Logs", "ja-JP": "システムログ"},
        "path": "/admin/logs", "component": "views/control/AdminLogsView.vue",
        "component_name": "AdminLogsView", "icon": "FileTextOutlined",
        "type": 2, "sort": 4, "parent": "wms:menu",
    },

    # --- 系统管理 -----------------------------------------------------------
    {
        "permission": "system:menu",
        "i18n": {"zh-CN": "系统管理", "zh-TW": "系統管理", "en-US": "System", "ja-JP": "システム管理"},
        "path": "/system", "component": None, "component_name": None,
        "icon": "SettingOutlined", "type": 1, "sort": 90, "parent": None,
    },
    {
        "permission": "sys:user:list",
        "i18n": {"zh-CN": "用户管理", "zh-TW": "用戶管理", "en-US": "Users", "ja-JP": "ユーザー管理"},
        "path": "/system/users", "component": "views/system/UserManage.vue",
        "component_name": "UserManage", "icon": "UserOutlined",
        "type": 2, "sort": 1, "parent": "system:menu",
    },
    {
        "permission": "sys:role:list",
        "i18n": {"zh-CN": "角色管理", "zh-TW": "角色管理", "en-US": "Roles", "ja-JP": "ロール管理"},
        "path": "/system/roles", "component": "views/system/RoleManage.vue",
        "component_name": "RoleManage", "icon": "SafetyCertificateOutlined",
        "type": 2, "sort": 2, "parent": "system:menu",
    },
    {
        "permission": "sys:menu:list",
        "i18n": {"zh-CN": "菜单管理", "zh-TW": "選單管理", "en-US": "Menus", "ja-JP": "メニュー管理"},
        "path": "/system/menus", "component": "views/system/MenuManage.vue",
        "component_name": "MenuManage", "icon": "MenuOutlined",
        "type": 2, "sort": 3, "parent": "system:menu",
    },
    {
        "permission": "sys:audit:list",
        "i18n": {"zh-CN": "审计日志", "zh-TW": "稽核日誌", "en-US": "Audit Logs", "ja-JP": "監査ログ"},
        "path": "/system/audit", "component": "views/system/AuditLog.vue",
        "component_name": "AuditLog", "icon": "HistoryOutlined",
        "type": 2, "sort": 4, "parent": "system:menu",
    },
    {
        "permission": "sys:dict:list",
        "i18n": {"zh-CN": "字典管理", "zh-TW": "字典管理", "en-US": "Dictionaries", "ja-JP": "辞書管理"},
        "path": "/system/dicts", "component": "views/system/DictManage.vue",
        "component_name": "DictManage", "icon": "BookOutlined",
        "type": 2, "sort": 5, "parent": "system:menu",
    },
    # Button-level permissions (type 3) — never rendered in the sidebar.
    *_button("sys:user", "用户", "用戶", "User", "ユーザー"),
    *_button("sys:role", "角色", "角色", "Role", "ロール"),
    *_button("sys:menu", "菜单", "選單", "Menu", "メニュー"),
    *_button("sys:dict", "字典", "字典", "Dictionary", "辞書"),
    {
        "permission": "sys:user:reset-password",
        "i18n": {"zh-CN": "重置密码", "zh-TW": "重設密碼", "en-US": "Reset Password",
                 "ja-JP": "パスワードリセット"},
        "type": 3, "sort": 95, "parent": "sys:user:list",
    },
    {
        "permission": "sys:user:assign-role",
        "i18n": {"zh-CN": "分配角色", "zh-TW": "分配角色", "en-US": "Assign Roles", "ja-JP": "ロール割当"},
        "type": 3, "sort": 96, "parent": "sys:user:list",
    },
    {
        "permission": "sys:role:assign-menu",
        "i18n": {"zh-CN": "分配菜单", "zh-TW": "分配選單", "en-US": "Assign Menus", "ja-JP": "メニュー割当"},
        "type": 3, "sort": 97, "parent": "sys:role:list",
    },
    {
        "permission": "sys:audit:delete",
        "i18n": {"zh-CN": "清理日志", "zh-TW": "清理日誌", "en-US": "Purge Logs", "ja-JP": "ログ削除"},
        "type": 3, "sort": 98, "parent": "sys:audit:list",
    },
    # Personal profile — reachable from the avatar menu, hidden in the sidebar.
    {
        "permission": "profile:view",
        "i18n": {"zh-CN": "个人信息", "zh-TW": "個人資訊", "en-US": "My Profile", "ja-JP": "個人情報"},
        "path": "/profile", "component": "views/ProfileView.vue",
        "component_name": "ProfileView", "icon": "IdcardOutlined",
        "type": 2, "sort": 99, "parent": None, "visible": 0,
    },
]

# Role catalogue — ``menus`` is either ``"*"`` (every menu) or a list of codes.
ROLE_SEED: list[dict[str, Any]] = [
    {
        "role_code": "super_admin",
        "role_name": {"zh-CN": "超级管理员", "zh-TW": "超級管理員",
                      "en-US": "Super Admin", "ja-JP": "スーパー管理者"},
        "description": "拥有全部权限，不可删除",
        "sort_order": 1,
        "menus": "*",
    },
    {
        "role_code": "admin",
        "role_name": {"zh-CN": "系统管理员", "zh-TW": "系統管理員",
                      "en-US": "System Admin", "ja-JP": "システム管理者"},
        "description": "可管理用户/角色/菜单/字典与审计日志",
        "sort_order": 2,
        "menus": [
            "dashboard:view",
            "device:menu", "sys:device:list", "sys:device:control",
            "wms:menu", "sys:order:list", "sys:scheduler:list", "sys:log:list",
            "system:menu",
            "sys:user:list", "sys:user:create", "sys:user:update", "sys:user:delete",
            "sys:user:reset-password", "sys:user:assign-role",
            "sys:role:list", "sys:role:create", "sys:role:update", "sys:role:delete",
            "sys:role:assign-menu",
            "sys:menu:list", "sys:menu:create", "sys:menu:update", "sys:menu:delete",
            "sys:audit:list", "sys:audit:delete",
            "sys:dict:list", "sys:dict:create", "sys:dict:update", "sys:dict:delete",
            "profile:view",
        ],
    },
    {
        "role_code": "operator",
        "role_name": {"zh-CN": "调度操作员", "zh-TW": "調度操作員",
                      "en-US": "Dispatch Operator", "ja-JP": "ディスパッチオペレーター"},
        "description": "日常仓储作业与设备控制",
        "sort_order": 3,
        "menus": [
            "dashboard:view",
            "device:menu", "sys:device:list", "sys:device:control",
            "wms:menu", "sys:order:list", "sys:scheduler:list", "sys:log:list",
            "profile:view",
        ],
    },
    {
        "role_code": "viewer",
        "role_name": {"zh-CN": "只读访客", "zh-TW": "唯讀訪客",
                      "en-US": "Read-only Viewer", "ja-JP": "閲覧者"},
        "description": "仅可查看控制台与孪生视图",
        "sort_order": 4,
        "menus": ["dashboard:view", "profile:view"],
    },
]

# User catalogue — ``password=None`` falls back to ``Settings.sys_default_password``.
USER_SEED: list[dict[str, Any]] = [
    {
        "username": "admin", "password": None, "real_name": "系统管理员",
        "email": "admin@rcs.local", "is_admin": True, "roles": ["super_admin"],
    },
    {
        "username": "operator", "password": None, "real_name": "调度操作员",
        "email": "operator@rcs.local", "is_admin": False, "roles": ["operator"],
    },
    {
        "username": "viewer", "password": None, "real_name": "只读访客",
        "email": "viewer@rcs.local", "is_admin": False, "roles": ["viewer"],
    },
]

DICT_SEED: list[dict[str, Any]] = [
    {
        "dict_code": "user_status", "dict_name": "用户状态", "dict_type": "system",
        "description": "sys_user.status 取值",
        "items": [
            {"item_code": "active", "item_name": "启用", "item_value": "active", "color": "green"},
            {"item_code": "disabled", "item_name": "禁用", "item_value": "disabled", "color": "red"},
        ],
    },
    {
        "dict_code": "menu_type", "dict_name": "菜单类型", "dict_type": "system",
        "description": "sys_menu.type 取值",
        "items": [
            {"item_code": "1", "item_name": "目录", "item_value": "1", "color": "blue"},
            {"item_code": "2", "item_name": "菜单", "item_value": "2", "color": "cyan"},
            {"item_code": "3", "item_name": "按钮", "item_value": "3", "color": "purple"},
        ],
    },
    {
        "dict_code": "operation_type", "dict_name": "操作类型", "dict_type": "system",
        "description": "sys_audit_log.operation_type 取值",
        "items": [
            {"item_code": "create", "item_name": "新增", "item_value": "create", "color": "green"},
            {"item_code": "update", "item_name": "修改", "item_value": "update", "color": "blue"},
            {"item_code": "delete", "item_name": "删除", "item_value": "delete", "color": "red"},
            {"item_code": "query", "item_name": "查询", "item_value": "query", "color": "default"},
            {"item_code": "login", "item_name": "登录", "item_value": "login", "color": "cyan"},
            {"item_code": "logout", "item_name": "登出", "item_value": "logout", "color": "default"},
        ],
    },
    {
        "dict_code": "robot_morphology", "dict_name": "机器人形态", "dict_type": "business",
        "description": "robot_devices.morphology 取值",
        "items": [
            {"item_code": "agv", "item_name": "AGV 搬运机器人", "item_value": "agv", "color": "blue"},
            {"item_code": "arm", "item_name": "机械臂", "item_value": "arm", "color": "purple"},
            {"item_code": "amr", "item_name": "AMR 自主移动", "item_value": "amr", "color": "cyan"},
            {"item_code": "forklift", "item_name": "无人叉车", "item_value": "forklift", "color": "orange"},
        ],
    },
    {
        "dict_code": "order_status", "dict_name": "订单状态", "dict_type": "business",
        "description": "robot_orders.status 取值",
        "items": [
            {"item_code": "queued", "item_name": "排队中", "item_value": "queued", "color": "default"},
            {"item_code": "running", "item_name": "执行中", "item_value": "running", "color": "blue"},
            {"item_code": "done", "item_name": "已完成", "item_value": "done", "color": "green"},
            {"item_code": "failed", "item_name": "失败", "item_value": "failed", "color": "red"},
            {"item_code": "cancelled", "item_name": "已取消", "item_value": "cancelled", "color": "default"},
        ],
    },
    {
        "dict_code": "log_level", "dict_name": "日志级别", "dict_type": "business",
        "description": "系统日志级别",
        "items": [
            {"item_code": "debug", "item_name": "DEBUG", "item_value": "debug", "color": "default"},
            {"item_code": "info", "item_name": "INFO", "item_value": "info", "color": "blue"},
            {"item_code": "warn", "item_name": "WARN", "item_value": "warn", "color": "orange"},
            {"item_code": "error", "item_name": "ERROR", "item_value": "error", "color": "red"},
        ],
    },
]


# ---------------------------------------------------------------------------
# Seeders
# ---------------------------------------------------------------------------

async def seed_menus(db: AsyncSession, force: bool = False) -> dict[str, int]:
    """Insert missing menus and resolve parent links; return permission -> id."""
    existing = {
        m.permission: m
        for m in (await db.execute(select(SysMenu))).scalars().all()
        if m.permission
    }
    created = 0
    updated = 0
    for item in MENU_SEED:
        menu = existing.get(item["permission"])
        if menu is None:
            menu = SysMenu(
                name=item["i18n"].get("zh-CN") or item["i18n"].get("en-US") or item["permission"],
                i18n=item["i18n"],
                permission=item["permission"],
                path=item.get("path"),
                type=item.get("type", 2),
                icon=item.get("icon"),
                component=item.get("component"),
                component_name=item.get("component_name"),
                sort=item.get("sort", 0),
                parent_id=0,
                visible=item.get("visible", 1),
                status=0,
            )
            db.add(menu)
            existing[item["permission"]] = menu
            created += 1
        elif force:
            menu.i18n = item["i18n"]
            menu.name = item["i18n"].get("zh-CN") or menu.name
            if item.get("component"):
                menu.component = item["component"]
                menu.component_name = item.get("component_name")
            updated += 1

    await db.flush()

    # Second pass: parents may point at menus created in this same run.
    for item in MENU_SEED:
        parent_perm = item.get("parent")
        if not parent_perm:
            continue
        parent = existing.get(parent_perm)
        child = existing.get(item["permission"])
        if parent is not None and child is not None:
            child.parent_id = parent.id

    await db.commit()
    logger.info("菜单种子：新增 %d，更新 %d", created, updated)
    return {perm: menu.id for perm, menu in existing.items() if menu.id is not None}


async def seed_roles(db: AsyncSession, menu_ids: dict[str, int], force: bool = False) -> dict[str, int]:
    """Insert roles and (re)build their ``sys_role_menu`` grants."""
    existing = {r.role_code: r for r in (await db.execute(select(SysRole))).scalars().all()}
    all_menu_ids = list(menu_ids.values())
    role_ids: dict[str, int] = {}

    for item in ROLE_SEED:
        role = existing.get(item["role_code"])
        if role is None:
            role = SysRole(
                role_code=item["role_code"],
                role_name=item["role_name"].get("zh-CN") or item["role_code"],
                description=item["description"],
                sort_order=item.get("sort_order", 0),
                status="active",
            )
            db.add(role)
            await db.flush()
            existing[item["role_code"]] = role
        elif force:
            role.role_name = item["role_name"].get("zh-CN") or role.role_name
            role.description = item["description"]

        role_ids[item["role_code"]] = role.role_id

        grants = item.get("menus")
        wanted = (
            all_menu_ids
            if grants == "*"
            else [menu_ids[p] for p in (grants or []) if p in menu_ids]
        )

        # Rebuild only when the role was just created or the grant set differs,
        # so manual tweaks survive a restart.
        current = {
            rm.menu_id
            for rm in (
                await db.execute(select(SysRoleMenu).where(SysRoleMenu.role_id == role.role_id))
            ).scalars().all()
        }
        if not current or current != set(wanted):
            from sqlalchemy import delete as _delete

            await db.execute(_delete(SysRoleMenu).where(SysRoleMenu.role_id == role.role_id))
            for menu_id in wanted:
                db.add(SysRoleMenu(role_id=role.role_id, menu_id=menu_id))

    await db.commit()
    logger.info("角色种子：%d 个角色已就绪", len(role_ids))
    return role_ids


async def seed_users(db: AsyncSession, role_ids: dict[str, int], force: bool = False) -> list[str]:
    """Insert the default accounts and attach their roles."""
    from rcs.config import get_settings

    default_password = get_settings().sys_default_password
    existing = {u.username: u for u in (await db.execute(select(SysUser))).scalars().all()}
    seen: list[str] = []

    for item in USER_SEED:
        user = existing.get(item["username"])
        if user is None:
            user = SysUser(
                username=item["username"],
                password_hash=get_password_hash(item["password"] or default_password),
                real_name=item["real_name"],
                email=item.get("email"),
                phone=item.get("phone"),
                is_admin=bool(item.get("is_admin", False)),
                status="active",
            )
            db.add(user)
            await db.flush()
            existing[item["username"]] = user
        elif force and item["password"]:
            user.password_hash = get_password_hash(item["password"])

        seen.append(item["username"])

        current = {
            ur.role_id
            for ur in (
                await db.execute(select(SysUserRole).where(SysUserRole.user_id == user.user_id))
            ).scalars().all()
        }
        wanted = {role_ids[c] for c in item.get("roles", []) if c in role_ids}
        if wanted != current:
            from sqlalchemy import delete as _delete

            await db.execute(_delete(SysUserRole).where(SysUserRole.user_id == user.user_id))
            for role_id in wanted:
                db.add(SysUserRole(user_id=user.user_id, role_id=role_id))

    await db.commit()
    logger.info("用户种子：%s（默认密码来自 RCS_SYS_DEFAULT_PASSWORD）", ", ".join(seen))
    return seen


async def seed_dictionaries(db: AsyncSession, force: bool = False) -> int:
    """Insert dictionaries and their items (items are added when missing)."""
    existing = {
        d.dict_code: d for d in (await db.execute(select(SysDictionary))).scalars().all()
    }
    count = 0
    for item in DICT_SEED:
        d = existing.get(item["dict_code"])
        if d is None:
            d = SysDictionary(
                dict_code=item["dict_code"],
                dict_name=item["dict_name"],
                dict_type=item.get("dict_type", "system"),
                description=item.get("description"),
                is_active=True,
            )
            db.add(d)
            await db.flush()
            existing[item["dict_code"]] = d
            count += 1
        elif force:
            d.dict_name = item["dict_name"]
            d.description = item.get("description")

        rows = {
            i.item_code: i
            for i in (
                await db.execute(
                    select(SysDictionaryItem).where(
                        SysDictionaryItem.dict_code == item["dict_code"]
                    )
                )
            ).scalars().all()
        }
        for index, raw in enumerate(item.get("items", [])):
            if raw["item_code"] in rows:
                continue
            db.add(
                SysDictionaryItem(
                    dict_code=item["dict_code"],
                    item_code=raw["item_code"],
                    item_name=raw["item_name"],
                    item_value=raw.get("item_value"),
                    color=raw.get("color"),
                    sort_order=index,
                    is_active=True,
                )
            )

    await db.commit()
    logger.info("字典种子：新增 %d 个字典", count)
    return count


async def seed_sys_data(db: AsyncSession, force: bool = False) -> dict[str, Any]:
    """Run every seeder in order inside the caller's session/transaction."""
    menu_ids = await seed_menus(db, force=force)
    role_ids = await seed_roles(db, menu_ids, force=force)
    users = await seed_users(db, role_ids, force=force)
    dicts = await seed_dictionaries(db, force=force)
    return {
        "menus": len(menu_ids),
        "roles": len(role_ids),
        "users": users,
        "dictionaries": dicts,
    }


async def seed_if_empty(force: bool = False) -> dict[str, Any] | None:
    """Open a short-lived session and seed when the tables look empty.

    Returns ``None`` when the seed step is disabled or the database is not
    reachable — startup must never fail because of seeding.
    """
    from rcs.config import get_settings
    from rcs.db.session import get_sessionmaker

    settings = get_settings()

    async with get_sessionmaker()() as db:
        try:
            if not force:
                menu_count = len((await db.execute(select(SysMenu.id))).all())
                user_count = len((await db.execute(select(SysUser.user_id))).all())
                if menu_count and user_count:
                    logger.info("系统管理数据已存在（菜单 %d，用户 %d），跳过初始化", menu_count, user_count)
                    return None
            return await seed_sys_data(db, force=force)
        except Exception as exc:  # noqa: BLE001 - seeding must not break startup
            logger.warning("系统管理数据初始化跳过（%s）", exc)
            await db.rollback()
            return None


def main() -> None:
    """CLI entry point: ``python -m rcs.sysadmin.seed [--force]``."""
    parser = argparse.ArgumentParser(description="Seed RCS system-administration data.")
    parser.add_argument("--force", action="store_true", help="refresh i18n/roles even when rows exist")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    async def _run() -> None:
        from rcs.db.session import get_sessionmaker

        async with get_sessionmaker()() as db:
            result = await seed_sys_data(db, force=args.force)
        print("Seed complete:", result)

    asyncio.run(_run())


if __name__ == "__main__":
    main()
