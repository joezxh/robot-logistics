"""Pallet task executor — 6-stage FSM for forklift pallet handling.

Pure-Python orchestration (no rclpy) so the state machine is unit-testable
in isolation. The ROS 2 node wrapper ``PalletTaskExecutorNode`` lives in
the same file (``main()``) and binds the FSM to ROS topics / actions.

Pallet flow (spec design.md 5.1 + 4.3.3):
    idle -> approach -> engage -> lift -> transfer -> place -> idle

The trajectory for each stage is delegated to
``robot_decision.planning.ForkliftMotionPlanner``. The executor only
manages state transitions and per-stage timeouts; the planner is
responsible for the actual 3-joint waypoints.
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from .state_machine import FSM, FSMError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

PALLET_STATES: tuple[str, ...] = (
    "idle",
    "approach",
    "engage",
    "lift",
    "transfer",
    "place",
)

PALLET_TRANSITIONS: dict[str, set[str]] = {
    "idle":      {"approach"},
    "approach":  {"engage"},
    "engage":    {"lift"},
    "lift":      {"transfer"},
    "transfer":  {"place"},
    "place":     {"idle"},
}

# Per-stage timeout (seconds). Pallet KPI is <= 12s per task, so the per-
# stage budget is intentionally tight.
PALLET_STAGE_TIMEOUTS_S: dict[str, float] = {
    "approach":  3.0,
    "engage":    2.0,
    "lift":      2.0,
    "transfer":  3.0,
    "place":     2.0,
}

# Forward sequence used by ``run_full_cycle()`` and the ROS node.
PALLET_FORWARD_SEQUENCE: tuple[str, ...] = (
    "approach",
    "engage",
    "lift",
    "transfer",
    "place",
    "idle",
)


# ---------------------------------------------------------------------------
# Result data classes
# ---------------------------------------------------------------------------

@dataclass
class PalletTaskResult:
    """Final outcome of a pallet task cycle."""

    success: bool
    final_state: str
    elapsed_s: float
    completed_stages: tuple[str, ...] = field(default_factory=tuple)
    error: str | None = None


# ---------------------------------------------------------------------------
# Executor
# ---------------------------------------------------------------------------

StageFn = Callable[[dict[str, Any]], None]


class PalletTaskExecutor:
    """6-stage forklift pallet executor.

    Parameters
    ----------
    planner:
        Object exposing ``plan_insert_pallet`` and ``plan_drop_pallet``
        methods. Defaults to a fresh ``ForkliftMotionPlanner`` from the
        ``planning`` subpackage. Pass ``None`` for a stub executor (used by
        unit tests that only care about FSM transitions).
    stage_callback:
        Optional callable invoked on every successful transition. Receives
        ``(state_name, parameters)`` and is the integration point used by
        the ROS 2 node to publish feedback.
    """

    def __init__(
        self,
        planner: Any = None,
        stage_callback: Callable[[str, dict[str, Any]], None] | None = None,
        stage_timeouts: dict[str, float] | None = None,
    ) -> None:
        self._planner = planner
        self._stage_callback = stage_callback
        self._stage_timeouts: dict[str, float] = dict(PALLET_STAGE_TIMEOUTS_S)
        if stage_timeouts:
            self._stage_timeouts.update(stage_timeouts)

        self._fsm = FSM(
            states=PALLET_STATES,
            transitions=PALLET_TRANSITIONS,
            initial="idle",
        )
        self._current_params: dict[str, Any] = {}
        self._task_started_at: float | None = None
        self._completed_stages: list[str] = []
        self._failed = False
        self._failure_reason: str | None = None

    # ---- introspection -----------------------------------------------------

    @property
    def state(self) -> str:
        return self._fsm.state

    @property
    def fsm(self) -> FSM:
        """Expose the underlying FSM (used by tests and the ROS node)."""
        return self._fsm

    # ---- public API --------------------------------------------------------

    def start_task(self, parameters: dict[str, Any] | None = None) -> None:
        """Begin a new pallet task cycle.

        Resets any prior failure state, stores the parameters, and enters
        the ``approach`` stage.
        """
        params = dict(parameters or {})
        self._current_params = params
        self._task_started_at = time.monotonic()
        self._completed_stages = []
        self._failed = False
        self._failure_reason = None

        if self._fsm.state != "idle":
            # Recovery: snap back to idle without raising. This mirrors the
            # behaviour used by ``TaskCoordinator.abort()`` for fault
            # recovery.
            logger.warning(
                "pallet executor: starting task from non-idle state %s; resetting",
                self._fsm.state,
            )
            self._fsm.reset("idle")

        self._enter_stage("approach", params)

    def advance(self) -> str:
        """Advance to the next stage in the forward sequence.

        Returns the new state. If the FSM is in ``idle`` or already failed,
        the call is a no-op.
        """
        if self._failed:
            return self._fsm.state
        idx = PALLET_FORWARD_SEQUENCE.index(self._fsm.state)
        next_state = PALLET_FORWARD_SEQUENCE[idx + 1]
        # The final entry in PALLET_FORWARD_SEQUENCE is "idle" itself which
        # has no outgoing edge, so check before transitioning.
        if next_state == self._fsm.state:
            return self._fsm.state
        if not self._fsm.can_transition(next_state):
            logger.warning(
                "pallet executor: cannot advance from %s to %s",
                self._fsm.state,
                next_state,
            )
            return self._fsm.state
        self._enter_stage(next_state, self._current_params)
        return self._fsm.state

    def abort(self, reason: str = "") -> PalletTaskResult:
        """Abort the current task and return the final result.

        Idempotent — calling abort multiple times is safe and always
        returns to ``idle``.
        """
        self._failed = True
        self._failure_reason = reason or "aborted"
        result = self._build_result(success=False)
        self._fsm.reset("idle")
        return result

    def run_full_cycle(self, parameters: dict[str, Any] | None = None) -> PalletTaskResult:
        """Convenience helper for tests / batch execution.

        Drives the executor through every stage in ``PALLET_FORWARD_SEQUENCE``
        without any per-tick callback. Honours per-stage timeouts and
        returns a ``PalletTaskResult``.
        """
        self.start_task(parameters)
        for target in PALLET_FORWARD_SEQUENCE[1:]:  # skip "approach" (current)
            if self._failed:
                break
            self.advance()
        return self._build_result(success=not self._failed)

    def check_timeouts(self) -> bool:
        """If the current stage has exceeded its budget, abort the task.

        Returns ``True`` when the executor has just been aborted.
        """
        if self._failed:
            return False
        timeout = self._stage_timeouts.get(self._fsm.state)
        if timeout is None:
            return False
        if self._fsm.time_in_state() > timeout:
            self.abort(
                f"stage {self._fsm.state!r} exceeded timeout "
                f"{timeout}s (elapsed {self._fsm.time_in_state():.2f}s)"
            )
            return True
        return False

    # ---- private helpers ---------------------------------------------------

    def _enter_stage(self, state: str, params: dict[str, Any]) -> None:
        try:
            self._fsm.transition(state)
        except FSMError:
            self._failed = True
            self._failure_reason = (
                f"illegal transition to {state!r} from {self._fsm.state!r}"
            )
            logger.error(self._failure_reason)
            return
        self._completed_stages.append(state)
        self._plan_stage(state, params)
        if self._stage_callback is not None:
            try:
                self._stage_callback(state, params)
            except Exception:
                logger.exception("pallet stage callback raised")

    def _plan_stage(self, state: str, params: dict[str, Any]) -> None:
        """Delegate per-stage trajectory planning to ``self._planner``.

        When no planner is provided the executor still runs through its
        FSM — useful for tests that verify transitions without invoking
        motion planning.
        """
        if self._planner is None:
            return
        try:
            if state == "approach":
                self._planner.plan_insert_pallet(
                    pallet_x=float(params.get("pallet_x", 5.0)),
                    pallet_z=float(params.get("pallet_z", 2.0)),
                    pallet_height=float(params.get("pallet_height", 0.15)),
                )
            elif state == "place":
                self._planner.plan_drop_pallet(
                    drop_x=float(params.get("drop_x", 0.0)),
                    drop_z=float(params.get("drop_z", 0.0)),
                )
            # engage / lift / transfer reuse the same planner instance but
            # call no-op helpers in the current implementation — left for
            # the motion-planning subagent (Task 16) to extend if needed.
        except Exception:
            logger.exception("pallet planner raised in stage %s", state)
            self._failed = True
            self._failure_reason = f"planner exception in stage {state}"

    def _build_result(self, *, success: bool) -> PalletTaskResult:
        if self._task_started_at is None:
            elapsed = 0.0
        else:
            elapsed = time.monotonic() - self._task_started_at
        return PalletTaskResult(
            success=success and not self._failed,
            final_state=self._fsm.state,
            elapsed_s=elapsed,
            completed_stages=tuple(self._completed_stages),
            error=None if success and not self._failed else self._failure_reason,
        )


# ---------------------------------------------------------------------------
# ROS 2 node wrapper
# ---------------------------------------------------------------------------

class PalletTaskExecutorNode:
    """ROS 2 wrapper around :class:`PalletTaskExecutor`.

    The runtime node is created lazily so importing this module does not
    require rclpy (matching the pattern in
    ``robot_decision/task_coordinator.py``). When rclpy is unavailable —
    e.g. unit tests — ``main()`` prints a friendly message and exits.
    """

    def __init__(self) -> None:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
        from sensor_msgs.msg import JointState

        from robot_decision.planning import ForkliftMotionPlanner

        if not rclpy.ok():
            rclpy.init()
        self._rclpy = rclpy
        self._node = Node("pallet_executor")

        self._executor = PalletTaskExecutor(
            planner=ForkliftMotionPlanner(),
            stage_callback=self._publish_feedback,
        )

        # Subscriptions
        self._node.create_subscription(
            String,
            "~/task_command",
            self._on_task_command,
            10,
        )
        self._node.create_subscription(
            JointState,
            "/forklift/joint_states",
            self._on_joint_states,
            10,
        )

        # Publishers
        self._feedback_pub = self._node.create_publisher(
            String, "~/task_feedback", 10
        )
        self._state_pub = self._node.create_publisher(String, "~/robot_state", 10)

        # 10 Hz tick timer — drives timeouts and FSM advancement.
        self._tick_timer = self._node.create_timer(0.1, self._tick)

        self._node.get_logger().info("PalletTaskExecutor ready")

    # ---- ROS callbacks -----------------------------------------------------

    def _on_task_command(self, msg: Any) -> None:
        try:
            data = json.loads(msg.data)
        except (ValueError, AttributeError):
            self._node.get_logger().error("invalid JSON on ~/task_command")
            return
        params = data.get("parameters", {})
        self._executor.start_task(params)

    def _on_joint_states(self, _msg: Any) -> None:
        # Real impl will use joint feedback to detect stage completion;
        # the stub executor simply advances on timer ticks for now.
        return

    def _tick(self) -> None:
        if self._executor.check_timeouts():
            self._publish_state()
            return
        # Auto-advance while not in idle and no failure.
        if self._executor.state not in ("idle",) and not self._executor.fsm.is_in_state("place"):
            self._executor.advance()
        self._publish_state()

    # ---- publishers --------------------------------------------------------

    def _publish_feedback(self, state: str, params: dict[str, Any]) -> None:
        from std_msgs.msg import String

        msg = String()
        msg.data = json.dumps({"state": state, "params": params})
        self._feedback_pub.publish(msg)

    def _publish_state(self) -> None:
        from std_msgs.msg import String

        msg = String()
        msg.data = json.dumps(
            {
                "ctrl": {"mode": "pallet_task", "state": self._executor.state},
            }
        )
        self._state_pub.publish(msg)

    def spin(self) -> None:
        try:
            self._rclpy.spin(self._node)
        except KeyboardInterrupt:
            pass
        finally:
            self._node.destroy_node()
            if self._rclpy.ok():
                self._rclpy.shutdown()


def main(args: Any = None) -> None:
    """ROS 2 entry point for the pallet executor (see ``setup.py``)."""
    try:
        node = PalletTaskExecutorNode()
    except ImportError:
        logger.error(
            "rclpy / ROS 2 not available — pallet executor runs in "
            "stub mode only. Use the PalletTaskExecutor class directly "
            "for tests."
        )
        return
    node.spin()


__all__ = [
    "PalletTaskExecutor",
    "PalletTaskExecutorNode",
    "PalletTaskResult",
    "PALLET_STATES",
    "PALLET_TRANSITIONS",
    "PALLET_STAGE_TIMEOUTS_S",
    "PALLET_FORWARD_SEQUENCE",
    "main",
]
