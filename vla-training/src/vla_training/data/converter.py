"""Convert raw episode manifests into training-ready shards.

Responsibilities:

1. Load and validate every raw episode.
2. Compute action normalisation statistics **from the training split only** --
   including validation episodes leaks their distribution into training and
   makes the validation metric optimistic.
3. Split by episode and write shards plus a ``stats.json`` sidecar.

The output layout is intentionally close to RLDS / LeRobot conventions so the
shards can be adapted to those loaders later without re-collecting data.
"""
from __future__ import annotations

import json
import logging
import math
import random
from pathlib import Path
from typing import Iterable, Sequence

from .types import DatasetStats, Episode

logger = logging.getLogger(__name__)

STATS_FILENAME = "stats.json"
MANIFEST_FILENAME = "manifest.json"


class TrajectoryConverter:
    """Turns ``raw_data_dir`` into a split, normalised ``processed_data_dir``."""

    def __init__(
        self,
        raw_dir: str | Path,
        processed_dir: str | Path,
        *,
        action_dim: int,
        val_split: float = 0.1,
        seed: int = 42,
        keep_failures: bool = False,
    ) -> None:
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.action_dim = action_dim
        self.val_split = val_split
        self.seed = seed
        self.keep_failures = keep_failures

    # --- entry point --------------------------------------------------------

    def convert(self) -> DatasetStats:
        """Run the full conversion and return the training-split statistics."""
        episodes = list(self.load_raw_episodes())
        if not episodes:
            raise ValueError(f"no usable episodes found under {self.raw_dir}")

        train, val = self.split(episodes)
        logger.info("split: %d train / %d val episodes", len(train), len(val))

        # Statistics come from the training split only -- see module docstring.
        stats = self.compute_stats(train)

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self._write_split("train", train)
        self._write_split("val", val)
        (self.processed_dir / STATS_FILENAME).write_text(
            json.dumps(stats.to_dict(), indent=2), encoding="utf-8"
        )
        logger.info("wrote processed dataset to %s", self.processed_dir)
        return stats

    # --- stages -------------------------------------------------------------

    def load_raw_episodes(self) -> Iterable[Episode]:
        """Load every raw manifest, skipping (loudly) the ones that are unusable."""
        from .collector import TrajectoryCollector

        for path in sorted(self.raw_dir.glob("*.json")):
            try:
                episode = TrajectoryCollector.load(path)
                episode.validate(expected_action_dim=self.action_dim)
            except (ValueError, KeyError, json.JSONDecodeError) as exc:
                # Skip rather than abort: one corrupt manifest should not throw
                # away a multi-day collection run.
                logger.warning("skipping %s: %s", path.name, exc)
                continue
            if not episode.success and not self.keep_failures:
                logger.debug("skipping failed episode %s", episode.episode_id)
                continue
            yield episode

    def split(self, episodes: Sequence[Episode]) -> tuple[list[Episode], list[Episode]]:
        """Split by episode, never by frame.

        Adjacent frames within an episode are near-identical; splitting between
        them puts almost the same sample on both sides and inflates the
        validation score.
        """
        shuffled = list(episodes)
        random.Random(self.seed).shuffle(shuffled)
        n_val = int(len(shuffled) * self.val_split)
        # A requested-but-rounded-away split silently trains with no validation
        # set, so borrow one episode. val_split == 0 is respected as deliberate.
        if n_val == 0 and self.val_split > 0 and len(shuffled) > 1:
            n_val = 1
        return shuffled[n_val:], shuffled[:n_val]

    def compute_stats(self, episodes: Sequence[Episode]) -> DatasetStats:
        """Per-dimension mean/std/min/max over all actions."""
        dim = self.action_dim
        count = 0
        total = [0.0] * dim
        total_sq = [0.0] * dim
        minimum = [math.inf] * dim
        maximum = [-math.inf] * dim

        for episode in episodes:
            for frame in episode.frames:
                count += 1
                for i, value in enumerate(frame.action):
                    total[i] += value
                    total_sq[i] += value * value
                    minimum[i] = min(minimum[i], value)
                    maximum[i] = max(maximum[i], value)

        if count == 0:
            raise ValueError("cannot compute statistics: no frames in the training split")

        mean = [t / count for t in total]
        std = []
        for i in range(dim):
            variance = max(total_sq[i] / count - mean[i] ** 2, 0.0)
            # Floor the std: a constant dimension (e.g. an unused joint) would
            # otherwise divide by zero and produce NaNs mid-training.
            std.append(max(math.sqrt(variance), 1e-6))

        return DatasetStats(
            action_mean=mean,
            action_std=std,
            action_min=minimum,
            action_max=maximum,
            num_episodes=len(episodes),
            num_frames=count,
        )

    # --- output -------------------------------------------------------------

    def _write_split(self, name: str, episodes: Sequence[Episode]) -> None:
        split_dir = self.processed_dir / name
        split_dir.mkdir(parents=True, exist_ok=True)
        manifest = []
        for episode in episodes:
            manifest.append(
                {
                    "episode_id": episode.episode_id,
                    "instruction": episode.instruction,
                    "source": episode.source.value,
                    "num_frames": len(episode),
                    "path": f"{episode.episode_id}.json",
                }
            )
            (split_dir / f"{episode.episode_id}.json").write_text(
                json.dumps(
                    {
                        "episode_id": episode.episode_id,
                        "instruction": episode.instruction,
                        "source": episode.source.value,
                        "success": episode.success,
                        "metadata": episode.metadata,
                        "frames": [
                            {
                                "timestamp_ns": f.timestamp_ns,
                                "images": f.images,
                                "joint_positions": f.joint_positions,
                                "joint_velocities": f.joint_velocities,
                                "action": f.action,
                                "gripper": f.gripper,
                            }
                            for f in episode.frames
                        ],
                    }
                ),
                encoding="utf-8",
            )
        (split_dir / MANIFEST_FILENAME).write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )


def normalize_action(action: Sequence[float], stats: DatasetStats) -> list[float]:
    """Apply the mean/std normalisation the model is trained against."""
    return [(a - m) / s for a, m, s in zip(action, stats.action_mean, stats.action_std)]


def denormalize_action(action: Sequence[float], stats: DatasetStats) -> list[float]:
    """Inverse of :func:`normalize_action`. Required at inference time before an
    action can be sent to the robot."""
    return [a * s + m for a, m, s in zip(action, stats.action_mean, stats.action_std)]
