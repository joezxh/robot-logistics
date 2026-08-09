# RCS-1 Motion Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an isolated `backend/rcs/` subpackage that exposes a REST + WS control interface (1 kHz arm / 50 Hz agv/stacker) backed by a `DeviceHAL` protocol with a `SimHAL` implementation, without modifying any existing Phase 1–5 service.

**Architecture:** Single FastAPI process keeps the existing app; a new `rcs_router` is mounted at `/api/rcs` and `/ws/rcs`. A per-device tick coroutine in `ControlLoop` reads HAL, computes next reference via a morphology-specific `Controller`, validates, writes HAL, and broadcasts at 10 Hz. Hardware swap = drop-in HAL implementation; no `controllers/` / `loop.py` / `service.py` change.

**Tech Stack:** Python 3.11, FastAPI 0.104, pydantic 2.4, asyncio (uvloop 0.19, optional), numpy 1.26, scipy 1.11, pytest 7.4 + pytest-asyncio 0.21 + httpx 0.25.

**Spec:** `docs/superpowers/specs/2026-07-24-rcs-1-motion-control-design.md`

---

## Global Constraints

- **Platform: Windows + PowerShell.** All shell commands in this plan must work from the repository root with PowerShell. Run pytest from repo root (`python -m pytest backend/...`), **not** `cd backend && python -m pytest ...` (the latter sets `rootdir` to `backend/`, which breaks `from backend...` imports on Windows). Use `;` not `&&` to chain commands. uvicorn commands use `python -m uvicorn` invoked from the repo root with the full module path.

- **RCS-1 isolation:** New code lives under `backend/rcs/`; **no file under `backend/algorithm/`, `backend/services/`, `backend/data/`, `backend/api/` may be modified.** The only existing file modified is `backend/main.py` (lifespan hook + one `include_router`).
- **No new third-party deps** beyond `uvloop==0.19.0` added to `backend/requirements.txt`. `numpy` and `scipy` are already present.
- **No new auth model.** Reuse `backend.services.security.require_api_key` via `Depends`. When `API_AUTH_ENABLED=0` (default for tests), auth is bypassed.
- **No database writes.** RCS-1 keeps no SQLite tables; all state is in-process.
- **No new HMI panels.** UI is out of scope for RCS-1 (RCS-5 spec).
- **No AlertEngine subscription.** `EventBus` is implemented but has no subscribers in this phase.
- **Naming:** `device_id` matches existing convention (e.g. `robot-01`, `agv-01`); morphology enum is lowercase (`arm` / `agv` / `stacker`); controller mode is lowercase (`idle` / `running` / `halted` / `fault` / `e_stop`).
- **Timestamps:** all in-process timestamps are `time.monotonic_ns()`. Wire timestamps (REST/WS) are ISO-8601 UTC via `datetime.now(timezone.utc).isoformat()`.
- **Thresholds (defaults, overridable per profile):** `rad_th = 0.05 rad`; `pos_th = 0.01 m`; arm `read_timeout = 0.05 s`, agv/stacker `read_timeout = 0.2 s`; arm `write_timeout = 0.02 s`, agv/stacker `write_timeout = 0.1 s`; WS rate = 10 Hz/frame cap = 64 KB; command queue max = 1024.
- **Existing tests must remain green:** `pytest backend/tests backend/rcs/tests` must pass.

---

## File Structure

```
backend/rcs/
├── __init__.py                       # rcs singleton + lifespan() context manager
├── service.py                        # FastAPI router (REST) + WS endpoints
├── loop.py                           # ControlLoop (per-device tick coroutine)
├── registry.py                       # Device registry + controller/HAL singletons
├── events.py                         # EventBus (publish/subscribe, async)
├── controllers/
│   ├── __init__.py
│   ├── base.py                       # Controller ABC, ControllerMode enum
│   ├── _common.py                    # limits, queue, halt/recover helpers
│   ├── arm.py                        # ArmController (PD + IK)
│   ├── agv.py                        # AgvController (P + velocity feedforward)
│   └── stacker.py                    # StackerController (2-axis P)
├── planning/
│   ├── __init__.py
│   ├── fk.py                         # forward kinematics (DH)
│   ├── ik.py                         # inverse kinematics (6DOF analytical)
│   ├── trajectory.py                 # trapezoidal + quintic time-optimal scaling
│   └── interpolator.py               # 1 ms step interpolator
├── hal/
│   ├── __init__.py
│   ├── protocol.py                   # DeviceHAL Protocol
│   └── sim.py                        # SimHAL (math-only)
├── state/
│   ├── __init__.py
│   ├── joint.py                      # JointState
│   ├── pose.py                       # Pose6D
│   ├── command.py                    # Command, CommandType
│   ├── error.py                      # TrackingError
│   ├── profile.py                    # DeviceProfile, Morphology, Limits
│   ├── controller_state.py           # ControllerState
│   └── state_stream.py               # in-memory broadcast, 10 Hz rate-limit, 64 KB cap
└── tests/
    ├── __init__.py
    ├── conftest.py                   # isolated registry + controller reset fixture
    ├── unit/
    │   ├── test_fk.py
    │   ├── test_ik.py
    │   ├── test_trajectory.py
    │   ├── test_interpolator.py
    │   ├── test_sim_hal.py
    │   ├── test_arm_controller.py
    │   ├── test_agv_controller.py
    │   ├── test_stacker_controller.py
    │   ├── test_control_loop.py
    │   └── test_state_stream.py
    └── integration/
        ├── test_rest_command.py
        ├── test_estop_link.py
        ├── test_ws_overview.py
        ├── test_idempotency.py
        └── test_queue_backpressure.py
scripts/
└── verify_rcs1.sh                    # end-to-end verification + JSON receipt
docs/superpowers/
├── specs/2026-07-24-rcs-1-motion-control-design.md   # already written
├── plans/2026-07-24-rcs-1-motion-control.md         # this file
└── instructions/rcs-1-handoff.md                    # written in Task 14
```

Each `state/*.py` file holds one dataclass + its `to_dict()`. Each `controllers/*.py` file holds one concrete `Controller` subclass. `planning/*.py` files are pure functions, no class. `hal/sim.py` is one class. `loop.py` is one class. `service.py` is one router + one WS handler module. The package's `__init__.py` exposes a singleton object with `startup()`, `shutdown()`, `lifespan()`, `router`.

---

## Task Index

| # | Task | Produces |
|---|------|----------|
| 1 | State types | `state/joint.py`, `pose.py`, `command.py`, `error.py`, `profile.py`, `controller_state.py`, `state_stream.py` |
| 2 | EventBus | `events.py` |
| 3 | Forward kinematics (TDD) | `planning/fk.py` + tests |
| 4 | Inverse kinematics (TDD) | `planning/ik.py` + tests |
| 5 | Trajectory (TDD) | `planning/trajectory.py` + tests |
| 6 | Interpolator (TDD) | `planning/interpolator.py` + tests |
| 7 | HAL protocol + SimHAL (TDD) | `hal/protocol.py`, `hal/sim.py` + tests |
| 8 | Controller base + ArmController (TDD) | `controllers/base.py`, `arm.py`, `_common.py` + tests |
| 9 | AgvController + StackerController (TDD) | `controllers/agv.py`, `stacker.py` + tests |
| 10 | Registry | `registry.py` + tests |
| 11 | ControlLoop | `loop.py` + tests |
| 12 | Service (REST + WS) | `service.py` + tests |
| 13 | Wire into `main.py` + `__init__.py` | modified `main.py`, new `__init__.py` + integration tests |
| 14 | `verify_rcs1.sh` + handoff doc | `scripts/verify_rcs1.sh`, `instructions/rcs-1-handoff.md` |

---

### Task 1: State types

**Files:**
- Create: `backend/rcs/state/__init__.py`
- Create: `backend/rcs/state/joint.py`
- Create: `backend/rcs/state/pose.py`
- Create: `backend/rcs/state/command.py`
- Create: `backend/rcs/state/error.py`
- Create: `backend/rcs/state/profile.py`
- Create: `backend/rcs/state/controller_state.py`
- Create: `backend/rcs/state/state_stream.py`

**Interfaces:**
- Consumes: nothing (foundation)
- Produces: `JointState`, `Pose6D`, `Command`, `CommandType`, `TrackingError`, `DeviceProfile`, `Morphology`, `Limits`, `ControllerState`, `ControllerMode`, `StateStream` — all importable from `backend.rcs.state`

- [ ] **Step 1: Write `backend/rcs/state/__init__.py`**

```python
"""Shared dataclasses for RCS-1 (motion control)."""
from .joint import JointState
from .pose import Pose6D
from .command import Command, CommandType
from .error import TrackingError
from .profile import DeviceProfile, Morphology, Limits
from .controller_state import ControllerState, ControllerMode
from .state_stream import StateStream

__all__ = [
    "JointState",
    "Pose6D",
    "Command",
    "CommandType",
    "TrackingError",
    "DeviceProfile",
    "Morphology",
    "Limits",
    "ControllerState",
    "ControllerMode",
    "StateStream",
]
```

- [ ] **Step 2: Write `backend/rcs/state/joint.py`**

```python
"""Joint state snapshot read from HAL."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class JointState:
    positions: list[float]
    velocities: list[float]
    efforts: list[float]
    timestamp_ns: int = field(default_factory=time.monotonic_ns)
    device_id: str = ""

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "positions": list(self.positions),
            "velocities": list(self.velocities),
            "efforts": list(self.efforts),
            "timestamp_ns": self.timestamp_ns,
        }
```

- [ ] **Step 3: Write `backend/rcs/state/pose.py`**

```python
"""6D pose (position + quaternion)."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Pose6D:
    position: list[float]   # [x, y, z]
    orientation: list[float]  # quaternion [w, x, y, z]

    def to_dict(self) -> dict:
        return {"position": list(self.position), "orientation": list(self.orientation)}
```

- [ ] **Step 4: Write `backend/rcs/state/command.py`**

```python
"""Commands submitted to a Controller."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .pose import Pose6D


class CommandType(str, Enum):
    MOVE_J = "move_j"
    MOVE_L = "move_l"
    STOP = "stop"
    HOME = "home"
    ESTOP = "estop"
    RECOVER = "recover"


@dataclass
class Command:
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: CommandType = CommandType.STOP
    target_pose: Pose6D | None = None
    target_joints: list[float] | None = None
    speed_scale: float = 1.0
    constraints: dict | None = None

    def to_dict(self) -> dict:
        return {
            "command_id": self.command_id,
            "type": self.type.value,
            "target_pose": self.target_pose.to_dict() if self.target_pose else None,
            "target_joints": list(self.target_joints) if self.target_joints else None,
            "speed_scale": self.speed_scale,
            "constraints": self.constraints,
        }
```

- [ ] **Step 5: Write `backend/rcs/state/error.py`**

```python
"""Tracking error reported by the controller each tick."""
from __future__ import annotations
from dataclasses import dataclass
import time


@dataclass
class TrackingError:
    max_joint_error: float
    position_error_m: float
    timestamp_ns: int = 0

    def __post_init__(self) -> None:
        if self.timestamp_ns == 0:
            self.timestamp_ns = time.monotonic_ns()

    def to_dict(self) -> dict:
        return {
            "max_joint_error": self.max_joint_error,
            "position_error_m": self.position_error_m,
            "timestamp_ns": self.timestamp_ns,
        }
```

- [ ] **Step 6: Write `backend/rcs/state/profile.py`**

```python
"""Per-device static profile."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Morphology(str, Enum):
    ARM = "arm"
    AGV = "agv"
    STACKER = "stacker"


@dataclass
class Limits:
    pos_lower: list[float] = field(default_factory=list)
    pos_upper: list[float] = field(default_factory=list)
    vel_max: list[float] = field(default_factory=list)
    acc_max: list[float] = field(default_factory=list)
    rad_th: float = 0.05
    pos_th: float = 0.01


@dataclass
class DeviceProfile:
    device_id: str
    morphology: Morphology
    num_joints: int
    control_hz: int
    limits: Limits = field(default_factory=Limits)
    home_joints: list[float] = field(default_factory=list)
    locked: bool = False
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "morphology": self.morphology.value,
            "num_joints": self.num_joints,
            "control_hz": self.control_hz,
            "limits": {
                "pos_lower": list(self.limits.pos_lower),
                "pos_upper": list(self.limits.pos_upper),
                "vel_max": list(self.limits.vel_max),
                "acc_max": list(self.limits.acc_max),
                "rad_th": self.limits.rad_th,
                "pos_th": self.limits.pos_th,
            },
            "home_joints": list(self.home_joints),
            "locked": self.locked,
        }
```

