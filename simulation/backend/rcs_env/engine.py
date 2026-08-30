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
        """Build a rcs.sim-backed renderer (MuJoCoEngine only)."""
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
    """High-fidelity engine backed by the C++ ``rcs.sim`` kernel (RCS parity).

    The engine loads an MJCF model through ``rcs.sim.Sim`` (which owns the
    MuJoCo model/data) and drives it via ``rcs.sim.SimRobot``. This replaces the
    previous raw-``mujoco`` implementation so the whole RCS-aligned stack shares
    one simulation kernel.

    Requires the ``rcs`` extension (built from ``rcs_sim_core``) plus MuJoCo. When
    the extension is unavailable, :func:`available` returns ``False`` and the
    :func:`build_engine` factory falls back to :class:`LogicEngine`.
    """

    def __init__(self, config: EngineConfig) -> None:
        super().__init__(config)
        self._sim = None
        self._robot = None
        self._dof = 0
        self._home_key = None
        self._try_load()

    @staticmethod
    def available() -> bool:
        try:
            from rcs import sim  # noqa: F401

            return True
        except Exception:  # pragma: no cover - optional dep
            return False

    # ---- model loading ----------------------------------------------------- #
    def _resolve_mjcf(self, path: str) -> str:
        """Resolve an MJCF path (absolute, or relative to the bundled models dir).

        Searches ``<pkg>/assets/robots/...`` for a few levels up from this file so
        the engine works regardless of the current working directory.
        """
        if os.path.isabs(path) and os.path.exists(path):
            return path
        import glob

        here = os.path.dirname(os.path.abspath(__file__))
        roots = [here, os.path.dirname(here), os.path.dirname(os.path.dirname(here))]
        for root in roots:
            # allow ``path`` to be relative (e.g. "fr3.xml") under any robot dir
            patterns = [
                os.path.join(root, "assets", "robots", path),
                os.path.join(root, "assets", "robots", "**", path),
            ]
            for pat in patterns:
                matches = glob.glob(pat, recursive=True)
                if matches:
                    return os.path.normpath(matches[0])
        # fall back to a normalized path so Sim raises a clear load error
        return os.path.normpath(os.path.join(here, "assets", "robots", path))

    def _try_load(self) -> None:
        from rcs import sim

        if self.config.mjcf_path is None:
            raise ValueError("MuJoCoEngine requires config.mjcf_path")
        model_path = self._resolve_mjcf(self.config.mjcf_path)
        model_dir = os.path.dirname(model_path)
        filename = os.path.basename(model_path)

        # Build a generic SimRobotConfig by introspecting the model (not FR3-only).
        # Returns (cfg, patched_model_path|None, home_key|None) — patched_model_path
        # is set when a TCP site had to be injected; home_key names a collision-free
        # "home" keyframe applied on reset() when present.
        cfg, patched, home_key = self._detect_robot_config(model_path)
        self._home_key = home_key

        # Load Sim from the (possibly patched) model. MuJoCo resolves meshdir
        # relative to the current working directory, so load from the model's own
        # directory and restore cwd.
        load_path = patched or model_path
        load_dir = os.path.dirname(os.path.abspath(load_path))
        load_name = os.path.basename(load_path)
        prev_cwd = os.getcwd()
        os.chdir(load_dir)
        try:
            self._sim = sim.Sim(load_name)
        finally:
            os.chdir(prev_cwd)

        self._robot = sim.SimRobot(self._sim, cfg)
        # DoF = number of controlled joints (arm actuators exposed by SimRobot)
        self._dof = int(np.asarray(self._robot.get_joint_position()).size)

    # ---- generic robot detection (any arm, not just FR3) -------------------- #
    @staticmethod
    def _detect_robot_config(model_path: str):
        """Introspect the MJCF and build a :class:`rcs.sim.SimRobotConfig`.

        Detects arm joints (joints driven by position/servo actuators), the base
        body, and a TCP site. If no TCP site exists, one is injected onto the
        end-effector body via ``mujoco.MjSpec`` and the patched model is loaded
        instead. This keeps :class:`MuJoCoEngine` robot-agnostic (P2.3 roster).
        """
        from rcs import sim

        try:
            import mujoco
        except ImportError as exc:  # pragma: no cover - needs mujoco
            raise RuntimeError("MuJoCoEngine needs mujoco to detect robot config") from exc

        if not os.path.exists(model_path):
            model_path = MuJoCoEngine._resolve_mjcf(model_path)
        # meshdir is resolved relative to cwd; load from the model's own directory
        _mdir = os.path.dirname(os.path.abspath(model_path))
        _prev = os.getcwd()
        os.chdir(_mdir)
        try:
            m = mujoco.MjModel.from_xml_path(os.path.basename(model_path))
        finally:
            os.chdir(_prev)

        joint_names = [m.joint(i).name for i in range(m.njnt)]
        actuator_names = [m.actuator(i).name for i in range(m.nu)]
        MJTRN_JOINT = 0
        # Map actuators -> controlled joint (trntype 0 = JOINT)
        arm_joints, arm_actuators = [], []
        for a in range(m.nu):
            if int(m.actuator_trntype[a]) != MJTRN_JOINT:
                continue
            jid = int(m.actuator_trnid[a, 0])
            jname = joint_names[jid] if 0 <= jid < len(joint_names) else ""
            if jname and jname not in arm_joints:
                arm_joints.append(jname)
                arm_actuators.append(actuator_names[a])

        # Base body: parent of the first arm joint's body
        base_body = "world"
        if arm_joints:
            first_body_id = int(m.jnt_bodyid[joint_names.index(arm_joints[0])])
            base_body = m.body(first_body_id).name

        # TCP site: prefer an explicit site, else inject one on the last arm link
        site_candidates = ("attachment_site", "tcp_site", "tcp", "ee_site", "flange", "tool")
        site_names = [m.site(i).name for i in range(m.nsite)]
        tcp_site = next((c for c in site_candidates if c in site_names), None)
        patched_path = None
        if tcp_site is None:
            # Inject a TCP site onto the end-effector body (patched model). The
            # injected site is always named "attachment_site", so accept it.
            patched_path = MuJoCoEngine._inject_tcp_site(model_path, arm_joints, base_body)
            tcp_site = "attachment_site"
        if tcp_site is None and site_names:
            tcp_site = site_names[0]

        cfg = sim.SimRobotConfig()
        cfg.joints = list(arm_joints)
        cfg.actuators = list(arm_actuators)
        cfg.base = base_body
        cfg.attachment_site = tcp_site or ""
        cfg.arm_collision_geoms = []  # collision geoms optional for generic arms

        # Detect a "home" keyframe so reset() can land the robot in its
        # collision-free ready pose instead of the MJCF default qpos.
        home_key = None
        key_names = [m.key(i).name for i in range(m.nkey)]
        if "home" in key_names:
            home_key = "home"
        return cfg, patched_path, home_key

    @staticmethod
    def _inject_tcp_site(model_path: str, arm_joints: list, base_body: str) -> str:
        """Add a TCP site to the end-effector body (last arm link) and recompile.

        Returns the path to a temporary patched MJCF.         Used for robots whose asset
        ships without an explicit attachment site (e.g. SO-101).
        """
        import mujoco

        spec = mujoco.MjSpec.from_file(model_path)
        # end-effector body = body of the last arm joint (load with cwd at model dir)
        _mdir = os.path.dirname(os.path.abspath(model_path))
        _prev = os.getcwd()
        os.chdir(_mdir)
        try:
            m = mujoco.MjModel.from_xml_path(os.path.basename(model_path))
        finally:
            os.chdir(_prev)
        if arm_joints:
            last_body_id = int(m.jnt_bodyid[m.joint(arm_joints[-1]).id])
            ee_body_name = m.body(last_body_id).name
        else:
            ee_body_name = base_body
        body = spec.body(ee_body_name)
        site = body.add_site(name="attachment_site", pos=[0, 0, 0], size=[0.005])
        site.name = "attachment_site"
        # Write the patched model alongside the original so its relative meshdir
        # still resolves. The caller loads Sim from this path; cleaned up at exit.
        tmp = os.path.join(_mdir, "rcs_tcp_patched.xml")
        spec.compile()
        with open(tmp, "w") as f:
            f.write(spec.to_xml())
        return tmp

    # ---- PhysicsEngine interface ------------------------------------------- #
    @property
    def dof(self) -> int:
        return int(self._dof)

    def ncon(self) -> int:
        """Number of active contacts after the last forward dynamics step."""
        return int(self._sim.ncon())

    def reset(self) -> None:
        if self._home_key is not None:
            # Land the robot in its collision-free "home" keyframe instead of the
            # MJCF default qpos (often all-zero, which self-collides on a table).
            self._sim.reset_key(self._home_key)
        else:
            self._sim.reset()
        # Forward dynamics so contact count / FK reflect the reset pose.
        self._sim.forward()

    def step(self, action: Sequence[float]) -> None:
        q = np.asarray(action, dtype=float).reshape(-1)
        self._robot.set_joint_position(q)
        self._sim.step(1)

    def qpos(self) -> np.ndarray:
        return np.asarray(self._robot.get_joint_position()).reshape(-1).copy()

    def qvel(self) -> np.ndarray:
        return np.asarray(self._robot.get_joint_velocity()).reshape(-1).copy()

    def set_qpos(self, qpos: Sequence[float]) -> None:
        q = np.asarray(qpos, dtype=float).reshape(-1)
        self._robot.set_joints_hard(q)
        self._sim.forward()

    def forward_kinematics(self, qpos: Sequence[float]) -> Pose:
        self.set_qpos(qpos)
        rcs_pose = self._robot.get_cartesian_position()  # world frame, wxyz
        t = np.asarray(rcs_pose.translation()).reshape(3)
        q_wxyz = np.asarray(rcs_pose.rotation_q()).reshape(4)
        # contract convention is xyzw
        q_xyzw = np.array([q_wxyz[1], q_wxyz[2], q_wxyz[3], q_wxyz[0]])
        return Pose(translation=t, quaternion=q_xyzw)

    def inverse_kinematics(self, goal: Pose, seed: Sequence[float] | None = None):
        """Solve joint angles reaching ``goal`` (robot_contracts.Pose, world frame).

        Returns a numpy joint vector, or None if the IK has no solution. Delegates
        to rcs.sim SimRobot's MjIK solver.
        """
        if self._robot is None:
            return None
        ik = self._robot.get_ik()
        if not ik:
            return None
        from rcs import common

        q0 = np.asarray(seed if seed is not None else self.qpos(), dtype=float)
        q = goal.quaternion  # xyzw
        wxyz = np.array([q[3], q[0], q[1], q[2]], dtype=float)
        cpose = common.Pose(wxyz, np.asarray(goal.translation, dtype=float))
        sol = ik.inverse(cpose, q0)
        if sol is None:
            return None
        return np.asarray(sol).reshape(-1).copy()

    def joint_limits(self) -> tuple[np.ndarray, np.ndarray]:
        low, high = self._robot.joint_limits()
        return np.asarray(low).reshape(-1).copy(), np.asarray(high).reshape(-1).copy()

    def collision_free(self, qpos: Sequence[float]) -> bool:
        self.set_qpos(qpos)
        return bool(self._sim.ncon() == 0)

    # ---- rendering (SimCameraSet) ------------------------------------------- #
    @property
    def sim(self):
        """The underlying ``rcs.sim.Sim`` (for camera / rendering wiring)."""
        return self._sim

    def close(self) -> None:
        """Release the underlying MuJoCo model/data/renderer explicitly.

        Must be called during normal operation (not at interpreter finalization)
        to avoid freeing MuJoCo memory during static teardown, which otherwise
        corrupts the CRT heap (0xc0000374) at process exit.
        """
        self._robot = None
        if self._sim is not None:
            try:
                self._sim.close()
            except Exception:
                pass
            self._sim = None

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
        """Build a :class:`SimRenderer` backed by ``rcs.sim.SimCameraSet``.

        Returns a zero-frame renderer (no GL) when the backend is unavailable, so
        headless callers still get a valid observation shape.
        """
        from .renderer import SimRenderer

        return SimRenderer(self._sim, cameras=cameras)

    def render(self) -> Any:
        """Render the latest frame via ``SimCameraSet`` (falls back to None)."""
        if self._sim is None:
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
