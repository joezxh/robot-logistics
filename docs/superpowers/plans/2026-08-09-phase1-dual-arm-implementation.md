# Phase 1: Dual-Arm AGV Loading Robot — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement dual-arm coordinated control for the loading robot (AGV + dual arms + hug grasp), covering TaskCoordinator FSM, executors, safety interlocks, URDF extensions, simulation, and frontend visualization.

**Architecture:** Pure-Python TaskCoordinator FSM dispatches task-level commands to subsystem executors (BaseExecutor, ArmExecutor, HugController). SafetyMonitor provides independent interlock enforcement. All contracts (TaskCommandMsg, BaseStateMsg, HugStateMsg) already exist in robot_msgs/contracts.py — this plan builds the logic layer on top.

**Tech Stack:** Python 3.10+, ROS 2 (rclpy, std_msgs, geometry_msgs), MoveIt 2, Three.js, Vue 3, pytest

## Global Constraints

- All new `robot_decision` modules are **pure Python** (no `rclpy` imports) for unit-testability — only the integration node imports rclpy
- Contract dataclasses in `robot_msgs/contracts.py` are **already extended** (TaskCommandMsg, HugParamsMsg, BaseStateMsg, HugStateMsg) — do NOT re-create them
- `robot_gateway/bridge.py` already has `task_sink` parameter and `execute_task` routing — only `mqtt_bridge_node.py` needs wiring
- Schema files (`command.schema.json`, `state.schema.json`, `telemetry.schema.json`) and `robot_contracts/payloads.py` are **already extended** — skip creation
- Existing `motion_planner.py` and `moveit_client.py` in robot_decision are preserved; new modules complement them
- Target: **~50 new unit tests**, all passing alongside existing 205 tests

---

## File Structure

### New Files

| File | Responsibility |
|---|---|
| `robot_decision/robot_decision/task_coordinator.py` | Layered FSM: 9 action phases + ABORTING |
| `robot_decision/robot_decision/safety_monitor.py` | Safety interlocks, cmd_vel interception |
| `robot_decision/robot_decision/base_executor.py` | AGV waypoint following (cmd_vel + /odom) |
| `robot_decision/robot_decision/arm_executor.py` | MoveIt plan + FollowJointTrajectory for left/right/dual_arm |
| `robot_decision/robot_decision/hug_controller.py` | Dual-arm synchronized hug grasp |
| `robot_decision/robot_decision/task_coordinator_node.py` | ROS 2 integration node (rclpy entry point) |
| `robot_decision/config/task_coordinator.yaml` | Phase timeouts, speed defaults |
| `robot_decision/tests/test_task_coordinator.py` | FSM transition tests (~15) |
| `robot_decision/tests/test_safety_monitor.py` | Interlock rule tests (~8) |
| `robot_decision/tests/test_base_executor.py` | Waypoint + odom tests (~5) |
| `robot_decision/tests/test_hug_controller.py` | Hug state machine tests (~7) |
| `robot-app/ros2_ws/src/robot_base_hal/` | New ROS 2 package: diff-drive base URDF + ros2_control |
| `simulation/frontend/src/three/AgvBase.ts` | Procedural AGV chassis geometry |
| `simulation/frontend/src/three/LoaderRobot.ts` | Composite: chassis + dual arms + paddles |

### Modified Files

| File | Change |
|---|---|
| `robot_gateway/mqtt_bridge_node.py` | Add `task_sink` wiring + `~/task_command` publisher |
| `simulation/backend/services/runtime.py` | Add `loader-01` device, 14-joint support |
| `simulation/backend/services/motion_commander.py` | Task-level command mapping for loader |
| `simulation/backend/services/mqtt_bridge.py` | Wildcard topic matching fix |
| `simulation/frontend/src/three/WarehouseScene.vue` | LoaderRobot integration + TS fix |
| `robot_decision/setup.py` | New entry_points + config data_files |

---

### Task 1: TaskCoordinator FSM

**Files:**
- Create: `robot-app/ros2_ws/src/robot_decision/robot_decision/task_coordinator.py`
- Test: `robot-app/ros2_ws/src/robot_decision/tests/test_task_coordinator.py`

**Interfaces:**
- Consumes: `TaskCommandMsg` (from `robot_msgs.contracts`)
- Produces: `phase: str` property, `on_phase_change` callback, executor dispatch decisions

- [ ] **Step 1: Write failing tests for FSM transitions**

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

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_task_coordinator.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'robot_decision.task_coordinator'"

- [ ] **Step 3: Implement TaskCoordinator**

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

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_task_coordinator.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/robot_decision/task_coordinator.py
git add robot-app/ros2_ws/src/robot_decision/tests/test_task_coordinator.py
git commit -m "feat(decision): add TaskCoordinator FSM for dual-arm loading tasks"
```

---

### Task 2: SafetyMonitor

**Files:**
- Create: `robot-app/ros2_ws/src/robot_decision/robot_decision/safety_monitor.py`
- Test: `robot-app/ros2_ws/src/robot_decision/tests/test_safety_monitor.py`

**Interfaces:**
- Consumes: estop state, laser scan distance, arm/base motion state
- Produces: `is_safe() -> bool`, `intercept_cmd_vel(vx, wz) -> (vx, wz)`

- [ ] **Step 1: Write failing tests**

```python
"""Tests for SafetyMonitor — safety interlocks."""
import pytest
from robot_decision.safety_monitor import SafetyMonitor


