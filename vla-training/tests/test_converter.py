"""Trajectory conversion: validation, splitting, statistics and normalisation."""
from __future__ import annotations

import json

import pytest
from vla_training.data.collector import TrajectoryCollector
from vla_training.data.converter import (
    STATS_FILENAME,
    TrajectoryConverter,
    denormalize_action,
    normalize_action,
)
from vla_training.data.types import DatasetStats, Episode, Frame, SourceType


class _Sink(TrajectoryCollector):
    """Concrete collector used only to exercise save/load."""

    def collect(self, num_episodes, instruction):  # pragma: no cover - unused
        raise NotImplementedError


@pytest.fixture
def sink(raw_dir):
    return _Sink(raw_dir)


# --- episode validation -----------------------------------------------------


def test_empty_episode_is_rejected():
    with pytest.raises(ValueError, match="no frames"):
        Episode(episode_id="e", instruction="do it", source=SourceType.SIMULATION).validate()


def test_blank_instruction_is_rejected(make_episode):
    episode = make_episode("e1")
    episode.instruction = "   "

    with pytest.raises(ValueError, match="instruction"):
        episode.validate()


def test_ragged_actions_are_rejected(make_episode):
    episode = make_episode("e1", action_dim=7)
    episode.frames[2].action = [0.0] * 3

    with pytest.raises(ValueError, match="ragged"):
        episode.validate()


def test_out_of_order_frames_are_rejected(make_episode):
    episode = make_episode("e1")
    episode.frames[0].timestamp_ns, episode.frames[1].timestamp_ns = (
        episode.frames[1].timestamp_ns,
        episode.frames[0].timestamp_ns,
    )

    with pytest.raises(ValueError, match="time-ordered"):
        episode.validate()


def test_action_dim_mismatch_is_rejected(make_episode):
    episode = make_episode("e1", action_dim=6)

    with pytest.raises(ValueError, match="action dim"):
        episode.validate(expected_action_dim=7)


# --- persistence ------------------------------------------------------------


def test_episode_round_trips_through_disk(sink, make_episode):
    original = make_episode("e1", num_frames=3)

    restored = TrajectoryCollector.load(sink.save(original))

    assert restored.episode_id == original.episode_id
    assert restored.instruction == original.instruction
    assert restored.source == original.source
    assert len(restored) == 3
    assert restored.frames[1].action == original.frames[1].action


def test_save_leaves_no_temp_file_behind(sink, make_episode):
    sink.save(make_episode("e1"))

    assert list(sink.output_dir.glob("*.tmp")) == []


# --- conversion -------------------------------------------------------------


def _convert(raw_dir, processed_dir, **kwargs):
    return TrajectoryConverter(raw_dir, processed_dir, action_dim=7, **kwargs)


def test_convert_writes_splits_and_stats(sink, raw_dir, processed_dir, make_episode):
    for i in range(10):
        sink.save(make_episode(f"e{i}"))

    stats = _convert(raw_dir, processed_dir, val_split=0.2).convert()

    assert (processed_dir / STATS_FILENAME).is_file()
    assert (processed_dir / "train" / "manifest.json").is_file()
    assert (processed_dir / "val" / "manifest.json").is_file()
    assert stats.num_episodes == 8
    assert stats.num_frames == 8 * 4


def test_split_is_by_episode_so_frames_never_leak(sink, raw_dir, processed_dir, make_episode):
    for i in range(10):
        sink.save(make_episode(f"e{i}"))

    _convert(raw_dir, processed_dir, val_split=0.3).convert()

    train_ids = {
        e["episode_id"]
        for e in json.loads((processed_dir / "train" / "manifest.json").read_text())
    }
    val_ids = {
        e["episode_id"]
        for e in json.loads((processed_dir / "val" / "manifest.json").read_text())
    }

    assert train_ids and val_ids
    assert train_ids.isdisjoint(val_ids)


