"""Aggregate router for ``/api/sys/**``.

Every route registered here inherits :class:`~rcs.sysadmin.audit.AuditRoute`,
which enforces the ``openapi_extra={"permissions": [...]}`` declarations and
writes an audit record for each call.
"""
from __future__ import annotations

from fastapi import APIRouter

from rcs.services.sys.sys_audit import AuditRoute
from rcs.api.sys import sys_dicts, sys_auth, sys_users, sys_dashboard, sys_roles, sys_menus, sys_audit

router = APIRouter(route_class=AuditRoute)

router.include_router(sys_auth.router)
router.include_router(sys_dashboard.router)
router.include_router(sys_users.router)
router.include_router(sys_roles.router)
router.include_router(sys_menus.router)
router.include_router(sys_audit.router)
router.include_router(sys_dicts.router)

__all__ = ["router"]