class TestSafetyMonitor:
    def _make(self):
        return SafetyMonitor(safety_zone_radius=1.5, min_obstacle_distance=0.3)

    def test_initial_state_is_safe(self):
        mon = self._make()
        assert mon.is_safe() is True

    def test_estop_makes_unsafe(self):
        mon = self._make()
        mon.on_estop(True)
        assert mon.is_safe() is False

    def test_estop_release_restores_safe(self):
        mon = self._make()
        mon.on_estop(True)
        mon.on_estop(False)
        assert mon.is_safe() is True

    def test_laser_obstacle_too_close(self):
        mon = self._make()
        mon.on_scan(min_distance=0.2)
        assert mon.is_safe() is False

    def test_laser_obstacle_safe_distance(self):
        mon = self._make()
        mon.on_scan(min_distance=1.0)
        assert mon.is_safe() is True

    def test_arm_motion_blocks_base(self):
        mon = self._make()
        mon.set_base_motion_state(True)  # base moving
        mon.set_arm_motion_state(True)   # arm moving
        vx, wz = mon.intercept_cmd_vel(0.5, 0.1)
        assert vx == 0.0 and wz == 0.0

    def test_base_motion_allowed_when_arm_stopped(self):
        mon = self._make()
        mon.set_base_motion_state(True)
        mon.set_arm_motion_state(False)
        vx, wz = mon.intercept_cmd_vel(0.5, 0.1)
        assert vx == 0.5 and wz == 0.1

    def test_intercept_returns_zero_when_unsafe(self):
        mon = self._make()
        mon.on_estop(True)
        vx, wz = mon.intercept_cmd_vel(0.5, 0.1)
        assert vx == 0.0 and wz == 0.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_safety_monitor.py -v`
Expected: FAIL

- [ ] **Step 3: Implement SafetyMonitor**

```python
"""SafetyMonitor — independent safety interlocks.

Runs alongside the TaskCoordinator but has its own authority to halt
motion. Never goes through the coordinator — direct executor stop.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class SafetyMonitor:
    """Safety interlock monitor. Pure Python, no rclpy."""

    def __init__(
        self,
        *,
        safety_zone_radius: float = 1.5,
        min_obstacle_distance: float = 0.3,
    ) -> None:
        self._estop_active = False
        self._min_obstacle_distance = min_obstacle_distance
        self._safety_zone_radius = safety_zone_radius
        self._current_min_distance: float = float("inf")
        self._base_moving = False
        self._arm_moving = False

    def is_safe(self) -> bool:
        if self._estop_active:
            return False
        if self._current_min_distance < self._min_obstacle_distance:
            return False
        return True

    def on_estop(self, active: bool) -> None:
        self._estop_active = active
        if active:
            logger.warning("E-STOP activated")
        else:
            logger.info("E-STOP released")

    def on_scan(self, *, min_distance: float) -> None:
        self._current_min_distance = min_distance

    def set_base_motion_state(self, moving: bool) -> None:
        self._base_moving = moving

    def set_arm_motion_state(self, moving: bool) -> None:
        self._arm_moving = moving

    def intercept_cmd_vel(self, vx: float, wz: float) -> tuple[float, float]:
        if not self.is_safe():
            return 0.0, 0.0
        # Interlock: arm moving → base must stop
        if self._arm_moving and self._base_moving:
            logger.warning("safety: arm motion detected, forcing base stop")
            return 0.0, 0.0
        return vx, wz
```

- [ ] **Step 4: Run tests**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_safety_monitor.py -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/robot_decision/safety_monitor.py
git add robot-app/ros2_ws/src/robot_decision/tests/test_safety_monitor.py
git commit -m "feat(decision): add SafetyMonitor with interlock rules"
```

---

### Task 3: BaseExecutor + ArmExecutor + HugController

**Files:**
- Create: `robot-app/ros2_ws/src/robot_decision/robot_decision/base_executor.py`
- Create: `robot-app/ros2_ws/src/robot_decision/robot_decision/arm_executor.py`
- Create: `robot-app/ros2_ws/src/robot_decision/robot_decision/hug_controller.py`
- Test: `robot-app/ros2_ws/src/robot_decision/tests/test_base_executor.py`
- Test: `robot-app/ros2_ws/src/robot_decision/tests/test_hug_controller.py`

**Interfaces:**
- BaseExecutor: `execute(phase, params)`, `stop()`, `get_feedback() -> dict`
- ArmExecutor: `execute(phase, params)`, `stop()`
- HugController: `execute(phase, params)`, `stop()`, `get_state() -> dict`

- [ ] **Step 1: Write failing tests for HugController**

```python
"""Tests for HugController — dual-arm synchronized grasp."""
import pytest
from robot_decision.hug_controller import HugController


class TestHugController:
    def _make(self):
        return HugController(paddle_max_opening=0.4)

    def test_initial_state_is_open(self):
        hc = self._make()
        assert hc.get_state()["state"] == "open"

    def test_start_hug_transitions_to_closed(self):
        hc = self._make()
        hc.start_hug(pressure_target=50.0, approach_speed=0.3, close_speed=0.1)
        assert hc.get_state()["state"] == "closed"

    def test_hug_reaches_target_transitions_to_holding(self):
        hc = self._make()
        hc.start_hug(pressure_target=50.0, approach_speed=0.3, close_speed=0.1)
        # Simulate paddle closing to target
        hc.update(current_opening=0.05, target_opening=0.05)
        assert hc.get_state()["state"] == "holding"

    def test_release_transitions_to_open(self):
        hc = self._make()
        hc.start_hug(pressure_target=50.0, approach_speed=0.3, close_speed=0.1)
        hc.update(current_opening=0.05, target_opening=0.05)
        hc.release()
        assert hc.get_state()["state"] == "open"

    def test_release_completes_to_open(self):
        hc = self._make()
        hc.start_hug(pressure_target=50.0, approach_speed=0.3, close_speed=0.1)
        hc.update(current_opening=0.05, target_opening=0.05)
        hc.release()
        hc.update(current_opening=0.39, target_opening=0.4)
        assert hc.get_state()["state"] == "open"

    def test_execute_dispatches_start_hug(self):
        hc = self._make()
        hc.execute("hugging", {"hug_params": {"pressure_target": 60.0}})
        assert hc.get_state()["state"] == "closed"

    def test_stop_resets_to_open(self):
        hc = self._make()
        hc.start_hug(pressure_target=50.0, approach_speed=0.3, close_speed=0.1)
        hc.stop()
        assert hc.get_state()["state"] == "open"
```

- [ ] **Step 2: Write failing tests for BaseExecutor**

```python
"""Tests for BaseExecutor — AGV waypoint following."""
import pytest
from robot_decision.base_executor import BaseExecutor


class TestBaseExecutor:
    def _make(self):
        return BaseExecutor(linear_kp=0.8, angular_kp=1.2)

    def test_initial_feedback(self):
        be = self._make()
        fb = be.get_feedback()
        assert "velocity" in fb
        assert "odom" in fb

    def test_execute_waypoint_sets_target(self):
        be = self._make()
        be.execute("navigating", {"target_pose": {"x": 5.0, "y": 0.0, "yaw": 0.0}})
        assert be._target_x == 5.0

    def test_compute_cmd_vel_toward_target(self):
        be = self._make()
        be.execute("navigating", {"target_pose": {"x": 5.0, "y": 0.0, "yaw": 0.0}})
        be.update_odom(x=0.0, y=0.0, yaw=0.0)
        vx, wz = be.compute_cmd_vel()
        assert vx > 0  # should move forward toward x=5

    def test_stop_zeros_velocity(self):
        be = self._make()
        be.execute("navigating", {"target_pose": {"x": 5.0, "y": 0.0, "yaw": 0.0}})
        be.stop()
        vx, wz = be.compute_cmd_vel()
        assert vx == 0.0 and wz == 0.0
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_hug_controller.py tests/test_base_executor.py -v`
Expected: FAIL

- [ ] **Step 4: Implement HugController**

```python
"""HugController — dual-arm synchronized hug grasp."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

