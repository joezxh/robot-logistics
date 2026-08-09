"""Tests for HugController."""
import pytest
from robot_decision.hug_controller import HugController, HugPhase


def test_initial_state_is_open():
    ctrl = HugController()
    assert ctrl.phase == HugPhase.OPEN


def test_approach_transitions_to_approaching():
    ctrl = HugController()
    ctrl.approach(target_pose={"x": 0.5, "y": 0.0, "z": 0.3})
    assert ctrl.phase == HugPhase.APPROACHING


def test_close_transitions_to_closing():
    ctrl = HugController()
    ctrl.close(pressure_target=50.0, approach_speed=0.2, close_speed=0.05)
    assert ctrl.phase == HugPhase.CLOSING


def test_reach_target_pressure_transitions_to_holding():
    ctrl = HugController()
    ctrl.close(pressure_target=50.0, approach_speed=0.2, close_speed=0.05)
    ctrl.update_feedback(pressure_l=49.0, pressure_r=51.0)
    assert ctrl.phase == HugPhase.HOLDING


def test_release_transitions_to_opening_then_open():
    ctrl = HugController()
    ctrl.close(pressure_target=50.0)
    ctrl.release()
    assert ctrl.phase == HugPhase.OPENING
    ctrl.complete_release()
    assert ctrl.phase == HugPhase.OPEN


def test_abort_returns_to_open():
    ctrl = HugController()
    ctrl.close(pressure_target=50.0)
    ctrl.abort()
    assert ctrl.phase == HugPhase.OPEN
