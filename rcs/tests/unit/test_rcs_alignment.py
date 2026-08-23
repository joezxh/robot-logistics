"""Tests for RCS-aligned control modes, poses, and registry robot-type mapping."""
from __future__ import annotations

import numpy as np

from robot_contracts import Pose, RobotType

from rcs.control import (
    ControlMode,
    CartesianCommand,
    command_in_robot,
    command_in_world,
    ee_pose_in_world,
    decompose_command,
)
from rcs.state.pose import Pose6D, world_from_base_pose, robot_from_world_pose
from rcs.registry import Registry, Morphology, _profile_from_dict


def test_profile_derives_robot_type():
    p = _profile_from_dict({
        "device_id": "robot-01", "morphology": "arm",
        "num_joints": 6, "control_hz": 1000,
    })
    assert p.robot_type == RobotType.ARM


def test_profile_preserves_explicit_robot_type_and_base_pose():
    p = _profile_from_dict({
        "device_id": "r", "morphology": "arm", "num_joints": 6, "control_hz": 50,
        "robot_type": "FR3",
        "base_pose_in_world": {"translation": [1.0, 0.0, 0.0],
                               "quaternion_xyzw": [0.0, 0.0, 0.0, 1.0]},
    })
    assert p.robot_type == RobotType.FR3
    assert np.allclose(p.base_pose_in_world.translation, [1.0, 0.0, 0.0])


def test_ee_pose_in_world_roundtrip():
    base = Pose.from_keywords(x=1.0, y=0.0, z=0.0)
    ee_in_base = Pose.from_keywords(x=0.5, y=0.0, z=0.0)
    world = ee_pose_in_world(base, ee_in_base)
    assert np.allclose(world.translation, [1.5, 0.0, 0.0])


def test_command_frame_conversion():
    base = Pose.from_keywords(x=2.0, y=0.0, z=0.0)
    cmd_world = CartesianCommand(translation=np.array([3.0, 0.0, 0.0]),
                                 quaternion_xyzw=np.array([0.0, 0.0, 0.0, 1.0]))
    cmd_robot = command_in_robot(base, cmd_world)
    assert np.allclose(cmd_robot.translation, [1.0, 0.0, 0.0])
    back = command_in_world(base, cmd_robot)
    assert np.allclose(back.translation, [3.0, 0.0, 0.0])


def test_decompose_tquat_and_cartesian():
    c1 = decompose_command([1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 1.0], ControlMode.TQUAT)
    assert c1.quaternion_xyzw[3] == 1.0
    c2 = decompose_command([1.0, 0.0, 0.0, 0.0, 0.0, 1.5708], ControlMode.CARTESIAN)
    assert np.isclose(c2.translation[0], 1.0)


def test_pose6d_bridge_wxyz_xyzw():
    legacy = Pose6D(position=[1.0, 2.0, 3.0], orientation=[1.0, 0.0, 0.0, 0.0])  # wxyz
    c = legacy.to_contract()
    assert list(c.quaternion) == [0.0, 0.0, 0.0, 1.0]  # xyzw
    back = Pose6D.from_contract(c)
    assert back.orientation == [1.0, 0.0, 0.0, 0.0]
