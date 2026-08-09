"""Fixtures for the vla-training tests.

Only the dependency-free layers are covered: config merging, trajectory
conversion and the inference manifest. The torch/transformers-dependent paths
are skeletons and have nothing meaningful to assert yet.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vla_training.data.types import Episode, Frame, SourceType  # noqa: E402


@pytest.fixture
def make_episode():
    """Build a valid episode with monotonically increasing timestamps."""

    def _make(
        episode_id: str,
        *,
        num_frames: int = 4,
        action_dim: int = 7,
        instruction: str = "pick up the box",
        source: SourceType = SourceType.SIMULATION,
        success: bool = True,
        action_value: float | None = None,
    ) -> Episode:
        frames = []
        for i in range(num_frames):
            value = float(i) if action_value is None else action_value
            frames.append(
                Frame(
                    timestamp_ns=1_000 * (i + 1),
                    images={"wrist_cam": f"{episode_id}_{i}.png"},
                    joint_positions=[0.0] * action_dim,
                    joint_velocities=[0.0] * action_dim,
                    action=[value] * action_dim,
                )
            )
        return Episode(
            episode_id=episode_id,
            instruction=instruction,
            source=source,
            success=success,
            frames=frames,
        )

    return _make


@pytest.fixture
def raw_dir(tmp_path: Path) -> Path:
    d = tmp_path / "raw"
    d.mkdir()
    return d


@pytest.fixture
def processed_dir(tmp_path: Path) -> Path:
    return tmp_path / "processed"