def test_val_split_is_never_empty_when_data_allows(sink, raw_dir, processed_dir, make_episode):
    """int(3 * 0.1) == 0, but silently training with no validation set is worse
    than borrowing one episode."""
    for i in range(3):
        sink.save(make_episode(f"e{i}"))

    _convert(raw_dir, processed_dir, val_split=0.1).convert()

    val = json.loads((processed_dir / "val" / "manifest.json").read_text())
    assert len(val) == 1


def test_failed_episodes_are_excluded_by_default(sink, raw_dir, processed_dir, make_episode):
    sink.save(make_episode("ok1"))
    sink.save(make_episode("ok2"))
    sink.save(make_episode("bad", success=False))

    stats = _convert(raw_dir, processed_dir, val_split=0.0).convert()

    assert stats.num_episodes == 2


def test_failed_episodes_can_be_kept(sink, raw_dir, processed_dir, make_episode):
    sink.save(make_episode("ok"))
    sink.save(make_episode("bad", success=False))

    stats = _convert(raw_dir, processed_dir, val_split=0.0, keep_failures=True).convert()

    assert stats.num_episodes == 2


def test_a_corrupt_manifest_is_skipped_not_fatal(sink, raw_dir, processed_dir, make_episode):
    """One bad file must not discard a whole collection run."""
    for i in range(4):
        sink.save(make_episode(f"e{i}"))
    (raw_dir / "corrupt.json").write_text("{not json", encoding="utf-8")

    stats = _convert(raw_dir, processed_dir, val_split=0.0).convert()

    assert stats.num_episodes == 4


def test_convert_fails_loudly_when_there_is_no_data(raw_dir, processed_dir):
    with pytest.raises(ValueError, match="no usable episodes"):
        _convert(raw_dir, processed_dir).convert()


def test_split_is_deterministic_for_a_fixed_seed(sink, raw_dir, processed_dir, make_episode):
    for i in range(10):
        sink.save(make_episode(f"e{i}"))

    first = _convert(raw_dir, processed_dir / "a", seed=7).convert()
    second = _convert(raw_dir, processed_dir / "b", seed=7).convert()

    assert first.action_mean == second.action_mean
    assert first.num_frames == second.num_frames


# --- statistics -------------------------------------------------------------


def test_stats_are_computed_over_all_training_frames(sink, raw_dir, processed_dir, make_episode):
    # Actions per episode are 0,1,2,3 across 7 identical dimensions.
    sink.save(make_episode("e1", num_frames=4))

    stats = _convert(raw_dir, processed_dir, val_split=0.0).convert()

    assert stats.action_mean == pytest.approx([1.5] * 7)
    assert stats.action_min == pytest.approx([0.0] * 7)
    assert stats.action_max == pytest.approx([3.0] * 7)


def test_constant_dimension_gets_a_floored_std(sink, raw_dir, processed_dir, make_episode):
    """A zero std would divide by zero and fill the batch with NaNs."""
    sink.save(make_episode("e1", action_value=2.0))

    stats = _convert(raw_dir, processed_dir, val_split=0.0).convert()

    assert all(s >= 1e-6 for s in stats.action_std)


def test_stats_round_trip_through_json():
    stats = DatasetStats(
        action_mean=[1.0, 2.0],
        action_std=[0.5, 0.5],
        action_min=[0.0, 0.0],
        action_max=[2.0, 4.0],
        num_episodes=3,
        num_frames=12,
    )

    assert DatasetStats.from_dict(json.loads(json.dumps(stats.to_dict()))) == stats


# --- normalisation ----------------------------------------------------------


def test_normalisation_round_trips():
    stats = DatasetStats(
        action_mean=[1.0, -2.0],
        action_std=[0.5, 4.0],
        action_min=[0.0, -10.0],
        action_max=[2.0, 6.0],
    )
    action = [1.75, 2.0]

    assert denormalize_action(normalize_action(action, stats), stats) == pytest.approx(action)


def test_normalisation_centres_the_mean():
    stats = DatasetStats(
        action_mean=[5.0], action_std=[2.0], action_min=[0.0], action_max=[10.0]
    )

    assert normalize_action([5.0], stats) == pytest.approx([0.0])
    assert normalize_action([7.0], stats) == pytest.approx([1.0])
