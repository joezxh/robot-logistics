"""Tests for TaskCoordinator FSM."""
import pytest
from robot_decision.task_coordinator import TaskCoordinator, CoordinationPhase


def test_initial_state_is_idle():
    coord = TaskCoordinator()
    assert coord.phase == CoordinationPhase.IDLE


def test_transition_to_navigating_on_goto():
    coord = TaskCoordinator()
    coord.execute_task("goto", {"target_pose": {"x": 1.0, "y": 2.0, "z": 0.0}})
    assert coord.phase == CoordinationPhase.NAVIGATING


def test_transition_to_hugging_on_pick_box():
    coord = TaskCoordinator()
    coord.execute_task("pick_box", {"target_pose": {"x": 0.5}, "hug_params": {}})
    assert coord.phase == CoordinationPhase.APPROACHING


def test_abort_from_any_phase():
    coord = TaskCoordinator()
    coord.execute_task("goto", {"target_pose": {"x": 1.0}})
    coord.abort("safety_trigger")
    assert coord.phase == CoordinationPhase.ABORTING


def test_abort_returns_to_idle():
    coord = TaskCoordinator()
    coord.execute_task("goto", {"target_pose": {"x": 1.0}})
    coord.abort("safety_trigger")
    coord.complete_abort()
    assert coord.phase == CoordinationPhase.IDLE


def test_invalid_task_type_raises():
    coord = TaskCoordinator()
    with pytest.raises(ValueError):
        coord.execute_task("invalid_task", {})
