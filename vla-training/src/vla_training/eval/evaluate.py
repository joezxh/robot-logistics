"""Evaluation: offline action accuracy and closed-loop task success.

Both matter, and they measure different things:

* **Offline metrics** (MSE / L1 against demonstrated actions) are cheap and run
  inside the training loop, but a low MSE does *not* imply a working policy --
  errors compound over a rollout, so a model can score well per-step and still
  fail every task.
* **Closed-loop success rate** is the metric that actually predicts real-world
  behaviour. It needs the simulator in the loop, so it runs as a separate step.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

logger = logging.getLogger(__name__)

from ..config import get_by_path  # noqa: E402


@dataclass
class RolloutResult:
    """Outcome of one closed-loop episode."""

    episode_id: str
    success: bool
    steps: int
    termination_reason: str = ""


@dataclass
class EvalReport:
    """Aggregate evaluation result."""

    action_mse: float = 0.0
    action_l1: float = 0.0
    success_rate: float = 0.0
    num_rollouts: int = 0
    rollouts: list[RolloutResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_mse": self.action_mse,
            "action_l1": self.action_l1,
            "success_rate": self.success_rate,
            "num_rollouts": self.num_rollouts,
        }


def evaluate_offline(adapter: Any, val_loader: Any, device: str) -> dict[str, float]:
    """Per-step action error over the validation split.

    Reported with the ``val_`` prefix so the keys match
    ``checkpointing.metric_for_best``.

    The adapter's :meth:`predict_actions` replaces the old skeleton
    ``predict_actions`` function -- each model family knows how to extract
    action predictions from its own output format.
    """
    import torch

    if hasattr(adapter, "eval"):
        adapter.eval()
    total_mse = 0.0
    total_l1 = 0.0
    count = 0

    with torch.no_grad():
        for batch in val_loader:
            predicted = predict_actions(adapter, batch, device)
            target = batch["actions"].to(device)
            total_mse += float(torch.nn.functional.mse_loss(predicted, target)) * len(target)
            total_l1 += float(torch.nn.functional.l1_loss(predicted, target)) * len(target)
            count += len(target)

    if hasattr(adapter, "train"):
        adapter.train()
    if count == 0:
        logger.warning("validation split is empty; reporting zero error")
        return {"val_action_mse": 0.0, "val_action_l1": 0.0}

    return {"val_action_mse": total_mse / count, "val_action_l1": total_l1 / count}


def predict_actions(adapter: Any, batch: Any, device: str) -> Any:
    """Forward pass returning a normalised action chunk.

    Delegates to the adapter's :meth:`predict_actions` which knows how to
    extract the action tensor from the model-specific output format.
    """
    return adapter.predict_actions(batch, device)


def evaluate_closed_loop(
    adapter: Any,
    tasks: Sequence[str],
    *,
    episodes_per_task: int = 10,
    max_steps: int = 500,
    config: Mapping[str, Any] | None = None,
) -> EvalReport:
    """Roll the policy out in the simulator and measure task success.

    RCS-aligned (mirrors RCS ``inference`` evaluation): the policy is wrapped by
    ``robot-app.rcs_layer.vla.load_policy`` and stepped through the
    ``simulation.rcs_env.SimEnv``; each task from ``robot-app.rcs_layer.tasks``
    provides the success predicate. This is the metric that actually predicts
    real-world behaviour -- offline MSE alone is not enough.

    The function is import-safe: the sim/app packages are imported lazily so the
    offline metrics keep working without them installed.
    """
    import numpy as np
    import sys
    from pathlib import Path

    # 动态添加项目路径
    project_root = Path(__file__).resolve().parents[4]
    for subproject in ["simulation/backend", "robot-app"]:
        p = str(project_root / subproject)
        if p not in sys.path:
            sys.path.insert(0, p)

    from backend.rcs_env import SimEnv
    from backend.rcs_env.envs.configs import get_config
    from rcs_layer.vla import load_policy
    from rcs_layer.tasks import get_task

    robot_type_cfg = str(get_by_path(config or {}, "action.robot_type", "ARM"))
    cfg = get_config(get_by_path(config or {}, "sim.config_name", "LogisticsArm"))
    env0 = SimEnv(
        robot_type=cfg.robot_type,
        mjcf_path=cfg.mjcf_path,
        logic_device_id=cfg.logic_device_id,
        planner=cfg.planner,
    )
    policy = load_policy(
        get_by_path(config or {}, "eval.checkpoint", None),
        action_dim=env0.engine.dof,
    )

    rollouts: list[RolloutResult] = []
    for task_name in tasks:
        task = get_task(task_name) if task_name in ("pallet", "box", "bag") else None
        for ep in range(episodes_per_task):
            env = SimEnv(
                robot_type=cfg.robot_type,
                mjcf_path=cfg.mjcf_path,
                logic_device_id=cfg.logic_device_id,
                planner=cfg.planner,
            )
            env.reset(seed=ep)
            if task is not None:
                task.reset()
            obs, info = env.reset()
            success = False
            reason = "max_steps"
            steps = 0
            for step in range(max_steps):
                action = policy(obs)
                obs, reward, terminated, truncated, info = env.step(action)
                steps = step
                if task is not None and task.done(info):
                    success = True
                    reason = "task_done"
                    break
                if terminated or truncated:
                    reason = "env_terminal"
                    break
            rollouts.append(
                RolloutResult(
                    episode_id=f"{task_name}_{ep}",
                    success=success,
                    steps=steps,
                    termination_reason=reason,
                )
            )

    num = len(rollouts)
    success_rate = sum(r.success for r in rollouts) / num if num else 0.0
    return EvalReport(success_rate=success_rate, num_rollouts=num, rollouts=rollouts)


def summarize(report: EvalReport) -> str:
    """One-line human-readable summary for logs."""
    return (
        f"success_rate={report.success_rate:.1%} "
        f"({report.num_rollouts} rollouts) "
        f"action_mse={report.action_mse:.5f} action_l1={report.action_l1:.5f}"
    )
