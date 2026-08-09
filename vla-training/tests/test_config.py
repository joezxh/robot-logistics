"""Config merging, dotted-path access and override semantics."""
from __future__ import annotations

import pytest
import yaml
from vla_training.config import (
    ConfigError,
    deep_merge,
    get_by_path,
    load_config,
    require,
    set_by_path,
)


def _write(path, data):
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def test_later_files_override_earlier_ones(tmp_path):
    a = _write(tmp_path / "a.yaml", {"training": {"epochs": 10, "batch_size": 8}})
    b = _write(tmp_path / "b.yaml", {"training": {"epochs": 3}})

    config = load_config(a, b)

    assert config["training"]["epochs"] == 3
    assert config["training"]["batch_size"] == 8, "unrelated keys must survive the merge"


def test_overrides_are_applied_last(tmp_path):
    a = _write(tmp_path / "a.yaml", {"training": {"epochs": 10}})

    config = load_config(a, overrides={"training.epochs": 1, "runtime.device": "cpu"})

    assert config["training"]["epochs"] == 1
    assert config["runtime"]["device"] == "cpu"


def test_missing_file_is_reported_clearly(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.yaml")


def test_non_mapping_root_is_rejected(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("- just\n- a list\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="mapping"):
        load_config(path)


def test_deep_merge_does_not_mutate_its_inputs():
    base = {"a": {"b": 1}}
    overlay = {"a": {"c": 2}}

    merged = deep_merge(base, overlay)

    assert merged == {"a": {"b": 1, "c": 2}}
    assert base == {"a": {"b": 1}}
    assert overlay == {"a": {"c": 2}}


def test_lists_are_replaced_not_concatenated():
    """Concatenating would make it impossible to shorten a list via override."""
    merged = deep_merge({"x": [1, 2, 3]}, {"x": [9]})

    assert merged["x"] == [9]


def test_get_by_path_returns_default_for_missing_keys():
    config = {"a": {"b": 1}}

    assert get_by_path(config, "a.b") == 1
    assert get_by_path(config, "a.z", "fallback") == "fallback"
    assert get_by_path(config, "nope.deeper", None) is None


def test_set_by_path_creates_intermediate_levels():
    config = {}

    set_by_path(config, "a.b.c", 42)

    assert config == {"a": {"b": {"c": 42}}}


def test_set_by_path_replaces_a_non_mapping_node():
    config = {"a": 5}

    set_by_path(config, "a.b", 1)

    assert config == {"a": {"b": 1}}


def test_require_raises_on_a_missing_key():
    with pytest.raises(ConfigError, match="model.base_model"):
        require({}, "model.base_model")


def test_shipped_configs_load_and_compose(tmp_path):
    """The configs committed to the repo must actually merge cleanly."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[1] / "configs"
    config = load_config(root / "base.yaml", root / "dataset.yaml", root / "finetune_lora.yaml")

    assert config["seed"] == 42
    assert config["action"]["dim"] == 7
    assert config["lora"]["alpha"] == 2 * config["lora"]["r"], "alpha is conventionally 2r"
    assert "action_head" in config["lora"]["modules_to_save"]
