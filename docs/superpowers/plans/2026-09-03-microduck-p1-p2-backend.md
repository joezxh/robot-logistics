# Microduck Backend Implementation Plan (P1 模型接入 + P2 仿真环境)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the Microduck biped MJCF models into robot-logic and deliver a floating-base locomotion Gym environment that implements the official 61-dim observation / 14-dim action contract.

**Architecture:** Assets (7 MJCF variants + 43 STL) are vendored into `simulation/backend/assets/robots/microduck/`. A data-driven variant registry (`microduck_cfg.py`) drives a single `MicroduckEnv` implementation. Because `MuJoCoEngine` is arm-oriented (its `step()` teleports `qpos` and it injects a TCP site), physics uses a new additive `FreeBaseMuJoCoEngine` that steps via `data.ctrl` + `mj_step`; scenes are assembled by reusing the existing `ModelComposer` with an empty prefix so joint names stay intact.

**Tech Stack:** Python 3.11, MuJoCo 3.12.0, Gymnasium 1.3.0, NumPy, pytest 9.1.1, stable-baselines3 2.9.0

### Spec deviation (important — read before starting)

The approved spec §3 says "复用 `MuJoCoEngine`". **That is not viable** and this plan amends it:

- `MuJoCoEngine.step()` does `data.qpos[:] = action` then `mj_forward` + `mj_step` — it **teleports qpos instead of driving `ctrl`**. With `nu=14` but `nq=21`, a 14-element action would overwrite the freejoint pose.
- `_detect_robot_config()` treats the 14 joints as an "arm", finds no TCP site, and calls `_inject_tcp_site()` which **rewrites the MJCF and reloads the model**.
- With no `home` keyframe, `_qpos_home = zeros(nq)` → the freejoint quaternion is all-zero (invalid).

This plan therefore **adds** `FreeBaseMuJoCoEngine` and leaves `MuJoCoEngine` (and its 11 existing tests) untouched.

### Environment (verified working)

```powershell
$env:PYTHONPATH = "d:/projects/robot-logic/simulation/backend"
Set-Location d:/projects/robot-logic/simulation/backend
$PY = "d:/projects/robot-logic/simulation/backend/rcs_sim_core/.venv/Scripts/python.exe"
& $PY -m pytest rcs_env/tests/test_envs.py -q     # baseline: 11 passed
```

---

## File Structure

| File | Responsibility |
|---|---|
| `simulation/backend/assets/robots/microduck/**` | Vendored MJCF (7 variants) + `assets/*.stl` |
| `simulation/backend/rcs_env/envs/microduck_cfg.py` | **Contract tables + variant registry** (single source of truth) |
| `simulation/backend/rcs_env/freebase_engine.py` | **`FreeBaseMuJoCoEngine`** — ctrl-driven stepping for freejoint robots |
| `simulation/backend/rcs_env/envs/microduck.py` | **`MicroduckEnv`** — obs/action/reward/termination |
| `shared/python/robot_contracts/kinematics.py` | Add `RobotType.MICRODUCK` |
| `simulation/backend/rcs_env/envs/base.py` | Register `rcs/microduck-*-v0` gym IDs |
| `simulation/backend/rcs_env/envs/__init__.py` | Export new symbols |
| `simulation/backend/rcs_env/tests/test_microduck.py` | Contract + env tests |

### Verified model facts (measured, do not re-derive)

- All 7 variants: `nu = 14`; **no mouth actuator in any variant** (mouth exists only on the real 15-servo bus).
- Base variants `nq = 21`, `nv = 20` (7 freejoint + 14 joints).
- `walk_backlash` / `groundcontact_backlash`: `nq = 35` (+14 `passive_*_backlash` hinges).
- `rollers`: `nq = 25` (+4 `passive_*wheel`); `rollers_backlash`: `nq = 39`.
- `robot_walk.xml` joint order is **exactly** `trunk_base_freejoint` + the 14 `POLICY_JOINTS` in policy order.

---

### Task 1: Vendor assets and prove all 7 variants load

**Files:**
- Create: `simulation/backend/assets/robots/microduck/**`
- Test: `simulation/backend/rcs_env/tests/test_microduck.py`

- [ ] **Step 1: Write the failing test**

```python
# simulation/backend/rcs_env/tests/test_microduck.py
import os
import mujoco

MICRODUCK_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "robots", "microduck",
)

VARIANT_XMLS = (
    "robot_walk.xml",
    "robot_groundcontact.xml",
    "robot_allcollisions.xml",
    "robot_groundcontact_rollers.xml",
    "robot_walk_backlash.xml",
    "robot_groundcontact_backlash.xml",
    "robot_groundcontact_rollers_backlash.xml",
)


def test_all_variants_present_and_load():
    for xml in VARIANT_XMLS:
        path = os.path.join(MICRODUCK_DIR, xml)
        assert os.path.exists(path), f"missing MJCF: {path}"
        m = mujoco.MjModel.from_xml_path(path)
        assert m.nu == 14, f"{xml}: expected nu=14, got {m.nu}"


def test_walk_joint_order_matches_policy_order():
    from rcs_env.envs.microduck_cfg import POLICY_JOINTS
    m = mujoco.MjModel.from_xml_path(os.path.join(MICRODUCK_DIR, "robot_walk.xml"))
    joints = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
    assert joints[0] == "trunk_base_freejoint"
    assert tuple(joints[1:]) == POLICY_JOINTS
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v`
Expected: FAIL — `missing MJCF` (assets not copied yet).