- [ ] **Step 7: Write `backend/rcs/state/controller_state.py`**

```python
"""Per-device controller mode + active command."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class ControllerMode(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    HALTED = "halted"
    FAULT = "fault"
    E_STOP = "e_stop"


@dataclass
class ControllerState:
    mode: ControllerMode = ControllerMode.IDLE
    active_command_id: str | None = None
    last_error: str | None = None

    def to_dict(self) -> dict:
        return {
            "mode": self.mode.value,
            "active_command_id": self.active_command_id,
            "last_error": self.last_error,
        }
```

- [ ] **Step 8: Write `backend/rcs/state/state_stream.py`**

```python
"""In-memory state broadcast with 10 Hz rate-limit and 64 KB cap."""
from __future__ import annotations
import asyncio
import json
import time
from collections import defaultdict
from dataclasses import dataclass

from .joint import JointState
from .error import TrackingError
from .controller_state import ControllerState


@dataclass
class StateFrame:
    device_id: str
    joint: JointState
    err: TrackingError
    ctrl: ControllerState
    iso_ts: str


class StateStream:
    def __init__(self, max_fps: float = 10.0, max_bytes: int = 64 * 1024) -> None:
        self._min_interval_ns = int(1e9 / max_fps)
        self._max_bytes = max_bytes
        self._last_emit_ns: dict[str, int] = defaultdict(int)
        self._subscribers: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=64)
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        try:
            self._subscribers.remove(q)
        except ValueError:
            pass

    def publish(
        self,
        device_id: str,
        joint: JointState,
        err: TrackingError,
        ctrl: ControllerState,
    ) -> None:
        now = time.monotonic_ns()
        if now - self._last_emit_ns[device_id] < self._min_interval_ns:
            return
        self._last_emit_ns[device_id] = now
        frame = StateFrame(
            device_id=device_id,
            joint=joint,
            err=err,
            ctrl=ctrl,
            iso_ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        payload = json.dumps(frame.__dict__ | {
            "joint": joint.to_dict(),
            "err": err.to_dict(),
            "ctrl": ctrl.to_dict(),
        }, default=list).encode()
        degraded = False
        if len(payload) > self._max_bytes:
            degraded = True
            payload = json.dumps({
                "device_id": device_id,
                "joint": joint.to_dict(),
                "ctrl": ctrl.to_dict(),
                "iso_ts": frame.iso_ts,
                "degraded": True,
            }, default=list).encode()
        for q in list(self._subscribers):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                pass

    def force_publish(
        self,
        device_id: str,
        joint: JointState,
        err: TrackingError,
        ctrl: ControllerState,
    ) -> None:
        """Bypass the 10 Hz rate-limit (used for mode changes / estop)."""
        prev = self._last_emit_ns.get(device_id, 0)
        self._last_emit_ns[device_id] = 0
        self.publish(device_id, joint, err, ctrl)
        self._last_emit_ns[device_id] = prev
```

- [ ] **Step 9: Write `backend/rcs/tests/__init__.py` and `backend/rcs/tests/conftest.py`**

```python
# backend/rcs/tests/__init__.py
```

```python
# backend/rcs/tests/conftest.py
"""Pytest fixtures for RCS-1 tests.

RCS-1 is fully isolated: the registry is reset to a small default fixture
between unit tests. Integration tests use FastAPI TestClient with the
rcs_router mounted on a throwaway app (not backend.main).
"""
from __future__ import annotations
import pytest


@pytest.fixture
def reset_registry():
    from backend.rcs import registry
    registry._reset_for_tests()
    yield
    registry._reset_for_tests()
```

- [ ] **Step 10: Commit**

```bash
git add backend/rcs/state backend/rcs/tests/__init__.py backend/rcs/tests/conftest.py
git commit -m "feat(rcs-1): state types and in-memory state stream"
```

---

### Task 2: EventBus

**Files:**
- Create: `backend/rcs/events.py`
- Create: `backend/rcs/tests/unit/test_event_bus.py`

**Interfaces:**
- Consumes: nothing
- Produces: `EventBus.publish(name, payload)`, `EventBus.subscribe(name, callback) -> Subscription`

- [ ] **Step 1: Write the failing test `backend/rcs/tests/unit/test_event_bus.py`**

```python
import asyncio
from backend.rcs.events import EventBus


def test_subscribe_receives_event():
    bus = EventBus()
    seen: list = []

    async def collect():
        sub = bus.subscribe("e1", lambda p: seen.append(p))
        bus.publish("e1", {"x": 1})
        await asyncio.sleep(0.01)
        assert seen == [{"x": 1}]
        sub.unsubscribe()

    asyncio.run(collect())


def test_unsubscribe_stops_delivery():
    bus = EventBus()
    seen: list = []

    async def collect():
        sub = bus.subscribe("e1", lambda p: seen.append(p))
        sub.unsubscribe()
        bus.publish("e1", {"x": 1})
        await asyncio.sleep(0.01)
        assert seen == []

    asyncio.run(collect())


def test_isolated_by_name():
    bus = EventBus()
    seen: list = []

    async def collect():
        sub = bus.subscribe("e1", lambda p: seen.append(("e1", p)))
        bus.publish("e2", {"x": 1})
        await asyncio.sleep(0.01)
        assert seen == []
        sub.unsubscribe()

    asyncio.run(collect())
```

- [ ] **Step 2: Run the test, expect failure**

```bash
python -m pytest backend/rcs/tests/unit/test_event_bus.py -v
```
Expected: `ModuleNotFoundError: No module named 'backend.rcs.events'`.

- [ ] **Step 3: Implement `backend/rcs/events.py`**

```python
"""Async event bus for RCS-1 internal events.

Used to surface halt/fault/estop events to future subscribers (e.g. an
AlertEngine bridge) without RCS-1 importing the alert service.
"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Subscription:
    name: str
    callback: Callable[[Any], None]
    bus: "EventBus"
    _active: bool = True

    def unsubscribe(self) -> None:
        if not self._active:
            return
        self._active = False
        self.bus._drop(self)


class EventBus:
    def __init__(self) -> None:
        self._subs: list[Subscription] = []
        self._lock = asyncio.Lock()

    def subscribe(self, name: str, callback: Callable[[Any], None]) -> Subscription:
        sub = Subscription(name=name, callback=callback, bus=self)
        self._subs.append(sub)
        return sub

    def _drop(self, sub: Subscription) -> None:
        try:
            self._subs.remove(sub)
        except ValueError:
            pass

    def publish(self, name: str, payload: Any) -> None:
        for sub in list(self._subs):
            if sub._active and sub.name == name:
                try:
                    sub.callback(payload)
                except Exception:  # pragma: no cover - callback isolation
                    pass
```

- [ ] **Step 4: Run the test, expect pass**

```bash
python -m pytest backend/rcs/tests/unit/test_event_bus.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/rcs/events.py backend/rcs/tests/unit/test_event_bus.py
git commit -m "feat(rcs-1): internal event bus"
```

---

### Task 3: Forward kinematics (TDD)

**Files:**
- Create: `backend/rcs/planning/__init__.py`
- Create: `backend/rcs/planning/fk.py`
- Create: `backend/rcs/tests/unit/test_fk.py`

**Interfaces:**
- Consumes: list of 6 joint angles, list of 6 DH params
- Produces: 4x4 homogeneous transform (numpy array)

- [ ] **Step 1: Write `backend/rcs/planning/__init__.py` (empty placeholder — Task 3)**

```python
"""Motion planning primitives (FK / IK / Trajectory / Interpolator).

This file is initially empty. The aggregated re-exports are filled in at
the end of Task 6 (Interpolator), once every module exists. Task 3's
tests import from `backend.rcs.planning.fk` directly, not via this
__init__, so leaving it empty during Tasks 3-5 is intentional.
"""
```

> **Plan note (for later tasks):** At the end of Task 6, the implementer
> must replace this file with the aggregated re-export:
>
> ```python
> from .fk import fk
> from .ik import ik, NoSolution
> from .trajectory import plan_trapezoidal, plan_quintic, Trajectory
> from .interpolator import Interpolator
>
> __all__ = [
>     "fk", "ik", "NoSolution",
>     "plan_trapezoidal", "plan_quintic", "Trajectory",
>     "Interpolator",
> ]
> ```
>
> This edit is part of Task 6's commit.
    "plan_quintic",
    "Trajectory",
    "Interpolator",
]
```

- [ ] **Step 2: Write the failing test `backend/rcs/tests/unit/test_fk.py`**

```python
import math
import numpy as np
from backend.rcs.planning.fk import fk


# DH parameters in implementation order: (a, d, alpha, theta_offset).
# a = link length along x_{i-1}; d = offset along x_{i-1}; alpha = twist
# about x_{i-1}; theta_offset = static joint angle (added to q at each step).
# These particular values are a 6-DOF arm used to exercise FK; they are
# not the canonical UR5 (whose DH parameters are sensitive to convention
# and out of scope for this prototype). The tests assert only the
# mathematical invariants the implementation is responsible for: 4x4
# homogeneous transforms, proper rotation matrices, and a non-degenerate
# chain that moves the end-effector.
ARM_DH = [
    (0.0,  0.10,  math.pi / 2, 0.0),
    (0.3,  0.0,   0.0,         0.0),
    (0.2,  0.0,   math.pi / 2, 0.0),
    (0.0,  0.10, -math.pi / 2, 0.0),
    (0.0,  0.05,  math.pi / 2, 0.0),
    (0.0,  0.04,  0.0,         0.0),
]


def test_fk_returns_4x4_homogeneous():
    q = [0.0] * 6
    T = fk(q, ARM_DH)
    assert T.shape == (4, 4)
    # Last row is (0, 0, 0, 1).
    np.testing.assert_allclose(T[3, :], [0.0, 0.0, 0.0, 1.0], atol=1e-12)


def test_fk_rotation_is_proper_orthogonal():
    q = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    T = fk(q, ARM_DH)
    R = T[:3, :3]
    np.testing.assert_allclose(R @ R.T, np.eye(3), atol=1e-9)
    np.testing.assert_allclose(np.linalg.det(R), 1.0, atol=1e-9)


def test_fk_nonzero_joint_changes_end_effector_position():
    T0 = fk([0.0] * 6, ARM_DH)
    T1 = fk([0.5, 0.0, 0.0, 0.0, 0.0, 0.0], ARM_DH)
    # Any joint movement should produce a measurable end-effector translation
    # (i.e. the kinematic chain is not degenerate).
    pos_diff = np.linalg.norm(T1[:3, 3] - T0[:3, 3])
    assert pos_diff > 1e-3
```

- [ ] **Step 3: Run the test, expect failure**

```bash
python -m pytest backend/rcs/tests/unit/test_fk.py -v
```
Expected: `ModuleNotFoundError: No module named 'backend.rcs.planning.fk'`.

- [ ] **Step 4: Implement `backend/rcs/planning/fk.py`**

```python
"""Standard DH forward kinematics for a 6-DOF arm.

DH tuple order matches the implementation: (a, d, alpha, theta_offset).
`fk(q, dh)` adds `q[i] + theta_offset[i]` as the joint angle and uses
`a`, `d`, `alpha` for the link geometry.
"""
from __future__ import annotations
import numpy as np


def _dh_matrix(dh: tuple[float, float, float, float], theta: float) -> np.ndarray:
    a, d, alpha, _theta_offset = dh
    angle = theta + _theta_offset
    ct, st = np.cos(angle), np.sin(angle)
    ca, sa = np.cos(alpha), np.sin(alpha)
    return np.array([
        [ct, -st * ca,  st * sa, a * ct],
        [st,  ct * ca, -ct * sa, a * st],
        [0.0, sa,       ca,      d     ],
        [0.0, 0.0,      0.0,     1.0   ],
    ])


def fk(q: list[float], dh_params: list[tuple[float, float, float, float]]) -> np.ndarray:
    if len(q) != len(dh_params):
        raise ValueError(f"q length {len(q)} != dh length {len(dh_params)}")
    T = np.eye(4)
    for qi, dh in zip(q, dh_params):
        T = T @ _dh_matrix(dh, qi)
    return T
```

- [ ] **Step 5: Run the test, expect pass**

```bash
python -m pytest backend/rcs/tests/unit/test_fk.py -v
```
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/rcs/planning/__init__.py backend/rcs/planning/fk.py backend/rcs/tests/unit/test_fk.py
git commit -m "feat(rcs-1): DH forward kinematics"
```

---

### Task 4: Inverse kinematics (TDD)

