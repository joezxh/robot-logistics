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


def evaluate_offline(model: Any, val_loader: Any, device: str) -> dict[str, float]:
    """Per-step action error over the validation split.

    Reported with the ``val_`` prefix so the keys match
    ``checkpointing.metric_for_best``.
    """
    import torch

    model.eval()
    total_mse = 0.0
    total_l1 = 0.0
    count = 0

    with torch.no_grad():
        for batch in val_loader:
            predicted = predict_actions(model, batch, device)
            target = batch["actions"].to(device)
            total_mse += float(torch.nn.functional.mse_loss(predicted, target)) * len(target)
            total_l1 += float(torch.nn.functional.l1_loss(predicted, target)) * len(target)
            count += len(target)

    model.train()
    if count == 0:
        logger.warning("validation split is empty; reporting zero error")
        return {"val_action_mse": 0.0, "val_action_l1": 0.0}

    return {"val_action_mse": total_mse / count, "val_action_l1": total_l1 / count}


def predict_actions(model: Any, batch: Any, device: str) -> Any:
    """Forward pass returning a normalised action chunk.

    Skeleton: signature depends on the base model family.
    """
    raise NotImplementedError(
        "predict_actions depends on the chosen base model; see vla-training/README.md"
    )


def evaluate_closed_loop(
    model: Any,
    tasks: Sequence[str],
    *,
    episodes_per_task: int = 10,
    max_steps: int = 500,
    config: Mapping[str, Any] | None = None,
) -> EvalReport:
    """Roll the policy out in the simulator and measure task success.

    Skeleton: requires a stepping interface and a success predicate from the
    ``simulation`` subproject.
    """
    raise NotImplementedError(
        "closed-loop evaluation requires a simulator stepping interface; "
        "see vla-training/README.md"
    )


def summarize(report: EvalReport) -> str:
    """One-line human-readable summary for logs."""
    return (
        f"success_rate={report.success_rate:.1%} "
        f"({report.num_rollouts} rollouts) "
        f"action_mse={report.action_mse:.5f} action_l1={report.action_l1:.5f}"
    )