- [ ] **Step 3: Copy the assets (no `.part` files)**

```powershell
$src = "d:\projects\github\microduck_rl\src\mjlab_microduck\robot\microduck"
$dst = "d:\projects\robot-logic\simulation\backend\assets\robots\microduck"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
Copy-Item "$src\*.xml" $dst
Copy-Item "$src\assets" $dst -Recurse
Get-ChildItem $dst -Recurse -Include *.stl | Measure-Object | Select-Object Count
```

Expected: `Count = 43` STL files; 12 XML files (7 robot + 5 scene/sensor extras).

- [ ] **Step 4: Run test to verify it passes**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add simulation/backend/assets/robots/microduck rcs_env/tests/test_microduck.py
git commit -m "feat(microduck): vendor 7 MJCF variants + 43 STL meshes (P1)"
```

---

### Task 2: Add `RobotType.MICRODUCK`

**Files:**
- Modify: `shared/python/robot_contracts/kinematics.py:44-48`
- Test: `simulation/backend/rcs_env/tests/test_microduck.py`

- [ ] **Step 1: Write the failing test**

```python
def test_robot_type_microduck_exists():
    from robot_contracts import RobotType
    assert RobotType.MICRODUCK.value == "Microduck"
    assert RobotType.MICRODUCK in RobotType.get_all()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py::test_robot_type_microduck_exists -v`
Expected: FAIL — `AttributeError: MICRODUCK`.

- [ ] **Step 3: Implement**

In `shared/python/robot_contracts/kinematics.py`, inside `class RobotType`, after `YAM = "Yam"`:

```python
    # robot-logic biped (floating base, freejoint root)
    MICRODUCK = "Microduck"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py::test_robot_type_microduck_exists -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add shared/python/robot_contracts/kinematics.py rcs_env/tests/test_microduck.py
git commit -m "feat(contracts): add RobotType.MICRODUCK (P1)"
```

---

### Task 3: Contract tables + variant registry (`microduck_cfg.py`)

**Files:**
- Create: `simulation/backend/rcs_env/envs/microduck_cfg.py`
- Test: `simulation/backend/rcs_env/tests/test_microduck.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_contract_dimensions():
    from rcs_env.envs.microduck_cfg import (
        N_OBS, N_ACTION, N_MOTOR_SLOTS, MOUTH_SLOT,
        POLICY_JOINTS, MOTOR_SLOTS, ACTION_TO_SLOT, BUS_IDS, HOME_POSE,
    )
    assert (N_OBS, N_ACTION, N_MOTOR_SLOTS) == (61, 14, 15)
    assert len(POLICY_JOINTS) == 14
    assert len(MOTOR_SLOTS) == 15
    assert len(ACTION_TO_SLOT) == 14
    assert MOTOR_SLOTS[MOUTH_SLOT] == "mouth"
    assert 9 not in ACTION_TO_SLOT          # mouth slot is never policy-driven
    assert set(ACTION_TO_SLOT) == set(range(15)) - {9}
    assert BUS_IDS["mouth"] == 34
    assert len(BUS_IDS) == 15
    assert set(HOME_POSE) == set(POLICY_JOINTS)
    assert HOME_POSE["left_hip_roll"] == -0.0873
    assert HOME_POSE["right_hip_roll"] == 0.0873