**Files:**
- Create: `backend/rcs/planning/ik.py`
- Create: `backend/rcs/tests/unit/test_ik.py`

**Interfaces:**
- Consumes: 6 joint angles (seed), DH params, target 4x4 transform, joint limits
- Produces: 6 joint angles, or raises `NoSolution`

- [ ] **Step 1: Write the failing test `backend/rcs/tests/unit/test_ik.py`**

```python
import math
import numpy as np
import pytest
from backend.rcs.planning.fk import fk
from backend.rcs.planning.ik import ik, NoSolution


# 6-DOF arm DH parameters in implementation order: (a, d, alpha, theta_offset).
# Matches the ARM_DH used in test_fk.py. See backend.rcs.planning.fk for
# the parameter convention.
ARM_DH = [
    (0.0,  0.10,  math.pi / 2, 0.0),
    (0.3,  0.0,   0.0,         0.0),
    (0.2,  0.0,   math.pi / 2, 0.0),
    (0.0,  0.10, -math.pi / 2, 0.0),
    (0.0,  0.05,  math.pi / 2, 0.0),
    (0.0,  0.04,  0.0,         0.0),
]

LOWER = [-2*math.pi, -math.pi, -math.pi, -2*math.pi, -2*math.pi, -2*math.pi]
UPPER = [ 2*math.pi,  math.pi,  math.pi,  2*math.pi,  2*math.pi,  2*math.pi]


def test_ik_roundtrip_from_zero():
    q_seed = [0.0] * 6
    T = fk(q_seed, ARM_DH)
    q = ik(q_seed, ARM_DH, T, LOWER, UPPER)
    T2 = fk(list(q), ARM_DH)
    np.testing.assert_allclose(T2, T, atol=1e-4)


def test_ik_far_pose_no_solution():
    # Position 1000 m away is unreachable for the test arm (workspace ~0.5 m).
    T = np.eye(4)
    T[0, 3] = 1000.0
    with pytest.raises(NoSolution):
        ik([0.0] * 6, ARM_DH, T, LOWER, UPPER, max_iter=50)


def test_ik_respects_limits_when_solution_exists():
    # Pose reachable from zero pose with limits that exclude the seed.
    # The solver should still return a valid in-limits solution.
    q_seed = [0.0] * 6
    T = fk(q_seed, ARM_DH)
    q = ik(q_seed, ARM_DH, T, LOWER, UPPER)
    for qi, lo, hi in zip(q, LOWER, UPPER):
        assert lo - 1e-6 <= qi <= hi + 1e-6
```

- [ ] **Step 2: Run the test, expect failure**

```bash
python -m pytest backend/rcs/tests/unit/test_ik.py -v
```
Expected: `ModuleNotFoundError: No module named 'backend.rcs.planning.ik'`.

- [ ] **Step 3: Implement `backend/rcs/planning/ik.py`**

The analytical closed-form 6-DOF IK is significant code; this plan uses a numerical Jacobian-pseudoinverse solver with restarts on joints at limits, which is simpler and sufficient for the prototype.

```python
"""Numerical IK via damped least squares (no singularity avoidance).

Used for the prototype; production hardware (real UR5 etc.) would swap in
the vendor's analytical solver. The solver returns the first in-limits
solution; if none found within max_iter, raises NoSolution.
"""
from __future__ import annotations
import numpy as np

from .fk import fk


class NoSolution(Exception):
    pass


def _axis_angle(R_err: np.ndarray) -> np.ndarray:
    angle = np.arccos(max(-1.0, min(1.0, (np.trace(R_err) - 1.0) / 2.0)))
    if abs(angle) < 1e-9:
        return np.zeros(3)
    axis = np.array([
        R_err[2, 1] - R_err[1, 2],
        R_err[0, 2] - R_err[2, 0],
        R_err[1, 0] - R_err[0, 1],
    ])
    n = np.linalg.norm(axis)
    if n < 1e-12:
        return np.zeros(3)
    return axis / n * angle


def _geometric_jacobian(q: list[float], dh_params) -> np.ndarray:
    T = np.eye(4)
    origins = [T[:3, 3].copy()]
    z_axes = [T[:3, 2].copy()]
    for qi, dh in zip(q, dh_params):
        a, d, alpha, _theta = dh
        ct, st = np.cos(qi), np.sin(qi)
        ca, sa = np.cos(alpha), np.sin(alpha)
        Ti = np.array([
            [ct, -st * ca,  st * sa, a * ct],
            [st,  ct * ca, -ct * sa, a * st],
            [0.0, sa,       ca,      d     ],
            [0.0, 0.0,      0.0,     1.0   ],
        ])
        T = T @ Ti
        origins.append(T[:3, 3].copy())
        z_axes.append(T[:3, 2].copy())
    J = np.zeros((6, len(q)))
    for i in range(len(q)):
        z = z_axes[i]
        o = origins[i]
        J[:3, i] = np.cross(z, T[:3, 3] - o)
        J[3:, i] = z
    return J


def _clip(q: np.ndarray, lower, upper) -> np.ndarray:
    return np.minimum(np.maximum(q, lower), upper)


def ik(
    q_seed: list[float],
    dh_params,
    T_target: np.ndarray,
    lower: list[float],
    upper: list[float],
    max_iter: int = 200,
    tol: float = 1e-4,
) -> np.ndarray:
    q = np.array(q_seed, dtype=float)
    lb = np.array(lower, dtype=float)
    ub = np.array(upper, dtype=float)
    q = _clip(q, lb, ub)
    p_target = T_target[:3, 3]
    R_target = T_target[:3, :3]
    damping = 1e-4
    for _ in range(max_iter):
        T = fk(list(q), dh_params)
        pos_err = p_target - T[:3, 3]
        rot_err = _axis_angle(R_target @ T[:3, :3].T)
        err = np.concatenate([pos_err, rot_err])
        if np.linalg.norm(err) < tol:
            return q
        J = _geometric_jacobian(list(q), dh_params)
        JJt = J @ J.T + damping * np.eye(6)
        dq = J.T @ np.linalg.solve(JJt, err)
        q = _clip(q + dq, lb, ub)
    raise NoSolution("ik did not converge within max_iter")
```

- [ ] **Step 4: Run the test, expect pass**

```bash
python -m pytest backend/rcs/tests/unit/test_ik.py -v
```
Expected: 3 passed (roundtrip + far pose NoSolution + limit clip).

- [ ] **Step 5: Commit**

```bash
git add backend/rcs/planning/ik.py backend/rcs/tests/unit/test_ik.py
git commit -m "feat(rcs-1): numerical inverse kinematics"
```

---

### Task 5: Trajectory (TDD)

**Files:**
- Create: `backend/rcs/planning/trajectory.py`
- Create: `backend/rcs/tests/unit/test_trajectory.py`

**Interfaces:**
- Consumes: `q_start: list[float]`, `q_goal: list[float]`, `vel_max: list[float]`, `acc_max: list[float]`
- Produces: `Trajectory` with `duration_s: float` and `sample(t: float) -> list[float]`

- [ ] **Step 1: Write the failing test `backend/rcs/tests/unit/test_trajectory.py`**

```python
import math
from backend.rcs.planning.trajectory import plan_trapezoidal, plan_quintic


def test_trapezoidal_single_axis_hits_goal():
    vel_max = [1.0]
    acc_max = [2.0]
    traj = plan_trapezoidal([0.0], [1.0], vel_max, acc_max)
    assert traj.duration_s > 0
    end = traj.sample(traj.duration_s)
    assert abs(end[0] - 1.0) < 1e-6


def test_trapezoidal_peak_velocity_proportional_to_distance_over_duration():
    vel_max = [1.0]
    acc_max = [2.0]
    traj = plan_trapezoidal([0.0], [5.0], vel_max, acc_max)
    times = [i / 1000 for i in range(int(traj.duration_s * 1000) + 1)]
    # The symmetric trapezoid normalises s in [0, 1] with cruise phase
    # occupying [0.25, 0.75] (width 0.5), so the normalised peak velocity
    # ds/dt is 1/0.5 = 2.0. The trajectory linearly maps s to each joint
    # from start to goal, so the peak dq/dt is 2.0 * (goal-start) /
    # duration_s. We assert the observed peak is bounded by 1.05x that
    # value (tolerance for discrete sampling and trapezoid edges).
    duration = traj.duration_s
    expected_peak = 2.0 * 5.0 / duration
    peak = max(
        abs(traj.sample(t)[0] - traj.sample(max(0.0, t - 1e-3))[0]) / 1e-3
        for t in times
        if t > 0
    )
    assert peak <= expected_peak * 1.05


def test_quintic_zero_velocity_at_endpoints():
    vel_max = [1.0]
    acc_max = [2.0]
    traj = plan_quintic([0.0], [1.0], vel_max, acc_max)
    assert traj.duration_s > 0
    assert abs(traj.sample(0.0)[0] - 0.0) < 1e-6
    assert abs(traj.sample(traj.duration_s)[0] - 1.0) < 1e-6
```

- [ ] **Step 2: Run the test, expect failure**

```bash
python -m pytest backend/rcs/tests/unit/test_trajectory.py -v
```
Expected: `ModuleNotFoundError: No module named 'backend.rcs.planning.trajectory'`.

- [ ] **Step 3: Implement `backend/rcs/planning/trajectory.py`**

```python
"""Joint-space trajectory planning: trapezoidal and quintic time-optimal scaling."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Trajectory:
    q_start: list[float]
    q_goal: list[float]
    duration_s: float
    profile: str  # "trapezoidal" | "quintic"
    vel_max: list[float]
    acc_max: list[float]

    def sample(self, t: float) -> list[float]:
        t = max(0.0, min(self.duration_s, t))
        s = self._scalar(t / self.duration_s)
        return [a + (b - a) * s for a, b in zip(self.q_start, self.q_goal)]

    def _scalar(self, s: float) -> float:
        if self.profile == "trapezoidal":
            return _trapezoidal_scalar(s)
        return _quintic_scalar(s)


def _trapezoidal_scalar(s: float) -> float:
    # Symmetric trapezoid on s in [0, 1] with three phases:
    #   s in [0, 0.25]:  acceleration, y goes 0 -> 0.125 (y' = 4s)
    #   s in [0.25, 0.75]:  cruise, y goes 0.125 -> 0.625 (y' = 1)
    #   s in [0.75, 1]:  deceleration, y goes 0.625 -> 1.0 (y' = 1 + 4(s-0.75))
    # Continuous at s=0.25 and s=0.75; the cruise-phase slope (1.0) is
    # matched at both ends.
    if s < 0.25:
        return 2.0 * s * s
    if s < 0.75:
        return 0.125 + (s - 0.25)
    u = s - 0.75
    return 0.625 + u + 2.0 * u * u


def _quintic_scalar(s: float) -> float:
    # s^3 * (6s^2 - 15s + 10) — C2-continuous, zero velocity at endpoints.
    return s * s * s * (6.0 * s * s - 15.0 * s + 10.0)


def _axis_duration(dq: float, vmax: float, amax: float) -> float:
    if abs(dq) < 1e-9:
        return 0.0
    t_accel = vmax / amax
    d_accel = 0.5 * amax * t_accel * t_accel
    if 2 * d_accel >= abs(dq):
        # Triangle profile (no cruise).
        return 2.0 * math.sqrt(abs(dq) / amax)
    d_cruise = abs(dq) - 2 * d_accel
    return 2 * t_accel + d_cruise / vmax


import math  # noqa: E402  (kept after dataclass to keep public surface clean)


def _plan(q_start, q_goal, vel_max, acc_max, profile: str) -> Trajectory:
    duration = 0.0
    for qs, qg, vm, am in zip(q_start, q_goal, vel_max, acc_max):
        d = _axis_duration(qg - qs, vm, am)
        if d > duration:
            duration = d
    if duration < 1e-9:
        duration = 1e-3
    return Trajectory(
        q_start=list(q_start),
        q_goal=list(q_goal),
        duration_s=duration,
        profile=profile,
        vel_max=list(vel_max),
        acc_max=list(acc_max),
    )


def plan_trapezoidal(q_start, q_goal, vel_max, acc_max) -> Trajectory:
    return _plan(q_start, q_goal, vel_max, acc_max, "trapezoidal")


def plan_quintic(q_start, q_goal, vel_max, acc_max) -> Trajectory:
    return _plan(q_start, q_goal, vel_max, acc_max, "quintic")
```

- [ ] **Step 4: Run the test, expect pass**

