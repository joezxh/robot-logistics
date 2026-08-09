#!/usr/bin/env python3
"""Export a trained checkpoint into a bundle robot_decision can load.

    python scripts/export_model.py --checkpoint outputs/checkpoints/best
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vla_training.config import get_by_path, load_config  # noqa: E402
from vla_training.export.to_inference import export  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        nargs="+",
        default=[
            "configs/base.yaml",
            "configs/dataset.yaml",
            "configs/finetune_lora.yaml",
        ],
    )
    parser.add_argument("--checkpoint", required=True, help="checkpoint directory to export")
    parser.add_argument("--export-dir", help="override paths.export_dir")
    parser.add_argument(
        "--no-merge",
        action="store_true",
        help="write the manifest only, keeping adapters separate from the base weights",
    )
    args = parser.parse_args(argv)

    config = load_config(*args.config)
    logging.basicConfig(
        level=str(get_by_path(config, "logging.level", "INFO")),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    export_dir = args.export_dir or get_by_path(config, "paths.export_dir", "outputs/export")
    path = export(args.checkpoint, export_dir, config, merge_adapters=not args.no_merge)

    print(f"Exported to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
