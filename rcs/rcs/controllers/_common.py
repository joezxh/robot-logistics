"""Shared helpers: limits, error thresholds, command queue."""
from __future__ import annotations
import asyncio
from collections import deque


def clip_to_limits(values: list[float], lower: list[float], upper: list[float]) -> list[float]:
    return [max(lower[i], min(upper[i], values[i])) for i in range(len(values))]


def abs_max(values: list[float]) -> float:
    if not values:
        return 0.0
    return max(abs(v) for v in values)


class CommandQueue:
    """Bounded FIFO with idempotency check on command_id."""

    def __init__(self, maxsize: int = 1024) -> None:
        self._q: deque = deque(maxlen=maxsize)
        self._seen: set[str] = set()

    def push(self, item) -> bool:
        if item.command_id in self._seen:
            return False
        if len(self._q) >= self._q.maxlen:
            return False
        self._q.append(item)
        self._seen.add(item.command_id)
        return True

    def pop(self):
        return self._q.popleft() if self._q else None

    def __len__(self) -> int:
        return len(self._q)
