"""Compatibility shim removed (Task 5 added ``task_type`` / ``parameters`` to Command natively)."""
from __future__ import annotations

from rcs.state.command import Command  # noqa: F401  (intentionally empty: re-export for legacy imports)
