"""RCS-aligned control modes and frame conversions.

Mirrors ``robot-control-stack``'s ``MjORobot`` control surface:
* :class:`ControlMode` — joint / cartesian / TQuat / relative-motion.
* :func:`command_in_world` / :func:`command_in_robot` — convert a Cartesian
  command between frames using the device's ``base_pose_in_world``.
* :func:`ee_pose_in_world` — forward kinematics result expressed in world frame.

The robot-logic control layer stays async-service oriented; this module provides
the *semantics* RCS encodes so the two systems are interchangeable at the API edge.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

import numpy as np

from robot_contracts import Pose, to_pose_in_robot_coordinates, to_pose_in_world_coordinates


class ControlMode(str, Enum):
    """RCS control modes."""

    JOINT = "joint"                 # joint-space target (rad)
    CARTESIAN = "cartesian"         # EE pose target in base frame [x,y,z,rpy]
    TQUAT = "tquat"                 # EE pose target [x,y,z, qx,qy,qz,qw]
    RELATIVE = "relative"           # incremental motion from current pose


@dataclass
class CartesianCommand:
    """A Cartesian-space command (RCS TQuat/Cartesian parity)."""

    translation: np.ndarray            # (3,) target xyz
    quaternion_xyzw: np.ndarray        # (4,) target orientation
    relative: bool = False


def ee_pose_in_world(base_pose_in_world: Pose, ee_in_base: Pose) -> Pose:
    """EE pose expressed in the world frame (RCS ``get_base_pose_in_world_coordinates``)."""
    return to_pose_in_world_coordinates(base_pose_in_world, ee_in_base)


def command_in_robot(base_pose_in_world: Pose, cmd_in_world: CartesianCommand) -> CartesianCommand:
    """Convert a world-frame Cartesian command into the robot base frame."""
    world_pose = Pose(translation=cmd_in_world.translation, quaternion=cmd_in_world.quaternion_xyzw)
    robot_pose = to_pose_in_robot_coordinates(base_pose_in_world, world_pose)
    return CartesianCommand(
        translation=robot_pose.translation,
        quaternion_xyzw=robot_pose.quaternion,
        relative=cmd_in_world.relative,
    )


def command_in_world(base_pose_in_world: Pose, cmd_in_robot: CartesianCommand) -> CartesianCommand:
    """Convert a robot-base-frame Cartesian command into the world frame."""
    robot_pose = Pose(translation=cmd_in_robot.translation, quaternion=cmd_in_robot.quaternion_xyzw)
    world_pose = to_pose_in_world_coordinates(base_pose_in_world, robot_pose)
    return CartesianCommand(
        translation=world_pose.translation,
        quaternion_xyzw=world_pose.quaternion,
        relative=cmd_in_robot.relative,
    )


def decompose_command(cmd: Sequence[float], mode: ControlMode) -> CartesianCommand:
    """Parse a raw command vector into a :class:`CartesianCommand` per control mode."""
    arr = np.asarray(cmd, dtype=float)
    if mode == ControlMode.TQUAT:
        return CartesianCommand(translation=arr[:3], quaternion_xyzw=arr[3:7], relative=False)
    if mode == ControlMode.CARTESIAN:
        # [x,y,z, roll,pitch,yaw]
        from robot_contracts import Pose

        p = Pose.from_rpy(arr[3:6], translation=arr[:3])
        return CartesianCommand(translation=p.translation, quaternion_xyzw=p.quaternion, relative=False)
    if mode == ControlMode.RELATIVE:
        from robot_contracts import Pose

        p = Pose.from_rpy(arr[3:6], translation=arr[:3])
        return CartesianCommand(translation=p.translation, quaternion_xyzw=p.quaternion, relative=True)
    raise ValueError(f"joint-space commands are not Cartesian: {mode}")


__all__ = [
    "ControlMode",
    "CartesianCommand",
    "ee_pose_in_world",
    "command_in_robot",
    "command_in_world",
    "decompose_command",
]
