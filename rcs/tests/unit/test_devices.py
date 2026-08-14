"""Tests for RCS device models."""
from __future__ import annotations

import pytest

from rcs.devices import ForkliftSpec, DualArmLoaderSpec
from rcs.devices.base import DeviceModel


def test_forklift_num_joints():
    fk = ForkliftSpec(device_id="forklift-test")
    assert fk.num_joints == 3
    assert len(fk.home_joints) == 3


def test_forklift_joint_limits():
    fk = ForkliftSpec(device_id="forklift-test", travel_range_m=10.0, lift_range_m=2.0, extend_range_m=0.3)
    lower, upper = fk.joint_limits()
    assert lower == [-10.0, 0.0, 0.0]
    assert upper == [10.0, 2.0, 0.3]


def test_dual_arm_num_joints():
    dl = DualArmLoaderSpec(device_id="loader-test")
    assert dl.num_joints == 14
    assert len(dl.home_joints) == 14


def test_dual_arm_joint_limits():
    dl = DualArmLoaderSpec(device_id="loader-test")
    lower, upper = dl.joint_limits()
    assert len(lower) == 14
    assert len(upper) == 14
    assert upper[12] == 1.0  # gripper closed
    assert upper[13] == 1.0


def test_forklift_inherits_device_model():
    fk = ForkliftSpec(device_id="forklift-test")
    assert isinstance(fk, DeviceModel)
