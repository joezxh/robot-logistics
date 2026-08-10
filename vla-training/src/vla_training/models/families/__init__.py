"""Model family adapters.

Each sub-package implements :class:`~vla_training.models.adapter.ModelAdapter`
for a specific VLA family and registers itself with the adapter registry.

Importing this module triggers registration of every built-in family.
"""
from . import hy_embodied  # noqa: F401  -- side-effect: registers adapter
