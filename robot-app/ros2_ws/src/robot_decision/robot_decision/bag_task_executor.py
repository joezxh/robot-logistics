"""Bag task executor — 5-stage FSM for bag handling with anti-swing control.

Pure-Python orchestration (no rclpy) so the state machine is unit-testable
in isolation. The ROS 2 node wrapper ``BagTaskExecutorNode`` lives in the
same file (``main()``) and binds the FSM to ROS topics.

Bag flow (spec design.md 5.3):
    idle -> detect -> grip -> carry -> release -> idle

The anti-swing carry trajectory is delegated to
``robot_decision.planning.BagTrajectoryGenerator``. Bag-specific grip
parameters (anti-slip pattern) are forwarded to a gripper controller at
runtime.
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

BAG_STATES: tuple[str, ...] = (
    "idle",
    "detect",
    "grip",
    "carry",
    "release",
)

BAG_TRANSITIONS: dict[str, set[str]] = {
    "idle":    {"detect"},
    "detect":  {"grip"},
    "grip":    {"carry"},
    "carry":   {"release"},
    "release": {"idle"},
}

# Per-stage timeout (seconds). Bag KPI is <= 8s per task (per spec).
BAG_STAGE_TIMEOUTS_S: dict[str, float] = {
    "detect":  1.0,
    "grip":    2.0,
    "carry":   3.0,
    "release": 2.0,
}

# Forward sequence used by ``run_full_cycle()`` and the ROS node.
BAG_FORWARD_SEQUENCE: tuple[str, ...] = (
    "detect",
    "grip",
    "carry",
    "release",
    "idle",
)

# Anti-slip / anti-swing tuning knobs. Values mirror the defaults used by
# ``BagTrajectoryGenerator`` in the planning subpackage.
BAG_ANTI_SLIP_PATTERN: str = "anti_slip"
BAG_GRIP_FORCE_N: float = 35.0
BAG_ANTI_SWING_DAMPING: float = 0.8
BAG_CARRY_DURATION_S: float = 4.0

# Slider / slip thresholds (spec design.md 5.3 KPI). Reported by the
# gripper monitor and consumed by ``record_grip_feedback`` to validate
# the ``grip`` stage.
BAG_SLIP_RATE_MAX: float = 0.01   # 1% slip allowed
BAG_BREAK_RATE_MAX: float = 0.005 # 0.5% breakage allowed


# ---------------------------------------------------------------------------
# Result data classes
# ---------------------------------------------------------------------------

@dataclass
class BagTaskResult:
    """Final outcome of a bag task cycle."""

    success: bool
    final_state: str
    elapsed_s: float
    completed_stages: tuple[str, ...] = field(default_factory=tuple)
    error: str | None = None


# ---------------------------------------------------------------------------
# Executor
# ---------------------------------------------------------------------------

StageFn = Callable[[dict[str, Any]], None]


class BagTaskExecutor:
    """5-stage bag executor with anti-slip grip and anti-swing carry.

    Parameters
    ----------
    planner:
        Object exposing ``generate(start, end)`` (BagTrajectoryGenerator).
        Defaults to a fresh ``BagTrajectoryGenerator`` from the
        ``planning`` subpackage.
    gripper_controller:
        Object exposing ``close_grip`` / ``open_grip`` (optional). Pass
        ``None`` for stub-only tests.
    stage_callback:
        Optional callable invoked on every successful transition.
    stage_timeouts:
        Override the default per-stage timeouts.
    """

    def __init__(
        self,
        planner: Any = None,
        gripper_controller: Any = None,
        stage_callback: Callable[[str, dict[str, Any]], None] | None = None,
        stage_timeouts: dict[str, float] | None = None,
    ) -> None:
        self._planner = planner
        self._gripper = gripper_controller
        self._stage_callback = stage_callback
        self._stage_timeouts: dict[str, float] = dict(BAG_STAGE_TIMEOUTS_S)
        if stage_timeouts:
            self._stage_timeouts.update(stage_timeouts)

        self._fsm = FSM(
            states=BAG_STATES,
            transitions=BAG_TRANSITIONS,
            initial="idle",
        )
        self._current_params: dict[str, Any] = {}
        self._task_started_at: float | None = None
        self._completed_stages: list[str] = []
        self._failed = False
        self._failure_reason: str | None = None
        # Bag-specific feedback accumulators.
        self._slip_observed: float = 0.0
        self._break_observed: float = 0.0
        self._swing_amplitude: float = 0.0

    # ---- introspection -----------------------------------------------------

    @property
    def state(self) -> str:
        return self._fsm.state

    @property
    def fsm(self) -> FSM:
        return self._fsm

    # ---- public API --------------------------------------------------------

    def start_task(self, parameters: dict[str, Any] | None = None) -> None:
        """Begin a new bag task cycle (enters ``detect``)."""
        params = dict(parameters or {})
        self._current_params = params
        self._task_started_at = time.monotonic()
        self._completed_stages = []
        self._failed = False
        self._failure_reason = None
        self._slip_observed = 0.0
        self._break_observed = 0.0
        self._swing_amplitude = 0.0

        if self._fsm.state != "idle":
            logger.warning(
                "bag executor: starting task from non-idle state %s; resetting",
                self._fsm.state,
            )
            self._fsm.reset("idle")

        self._enter_stage("detect", params)

    def advance(self) -> str:
        """Advance to the next stage in the forward sequence."""
        if self._failed:
            return self._fsm.state
        try:
            idx = BAG_FORWARD_SEQUENCE.index(self._fsm.state)
        except ValueError:
            return self._fsm.state
        next_state = BAG_FORWARD_SEQUENCE[idx + 1]
        if next_state == self._fsm.state:
            return self._fsm.state
        if not self._fsm.can_transition(next_state):
            logger.warning(
                "bag executor: cannot advance from %s to %s",
                self._fsm.state,
                next_state,
            )
            return self._fsm.state
        self._enter_stage(next_state, self._current_params)
        return self._fsm.state

    def abort(self, reason: str = "") -> BagTaskResult:
        """Abort the current task and return the final result."""
        self._failed = True
        self._failure_reason = reason or "aborted"
        result = self._build_result(success=False)
        self._fsm.reset("idle")
        return result

    def run_full_cycle(self, parameters: dict[str, Any] | None = None) -> BagTaskResult:
        """Drive through every stage in ``BAG_FORWARD_SEQUENCE``."""
        self.start_task(parameters)
        for target in BAG_FORWARD_SEQUENCE[1:]:
            if self._failed:
                break
            self.advance()
        return self._build_result(success=not self._failed)

    def check_timeouts(self) -> bool:
        """If the current stage has exceeded its budget, abort the task."""
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

    # ---- bag-specific feedback --------------------------------------------

    def record_grip_feedback(self, slip_rate: float, break_rate: float) -> None:
        """Forward gripper slip / breakage telemetry.

        No-op outside the ``grip`` stage. If the cumulative rates exceed
        the KPI thresholds (spec design.md 5.3) the executor aborts.
        """
        if self._fsm.state != "grip":
            return
        self._slip_observed = max(self._slip_observed, float(slip_rate))
        self._break_observed = max(self._break_observed, float(break_rate))
        if self._slip_observed > BAG_SLIP_RATE_MAX:
            self.abort(
                f"slip rate {self._slip_observed:.3f} > {BAG_SLIP_RATE_MAX}"
            )
        elif self._break_observed > BAG_BREAK_RATE_MAX:
            self.abort(
                f"break rate {self._break_observed:.3f} > {BAG_BREAK_RATE_MAX}"
            )

    def record_carry_feedback(self, swing_amplitude: float) -> None:
        """Track peak swing amplitude during the ``carry`` stage."""
        if self._fsm.state != "carry":
            return
        self._swing_amplitude = max(self._swing_amplitude, float(swing_amplitude))

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
                logger.exception("bag stage callback raised")

    def _plan_stage(self, state: str, params: dict[str, Any]) -> None:
        """Delegate per-stage planning to ``self._planner`` / gripper.

        When no planner/controller is provided the executor still runs
        through its FSM — useful for tests that verify transitions without
        invoking motion planning.
        """
        try:
            if state == "grip" and self._gripper is not None:
                if hasattr(self._gripper, "close_grip"):
                    self._gripper.close_grip(
                        grip_pattern=params.get(
                            "grip_pattern", BAG_ANTI_SLIP_PATTERN
                        ),
                        force_n=float(params.get("force_n", BAG_GRIP_FORCE_N)),
                    )
            elif state == "carry" and self._planner is not None:
                self._planner.generate(
                    start=tuple(params.get("start", (0.0, 0.0, 1.0))),
                    end=tuple(params.get("end", (2.0, 0.0, 1.0))),
                    duration_s=float(
                        params.get("duration_s", BAG_CARRY_DURATION_S)
                    ),
                )
            elif state == "release" and self._gripper is not None:
                if hasattr(self._gripper, "open_grip"):
                    self._gripper.open_grip()
        except Exception:
            logger.exception("bag planner/gripper raised in stage %s", state)
            self._failed = True
            self._failure_reason = f"planner/gripper exception in stage {state}"

    def _build_result(self, *, success: bool) -> BagTaskResult:
        if self._task_started_at is None:
            elapsed = 0.0
        else:
            elapsed = time.monotonic() - self._task_started_at
        return BagTaskResult(
            success=success and not self._failed,
            final_state=self._fsm.state,
            elapsed_s=elapsed,
            completed_stages=tuple(self._completed_stages),
            error=None if success and not self._failed else self._failure_reason,
        )


# ---------------------------------------------------------------------------
# ROS 2 node wrapper
# ---------------------------------------------------------------------------

class BagTaskExecutorNode:
    """ROS 2 wrapper around :class:`BagTaskExecutor`."""

    def __init__(self) -> None:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
        from geometry_msgs.msg import WrenchStamped

        from robot_decision.planning import BagTrajectoryGenerator

        if not rclpy.ok():
            rclpy.init()
        self._rclpy = rclpy
        self._node = Node("bag_executor")

        self._executor = BagTaskExecutor(
            planner=BagTrajectoryGenerator(),
            stage_callback=self._publish_feedback,
        )

        # Subscriptions
        self._node.create_subscription(
            String, "~/task_command", self._on_task_command, 10
        )
        self._node.create_subscription(
            WrenchStamped, "/gripper/wrench", self._on_wrench, 10
        )

        # Publishers
        self._feedback_pub = self._node.create_publisher(
            String, "~/task_feedback", 10
        )
        self._state_pub = self._node.create_publisher(String, "~/robot_state", 10)

        self._tick_timer = self._node.create_timer(0.1, self._tick)
        self._node.get_logger().info("BagTaskExecutor ready")

    # ---- ROS callbacks -----------------------------------------------------

    def _on_task_command(self, msg: Any) -> None:
        try:
            data = json.loads(msg.data)
        except (ValueError, AttributeError):
            self._node.get_logger().error("invalid JSON on ~/task_command")
            return
        self._executor.start_task(data.get("parameters", {}))

    def _on_wrench(self, msg: Any) -> None:
        # Map raw wrench into slip/break proxies. Real gripper monitor
        # publishes per-stage telemetry; for the stub we treat force.z
        # variation as a slip proxy.
        wrench = getattr(msg, "wrench", None)
        if wrench is None:
            return
        force_z = float(getattr(wrench.force, "z", 0.0))
        # Normalise by grip force target — slip proxy (unitless ratio).
        slip_proxy = abs(force_z) / max(BAG_GRIP_FORCE_N, 1e-6)
        self._executor.record_grip_feedback(slip_proxy, 0.0)

    def _tick(self) -> None:
        if self._executor.check_timeouts():
            self._publish_state()
            return
        # Auto-advance through every non-idle stage. The carry stage
        # finishes on its own once the planned trajectory duration
        # elapses; the stub ROS node advances on every tick.
        if self._executor.state != "idle":
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
            {"ctrl": {"mode": "bag_task", "state": self._executor.state}}
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
    """ROS 2 entry point for the bag executor (see ``setup.py``)."""
    try:
        node = BagTaskExecutorNode()
    except ImportError:
        logger.error(
            "rclpy / ROS 2 not available — bag executor runs in stub "
            "mode only. Use the BagTaskExecutor class directly for tests."
        )
        return
    node.spin()


__all__ = [
    "BagTaskExecutor",
    "BagTaskExecutorNode",
    "BagTaskResult",
    "BAG_STATES",
    "BAG_TRANSITIONS",
    "BAG_STAGE_TIMEOUTS_S",
    "BAG_FORWARD_SEQUENCE",
    "BAG_ANTI_SLIP_PATTERN",
    "BAG_GRIP_FORCE_N",
    "BAG_ANTI_SWING_DAMPING",
    "BAG_CARRY_DURATION_S",
    "BAG_SLIP_RATE_MAX",
    "BAG_BREAK_RATE_MAX",
    "main",
]
