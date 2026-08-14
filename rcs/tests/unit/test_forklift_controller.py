"""Tests for ForkliftController 3-joint independent PID."""
from __future__ import annotations

import pytest

from rcs.rcs.controllers.forklift import ForkliftController
from rcs.rcs.devices import ForkliftSpec
from rcs.rcs.state.command import Command, CommandType
from rcs.rcs.state.joint import JointState
from rcs.rcs.state.profile import DeviceProfile, Limits, Morphology


@pytest.fixture
def forklift_profile() -> DeviceProfile:
    return DeviceProfile(
        device_id="forklift-01",
        morphology=Morphology.ARM,  # reused; ForkliftController overrides morphology
        num_joints=3,
        control_hz=50,
        limits=Limits(
            pos_lower=[-50.0, 0.0, 0.0],
            pos_upper=[50.0, 3.0, 0.5],
            vel_max=[1.5, 0.3, 0.2],
            acc_max=[2.0, 1.0, 1.0],
            rad_th=0.05,
            pos_th=0.01,
        ),
        home_joints=[0.0, 0.0, 0.0],
    )


@pytest.fixture
def forklift_spec() -> ForkliftSpec:
    return ForkliftSpec(device_id="forklift-01")


@pytest.fixture
def controller(forklift_profile, forklift_spec) -> ForkliftController:
    return ForkliftController(forklift_profile, forklift_spec)


def test_extend_fork_sets_extend_joint(controller):
    cmd = Command(
        type=CommandType.EXECUTE_TASK,
        command_id="cmd-1",
        task_type="extend_fork",
        parameters={"extension_m": 0.3},
    )
    controller.on_command(cmd)
    hal_state = JointState(positions=[0.0, 0.0, 0.0], velocities=[0.0]*3, efforts=[0.0]*3, device_id="forklift-01")
    for _ in range(100):
        out = controller.update(hal_state)
    assert out.positions[2] > 0.2


def test_lift_fork_sets_lift_joint(controller):
    cmd = Command(
        type=CommandType.EXECUTE_TASK,
        command_id="cmd-2",
        task_type="lift_fork",
        parameters={"height_m": 1.5},
    )
    controller.on_command(cmd)
    hal_state = JointState(positions=[0.0, 0.0, 0.0], velocities=[0.0]*3, efforts=[0.0]*3, device_id="forklift-01")
    for _ in range(200):
        out = controller.update(hal_state)
    assert out.positions[1] > 1.3


def test_move_to_sets_travel_joint(controller):
    cmd = Command(
        type=CommandType.EXECUTE_TASK,
        command_id="cmd-3",
        task_type="move_to",
        parameters={"x": 5.0, "z": 2.0},
    )
    controller.on_command(cmd)
    hal_state = JointState(positions=[0.0, 0.0, 0.0], velocities=[0.0]*3, efforts=[0.0]*3, device_id="forklift-01")
    for _ in range(500):
        out = controller.update(hal_state)
    assert abs(out.positions[0] - 5.0) < 0.1


def test_three_joints_independent_pid(controller):
    """Lift to 1.5 and extend to 0.3 in parallel †both make progress."""
    controller.on_command(Command(type=CommandType.EXECUTE_TASK, task_type="lift_fork", parameters={"height_m": 1.5}))
    controller.on_command(Command(type=CommandType.EXECUTE_TASK, task_type="extend_fork", parameters={"extension_m": 0.3}))
    hal_state = JointState(positions=[0.0, 0.0, 0.0], velocities=[0.0]*3, efforts=[0.0]*3, device_id="forklift-01")
    for _ in range(200):
        out = controller.update(hal_state)
    assert out.positions[1] > 0.5
    assert out.positions[2] > 0.1


def test_tracking_error_triggers_halt(controller):
    target = JointState(positions=[0.0, 0.0, 0.0], velocities=[0.0]*3, efforts=[0.0]*3, device_id="forklift-01")
    current = JointState(positions=[0.0, 0.0, 1.0], velocities=[0.0]*3, efforts=[0.0]*3, device_id="forklift-01")
    controller.tracking_error(target, current)
    assert controller.state.mode.value == "halted"
