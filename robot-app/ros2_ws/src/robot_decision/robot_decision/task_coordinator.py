"""TaskCoordinator — layered state machine for dual-arm loading tasks.

Pure Python (no rclpy) so it can be unit-tested in isolation.
The ROS 2 integration node (task_coordinator_node.py) wraps this class.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)

# 9 action phases + ABORTING
PHASES = (
    "idle", "navigating", "docking", "approaching", "hugging",
    "lifting", "transporting", "placing", "retreating", "aborting",
)

# Valid transitions: from_phase -> set(to_phases)
_VALID_TRANSITIONS: dict[str, set[str]] = {
    "idle":         {"navigating", "retreating"},
    "navigating":   {"docking", "aborting"},
    "docking":      {"approaching", "aborting"},
    "approaching":  {"hugging", "aborting"},
    "hugging":      {"lifting", "aborting"},
    "lifting":      {"transporting", "aborting"},
    "transporting": {"placing", "aborting"},
    "placing":      {"retreating", "aborting"},
    "retreating":   {"idle", "aborting"},
    "aborting":     {"idle"},
}

# Task type → entry phase mapping
_TASK_ENTRY: dict[str, str] = {
    "goto":       "navigating",
    "pick_box":   "navigating",
    "place_box":  "navigating",
    "home_all":   "retreating",
    "transport":  "transporting",
    "dock":       "docking",
    "hug_close":  "hugging",
    "hug_release": "placing",
}

# Phase → executor name mapping
_PHASE_EXECUTOR: dict[str, str] = {
    "navigating":   "base",
    "transporting": "base",
    "retreating":   "base",
    "docking":      "arm",
    "approaching":  "arm",
    "hugging":      "hug",
    "lifting":      "arm",
    "placing":      "arm",
}

_DEFAULT_TIMEOUTS: dict[str, float] = {
    "navigating": 60.0,
    "docking": 30.0,
    "approaching": 20.0,
    "hugging": 15.0,
    "lifting": 15.0,
    "transporting": 60.0,
    "placing": 15.0,
    "retreating": 20.0,
}


class TaskCoordinator:
    """Layered FSM coordinating base + arms + hug for loading tasks."""

    def __init__(
        self,
        *,
        on_phase_change: Callable[[str], None] | None = None,
        phase_timeouts: dict[str, float] | None = None,
    ) -> None:
        self._phase = "idle"
        self._executors: dict[str, Any] = {}
        self._on_phase_change = on_phase_change
        self._current_task_type: str = ""
        self._current_params: dict[str, Any] = {}
        self._phase_start_time: float = time.monotonic()
        self._phase_timeouts: dict[str, float] = dict(_DEFAULT_TIMEOUTS)
        if phase_timeouts:
            self._phase_timeouts.update(phase_timeouts)

    @property
    def phase(self) -> str:
        return self._phase

    def get_phase(self) -> str:
        return self._phase

    def set_executor(self, name: str, executor: Any) -> None:
        self._executors[name] = executor

    def _transition(self, new_phase: str) -> None:
        allowed = _VALID_TRANSITIONS.get(self._phase, set())
        if new_phase not in allowed:
            raise RuntimeError(
                f"invalid transition {self._phase!r} → {new_phase!r}"
            )
        old = self._phase
        self._phase = new_phase
        self._phase_start_time = time.monotonic()
        logger.info("coordinator: %s → %s", old, new_phase)
        if self._on_phase_change:
            self._on_phase_change(new_phase)

    def on_task_command(self, *, task_type: str, parameters: dict[str, Any]) -> None:
        if task_type not in _TASK_ENTRY:
            raise ValueError(f"unknown task_type {task_type!r}; expected one of {tuple(_TASK_ENTRY)}")
        self._current_task_type = task_type
        self._current_params = parameters
        entry = _TASK_ENTRY[task_type]
        if self._phase != "idle":
            self._transition("aborting")
            self._transition("idle")
        self._transition(entry)
        self._dispatch_current_phase()

    def advance_phase(self) -> None:
        """Advance to the next phase in the normal flow."""
        forward_map: dict[str, str] = {
            "navigating": "docking",
            "docking": "approaching",
            "approaching": "hugging",
            "hugging": "lifting",
            "lifting": "transporting",
            "transporting": "placing",
            "placing": "retreating",
            "retreating": "idle",
            "aborting": "idle",
        }
        next_phase = forward_map.get(self._phase)
        if next_phase:
            self._transition(next_phase)
            if self._phase not in ("idle", "aborting"):
                self._dispatch_current_phase()

    def abort(self, reason: str = "") -> None:
        logger.warning("abort requested from phase=%s: %s", self._phase, reason)
        for exe in self._executors.values():
            if hasattr(exe, "stop"):
                exe.stop()
        if self._phase not in ("idle", "aborting"):
            self._transition("aborting")

    def check_timeouts(self) -> None:
        if self._phase in ("idle", "aborting"):
            return
        timeout = self._phase_timeouts.get(self._phase)
        if timeout is not None and (time.monotonic() - self._phase_start_time) > timeout:
            self.abort(f"phase {self._phase} timed out after {timeout}s")

    def _dispatch_current_phase(self) -> None:
        exe_name = _PHASE_EXECUTOR.get(self._phase)
        if not exe_name:
            return
        executor = self._executors.get(exe_name)
        if executor is None:
            logger.warning("no executor %r for phase %s", exe_name, self._phase)
            return
        if hasattr(executor, "execute"):
            executor.execute(self._phase, self._current_params)
