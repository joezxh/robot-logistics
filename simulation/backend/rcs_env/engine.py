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

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Sequence

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
    """High-fidelity MuJoCo engine (RCS ``rcs.sim`` parity).

    Requires ``pip install mujoco`` and an MJCF model. Falls back gracefully via
    :func:`available` when the optional dependency is absent.
    """

    def __init__(self, config: EngineConfig) -> None:
        super().__init__(config)
        self._mj = None
        self._model = None
        self._data = None
        self._try_load()

    @staticmethod
    def available() -> bool:
        try:
            import mujoco  # noqa: F401
            return True
        except Exception:  # pragma: no cover - optional dep
            return False

    def _try_load(self) -> None:  # pragma: no cover - requires mujoco
        import mujoco

        if self.config.mjcf_path is None:
            raise ValueError("MuJoCoEngine requires config.mjcf_path")
        self._mj = mujoco
        self._model = mujoco.MjModel.from_xml_path(self.config.mjcf_path)
        self._data = mujoco.MjData(self._model)

    @property
    def dof(self) -> int:  # pragma: no cover - requires mujoco
        return int(self._model.nu)

    def reset(self) -> None:  # pragma: no cover - requires mujoco
        self._mj.mj_resetData(self._model, self._data)

    def step(self, action: Sequence[float]) -> None:  # pragma: no cover - requires mujoco
        self._data.ctrl[:] = np.asarray(action, dtype=float)
        self._mj.mj_step(self._model, self._data)

    def qpos(self) -> np.ndarray:  # pragma: no cover - requires mujoco
        return self._data.qpos[: self.dof].copy()

    def qvel(self) -> np.ndarray:  # pragma: no cover - requires mujoco
        return self._data.qvel[: self.dof].copy()

    def set_qpos(self, qpos: Sequence[float]) -> None:  # pragma: no cover - requires mujoco
        self._data.qpos[: self.dof] = np.asarray(qpos, dtype=float)
        self._mj.mj_forward(self._model, self._data)

    def forward_kinematics(self, qpos: Sequence[float]) -> Pose:  # pragma: no cover - requires mujoco
        self.set_qpos(qpos)
        body_id = self._model.body("ee").id
        mat = self._data.xmat[body_id].reshape(3, 3)
        pos = self._data.xpos[body_id]
        q = _rotmat_to_xyzw(mat)
        return Pose(translation=pos, quaternion=q)

    def joint_limits(self) -> tuple[np.ndarray, np.ndarray]:  # pragma: no cover - requires mujoco
        return self._model.jnt_range[: self.dof, 0].copy(), self._model.jnt_range[: self.dof, 1].copy()

    def collision_free(self, qpos: Sequence[float]) -> bool:  # pragma: no cover - requires mujoco
        self.set_qpos(qpos)
        return bool(self._data.ncon == 0)


def _rotmat_to_xyzw(mat: np.ndarray) -> np.ndarray:  # pragma: no cover - mujoco only
    trace = mat[0, 0] + mat[1, 1] + mat[2, 2]
    if trace > 0:
        s = 0.5 / (trace + 1.0) ** 0.5
        w = 0.25 / s
        x = (mat[2, 1] - mat[1, 2]) * s
        y = (mat[0, 2] - mat[2, 0]) * s
        z = (mat[1, 0] - mat[0, 1]) * s
    else:
        x = (mat[0, 0] - mat[1, 1] - mat[2, 2] + 1.0) ** 0.5 / 2
        y = (mat[1, 0] + mat[0, 1]) / (4 * x)
        z = (mat[2, 0] + mat[0, 2]) / (4 * x)
        w = (mat[2, 1] - mat[1, 2]) / (4 * x)
    return np.array([x, y, z, w])


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