HUG_STATES = ("open", "closed", "holding")


class HugController:
    """Controls dual-arm hug grasp via paddle position thresholds."""

    def __init__(self, *, paddle_max_opening: float = 0.4) -> None:
        self._state = "open"
        self._pressure_target = 50.0
        self._approach_speed = 0.2
        self._close_speed = 0.05
        self._paddle_max_opening = paddle_max_opening
        self._target_opening = paddle_max_opening

    def get_state(self) -> dict[str, Any]:
        return {"state": self._state, "pressure_target": self._pressure_target}

    def start_hug(self, *, pressure_target: float = 50.0,
                  approach_speed: float = 0.2, close_speed: float = 0.05) -> None:
        self._pressure_target = pressure_target
        self._approach_speed = approach_speed
        self._close_speed = close_speed
        # Map pressure_target to paddle opening (higher pressure = tighter grip)
        self._target_opening = max(0.01, self._paddle_max_opening * (1.0 - pressure_target / 100.0))
        self._state = "closed"
        logger.info("hug started: target_opening=%.3f", self._target_opening)

    def release(self) -> None:
        self._target_opening = self._paddle_max_opening
        self._state = "open"
        logger.info("hug release started")

    def update(self, *, current_opening: float, target_opening: float | None = None) -> None:
        if target_opening is not None:
            self._target_opening = target_opening
        tolerance = 0.02
        if self._state == "closed" and current_opening <= self._target_opening + tolerance:
            self._state = "holding"
            logger.info("hug holding: opening=%.3f", current_opening)
        elif self._state == "open" and current_opening >= self._target_opening - tolerance:
            # Already open, no state change needed
            pass

    def execute(self, phase: str, params: dict[str, Any]) -> None:
        hug_params = params.get("hug_params", {})
        if phase == "hugging":
            self.start_hug(**{k: v for k, v in hug_params.items()
                             if k in ("pressure_target", "approach_speed", "close_speed")})

    def stop(self) -> None:
        self._state = "open"
        self._target_opening = self._paddle_max_opening