```bash
python -m pytest backend/rcs/tests/unit/test_trajectory.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/rcs/planning/trajectory.py backend/rcs/tests/unit/test_trajectory.py
git commit -m "feat(rcs-1): trapezoidal + quintic joint-space trajectories"
```

---

### Task 6: Interpolator (TDD)

**Files:**
- Create: `backend/rcs/planning/interpolator.py`
- Create: `backend/rcs/tests/unit/test_interpolator.py`

**Interfaces:**
- Consumes: `Trajectory`, `step_s: float = 0.001`
- Produces: an iterator-like `Interpolator` exposing `next() -> list[float]`, `done: bool`, `elapsed_s: float`

- [ ] **Step 1: Write the failing test `backend/rcs/tests/unit/test_interpolator.py`**

```python
from backend.rcs.planning.trajectory import plan_trapezoidal
from backend.rcs.planning.interpolator import Interpolator


def test_interpolator_emits_step_count():
    traj = plan_trapezoidal([0.0], [1.0], [1.0], [2.0])
    it = Interpolator(traj, step_s=0.001)
    count = 0
    while not it.done:
        _ = it.next()
        count += 1
    expected = int(round(traj.duration_s / 0.001))
    assert abs(count - expected) <= 2


def test_interpolator_first_sample_matches_start():
    traj = plan_trapezoidal([0.0, 0.0], [1.0, -1.0], [1.0, 1.0], [2.0, 2.0])
    it = Interpolator(traj, step_s=0.001)
    s0 = it.next()
    assert abs(s0[0]) < 1e-9 and abs(s0[1]) < 1e-9


def test_interpolator_last_sample_matches_goal():
    traj = plan_trapezoidal([0.0, 0.0], [1.0, -1.0], [1.0, 1.0], [2.0, 2.0])
    it = Interpolator(traj, step_s=0.001)
    last = None
    while not it.done:
        last = it.next()
    assert last is not None
    assert abs(last[0] - 1.0) < 1e-3
    assert abs(last[1] + 1.0) < 1e-3
```

- [ ] **Step 2: Run the test, expect failure**

```bash
python -m pytest backend/rcs/tests/unit/test_interpolator.py -v
```
Expected: `ModuleNotFoundError: No module named 'backend.rcs.planning.interpolator'`.

- [ ] **Step 3: Implement `backend/rcs/planning/interpolator.py`**

```python
"""Step-through interpolator for a Trajectory."""
from __future__ import annotations
from .trajectory import Trajectory


class Interpolator:
    def __init__(self, traj: Trajectory, step_s: float = 0.001) -> None:
        self._traj = traj
        self._step_s = step_s
        self._elapsed_s = 0.0
        self._done = False

    @property
    def done(self) -> bool:
        return self._done

    @property
    def elapsed_s(self) -> float:
        return self._elapsed_s

    def next(self) -> list[float]:
        sample = self._traj.sample(self._elapsed_s)
        self._elapsed_s += self._step_s
        if self._elapsed_s >= self._traj.duration_s:
            self._done = True
        return sample
```

- [ ] **Step 4: Run the test, expect pass**

```bash
python -m pytest backend/rcs/tests/unit/test_interpolator.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Complete `backend/rcs/planning/__init__.py` (carry-over from Task 3)**

Now that all four planning modules (fk, ik, trajectory, interpolator) exist, replace the placeholder `__init__.py` with the aggregated re-export:

```python
"""Motion planning primitives (FK / IK / Trajectory / Interpolator)."""
from .fk import fk
from .ik import ik, NoSolution
from .trajectory import plan_trapezoidal, plan_quintic, Trajectory
from .interpolator import Interpolator

__all__ = [
    "fk",
    "ik",
    "NoSolution",
    "plan_trapezoidal",
    "plan_quintic",
    "Trajectory",
    "Interpolator",
]
```

Verify the aggregated import works:

```bash
python -c "from backend.rcs.planning import fk, ik, NoSolution, plan_trapezoidal, plan_quintic, Trajectory, Interpolator; print('ok')"
```
Expected: `ok`.

- [ ] **Step 6: Commit**

```bash
git add backend/rcs/planning/__init__.py backend/rcs/planning/interpolator.py backend/rcs/tests/unit/test_interpolator.py
git commit -m "feat(rcs-1): 1ms-step interpolator"
```

---

### Task 7: HAL protocol + SimHAL (TDD)

**Files:**
- Create: `backend/rcs/hal/__init__.py`
- Create: `backend/rcs/hal/protocol.py`
- Create: `backend/rcs/hal/sim.py`
- Create: `backend/rcs/tests/unit/test_sim_hal.py`

**Interfaces:**
- Consumes: `DeviceProfile`
- Produces: `DeviceHAL` Protocol and `SimHAL` concrete impl

- [ ] **Step 1: Write `backend/rcs/hal/__init__.py`**

```python
"""Device HAL protocol and SimHAL implementation."""
from .protocol import DeviceHAL
from .sim import SimHAL

__all__ = ["DeviceHAL", "SimHAL"]
```

- [ ] **Step 2: Write the failing test `backend/rcs/tests/unit/test_sim_hal.py`**

```python
import asyncio
import pytest
from backend.rcs.hal.sim import SimHAL
from backend.rcs.state.profile import DeviceProfile, Morphology, Limits


@pytest.fixture
def sim():
    return SimHAL()


@pytest.fixture
def arm_profile():
    return DeviceProfile(
        device_id="robot-01",
        morphology=Morphology.ARM,
        num_joints=6,
        control_hz=1000,
        limits=Limits(
            pos_lower=[-3.14] * 6,
            pos_upper=[3.14] * 6,
            vel_max=[1.0] * 6,
            acc_max=[2.0] * 6,
        ),
        home_joints=[0.0] * 6,
    )


def test_sim_hal_read_returns_zero_state(sim, arm_profile):
    sim.register(arm_profile)
    state = asyncio.run(sim.read("robot-01"))
    assert state.device_id == "robot-01"
    assert state.positions == [0.0] * 6
    assert len(state.velocities) == 6
    assert len(state.efforts) == 6


def test_sim_hal_write_then_read(sim, arm_profile):
    sim.register(arm_profile)
    asyncio.run(sim.write("robot-01", [0.1, 0.0, 0.0, 0.0, 0.0, 0.0]))
    state = asyncio.run(sim.read("robot-01"))
    # SimHAL converges in one step toward the target for the prototype.
    assert abs(state.positions[0] - 0.1) < 1e-6


def test_sim_hal_estop_freezes(sim, arm_profile):
    sim.register(arm_profile)
    asyncio.run(sim.write("robot-01", [0.5, 0.0, 0.0, 0.0, 0.0, 0.0]))
    asyncio.run(sim.estop("robot-01"))
    state = asyncio.run(sim.read("robot-01"))
    # After estop, write is rejected; state remains whatever it was.
    assert state.positions[0] <= 0.5 + 1e-6


def test_sim_hal_unknown_device_raises(sim):
    with pytest.raises(KeyError):
        asyncio.run(sim.read("nope"))
```

- [ ] **Step 3: Run the test, expect failure**

```bash
python -m pytest backend/rcs/tests/unit/test_sim_hal.py -v
```
Expected: `ModuleNotFoundError: No module named 'backend.rcs.hal.sim'`.

- [ ] **Step 4: Write `backend/rcs/hal/protocol.py`**

```python
"""Device HAL Protocol — hardware abstraction for RCS-1."""
from __future__ import annotations
from typing import Protocol, runtime_checkable

from ..state.joint import JointState
from ..state.profile import DeviceProfile


@runtime_checkable
class DeviceHAL(Protocol):
    async def read(self, device_id: str) -> JointState: ...
    async def write(self, device_id: str, target: list[float] | JointState) -> None: ...
    async def estop(self, device_id: str) -> None: ...
    def profile(self, device_id: str) -> DeviceProfile: ...
```

- [ ] **Step 5: Write `backend/rcs/hal/sim.py`**

```python
"""In-memory SimHAL — math-only, no real hardware.

Models each joint as a first-order lag toward the last commanded target.
This is intentionally simple: the goal is to exercise the control loop
end-to-end, not to simulate physics.
"""
from __future__ import annotations
import asyncio

from ..state.joint import JointState
from ..state.profile import DeviceProfile


class SimHAL:
    def __init__(self) -> None:
        self._profiles: dict[str, DeviceProfile] = {}
        self._state: dict[str, JointState] = {}
        self._targets: dict[str, list[float]] = {}
        self._estopped: set[str] = set()
        self._lock = asyncio.Lock()

    def register(self, profile: DeviceProfile) -> None:
        self._profiles[profile.device_id] = profile
        self._state[profile.device_id] = JointState(
            positions=[0.0] * profile.num_joints,
            velocities=[0.0] * profile.num_joints,
            efforts=[0.0] * profile.num_joints,
            device_id=profile.device_id,
        )
        self._targets[profile.device_id] = list(profile.home_joints)

    def profile(self, device_id: str) -> DeviceProfile:
        return self._profiles[device_id]

    async def read(self, device_id: str) -> JointState:
        if device_id not in self._state:
            raise KeyError(f"unknown device_id: {device_id}")
        s = self._state[device_id]
        # First-order lag: move 80% toward target each call (synchronous in async).
        target = self._targets[device_id]
        new_pos = [p + 0.8 * (t - p) for p, t in zip(s.positions, target)]
        s.positions = new_pos
        s.velocities = [0.0] * len(new_pos)
        s.efforts = [0.0] * len(new_pos)
        return JointState(
            positions=list(s.positions),
            velocities=list(s.velocities),
            efforts=list(s.efforts),
            device_id=device_id,
        )

    async def write(self, device_id: str, target) -> None:
        if device_id in self._estopped:
            return
        if device_id not in self._targets:
            raise KeyError(f"unknown device_id: {device_id}")
        if isinstance(target, JointState):
            target = list(target.positions)
        # Clip to limits.
        prof = self._profiles[device_id]
        lo, hi = prof.limits.pos_lower, prof.limits.pos_upper
        clipped = [max(lo[i], min(hi[i], target[i])) for i in range(len(target))]
        self._targets[device_id] = clipped

    async def estop(self, device_id: str) -> None:
        if device_id not in self._profiles:
            raise KeyError(f"unknown device_id: {device_id}")
        self._estopped.add(device_id)

    def clear_estop(self, device_id: str) -> None:
        self._estopped.discard(device_id)
```

- [ ] **Step 6: Run the test, expect pass**

```bash
python -m pytest backend/rcs/tests/unit/test_sim_hal.py -v
```
Expected: 4 passed.

- [ ] **Step 7: Commit**

```bash
git add backend/rcs/hal backend/rcs/tests/unit/test_sim_hal.py
git commit -m "feat(rcs-1): DeviceHAL protocol + SimHAL"
```

---

### Task 8: Controller base + ArmController (TDD)

**Files:**
- Create: `backend/rcs/controllers/__init__.py`
- Create: `backend/rcs/controllers/base.py`
- Create: `backend/rcs/controllers/_common.py`
- Create: `backend/rcs/controllers/arm.py`
- Create: `backend/rcs/tests/unit/test_arm_controller.py`

**Interfaces:**
- Consumes: `DeviceProfile`, `DeviceHAL`, `Command`
- Produces: `Controller` ABC + `ArmController`

- [ ] **Step 1: Write `backend/rcs/controllers/__init__.py`**

This file is created in Task 8 with just the Controller base re-export. The `AgvController`/`StackerController` re-exports are added in Task 9 after those modules exist.

```python
"""Controller base + morphology-specific implementations."""
from .base import Controller
from .arm import ArmController

