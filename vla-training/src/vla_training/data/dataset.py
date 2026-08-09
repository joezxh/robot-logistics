"""PyTorch ``Dataset`` over the converted shards.

Indexing is frame-level but storage is episode-level, so the constructor builds
a flat ``(episode_idx, frame_idx)`` index once. Manifests are held in memory
(small); frames and images are read lazily per ``__getitem__`` so an epoch never
materialises the whole dataset.

``torch`` is imported lazily: the collector and converter must remain usable on
machines without a training stack.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Sequence

from .converter import STATS_FILENAME, normalize_action
from .types import DatasetStats

logger = logging.getLogger(__name__)


def _torch():
    try:
        import torch

        return torch
    except ImportError as exc:  # pragma: no cover - dependency not installed
        raise ImportError(
            "PyTorch is required for the dataset; install vla-training/requirements.txt"
        ) from exc


class VLADataset:
    """Frame-indexed view over a converted split.

    Subclasses ``torch.utils.data.Dataset`` at runtime via duck typing -- it
    implements ``__len__`` and ``__getitem__``, which is all a ``DataLoader``
    requires, and avoids importing torch at module import time.

    :param chunk_size: number of consecutive future actions returned per sample.
        Predicting a chunk instead of a single step markedly reduces compounding
        error during closed-loop rollout.
    """

    def __init__(
        self,
        split_dir: str | Path,
        *,
        stats: DatasetStats | None = None,
        chunk_size: int = 1,
        image_size: tuple[int, int] = (224, 224),
        camera_names: Sequence[str] | None = None,
    ) -> None:
        self.split_dir = Path(split_dir)
        self.chunk_size = chunk_size
        self.image_size = image_size
        self.camera_names = list(camera_names or ["wrist_cam", "overhead_cam"])

        manifest_path = self.split_dir / "manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(f"missing manifest: {manifest_path}")
        self.manifest: list[dict[str, Any]] = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        self.stats = stats if stats is not None else self._load_stats()

        # Flat frame index. Built once so __getitem__ stays O(1).
        self._index: list[tuple[int, int]] = []
        for ep_idx, entry in enumerate(self.manifest):
            for frame_idx in range(int(entry["num_frames"])):
                self._index.append((ep_idx, frame_idx))

        self._episode_cache: dict[int, dict[str, Any]] = {}
        logger.info(
            "loaded %s: %d episodes, %d frames",
            self.split_dir.name,
            len(self.manifest),
            len(self._index),
        )

    def _load_stats(self) -> DatasetStats:
        # stats.json lives beside the split directories, not inside them: both
        # train and val must normalise with the *same* training statistics.
        path = self.split_dir.parent / STATS_FILENAME
        if not path.is_file():
            raise FileNotFoundError(
                f"missing {STATS_FILENAME} at {path}; run the converter first"
            )
        return DatasetStats.from_dict(json.loads(path.read_text(encoding="utf-8")))

    # --- Dataset protocol ---------------------------------------------------

    def __len__(self) -> int:
        return len(self._index)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        torch = _torch()
        ep_idx, frame_idx = self._index[idx]
        episode = self._load_episode(ep_idx)
        frames = episode["frames"]
        frame = frames[frame_idx]

        # Action chunk, right-padded by repeating the final action. Padding with
        # zeros would teach the model to stop abruptly at episode boundaries.
        chunk = []
        for offset in range(self.chunk_size):
            src = frames[min(frame_idx + offset, len(frames) - 1)]
            chunk.append(normalize_action(src["action"], self.stats))

        return {
            "images": {
                name: self._load_image(frame["images"].get(name))
                for name in self.camera_names
            },
            "instruction": episode["instruction"],
            "joint_positions": torch.tensor(
                frame.get("joint_positions", []), dtype=torch.float32
            ),
            "actions": torch.tensor(chunk, dtype=torch.float32),
            "episode_id": episode["episode_id"],
        }

    # --- loading ------------------------------------------------------------

    def _load_episode(self, ep_idx: int) -> dict[str, Any]:
        cached = self._episode_cache.get(ep_idx)
        if cached is not None:
            return cached
        entry = self.manifest[ep_idx]
        data = json.loads((self.split_dir / entry["path"]).read_text(encoding="utf-8"))
        # Bounded cache: shuffled access would otherwise pull every episode into
        # memory over one epoch.
        if len(self._episode_cache) > 64:
            self._episode_cache.clear()
        self._episode_cache[ep_idx] = data
        return data

    def _load_image(self, path: str | None):
        """Load and preprocess one camera frame.

        Skeleton: the concrete decode + normalisation must match the base VLA
        model's image processor, so it is wired up together with the model in
        :mod:`vla_training.models.loader`.
        """
        raise NotImplementedError(
            "image loading must match the base model's image processor; "
            "see vla-training/README.md"
        )


def build_dataloader(dataset: VLADataset, *, batch_size: int, shuffle: bool, num_workers: int = 4):
    """Wrap a :class:`VLADataset` in a ``torch`` ``DataLoader``."""
    torch = _torch()
    from torch.utils.data import DataLoader

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=shuffle,  # drop the ragged tail only while training
    )