```

- [ ] **Step 5: Implement BaseExecutor**

```python
"""BaseExecutor — AGV waypoint following via cmd_vel."""
from __future__ import annotations

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)


class BaseExecutor:
    """Simple PID waypoint follower for differential-drive base."""

    def __init__(self, *, linear_kp: float = 0.8, angular_kp: float = 1.2,
                 max_linear_speed: float = 0.5, max_angular_speed: float = 1.0) -> None:
        self._linear_kp = linear_kp
        self._angular_kp = angular_kp
        self._max_linear_speed = max_linear_speed
        self._max_angular_speed = max_angular_speed
        self._target_x = 0.0
        self._target_y = 0.0
        self._target_yaw = 0.0
        self._odom_x = 0.0
        self._odom_y = 0.0
        self._odom_yaw = 0.0
        self._active = False

    def get_feedback(self) -> dict[str, Any]:
        return {
            "velocity": [0.0, 0.0],
            "odom": {"x": self._odom_x, "y": self._odom_y, "yaw": self._odom_yaw},
        }

    def update_odom(self, *, x: float, y: float, yaw: float) -> None:
        self._odom_x = x
        self._odom_y = y
        self._odom_yaw = yaw

    def execute(self, phase: str, params: dict[str, Any]) -> None:
        pose = params.get("target_pose", {})
        self._target_x = float(pose.get("x", 0.0))
        self._target_y = float(pose.get("y", 0.0))
        self._target_yaw = float(pose.get("yaw", 0.0))
        self._active = True
        logger.info("base navigating to (%.2f, %.2f, %.2f)",
                     self._target_x, self._target_y, self._target_yaw)

    def compute_cmd_vel(self) -> tuple[float, float]:
        if not self._active:
            return 0.0, 0.0
        dx = self._target_x - self._odom_x
        dy = self._target_y - self._odom_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < 0.05:
            self._active = False
            return 0.0, 0.0
        target_bearing = math.atan2(dy, dx)
        angle_error = target_bearing - self._odom_yaw
        vx = min(self._max_linear_speed, self._linear_kp * distance)
        wz = max(-self._max_angular_speed,
                 min(self._max_angular_speed, self._angular_kp * angle_error))
        return vx, wz

    def stop(self) -> None:
        self._active = False
```

- [ ] **Step 6: Implement ArmExecutor (thin wrapper)**

```python
"""ArmExecutor — MoveIt plan + FollowJointTrajectory for named groups."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ArmExecutor:
    """Wraps MoveItClient for left/right/dual_arm planning groups."""

    def __init__(self) -> None:
        self._active = False
        self._group_name: str = ""

    def execute(self, phase: str, params: dict[str, Any]) -> None:
        group = params.get("group", "dual_arm")
        self._group_name = group
        self._active = True
        logger.info("arm executing phase=%s group=%s", phase, group)

    def stop(self) -> None:
        self._active = False
        logger.info("arm stopped")
```

- [ ] **Step 7: Run tests**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_hug_controller.py tests/test_base_executor.py -v`
Expected: 11 passed

- [ ] **Step 8: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/robot_decision/base_executor.py
git add robot-app/ros2_ws/src/robot_decision/robot_decision/arm_executor.py
git add robot-app/ros2_ws/src/robot_decision/robot_decision/hug_controller.py
git add robot-app/ros2_ws/src/robot_decision/tests/test_base_executor.py
git add robot-app/ros2_ws/src/robot_decision/tests/test_hug_controller.py
git commit -m "feat(decision): add BaseExecutor, ArmExecutor, HugController"
```

---

### Task 4: TaskCoordinatorNode + Config

**Files:**
- Create: `robot-app/ros2_ws/src/robot_decision/robot_decision/task_coordinator_node.py`
- Create: `robot-app/ros2_ws/src/robot_decision/config/task_coordinator.yaml`
- Modify: `robot-app/ros2_ws/src/robot_decision/setup.py`

**Interfaces:**
- Consumes: `~/task_command` (String, JSON TaskCommandMsg)
- Produces: `~/robot_state` (String, JSON RobotStateMsg with ctrl.phase)

- [ ] **Step 1: Create task_coordinator.yaml**

```yaml
task_coordinator:
  ros__parameters:
    phase_timeouts:
      navigating: 60.0
      docking: 30.0
      approaching: 20.0
      hugging: 15.0
      lifting: 15.0
      transporting: 60.0
      placing: 15.0
      retreating: 20.0
    safety_zone_radius: 1.5
    min_obstacle_distance: 0.3
    max_linear_speed: 0.5
    max_angular_speed: 1.0
```

- [ ] **Step 2: Create task_coordinator_node.py**

```python
"""ROS 2 node wrapping TaskCoordinator for dual-arm loading tasks.

