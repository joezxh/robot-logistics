"""Export a trained checkpoint into the bundle ``robot_decision`` consumes.

The exported bundle is deliberately self-describing. Three things must travel
together or inference silently misbehaves:

1. **Weights** -- merged LoRA adapters (merging avoids paying PEFT's wrapper
   overhead on every inference step).
2. **Normalisation statistics** -- the model predicts *normalised* actions.
   Denormalising with anything other than the training statistics produces
   plausible-looking but wrong joint targets.
3. **Action space metadata** -- dimension, ordering and semantics, so the robot
   can reject a model that does not match its arm instead of executing it.

Consumer: ``robot-app/ros2_ws/src/robot_decision``.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from ..config import get_by_path
from ..data.converter import STATS_FILENAME
from ..data.types import DatasetStats

logger = logging.getLogger(__name__)

MANIFEST_FILENAME = "inference_manifest.json"
BUNDLE_VERSION = 1


@dataclass
class InferenceManifest:
    """Everything the robot needs to use a checkpoint correctly.

    RCS-aligned: ``robot_type`` declares the target robot using the unified
    ``RobotType`` taxonomy (RCS stock arms + robot-logic logistics morphologies)
    so a model is unambiguously bound to the hardware it was trained for.
    """

    bundle_version: int = BUNDLE_VERSION
    base_model: str = ""
    robot_type: str = ""
    action_dim: int = 0
    action_space: str = "joint_position"
    chunk_size: int = 1
    image_size: list[int] = field(default_factory=lambda: [224, 224])
    camera_names: list[str] = field(default_factory=list)
    action_mean: list[float] = field(default_factory=list)
    action_std: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle_version": self.bundle_version,
            "base_model": self.base_model,
            "robot_type": self.robot_type,
            "action_dim": self.action_dim,
            "action_space": self.action_space,
            "chunk_size": self.chunk_size,
            "image_size": self.image_size,
            "camera_names": self.camera_names,
            "action_mean": self.action_mean,
            "action_std": self.action_std,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "InferenceManifest":
        return cls(
            bundle_version=int(data.get("bundle_version", 0)),
            base_model=str(data.get("base_model", "")),
            robot_type=str(data.get("robot_type", "")),
            action_dim=int(data.get("action_dim", 0)),
            action_space=str(data.get("action_space", "joint_position")),
            chunk_size=int(data.get("chunk_size", 1)),
            image_size=list(data.get("image_size", [224, 224])),
            camera_names=list(data.get("camera_names", [])),
            action_mean=list(data.get("action_mean", [])),
            action_std=list(data.get("action_std", [])),
        )

    def validate_against_robot(self, *, robot_action_dim: int, robot_type: str = "") -> None:
        """Refuse a model that does not fit the arm it is about to drive.

        Called by ``robot_decision`` at load time. Executing a 7-DOF policy on a
        6-DOF arm is a hardware-damaging failure, so it must fail at load, not
        at the first command.
        """
        if self.bundle_version != BUNDLE_VERSION:
            raise ValueError(
                f"unsupported bundle version {self.bundle_version} "
                f"(expected {BUNDLE_VERSION})"
            )
        if self.action_dim != robot_action_dim:
            raise ValueError(
                f"model action_dim {self.action_dim} != robot action_dim "
                f"{robot_action_dim}; refusing to load"
            )
        if robot_type and self.robot_type and self.robot_type != robot_type:
            raise ValueError(
                f"model robot_type {self.robot_type} != robot {robot_type}; "
                f"refusing to load"
            )
        if len(self.action_mean) != self.action_dim or len(self.action_std) != self.action_dim:
            raise ValueError("normalisation statistics do not match action_dim")


def build_manifest(config: Mapping[str, Any], stats: DatasetStats) -> InferenceManifest:
    """Assemble the manifest from the training config and dataset statistics."""
    cameras = [c["name"] for c in get_by_path(config, "observation.images", []) or []]
    first_image = (get_by_path(config, "observation.images", []) or [{}])[0]
    return InferenceManifest(
        base_model=str(get_by_path(config, "model.base_model", "")),
        robot_type=str(get_by_path(config, "action.robot_type", "")),
        action_dim=int(get_by_path(config, "action.dim", len(stats.action_mean))),
        action_space=str(get_by_path(config, "action.space", "joint_position")),
        chunk_size=int(get_by_path(config, "action.chunk_size", 1)),
        image_size=list(first_image.get("resolution", [224, 224])),
        camera_names=cameras,
        action_mean=list(stats.action_mean),
        action_std=list(stats.action_std),
    )


def export(
    checkpoint_dir: str | Path,
    export_dir: str | Path,
    config: Mapping[str, Any],
    *,
    merge_adapters: bool = True,
) -> Path:
    """Produce a deployable bundle at ``export_dir``."""
    checkpoint_dir = Path(checkpoint_dir)
    export_dir = Path(export_dir)
    if not checkpoint_dir.is_dir():
        raise FileNotFoundError(f"checkpoint not found: {checkpoint_dir}")
    export_dir.mkdir(parents=True, exist_ok=True)

    processed = Path(str(get_by_path(config, "paths.processed_data_dir", "data/processed")))
    stats_path = processed / STATS_FILENAME
    if not stats_path.is_file():
        raise FileNotFoundError(
            f"missing {stats_path}: the exported model would have no way to "
            "denormalise its predictions"
        )
    stats = DatasetStats.from_dict(json.loads(stats_path.read_text(encoding="utf-8")))

    manifest = build_manifest(config, stats)
    (export_dir / MANIFEST_FILENAME).write_text(
        json.dumps(manifest.to_dict(), indent=2), encoding="utf-8"
    )
    logger.info("wrote %s", export_dir / MANIFEST_FILENAME)

    if merge_adapters:
        merge_and_save(checkpoint_dir, export_dir, config)

    return export_dir


def merge_and_save(checkpoint_dir: Path, export_dir: Path, config: Mapping[str, Any]) -> None:
    """Merge LoRA adapters into the base weights and write the result.

    Uses the model adapter's ``merge_adapters`` method, which delegates to
    the standard PEFT / transformers save path for HF-compatible checkpoints.
    Model families that need custom merging (e.g. non-HF checkpoints) can
    override ``merge_adapters`` in their adapter class.
    """
    from ..models.loader import build_adapter

    adapter = build_adapter(config)

    # Load the trained LoRA weights from the checkpoint.
    if hasattr(adapter.model, "from_pretrained"):
        try:
            adapter.model = type(adapter.model).from_pretrained(str(checkpoint_dir))
            logger.info("loaded LoRA weights from %s", checkpoint_dir)
        except Exception as exc:
            logger.warning("could not load checkpoint %s: %s", checkpoint_dir, exc)

    adapter.merge_adapters(export_dir)
    logger.info("exported merged model to %s", export_dir)
