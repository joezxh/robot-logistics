"""API router registry.

Re-exports the router objects so ``rcs.main`` can mount them. The legacy
``topology_*`` routers were removed in favour of the unified-maps API
(``rcs.api.control.control_unified_maps``).
"""
from rcs.api.orders import router as orders

__all__ = ["orders"]