def test_variant_registry_covers_all_seven():
    from rcs_env.envs.microduck_cfg import VARIANTS, MICRODUCK_DIR
    import os
    assert len(VARIANTS) == 7
    for name, v in VARIANTS.items():
        assert os.path.exists(v.mjcf_path), f"{name}: {v.mjcf_path} missing"
    assert VARIANTS["walk"].passive_prefixes == ()
    assert VARIANTS["rollers"].passive_prefixes == ("passive_",)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v -k "contract or variant_registry"`
Expected: FAIL — `ModuleNotFoundError: rcs_env.envs.microduck_cfg`.

- [ ] **Step 3: Implement `microduck_cfg.py`**

```python
"""Microduck contract tables, home pose and MJCF variant registry.

Single source of truth for the official deployment contract (61-dim observation,
14-dim action) documented in
``docs/superpowers/specs/2026-09-03-microduck-design.md`` §7.

Kept out of ``configs.py`` because that module is the fixed-base arm roster;
biped variants carry extra fields (home pose, passive-joint prefixes).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

# ---- assets --------------------------------------------------------------- #
_ASSETS_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "assets")
)
MICRODUCK_DIR = os.path.join(_ASSETS_ROOT, "robots", "microduck")

# ---- contract dimensions -------------------------------------------------- #
N_OBS = 61
N_ACTION = 14
N_MOTOR_SLOTS = 15
MOUTH_SLOT = 9

#: 14 policy joints in policy-action order (verified == robot_walk.xml order).
POLICY_JOINTS: tuple[str, ...] = (
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
    "neck_pitch", "head_pitch", "head_yaw", "head_roll",
    "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle",
)

#: 15-slot motor target array order; the mouth occupies slot 9.
MOTOR_SLOTS: tuple[str, ...] = (
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
    "neck_pitch", "head_pitch", "head_yaw", "head_roll",
    "mouth",
    "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle",
)

#: action index -> MOTOR_SLOTS index. Slot 9 (mouth) is skipped by construction.
ACTION_TO_SLOT: tuple[int, ...] = (0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14)

#: Dynamixel bus IDs (docs/microduck.md §2.1). Mouth is not a policy joint.
BUS_IDS: Mapping[str, int] = {
    "left_hip_yaw": 20, "left_hip_roll": 21, "left_hip_pitch": 22,
    "left_knee": 23, "left_ankle": 24,
    "neck_pitch": 30, "head_pitch": 31, "head_yaw": 32, "head_roll": 33,
    "mouth": 34,
    "right_hip_yaw": 10, "right_hip_roll": 11, "right_hip_pitch": 12,
    "right_knee": 13, "right_ankle": 14,
}

#: home pose (STAND2) — docs/microduck.md / microduck_constants.HOME_FRAME (rad).
HOME_POSE: Mapping[str, float] = {
    "left_hip_yaw": 0.0, "right_hip_yaw": 0.0,
    "left_hip_roll": -0.0873, "right_hip_roll": 0.0873,
    "left_hip_pitch": -0.4579, "right_hip_pitch": 0.4579,
    "left_knee": -0.0049, "right_knee": 0.0049,
    "left_ankle": 0.4530, "right_ankle": -0.4530,
    "neck_pitch": 0.3491, "head_pitch": 0.3491,
    "head_yaw": 0.0, "head_roll": 0.0,
}

# ---- observation block layout --------------------------------------------- #
OBS_GYRO = slice(0, 3)
OBS_GRAVITY = slice(3, 6)
OBS_JOINT_POS = slice(6, 20)
OBS_JOINT_VEL = slice(20, 34)
OBS_LAST_ACTION = slice(34, 48)
OBS_COMMAND = slice(48, 61)

GRAVITY_WORLD = np.array([0.0, 0.0, -1.0])


@dataclass(frozen=True)
class MicroduckVariant:
    """A Microduck MJCF variant."""

    name: str
    xml: str                                  # file name inside MICRODUCK_DIR
    passive_prefixes: tuple[str, ...] = ()    # prefixes of unactuated joints

    @property
    def mjcf_path(self) -> str:
        return os.path.join(MICRODUCK_DIR, self.xml)


VARIANTS: dict[str, MicroduckVariant] = {
    "walk": MicroduckVariant("walk", "robot_walk.xml"),
    "groundcontact": MicroduckVariant("groundcontact", "robot_groundcontact.xml"),
    "allcollisions": MicroduckVariant("allcollisions", "robot_allcollisions.xml"),
    "rollers": MicroduckVariant(
        "rollers", "robot_groundcontact_rollers.xml", ("passive_",)
    ),
    "walk_backlash": MicroduckVariant(
        "walk_backlash", "robot_walk_backlash.xml", ("passive_",)
    ),
    "groundcontact_backlash": MicroduckVariant(
        "groundcontact_backlash", "robot_groundcontact_backlash.xml", ("passive_",)
    ),
    "rollers_backlash": MicroduckVariant(
        "rollers_backlash", "robot_groundcontact_rollers_backlash.xml", ("passive_",)
    ),
}


def policy_action_to_motor_targets(
    action: Sequence[float], mouth_target: float = 0.0
) -> np.ndarray:
    """Expand a 14-dim policy action into the 15-slot motor target array.

    Slot 9 is the mouth and is NOT policy-driven, so ``action[9:]`` lands on
    slots 10..14. Writing ``action[9]`` to slot 9 would command the mouth with
    the right-hip value and shift the entire right leg.
    """
    a = np.asarray(action, dtype=float).reshape(-1)
    if a.shape[0] != N_ACTION:
        raise ValueError(f"action must have {N_ACTION} entries, got {a.shape[0]}")
    targets = np.zeros(N_MOTOR_SLOTS, dtype=float)
    targets[list(ACTION_TO_SLOT)] = a
    targets[MOUTH_SLOT] = float(mouth_target)
    return targets


def home_pose_vector(
    joint_names: Sequence[str], variant: "MicroduckVariant | None" = None
) -> np.ndarray:
    """Home pose ordered like ``joint_names``; passive joints pinned to 0.

    Passive (backlash/wheel) joints are matched FIRST because the upstream
    pattern-matching is first-match-wins — a passive ``*_backlash`` hinge has a
    +-1 deg range and must never receive a servo home value.
    """
    out = np.zeros(len(joint_names), dtype=float)
    for i, name in enumerate(joint_names):
        if variant is not None and name.startswith(variant.passive_prefixes):
            out[i] = 0.0
        elif name in HOME_POSE:
            out[i] = HOME_POSE[name]
    return out


def quat_wxyz_to_rot(q: Sequence[float]) -> np.ndarray:
    """MuJoCo quaternion (w, x, y, z) -> 3x3 rotation matrix (world <- body)."""
    w, x, y, z = (float(v) for v in q)
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v`
Expected: PASS (all tests so far).

- [ ] **Step 5: Commit**

```bash
git add rcs_env/envs/microduck_cfg.py rcs_env/tests/test_microduck.py
git commit -m "feat(microduck): add contract tables + variant registry (P1)"
```

---

### Task 4: 14→15 slot mapping (the #1 bug source)

**Files:**
- Test: `simulation/backend/rcs_env/tests/test_microduck.py`

- [ ] **Step 1: Write the failing tests**

```python
import numpy as np


def test_action_to_motor_targets_places_right_leg_after_mouth():
    from rcs_env.envs.microduck_cfg import policy_action_to_motor_targets
    action = np.arange(14, dtype=float)          # 0..13
    t = policy_action_to_motor_targets(action)
    assert t.shape == (15,)
    # left leg 0..4 and head/neck 5..8 map straight through
    assert np.allclose(t[0:9], action[0:9])
    assert t[9] == 0.0                            # mouth untouched by policy
    assert np.allclose(t[10:15], action[9:14])    # right leg shifted past mouth


def test_action_to_motor_targets_rejects_wrong_width():
    from rcs_env.envs.microduck_cfg import policy_action_to_motor_targets
    import pytest
    with pytest.raises(ValueError):
        policy_action_to_motor_targets(np.zeros(13))


def test_home_pose_pins_backlash_joints_to_zero():
    from rcs_env.envs.microduck_cfg import home_pose_vector, VARIANTS
    names = ["left_hip_roll", "passive_left_hip_roll_backlash", "right_knee"]
    v = home_pose_vector(names, VARIANTS["walk_backlash"])
    assert v[0] == -0.0873      # servo keeps its home value
    assert v[1] == 0.0          # passive backlash pinned to 0
    assert v[2] == 0.0049
```

- [ ] **Step 2: Run tests to verify they pass** (implementation already exists from Task 3)

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v -k "motor_targets or backlash"`
Expected: PASS (3 tests). If any fails, fix `microduck_cfg.py` before continuing.

- [ ] **Step 3: Commit**

```bash
git add rcs_env/tests/test_microduck.py
git commit -m "test(microduck): lock down 14->15 slot mapping + backlash home pose (P2)"
```

---

### Task 5: `FreeBaseMuJoCoEngine`

**Files:**
- Create: `simulation/backend/rcs_env/freebase_engine.py`
- Test: `simulation/backend/rcs_env/tests/test_microduck.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_freebase_engine_steps_without_destroying_freejoint():
    from rcs_env.freebase_engine import FreeBaseMuJoCoEngine
    eng = FreeBaseMuJoCoEngine.from_variant("walk")
    eng.reset()
    assert eng.nq == 21 and eng.nu == 14 and eng.nv == 20
    # freejoint quaternion must be valid (unit length) after reset ...
    assert np.isclose(np.linalg.norm(eng.qpos()[3:7]), 1.0, atol=1e-6)
    # ... and must survive a ctrl step. A 14-element command must NOT be written
    # into qpos (that is what MuJoCoEngine.step() does, and it would clobber the
    # freejoint pose because nq=21 > nu=14).
    eng.step_ctrl(np.zeros(14))
    assert eng.qpos().shape == (21,)
    assert np.isclose(np.linalg.norm(eng.qpos()[3:7]), 1.0, atol=1e-6)


def test_freebase_engine_ctrl_moves_joints_toward_target():
    from rcs_env.freebase_engine import FreeBaseMuJoCoEngine
    from rcs_env.envs.microduck_cfg import HOME_POSE, POLICY_JOINTS
    eng = FreeBaseMuJoCoEngine.from_variant("walk")
    eng.reset()
    target = np.array([HOME_POSE[j] for j in POLICY_JOINTS])
    err_before = float(np.abs(eng.joint_qpos(POLICY_JOINTS) - target).max())
    for _ in range(2000):
        eng.step_ctrl(target)
    err_after = float(np.abs(eng.joint_qpos(POLICY_JOINTS) - target).max())
    assert err_after < err_before, f"no convergence: {err_before} -> {err_after}"
    assert err_after < 0.1, f"tracking error too large: {err_after}"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v -k freebase`
Expected: FAIL — `ModuleNotFoundError: rcs_env.freebase_engine`.

- [ ] **Step 3: Implement `freebase_engine.py`**

```python
"""Floating-base MuJoCo engine (ctrl-driven) for freejoint robots.

