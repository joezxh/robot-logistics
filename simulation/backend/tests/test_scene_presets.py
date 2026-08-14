"""Tests for scene preset data integrity."""
from backend.services.scene_presets import (
    SCENE_PRESETS, list_scene_names, get_scene,
)


def test_three_scenes_present():
    assert set(SCENE_PRESETS.keys()) == {"pallet", "box", "bag"}
    assert list_scene_names() == ["pallet", "box", "bag"]


def test_each_preset_has_required_fields():
    required = {"name", "label", "description", "sites", "devices", "tasks", "kpi_definitions"}
    for name, preset in SCENE_PRESETS.items():
        assert required.issubset(preset.keys()), f"{name} missing fields"
        assert preset["name"] == name


def test_each_preset_has_minimum_one_site_device_task():
    for name, preset in SCENE_PRESETS.items():
        assert len(preset["sites"]) >= 1, f"{name} no sites"
        assert len(preset["devices"]) >= 2, f"{name} not enough devices"
        assert len(preset["tasks"]) >= 1, f"{name} no tasks"


def test_get_scene_raises_for_unknown():
    import pytest
    with pytest.raises(KeyError, match="unknown scene"):
        get_scene("does-not-exist")


def test_pallet_has_pallet_forklift_devices():
    devices = SCENE_PRESETS["pallet"]["devices"]
    types = {d["device_type"] for d in devices}
    assert "pallet_forklift" in types
