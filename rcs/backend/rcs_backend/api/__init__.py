"""API router registry.

Task 1 stubs all six router names so `rcs_backend.main` can import this
package without ImportError. Tasks 11-16 replace each stub with the real
router (re-imported from the submodule via this package's __init__.py).
"""
from fastapi import APIRouter

# Stub routers — Tasks 11-16 will replace these with the real routers
# (each task will modify THIS file to do the re-export).
topology_shell = APIRouter()
topology_grid = APIRouter()
topology_import = APIRouter()
topology_export = APIRouter()
topology_templates = APIRouter()
orders = APIRouter()

__all__ = [
    "topology_shell", "topology_grid", "topology_import",
    "topology_export", "topology_templates", "orders",
]
