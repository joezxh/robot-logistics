#!/usr/bin/env python3
"""Launch LoRA fine-tuning.

    python scripts/run_finetune.py \
        --config configs/base.yaml configs/dataset.yaml configs/finetune_lora.yaml \
        --set training.epochs=3 training.batch_size=4
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vla_training.config import get_by_path, load_config  # noqa: E402
from vla_training.train.finetune import finetune  # noqa: E402


def parse_overrides(pairs: list[str]) -> dict[str, object]:
    """Parse ``--set a.b=1 c.d=text`` into a dotted-key override mapping."""
    overrides: dict[str, object] = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"invalid --set entry (expected key=value): {pair}")
        key, raw = pair.split("=", 1)
        overrides[key.strip()] = _coerce(raw.strip())
    return overrides


def _coerce(raw: str) -> object:
    """Best-effort scalar typing so ``epochs=3`` is an int, not the string "3"."""
    lowered = raw.lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    if lowered in ("none", "null"):
        return None
    for cast in (int, float):
        try:
            return cast(raw)
        except ValueError:
            continue
    return raw


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
        help="config files, merged left to right",
    )
    parser.add_argument(
        "--set",
        nargs="*",
        default=[],
        dest="overrides",
        metavar="KEY=VALUE",
        help="dotted-key config overrides applied last",
    )
    args = parser.parse_args(argv)

    config = load_config(*args.config, overrides=parse_overrides(args.overrides))
    logging.basicConfig(
        level=str(get_by_path(config, "logging.level", "INFO")),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    state = finetune(config)
    print(f"Finished at step {state.step}, best metric {state.best_metric:.5f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
