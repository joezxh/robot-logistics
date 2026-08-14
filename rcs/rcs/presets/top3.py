"""Top 3 loading scenario presets (RCS view).

Mirrors ``simulation/backend/services/scene_presets.py`` but adds controller
class registry and MQTT topic configuration per scene.
"""
from __future__ import annotations

from typing import Any

from ..devices import ForkliftSpec, DualArmLoaderSpec
from ..controllers.agv import AgvController
from ..controllers.stacker import StackerController


class Top3PresetManager:
    PALLET_DEVICES: dict[str, dict[str, Any]] = {
        "forklift-01": {
            "device_type": "pallet_forklift",
            "spec": ForkliftSpec(device_id="forklift-01", travel_range_m=50.0),
            "controller_cls": None,
            "mqtt_topic_cmd": "rcs/forklift-01/command",
            "mqtt_topic_status": "rcs/forklift-01/status",
        },
        "forklift-02": {
            "device_type": "pallet_forklift",
            "spec": ForkliftSpec(device_id="forklift-02", travel_range_m=50.0),
            "controller_cls": None,
            "mqtt_topic_cmd": "rcs/forklift-02/command",
            "mqtt_topic_status": "rcs/forklift-02/status",
        },
        "agv-01": {
            "device_type": "agv",
            "controller_cls": AgvController,
            "mqtt_topic_cmd": "rcs/agv-01/command",
            "mqtt_topic_status": "rcs/agv-01/status",
        },
    }

    BOX_DEVICES: dict[str, dict[str, Any]] = {
        "loader-01": {
            "device_type": "loading_robot",
            "spec": DualArmLoaderSpec(device_id="loader-01"),
            "controller_cls": None,
            "mqtt_topic_cmd": "rcs/loader-01/command",
            "mqtt_topic_status": "rcs/loader-01/status",
        },
        "agv-01": {
            "device_type": "agv",
            "controller_cls": AgvController,
            "mqtt_topic_cmd": "rcs/agv-01/command",
            "mqtt_topic_status": "rcs/agv-01/status",
        },
        "agv-02": {
            "device_type": "agv",
            "controller_cls": AgvController,
            "mqtt_topic_cmd": "rcs/agv-02/command",
            "mqtt_topic_status": "rcs/agv-02/status",
        },
        "stacker-01": {
            "device_type": "stacker",
            "controller_cls": StackerController,
            "mqtt_topic_cmd": "rcs/stacker-01/command",
            "mqtt_topic_status": "rcs/stacker-01/status",
        },
    }

    BAG_DEVICES: dict[str, dict[str, Any]] = {
        "loader-01": {
            "device_type": "loading_robot",
            "spec": DualArmLoaderSpec(device_id="loader-01"),
            "controller_cls": None,
            "mqtt_topic_cmd": "rcs/loader-01/command",
            "mqtt_topic_status": "rcs/loader-01/status",
        },
        "agv-01": {
            "device_type": "agv",
            "controller_cls": AgvController,
            "mqtt_topic_cmd": "rcs/agv-01/command",
            "mqtt_topic_status": "rcs/agv-01/status",
        },
        "stacker-01": {
            "device_type": "stacker",
            "controller_cls": StackerController,
            "mqtt_topic_cmd": "rcs/stacker-01/command",
            "mqtt_topic_status": "rcs/stacker-01/status",
        },
    }

    PRESETS: dict[str, dict[str, dict[str, Any]]] = {
        "pallet": PALLET_DEVICES,
        "box": BOX_DEVICES,
        "bag": BAG_DEVICES,
    }

    @classmethod
    def list(cls) -> list[str]:
        return list(cls.PRESETS.keys())

    @classmethod
    def load(cls, name: str) -> dict[str, dict[str, Any]]:
        if name not in cls.PRESETS:
            raise KeyError(f"unknown scene: {name!r}; available: {cls.list()}")
        return cls.PRESETS[name]

    @classmethod
    def get_mqtt_topics(cls, name: str) -> dict[str, dict[str, str]]:
        if name not in cls.PRESETS:
            raise KeyError(f"unknown scene: {name!r}")
        result: dict[str, dict[str, str]] = {}
        for device_id, spec in cls.PRESETS[name].items():
            result[device_id] = {
                "cmd": spec["mqtt_topic_cmd"],
                "status": spec["mqtt_topic_status"],
            }
        return result