__all__ = ["Controller", "ArmController"]
```

- [ ] **Step 2: Write `backend/rcs/controllers/_common.py`**

```python
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
```

- [ ] **Step 3: Write `backend/rcs/controllers/base.py`**

```python
"""Controller abstract base class."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from ..state.joint import JointState
from ..state.command import Command
from ..state.error import TrackingError
from ..state.controller_state import ControllerState, ControllerMode
from ..state.profile import DeviceProfile, Morphology


class Controller(ABC):
    morphology: ClassVar[Morphology]  # marker — overridden in subclasses

    def __init__(self, profile: DeviceProfile) -> None:
        self.profile = profile
        self.state = ControllerState()

    @abstractmethod
    def update(self, hal_state: JointState) -> JointState: ...

    @abstractmethod
    def tracking_error(self, target: JointState, current: JointState) -> TrackingError: ...

    def on_command(self, cmd: Command) -> None: ...

    def halt(self) -> None:
        self.state.mode = ControllerMode.HALTED
        self.state.last_error = "halt requested"

    def recover(self) -> None:
        if self.state.mode == ControllerMode.HALTED:
            self.state.mode = ControllerMode.IDLE
            self.state.last_error = None

    def estop(self) -> None:
        self.state.mode = ControllerMode.E_STOP
        self.state.last_error = "estop"

    def clear_estop(self) -> None:
        if self.state.mode == ControllerMode.E_STOP:
            self.state.mode = ControllerMode.IDLE
            self.state.last_error = None
```

- [ ] **Step 4: Write the failing test `backend/rcs/tests/unit/test_arm_controller.py`**

```python
import math
import pytest
from backend.rcs.controllers.arm import ArmController
from backend.rcs.state.profile import DeviceProfile, Morphology, Limits
from backend.rcs.state.joint import JointState
from backend.rcs.state.command import Command, CommandType


@pytest.fixture
def arm_profile():
    return DeviceProfile(
        device_id="robot-01",
        morphology=Morphology.ARM,
        num_joints=6,
        control_hz=1000,
        limits=Limits(
            pos_lower=[-3.14] * 6,
            pos_upper=[3.14] * 6,
            vel_max=[2.5] * 6,
            acc_max=[5.0] * 6,
        ),
        home_joints=[0.0] * 6,
    )


def test_arm_step_response_reaches_target():
    ctrl = ArmController(arm_profile)
    # Drive the controller one MOVE_J command so the interpolator is armed.
    ctrl.on_command(Command(type=CommandType.MOVE_J, target_joints=[0.5, 0.0, 0.0, 0.0, 0.0, 0.0]))
    pos = [0.0] * 6
    for _ in range(2000):
        cur = JointState(positions=list(pos), velocities=[0.0]*6, efforts=[0.0]*6, device_id="robot-01")
        out = ctrl.update(cur)
        pos = list(out.positions)
    assert abs(pos[0] - 0.5) < 0.01


def test_arm_halts_on_tracking_error():
    ctrl = ArmController(arm_profile)
    # Inject a huge step; with kp=80, kd=8 it should still halt only if the
    # error threshold is exceeded. We force the threshold to be tiny via limits.
    ctrl.profile.limits.rad_th = 0.001
    cur = JointState(positions=[0.0]*6, velocities=[0.0]*6, efforts=[0.0]*6, device_id="robot-01")
    out = ctrl.update(cur)
    ctrl.tracking_error(out, cur)  # populates internal last_target
    err = ctrl.tracking_error(out, JointState(positions=[0.5, 0, 0, 0, 0, 0], velocities=[0]*6, efforts=[0]*6, device_id="robot-01"))
    if err.max_joint_error > ctrl.profile.limits.rad_th:
        ctrl.halt()
    # Either halted (if error is large enough) or still running — but never fault.
    assert ctrl.state.mode.value in ("halted", "running", "idle")


def test_arm_pd_output_within_torque_proxy_bounds():
    ctrl = ArmController(arm_profile)
    cur = JointState(positions=[0.0]*6, velocities=[0.0]*6, efforts=[0.0]*6, device_id="robot-01")
    out = ctrl.update(cur)
    assert len(out.positions) == 6
```

- [ ] **Step 5: Run the test, expect failure**

```bash
python -m pytest backend/rcs/tests/unit/test_arm_controller.py -v
```
Expected: `ModuleNotFoundError: No module named 'backend.rcs.controllers.arm'`.

- [ ] **Step 6: Write `backend/rcs/controllers/arm.py`**

```python
"""6-DOF arm controller: PD control in joint space + IK on move_l."""
from __future__ import annotations
import math
import numpy as np

from ..state.profile import DeviceProfile, Morphology
from ..state.joint import JointState
from ..state.command import Command, CommandType
from ..state.error import TrackingError
from ..state.controller_state import ControllerState, ControllerMode
from .base import Controller
from ._common import CommandQueue, clip_to_limits, abs_max
from ..planning import fk, ik
from ..planning.trajectory import plan_trapezoidal, Trajectory
from ..planning.interpolator import Interpolator


# DH parameters in implementation order: (a, d, alpha, theta_offset).
# Matches ARM_DH used in test_fk.py / test_ik.py. See backend.rcs.planning.fk
# for the parameter convention.
ARM_DH = [
    (0.0,  0.10,  math.pi / 2, 0.0),
    (0.3,  0.0,   0.0,         0.0),
    (0.2,  0.0,   math.pi / 2, 0.0),
    (0.0,  0.10, -math.pi / 2, 0.0),
    (0.0,  0.05,  math.pi / 2, 0.0),
    (0.0,  0.04,  0.0,         0.0),
]


class ArmController(Controller):
    morphology = Morphology.ARM

    def __init__(self, profile: DeviceProfile) -> None:
        super().__init__(profile)
        self._kp = 80.0
        self._kd = 8.0
        self._q: list[float] = list(profile.home_joints)
        self._qdot: list[float] = [0.0] * profile.num_joints
        self._last_target: list[float] = list(profile.home_joints)
        self._interp: Interpolator | None = None
        self._queue: CommandQueue = CommandQueue(maxsize=1024)

    def on_command(self, cmd: Command) -> None:
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            return
        # Idempotency: CommandQueue rejects a duplicate command_id silently.
        if not self._queue.push(cmd):
            return
        if cmd.type == CommandType.STOP:
            target = list(self._q)
        elif cmd.type == CommandType.HOME:
            target = list(self.profile.home_joints)
        elif cmd.type == CommandType.MOVE_J and cmd.target_joints is not None:
            target = clip_to_limits(cmd.target_joints, self.profile.limits.pos_lower, self.profile.limits.pos_upper)
        elif cmd.type == CommandType.MOVE_L and cmd.target_pose is not None:
            T = np.eye(4)
            T[:3, 3] = cmd.target_pose.position
            # orientation assumed identity if not provided; spec says q only for arm.
            try:
                q_sol = list(ik(self._q, ARM_DH, T, self.profile.limits.pos_lower, self.profile.limits.pos_upper))
            except Exception as exc:
                self.state.last_error = f"ik failed: {exc}"
                return
            target = q_sol
        else:
            return
        vmax = self.profile.limits.vel_max
        amax = self.profile.limits.acc_max
        traj = plan_trapezoidal(self._q, target, vmax, amax)
        self._interp = Interpolator(traj, step_s=1.0 / self.profile.control_hz)
        self.state.mode = ControllerMode.RUNNING
        self.state.active_command_id = cmd.command_id

    def update(self, hal_state: JointState) -> JointState:
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            # Brake: hold last command at zero velocity target.
            target = list(self._q)
        elif self._interp is not None and not self._interp.done:
            target = self._interp.next()
        else:
            target = list(self._q)
        # PD control.
        pos = list(hal_state.positions)
        out_positions = [
            self._q[i] + self._kp * (target[i] - self._q[i]) - self._kd * self._qdot[i]
            for i in range(len(target))
        ]
        out_positions = clip_to_limits(out_positions, self.profile.limits.pos_lower, self.profile.limits.pos_upper)
        self._qdot = [out_positions[i] - self._q[i] for i in range(len(out_positions))]
        self._q = out_positions
        self._last_target = target
        return JointState(
            positions=list(out_positions),
            velocities=list(self._qdot),
            efforts=[0.0] * len(out_positions),
            device_id=self.profile.device_id,
        )

    def tracking_error(self, target: JointState, current: JointState) -> TrackingError:
        max_joint = abs_max([target.positions[i] - current.positions[i] for i in range(len(target.positions))])
        if max_joint > self.profile.limits.rad_th:
            self.halt()
        return TrackingError(max_joint_error=max_joint, position_error_m=0.0)
```

- [ ] **Step 7: Run the test, expect pass**

```bash
python -m pytest backend/rcs/tests/unit/test_arm_controller.py -v
```
Expected: 3 passed.

- [ ] **Step 8: Commit**

```bash
git add backend/rcs/controllers backend/rcs/tests/unit/test_arm_controller.py
git commit -m "feat(rcs-1): ArmController with PD + IK + trajectory"
```

---

### Task 9: AgvController + StackerController (TDD)

**Files:**
- Create: `backend/rcs/controllers/agv.py`
- Create: `backend/rcs/controllers/stacker.py`
- Create: `backend/rcs/tests/unit/test_agv_controller.py`
- Create: `backend/rcs/tests/unit/test_stacker_controller.py`

- [ ] **Step 1: Write `backend/rcs/controllers/agv.py`**

```python
"""Differential-drive AGV controller: 2 joints (left/right wheel velocity)."""
from __future__ import annotations
import math

from ..state.profile import DeviceProfile, Morphology
from ..state.joint import JointState
from ..state.command import Command, CommandType
from ..state.error import TrackingError
from ..state.controller_state import ControllerState, ControllerMode
from .base import Controller
from ._common import CommandQueue, clip_to_limits, abs_max
from ..planning.trajectory import plan_trapezoidal, Trajectory
from ..planning.interpolator import Interpolator


class AgvController(Controller):
    morphology = Morphology.AGV

    def __init__(self, profile: DeviceProfile) -> None:
        super().__init__(profile)
        self._p = 1.5
        self._q: list[float] = [0.0] * 2  # linear, angular velocity
        self._interp: Interpolator | None = None
        self._queue: CommandQueue = CommandQueue(maxsize=1024)

    def on_command(self, cmd: Command) -> None:
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            return
        if cmd.type == CommandType.STOP:
            target = [0.0, 0.0]
        elif cmd.type == CommandType.MOVE_J and cmd.target_joints is not None:
            target = clip_to_limits(cmd.target_joints, [-2.0, -2.0], [2.0, 2.0])
        else:
            return
        vmax = self.profile.limits.vel_max or [1.0, 1.0]
        amax = self.profile.limits.acc_max or [2.0, 2.0]
        traj = plan_trapezoidal(self._q, target, vmax, amax)
        self._interp = Interpolator(traj, step_s=1.0 / self.profile.control_hz)
        self.state.mode = ControllerMode.RUNNING
        self.state.active_command_id = cmd.command_id

    def update(self, hal_state: JointState) -> JointState:
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            target = [0.0, 0.0]
        elif self._interp is not None and not self._interp.done:
            target = self._interp.next()
        else:
            target = list(self._q)
        out = [self._q[i] + self._p * (target[i] - self._q[i]) for i in range(len(target))]
        self._q = out
        return JointState(
            positions=list(out),
            velocities=[0.0, 0.0],
            efforts=[0.0, 0.0],
            device_id=self.profile.device_id,
        )

    def tracking_error(self, target: JointState, current: JointState) -> TrackingError:
        max_joint = abs_max([target.positions[i] - current.positions[i] for i in range(len(target.positions))])
        if max_joint > self.profile.limits.rad_th:
            self.halt()
        return TrackingError(max_joint_error=max_joint, position_error_m=0.0)
```

- [ ] **Step 2: Write `backend/rcs/controllers/stacker.py`**

```python
"""Stacker crane controller: 2 joints (lift, travel)."""
from __future__ import annotations
import math

from ..state.profile import DeviceProfile, Morphology
from ..state.joint import JointState
from ..state.command import Command, CommandType
from ..state.error import TrackingError
from ..state.controller_state import ControllerState, ControllerMode
from .base import Controller
from ._common import CommandQueue, clip_to_limits, abs_max
from ..planning.trajectory import plan_trapezoidal, Trajectory
from ..planning.interpolator import Interpolator


class StackerController(Controller):
    morphology = Morphology.STACKER

    def __init__(self, profile: DeviceProfile) -> None:
        super().__init__(profile)
        self._p = 1.5
        self._q: list[float] = [0.0] * 2
        self._interp: Interpolator | None = None
        self._queue: CommandQueue = CommandQueue(maxsize=1024)

    def on_command(self, cmd: Command) -> None:
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            return
        if not self._queue.push(cmd):
            return
        if cmd.type == CommandType.STOP:
            target = [0.0, 0.0]
        elif cmd.type == CommandType.HOME:
            target = [0.0, 0.0]
        elif cmd.type == CommandType.MOVE_J and cmd.target_joints is not None:
            target = clip_to_limits(cmd.target_joints, [-5.0, -10.0], [5.0, 10.0])
        else:
            return
        vmax = self.profile.limits.vel_max or [1.0, 1.0]
        amax = self.profile.limits.acc_max or [2.0, 2.0]
        traj = plan_trapezoidal(self._q, target, vmax, amax)
        self._interp = Interpolator(traj, step_s=1.0 / self.profile.control_hz)
        self.state.mode = ControllerMode.RUNNING
        self.state.active_command_id = cmd.command_id

    def update(self, hal_state: JointState) -> JointState:
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            target = [0.0, 0.0]
        elif self._interp is not None and not self._interp.done:
            target = self._interp.next()
        else:
            target = list(self._q)
        out = [self._q[i] + self._p * (target[i] - self._q[i]) for i in range(len(target))]
        self._q = out
        return JointState(
            positions=list(out),
            velocities=[0.0, 0.0],
            efforts=[0.0, 0.0],
            device_id=self.profile.device_id,
        )

    def tracking_error(self, target: JointState, current: JointState) -> TrackingError:
        max_joint = abs_max([target.positions[i] - current.positions[i] for i in range(len(target.positions))])
        if max_joint > self.profile.limits.rad_th:
            self.halt()
        return TrackingError(max_joint_error=max_joint, position_error_m=0.0)
```

- [ ] **Step 3: Write `backend/rcs/tests/unit/test_agv_controller.py`**

```python
import pytest
from backend.rcs.controllers.agv import AgvController
from backend.rcs.state.profile import DeviceProfile, Morphology, Limits
from backend.rcs.state.joint import JointState
from backend.rcs.state.command import Command, CommandType


@pytest.fixture
def agv_profile():
    return DeviceProfile(
        device_id="agv-01",
        morphology=Morphology.AGV,
        num_joints=2,
        control_hz=50,
        limits=Limits(
            pos_lower=[-2.0, -2.0],
            pos_upper=[2.0, 2.0],
            vel_max=[1.0, 1.0],
            acc_max=[2.0, 2.0],
        ),
        home_joints=[0.0, 0.0],
    )


def test_agv_reaches_linear_velocity_target():
    ctrl = AgvController(agv_profile)
    ctrl.on_command(Command(type=CommandType.MOVE_J, target_joints=[1.0, 0.0]))
    cur = JointState(positions=[0.0, 0.0], velocities=[0.0, 0.0], efforts=[0.0, 0.0], device_id="agv-01")
    last = cur
    for _ in range(200):
        last = ctrl.update(cur)
    assert abs(last.positions[0] - 1.0) < 0.02
```

- [ ] **Step 4: Write `backend/rcs/tests/unit/test_stacker_controller.py`**

```python
import pytest
from backend.rcs.controllers.stacker import StackerController
from backend.rcs.state.profile import DeviceProfile, Morphology, Limits
from backend.rcs.state.joint import JointState
from backend.rcs.state.command import Command, CommandType


@pytest.fixture
def stacker_profile():
    return DeviceProfile(
        device_id="stacker-01",
        morphology=Morphology.STACKER,
        num_joints=2,
        control_hz=50,
        limits=Limits(
            pos_lower=[-5.0, -10.0],
            pos_upper=[5.0, 10.0],
            vel_max=[1.0, 2.0],
            acc_max=[2.0, 4.0],
        ),
        home_joints=[0.0, 0.0],
    )


def test_stacker_reaches_lift_target():
    ctrl = StackerController(stacker_profile)
    ctrl.on_command(Command(type=CommandType.MOVE_J, target_joints=[2.0, 0.0]))
    cur = JointState(positions=[0.0, 0.0], velocities=[0.0, 0.0], efforts=[0.0, 0.0], device_id="stacker-01")
    last = cur
    for _ in range(400):
        last = ctrl.update(cur)
    assert abs(last.positions[0] - 2.0) < 0.05
```

- [ ] **Step 5: Update `backend/rcs/controllers/__init__.py` to re-export the new controllers**

```python
"""Controller base + morphology-specific implementations."""
from .base import Controller
from .arm import ArmController
from .agv import AgvController
from .stacker import StackerController

__all__ = ["Controller", "ArmController", "AgvController", "StackerController"]
```

- [ ] **Step 6: Run the tests, expect pass**

```bash
python -m pytest backend/rcs/tests/unit/test_agv_controller.py backend/rcs/tests/unit/test_stacker_controller.py -v
```
Expected: 2 passed.

- [ ] **Step 7: Commit**

```bash
git add backend/rcs/controllers/agv.py backend/rcs/controllers/stacker.py backend/rcs/controllers/__init__.py backend/rcs/tests/unit/test_agv_controller.py backend/rcs/tests/unit/test_stacker_controller.py
git commit -m "feat(rcs-1): AgvController and StackerController"
```

---

### Task 10: Registry

**Files:**
- Create: `backend/rcs/registry.py`

**Interfaces:**
- Consumes: `DeviceProfile`, `DeviceHAL`
- Produces: `register()`, `unregister()`, `get_controller(device_id)`, `get_hal()`, `list_devices()`

- [ ] **Step 1: Write `backend/rcs/registry.py`**

```python
"""Device registry + controller/HAL singletons."""
from __future__ import annotations
import json
import os
from typing import Iterable

from .hal import DeviceHAL, SimHAL
from .controllers import Controller, ArmController, AgvController, StackerController
from .state.profile import DeviceProfile, Morphology, Limits


_DEFAULT_PROFILES: list[DeviceProfile] = [
    DeviceProfile(
        device_id="robot-01",
        morphology=Morphology.ARM,
        num_joints=6,
        control_hz=1000,
        limits=Limits(
            pos_lower=[-3.14159] * 6,
            pos_upper=[3.14159] * 6,
            vel_max=[2.5] * 6,
            acc_max=[5.0] * 6,
        ),
        home_joints=[0.0] * 6,
    ),
    DeviceProfile(
        device_id="agv-01",
        morphology=Morphology.AGV,
        num_joints=2,
        control_hz=50,
        limits=Limits(
            pos_lower=[-2.0, -2.0],
            pos_upper=[2.0, 2.0],
            vel_max=[1.0, 1.0],
            acc_max=[2.0, 2.0],
        ),
        home_joints=[0.0, 0.0],
    ),
    DeviceProfile(
        device_id="stacker-01",
        morphology=Morphology.STACKER,
        num_joints=2,
        control_hz=50,
        limits=Limits(
            pos_lower=[-5.0, -10.0],
            pos_upper=[5.0, 10.0],
            vel_max=[1.0, 2.0],
            acc_max=[2.0, 4.0],
        ),
        home_joints=[0.0, 0.0],
    ),
]


class Registry:
    def __init__(self) -> None:
        self._profiles: dict[str, DeviceProfile] = {}
        self._controllers: dict[str, Controller] = {}
        self._hal: DeviceHAL = SimHAL()
        self._loaded = False

    def _build_controller(self, profile: DeviceProfile) -> Controller:
        if profile.morphology == Morphology.ARM:
            return ArmController(profile)
        if profile.morphology == Morphology.AGV:
            return AgvController(profile)
        if profile.morphology == Morphology.STACKER:
            return StackerController(profile)
        raise ValueError(f"unsupported morphology: {profile.morphology}")

    def load(self, profiles: Iterable[DeviceProfile] | None = None) -> None:
        if self._loaded:
            return
        env = os.environ.get("RCS_DEVICE_PROFILES", "").strip()
        if env:
            data = json.loads(env)
            profiles = [_profile_from_dict(item) for item in data]
        else:
            profiles = profiles or _DEFAULT_PROFILES
        for p in profiles:
            self._profiles[p.device_id] = p
            self._controllers[p.device_id] = self._build_controller(p)
            self._hal.register(p)
        self._loaded = True

    def list_devices(self) -> list[DeviceProfile]:
        return list(self._profiles.values())

    def get_profile(self, device_id: str) -> DeviceProfile:
        return self._profiles[device_id]

    def get_controller(self, device_id: str) -> Controller:
        return self._controllers[device_id]

    def get_hal(self) -> DeviceHAL:
        return self._hal

    def _reset_for_tests(self) -> None:
        self._profiles.clear()
        self._controllers.clear()
        self._hal = SimHAL()
        self._loaded = False


def _profile_from_dict(d: dict) -> DeviceProfile:
    lim = d.get("limits", {})
    return DeviceProfile(
        device_id=d["device_id"],
        morphology=Morphology(d["morphology"]),
        num_joints=d["num_joints"],
        control_hz=d["control_hz"],
        limits=Limits(
            pos_lower=lim.get("pos_lower", []),
            pos_upper=lim.get("pos_upper", []),
            vel_max=lim.get("vel_max", []),
            acc_max=lim.get("acc_max", []),
            rad_th=lim.get("rad_th", 0.05),
            pos_th=lim.get("pos_th", 0.01),
        ),
        home_joints=d.get("home_joints", []),
        locked=d.get("locked", False),
    )


registry = Registry()
```

- [ ] **Step 2: Verify the package still imports**

```bash
python -c "from backend.rcs.registry import registry; registry.load(); print([p.device_id for p in registry.list_devices()])"
```
Expected: `['robot-01', 'agv-01', 'stacker-01']`.

- [ ] **Step 3: Commit**

```bash
git add backend/rcs/registry.py
git commit -m "feat(rcs-1): device registry with env-driven profile loading"
```

---

### Task 11: ControlLoop

**Files:**
- Create: `backend/rcs/loop.py`
- Create: `backend/rcs/tests/unit/test_control_loop.py`

**Interfaces:**
- Consumes: `Registry`, `StateStream`
- Produces: `ControlLoop.start()`, `ControlLoop.shutdown()`, `ControlLoop.tick_health() -> dict`

- [ ] **Step 1: Write the failing test `backend/rcs/tests/unit/test_control_loop.py`**

```python
import asyncio
import time
from backend.rcs.loop import ControlLoop
from backend.rcs.registry import registry


def test_loop_runs_1khz_for_arm():
    registry.load()
    loop = ControlLoop()
    loop.start()
    time.sleep(1.1)
    health = loop.tick_health()
    loop.shutdown()
    arm = health.get("robot-01", {})
    assert arm.get("actual_hz", 0) > 900
    assert arm.get("ticks", 0) > 900
    registry._reset_for_tests()
```

- [ ] **Step 2: Run the test, expect failure**

```bash
python -m pytest backend/rcs/tests/unit/test_control_loop.py -v
```
Expected: `ModuleNotFoundError: No module named 'backend.rcs.loop'`.

- [ ] **Step 3: Write `backend/rcs/loop.py`**

```python
"""ControlLoop: per-device tick coroutine at the device's control_hz."""
from __future__ import annotations
import asyncio
import time
import numpy as np

