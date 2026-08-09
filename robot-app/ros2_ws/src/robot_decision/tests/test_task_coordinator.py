"""Tests for TaskCoordinator — pure Python FSM, no rclpy."""
import time
import pytest
from robot_decision.task_coordinator import TaskCoordinator


class FakeExecutor:
    def __init__(self, succeeds=True):
        self.calls = []
        self._succeeds = succeeds

    def execute(self, phase, params):
        self.calls.append((phase, params))

    def stop(self):
        self.calls.append(("stop",))


class TestTaskCoordinatorTransitions:
    def _make(self):
        received = []
        coord = TaskCoordinator(on_phase_change=lambda p: received.append(p))
        return coord, received

    def test_initial_phase_is_idle(self):
        coord, _ = self._make()
        assert coord.phase == "idle"

    def test_goto_triggers_navigating(self):
        coord, received = self._make()
        base = FakeExecutor()
        coord.set_executor("base", base)
        coord.on_task_command(task_type="goto", parameters={"target_pose": {"x": 1, "y": 2, "yaw": 0}})
        assert coord.phase == "navigating"
        assert "navigating" in received

    def test_pick_box_full_sequence(self):
        coord, received = self._make()
        base = FakeExecutor()
        arm = FakeExecutor()
        hug = FakeExecutor()
        coord.set_executor("base", base)
        coord.set_executor("arm", arm)
        coord.set_executor("hug", hug)
        coord.on_task_command(task_type="pick_box", parameters={
            "target_pose": {"x": 1, "y": 0, "yaw": 0},
            "hug_params": {"pressure_target": 50.0, "approach_speed": 0.3, "close_speed": 0.1},
        })
        assert coord.phase == "navigating"
        coord.advance_phase()  # navigating → docking
        assert coord.phase == "docking"
        coord.advance_phase()  # docking → approaching
        assert coord.phase == "approaching"
        coord.advance_phase()  # approaching → hugging
        assert coord.phase == "hugging"
        coord.advance_phase()  # hugging → lifting
        assert coord.phase == "lifting"

    def test_abort_from_any_phase(self):
        coord, _ = self._make()
        coord.set_executor("base", FakeExecutor())
        for phase in ["navigating", "docking", "hugging", "lifting", "transporting"]:
            coord._phase = phase
            coord.abort("test abort")
            assert coord.phase == "aborting"

    def test_abort_returns_to_idle(self):
        coord, _ = self._make()
        coord.set_executor("base", FakeExecutor())
        coord._phase = "navigating"
        coord.abort("test")
        coord.advance_phase()  # aborting → idle
        assert coord.phase == "idle"

    def test_invalid_task_type_raises(self):
        coord, _ = self._make()
        with pytest.raises(ValueError, match="unknown task_type"):
            coord.on_task_command(task_type="fly_away", parameters={})

    def test_home_all_returns_to_idle_after_retreat(self):
        coord, _ = self._make()
        coord.set_executor("base", FakeExecutor())
        coord.set_executor("arm", FakeExecutor())
        coord.on_task_command(task_type="home_all", parameters={})
        # home_all goes through retreating then idle
        assert coord.phase in ("retreating", "idle")

    def test_phase_timeout_triggers_abort(self):
        coord, _ = self._make()
        coord.set_executor("base", FakeExecutor())
        coord._phase_timeouts["navigating"] = 0.0  # immediate timeout
        # Set phase first (resets _phase_start_time to now), then override to past
        coord._phase = "navigating"
        coord._phase_start_time = time.monotonic() - 1.0
        coord.check_timeouts()
        assert coord.phase == "aborting"

    def test_get_phase_returns_current(self):
        coord, _ = self._make()
        assert coord.get_phase() == "idle"