Subscribes to ~/task_command (String JSON), dispatches to executors,
publishes state on ~/robot_state.
"""
from __future__ import annotations

import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from robot_decision.task_coordinator import TaskCoordinator
from robot_decision.safety_monitor import SafetyMonitor
from robot_decision.base_executor import BaseExecutor
from robot_decision.arm_executor import ArmExecutor
from robot_decision.hug_controller import HugController


class TaskCoordinatorNode(Node):
    def __init__(self) -> None:
        super().__init__("task_coordinator_node")

        self.declare_parameter("safety_zone_radius", 1.5)
        self.declare_parameter("min_obstacle_distance", 0.3)
        self.declare_parameter("max_linear_speed", 0.5)
        self.declare_parameter("max_angular_speed", 1.0)

        self._coordinator = TaskCoordinator(
            on_phase_change=self._on_phase_change,
        )
        self._safety = SafetyMonitor(
            safety_zone_radius=float(self.get_parameter("safety_zone_radius").value),
            min_obstacle_distance=float(self.get_parameter("min_obstacle_distance").value),
        )
        self._base = BaseExecutor(
            max_linear_speed=float(self.get_parameter("max_linear_speed").value),
            max_angular_speed=float(self.get_parameter("max_angular_speed").value),
        )
        self._arm = ArmExecutor()
        self._hug = HugController()

        self._coordinator.set_executor("base", self._base)
        self._coordinator.set_executor("arm", self._arm)
        self._coordinator.set_executor("hug", self._hug)

        self._task_cmd_sub = self.create_subscription(
            String, "~/task_command", self._on_task_command, 10
        )
        self._state_pub = self.create_publisher(String, "~/robot_state", 10)

        self._timer = self.create_timer(0.1, self._tick)
        self.get_logger().info("TaskCoordinatorNode ready")

    def _on_task_command(self, msg: String) -> None:
        try:
            data = json.loads(msg.data)
            self._coordinator.on_task_command(
                task_type=data["task_type"],
                parameters=data.get("parameters", {}),
            )
        except Exception:
            self.get_logger().exception("failed to process task command")

    def _on_phase_change(self, phase: str) -> None:
        self._publish_state()

    def _tick(self) -> None:
        self._coordinator.check_timeouts()
        self._publish_state()

    def _publish_state(self) -> None:
        state = {
            "ctrl": {
                "mode": "task",
                "phase": self._coordinator.get_phase(),
            },
            "hug": self._hug.get_state(),
            "base": self._base.get_feedback(),
        }
        msg = String()
        msg.data = json.dumps(state)
        self._state_pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TaskCoordinatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Update setup.py**

Add to `setup.py` entry_points and data_files:

```python
# In setup.py, update:
data_files=[
    ("share/ament_index/resource_index/packages", ["resource/" + PACKAGE_NAME]),
    ("share/" + PACKAGE_NAME, ["package.xml"]),
    ("share/" + PACKAGE_NAME + "/config", glob("config/*.yaml")),
],
entry_points={
    "console_scripts": [
        "motion_planner_node = robot_decision.motion_planner:main",
        "task_coordinator_node = robot_decision.task_coordinator_node:main",
    ],
},
```

- [ ] **Step 4: Run all robot_decision tests**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/ -v`
Expected: All existing + new tests pass

- [ ] **Step 5: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/robot_decision/task_coordinator_node.py
git add robot-app/ros2_ws/src/robot_decision/config/task_coordinator.yaml
git add robot-app/ros2_ws/src/robot_decision/setup.py
git commit -m "feat(decision): add TaskCoordinatorNode + config + setup entry point"
```

---

### Task 5: Gateway task_sink Wiring

**Files:**
- Modify: `robot-app/ros2_ws/src/robot_gateway/robot_gateway/mqtt_bridge_node.py`

**Interfaces:**
- Consumes: `task_sink` from `MqttBridge` (already exists in bridge.py)
- Produces: `~/task_command` (String, JSON TaskCommandMsg)

- [ ] **Step 1: Add task_command publisher and task_sink to mqtt_bridge_node.py**

In `mqtt_bridge_node.py`, add:
1. A `_task_cmd_pub` publisher for `~/task_command`
2. A `_on_task_command` method that serializes TaskCommandMsg to JSON
3. Pass `task_sink=self._on_task_command` to `MqttBridge()`

```python
# Add after _alert_sub creation (around line 87):
self._task_cmd_pub = self.create_publisher(String, "~/task_command", 10)

# Modify MqttBridge construction (around line 64-70) to add task_sink:
self._bridge = MqttBridge(
    self._link,
    device_id=device_id,
    motion_sink=self._on_motion_command,
    estop_sink=self._on_estop_command,
    task_sink=self._on_task_command,
    topic_prefix=topic_prefix,
)

# Add new method:
def _on_task_command(self, msg) -> None:
    """Forward a task command to robot_decision via ~/task_command."""
    payload = {
        "command_id": msg.command_id,
        "task_type": msg.task_type,
        "parameters": msg.parameters,
        "speed_scale": msg.speed_scale,
        "group": msg.group,
    }
    ros_msg = String()
    ros_msg.data = json.dumps(payload)
    self._task_cmd_pub.publish(ros_msg)
    self.get_logger().info(
        f"forwarded task_command {msg.task_type} (id={msg.command_id}) to ~/task_command"
    )
```

- [ ] **Step 2: Run gateway tests**

Run: `cd robot-app/ros2_ws/src/robot_gateway && python -m pytest tests/ -v`
Expected: 44 passed (no regression)

- [ ] **Step 3: Commit**

```bash
git add robot-app/ros2_ws/src/robot_gateway/robot_gateway/mqtt_bridge_node.py
git commit -m "feat(gateway): wire task_sink to ~/task_command for TaskCoordinator"
```

---

### Task 6: robot_base_hal Package

**Files:**
- Create: `robot-app/ros2_ws/src/robot_base_hal/package.xml`
- Create: `robot-app/ros2_ws/src/robot_base_hal/setup.py`
- Create: `robot-app/ros2_ws/src/robot_base_hal/setup.cfg`
- Create: `robot-app/ros2_ws/src/robot_base_hal/resource/robot_base_hal`
- Create: `robot-app/ros2_ws/src/robot_base_hal/robot_base_hal/__init__.py`
- Create: `robot-app/ros2_ws/src/robot_base_hal/urdf/base.ros2_control.xacro`
- Create: `robot-app/ros2_ws/src/robot_base_hal/config/diff_drive.yaml`

- [ ] **Step 1: Create package scaffolding**

`package.xml`:
```xml
<?xml version="1.0"?>
<package format="3">
  <name>robot_base_hal</name>
  <version>0.1.0</version>
  <description>Differential-drive base HAL for loading robot AGV</description>
  <maintainer email="joezxh@qq.com">joezxh</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_python</buildtool_depend>
  <exec_depend>ros2_control</exec_depend>
  <exec_depend>diff_drive_controller</exec_depend>
</package>
```

`setup.py`:
```python
from glob import glob
from setuptools import setup

PACKAGE_NAME = "robot_base_hal"

setup(
    name=PACKAGE_NAME,
    version="0.1.0",
    packages=[PACKAGE_NAME],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + PACKAGE_NAME]),
        ("share/" + PACKAGE_NAME, ["package.xml"]),
        ("share/" + PACKAGE_NAME + "/urdf", glob("urdf/*.xacro")),
        ("share/" + PACKAGE_NAME + "/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
)
```

`setup.cfg`:
```ini
[develop]
script_dir=$base/lib/robot_base_hal
[install]
install_scripts=$base/lib/robot_base_hal
```

`robot_base_hal/__init__.py`: empty file

`resource/robot_base_hal`: empty file

- [ ] **Step 2: Create base.ros2_control.xacro**

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:macro name="base_ros2_control" params="name use_gazebo">
    <ros2_control name="${name}" type="system">
      <xacro:if value="${use_gazebo}">
        <hardware>
          <plugin>gz_ros2_control/GzSystem</plugin>
        </hardware>
      </xacro:if>
      <xacro:unless value="${use_gazebo}">
        <hardware>
          <plugin>mock_components/GenericSystem</plugin>
          <param name="mock_sensor_commands">true</param>
        </hardware>
      </xacro:unless>

      <joint name="left_wheel">
        <command_interface name="velocity">
          <param name="min">-10.0</param>
          <param name="max">10.0</param>
        </command_interface>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
      </joint>
      <joint name="right_wheel">
        <command_interface name="velocity">
          <param name="min">-10.0</param>
          <param name="max">10.0</param>
        </command_interface>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
      </joint>
    </ros2_control>
  </xacro:macro>
</robot>
```

- [ ] **Step 3: Create diff_drive.yaml**

```yaml
controller_manager:
  ros__parameters:
    update_rate: 50
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster
    diff_drive_controller:
      type: diff_drive_controller/DiffDriveController

diff_drive_controller:
  ros__parameters:
    left_wheel_names: ["left_wheel"]
    right_wheel_names: ["right_wheel"]
    wheel_separation: 0.4
    wheel_radius: 0.075
    publish_rate: 50.0
    use_stamped_vel: false
```

- [ ] **Step 4: Commit**

```bash
git add robot-app/ros2_ws/src/robot_base_hal/
git commit -m "feat(base_hal): add robot_base_hal package with diff-drive URDF"
```

---

### Task 7: robot_arm_hal Dual-Arm Extension

**Files:**
- Create: `robot-app/ros2_ws/src/robot_dual_arm_hal/urdf/dual_arm.ros2_control.xacro`

**Interfaces:**
- Uses existing `arm_hal.ros2_control.xacro` macro `arm_hal_ros2_control`
- Instantiates with `arm_id=left` and `arm_id=right`

- [ ] **Step 1: Create dual_arm.ros2_control.xacro**

```xml
<?xml version="1.0"?>
<!--
  dual_arm.ros2_control.xacro
  Phase 1: instantiates the arm_hal macro twice for left/right arms
  on the loading robot AGV.
-->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:include filename="$(find robot_arm_hal)/urdf/arm_hal.ros2_control.xacro"/>

  <!-- Left arm -->
  <xacro:arm_hal_ros2_control
    name="left_arm_ros2_control"
    use_fake_hardware="true"
    use_gazebo="false"
    arm_id="left"/>

  <!-- Right arm -->
  <xacro:arm_hal_ros2_control
    name="right_arm_ros2_control"
    use_fake_hardware="true"
    use_gazebo="false"
    arm_id="right"/>
</robot>
```

- [ ] **Step 2: Commit**

```bash
git add robot-app/ros2_ws/src/robot_dual_arm_hal/urdf/dual_arm.ros2_control.xacro
git commit -m "feat(arm_hal): add dual-arm ros2_control xacro instantiation"
```

---

### Task 8: Simulation Backend Extension

**Files:**
- Modify: `simulation/backend/services/runtime.py`
- Modify: `simulation/backend/services/motion_commander.py`
- Modify: `simulation/backend/services/mqtt_bridge.py`
- Test: `simulation/backend/tests/test_mqtt_bridge.py` (add wildcard test)

- [ ] **Step 1: Fix wildcard topic matching in mqtt_bridge.py**

In `_on_message`, replace exact topic lookup with wildcard matching:

```python
def _on_message(self, client: Any, userdata: Any, msg: Any) -> None:
    # Try exact match first, then wildcard
    cb = self._state_callbacks.get(msg.topic)
    if cb is None:
        cb = self._match_wildcard(msg.topic)
    if cb is not None:
        try:
            payload = json.loads(msg.payload.decode())
            cb(payload)
        except Exception:
            logger.exception("state callback failed for %s", msg.topic)

def _match_wildcard(self, topic: str):
    """Match MQTT wildcard subscriptions (+, #)."""
    for pattern, cb in self._state_callbacks.items():
        if "#" in pattern or "+" in pattern:
            if self._topic_matches(pattern, topic):
                return cb
    return None

@staticmethod
def _topic_matches(pattern: str, topic: str) -> bool:
    pattern_parts = pattern.split("/")
    topic_parts = topic.split("/")
    for i, pp in enumerate(pattern_parts):
        if pp == "#":
            return True
        if i >= len(topic_parts):
            return False
        if pp != "+" and pp != topic_parts[i]:
            return False
    return len(pattern_parts) == len(topic_parts)
```

- [ ] **Step 2: Add wildcard matching test**

```python
def test_wildcard_topic_matching(self):
    bridge = self._make_bridge()
    received = []
    bridge.subscribe_state("rcs/+/state", lambda msg: received.append(msg))
    fake_msg = MagicMock()
    fake_msg.topic = "rcs/loader-01/state"
    fake_msg.payload = json.dumps({"device_id": "loader-01"}).encode()
    bridge._on_message(None, None, fake_msg)
    assert len(received) == 1
    assert received[0]["device_id"] == "loader-01"
```

- [ ] **Step 3: Add loader-01 device to runtime.py**

In `Runtime.__init__()`, after `self._seed_tasks()`:

```python
# Register loader device for Phase 1 dual-arm AGV
self.devices.register_device("loader-01", device_type="loading_robot", num_joints=14)
```

Note: Check if `DeviceManager.register_device()` supports `device_type` and `num_joints` parameters. If not, extend the DeviceManager or add a simple device record.

- [ ] **Step 4: Extend motion_commander.py for task-level commands**

Add a method to handle `execute_task` commands:

```python
def on_task_command(self, task_type: str, device_id: str, parameters: dict) -> dict[str, Any] | None:
    command_id = f"cmd-{uuid.uuid4().hex[:8]}"
    return {
        "command_id": command_id,
        "type": "execute_task",
        "task_type": task_type,
        "parameters": parameters,
        "speed_scale": 1.0,
    }
```

- [ ] **Step 5: Run simulation tests**

Run: `cd simulation/backend && python -m pytest tests/ -v`
Expected: All pass (existing 68 + new tests)

- [ ] **Step 6: Commit**

```bash
git add simulation/backend/services/mqtt_bridge.py
git add simulation/backend/services/runtime.py
git add simulation/backend/services/motion_commander.py
git add simulation/backend/tests/test_mqtt_bridge.py
git commit -m "feat(sim): extend backend for loader-01 + fix wildcard topics"
```

---

### Task 9: Frontend LoaderRobot Visualization

**Files:**
- Create: `simulation/frontend/src/three/AgvBase.ts`
- Create: `simulation/frontend/src/three/LoaderRobot.ts`
- Modify: `simulation/frontend/src/three/WarehouseScene.vue`

- [ ] **Step 1: Create AgvBase.ts**

```typescript
/**
 * Procedural AGV chassis: flat box + two drive wheels.
 */
import * as THREE from 'three'

const CHASSIS = { width: 0.8, height: 0.15, depth: 0.6 }
const WHEEL = { radius: 0.075, width: 0.04 }

export class AgvBase {
  public group: THREE.Group
  private wheels: THREE.Mesh[] = []

  constructor() {
    this.group = new THREE.Group()
    this.group.name = 'AgvBase'
    this.build()
  }

  private build() {
    const chassisMat = new THREE.MeshStandardMaterial({ color: 0x4a5568, roughness: 0.6 })
    const body = new THREE.Mesh(
      new THREE.BoxGeometry(CHASSIS.width, CHASSIS.height, CHASSIS.depth),
      chassisMat
    )
    body.position.y = WHEEL.radius + CHASSIS.height / 2
    this.group.add(body)

    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x2d3748 })
    const wheelGeom = new THREE.CylinderGeometry(WHEEL.radius, WHEEL.radius, WHEEL.width, 16)
    for (const side of [-1, 1]) {
      const wheel = new THREE.Mesh(wheelGeom, wheelMat)
      wheel.rotation.x = Math.PI / 2
      wheel.position.set(0, WHEEL.radius, side * (CHASSIS.depth / 2 + WHEEL.width / 2))
      this.group.add(wheel)
      this.wheels.push(wheel)
    }
  }

  addToScene(scene: THREE.Scene, position?: THREE.Vector3) {
    if (position) this.group.position.copy(position)
    scene.add(this.group)
  }
}
```

- [ ] **Step 2: Create LoaderRobot.ts**

```typescript
/**
 * Composite loader robot: AGV base + dual arms + hug paddles.
 */