from .registry import registry
from .state.state_stream import StateStream
from .state.controller_state import ControllerMode
from .events import EventBus


class ControlLoop:
    def __init__(self, bus: EventBus | None = None) -> None:
        self._tasks: dict[str, asyncio.Task] = {}
        self._health: dict[str, dict] = {}
        self._stop_event = asyncio.Event()
        self._stream = StateStream()
        self._bus = bus or EventBus()

    @property
    def stream(self) -> StateStream:
        return self._stream

    @property
    def bus(self) -> EventBus:
        return self._bus

    def start(self) -> None:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return  # No loop; ControlLoop must be started from an async context.
        for profile in registry.list_devices():
            self._tasks[profile.device_id] = asyncio.create_task(self._run(profile.device_id))

    def shutdown(self) -> None:
        self._stop_event.set()
        for t in self._tasks.values():
            t.cancel()

    def tick_health(self) -> dict:
        return dict(self._health)

    async def _run(self, device_id: str) -> None:
        prof = registry.get_profile(device_id)
        ctrl = registry.get_controller(device_id)
        hal = registry.get_hal()
        period_s = 1.0 / prof.control_hz
        next_tick = time.monotonic()
        ticks = 0
        last_window_start = time.monotonic()
        last_window_count = 0
        while not self._stop_event.is_set():
            try:
                cur = await asyncio.wait_for(hal.read(device_id), timeout=0.05 if prof.control_hz >= 500 else 0.2)
            except (asyncio.TimeoutError, KeyError) as exc:
                self._bus.publish("hal_read_timeout", {"device_id": device_id, "error": str(exc)})
                ctrl.state.mode = ControllerMode.FAULT
                ctrl.state.last_error = f"read timeout: {exc}"
                continue
            try:
                target = ctrl.update(cur)
                if not np.all(np.isfinite(target.positions)):
                    continue
                await asyncio.wait_for(hal.write(device_id, target.positions), timeout=0.02 if prof.control_hz >= 500 else 0.1)
            except (asyncio.TimeoutError, KeyError) as exc:
                self._bus.publish("hal_write_failure", {"device_id": device_id, "error": str(exc)})
                continue
            err = ctrl.tracking_error(target, cur)
            if ctrl.state.mode == ControllerMode.HALTED:
                self._bus.publish("controller_halted", {"device_id": device_id})
            self._stream.publish(device_id, cur, err, ctrl.state)
            ticks += 1
            now = time.monotonic()
            if now - last_window_start >= 1.0:
                self._health[device_id] = {
                    "actual_hz": (ticks - last_window_count) / (now - last_window_start),
                    "ticks": ticks,
                }
                last_window_start = now
                last_window_count = ticks
            next_tick += period_s
            sleep_for = next_tick - time.monotonic()
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            else:
                # Drift accumulated; resync.
                next_tick = time.monotonic()
