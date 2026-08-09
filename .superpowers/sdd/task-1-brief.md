### Task 1: TaskCoordinator FSM

**Files:**
- Create: `robot-app/ros2_ws/src/robot_decision/robot_decision/task_coordinator.py`
- Test: `robot-app/ros2_ws/src/robot_decision/tests/test_task_coordinator.py`

**Interfaces:**
- Consumes: `TaskCommandMsg` (from `robot_msgs.contracts`)
- Produces: `phase: str` property, `on_phase_change` callback, executor dispatch decisions

- [ ] **Step 1: Write the failing test**

```python
"""Tests for TaskCoordinator — pure Python FSM, no rclpy."""
import time
import pytest
from robot_decision.task_coordinator import TaskCoordinator


class FakeExecutor:
    def __init__(self, succeeds=True):
        self.calls = []
        self._succeeds = succeeds

    def execute(self, phase, params):
        self.calls.append((phase, params))

    def stop(self):
        self.calls.append(("stop",))


class TestTaskCoordinatorTransitions:
    def _make(self):
        received = []
        coord = TaskCoordinator(on_phase_change=lambda p: received.append(p))
        return coord, received

    def test_initial_phase_is_idle(self):
        coord, _ = self._make()
        assert coord.phase == "idle"

    def test_goto_triggers_navigating(self):
        coord, received = self._make()
        base = FakeExecutor()
        coord.set_executor("base", base)
        coord.on_task_command(task_type="goto", parameters={"target_pose": {"x": 1, "y": 2, "yaw": 0}})
        assert coord.phase == "navigating"
        assert "navigating" in received

    def test_pick_box_full_sequence(self):
        coord, received = self._make()
        base = FakeExecutor()
        arm = FakeExecutor()
        hug = FakeExecutor()
        coord.set_executor("base", base)
        coord.set_executor("arm", arm)
        coord.set_executor("hug", hug)
        coord.on_task_command(task_type="pick_box", parameters={
            "target_pose": {"x": 1, "y": 0, "yaw": 0},
            "hug_params": {"pressure_target": 50.0, "approach_speed": 0.3, "close_speed": 0.1},
        })
        assert coord.phase == "navigating"
        coord.advance_phase()  # navigating → docking
        assert coord.phase == "docking"
        coord.advance_phase()  # docking → approaching
        assert coord.phase == "approaching"
        coord.advance_phase()  # approaching → hugging
        assert coord.phase == "hugging"
        coord.advance_phase()  # hugging → lifting
        assert coord.phase == "lifting"

    def test_abort_from_any_phase(self):
        coord, _ = self._make()
        coord.set_executor("base", FakeExecutor())
        for phase in ["navigating", "docking", "hugging", "lifting", "transporting"]:
            coord._phase = phase
            coord.abort("test abort")
            assert coord.phase == "aborting"

    def test_abort_returns_to_idle(self):
        coord, _ = self._make()
        coord.set_executor("base", FakeExecutor())
        coord._phase = "navigating"
        coord.abort("test")
        coord.advance_phase()  # aborting → idle
        assert coord.phase == "idle"

    def test_invalid_task_type_raises(self):
        coord, _ = self._make()
        with pytest.raises(ValueError, match="unknown task_type"):
            coord.on_task_command(task_type="fly_away", parameters={})

    def test_home_all_returns_to_idle_after_retreat(self):
        coord, _ = self._make()
        coord.set_executor("base", FakeExecutor())
        coord.set_executor("arm", FakeExecutor())
        coord.on_task_command(task_type="home_all", parameters={})
        # home_all goes through retreating then idle
        assert coord.phase in ("retreating", "idle")

    def test_phase_timeout_triggers_abort(self):
        coord, _ = self._make()
        coord.set_executor("base", FakeExecutor())
        coord._phase_timeouts["navigating"] = 0.0  # immediate timeout
        coord._phase_start_time = time.monotonic() - 1.0
        coord._phase = "navigating"
        coord.check_timeouts()
        assert coord.phase == "aborting"

    def test_get_phase_returns_current(self):
        coord, _ = self._make()
        assert coord.get_phase() == "idle"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_task_coordinator.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'robot_decision.task_coordinator'"

- [ ] **Step 3: Write minimal implementation**

```python
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
    "idle":         {"navigating"},
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
        if timeout and (time.monotonic() - self._phase_start_time) > timeout:
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_task_coordinator.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/robot_decision/task_coordinator.py
git add robot-app/ros2_ws/src/robot_decision/tests/test_task_coordinator.py
git commit -m "feat(decision): add TaskCoordinator FSM for dual-arm loading tasks"
```