import * as THREE from 'three'
import { RobotArm } from './RobotArm'
import { AgvBase } from './AgvBase'

export class LoaderRobot {
  public group: THREE.Group
  public base: AgvBase
  public leftArm: RobotArm
  public rightArm: RobotArm
  private paddles: THREE.Mesh[] = []

  constructor() {
    this.group = new THREE.Group()
    this.group.name = 'LoaderRobot'
    this.base = new AgvBase()
    this.leftArm = new RobotArm()
    this.rightArm = new RobotArm()
    this.build()
  }

  private build() {
    this.base.addToScene(this.group, new THREE.Vector3(0, 0, 0))
    this.group.add(this.base.group)

    // Position arms on left/right sides of chassis
    this.leftArm.addToScene(this.group, new THREE.Vector3(-0.25, 0.2, 0))
    this.rightArm.addToScene(this.group, new THREE.Vector3(0.25, 0.2, 0))

    // Hug paddles (prismatic joints)
    const paddleMat = new THREE.MeshStandardMaterial({ color: 0xed8936 })
    const paddleGeom = new THREE.BoxGeometry(0.02, 0.3, 0.15)
    for (const side of [-1, 1]) {
      const paddle = new THREE.Mesh(paddleGeom, paddleMat)
      paddle.position.set(side * 0.35, 0.35, 0)
      this.group.add(paddle)
      this.paddles.push(paddle)
    }
  }

