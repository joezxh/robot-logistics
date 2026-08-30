#!/usr/bin/env python
"""Initialise the RCS console: schema extension, seed data, and a smoke check.

Usage::

    # from rcs/backend/
    python scripts/init_sys_data.py                 # seed menus/roles/users/dicts
    python scripts/init_sys_data.py --force         # also refresh i18n + grants
    python scripts/init_sys_data.py --migrate       # apply migrations/003_sys_admin.sql first
    python scripts/init_sys_data.py --verify        # seed, then print a summary
    python scripts/init_sys_data.py --password xxx  # override the default password

Environment:
    RCS_DATABASE_URL   postgresql+asyncpg://...   (required)
    RCS_SYS_DEFAULT_PASSWORD                      default password for seeded users

The script is idempotent: re-running it will not duplicate rows nor clobber
manual edits (unless ``--force``).

Prerequisite — table privileges
-------------------------------
When the ``sys_*`` tables were created by another role (a common case when
``rcs/docs/sys.sql`` was applied as ``postgres``), the application role needs
explicit grants before seeding. Run once as the owning role::

    GRANT USAGE ON SCHEMA public TO rcs;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO rcs;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO rcs;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO rcs;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT USAGE, SELECT ON SEQUENCES TO rcs;

A missing grant surfaces as ``InsufficientPrivilegeError``; startup logs
"系统管理数据初始化跳过" and continues serving, so the API never fails to boot
because of seeding.
"""
from __future__ import annotations
import argparse
import asyncio
import os
import sys
from pathlib import Path

# Make ``rcs`` importable when the script is invoked directly.
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from sqlalchemy import func, select  # noqa: E402

from rcs.db.session import get_sessionmaker  # noqa: E402
from rcs.sysadmin.models import (  # noqa: E402
    SysAuditLog,
    SysDictionary,
    SysDictionaryItem,
    SysMenu,
    SysRole,
    SysRoleMenu,
    SysUser,
    SysUserRole,
)
from rcs.sysadmin.seed import seed_sys_data  # noqa: E402


async def _count(db, model) -> int:
    return int((await db.execute(select(func.count()).select_from(model))).scalar_one())


async def apply_migration() -> None:
    """Run ``migrations/003_sys_admin.sql`` through a synchronous psycopg URL."""
    url = os.getenv("RCS_DATABASE_URL", "")
    if not url:
        print("! RCS_DATABASE_URL is not set — skipping the SQL migration step.")
        return

    sql_path = _BACKEND_ROOT / "migrations" / "003_sys_admin.sql"
    if not sql_path.exists():
        print(f"! migration file not found: {sql_path}")
        return

    try:
        import psycopg  # type: ignore[import-not-found]
    except ImportError:
        print(
            "! psycopg is not installed; apply the migration manually:\n"
            f"    psql \"$RCS_DATABASE_URL\" -f {sql_path}"
        )
        return

    dsn = url.replace("postgresql+asyncpg://", "postgresql://")
    print(f"> applying {sql_path.name}")
    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute(sql_path.read_text(encoding="utf-8"))
    print("  migration applied")


async def seed(force: bool, password: str | None) -> dict:
    if password:
        os.environ["RCS_SYS_DEFAULT_PASSWORD"] = password
        # get_settings() caches a singleton; drop it so the override is picked up.
        import rcs.config as cfg

        cfg._settings = None

    async with get_sessionmaker()() as db:
        result = await seed_sys_data(db, force=force)
    return result


async def verify() -> None:
    """Print a post-seed summary so a human can sanity-check the result."""
    async with get_sessionmaker()() as db:
        print("\n--- 数据库概览 ---")
        print(f"菜单/权限 : {await _count(db, SysMenu)}")
        print(f"角色      : {await _count(db, SysRole)}")
        print(f"用户      : {await _count(db, SysUser)}")
        print(f"用户-角色 : {await _count(db, SysUserRole)}")
        print(f"角色-菜单 : {await _count(db, SysRoleMenu)}")
        print(f"字典      : {await _count(db, SysDictionary)}")
        print(f"字典项    : {await _count(db, SysDictionaryItem)}")
        print(f"审计日志  : {await _count(db, SysAuditLog)}")

        users = (await db.execute(select(SysUser).order_by(SysUser.user_id))).scalars().all()
        print("\n--- 默认账号 ---")
        for u in users:
            roles = (
                await db.execute(
                    select(SysRole.role_code)
                    .join(SysUserRole, SysUserRole.role_id == SysRole.role_id)
                    .where(SysUserRole.user_id == u.user_id)
                )
            ).all()
            print(
                f"  {u.username:<10} admin={str(u.is_admin):<5} "
                f"roles={[r[0] for r in roles]} name={u.real_name}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialise RCS system-administration data.")
    parser.add_argument("--force", action="store_true",
                        help="refresh i18n / role grants / passwords on existing rows")
    parser.add_argument("--migrate", action="store_true",
                        help="apply migrations/003_sys_admin.sql before seeding")
    parser.add_argument("--verify", action="store_true", help="print a summary after seeding")
    parser.add_argument("--password", default=None, help="password for the seeded accounts")
    args = parser.parse_args()

    if not os.getenv("RCS_DATABASE_URL"):
        print("! RCS_DATABASE_URL is not set; falling back to the configured default.")

    async def _run() -> None:
        if args.migrate:
            await apply_migration()
        result = await seed(args.force, args.password)
        print("> seed result:", result)
        if args.verify:
            await verify()

    asyncio.run(_run())


if __name__ == "__main__":
    main()