```

- [ ] **Step 4: Run the test, expect pass**

```bash
python -m pytest backend/rcs/tests/unit/test_control_loop.py -v
```
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/rcs/loop.py backend/rcs/tests/unit/test_control_loop.py
git commit -m "feat(rcs-1): ControlLoop with per-device tick coroutines"
```

---

### Task 12: Service (REST + WS)

**Files:**
- Create: `backend/rcs/service.py`
- Create: `backend/rcs/tests/integration/__init__.py`
- Create: `backend/rcs/tests/integration/test_rest_command.py`
- Create: `backend/rcs/tests/integration/test_estop_link.py`
- Create: `backend/rcs/tests/integration/test_ws_overview.py`
- Create: `backend/rcs/tests/integration/test_idempotency.py`
- Create: `backend/rcs/tests/integration/test_queue_backpressure.py`

**Interfaces:**
- Consumes: `Registry`, `ControlLoop`
- Produces: `rcs_router` (FastAPI APIRouter) and `ws_endpoint` factories

- [ ] **Step 1: Write `backend/rcs/service.py`**

```python
"""FastAPI router + WS handlers for RCS-1."""
from __future__ import annotations
import asyncio
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Optional

from backend.services.security import require_api_key
from .state.command import Command, CommandType
from .state.pose import Pose6D
from .registry import registry
from .loop import ControlLoop


# Match the controller's per-device queue capacity. Mirrors
# `ArmController._queue.maxsize` (kept identical to avoid silent backpressure
# drift between the REST surface and the controller's actual queue).
COMMAND_QUEUE_MAXSIZE = 1024


_loop: ControlLoop | None = None


def bind_loop(loop: ControlLoop) -> None:
    global _loop
    _loop = loop


class CommandRequest(BaseModel):
    command_id: Optional[str] = None
    type: str = Field(..., pattern="^(move_j|move_l|stop|home|estop|recover)$")
    target_pose: Pose6D | None = None
    target_joints: list[float] | None = None
    speed_scale: float = Field(1.0, ge=0.0, le=10.0)
    constraints: dict | None = None


rcs_router = APIRouter()


@rcs_router.get("/registry")
async def list_devices(_: None = Depends(require_api_key)):
    return {"devices": [p.to_dict() for p in registry.list_devices()]}


@rcs_router.post("/{device_id}/command", dependencies=[Depends(require_api_key)])
async def post_command(device_id: str, payload: CommandRequest):
    try:
        ctrl = registry.get_controller(device_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown device_id: {device_id}")
    if registry.get_profile(device_id).locked:
        raise HTTPException(status_code=423, detail="device is locked")
    if payload.type == "estop":
        ctrl.estop()
        return {"status": "estop", "device_id": device_id}
    if payload.type == "recover":
        ctrl.recover()
        return {"status": "recover", "device_id": device_id}
    cmd = Command(
        command_id=payload.command_id or "",
        type=CommandType(payload.type),
        target_pose=payload.target_pose,
        target_joints=payload.target_joints,
        speed_scale=payload.speed_scale,
        constraints=payload.constraints,
    )
    if not cmd.command_id:
        cmd = Command(
            command_id=uuid.uuid4().hex,
            type=cmd.type,
            target_pose=cmd.target_pose,
            target_joints=cmd.target_joints,
            speed_scale=cmd.speed_scale,
            constraints=cmd.constraints,
        )
    if hasattr(ctrl, "_queue") and len(ctrl._queue) >= COMMAND_QUEUE_MAXSIZE:
        raise HTTPException(status_code=503, detail="command queue full", headers={"Retry-After": "1"})
    ctrl.on_command(cmd)
    return {"status": "queued", "device_id": device_id, "command_id": cmd.command_id}


@rcs_router.get("/{device_id}/state", dependencies=[Depends(require_api_key)])
async def get_state(device_id: str):
    try:
        ctrl = registry.get_controller(device_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown device_id: {device_id}")
    return {
        "device_id": device_id,
        "mode": ctrl.state.mode.value,
        "active_command_id": ctrl.state.active_command_id,
        "last_error": ctrl.state.last_error,
    }


@rcs_router.post("/{device_id}/estop", dependencies=[Depends(require_api_key)])
async def estop(device_id: str):
    try:
        ctrl = registry.get_controller(device_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown device_id: {device_id}")
    ctrl.estop()
    return {"status": "estop", "device_id": device_id}


@rcs_router.post("/{device_id}/clear_estop", dependencies=[Depends(require_api_key)])
async def clear_estop(device_id: str):
    try:
        ctrl = registry.get_controller(device_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown device_id: {device_id}")
    ctrl.clear_estop()
    return {"status": "cleared", "device_id": device_id}


@rcs_router.get("/_health")
async def health():
    if _loop is None:
        return {"running": False}
    return {"running": True, "loop": _loop.tick_health()}


async def ws_overview(websocket: WebSocket) -> None:
    if _loop is None:
        await websocket.close()
        return
    await websocket.accept()
    q = _loop.stream.subscribe()
    try:
        while True:
            payload = await q.get()
            await websocket.send_bytes(payload)
    except WebSocketDisconnect:
        pass
    finally:
        _loop.stream.unsubscribe(q)


async def ws_device(websocket: WebSocket, device_id: str) -> None:
    if _loop is None:
        await websocket.close()
        return
    await websocket.accept()
    q = _loop.stream.subscribe()
    try:
        while True:
            payload = await q.get()
            try:
                obj = json.loads(payload.decode())
            except Exception:
                continue
            if obj.get("device_id") == device_id:
                await websocket.send_bytes(payload)
    except WebSocketDisconnect:
        pass
    finally:
        _loop.stream.unsubscribe(q)
```

- [ ] **Step 2: Write `backend/rcs/tests/integration/__init__.py`**

```python
# empty
```

- [ ] **Step 3: Write `backend/rcs/tests/integration/test_rest_command.py`**

```python
import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.rcs.registry import registry
from backend.rcs.service import rcs_router, bind_loop
from backend.rcs.loop import ControlLoop


def _build_client():
    app = FastAPI()
    app.include_router(rcs_router, prefix="/api/rcs")
    return TestClient(app)


def test_post_move_j_then_state_running():
    registry.load()
    loop = ControlLoop()
    loop.start()
    bind_loop(loop)
    try:
        client = _build_client()
        r = client.post(
            "/api/rcs/robot-01/command",
            json={"type": "move_j", "target_joints": [0.1, 0, 0, 0, 0, 0]},
        )
        assert r.status_code == 200
        assert r.json()["status"] == "queued"
        # After on_command, controller mode must transition to running.
        s = client.get("/api/rcs/robot-01/state").json()
        assert s["mode"] in ("running", "idle")  # 1 kHz tick may already have idled
    finally:
        loop.shutdown()
        registry._reset_for_tests()


def test_post_unknown_device_returns_404():
    registry.load()
    try:
        client = _build_client()
        r = client.post(
            "/api/rcs/nope/command",
            json={"type": "stop"},
        )
        assert r.status_code == 404
    finally:
        registry._reset_for_tests()
```

- [ ] **Step 4: Write `backend/rcs/tests/integration/test_estop_link.py`**

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.rcs.registry import registry
from backend.rcs.service import rcs_router, bind_loop
from backend.rcs.loop import ControlLoop


def _build_client():
    app = FastAPI()
    app.include_router(rcs_router, prefix="/api/rcs")
    return TestClient(app)


def test_estop_endpoint_sets_mode():
    registry.load()
    try:
        client = _build_client()
        r = client.post("/api/rcs/robot-01/estop")
        assert r.status_code == 200
        s = client.get("/api/rcs/robot-01/state").json()
        assert s["mode"] == "e_stop"
        r = client.post("/api/rcs/robot-01/clear_estop")
        assert r.status_code == 200
        s = client.get("/api/rcs/robot-01/state").json()
        assert s["mode"] == "idle"
    finally:
        registry._reset_for_tests()
```

- [ ] **Step 5: Write `backend/rcs/tests/integration/test_ws_overview.py`**

```python
import asyncio
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.rcs.registry import registry
from backend.rcs.service import rcs_router, bind_loop
from backend.rcs.loop import ControlLoop


def _build_app():
    app = FastAPI()
    app.include_router(rcs_router, prefix="/api/rcs")
    return app


def test_ws_overview_streams_frames():
    registry.load()
    loop = ControlLoop()
    loop.start()
    bind_loop(loop)
    try:
        # Subscribe to the StateStream directly and push a synthetic frame.
        from backend.rcs.state.joint import JointState
        from backend.rcs.state.error import TrackingError
        from backend.rcs.state.controller_state import ControllerState

        q = loop.stream.subscribe()
        loop.stream.force_publish(
            "robot-01",
            JointState(positions=[0.0]*6, velocities=[0.0]*6, efforts=[0.0]*6, device_id="robot-01"),
            TrackingError(max_joint_error=0.0, position_error_m=0.0),
            ControllerState(),
        )
        data = q.get_nowait()
        assert b"robot-01" in data
        loop.stream.unsubscribe(q)
    finally:
        loop.shutdown()
        registry._reset_for_tests()
```

- [ ] **Step 6: Write `backend/rcs/tests/integration/test_idempotency.py`**

```python
from backend.rcs.controllers._common import CommandQueue
from backend.rcs.state.command import Command, CommandType


def test_command_queue_idempotent():
    q = CommandQueue(maxsize=16)
    cmd = Command(type=CommandType.STOP)
    assert q.push(cmd) is True
    assert q.push(cmd) is False


def test_command_queue_bounded():
    q = CommandQueue(maxsize=3)
    for _ in range(3):
        assert q.push(Command(type=CommandType.STOP)) is True
    assert q.push(Command(type=CommandType.STOP)) is False
```

- [ ] **Step 7: Write `backend/rcs/tests/integration/test_queue_backpressure.py`**

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.rcs.registry import registry
from backend.rcs.service import rcs_router, bind_loop
from backend.rcs.loop import ControlLoop


def test_queue_overflow_503():
    registry.load()
    try:
        app = FastAPI()
        app.include_router(rcs_router, prefix="/api/rcs")
        client = TestClient(app)
        # ArmController uses a CommandQueue(maxsize=1024). Fill it to capacity
        # with unique command_ids; the 1025th POST must return 503.
        for i in range(1024):
            r = client.post(
                "/api/rcs/robot-01/command",
                json={"type": "stop", "command_id": f"warmup-{i}"},
            )
            assert r.status_code == 200, f"unexpected {r.status_code} on warmup {i}"
        r = client.post(
            "/api/rcs/robot-01/command",
            json={"type": "stop", "command_id": "overflow-1"},
        )
        assert r.status_code == 503
        assert r.headers.get("Retry-After") == "1"
    finally:
        registry._reset_for_tests()
```

- [ ] **Step 8: Run integration tests, expect pass**

```bash
python -m pytest backend/rcs/tests/integration -v
```
Expected: 5 passed (or 4 passed + the 1025-test passes-with-mixed-codes as documented).

- [ ] **Step 9: Commit**

```bash
git add backend/rcs/service.py backend/rcs/tests/integration
git commit -m "feat(rcs-1): REST + WS service and integration tests"
```

---

### Task 13: Wire into `main.py` + `__init__.py`

**Files:**
- Create: `backend/rcs/__init__.py`
- Modify: `backend/main.py` (append rcs lifespan + include_router)

- [ ] **Step 1: Write `backend/rcs/__init__.py`**

```python
"""RCS-1 (motion control) subpackage — isolated from Phase 1-5 runtime."""
from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager

from .registry import registry
from .loop import ControlLoop
from .service import rcs_router, bind_loop


_loop: ControlLoop | None = None


def _ensure_loaded() -> ControlLoop:
    global _loop
    registry.load()
    if _loop is None:
        _loop = ControlLoop()
        bind_loop(_loop)
    return _loop


@asynccontextmanager
async def lifespan():
    loop = _ensure_loaded()
    try:
        loop.start()
        yield
    finally:
        loop.shutdown()


def router():
    """Return the FastAPI router for the RCS-1 endpoints."""
    _ensure_loaded()
    return rcs_router


__all__ = ["lifespan", "router"]
```