  setJointPositions(positions: number[]) {
    // Split 14 joints: base(0) + left_arm(1-6) + right_arm(7-12) + paddles(13)
    if (positions.length >= 7) {
      this.leftArm.setJointPositions(positions.slice(1, 7))
    }
    if (positions.length >= 13) {
      this.rightArm.setJointPositions(positions.slice(7, 13))
    }
  }

  update(dt: number) {
    this.leftArm.update(dt)
    this.rightArm.update(dt)
  }

  addToScene(scene: THREE.Scene, position?: THREE.Vector3) {
    if (position) this.group.position.copy(position)
    scene.add(this.group)
  }
}
```

- [ ] **Step 3: Modify WarehouseScene.vue**

Replace the single `RobotArm` with `LoaderRobot`:

```typescript
// Change import
import { LoaderRobot } from './LoaderRobot'

// Change variable
let loaderRobot: LoaderRobot | undefined

// In init(), replace robotArm creation:
loaderRobot = new LoaderRobot()
loaderRobot.addToScene(scene, new THREE.Vector3(-6, 0, 5))

// SSE subscription — update loader robot
jointEventSource = new EventSource('/api/devices/loader-01/joints')
jointEventSource.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data)
    if (data.positions && loaderRobot) {
      loaderRobot.setJointPositions(data.positions)
    }
  } catch { /* ignore */ }
}