Why this exists: :class:`rcs_env.engine.MuJoCoEngine` is arm-oriented — its
``step()`` writes ``data.qpos`` directly (teleporting the robot instead of
driving actuators) and its ``_detect_robot_config()`` injects a TCP site and
reloads the MJCF. Both are wrong for a freejoint biped, whose 14-element action
would otherwise overwrite the 7-element freejoint pose.

This engine is purely additive: it drives ``data.ctrl`` and integrates with
``mj_step``, and exposes the full ``qpos``/``qvel`` including the freejoint.
"""
from __future__ import annotations

from typing import Sequence

import mujoco
import numpy as np

from .envs.microduck_cfg import VARIANTS


class FreeBaseMuJoCoEngine:
    """MuJoCo wrapper for floating-base robots driven through ``data.ctrl``."""

    def __init__(self, model: "mujoco.MjModel", dt: float = 0.002) -> None:
        self.model = model
        self.data = mujoco.MjData(model)
        self.dt = float(dt)
        model.opt.timestep = self.dt
        self.qpos_addr: dict[str, int] = {}
        self.qvel_addr: dict[str, int] = {}
        self._cache_addresses()

    # ---- construction ----------------------------------------------------- #
    @classmethod
    def from_mjcf(cls, mjcf_path: str, dt: float = 0.002) -> "FreeBaseMuJoCoEngine":
        return cls(mujoco.MjModel.from_xml_path(mjcf_path), dt=dt)

    @classmethod
    def from_variant(cls, variant: str, dt: float = 0.002) -> "FreeBaseMuJoCoEngine":
        if variant not in VARIANTS:
            raise KeyError(f"Unknown Microduck variant '{variant}'. Known: {sorted(VARIANTS)}")
        return cls.from_mjcf(VARIANTS[variant].mjcf_path, dt=dt)

    def _cache_addresses(self) -> None:
        for i in range(self.model.njnt):
            name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, i)
            if not name:
                continue
            self.qpos_addr[name] = int(self.model.jnt_qposadr[i])
            self.qvel_addr[name] = int(self.model.jnt_dofadr[i])

    # ---- dimensions ------------------------------------------------------- #
    @property
    def nq(self) -> int:
        return int(self.model.nq)

    @property
    def nv(self) -> int:
        return int(self.model.nv)

    @property
    def nu(self) -> int:
        return int(self.model.nu)

    # ---- state ------------------------------------------------------------ #
    def reset(self, qpos: "np.ndarray | None" = None, qvel: "np.ndarray | None" = None) -> None:
        mujoco.mj_resetData(self.model, self.data)
        # mj_resetData can leave an all-zero (invalid) freejoint quaternion when
        # the MJCF declares no default rotation; force a valid identity quat.
        if self.model.nq >= 7 and not np.any(self.data.qpos[3:7]):
            self.data.qpos[3:7] = (1.0, 0.0, 0.0, 0.0)
        if qpos is not None:
            self.data.qpos[:] = np.asarray(qpos, dtype=float).reshape(-1)
        if qvel is not None:
            self.data.qvel[:] = np.asarray(qvel, dtype=float).reshape(-1)
        mujoco.mj_forward(self.model, self.data)

    def step_ctrl(self, ctrl: Sequence[float]) -> None:
        """Write actuator commands and integrate real dynamics."""
        c = np.asarray(ctrl, dtype=float).reshape(-1)
        if c.shape[0] != self.nu:
            raise ValueError(f"ctrl must have {self.nu} entries, got {c.shape[0]}")
        self.data.ctrl[:] = c
        mujoco.mj_step(self.model, self.data)

    def qpos(self) -> np.ndarray:
        """Full generalized position INCLUDING the freejoint."""
        return self.data.qpos.copy()

    def qvel(self) -> np.ndarray:
        """Full generalized velocity INCLUDING the freejoint."""
        return self.data.qvel.copy()

    def joint_qpos(self, names: Sequence[str]) -> np.ndarray:
        return np.array([self.data.qpos[self._qpos_addr[n]] for n in names])

    def joint_qvel(self, names: Sequence[str]) -> np.ndarray:
        return np.array([self.data.qvel[self._qvel_addr[n]] for n in names])

    def actuator_names(self) -> list[str]:
        return [
            mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, i) or ""
            for i in range(self.nu)
        ]

    def joint_names(self) -> list[str]:
        return [
            mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, i) or ""
            for i in range(self.model.njnt)
        ]

    def lowest_geom_z(self) -> float:
        """Lowest world-z over all geoms (used to stand the robot on the floor)."""
        mujoco.mj_forward(self.model, self.data)
        return float(np.min(self.data.geom_xpos[:, 2]))

    def close(self) -> None:
        self.model = None  # type: ignore[assignment]
        self.data = None  # type: ignore[assignment]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v -k freebase`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add rcs_env/freebase_engine.py rcs_env/tests/test_microduck.py
git commit -m "feat(microduck): add FreeBaseMuJoCoEngine (ctrl-driven stepping) (P2)"
```

---

### Task 6: `MicroduckEnv` — observation, reward, termination

**Files:**
- Create: `simulation/backend/rcs_env/envs/microduck.py`
- Test: `simulation/backend/rcs_env/tests/test_microduck.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_env_observation_is_61_dim():
    from rcs_env.envs.microduck import MicroduckEnv
    env = MicroduckEnv(variant="walk")
    obs, _ = env.reset(seed=0)
    assert env.observation_space.shape == (61,)
    assert env.action_space.shape == (14,)
    assert obs.shape == (61,)
    assert np.all(np.isfinite(obs))


def test_env_observation_blocks_are_correct():
    from rcs_env.envs.microduck import MicroduckEnv
    env = MicroduckEnv(variant="walk")
    obs, _ = env.reset(seed=0)
    g = obs[3:6]
    assert np.isclose(np.linalg.norm(g), 1.0, atol=1e-6)   # projected gravity is unit
    assert np.allclose(obs[6:20], 0.0, atol=1e-6)          # joint pos == home at reset
    assert np.allclose(obs[20:34], 0.0, atol=1e-6)         # zero velocity
    assert np.allclose(obs[34:48], 0.0)                    # no previous action
    assert np.allclose(obs[48:61], 0.0)                    # zero command


def test_env_step_returns_five_tuple_and_terminates_on_fall():
    from rcs_env.envs.microduck import MicroduckEnv
    env = MicroduckEnv(variant="walk")
    env.reset(seed=0)
    obs, reward, term, trunc, info = env.step(np.zeros(14))
    assert obs.shape == (61,)
    assert isinstance(float(reward), float)
    assert isinstance(bool(term), bool) and isinstance(bool(trunc), bool)
    # holding home pose should NOT immediately terminate
    assert not term, "robot should survive at least one control step at home pose"


def test_env_terminates_when_trunk_drops():
    from rcs_env.envs.microduck import MicroduckEnv
    env = MicroduckEnv(variant="walk")
    env.reset(seed=0)
    env.set_state_qpos_base_z(0.05)      # slam the trunk below the 0.15 m floor
    assert env._terminated()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v -k "env_"`
Expected: FAIL — `ModuleNotFoundError: rcs_env.envs.microduck`.

- [ ] **Step 3: Implement `envs/microduck.py`**

```python
"""Microduck biped locomotion environment (floating base).

