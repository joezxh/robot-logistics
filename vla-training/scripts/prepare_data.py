#!/usr/bin/env python3
"""Convert raw trajectories into a training-ready dataset.

    python scripts/prepare_data.py --config configs/base.yaml configs/dataset.yaml
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vla_training.config import get_by_path, load_config  # noqa: E402
from vla_training.data.converter import TrajectoryConverter  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        nargs="+",
        default=["configs/base.yaml", "configs/dataset.yaml"],
        help="config files, merged left to right",
    )
    parser.add_argument("--raw-dir", help="override paths.raw_data_dir")
    parser.add_argument("--processed-dir", help="override paths.processed_data_dir")
    parser.add_argument(
        "--keep-failures",
        action="store_true",
        help="include unsuccessful episodes (excluded by default)",
    )
    args = parser.parse_args(argv)

    config = load_config(*args.config)
    logging.basicConfig(
        level=str(get_by_path(config, "logging.level", "INFO")),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    raw_dir = args.raw_dir or get_by_path(config, "paths.raw_data_dir", "data/raw")
    processed_dir = args.processed_dir or get_by_path(
        config, "paths.processed_data_dir", "data/processed"
    )

    converter = TrajectoryConverter(
        raw_dir,
        processed_dir,
        action_dim=int(get_by_path(config, "action.dim", 7)),
        val_split=float(get_by_path(config, "dataset.val_split", 0.1)),
        seed=int(get_by_path(config, "seed", 42)),
        keep_failures=args.keep_failures,
    )
    stats = converter.convert()

    print(
        f"Prepared {stats.num_episodes} training episodes "
        f"({stats.num_frames} frames) -> {processed_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
