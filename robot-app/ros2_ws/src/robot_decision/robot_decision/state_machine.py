"""Generic finite state machine (FSM) base for robot_decision executors.

Pure Python — no rclpy dependency so it can be unit-tested in isolation.
Each executor subclass (pallet/box/bag) declares its states, the legal
transitions between them, and optional on_enter/on_exit hooks.

Design goals
------------
1. **Pure data structure** — the FSM only tracks the current state and the
   registered transitions. Side effects (joint commands, MQTT publish) live
   in the subclass hooks.
2. **Deterministic transitions** — every ``transition`` call validates that
   the requested state is reachable from the current one. Unknown
   transitions raise ``FSMError`` instead of silently advancing.
3. **Observable** — ``on_enter`` / ``on_exit`` hooks are called in order and
   failures are logged but do not block the transition (matches existing
   ``TaskCoordinator`` behaviour).
4. **Time-aware** — ``phase_start_time`` is updated on every transition so
   subclasses can implement timeouts with ``time.monotonic()`` (mirrors the
   pattern used in ``task_coordinator.py``).
"""
from __future__ import annotations

import logging
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


class FSMError(RuntimeError):
    """Raised when a transition is illegal or the FSM is in an invalid state."""


HookFn = Callable[["FSM"], None]


class FSM:
    """Reusable finite-state-machine base class.

    Parameters
    ----------
    states:
        Tuple of state names. The first state is treated as the initial
        state when ``initial`` is not provided.
    transitions:
        Optional dict ``{from_state: {to_state, ...}}`` describing the legal
        forward edges. Any transition not in the map is rejected.
    initial:
        Initial state name (defaults to ``states[0]``).
    on_enter / on_exit:
        Optional dicts ``{state_name: callable}`` invoked when the FSM
        enters/exits the given state.

    The class itself is reusable across the three Top 3 executors — each
    subclass just supplies its own ``states`` / ``transitions`` table.
    """

    def __init__(
        self,
        *,
        states: tuple[str, ...],
        transitions: dict[str, set[str]] | None = None,
        initial: str | None = None,
        on_enter: dict[str, HookFn] | None = None,
        on_exit: dict[str, HookFn] | None = None,
    ) -> None:
        if not states:
            raise ValueError("FSM requires at least one state")
        self._all_states = tuple(states)
        self._transitions: dict[str, set[str]] = {
            s: set() for s in self._all_states
        }
        if transitions:
            for src, dests in transitions.items():
                if src not in self._all_states:
                    raise ValueError(f"unknown source state {src!r}")
                for dest in dests:
                    if dest not in self._all_states:
                        raise ValueError(
                            f"unknown destination state {dest!r} from {src!r}"
                        )
                self._transitions[src] = set(dests)

        start = initial if initial is not None else self._all_states[0]
        if start not in self._all_states:
            raise ValueError(f"initial state {start!r} not in states")
        self._state: str = start
        self._previous_state: str | None = None
        self._phase_start_time: float = time.monotonic()
        self._entered_at: dict[str, float] = {start: self._phase_start_time}
        self._on_enter: dict[str, HookFn] = dict(on_enter or {})
        self._on_exit: dict[str, HookFn] = dict(on_exit or {})

    # ---- introspection -----------------------------------------------------

    @property
    def state(self) -> str:
        return self._state

    @property
    def previous_state(self) -> str | None:
        return self._previous_state

    @property
    def phase_start_time(self) -> float:
        return self._phase_start_time

    @property
    def states(self) -> tuple[str, ...]:
        return self._all_states

    def allowed_next(self) -> set[str]:
        """Return the set of legal next states from the current state."""
        return set(self._transitions.get(self._state, set()))

    def is_in_state(self, state: str) -> bool:
        return self._state == state

    def time_in_state(self) -> float:
        """Elapsed seconds since the FSM entered the current state."""
        return time.monotonic() - self._phase_start_time

    # ---- state transitions -------------------------------------------------

    def transition(self, to_state: str) -> None:
        """Move to ``to_state`` if a legal forward edge exists.

        Raises ``FSMError`` if the transition is not registered. The
        ``on_exit`` hook for the current state is invoked before the
        ``on_enter`` hook for the new state — matching the convention used
        in the existing ``TaskCoordinator``.
        """
        allowed = self._transitions.get(self._state, set())
        if to_state not in allowed:
            raise FSMError(
                f"illegal transition {self._state!r} -> {to_state!r}; "
                f"allowed: {sorted(allowed) or '(none)'}"
            )
        old = self._state
        # Update bookkeeping *before* invoking hooks so that on_exit can read
        # the previous_state via ``fsm.previous_state`` consistently.
        self._previous_state = old
        self._invoke_hook(self._on_exit.get(old), f"on_exit[{old}]")
        self._state = to_state
        self._phase_start_time = time.monotonic()
        self._entered_at[to_state] = self._phase_start_time
        logger.info("fsm: %s -> %s", old, to_state)
        self._invoke_hook(self._on_enter.get(to_state), f"on_enter[{to_state}]")

    def can_transition(self, to_state: str) -> bool:
        return to_state in self._transitions.get(self._state, set())

    def reset(self, to_state: str | None = None) -> None:
        """Reset to ``to_state`` (or the initial state) without raising.

        Unlike ``transition``, ``reset`` ignores the transition table — it is
        intended for fault-recovery scenarios where the FSM must snap back
        to ``idle`` regardless of the current state.
        """
        target = to_state if to_state is not None else self._all_states[0]
        if target not in self._all_states:
            raise FSMError(f"unknown reset target {target!r}")
        old = self._state
        self._invoke_hook(self._on_exit.get(old), f"on_exit[{old}]")
        self._previous_state = old
        self._state = target
        self._phase_start_time = time.monotonic()
        self._entered_at[target] = self._phase_start_time
        logger.warning("fsm reset: %s -> %s", old, target)
        self._invoke_hook(self._on_enter.get(target), f"on_enter[{target}]")

    # ---- hook helpers ------------------------------------------------------

    def _invoke_hook(self, hook: HookFn | None, label: str) -> None:
        if hook is None:
            return
        try:
            hook(self)
        except Exception:
            # Hook failures must not corrupt FSM state — log and continue.
            logger.exception("fsm hook %s raised", label)

    def add_hook(
        self,
        *,
        state: str,
        on_enter: HookFn | None = None,
        on_exit: HookFn | None = None,
    ) -> None:
        """Attach hooks for an existing state. Useful for subclass setup."""
        if state not in self._all_states:
            raise ValueError(f"unknown state {state!r}")
        if on_enter is not None:
            self._on_enter[state] = on_enter
        if on_exit is not None:
            self._on_exit[state] = on_exit


__all__ = ["FSM", "FSMError", "HookFn"]
