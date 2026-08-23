"""RCS-aligned kinematics primitives — the single source of truth for poses,
robot/gripper taxonomy, and world<->robot frame transforms.

This module mirrors the conventions of ``robot-control-stack`` (``rcs._core.common``)
so that ``robot-logic``'s four subprojects (``rcs``, ``robot-app``, ``vla-training``,
``simulation``) share one coordinate vocabulary:

* **World frame** is a right-handed system with x forward, y left, z up.
* **Quaternions** are stored internally as ``[x, y, z, w]`` (xyzw), matching RCS.
  MuJoCo ``qpos`` uses ``[w, x, y, z]`` (wxyz) — converters are provided.
* **Pose** supports translation + quaternion, plus rpy (roll/pitch/yaw, intrinsic
  XYZ) construction to match RCS ``rpy_vector``.

Everything is pure-python and depends only on ``numpy`` so ``shared`` stays free of
any subproject import (the one-way dependency rule is preserved).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

import numpy as np


# --------------------------------------------------------------------------- #
# Robot / Gripper taxonomy
# --------------------------------------------------------------------------- #
class RobotType(str, Enum):
    """Unified robot taxonomy spanning RCS stock robots and robot-logic logistics.

    RCS stock arms: FR3, Panda, UR5e, XArm7, SO100, SO101, Yam.
    robot-logic logistics morphologies: ARM (generic 6-DoF), AGV, STACKER.
    """

    # RCS stock arms
    FR3 = "FR3"
    PANDA = "Panda"
    UR5E = "UR5e"
    XARM7 = "XArm7"
    SO100 = "SO100"
    SO101 = "SO101"
    YAM = "Yam"
    # robot-logic logistics devices
    ARM = "ARM"
    AGV = "AGV"
    STACKER = "STACKER"

    @classmethod
    def get_all(cls) -> list["RobotType"]:
        return list(cls)


class GripperType(str, Enum):
    """End-effector taxonomy."""

    FRANKA_HAND = "FrankaHand"
    ROBOTIQ_2F85 = "Robotiq2F85"
    YAM = "Yam"
    # robot-logic logistics gripper (pallet/box/bag)
    LOGISTICS_GRIPPER = "LogisticsGripper"
    NONE = "None"

    @classmethod
    def get_all(cls) -> list["GripperType"]:
        return list(cls)


class RobotPlatform(str, Enum):
    """Where the robot is mounted — mirrors RCS ``RobotPlatform``."""

    FIXED = "fixed"
    MOBILE = "mobile"
    RAIL = "rail"


# --------------------------------------------------------------------------- #
# Pose
# --------------------------------------------------------------------------- #
@dataclass
class Pose:
    """6D pose with translation + quaternion (xyzw, RCS convention).

    Construction helpers:
        Pose(translation=..., quaternion=...)     # explicit, xyzw
        Pose(pose_matrix=...)                     # 4x4 homogeneous
        Pose(rpy_vector=...)                      # roll/pitch/yaw (rad), intrinsic XYZ
        Pose(x=, y=, z=, qx=, qy=, qz=, qw=)      # keyword form
    """

    translation: np.ndarray = field(default_factory=lambda: np.zeros(3))
    quaternion: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0, 1.0]))

    def __post_init__(self) -> None:
        self.translation = np.asarray(self.translation, dtype=float).reshape(3)
        self.quaternion = np.asarray(self.quaternion, dtype=float).reshape(4)
        self._normalize()

    # ---- construction helpers ------------------------------------------------ #
    @classmethod
    def from_keywords(
        cls,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        qx: float = 0.0,
        qy: float = 0.0,
        qz: float = 0.0,
        qw: float = 1.0,
    ) -> "Pose":
        return cls(translation=[x, y, z], quaternion=[qx, qy, qz, qw])

    @classmethod
    def from_matrix(cls, matrix: np.ndarray) -> "Pose":
        m = np.asarray(matrix, dtype=float)
        t = m[:3, 3].copy()
        q = _rotation_matrix_to_xyzw_quaternion(m[:3, :3])
        return cls(translation=t, quaternion=q)

    @classmethod
    def from_rpy(cls, rpy: Sequence[float], translation: Sequence[float] | None = None) -> "Pose":
        r, p, y = rpy
        q = _rpy_to_xyzw_quaternion(r, p, y)
        t = list(translation) if translation is not None else [0.0, 0.0, 0.0]
        return cls(translation=t, quaternion=q)

    # ---- conversion ---------------------------------------------------------- #
    def to_matrix(self) -> np.ndarray:
        m = np.eye(4)
        m[:3, :3] = _xyzw_quaternion_to_rotation_matrix(self.quaternion)
        m[:3, 3] = self.translation
        return m

    def to_rpy(self) -> np.ndarray:
        """Intrinsic XYZ (roll, pitch, yaw) in radians."""
        return _xyzw_quaternion_to_rpy(self.quaternion)

    @property
    def xyzw(self) -> np.ndarray:
        return self.quaternion

    @property
    def wxyz(self) -> np.ndarray:
        """MuJoCo qpos convention [w, x, y, z]."""
        q = self.quaternion
        return np.array([q[3], q[0], q[1], q[2]])

    @classmethod
    def from_wxyz(cls, qwxyz: Sequence[float], translation: Sequence[float] | None = None) -> "Pose":
        w, x, y, z = qwxyz
        t = list(translation) if translation is not None else [0.0, 0.0, 0.0]
        return cls(translation=t, quaternion=[x, y, z, w])

    # ---- operators ----------------------------------------------------------- #
    def __matmul__(self, other: "Pose") -> "Pose":
        """Compose this @ other in SE(3)."""
        return Pose.from_matrix(self.to_matrix() @ other.to_matrix())

    def inverse(self) -> "Pose":
        return Pose.from_matrix(np.linalg.inv(self.to_matrix()))

    def _normalize(self) -> None:
        norm = np.linalg.norm(self.quaternion)
        if norm < 1e-12:
            self.quaternion = np.array([0.0, 0.0, 0.0, 1.0])
        else:
            self.quaternion = self.quaternion / norm

    def to_dict(self) -> dict:
        q = self.quaternion
        return {
            "translation": self.translation.tolist(),
            "quaternion_xyzw": q.tolist(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Pose":
        if "pose_matrix" in d:
            return cls.from_matrix(np.asarray(d["pose_matrix"]))
        if "rpy_vector" in d:
            t = d.get("translation")
            return cls.from_rpy(d["rpy_vector"], list(t) if t is not None else None)
        q = d.get("quaternion_xyzw") or d.get("quaternion") or [0.0, 0.0, 0.0, 1.0]
        t = d.get("translation")
        return cls(translation=list(t) if t is not None else [0.0, 0.0, 0.0], quaternion=q)

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        t = np.round(self.translation, 4)
        q = np.round(self.quaternion, 4)
        return f"Pose(t={t.tolist()}, q_xyzw={q.tolist()})"


# --------------------------------------------------------------------------- #
# Coordinate-frame helpers (mirrors RCS MjORobot)
# --------------------------------------------------------------------------- #
def get_base_pose_in_world_coordinates(world_from_base: Pose, base_from_point: Pose) -> Pose:
    """Transform a pose expressed in the robot base frame into world coordinates."""
    return world_from_base @ base_from_point


def to_pose_in_world_coordinates(world_from_base: Pose, base_from_point: Pose) -> Pose:
    return get_base_pose_in_world_coordinates(world_from_base, base_from_point)


def to_pose_in_robot_coordinates(world_from_base: Pose, world_from_point: Pose) -> Pose:
    """Transform a world-coordinate pose into the robot base frame."""
    return world_from_base.inverse() @ world_from_point


# --------------------------------------------------------------------------- #
# numpy / quaternion internals
# --------------------------------------------------------------------------- #
def _rpy_to_xyzw_quaternion(roll: float, pitch: float, yaw: float) -> np.ndarray:
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    return np.array([qx, qy, qz, qw])


def _xyzw_quaternion_to_rpy(q: np.ndarray) -> np.ndarray:
    x, y, z, w = q
    # roll (x)
    sinr = 2.0 * (w * x + y * z)
    cosr = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr, cosr)
    # pitch (y)
    sinp = 2.0 * (w * y - z * x)
    pitch = math.asin(max(-1.0, min(1.0, sinp)))
    # yaw (z)
    siny = 2.0 * (w * z + x * y)
    cosy = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny, cosy)
    return np.array([roll, pitch, yaw])


def _xyzw_quaternion_to_rotation_matrix(q: np.ndarray) -> np.ndarray:
    x, y, z, w = q
    n = w * w + x * x + y * y + z * z
    s = 0.0 if n < 1e-12 else 2.0 / n
    wx, wy, wz = s * w * x, s * w * y, s * w * z
    xx, xy, xz = s * x * x, s * x * y, s * x * z
    yy, yz = s * y * y, s * y * z
    zz = s * z * z
    return np.array(
        [
            [1.0 - (yy + zz), xy - wz, xz + wy],
            [xy + wz, 1.0 - (xx + zz), yz - wx],
            [xz - wy, yz + wx, 1.0 - (xx + yy)],
        ]
    )


def _rotation_matrix_to_xyzw_quaternion(r: np.ndarray) -> np.ndarray:
    m = np.asarray(r, dtype=float)
    trace = m[0, 0] + m[1, 1] + m[2, 2]
    if trace > 0.0:
        s = 0.5 / math.sqrt(trace + 1.0)
        w = 0.25 / s
        x = (m[2, 1] - m[1, 2]) * s
        y = (m[0, 2] - m[2, 0]) * s
        z = (m[1, 0] - m[0, 1]) * s
    else:
        if m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
            s = 2.0 * math.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2])
            w = (m[2, 1] - m[1, 2]) / s
            x = 0.25 * s
            y = (m[0, 1] + m[1, 0]) / s
            z = (m[0, 2] + m[2, 0]) / s
        elif m[1, 1] > m[2, 2]:
            s = 2.0 * math.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2])
            w = (m[0, 2] - m[2, 0]) / s
            x = (m[0, 1] + m[1, 0]) / s
            y = 0.25 * s
            z = (m[1, 2] + m[2, 1]) / s
        else:
            s = 2.0 * math.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1])
            w = (m[1, 0] - m[0, 1]) / s
            x = (m[0, 2] + m[2, 0]) / s
            y = (m[1, 2] + m[2, 1]) / s
            z = 0.25 * s
    return np.array([x, y, z, w])


__all__ = [
    "RobotType",
    "GripperType",
    "RobotPlatform",
    "Pose",
    "get_base_pose_in_world_coordinates",
    "to_pose_in_world_coordinates",
    "to_pose_in_robot_coordinates",
]
