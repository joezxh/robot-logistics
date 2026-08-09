"""Config loading with layered overrides.

Configs merge left-to-right so a run can be described by composing files rather
than duplicating them::

    load_config("configs/base.yaml", "configs/dataset.yaml",
                "configs/finetune_lora.yaml", overrides={"training.epochs": 3})

Merging is recursive for mappings and replace-on-conflict for everything else --
merging lists would make it impossible to *shorten* a list from an override.
"""
from __future__ import annotations

import copy
import logging
from pathlib import Path
from typing import Any, Mapping

logger = logging.getLogger(__name__)


class ConfigError(ValueError):
    """Raised when a config file is missing, malformed, or internally inconsistent."""


def load_config(*paths: str | Path, overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Load and merge YAML configs, then apply dotted-key overrides."""
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - dependency not installed
        raise ConfigError(
            "PyYAML is required to load configs; install vla-training/requirements.txt"
        ) from exc

    merged: dict[str, Any] = {}
    for path in paths:
        p = Path(path)
        if not p.is_file():
            raise ConfigError(f"config file not found: {p}")
        with p.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            raise ConfigError(f"config root must be a mapping: {p}")
        merged = deep_merge(merged, data)
        logger.debug("merged config layer: %s", p)

    for dotted, value in (overrides or {}).items():
        set_by_path(merged, dotted, value)

    return merged


def deep_merge(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge ``overlay`` onto ``base`` without mutating either."""
    result = copy.deepcopy(dict(base))
    for key, value in overlay.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def get_by_path(config: Mapping[str, Any], dotted: str, default: Any = None) -> Any:
    """Read ``a.b.c`` from a nested mapping."""
    node: Any = config
    for part in dotted.split("."):
        if not isinstance(node, Mapping) or part not in node:
            return default
        node = node[part]
    return node


def set_by_path(config: dict[str, Any], dotted: str, value: Any) -> None:
    """Write ``a.b.c``, creating intermediate mappings as needed."""
    parts = dotted.split(".")
    node = config
    for part in parts[:-1]:
        existing = node.get(part)
        if not isinstance(existing, dict):
            existing = {}
            node[part] = existing
        node = existing
    node[parts[-1]] = value


def require(config: Mapping[str, Any], dotted: str) -> Any:
    """Read a value that has no sensible default, failing loudly if absent."""
    sentinel = object()
    value = get_by_path(config, dotted, sentinel)
    if value is sentinel:
        raise ConfigError(f"required config key missing: {dotted}")
    return value


def resolve_device(config: Mapping[str, Any]) -> str:
    """Resolve ``runtime.device: auto`` against the machine actually running."""
    requested = str(get_by_path(config, "runtime.device", "auto"))
    if requested != "auto":
        return requested
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"
