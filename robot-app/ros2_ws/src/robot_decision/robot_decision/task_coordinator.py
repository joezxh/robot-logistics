"""TaskCoordinator — layered state machine for dual-arm loading tasks.

重构为继承通用 FSM 基类，消除架构重复。
"""
from __future__ import annotations

import logging
import time
from typing import Any, Callable

from robot_decision.state_machine import FSM, FSMError

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


class TaskCoordinator(FSM):
    """Layered FSM coordinating base + arms + hug for loading tasks.

    重构为继承通用 FSM 基类，统一架构。
    与 robot_decision/state_machine.py 的 FSM 类共享代码。
    """

    def __init__(
        self,
        *,
        on_phase_change: Callable[[str], None] | None = None,
        phase_timeouts: dict[str, float] | None = None,
    ) -> None:
        # 初始化 FSM 基类
        super().__init__(
            states=PHASES,
            transitions=_VALID_TRANSITIONS,
            initial="idle",
            on_enter={p: self._on_phase_enter for p in PHASES},
        )

        self._executors: dict[str, Any] = {}
        self._on_phase_change = on_phase_change
        self._current_task_type: str = ""
        self._current_params: dict[str, Any] = {}
        self._phase_timeouts: dict[str, float] = dict(_DEFAULT_TIMEOUTS)
        if phase_timeouts:
            self._phase_timeouts.update(phase_timeouts)

    def _on_phase_enter(self, fsm: FSM) -> None:
        """FSM 钩子：阶段进入时触发"""
        if self._on_phase_change:
            self._on_phase_change(self._state)
        self._dispatch_current_phase()

    def set_executor(self, name: str, executor: Any) -> None:
        self._executors[name] = executor

    def on_task_command(self, *, task_type: str, parameters: dict[str, Any]) -> None:
        if task_type not in _TASK_ENTRY:
            raise ValueError(f"unknown task_type {task_type!r}; expected one of {tuple(_TASK_ENTRY)}")
        self._current_task_type = task_type
        self._current_params = parameters
        entry = _TASK_ENTRY[task_type]

        # 使用 FSM 基类的 transition 方法
        if self._state != "idle":
            self.transition("aborting")
            self.transition("idle")
        self.transition(entry)

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
        next_phase = forward_map.get(self._state)
        if next_phase:
            self.transition(next_phase)

    def abort(self, reason: str = "") -> None:
        logger.warning("abort requested from phase=%s: %s", self._state, reason)
        for exe in self._executors.values():
            if hasattr(exe, "stop"):
                exe.stop()
        if self._state not in ("idle", "aborting"):
            self.transition("aborting")

    def check_timeouts(self) -> None:
        if self._state in ("idle", "aborting"):
            return
        timeout = self._phase_timeouts.get(self._state)
        if timeout is not None and (time.monotonic() - self._phase_start_time) > timeout:
            self.abort(f"phase {self._state} timed out after {timeout}s")

    def _dispatch_current_phase(self) -> None:
        exe_name = _PHASE_EXECUTOR.get(self._state)
        if not exe_name:
            return
        executor = self._executors.get(exe_name)
        if executor is None:
            logger.warning("no executor %r for phase %s", exe_name, self._state)
            return
        if hasattr(executor, "execute"):
            executor.execute(self._state, self._current_params)
