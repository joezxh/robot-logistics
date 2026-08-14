"""Tests for Top3PresetManager."""
from __future__ import annotations

import pytest

from rcs.presets import Top3PresetManager


def test_list_presets():
    names = Top3PresetManager.list()
    assert names == ["pallet", "box", "bag"]


def test_load_pallet():
    scene = Top3PresetManager.load("pallet")
    assert "forklift-01" in scene
    assert "forklift-02" in scene
    assert "agv-01" in scene
    assert scene["forklift-01"]["device_type"] == "pallet_forklift"


def test_load_box():
    scene = Top3PresetManager.load("box")
    assert "loader-01" in scene
    assert scene["loader-01"]["device_type"] == "loading_robot"
    assert "stacker-01" in scene


def test_load_bag():
    scene = Top3PresetManager.load("bag")
    assert "loader-01" in scene
    assert scene["loader-01"]["device_type"] == "loading_robot"


def test_load_unknown_raises():
    with pytest.raises(KeyError, match="unknown scene"):
        Top3PresetManager.load("nonexistent")


def test_get_mqtt_topics():
    topics = Top3PresetManager.get_mqtt_topics("pallet")
    assert topics["forklift-01"]["cmd"] == "rcs/forklift-01/command"
    assert topics["forklift-01"]["status"] == "rcs/forklift-01/status"
    assert topics["agv-01"]["cmd"] == "rcs/agv-01/command"


def test_get_mqtt_topics_unknown():
    with pytest.raises(KeyError):
        Top3PresetManager.get_mqtt_topics("nope")
