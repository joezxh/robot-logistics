"""Shared data contracts for the RCS-aligned simulation stack.

This package defines the cross-module types (``Pose``, ``RobotType``) that the
``rcs_env`` Gym/OMPL layer and the ``backend`` services depend on. It is kept
dependency-light (numpy only) so it can be imported without MuJoCo or the C++
``rcs`` extension.

To support the high-fidelity engine, :class:`Pose` mirrors the field layout used
by ``rcs.common.Pose`` (``translation`` + ``quaternion`` as numpy arrays, with
the quaternion stored in **xyzw** order, the de-facto ROS/Gym convention).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class RobotType(str, Enum):
    """Robot morphology tags used across the sim + control stack."""

    ARM = "arm"
    AGV = "agv"
    STACKER = "stacker"
    FR3 = "fr3"
    PANDA = "panda"
    UR5E = "ur5e"
    XARM7 = "xarm7"
    SO101 = "so101"
    YAM = "yam"


@dataclass
class Pose:
    """Rigid transform. ``quaternion`` is xyzw (ROS/Gym convention)."""

    translation: np.ndarray  # (3,)
    quaternion: np.ndarray   # (4,) xyzw

    def __post_init__(self) -> None:
        self.translation = np.asarray(self.translation, dtype=float).reshape(3)
        self.quaternion = np.asarray(self.quaternion, dtype=float).reshape(4)

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
        return cls(translation=np.array([x, y, z]), quaternion=np.array([qx, qy, qz, qw]))

    @property
    def pose_matrix(self) -> np.ndarray:
        """Return the 4x4 homogeneous transform from translation + xyzw quaternion."""
        x, y, z, w = self.quaternion
        n = x * x + y * y + z * z + w * w
        if n == 0.0:
            rot = np.eye(3)
        else:
            s = 2.0 / n
            rot = np.array([
                [1 - s * (y * y + z * z), s * (x * y - z * w), s * (x * z + y * w)],
                [s * (x * y + z * w), 1 - s * (x * x + z * z), s * (y * z - x * w)],
                [s * (x * z - y * w), s * (y * z + x * w), 1 - s * (x * x + y * y)],
            ])
        m = np.eye(4)
        m[:3, :3] = rot
        m[:3, 3] = self.translation
        return m


def get_site_profile(site_id: str) -> "SiteProfile":
    """Return the TCP profile for a logistics site.

    Placeholder until the real site registry is wired in. Falls back to an
    identity TCP pose expressed in the robot base frame.
    """
    return SiteProfile(site_id=site_id, tcp_pose_in_base=Pose.from_keywords())


@dataclass
class SiteProfile:
    site_id: str
    tcp_pose_in_base: Pose


__all__ = ["RobotType", "Pose", "SiteProfile", "get_site_profile"]
