"""Physics-engine abstraction for the RCS-aligned simulation layer.

Mirrors ``robot-control-stack``'s separation between the high-fidelity MuJoCo
engine (``rcs.sim``) and the lightweight logic simulator used by robot-logic's
existing warehouse device backend.

Design (RCS convention):
* A :class:`PhysicsEngine` exposes a minimal forward-kinematics / step API that
  the Gym env and the OMPL planner consume.
* :class:`MuJoCoEngine` uses ``mujoco`` (optional dependency) for real rigid-body
  dynamics + collision detection.
* :class:`LogicEngine` wraps robot-logic's existing ``backend.algorithm.simulator``
  device model so the new RCS-aligned stack runs without a MuJoCo install.

Both engines implement the same interface, so the planner / env never depend on
the concrete engine — matching RCS's engine-agnostic ``MjORobot`` boundary.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np

from robot_contracts import Pose, RobotType


@dataclass
class EngineConfig:
    """Construction parameters shared by all engines."""

    robot_type: RobotType = RobotType.ARM
    mjcf_path: str | None = None
    # logic-engine device id when wrapping the legacy warehouse sim
    logic_device_id: str | None = None
    gravity: tuple[float, float, float] = (0.0, 0.0, -9.81)
    dt: float = 0.002
    seed: int = 0


class PhysicsEngine(ABC):
    """Minimal engine API consumed by :mod:`rcs_env.envs` and :mod:`rcs_env.ompl`."""

    def __init__(self, config: EngineConfig) -> None:
        self.config = config

    @property
    @abstractmethod
    def dof(self) -> int:
        """Number of actuated joints (DoF)."""

    @abstractmethod
    def reset(self) -> None:
        """Reset to the initial state."""

    @abstractmethod
    def step(self, action: Sequence[float]) -> None:
        """Advance the simulation by one control step."""

    @abstractmethod
    def qpos(self) -> np.ndarray:
        """Current joint positions (DoF,)."""

    @abstractmethod
    def qvel(self) -> np.ndarray:
        """Current joint velocities (DoF,)."""

    @abstractmethod
    def set_qpos(self, qpos: Sequence[float]) -> None:
        """Set joint positions (used by the planner and reset)."""

    @abstractmethod
    def forward_kinematics(self, qpos: Sequence[float]) -> Pose:
        """EE pose (base frame) for the given joint configuration."""

    @abstractmethod
    def joint_limits(self) -> tuple[np.ndarray, np.ndarray]:
        """(low, high) joint limits, each shape (DoF,)."""

    @abstractmethod
    def collision_free(self, qpos: Sequence[float]) -> bool:
        """Broad-phase collision check for a configuration (RCS ``collision_free``)."""

    # ---- optional coupling-check hooks (RCS OMPL relies on these) ---------- #
    def is_state_valid(self, qpos: Sequence[float]) -> bool:
        low, high = self.joint_limits()
        q = np.asarray(qpos, dtype=float)
        if q.shape != low.shape:
            return False
        if np.any(q < low) or np.any(q > high):
            return False
        return self.collision_free(q)

    def set_pose(self, pose: Pose) -> None:  # pragma: no cover - engine specific
        """Optionally place the robot / object (RCS ``set_pose``)."""

    def render(self) -> Any:  # pragma: no cover - visual only
        return None

    def build_renderer(self, cameras: Mapping[str, tuple] | None = None) -> Any:
        """Build a renderer (MuJoCoEngine only — official mujoco.Renderer)."""
        raise NotImplementedError


class LogicEngine(PhysicsEngine):
    """Wraps robot-logic's existing warehouse device simulator.

    The legacy :class:`backend.algorithm.simulator.device.Device` models
    logistics robots (ARM/AGV/STACKER) at the kinematic level only. We adapt its
    joint state into the RCS engine interface so the new Gym/OMPL stack runs
    immediately without a MuJoCo dependency, then swap in :class:`MuJoCoEngine`
    for high-fidelity dynamics later.
    """

    def __init__(self, config: EngineConfig) -> None:
        super().__init__(config)
        self._qpos = np.zeros(self.dof)
        self._qvel = np.zeros(self.dof)
        # DoF per morphology (matches legacy device profiles)
        self._limits_low = np.array([0.0] * self.dof)
        self._limits_high = np.array([2 * np.pi] * self.dof)
        self._ee_home = Pose.from_keywords(x=0.4, y=0.0, z=0.3)

    @property
    def dof(self) -> int:
        if self.config.robot_type in (RobotType.AGV, RobotType.STACKER):
            return 2
        return 6

    def reset(self) -> None:
        self._qpos = np.zeros(self.dof)
        self._qvel = np.zeros(self.dof)

    def step(self, action: Sequence[float]) -> None:
        act = np.asarray(action, dtype=float)
        self._qpos = np.clip(self._qpos + act * self.config.dt, self._limits_low, self._limits_high)
        self._qvel = act

    def qpos(self) -> np.ndarray:
        return self._qpos.copy()

    def qvel(self) -> np.ndarray:
        return self._qvel.copy()

    def set_qpos(self, qpos: Sequence[float]) -> None:
        self._qpos = np.asarray(qpos, dtype=float).copy()

    def forward_kinematics(self, qpos: Sequence[float]) -> Pose:
        # Simple planar/6D approximation of the legacy kinematic model.
        q = np.asarray(qpos, dtype=float)
        if self.dof == 2:  # AGV / stacker: (x, theta)
            return Pose.from_keywords(x=float(q[0]), y=0.0, z=0.0, qz=np.sin(q[1] / 2), qw=np.cos(q[1] / 2))
        # 6-DoF arm: incremental yaw + reach from joint sum
        reach = float(np.sum(np.abs(q)) * 0.05) + 0.3
        yaw = float(q[0]) if q.size > 0 else 0.0
        return Pose.from_keywords(x=self._ee_home.translation[0] + reach * np.cos(yaw),
                                  y=self._ee_home.translation[1] + reach * np.sin(yaw),
                                  z=self._ee_home.translation[2])

    def joint_limits(self) -> tuple[np.ndarray, np.ndarray]:
        return self._limits_low.copy(), self._limits_high.copy()

    def collision_free(self, qpos: Sequence[float]) -> bool:
        # Legacy sim has no obstacle field; always free at the kinematic level.
        return True


class MuJoCoEngine(PhysicsEngine):
    """High-fidelity physics engine backed directly by the official ``mujoco`` package.

    Replaces the previous C++ ``rcs.sim`` kernel (``rcs_sim_core`` extension) with
    the official ``mujoco`` Python binding, which wraps the same MuJoCo C core via
    pybind11. This removes the need to build the C++ extension while keeping
    identical physics accuracy and (single-process) performance.

    The engine:

    * loads an MJCF model through ``mujoco.MjModel.from_xml_path`` (robot-agnostic:
      it introspects actuators to find the arm joints + TCP site, and detects a
      ``home`` keyframe for a collision-free reset),
    * drives dynamics via ``mj_step`` / ``mj_forward``,
    * computes FK through ``mj_jacSite`` + site transforms,
    * uses a pure-Python damped-least-squares IK solver (:class:`rcs_env.ik.MjIK`,
      the same DLS algorithm the C++ ``MjIK`` used),
    * exposes collision state via ``data.ncon``.

    Requires the ``mujoco`` package. When it is unavailable, :func:`available`
    returns ``False`` and :func:`build_engine` falls back to :class:`LogicEngine`.
    """

    def __init__(self, config: EngineConfig) -> None:
        super().__init__(config)
        import mujoco

        self._mj = mujoco
        self._model = None
        self._data = None
        self._dof = 0
        self._tcp_site = "tcp"
        self._home_key_id = None
        self._qpos_home = None
        self._try_load()

    @staticmethod
    def available() -> bool:
        try:
            import mujoco  # noqa: F401

            return True
        except Exception:  # pragma: no cover - optional dep
            return False

    # ---- model loading ----------------------------------------------------- #
    def _resolve_mjcf(self, path: str) -> str:
        """Resolve an MJCF path (absolute, or relative to the bundled models dir)."""
        if os.path.isabs(path) and os.path.exists(path):
            return path
        import glob

        here = os.path.dirname(os.path.abspath(__file__))
        roots = [here, os.path.dirname(here), os.path.dirname(os.path.dirname(here))]
        for root in roots:
            patterns = [
                os.path.join(root, "assets", "robots", path),
                os.path.join(root, "assets", "robots", "**", path),
            ]
            for pat in patterns:
                matches = glob.glob(pat, recursive=True)
                if matches:
                    return os.path.normpath(matches[0])
        return os.path.normpath(os.path.join(here, "assets", "robots", path))

    def _try_load(self) -> None:
        if self.config.mjcf_path is None:
            raise ValueError("MuJoCoEngine requires config.mjcf_path")
        model_path = self._resolve_mjcf(self.config.mjcf_path)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"MJCF not found: {model_path}")

        # meshdir / texture paths resolve relative to cwd; load from the model dir
        load_dir = os.path.dirname(os.path.abspath(model_path))
        prev_cwd = os.getcwd()
        os.chdir(load_dir)
        try:
            self._model = self._mj.MjModel.from_xml_path(os.path.basename(model_path))
        finally:
            os.chdir(prev_cwd)
        self._data = self._mj.MjData(self._model)

        # Introspect the model: arm joints, TCP site, home keyframe.
        self._detect_robot_config(model_path)
        # IK solver bound to this model/data (pure-Python DLS).
        from .ik import MjIK

        self._ik = MjIK(self._model, self._data, tcp_site=self._tcp_site)

        self._dof = int(self._model.nu)
        self.reset()

    # ---- generic robot detection (any arm, not just FR3) -------------------- #
    def _detect_robot_config(self, model_path: str) -> None:
        """Introspect the MJCF for arm joints, a TCP site, and a home keyframe.

        Mirrors the previous ``rcs.sim`` detection: map JOINT actuators to the
        controlled joints, pick the TCP site from a candidate list (injecting one
        if missing), and detect a ``home`` keyframe for a collision-free reset.
        """
        m = self._model
        joint_names = [m.joint(i).name for i in range(m.njnt)]
        actuator_names = [m.actuator(i).name for i in range(m.nu)]
        MJTRN_JOINT = 0
        arm_joints, arm_actuators = [], []
        for a in range(m.nu):
            if int(m.actuator_trntype[a]) != MJTRN_JOINT:
                continue
            jid = int(m.actuator_trnid[a, 0])
            jname = joint_names[jid] if 0 <= jid < len(joint_names) else ""
            if jname and jname not in arm_joints:
                arm_joints.append(jname)
                arm_actuators.append(actuator_names[a])

        # TCP site: prefer an explicit site, else inject one on the last arm link.
        site_candidates = ("attachment_site", "tcp_site", "tcp", "ee_site", "flange", "tool")
        site_names = [m.site(i).name for i in range(m.nsite)]
        tcp_site = next((c for c in site_candidates if c in site_names), None)
        if tcp_site is None:
            tcp_site = self._inject_tcp_site(model_path, arm_joints)
        if tcp_site is None and site_names:
            tcp_site = site_names[0]
        self._tcp_site = tcp_site or "tcp"

        # Detect a "home" keyframe (re-read from the possibly-reloaded model) so
        # reset() lands the robot in its collision-free ready pose instead of the
        # MJCF default qpos (often all-zero, which self-collides on a table).
        m = self._model  # may have been reloaded by _inject_tcp_site
        key_names = [m.key(i).name for i in range(m.nkey)]
        if "home" in key_names:
            self._home_key_id = key_names.index("home")
            self._qpos_home = self._model.key_qpos[self._home_key_id].copy()
        else:
            self._home_key_id = None
            self._qpos_home = np.zeros(m.nq, dtype=float)

    def _inject_tcp_site(self, model_path: str, arm_joints: list) -> str | None:
        """Inject a TCP site onto the end-effector body and reload as ``attachment_site``.

        Returns the resolved site name (``attachment_site``) on success, else None.
        Used for robots whose asset ships without an explicit attachment site
        (e.g. SO-101). The patched XML is written next to the original so its
        relative meshdir still resolves.
        """
        m = self._model
        if arm_joints:
            last_body_id = int(m.jnt_bodyid[m.joint(arm_joints[-1]).id])
            ee_body_name = m.body(last_body_id).name
        else:
            return None

        load_dir = os.path.dirname(os.path.abspath(model_path))
        spec = self._mj.MjSpec.from_file(model_path)
        body = spec.body(ee_body_name)
        body.add_site(name="attachment_site", pos=[0, 0, 0], size=[0.005])
        # Write the patched model to a temp dir (not next to the asset) so the
        # bundled assets stay clean and git-untracked on every run.
        import tempfile

        patched_dir = tempfile.mkdtemp(prefix="rcs_tcp_")
        patched = os.path.join(patched_dir, "rcs_tcp_patched.xml")
        spec.compile()
        with open(patched, "w") as f:
            f.write(spec.to_xml())

        # Reload the patched model so this engine instance uses the new site.
        prev_cwd = os.getcwd()
        os.chdir(patched_dir)
        try:
            self._model = self._mj.MjModel.from_xml_path("rcs_tcp_patched.xml")
        finally:
            os.chdir(prev_cwd)
        self._data = self._mj.MjData(self._model)
        return "attachment_site"

    # ---- PhysicsEngine interface ------------------------------------------- #
    @property
    def dof(self) -> int:
        return int(self._dof)

    @property
    def joint_names(self) -> list[str]:
        """Names of the actuated joints (DoF), in actuator order."""
        names = []
        for a in range(self._model.nu):
            if int(self._model.actuator_trntype[a]) == 0:  # mjTRN_JOINT
                jid = int(self._model.actuator_trnid[a, 0])
                if 0 <= jid < self._model.njnt:
                    names.append(self._model.joint(jid).name)
        return names

    def ncon(self) -> int:
        """Number of active contacts after the last forward dynamics step."""
        return int(self._data.ncon)

    def reset(self) -> None:
        # Land the robot in its collision-free "home" keyframe instead of the
        # MJCF default qpos (often all-zero, which self-collides on a table).
        self._mj.mj_resetData(self._model, self._data)
        if self._home_key_id is not None and self._model.nkey > 0:
            self._mj.mj_resetDataKeyframe(self._model, self._data, self._home_key_id)
        else:
            self._data.qpos[:] = self._qpos_home
        self._mj.mj_forward(self._model, self._data)

    def step(self, action: Sequence[float]) -> None:
        q = np.asarray(action, dtype=float).reshape(-1)
        # Position-control contract: command target qpos; integrate + forward.
        if q.shape[0] >= self._model.nq:
            self._data.qpos[:] = q[: self._model.nq]
        else:
            self._data.qpos[: q.shape[0]] = q
        self._mj.mj_forward(self._model, self._data)
        self._mj.mj_step(self._model, self._data)

    def qpos(self) -> np.ndarray:
        # Return the actuated joints (DoF) for parity with the previous interface.
        if self._model.nu == self._model.nq:
            return self._data.qpos.copy()
        # map actuators -> joint qpos
        out = np.zeros(self._model.nu, dtype=float)
        for a in range(self._model.nu):
            jid = int(self._model.actuator_trnid[a, 0])
            if 0 <= jid < self._model.nq:
                out[a] = self._data.qpos[jid]
        return out

    def qvel(self) -> np.ndarray:
        return self._data.qvel[: self._model.nu].copy()

    def set_qpos(self, qpos: Sequence[float]) -> None:
        q = np.asarray(qpos, dtype=float).reshape(-1)
        if q.shape[0] >= self._model.nq:
            self._data.qpos[:] = q[: self._model.nq]
        else:
            self._data.qpos[: q.shape[0]] = q
        self._mj.mj_forward(self._model, self._data)

    def forward_kinematics(self, qpos: Sequence[float]) -> Pose:
        self.set_qpos(qpos)
        site_id = self._mj.mj_name2id(
            self._model, self._mj.mjtObj.mjOBJ_SITE, self._tcp_site
        )
        t = self._data.site_xpos[site_id].copy()
        rot = self._data.site_xmat[site_id].reshape(3, 3).copy()
        q_wxyz = self._rot_to_quat_wxyz(rot)
        # contract convention is xyzw
        q_xyzw = np.array([q_wxyz[1], q_wxyz[2], q_wxyz[3], q_wxyz[0]])
        return Pose(translation=t, quaternion=q_xyzw)

    def inverse_kinematics(self, goal: Pose, seed: Sequence[float] | None = None):
        """Solve joint angles reaching ``goal`` (robot_contracts.Pose, world frame).

        Pure-Python damped-least-squares IK (no C++ dependency). Returns a numpy
        joint vector, or None if the solver fails to converge.
        """
        q0 = np.asarray(seed if seed is not None else self.qpos(), dtype=float)
        sol = self._ik.solve(goal.translation, goal.quaternion, q0)
        if sol is None:
            return None
        return np.asarray(sol).reshape(-1).copy()

    def joint_limits(self) -> tuple[np.ndarray, np.ndarray]:
        low, high = [], []
        for j in range(self._model.njnt):
            rng = self._model.jnt_range[j]
            low.append(rng[0])
            high.append(rng[1])
        # return only the actuated joints' limits (DoF,)
        arm_low, arm_high = [], []
        for a in range(self._model.nu):
            jid = int(self._model.actuator_trnid[a, 0])
            if 0 <= jid < len(low):
                arm_low.append(low[jid])
                arm_high.append(high[jid])
        if arm_low:
            return np.asarray(arm_low), np.asarray(arm_high)
        return np.asarray(low), np.asarray(high)

    def collision_free(self, qpos: Sequence[float]) -> bool:
        self.set_qpos(qpos)
        return bool(self._data.ncon == 0)

    def gravity_compensation(self) -> np.ndarray:
        """Inverse-dynamics gravity + bias terms (qfrc_inverse) for free-space holding."""
        self._mj.mj_inverse(self._model, self._data)
        return self._data.qfrc_inverse.copy()

    def contact_forces(self, site: str = "tcp") -> np.ndarray:
        """Accumulated contact wrench (force/torque, 6,) at ``site`` (world frame)."""
        site_id = self._mj.mj_name2id(self._model, self._mj.mjtObj.mjOBJ_SITE, site)
        wrench = np.zeros(6, dtype=float)
        for c in range(self._data.ncon):
            f = np.zeros(6, dtype=float)
            self._mj.mj_contactForce(self._model, self._data, c, f)
            wrench += f
        return wrench

    # ---- helpers ------------------------------------------------------------ #
    @staticmethod
    def _rot_to_quat_wxyz(rot: np.ndarray) -> np.ndarray:
        """Convert a 3x3 rotation matrix to a wxyz quaternion (MuJoCo order)."""
        r = np.asarray(rot, dtype=float)
        w = np.sqrt(max(0.0, 1.0 + r[0, 0] + r[1, 1] + r[2, 2])) / 2.0
        x = np.sqrt(max(0.0, 1.0 + r[0, 0] - r[1, 1] - r[2, 2])) / 2.0
        y = np.sqrt(max(0.0, 1.0 - r[0, 0] + r[1, 1] - r[2, 2])) / 2.0
        z = np.sqrt(max(0.0, 1.0 - r[0, 0] - r[1, 1] + r[2, 2])) / 2.0
        if r[2, 1] - r[1, 2] < 0:
            x = -x
        if r[0, 2] - r[2, 0] < 0:
            y = -y
        if r[1, 0] - r[0, 1] < 0:
            z = -z
        return np.array([w, x, y, z], dtype=float)

    # ---- rendering (mujoco.Renderer) ---------------------------------------- #
    @property
    def model(self):
        """The underlying ``mujoco.MjModel`` (for camera / rendering wiring)."""
        return self._model

    def close(self) -> None:
        """Release the underlying MuJoCo model/data (official binding holds no CRT handles)."""
        self._model = None
        self._data = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def build_renderer(self, cameras: Mapping[str, tuple] | None = None) -> Any:
        """Build a :class:`SimRenderer` backed by ``mujoco.Renderer``."""
        from .renderer import SimRenderer

        return SimRenderer(self._model, self._data, cameras=cameras)

    def render(self) -> Any:
        """Render the latest frame via ``mujoco.Renderer`` (falls back to None)."""
        if self._model is None:
            return None
        try:
            return self.build_renderer().render()
        except Exception:  # pragma: no cover - GL unavailable
            return None


def build_engine(config: EngineConfig) -> PhysicsEngine:
    """Factory: prefer MuJoCo when available, else the logic engine (RCS parity)."""
    if config.mjcf_path and MuJoCoEngine.available():
        return MuJoCoEngine(config)
    return LogicEngine(config)


__all__ = [
    "EngineConfig",
    "PhysicsEngine",
    "LogicEngine",
    "MuJoCoEngine",
    "build_engine",
]
