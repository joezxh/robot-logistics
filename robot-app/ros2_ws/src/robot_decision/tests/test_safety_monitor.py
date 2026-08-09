"""Tests for SafetyMonitor."""
import pytest
from robot_decision.safety_monitor import SafetyMonitor, SafetyState


def test_initial_state_is_safe():
    monitor = SafetyMonitor()
    assert monitor.state == SafetyState.SAFE


def test_estop_trigger_transitions_to_emergency():
    monitor = SafetyMonitor()
    monitor.trigger_estop()
    assert monitor.state == SafetyState.EMERGENCY


def test_scan_dangerous_transitions_to_slowdown():
    monitor = SafetyMonitor()
    monitor.update_scan(min_distance=0.3)  # Below safety threshold
    assert monitor.state == SafetyState.SLOWDOWN


def test_scan_safe_returns_to_safe():
    monitor = SafetyMonitor()
    monitor.update_scan(min_distance=0.3)
    monitor.update_scan(min_distance=2.0)  # Back to safe distance
    assert monitor.state == SafetyState.SAFE


def test_estop_blocks_cmd_vel():
    monitor = SafetyMonitor()
    monitor.trigger_estop()
    assert monitor.is_cmd_vel_allowed() is False


def test_safe_allows_cmd_vel():
    monitor = SafetyMonitor()
    assert monitor.is_cmd_vel_allowed() is True


def test_recovery_from_estop():
    monitor = SafetyMonitor()
    monitor.trigger_estop()
    monitor.reset_estop()
    assert monitor.state == SafetyState.SAFE
