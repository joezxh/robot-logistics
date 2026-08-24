"""6D pose bridge — delegates to the shared RCS-aligned Pose contract.

Historically robot-logic used a local ``Pose6D`` (quaternion stored wxyz). To align
with ``robot-control-stack`` we now use :class:`robot_contracts.Pose` as the single
representation (xyzw, world-frame right-handed x-forward / y-left / z-up). This
module keeps a thin ``Pose6D`` adapter for legacy callers and adds the
world<->robot frame conversions that RCS exposes via ``MjORobot``.
"""
from __future__ import annotations

from dataclasses import dataclass

from robot_contracts import (
    Pose as ContractPose,
    to_pose_in_world_coordinates,
    to_pose_in_robot_coordinates,
)


@dataclass
class Pose6D:
    """Legacy adapter. ``orientation`` is [w, x, y, z] (MuJoCo qpos convention)."""

    position: list[float]
    orientation: list[float]

    def to_dict(self) -> dict:
        return {"position": list(self.position), "orientation": list(self.orientation)}

    @classmethod
    def from_contract(cls, pose: ContractPose) -> "Pose6D":
        """Convert from the shared (xyzw) Pose to legacy (wxyz) Pose6D."""
        q = pose.quaternion
        return cls(position=list(pose.translation), orientation=[q[3], q[0], q[1], q[2]])

    def to_contract(self) -> ContractPose:
        w, x, y, z = self.orientation
        return ContractPose(translation=self.position, quaternion=[x, y, z, w])


def world_from_base_pose(base_pose_in_world: ContractPose, base_point: ContractPose) -> ContractPose:
    """RCS ``to_pose_in_world_coordinates``."""
    return to_pose_in_world_coordinates(base_pose_in_world, base_point)


def robot_from_world_pose(base_pose_in_world: ContractPose, world_point: ContractPose) -> ContractPose:
    """RCS ``to_pose_in_robot_coordinates``."""
    return to_pose_in_robot_coordinates(base_pose_in_world, world_point)


__all__ = ["Pose6D", "world_from_base_pose", "robot_from_world_pose"]
