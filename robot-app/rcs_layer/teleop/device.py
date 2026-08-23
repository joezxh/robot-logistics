"""Teleop input adapters (RCS ``teleop`` parity)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

import numpy as np


class TeleopInput(ABC):
    """Produces a delta action (Cartesian [dx,dy,dz,droll,dpitch,dyaw] or joints)."""

    @abstractmethod
    def read(self) -> np.ndarray:
        """Return the latest delta command (shape depends on the device)."""

    def close(self) -> None:  # pragma: no cover - optional
        return None


class KeyboardAdapter(TeleopInput):
    """ASCII-key delta adapter (no external deps; unit-testable).

    Maps WASD / QE / arrow keys to a 6-D Cartesian delta. Used as the default
    teleop source so demos run without special hardware (mirrors RCS keyboard teleop).
    """

    def __init__(self, step: float = 0.01) -> None:
        self.step = step
        self._keys: set[str] = set()

    def press(self, key: str) -> None:
        self._keys.add(key.lower())

    def release(self, key: str) -> None:
        self._keys.discard(key.lower())

    def read(self) -> np.ndarray:
        s = self.step
        d = np.zeros(6)
        if "w" in self._keys:
            d[0] += s
        if "s" in self._keys:
            d[0] -= s
        if "a" in self._keys:
            d[1] += s
        if "d" in self._keys:
            d[1] -= s
        if "q" in self._keys:
            d[2] += s
        if "e" in self._keys:
            d[2] -= s
        if "j" in self._keys:
            d[5] += s
        if "l" in self._keys:
            d[5] -= s
        return d

    def get_action(self, obs: dict | None = None) -> np.ndarray:
        """Get current action for data collection.

        Args:
            obs: Current observation (unused for keyboard, kept for API compatibility)

        Returns:
            Current delta action
        """
        return self.read()


class SpaceMouseAdapter(TeleopInput):
    """3D mouse adapter placeholder (RCS SpaceMouse teleop parity).

    Falls back to zero deltas when the device/HID library is unavailable so the
    pipeline remains runnable; real HID polling is wired in when hardware is present.
    """

    def __init__(self, scale: float = 0.05) -> None:
        self.scale = scale

    def read(self) -> np.ndarray:
        return np.zeros(6)  # hook: poll HID device when available


__all__ = ["TeleopInput", "KeyboardAdapter", "SpaceMouseAdapter"]
