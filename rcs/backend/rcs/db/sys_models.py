"""SQLAlchemy ORM models for the system-administration module.

Every class here maps 1:1 onto a table in ``rcs/docs/sys.sql`` (schema
``public``, PostgreSQL). Column names, types, nullability and defaults follow
that dump so the module can run against an already-provisioned database
without emitting a divergent DDL.

Only one column is an extension: ``SysMenu.i18n`` (JSONB) carries the
per-locale menu titles and is added by ``migrations/003_sys_admin.sql``.

Relationships use ``lazy="selectin"``: under asyncpg a plain ``select``
lazy-load would raise ``MissingGreenlet`` when the attribute is touched
outside the greenlet context.
"""
from __future__ import annotations
import datetime as dt

from sqlalchemy import (
    BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from rcs.db.models import Base


def _now() -> dt.datetime:
    """Naive UTC timestamp — ``sys.sql`` declares ``timestamp`` (no TZ)."""
    return dt.datetime.utcnow()


class SysUser(Base):
    """系统用户表 (sys_user)。"""

    __tablename__ = "sys_user"
    __table_args__ = (
        Index("ix_sys_user_username", "username", unique=True),
        Index("idx_user_status", "status"),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    real_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_login_at: Mapped[dt.datetime | None] = mapped_column(DateTime)
    last_login_ip: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=_now
    )
    deleted_at: Mapped[dt.datetime | None] = mapped_column(DateTime)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user_roles: Mapped[list["SysUserRole"]] = relationship(
        back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<SysUser {self.username}>"


class SysRole(Base):
    """系统角色表 (sys_role)。"""

    __tablename__ = "sys_role"
    __table_args__ = (
        Index("idx_role_code", "role_code"),
        Index("idx_role_region", "region_code"),
    )

    role_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    region_code: Mapped[str | None] = mapped_column(String(20))
    region_level: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=_now
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user_roles: Mapped[list["SysUserRole"]] = relationship(
        back_populates="role", lazy="selectin", cascade="all, delete-orphan"
    )
    role_menus: Mapped[list["SysRoleMenu"]] = relationship(
        back_populates="role", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<SysRole {self.role_code}>"


class SysUserRole(Base):
    """用户角色关联表 (sys_user_role)。"""

    __tablename__ = "sys_user_role"
    __table_args__ = (
        Index("uk_user_role", "user_id", "role_id", unique=True),
        Index("idx_user_role_role", "role_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("sys_user.user_id"), nullable=False, index=True
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("sys_role.role_id"), nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    user: Mapped["SysUser"] = relationship(back_populates="user_roles", lazy="selectin")
    role: Mapped["SysRole"] = relationship(back_populates="user_roles", lazy="selectin")

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<SysUserRole user={self.user_id} role={self.role_id}>"


class SysMenu(Base):
    """菜单/权限表 (sys_menu)。

    ``type`` 语义：1=目录, 2=菜单, 3=按钮。
    ``status`` 语义：0=开启, 1=关闭。
    """

    __tablename__ = "sys_menu"
    __table_args__ = (
        Index("idx_menu_parent_id", "parent_id"),
        Index("idx_menu_status", "status"),
        Index("idx_menu_type", "type"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    path: Mapped[str | None] = mapped_column(String(255))
    parent_id: Mapped[int | None] = mapped_column(BigInteger, default=0)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=_now
    )
    permission: Mapped[str | None] = mapped_column(String(100), index=True)
    type: Mapped[int] = mapped_column(Integer, default=2)
    icon: Mapped[str | None] = mapped_column(String(100))
    component: Mapped[str | None] = mapped_column(String(255))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    component_name: Mapped[str | None] = mapped_column(String(100))
    visible: Mapped[int] = mapped_column(Integer, default=1)
    keep_alive: Mapped[int] = mapped_column(Integer, default=0)
    always_show: Mapped[int] = mapped_column(Integer, default=0)

    # --- Extension (migrations/003_sys_admin.sql) -------------------------
    # Per-locale titles: {"zh-CN": "设备管理", "en-US": "Devices", ...}.
    # `name` stays the fallback rendered when a locale key is missing.
    i18n: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    role_menus: Mapped[list["SysRoleMenu"]] = relationship(
        back_populates="menu", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<SysMenu {self.name}>"


class SysRoleMenu(Base):
    """角色菜单关联表 (sys_role_menu)。"""

    __tablename__ = "sys_role_menu"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("sys_role.role_id"), nullable=False, index=True
    )
    menu_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("sys_menu.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    role: Mapped["SysRole"] = relationship(back_populates="role_menus", lazy="selectin")
    menu: Mapped["SysMenu"] = relationship(back_populates="role_menus", lazy="selectin")

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<SysRoleMenu role={self.role_id} menu={self.menu_id}>"


class SysAuditLog(Base):
    """系统审计日志表 (sys_audit_log)。"""

    __tablename__ = "sys_audit_log"
    __table_args__ = (
        Index("idx_audit_operation", "operation_type", "operation_module"),
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_time", "created_at"),
        Index("idx_audit_ip", "request_ip"),
    )

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger)
    username: Mapped[str | None] = mapped_column(String(50))
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    operation_module: Mapped[str | None] = mapped_column(String(50))
    operation_desc: Mapped[str | None] = mapped_column(Text)
    request_method: Mapped[str | None] = mapped_column(String(10))
    request_url: Mapped[str | None] = mapped_column(String(500))
    request_params: Mapped[dict | None] = mapped_column(JSONB)
    request_ip: Mapped[str | None] = mapped_column(String(50))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    response_status: Mapped[int | None] = mapped_column(Integer)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    old_data: Mapped[dict | None] = mapped_column(JSONB)
    new_data: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<SysAuditLog {self.log_id} {self.operation_type}>"


class SysDictionary(Base):
    """系统字典表 (sys_dictionary)。"""

    __tablename__ = "sys_dictionary"
    __table_args__ = (
        Index("idx_dict_code", "dict_code"),
        Index("idx_dict_type", "dict_type"),
        Index("idx_dict_active", "is_active"),
    )

    dict_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    dict_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    dict_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dict_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    extra_data: Mapped[dict | None] = mapped_column(JSONB)
    created_by: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=_now
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<SysDictionary {self.dict_code}>"


class SysDictionaryItem(Base):
    """系统字典项表 (sys_dictionary_item)。"""

    __tablename__ = "sys_dictionary_item"
    __table_args__ = (
        Index("uk_dict_item", "dict_code", "item_code", unique=True),
        Index("idx_item_dict_code", "dict_code"),
        Index("idx_item_code", "item_code"),
        Index("idx_item_parent", "parent_code"),
        Index("idx_item_active", "is_active"),
    )

    item_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    dict_code: Mapped[str] = mapped_column(String(50), nullable=False)
    item_code: Mapped[str] = mapped_column(String(50), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    item_value: Mapped[str | None] = mapped_column(String(200))
    parent_code: Mapped[str | None] = mapped_column(String(50))
    level: Mapped[int] = mapped_column(Integer, default=1)
    color: Mapped[str | None] = mapped_column(String(20))
    icon: Mapped[str | None] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    extra_data: Mapped[dict | None] = mapped_column(JSONB)
    remark: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=_now
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<SysDictionaryItem {self.dict_code}.{self.item_code}>"


__all__ = [
    "SysAuditLog",
    "SysDictionary",
    "SysDictionaryItem",
    "SysMenu",
    "SysRole",
    "SysRoleMenu",
    "SysUser",
    "SysUserRole",
]