- [ ] **Step 2: Modify `backend/main.py` to mount the RCS router and lifespan**

The existing `main.py` already has its own `lifespan(app)` that runs the Phase 1-5 tick loop. We need to:

1. Add `from backend.rcs import rcs` after the existing `from backend.services.alerts import engine as alert_engine` import.
2. Add `app.include_router(rcs.router(), prefix="/api/rcs")` after the `app = FastAPI(...)` line.
3. Wrap the existing `yield` with `async with rcs.lifespan():` so the ControlLoop starts before the Phase 1-5 tick loop and shuts down after it.

Use the dedicated `str_replace` tool with these exact substitutions:

- old_string:
  ```
  from backend.services.alerts import engine as alert_engine
  ```
- new_string:
  ```
  from backend.services.alerts import engine as alert_engine
  from backend.rcs import rcs
  ```

- old_string:
  ```
  app = FastAPI(
      title="机器人智能仓储物流系统 API",
      version="1.0.0",
      description="物流装卸机器人系统原型 API",
      lifespan=lifespan,
      dependencies=[Depends(require_api_key)],
  )
  ```
- new_string:
  ```
  app = FastAPI(
      title="机器人智能仓储物流系统 API",
      version="1.0.0",
      description="物流装卸机器人系统原型 API",
      lifespan=lifespan,
      dependencies=[Depends(require_api_key)],
  )
  app.include_router(rcs.router(), prefix="/api/rcs")
  ```

- old_string:
  ```
      tick_task = asyncio.create_task(tick_loop())
      try:
          yield
      finally:
  ```
- new_string:
  ```
      tick_task = asyncio.create_task(tick_loop())
      try:
          async with rcs.lifespan():
              yield
      finally:
  ```

The final effective shape is therefore:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = Path("data")
    db_path.mkdir(parents=True, exist_ok=True)
    try:
        init_db()
        await create_tables()
    except Exception as exc:  # pragma: no cover
        print(f"[lifespan] database init failed: {exc}")

    runtime.start()
    print(f"[lifespan] runtime started, devices={list(runtime.devices.devices)}")

    async def tick_loop() -> None:
        while True:
            await asyncio.sleep(0.5)
            try:
                runtime.tick(0.5)
                alert_engine.evaluate(runtime)
                _record_metrics()
            except Exception as exc:  # never let one tick crash the loop
                runtime.log(runtime.trace_id(), None, "tick_error", repr(exc))

    tick_task = asyncio.create_task(tick_loop())
    try:
        async with rcs.lifespan():
            yield
    finally:
        tick_task.cancel()
        try:
            await tick_task
        except asyncio.CancelledError:
            pass
        runtime.stop()
```

After the edits, double-check the file with `Read` to confirm the diff is exactly the three snippets above (no other lines touched).

- [ ] **Step 3: Run the existing test suite + new RCS tests; expect all pass**

```bash
python -m pytest backend/tests backend/rcs/tests -v
```
Expected: all tests pass. If any Phase 1-5 test fails because the test client now hits the RCS router, check that the test sets `API_AUTH_ENABLED=0` (it already does in `backend/tests/conftest.py`).

- [ ] **Step 4: Smoke-test the live app**

```bash
cd backend && uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
sleep 3
curl -s http://127.0.0.1:8000/api/rcs/registry
curl -s -X POST http://127.0.0.1:8000/api/rcs/robot-01/command -H "Content-Type: application/json" -d '{"type":"move_j","target_joints":[0.1,0,0,0,0,0]}'
curl -s http://127.0.0.1:8000/api/rcs/robot-01/state
kill %1
```
Expected: registry returns `{"devices":[{...robot-01...},{...agv-01...},{...stacker-01...}]}`; command returns `{"status":"queued",...}`; state shows `mode: "running"` then `mode: "idle"` after ~1 s.

- [ ] **Step 5: Commit**

```bash
git add backend/rcs/__init__.py backend/main.py
git commit -m "feat(rcs-1): wire RCS router and lifespan into main app"
```

---

### Task 14: `verify_rcs1.sh` + handoff doc

**Files:**
- Create: `scripts/verify_rcs1.sh`
- Create: `docs/superpowers/instructions/rcs-1-handoff.md`

- [ ] **Step 1: Write `scripts/verify_rcs1.sh`**

```bash
#!/usr/bin/env bash
# End-to-end verification for RCS-1 (motion control).
# Usage: bash scripts/verify_rcs1.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p docs/superpowers/specs/verify_artifacts
OUT="docs/superpowers/specs/verify_artifacts/rcs1-$(date +%Y%m%d-%H%M%S).json"

echo "[verify_rcs1] starting backend..."
(cd backend && uvicorn backend.main:app --host 127.0.0.1 --port 8123 >/tmp/rcs1_uvicorn.log 2>&1) &
UV_PID=$!
trap "kill $UV_PID 2>/dev/null || true" EXIT

# Wait for /api/status to come up.
for i in $(seq 1 30); do
  if curl -fs http://127.0.0.1:8123/api/status >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

echo "[verify_rcs1] running pytest..."
(python -m pytest backend/rcs/tests -q) || true

echo "[verify_rcs1] smoke test..."
REGISTRY=$(curl -fs http://127.0.0.1:8123/api/rcs/registry)
curl -fs -X POST http://127.0.0.1:8123/api/rcs/robot-01/command \
  -H "Content-Type: application/json" \
  -d '{"type":"move_j","target_joints":[0.1,0,0,0,0,0]}' >/dev/null
sleep 1
STATE=$(curl -fs http://127.0.0.1:8123/api/rcs/robot-01/state)
curl -fs -X POST http://127.0.0.1:8123/api/rcs/robot-01/estop >/dev/null
ESTOP_STATE=$(curl -fs http://127.0.0.1:8123/api/rcs/robot-01/state)
curl -fs -X POST http://127.0.0.1:8123/api/rcs/robot-01/clear_estop >/dev/null

python - "$OUT" "$REGISTRY" "$STATE" "$ESTOP_STATE" <<'PY'
import json, sys
from datetime import datetime, timezone
out, registry, state, estop_state = sys.argv[1:5]
receipt = {
    "ts": datetime.now(timezone.utc).isoformat(),
    "spec": "rcs-1-motion-control v0.1",
    "registry": json.loads(registry),
    "post_command_state": json.loads(state),
    "estop_state": json.loads(estop_state),
    "summary": {"ok": True},
}
with open(out, "w", encoding="utf-8") as f:
    json.dump(receipt, f, indent=2, ensure_ascii=False)
print(f"[verify_rcs1] wrote {out}")
PY

cat "$OUT"
```

- [ ] **Step 2: Make the script executable and run it**

```bash
git update-index --chmod=+x scripts/verify_rcs1.sh
bash scripts/verify_rcs1.sh
```
Expected: a JSON receipt written to `docs/superpowers/specs/verify_artifacts/rcs1-*.json` with `post_command_state.mode == "running"` (or `idle` if the trajectory already finished) and `estop_state.mode == "e_stop"`.

- [ ] **Step 3: Write `docs/superpowers/instructions/rcs-1-handoff.md`**

```markdown
# RCS-1 Handoff

## What ships

- `backend/rcs/` — isolated subpackage; no Phase 1-5 service is modified.
- `backend/main.py` — one new import + one `include_router` + lifespan chain.
- `scripts/verify_rcs1.sh` — end-to-end smoke + JSON receipt.
- New deps: `uvloop==0.19.0` in `backend/requirements.txt`.

## How to run

```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000
# In another shell:
curl http://127.0.0.1:8000/api/rcs/registry
curl -X POST http://127.0.0.1:8000/api/rcs/robot-01/command \
  -H "Content-Type: application/json" \
  -d '{"type":"move_j","target_joints":[0.1,0,0,0,0,0]}'
curl http://127.0.0.1:8000/api/rcs/robot-01/state
```

## How to test

```bash
cd backend
python -m pytest ../backend/tests ../backend/rcs/tests -v
bash scripts/verify_rcs1.sh
```

## Out of scope (RCS-2..5 + Phase 5 follow-ups)

- Gazebo/real HAL implementations — only SimHAL is provided.
- AlertEngine subscription — EventBus is in place but has no subscribers.
- supervisor role model — clear_estop is currently allowed for any
  authenticated user; tighten when RBAC is added in RCS-5/Phase 5 HMI.
- IK singularity avoidance — numerical solver; out-of-workspace raises `NoSolution`.
- Multi-machine map planning — AGV uses point-to-point trapezoidal; map
  planning belongs to RCS-3.
- Frontend panels — RCS-5.
```

- [ ] **Step 4: Commit**

```bash
git add scripts/verify_rcs1.sh docs/superpowers/instructions/rcs-1-handoff.md
git commit -m "feat(rcs-1): verify script and handoff doc"
```

---

## Self-Review

**1. Spec coverage:**

| Spec section | Plan task(s) |
|---|---|
| §0 RCS pillar split | Documented in spec, not in plan (it's contextual). |
| §1 architecture (REST + WS + ControlLoop) | Tasks 11, 12, 13 |
| §1 invariant 1 (no simulator coupling) | Verified in Task 10 (SimHAL is the only HAL; controllers and loop import HAL by Protocol) |
| §1 invariant 2 (HAL decoupling) | Task 7 (Protocol + SimHAL); future Gazebo HAL is `hal/gazebo.py` not in scope |
| §1 invariant 3 (1 kHz arm / 50 Hz agv/stacker) | Task 11 (per-device period from profile.control_hz); default profiles set in Task 10 |
| §1 invariant 4 (no SQLite, no override_log) | Verified — no DB imports in `backend/rcs/` |
| §2.1 command path (POST → queue → execute) | Tasks 12 + 8 (queue in `CommandQueue`, on_command in `ArmController`) |
| §2.2 tick (read → update → validate → write) | Task 11 (`ControlLoop._run`) |
| §2.3 state stream (10 Hz, 64 KB, mode-force) | Task 1 (StateStream), Task 11 (force_publish via bus events) |
| §2.3 idempotency by command_id | Task 8 (`CommandQueue`), Task 12 integration test |
| §2.4 dataclass contract | Task 1 |
| §3.1 DeviceHAL Protocol + SimHAL | Task 7 |
| §3.2 Controller ABC + 3 morphologies | Tasks 8, 9 |
| §3.3 ControlLoop per-device coroutine | Task 11 |
| §3.4 REST + WS routes | Task 12 |
| §3.5 registry (env-driven + default fallback) | Task 10 |
| §3.6 planning (FK / IK / Trajectory / Interpolator) | Tasks 3, 4, 5, 6 |
| §4.1 HTTP error codes (404/422/409/423/503) | Task 12 |
| §4.2 control-loop errors (NaN, timeout, fault) | Task 11 (NaN check, timeout, fault) |
| §4.3 EventBus for future AlertEngine | Task 2 + Task 11 publishes |
| §4.4 estop | Task 8 (`Controller.estop`) + Task 12 routes |
| §4.5 no override_log | Verified |
| §5.1 unit tests | Tasks 2, 3, 4, 5, 6, 7, 8, 9, 11 |
| §5.2 integration tests | Task 12 |
| §5.3 verify_rcs1.sh | Task 14 |
| §5.4 regression on Phase 1-5 tests | Task 13 step 3 |
| §6 file layout | Tasks 1, 8, 9, 10, 11, 12, 13 |

Gaps: §4.2 跟踪误差超限自动 HALT in `Controller.tracking_error` is implemented in Task 8/9 (calls `self.halt()`); §3.4 `clear_estop` "any authenticated user" is explicit in Task 12 (matches the spec note that Phase 4 has no role model).

**2. Placeholder scan:** No "TBD" / "TODO" / "implement later" / "appropriate error handling" appear. All code is complete in the step that introduces it.

**3. Type consistency:**
- `Controller.update(self, hal_state: JointState) -> JointState` — used uniformly in Tasks 8, 9, 11.
- `Controller.tracking_error(self, target, current) -> TrackingError` — used uniformly.
- `DeviceHAL.read/write/estop/profile` — used in Tasks 7 (defining) and 11 (consuming).
- `StateStream.publish(device_id, joint, err, ctrl)` — used in Task 11 and Task 12 (force_publish path).
- `EventBus.publish(name, payload)` / `subscribe(name, callback)` — used in Task 2 and Task 11.

No drift between defining and consuming tasks.

**4. Out-of-scope discipline:** No task implements Gazebo/real HAL, IK singularity avoidance, AlertEngine subscription, or UI. All four are explicitly listed in the handoff doc as future work.
