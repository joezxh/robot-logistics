"""Task registry — mirrors RCS ``scenes``/``configs`` lookup by name."""
from __future__ import annotations

from .base import LogisticsTask
from .pallet_task import PalletTask


TASK_REGISTRY: dict[str, type[LogisticsTask]] = {
    "pallet": PalletTask,
}


def register_task(name: str, cls: type[LogisticsTask]) -> None:
    TASK_REGISTRY[name] = cls


def get_task(name: str) -> LogisticsTask:
    if name not in TASK_REGISTRY:
        raise KeyError(f"unknown task {name!r}; available: {sorted(TASK_REGISTRY)}")
    return TASK_REGISTRY[name]()


__all__ = ["TASK_REGISTRY", "register_task", "get_task"]
