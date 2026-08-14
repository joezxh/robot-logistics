"""Pure-Python tests for robot_decision.state_machine.FSM.

Run via:
    cd robot-app/ros2_ws/src/robot_decision
    python -m pytest test/test_state_machine.py -v
"""
from __future__ import annotations

import logging
import time

import pytest

from robot_decision.state_machine import FSM, FSMError


# ---------------------------------------------------------------------------
# Construction / configuration
# ---------------------------------------------------------------------------


def test_initial_state_defaults_to_first_state():
    fsm = FSM(states=("idle", "running", "done"))
    assert fsm.state == "idle"


def test_initial_state_can_be_overridden():
    fsm = FSM(states=("idle", "running", "done"), initial="running")
    assert fsm.state == "running"


def test_known_states_are_exposed():
    fsm = FSM(states=("idle", "approach", "engage", "lift", "transfer", "place"))
    assert fsm.states == (
        "idle",
        "approach",
        "engage",
        "lift",
        "transfer",
        "place",
    )


def test_unknown_initial_state_raises():
    with pytest.raises(ValueError):
        FSM(states=("idle", "done"), initial="missing")


def test_empty_states_raises():
    with pytest.raises(ValueError):
        FSM(states=())


def test_unknown_source_state_in_transitions_raises():
    with pytest.raises(ValueError):
        FSM(
            states=("idle", "done"),
            transitions={"flying": {"done"}},
        )


def test_unknown_destination_state_in_transitions_raises():
    with pytest.raises(ValueError):
        FSM(
            states=("idle", "done"),
            transitions={"idle": {"nowhere"}},
        )


def test_states_with_no_outgoing_transitions_have_empty_allowed():
    fsm = FSM(states=("idle", "done"))  # no transitions provided
    assert fsm.allowed_next() == set()
    assert fsm.state == "idle"


# ---------------------------------------------------------------------------
# Transitions
# ---------------------------------------------------------------------------


def test_legal_transition_updates_state_and_records_previous():
    fsm = FSM(
        states=("idle", "approach", "engage"),
        transitions={"idle": {"approach"}, "approach": {"engage"}},
    )
    fsm.transition("approach")
    assert fsm.state == "approach"
    assert fsm.previous_state == "idle"


def test_illegal_transition_raises_fsm_error():
    fsm = FSM(
        states=("idle", "approach", "engage"),
        transitions={"idle": {"approach"}, "approach": {"engage"}},
    )
    with pytest.raises(FSMError):
        fsm.transition("engage")  # skip over approach is illegal


def test_can_transition_returns_bool():
    fsm = FSM(
        states=("idle", "approach"),
        transitions={"idle": {"approach"}},
    )
    assert fsm.can_transition("approach") is True
    assert fsm.can_transition("nowhere") is False


def test_full_pallet_sequence():
    """Six-stage pallet flow matches the spec design (5.1 / design.md 4.3.3)."""
    pallet_states = ("idle", "approach", "engage", "lift", "transfer", "place")
    fsm = FSM(
        states=pallet_states,
        transitions={
            "idle": {"approach"},
            "approach": {"engage"},
            "engage": {"lift"},
            "lift": {"transfer"},
            "transfer": {"place"},
            "place": {"idle"},
        },
    )
    expected_path = [
        "approach",
        "engage",
        "lift",
        "transfer",
        "place",
        "idle",
    ]
    for expected in expected_path:
        fsm.transition(expected)
        assert fsm.state == expected


def test_reset_ignores_transition_table():
    fsm = FSM(
        states=("idle", "approach", "engage"),
        transitions={"idle": {"approach"}, "approach": {"engage"}},
    )
    fsm.transition("approach")
    fsm.reset("idle")
    assert fsm.state == "idle"
    assert fsm.previous_state == "approach"


def test_reset_without_argument_returns_to_initial():
    fsm = FSM(
        states=("a", "b", "c"),
        transitions={"a": {"b"}, "b": {"c"}},
        initial="a",
    )
    fsm.transition("b")
    fsm.reset()
    assert fsm.state == "a"


def test_reset_to_unknown_state_raises():
    fsm = FSM(states=("a", "b"))
    with pytest.raises(FSMError):
        fsm.reset("nope")


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------


def test_on_enter_hook_runs_after_state_change():
    seen: list[tuple[str, str]] = []

    def enter(fsm: FSM) -> None:
        seen.append(("enter", fsm.state))

    fsm = FSM(
        states=("idle", "running"),
        transitions={"idle": {"running"}},
        on_enter={"running": enter},
    )
    fsm.transition("running")
    assert seen == [("enter", "running")]


def test_on_exit_hook_runs_before_state_change():
    seen: list[tuple[str, str]] = []

    def exit_(fsm: FSM) -> None:
        seen.append(("exit", fsm.state))

    fsm = FSM(
        states=("idle", "running"),
        transitions={"idle": {"running"}},
        on_exit={"idle": exit_},
    )
    fsm.transition("running")
    assert seen == [("exit", "idle")]


def test_exit_runs_before_enter_in_order():
    seen: list[str] = []

    def exit_(fsm: FSM) -> None:
        seen.append(f"exit:{fsm.previous_state}")

    def enter(fsm: FSM) -> None:
        seen.append(f"enter:{fsm.state}")

    fsm = FSM(
        states=("idle", "running"),
        transitions={"idle": {"running"}},
        on_enter={"running": enter},
        on_exit={"idle": exit_},
    )
    fsm.transition("running")
    assert seen == ["exit:idle", "enter:running"]


def test_hook_exceptions_do_not_block_transition(caplog):
    def broken(_: FSM) -> None:
        raise RuntimeError("boom")

    fsm = FSM(
        states=("idle", "running"),
        transitions={"idle": {"running"}},
        on_enter={"running": broken},
    )
    with caplog.at_level(logging.ERROR, logger="robot_decision.state_machine"):
        fsm.transition("running")  # must not raise
    assert fsm.state == "running"
    assert any("on_enter[running] raised" in rec.message for rec in caplog.records)


def test_add_hook_attaches_to_existing_state():
    seen: list[str] = []

    def enter(_: FSM) -> None:
        seen.append("enter")

    fsm = FSM(
        states=("idle", "running"),
        transitions={"idle": {"running"}},
    )
    fsm.add_hook(state="running", on_enter=enter)
    fsm.transition("running")
    assert seen == ["enter"]


def test_add_hook_for_unknown_state_raises():
    fsm = FSM(states=("idle",))
    with pytest.raises(ValueError):
        fsm.add_hook(state="nowhere", on_enter=lambda f: None)


# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------


def test_time_in_state_advances_monotonically():
    fsm = FSM(
        states=("idle", "running"),
        transitions={"idle": {"running"}},
    )
    fsm.transition("running")
    first = fsm.time_in_state()
    # Sleep enough to exceed the Windows ``time.monotonic`` resolution
    # (~15 ms); subsequent reads must report an elapsed time of zero or more.
    time.sleep(0.05)
    second = fsm.time_in_state()
    assert second >= first
    assert second >= 0.0  # monotonic clock can be quantised; allow zero


def test_phase_start_time_resets_on_transition():
    fsm = FSM(
        states=("idle", "running"),
        transitions={"idle": {"running"}},
    )
    initial_start = fsm.phase_start_time
    time.sleep(0.005)
    fsm.transition("running")
    assert fsm.phase_start_time >= initial_start


def test_is_in_state_helper():
    fsm = FSM(states=("idle", "running"), initial="running")
    assert fsm.is_in_state("running") is True
    assert fsm.is_in_state("idle") is False
