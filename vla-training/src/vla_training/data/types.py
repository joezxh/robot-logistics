"""Trajectory data model shared by the collector, converter and dataset.

Deliberately dependency-free (no torch, no numpy) so the collection side can run
on a robot or a lightweight simulator host without a training stack installed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SourceType(str, Enum):
    """Where an episode came from. Recorded per-episode so runs stay auditable
    and so sim/real can be reweighted without re-collecting."""

    SIMULATION = "simulation"
    REAL = "real"


@dataclass(slots=True)
class Frame:
    """One control step: what the robot saw, and what it did next.

    :param images: camera name -> image reference. During collection these are
        paths on disk; loading them eagerly would blow up memory on long episodes.
    :param joint_positions: proprioceptive state at capture time.
    :param action: the action executed *from* this observation. This ordering is
        the usual off-by-one trap -- pairing an action with the state that
        followed it teaches the model to predict the past.
    """

    timestamp_ns: int
    images: dict[str, str] = field(default_factory=dict)
    joint_positions: list[float] = field(default_factory=list)
    joint_velocities: list[float] = field(default_factory=list)
    action: list[float] = field(default_factory=list)
    gripper: float = 0.0


@dataclass(slots=True)
class Episode:
    """A complete demonstration of one task attempt."""

    episode_id: str
    instruction: str
    source: SourceType
    frames: list[Frame] = field(default_factory=list)
    # Only successful episodes are used for imitation learning by default;
    # failures are still worth keeping for future failure-aware objectives.
    success: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.frames)

    @property
    def action_dim(self) -> int:
        return len(self.frames[0].action) if self.frames else 0

    def validate(self, *, expected_action_dim: int | None = None) -> None:
        """Fail loudly on the malformed episodes that would otherwise silently
        degrade a training run."""
        if not self.frames:
            raise ValueError(f"episode {self.episode_id} has no frames")
        if not self.instruction.strip():
            raise ValueError(f"episode {self.episode_id} has an empty instruction")

        dim = self.action_dim
        if expected_action_dim is not None and dim != expected_action_dim:
            raise ValueError(
                f"episode {self.episode_id}: action dim {dim} != configured "
                f"{expected_action_dim}"
            )
        for i, frame in enumerate(self.frames):
            if len(frame.action) != dim:
                raise ValueError(
                    f"episode {self.episode_id} frame {i}: ragged action "
                    f"({len(frame.action)} != {dim})"
                )
        timestamps = [f.timestamp_ns for f in self.frames]
        if timestamps != sorted(timestamps):
            raise ValueError(f"episode {self.episode_id}: frames are not time-ordered")


@dataclass(slots=True)
class DatasetStats:
    """Per-dimension action statistics used for normalisation.

    Persisted alongside the processed data and **reused verbatim at inference**:
    normalising with different statistics than the model trained on is a silent
    failure that looks like a badly trained policy.
    """

    action_mean: list[float]
    action_std: list[float]
    action_min: list[float]
    action_max: list[float]
    num_episodes: int = 0
    num_frames: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_mean": self.action_mean,
            "action_std": self.action_std,
            "action_min": self.action_min,
            "action_max": self.action_max,
            "num_episodes": self.num_episodes,
            "num_frames": self.num_frames,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DatasetStats":
        return cls(
            action_mean=list(data["action_mean"]),
            action_std=list(data["action_std"]),
            action_min=list(data["action_min"]),
            action_max=list(data["action_max"]),
            num_episodes=int(data.get("num_episodes", 0)),
            num_frames=int(data.get("num_frames", 0)),
        )
