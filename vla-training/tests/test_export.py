"""Inference manifest: the contract between training and robot_decision."""
from __future__ import annotations

import json

import pytest
from vla_training.data.types import DatasetStats
from vla_training.export.to_inference import (
    BUNDLE_VERSION,
    MANIFEST_FILENAME,
    InferenceManifest,
    build_manifest,
    export,
)


@pytest.fixture
def stats() -> DatasetStats:
    return DatasetStats(
        action_mean=[0.0] * 7,
        action_std=[1.0] * 7,
        action_min=[-1.0] * 7,
        action_max=[1.0] * 7,
        num_episodes=5,
        num_frames=40,
    )


@pytest.fixture
def config(tmp_path) -> dict:
    return {
        "paths": {"processed_data_dir": str(tmp_path / "processed")},
        "model": {"base_model": "openvla/openvla-7b"},
        "action": {"dim": 7, "space": "joint_position", "chunk_size": 8},
        "observation": {
            "images": [
                {"name": "wrist_cam", "resolution": [224, 224]},
                {"name": "overhead_cam", "resolution": [224, 224]},
            ]
        },
    }


def test_manifest_captures_everything_inference_needs(config, stats):
    manifest = build_manifest(config, stats)

    assert manifest.base_model == "openvla/openvla-7b"
    assert manifest.action_dim == 7
    assert manifest.chunk_size == 8
    assert manifest.camera_names == ["wrist_cam", "overhead_cam"]
    assert manifest.image_size == [224, 224]
    # Statistics must travel with the weights or predictions cannot be denormalised.
    assert manifest.action_mean == stats.action_mean
    assert manifest.action_std == stats.action_std


def test_manifest_round_trips_through_json(config, stats):
    manifest = build_manifest(config, stats)

    restored = InferenceManifest.from_dict(json.loads(json.dumps(manifest.to_dict())))

    assert restored == manifest


def test_matching_robot_passes_validation(config, stats):
    build_manifest(config, stats).validate_against_robot(robot_action_dim=7)


def test_action_dim_mismatch_is_refused_at_load(config, stats):
    """Executing a 7-DOF policy on a 6-DOF arm can damage hardware."""
    manifest = build_manifest(config, stats)

    with pytest.raises(ValueError, match="action_dim"):
        manifest.validate_against_robot(robot_action_dim=6)


def test_unknown_bundle_version_is_refused(config, stats):
    manifest = build_manifest(config, stats)
    manifest.bundle_version = BUNDLE_VERSION + 1

    with pytest.raises(ValueError, match="bundle version"):
        manifest.validate_against_robot(robot_action_dim=7)


def test_truncated_statistics_are_refused(config, stats):
    manifest = build_manifest(config, stats)
    manifest.action_std = [1.0, 1.0]

    with pytest.raises(ValueError, match="normalisation statistics"):
        manifest.validate_against_robot(robot_action_dim=7)


def test_export_without_stats_fails_clearly(tmp_path, config):
    checkpoint = tmp_path / "ckpt"
    checkpoint.mkdir()

    with pytest.raises(FileNotFoundError, match="denormalise"):
        export(checkpoint, tmp_path / "export", config)


def test_export_writes_the_manifest(tmp_path, config, stats):
    checkpoint = tmp_path / "ckpt"
    checkpoint.mkdir()
    processed = tmp_path / "processed"
    processed.mkdir()
    (processed / "stats.json").write_text(json.dumps(stats.to_dict()), encoding="utf-8")

    export_dir = export(checkpoint, tmp_path / "export", config, merge_adapters=False)

    written = json.loads((export_dir / MANIFEST_FILENAME).read_text())
    assert written["action_dim"] == 7
    assert written["bundle_version"] == BUNDLE_VERSION


def test_export_rejects_a_missing_checkpoint(tmp_path, config):
    with pytest.raises(FileNotFoundError, match="checkpoint not found"):
        export(tmp_path / "nope", tmp_path / "export", config)
