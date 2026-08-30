"""Pydantic v2 request/response models for the system-administration API.

Two response shapes coexist on purpose:

* ``Envelope[T]`` — the ``{code, message, data, total}`` wrapper used by every
  management endpoint (mirrors the reference implementation so the console
  front-end can share the same parsing logic).
* Bare models — ``LoginResponse`` / ``UserInfo`` / ``MenuNode``, which the auth
  endpoints return unwrapped.
"""
from __future__ import annotations
import datetime as dt
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Envelope(BaseModel, Generic[T]):
    """Uniform success envelope for management endpoints."""

    code: int = 0
    message: str = "success"
    data: T | None = None
    total: int | None = None


# ---------------------------------------------------------------------------
# Authentication / profile
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class LoginResponse(BaseModel):
    token: str
    tokenType: str = "Bearer"
    expiresIn: int = 0
    userId: int
    username: str
    realName: str


class UserInfo(BaseModel):
    """Everything the console needs right after login."""

    userId: int
    username: str
    realName: str
    phone: str | None = None
    email: str | None = None
    avatar: str | None = None
    status: str = "active"
    isAdmin: bool = False
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    lastLoginAt: str | None = None
    createdAt: str | None = None


class UpdateProfileRequest(BaseModel):
    realName: str | None = None
    phone: str | None = None
    email: str | None = None
    avatar: str | None = None


class ChangePasswordRequest(BaseModel):
    oldPassword: str = Field(..., min_length=1)
    newPassword: str = Field(..., min_length=6)


# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------

class MenuNode(BaseModel):
    """A menu entry as consumed by the console (recursive)."""

    id: int
    name: str
    i18n: dict[str, str] = Field(default_factory=dict)
    permission: str | None = None
    path: str | None = None
    type: int = 2
    parentId: int | None = None
    icon: str | None = None
    component: str | None = None
    componentName: str | None = None
    sort: int = 0
    status: int = 0
    visible: int = 1
    keepAlive: int = 0
    alwaysShow: int = 0
    children: list["MenuNode"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class MenuCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    i18n: dict[str, str] = Field(default_factory=dict)
    permission: str | None = None
    path: str | None = None
    type: int = 2
    parentId: int | None = 0
    icon: str | None = None
    component: str | None = None
    componentName: str | None = None
    sort: int = 0
    status: int = 0
    visible: int = 1
    keepAlive: int = 0
    alwaysShow: int = 0


class MenuUpdate(BaseModel):
    name: str | None = None
    i18n: dict[str, str] | None = None
    permission: str | None = None
    path: str | None = None
    type: int | None = None
    parentId: int | None = None
    icon: str | None = None
    component: str | None = None
    componentName: str | None = None
    sort: int | None = None
    status: int | None = None
    visible: int | None = None
    keepAlive: int | None = None
    alwaysShow: int | None = None


class MenuSimple(BaseModel):
    """Minimal projection for parent-menu pickers."""

    id: int
    parentId: int | None = None
    name: str
    i18n: dict[str, str] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    realName: str = Field(..., min_length=1, max_length=100)
    phone: str | None = None
    email: str | None = None
    status: str = "active"
    isAdmin: bool = False
    roleIds: list[int] = Field(default_factory=list)


class UserUpdate(BaseModel):
    realName: str | None = None
    phone: str | None = None
    email: str | None = None
    avatar: str | None = None
    status: str | None = None
    isAdmin: bool | None = None


class UserStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(active|disabled)$")


class UserRow(BaseModel):
    userId: int
    username: str
    realName: str
    phone: str | None = None
    email: str | None = None
    avatar: str | None = None
    status: str
    isAdmin: bool = False
    roleIds: list[int] = Field(default_factory=list)
    roleNames: list[str] = Field(default_factory=list)
    lastLoginAt: str | None = None
    lastLoginIp: str | None = None
    createdAt: str | None = None
    updatedAt: str | None = None


class RoleAssignRequest(BaseModel):
    roleIds: list[int] = Field(default_factory=list)


class PasswordResetRequest(BaseModel):
    """Administrator resets another user's password (no old password)."""

    newPassword: str = Field(..., min_length=6, max_length=128)


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

class RoleCreate(BaseModel):
    roleName: str = Field(..., min_length=1, max_length=100)
    roleCode: str = Field(..., min_length=1, max_length=50)
    description: str | None = None
    regionCode: str | None = None
    regionLevel: str | None = None
    sortOrder: int = 0
    status: str = "active"


class RoleUpdate(BaseModel):
    roleName: str | None = None
    roleCode: str | None = None
    description: str | None = None
    regionCode: str | None = None
    regionLevel: str | None = None
    sortOrder: int | None = None
    status: str | None = None


class RoleRow(BaseModel):
    roleId: int
    roleName: str
    roleCode: str
    description: str | None = None
    regionCode: str | None = None
    regionLevel: str | None = None
    sortOrder: int = 0
    status: str = "active"
    menuIds: list[int] = Field(default_factory=list)
    createdAt: str | None = None


class RoleMenuAssign(BaseModel):
    menuIds: list[int] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Dictionaries
# ---------------------------------------------------------------------------

class DictItemBase(BaseModel):
    dictCode: str
    itemCode: str
    itemName: str
    itemValue: str | None = None
    parentCode: str | None = None
    level: int = 1
    color: str | None = None
    icon: str | None = None
    sortOrder: int = 0
    isActive: bool = True
    extraData: dict[str, Any] | None = None
    remark: str | None = None


class DictItemCreate(DictItemBase):
    pass


class DictItemUpdate(BaseModel):
    itemName: str | None = None
    itemValue: str | None = None
    parentCode: str | None = None
    level: int | None = None
    color: str | None = None
    icon: str | None = None
    sortOrder: int | None = None
    isActive: bool | None = None
    extraData: dict[str, Any] | None = None
    remark: str | None = None


class DictItemRow(DictItemBase):
    itemId: int
    createdAt: str | None = None
    updatedAt: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DictBase(BaseModel):
    dictCode: str
    dictName: str
    dictType: str
    description: str | None = None
    sortOrder: int = 0
    isActive: bool = True
    extraData: dict[str, Any] | None = None


class DictCreate(DictBase):
    items: list[DictItemCreate] = Field(default_factory=list)


class DictUpdate(BaseModel):
    dictName: str | None = None
    dictType: str | None = None
    description: str | None = None
    sortOrder: int | None = None
    isActive: bool | None = None
    extraData: dict[str, Any] | None = None


class DictRow(DictBase):
    dictId: int
    createdAt: str | None = None
    updatedAt: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DictWithItems(DictRow):
    items: list[DictItemRow] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Audit logs
# ---------------------------------------------------------------------------

class AuditLogRow(BaseModel):
    logId: int
    userId: int | None = None
    username: str | None = None
    operationType: str
    operationModule: str | None = None
    operationDesc: str | None = None
    requestMethod: str | None = None
    requestUrl: str | None = None
    requestParams: dict[str, Any] | None = None
    requestIp: str | None = None
    userAgent: str | None = None
    responseStatus: int | None = None
    responseTimeMs: int | None = None
    oldData: dict[str, Any] | None = None
    newData: dict[str, Any] | None = None
    createdAt: str | None = None


def _iso(value: dt.datetime | None) -> str | None:
    """Serialise a naive DB timestamp to an ISO-8601 string."""
    return value.isoformat() if value is not None else None