Implements the official deployment contract from
``docs/superpowers/specs/2026-09-03-microduck-design.md`` §7:
* observation: 61 dims (gyro, projected gravity, joint pos/vel, last action, command)
* action: 14 dims, interpreted as an offset around ``home_pose`` scaled by ``action_scale``

Deliberately does NOT inherit :class:`rcs_env.envs.base.SimEnv` — that class is
arm-oriented (EE-pose observation, gripper, OMPL planner).
"""
from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np

from ..freebase_engine import FreeBaseMuJoCoEngine
from .microduck_cfg import (
    GRAVITY_WORLD,
    HOME_POSE,
    N_ACTION,
    N_OBS,
    OBS_COMMAND,
    OBS_GRAVITY,
    OBS_GYRO,
    OBS_JOINT_POS,
    OBS_JOINT_VEL,
    OBS_LAST_ACTION,
    POLICY_JOINTS,
    VARIANTS,
    home_pose_vector,
    quat_wxyz_to_rot,
)

# Reward weights (spec §5.5 initial defaults)
W_LIN_VEL = 1.0
W_ANG_VEL = 0.5
W_ALIVE = 0.1
W_UPRIGHT = -0.2
W_JOINT_LIMIT = -0.1
W_ACTION_RATE = -0.01
W_ENERGY = -0.001
W_SLIP = -0.05

LIN_VEL_SIGMA = 0.25
MIN_TRUNK_HEIGHT = 0.15      # m
MAX_TILT_DEG = 60.0
MAX_EPISODE_STEPS = 1000     # control steps (20 s at 50 Hz)


class MicroduckEnv(gym.Env):
    """Velocity-tracking locomotion env for the Microduck biped."""

    metadata = {"render_modes": ["rgb_array"], "render_fps": 50}

    def __init__(
        self,
        variant: str = "walk",
        dt: float = 0.002,
        control_dt: float = 0.02,
        action_scale: float = 0.5,
        render_mode: str | None = None,
        seed: int = 0,
    ) -> None:
        super().__init__()
        if variant not in VARIANTS:
            raise KeyError(f"Unknown variant '{variant}'. Known: {sorted(VARIANTS)}")
        self.variant_name = variant
        self.variant = VARIANTS[variant]
        self.action_scale = float(action_scale)
        self.render_mode = render_mode

        self.engine = FreeBaseMuJoCoEngine.from_variant(variant, dt=dt)
        self._control_steps = max(1, int(round(control_dt / dt)))

        # Fail fast: actuator order must match the policy joint order.
        act = [a for a in self.engine.actuator_names() if a]
        if tuple(act) != POLICY_JOINTS:
            raise ValueError(
                f"{self.variant.xml}: actuator order {act} != POLICY_JOINTS {POLICY_JOINTS}"
            )

        joint_names = self.engine.joint_names()
        self._home_vec = home_pose_vector(joint_names, self.variant)
        self._qpos_addr = [self.engine.qpos_addr[n] for n in POLICY_JOINTS]
        self._qvel_addr = [self.engine.qvel_addr[n] for n in POLICY_JOINTS]

        self.action_space = gym.spaces.Box(
            low=-1.0, high=1.0, shape=(N_ACTION,), dtype=np.float64
        )
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(N_OBS,), dtype=np.float64
        )

        self._last_action = np.zeros(N_ACTION, dtype=float)
        self._command = np.zeros(13, dtype=float)
        self._steps = 0
        self._rng = np.random.default_rng(seed)
        self._base_z = self._compute_standing_height()

    # ---- helpers ---------------------------------------------------------- #
    def _compute_standing_height(self) -> float:
        """Base z that puts the lowest geom exactly on the floor at home pose."""
        saved = self.engine.qpos().copy()
        q = saved.copy()
        for addr, name in zip(self._qpos_addr, POLICY_JOINTS):
            q[addr] = HOME_POSE[name]
        q[0:3] = 0.0
        q[3:7] = (1.0, 0.0, 0.0, 0.0)
        self.engine.reset(qpos=q)
        z = -self.engine.lowest_geom_z()
        self.engine.reset(qpos=saved)
        return float(z)

    def set_command(self, command: np.ndarray) -> None:
        """Set the 13-dim command block: twist(3) + head_pose(4) + body_pose(6)."""
        c = np.asarray(command, dtype=float).reshape(-1)
        if c.shape[0] != 13:
            raise ValueError(f"command must have 13 entries, got {c.shape[0]}")
        self._command = c.copy()

    def set_state_qpos_base_z(self, z: float) -> None:
        """Test hook: move the trunk to an absolute height (for termination tests)."""
        q = self.engine.qpos().copy()
        q[2] = float(z)
        self.engine.reset(qpos=q, qvel=np.zeros(self.engine.nv))

    # ---- observation ------------------------------------------------------ #
    def _get_obs(self) -> np.ndarray:
        qpos = self.engine.data.qpos
        qvel = self.engine.data.qvel
        rot = quat_wxyz_to_rot(qpos[3:7])          # world <- body

        gyro_body = rot.T @ qvel[3:6]              # world ang. vel -> body frame
        proj_gravity = rot.T @ GRAVITY_WORLD

        joint_pos = np.array([qpos[a] for a in self._qpos_addr])
        joint_vel = np.array([qvel[a] for a in self._qvel_addr])
        home = np.array([HOME_POSE[j] for j in POLICY_JOINTS])

        obs = np.zeros(N_OBS, dtype=np.float64)
        obs[OBS_GYRO] = gyro_body
        obs[OBS_GRAVITY] = proj_gravity
        obs[OBS_JOINT_POS] = joint_pos - home
        obs[OBS_JOINT_VEL] = joint_vel
        obs[OBS_LAST_ACTION] = self._last_action
        obs[OBS_COMMAND] = self._command
        return obs

    # ---- termination / reward --------------------------------------------- #
    def _terminated(self) -> bool:
        qpos = self.engine.data.qpos
        if float(qpos[2]) < MIN_TRUNK_HEIGHT:
            return True
        rot = quat_wxyz_to_rot(qpos[3:7])
        proj = rot.T @ GRAVITY_WORLD
        tilt = float(np.degrees(np.arccos(np.clip(-proj[2], -1.0, 1.0))))
        return tilt > MAX_TILT_DEG

    def _reward(self) -> float:
        qpos = self.engine.data.qpos
        qvel = self.engine.data.qvel
        rot = quat_wxyz_to_rot(qpos[3:7])
        lin_vel_body = rot.T @ qvel[0:3]

        cmd_vx, cmd_vy, cmd_vyaw = self._command[0], self._command[1], self._command[2]
        lin_err = (lin_vel_body[0] - cmd_vx) ** 2 + (lin_vel_body[1] - cmd_vy) ** 2
        ang_err = (qvel[5] - cmd_vyaw) ** 2
        r_track = W_LIN_VEL * float(np.exp(-lin_err / LIN_VEL_SIGMA))
        r_ang = W_ANG_VEL * float(np.exp(-ang_err / LIN_VEL_SIGMA))

        proj = rot.T @ GRAVITY_WORLD
        r_up = W_UPRIGHT * float(np.linalg.norm(proj[0:2]))

        joint_pos = np.array([qpos[a] for a in self._qpos_addr])
        home = np.array([HOME_POSE[j] for j in POLICY_JOINTS])
        r_limit = W_JOINT_LIMIT * float(np.sum(np.abs(joint_pos - home) > 0.9))

        r_rate = W_ACTION_RATE * float(np.sum(self._last_action ** 2))
        r_energy = W_ENERGY * float(np.sum(np.abs(self.engine.data.qfrc_actuator[self._qvel_addr])))

        return float(
            r_track + r_ang + W_ALIVE + r_up + r_limit + r_rate + r_energy
        )

    # ---- Gym API ---------------------------------------------------------- #
    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        q = np.zeros(self.engine.nq, dtype=float)
        q[2] = self._base_z
        q[3:7] = (1.0, 0.0, 0.0, 0.0)
        for addr, name in zip(self._qpos_addr, POLICY_JOINTS):
            q[addr] = HOME_POSE[name]
        self.engine.reset(qpos=q, qvel=np.zeros(self.engine.nv))
        self._last_action = np.zeros(N_ACTION, dtype=float)
        self._command = np.zeros(13, dtype=float)
        self._steps = 0
        return self._get_obs(), {}

    def step(self, action: np.ndarray):
        a = np.asarray(action, dtype=float).reshape(-1)
        if a.shape[0] != N_ACTION:
            raise ValueError(f"action must have {N_ACTION} entries, got {a.shape[0]}")
        a = np.clip(a, -1.0, 1.0)

        home = np.array([HOME_POSE[j] for j in POLICY_JOINTS])
        targets = home + self.action_scale * a

        for _ in range(self._control_steps):
            self.engine.step_ctrl(targets)

        self._last_action = a.copy()
        self._steps += 1

        obs = self._get_obs()
        reward = self._reward()
        terminated = self._terminated()
        truncated = self._steps >= MAX_EPISODE_STEPS
        info: dict[str, Any] = {
            "trunk_height": float(self.engine.data.qpos[2]),
            "steps": self._steps,
        }
        return obs, reward, bool(terminated), bool(truncated), info

    def close(self) -> None:
        self.engine.close()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v -k "env_"`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add rcs_env/envs/microduck.py rcs_env/tests/test_microduck.py
git commit -m "feat(microduck): add MicroduckEnv with 61-dim obs contract (P2)"
```

---

### Task 7: Register gym IDs and export symbols

**Files:**
- Modify: `simulation/backend/rcs_env/envs/base.py:183-208`
- Modify: `simulation/backend/rcs_env/envs/__init__.py`
- Test: `simulation/backend/rcs_env/tests/test_microduck.py`

- [ ] **Step 1: Write the failing test**

```python
def test_microduck_gym_ids_registered():
    import gymnasium as gym
    from rcs_env.envs.base import register_envs
    register_envs()
    for variant in ("walk", "groundcontact", "rollers"):
        env = gym.make(f"rcs/microduck-{variant}-v0")
        obs, _ = env.reset(seed=0)
        assert obs.shape == (61,)
        env.close()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py::test_microduck_gym_ids_registered -v`
Expected: FAIL — `NameNotFound: rcs/microduck-walk-v0`.

- [ ] **Step 3: Implement**

In `simulation/backend/rcs_env/envs/base.py`, inside `register_envs()`, after the `SCENES` loop and before `_REGISTERED = True`:

```python
    from .microduck_cfg import VARIANTS

    for variant_name in VARIANTS:
        gym.register(
            id=f"rcs/microduck-{variant_name}-v0",
            entry_point="rcs_env.envs.microduck:MicroduckEnv",
            kwargs={"variant": variant_name},
        )
```

In `simulation/backend/rcs_env/envs/__init__.py`, add to imports and `__all__`:

```python
from .microduck import MicroduckEnv
from .microduck_cfg import VARIANTS as MICRODUCK_VARIANTS
```

- [ ] **Step 4: Run test to verify it passes**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v`
Expected: PASS (full microduck suite).

- [ ] **Step 5: Run the full suite to prove no regression**

Run: `& $PY -m pytest rcs_env/tests/ -q`
Expected: all pass (11 pre-existing + new microduck tests).

- [ ] **Step 6: Commit**

```bash
git add rcs_env/envs/base.py rcs_env/envs/__init__.py rcs_env/tests/test_microduck.py
git commit -m "feat(microduck): register rcs/microduck-*-v0 gym IDs (P1/P2)"
```

---

### Task 8: Vectorized rollout + digital-twin smoke test

**Files:**
- Create: `simulation/backend/rcs_env/training/microduck_rollout.py`
- Test: manual smoke run (no pytest — requires a live script)

- [ ] **Step 1: Write the script**

```python
"""Random-policy rollout + digital-twin smoke test for Microduck (P2 acceptance)."""
from __future__ import annotations

import argparse

import numpy as np

from rcs_env.envs.twin import DigitalTwinSink, InMemoryTransport
from rcs_env.envs.vec import make_vec_env, random_rollout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="walk")
    ap.add_argument("--n-envs", type=int, default=2)
    ap.add_argument("--steps", type=int, default=64)
    args = ap.parse_args()

    transport = InMemoryTransport()
    sink = DigitalTwinSink(device_id="microduck-01", transport=transport, rate=0)

    vec_env = make_vec_env(
        f"rcs/microduck-{args.variant}-v0", n_envs=args.n_envs, seed=0
    )
    print(f"[vec] {args.n_envs} x rcs/microduck-{args.variant}-v0 "
          f"obs={vec_env.single_observation_space.shape} "
          f"act={vec_env.single_action_space.shape}")

    stats = random_rollout(vec_env, steps=args.steps)
    print(f"[random] mean_ep_return={stats['mean_episode_return']:.3f} "
          f"mean_ep_len={stats['mean_episode_length']:.1f}")

    print(f"[twin] {len(transport)} telemetry records buffered in-memory")
    vec_env.close()
    print("[done]")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the smoke test**

Run: `& $PY -m rcs_env.training.microduck_rollout --n-envs 2 --steps 64`
Expected: prints obs=(61,) act=(14,) and finite rollout stats; no exceptions.

- [ ] **Step 3: Commit**

```bash
git add rcs_env/training/microduck_rollout.py
git commit -m "feat(microduck): vectorized rollout + digital twin smoke test (P2)"
```

---

## Self-Review Notes

- **Spec coverage**: §4 assets (T1), §4.2 RobotType + registry (T2/T3), §4.3 backlash (T4), §5 env (T5/T6), §5.5 reward (T6), §7.1 obs (T6), §7.2 mapping (T4), §7.3 home pose (T3), §9 P1/P2 acceptance (T7/T8). §7.4 ONNX is P5 (separate plan).
- **Known gap**: `W_SLIP` (foot slip penalty) is defined but not yet wired into `_reward()` — foot contact detection needs the ground plane, which arrives with the scene composition in P3. Tracked as a P4 task.
- **Known gap**: the env loads the bare robot MJCF with no floor; `_compute_standing_height()` places the robot so its lowest geom rests at z=0, which is sufficient for P2 contract tests but means contacts only begin once a floor is composed in P3.
