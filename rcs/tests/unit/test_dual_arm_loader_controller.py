"""Tests for DualArmLoaderController 6+6 dual PD with grippers."""
from __future__ import annotations

import pytest

from rcs.controllers.dual_arm_loader import DualArmLoaderController
from rcs.devices import DualArmLoaderSpec
from rcs.state.command import Command, CommandType
from rcs.state.joint import JointState
from rcs.state.profile import DeviceProfile, Limits, Morphology


@pytest.fixture
def loader_profile() -> DeviceProfile:
    return DeviceProfile(
        device_id="loader-01",
        morphology=Morphology.ARM,
        num_joints=14,
        control_hz=50,
        limits=Limits(
            pos_lower=[-3.14] * 6 + [-3.14] * 6 + [0.0, 0.0],
            pos_upper=[3.14] * 6 + [3.14] * 6 + [1.0, 1.0],
            vel_max=[1.0] * 14,
            acc_max=[2.0] * 14,
            rad_th=0.05,
            pos_th=0.01,
        ),
        home_joints=[0.0] * 14,
    )


@pytest.fixture
def loader_spec() -> DualArmLoaderSpec:
    return DualArmLoaderSpec(device_id="loader-01")


@pytest.fixture
def controller(loader_profile, loader_spec) -> DualArmLoaderController:
    return DualArmLoaderController(loader_profile, loader_spec)


def test_open_grip_sets_gripper_zero(controller):
    cmd = Command(
        type=CommandType.EXECUTE_TASK,
        command_id="cmd-1",
        task_type="open_grip",
        parameters={"gripper": "both"},
    )
    controller.on_command(cmd)
    hal_state = JointState(positions=[0.0]*14, velocities=[0.0]*14, efforts=[0.0]*14, device_id="loader-01")
    for _ in range(50):
        out = controller.update(hal_state)
    assert out.positions[12] < 0.5
    assert out.positions[13] < 0.5


def test_close_grip_sets_gripper_one(controller):
    cmd = Command(
        type=CommandType.EXECUTE_TASK,
        command_id="cmd-2",
        task_type="close_grip",
        parameters={"gripper": "left", "force_n": 50.0},
    )
    controller.on_command(cmd)
    hal_state = JointState(positions=[0.0]*14, velocities=[0.0]*14, efforts=[0.0]*14, device_id="loader-01")
    for _ in range(100):
        out = controller.update(hal_state)
    assert out.positions[12] > 0.5
    assert out.positions[13] < 0.5  # right untouched


def test_hug_grasp_moves_arms_toward_center(controller):
    cmd = Command(
        type=CommandType.EXECUTE_TASK,
        command_id="cmd-3",
        task_type="hug_grasp",
        parameters={"object_width_m": 0.4, "approach_speed": 0.1},
    )
    controller.on_command(cmd)
    hal_state = JointState(positions=[0.0]*14, velocities=[0.0]*14, efforts=[0.0]*14, device_id="loader-01")
    for _ in range(100):
        out = controller.update(hal_state)
    assert out.positions[0] > 0.05  # left arm j0 moves positive
    assert out.positions[6] < -0.05  # right arm j0 moves negative


def test_dual_arm_sync_targets(controller):
    cmd = Command(
        type=CommandType.EXECUTE_TASK,
        command_id="cmd-4",
        task_type="dual_arm_sync",
        parameters={"left_target": 0.5, "right_target": -0.5},
    )
    controller.on_command(cmd)
    hal_state = JointState(positions=[0.0]*14, velocities=[0.0]*14, efforts=[0.0]*14, device_id="loader-01")
    for _ in range(200):
        out = controller.update(hal_state)
    assert abs(out.positions[0] - 0.5) < 0.1
    assert abs(out.positions[6] + 0.5) < 0.1


def test_tracking_error_triggers_halt(controller):
    target = JointState(positions=[0.0]*14, velocities=[0.0]*14, efforts=[0.0]*14, device_id="loader-01")
    current = JointState(positions=[0.0]*13 + [1.0], velocities=[0.0]*14, efforts=[0.0]*14, device_id="loader-01")
    controller.tracking_error(target, current)
    assert controller.state.mode.value == "halted"
