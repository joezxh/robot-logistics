"""API router registry.

Task 1 stubs all six router names. Tasks 11-16 each edit THIS file to replace
their stub with the real re-export (same pattern as Task 11 below).
"""
from fastapi import APIRouter
from rcs_backend.api.topology_shell import router as topology_shell
from rcs_backend.api.topology_grid import router as topology_grid
from rcs_backend.api.topology_import import router as topology_import
from rcs_backend.api.topology_export import router as topology_export
from rcs_backend.api.topology_templates import router as topology_templates
from rcs_backend.api.orders import router as orders

__all__ = [
    "topology_shell", "topology_grid",
    "topology_import", "topology_export",
    "topology_templates", "orders",
]
