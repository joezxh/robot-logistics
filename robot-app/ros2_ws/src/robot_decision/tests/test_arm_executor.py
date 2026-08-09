"""Tests for ArmExecutor."""
import pytest
from robot_decision.arm_executor import ArmExecutor, ArmState


def test_initial_state_is_idle():
    executor = ArmExecutor(arm_id="left")
    assert executor.state == ArmState.IDLE
    assert executor.arm_id == "left"


def test_plan_and_execute_transitions_to_planning():
    executor = ArmExecutor(arm_id="right")
    executor.plan_and_execute(target_joints=[0.0] * 6)
    assert executor.state == ArmState.PLANNING


def test_cancel_transitions_to_idle():
    executor = ArmExecutor(arm_id="left")
    executor.plan_and_execute(target_joints=[0.0] * 6)
    executor.cancel()
    assert executor.state == ArmState.IDLE