// In animate(), replace robotArm.update:
if (loaderRobot) loaderRobot.update(0.016 * speed.value)

// Fix TS window narrowing (line ~119):
// Change: window.addEventListener('resize', onResize)
// To: (window as Window).addEventListener('resize', onResize)

// In onUnmounted():
// Change: jointEventSource?.close()  (keep as is)
```

- [ ] **Step 4: Commit**

```bash
git add simulation/frontend/src/three/AgvBase.ts
git add simulation/frontend/src/three/LoaderRobot.ts
git add simulation/frontend/src/three/WarehouseScene.vue
git commit -m "feat(frontend): add LoaderRobot with dual arms + AGV base"
```

---

### Task 10: Integration Verification

**Files:** No new files — run all test suites

- [ ] **Step 1: Run simulation backend tests**

Run: `cd simulation/backend && python -m pytest tests/ -v`
Expected: All pass (68+ tests)

- [ ] **Step 2: Run robot_decision tests**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/ -v`
Expected: All pass (~30 tests)

- [ ] **Step 3: Run robot_gateway tests**

Run: `cd robot-app/ros2_ws/src/robot_gateway && python -m pytest tests/ -v`
Expected: 44 passed (no regression)

- [ ] **Step 4: Run RCS tests**

Run: `cd rcs && python -m pytest tests/ -v`
Expected: 85 passed (no regression)

- [ ] **Step 5: Update progress.md**

Update `.superpowers/sdd/progress.md` with all task results.

- [ ] **Step 6: Final commit**

```bash
git add .superpowers/sdd/progress.md
git commit -m "chore: update progress ledger — Phase 1 complete"
```
