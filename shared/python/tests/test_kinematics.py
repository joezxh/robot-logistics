"""Tests for the RCS-aligned kinematics primitives in robot_contracts.kinematics."""
from __future__ import annotations

import numpy as np
import pytest

from robot_contracts import (
    Pose,
    RobotType,
    GripperType,
    to_pose_in_robot_coordinates,
    to_pose_in_world_coordinates,
)


def test_identity_inverse():
    p = Pose.from_keywords(x=1.0, y=2.0, z=3.0, qx=0.0, qy=0.0, qz=0.0, qw=1.0)
    assert np.allclose((p @ p.inverse()).to_matrix(), np.eye(4), atol=1e-9)


def test_compose_translation():
    a = Pose.from_keywords(x=1.0, y=0.0, z=0.0)
    b = Pose.from_keywords(x=2.0, y=1.0, z=0.0)
    c = a @ b
    assert np.allclose(c.translation, [3.0, 1.0, 0.0])


def test_wxyz_roundtrip():
    p = Pose.from_keywords(x=0.5, y=0.2, z=0.1, qx=0.1, qy=0.2, qz=0.3, qw=0.9)
    p2 = Pose.from_wxyz(p.wxyz, translation=p.translation)
    assert np.allclose(p.to_matrix(), p2.to_matrix(), atol=1e-9)


def test_rpy_roundtrip():
    p = Pose.from_rpy([0.3, -0.2, 0.7], translation=[1.0, -1.0, 0.5])
    rpy = p.to_rpy()
    assert np.allclose(rpy, [0.3, -0.2, 0.7], atol=1e-9)


def test_world_robot_roundtrip():
    world_from_base = Pose.from_keywords(x=0.0, y=0.0, z=0.0, qz=0.7071068, qw=0.7071068)
    base_p = Pose.from_keywords(x=1.0, y=0.0, z=0.0)
    world_p = to_pose_in_world_coordinates(world_from_base, base_p)
    back = to_pose_in_robot_coordinates(world_from_base, world_p)
    assert np.allclose(back.translation, base_p.translation, atol=1e-9)
    assert np.allclose(back.to_matrix(), base_p.to_matrix(), atol=1e-9)


def test_robot_type_enum():
    assert RobotType.FR3.value == "FR3"
    assert RobotType.ARM.value == "ARM"
    assert len(RobotType.get_all()) >= 10


def test_quaternion_normalized():
    p = Pose(translation=[0, 0, 0], quaternion=[1.0, 0.0, 0.0, 0.0])
    assert np.isclose(np.linalg.norm(p.quaternion), 1.0)
