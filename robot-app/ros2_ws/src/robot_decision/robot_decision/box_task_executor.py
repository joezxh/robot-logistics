"""Box task executor — 5-stage FSM for dual-arm box handling.

Pure-Python orchestration (no rclpy) so the state machine is unit-testable
in isolation. The ROS 2 node wrapper ``BoxTaskExecutorNode`` lives in the
same file (``main()``) and binds the FSM to ROS topics.

Box flow (spec design.md 5.2):
    idle -> detect -> approach -> hug -> place -> idle

The dual-arm trajectory optimisation for each stage is delegated to
``robot_decision.planning.DualArmOptimizer``. Force feedback for the
``hug`` stage is delegated to :class:`robot_decision.hug_controller.HugController`.
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

BOX_STATES: tuple[str, ...] = (
    "idle",
    "detect",
    "approach",
    "hug",
    "place",
)

BOX_TRANSITIONS: dict[str, set[str]] = {
    "idle":     {"detect"},
    "detect":   {"approach"},
    "approach": {"hug"},
    "hug":      {"place"},
    "place":    {"idle"},
}

# Per-stage timeout (seconds). Box KPI is <= 5s per task (per spec).
BOX_STAGE_TIMEOUTS_S: dict[str, float] = {
    "detect":   1.0,
    "approach": 1.0,
    "hug":      1.5,
    "place":    1.5,
}

# Forward sequence used by ``run_full_cycle()`` and the ROS node.
BOX_FORWARD_SEQUENCE: tuple[str, ...] = (
    "detect",
    "approach",
    "hug",
    "place",
    "idle",
)

# Force-control thresholds for the ``hug`` stage (delegated to
# ``HugController`` at runtime). These defaults match the constants used
# in ``task_coordinator.py`` for consistency.
BOX_HUG_PRESSURE_TARGET_N: float = 50.0
BOX_HUG_PRESSURE_THRESHOLD_N: float = 45.0
BOX_HUG_APPROACH_SPEED_MPS: float = 0.2
BOX_HUG_CLOSE_SPEED_MPS: float = 0.05

# Dual-arm sync tolerance (spec design.md 3.2.2). Kept here so the executor
# advertises the contract even when the planner isn't injected.
BOX_DUAL_ARM_SYNC_TOLERANCE_M: float = 0.003


# ---------------------------------------------------------------------------
# Result data classes
# ---------------------------------------------------------------------------

@dataclass
class BoxTaskResult:
    """Final outcome of a box task cycle."""

    success: bool
    final_state: str
    elapsed_s: float
    completed_stages: tuple[str, ...] = field(default_factory=tuple)
    error: str | None = None


# ---------------------------------------------------------------------------
# Executor
# ---------------------------------------------------------------------------

StageFn = Callable[[dict[str, Any]], None]


class BoxTaskExecutor:
    """5-stage dual-arm box executor.

    Parameters
    ----------
    planner:
        Object exposing ``optimize`` (DualArmOptimizer). Defaults to a
        fresh ``DualArmOptimizer`` from the ``planning`` subpackage.
    hug_controller:
        Object exposing ``HugController`` API. Defaults to a fresh
        ``HugController``. Pass ``None`` for stub-only tests.
    stage_callback:
        Optional callable invoked on every successful transition.
    stage_timeouts:
        Override the default per-stage timeouts.
    """

    def __init__(
        self,
        planner: Any = None,
        hug_controller: Any = None,
        stage_callback: Callable[[str, dict[str, Any]], None] | None = None,
        stage_timeouts: dict[str, float] | None = None,
    ) -> None:
        self._planner = planner
        self._hug = hug_controller
        self._stage_callback = stage_callback
        self._stage_timeouts: dict[str, float] = dict(BOX_STAGE_TIMEOUTS_S)
        if stage_timeouts:
            self._stage_timeouts.update(stage_timeouts)

        self._fsm = FSM(
            states=BOX_STATES,
            transitions=BOX_TRANSITIONS,
            initial="idle",
        )
        self._current_params: dict[str, Any] = {}
        self._task_started_at: float | None = None
        self._completed_stages: list[str] = []
        self._failed = False
        self._failure_reason: str | None = None
        # Force-feedback tracking for the ``hug`` stage.
        self._hug_pressure_l: float = 0.0
        self._hug_pressure_r: float = 0.0

    # ---- introspection -----------------------------------------------------

    @property
    def state(self) -> str:
        return self._fsm.state

    @property
    def fsm(self) -> FSM:
        return self._fsm

    # ---- public API --------------------------------------------------------

    def start_task(self, parameters: dict[str, Any] | None = None) -> None:
        """Begin a new box task cycle (enters ``detect``)."""
        params = dict(parameters or {})
        self._current_params = params
        self._task_started_at = time.monotonic()
        self._completed_stages = []
        self._failed = False
        self._failure_reason = None
        self._hug_pressure_l = 0.0
        self._hug_pressure_r = 0.0

        if self._fsm.state != "idle":
            logger.warning(
                "box executor: starting task from non-idle state %s; resetting",
                self._fsm.state,
            )
            self._fsm.reset("idle")

        self._enter_stage("detect", params)

    def advance(self) -> str:
        """Advance to the next stage in the forward sequence."""
        if self._failed:
            return self._fsm.state
        try:
            idx = BOX_FORWARD_SEQUENCE.index(self._fsm.state)
        except ValueError:
            return self._fsm.state
        next_state = BOX_FORWARD_SEQUENCE[idx + 1]
        if next_state == self._fsm.state:
            return self._fsm.state
        if not self._fsm.can_transition(next_state):
            logger.warning(
                "box executor: cannot advance from %s to %s",
                self._fsm.state,
                next_state,
            )
            return self._fsm.state
        self._enter_stage(next_state, self._current_params)
        return self._fsm.state

    def abort(self, reason: str = "") -> BoxTaskResult:
        """Abort the current task and return the final result."""
        self._failed = True
        self._failure_reason = reason or "aborted"
        result = self._build_result(success=False)
        self._fsm.reset("idle")
        return result

    def run_full_cycle(self, parameters: dict[str, Any] | None = None) -> BoxTaskResult:
        """Drive through every stage in ``BOX_FORWARD_SEQUENCE``."""
        self.start_task(parameters)
        for target in BOX_FORWARD_SEQUENCE[1:]:
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

    # ---- hug feedback ------------------------------------------------------

    def update_hug_feedback(self, pressure_left: float, pressure_right: float) -> None:
        """Forward force-feedback to the ``HugController``.

        No-op when no controller is attached or the executor is not in the
        ``hug`` stage. The hug controller's own phase machine transitions
        to ``HOLDING`` once the pressure threshold is reached; the executor
        does not auto-advance from ``hug`` to ``place`` until that happens.
        """
        if self._hug is None or self._fsm.state != "hug":
            return
        self._hug_pressure_l = float(pressure_left)
        self._hug_pressure_r = float(pressure_right)
        if hasattr(self._hug, "update_feedback"):
            try:
                self._hug.update_feedback(pressure_left, pressure_right)
            except Exception:
                logger.exception("hug controller feedback raised")

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
                logger.exception("box stage callback raised")

    def _plan_stage(self, state: str, params: dict[str, Any]) -> None:
        """Delegate per-stage planning to ``self._planner`` and ``self._hug``.

        When no planner/controller is provided the executor still runs
        through its FSM — useful for tests that verify transitions without
        invoking motion planning.
        """
        try:
            if state == "approach" and self._planner is not None:
                self._planner.optimize(
                    left_target=[0.5, 0.0, 0.0, 0.0, 0.0, 0.0],
                    right_target=[0.5, 0.0, 0.0, 0.0, 0.0, 0.0],
                )
            elif state == "hug" and self._hug is not None:
                if hasattr(self._hug, "close"):
                    self._hug.close(
                        pressure_target=float(
                            params.get("pressure_target", BOX_HUG_PRESSURE_TARGET_N)
                        ),
                        approach_speed=float(
                            params.get("approach_speed", BOX_HUG_APPROACH_SPEED_MPS)
                        ),
                        close_speed=float(
                            params.get("close_speed", BOX_HUG_CLOSE_SPEED_MPS)
                        ),
                    )
            elif state == "place" and self._hug is not None:
                if hasattr(self._hug, "release"):
                    self._hug.release()
        except Exception:
            logger.exception("box planner/controller raised in stage %s", state)
            self._failed = True
            self._failure_reason = f"planner/controller exception in stage {state}"

    def _build_result(self, *, success: bool) -> BoxTaskResult:
        if self._task_started_at is None:
            elapsed = 0.0
        else:
            elapsed = time.monotonic() - self._task_started_at
        return BoxTaskResult(
            success=success and not self._failed,
            final_state=self._fsm.state,
            elapsed_s=elapsed,
            completed_stages=tuple(self._completed_stages),
            error=None if success and not self._failed else self._failure_reason,
        )


# ---------------------------------------------------------------------------
# ROS 2 node wrapper
# ---------------------------------------------------------------------------

class BoxTaskExecutorNode:
    """ROS 2 wrapper around :class:`BoxTaskExecutor`."""

    def __init__(self) -> None:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
        from geometry_msgs.msg import WrenchStamped

        from robot_decision.planning import DualArmOptimizer
        from robot_decision.hug_controller import HugController

        if not rclpy.ok():
            rclpy.init()
        self._rclpy = rclpy
        self._node = Node("box_executor")

        self._executor = BoxTaskExecutor(
            planner=DualArmOptimizer(),
            hug_controller=HugController(),
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
        self._node.get_logger().info("BoxTaskExecutor ready")

    # ---- ROS callbacks -----------------------------------------------------

    def _on_task_command(self, msg: Any) -> None:
        try:
            data = json.loads(msg.data)
        except (ValueError, AttributeError):
            self._node.get_logger().error("invalid JSON on ~/task_command")
            return
        self._executor.start_task(data.get("parameters", {}))

    def _on_wrench(self, msg: Any) -> None:
        # Use force.z (or x/y/z, whichever the gripper publishes) as the
        # dual-arm pressure proxy. Real dual-arm load cells publish one
        # WrenchStamped per arm; we split the payload evenly for the stub.
        wrench = getattr(msg, "wrench", None)
        if wrench is None:
            return
        force = abs(float(getattr(wrench.force, "z", 0.0)))
        self._executor.update_hug_feedback(force / 2.0, force / 2.0)

    def _tick(self) -> None:
        if self._executor.check_timeouts():
            self._publish_state()
            return
        # Auto-advance through every non-idle, non-hug stage. The hug stage
        # is driven by force feedback — see ``update_hug_feedback`` — so we
        # only advance out of it once the HugController transitions to
        # HOLDING (left as a follow-up when the gripper monitor publishes
        # force data; the stub returns to idle on its own).
        if self._executor.state not in ("idle", "hug"):
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
            {"ctrl": {"mode": "box_task", "state": self._executor.state}}
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
    """ROS 2 entry point for the box executor (see ``setup.py``)."""
    try:
        node = BoxTaskExecutorNode()
    except ImportError:
        logger.error(
            "rclpy / ROS 2 not available — box executor runs in stub "
            "mode only. Use the BoxTaskExecutor class directly for tests."
        )
        return
    node.spin()


__all__ = [
    "BoxTaskExecutor",
    "BoxTaskExecutorNode",
    "BoxTaskResult",
    "BOX_STATES",
    "BOX_TRANSITIONS",
    "BOX_STAGE_TIMEOUTS_S",
    "BOX_FORWARD_SEQUENCE",
    "BOX_HUG_PRESSURE_TARGET_N",
    "BOX_HUG_PRESSURE_THRESHOLD_N",
    "BOX_HUG_APPROACH_SPEED_MPS",
    "BOX_HUG_CLOSE_SPEED_MPS",
    "BOX_DUAL_ARM_SYNC_TOLERANCE_M",
    "main",
]
