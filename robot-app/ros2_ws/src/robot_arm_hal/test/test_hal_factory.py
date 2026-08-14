"""Tests for HAL factory and SimHalDriver."""
from __future__ import annotations

import os

from robot_arm_hal.hal_interface import make_hal, CommandMsg
from robot_arm_hal.sim_hal_driver import SimHalDriver


def test_default_mode_is_sim():
    os.environ.pop("HAL_MODE", None)
    hal = make_hal("test-forklift", num_joints=3)
    assert isinstance(hal, SimHalDriver)


def test_sim_hal_send_and_read():
    hal = SimHalDriver(device_id="test-fk", num_joints=3)
    hal.inject_state([1.0, 2.0, 0.3])
    state = hal.read_state()
    assert state.positions == [1.0, 2.0, 0.3]
    assert hal.send_command(CommandMsg(type="execute_task", task_type="extend_fork", parameters={"extension_m": 0.5})) is True
    assert hal.get_command_count() == 1


def test_sim_hal_estop_blocks_commands():
    hal = SimHalDriver(device_id="test-fk", num_joints=3)
    hal.estop()
    assert hal.send_command(CommandMsg(type="execute_task", task_type="lift_fork")) is False
    hal.recover()
    assert hal.send_command(CommandMsg(type="execute_task", task_type="lift_fork")) is True


def test_sim_hal_num_joints_constant():
    hal = SimHalDriver(device_id="test-loader", num_joints=14)
    assert hal.num_joints == 14
    state = hal.read_state()
    assert len(state.positions) == 14