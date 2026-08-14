from __future__ import annotations

from typing import Iterable

from .device import Device


DEFAULT_SEED_DEVICES: list[dict] = [
    {"device_id": "robot-01", "device_type": "container_robot",
     "name": "集装箱装卸机器人", "x": -8.0, "z": 2.0, "speed": 0.55},
    {"device_id": "loader-01", "device_type": "loading_robot",
     "name": "双臂AGV装卸机器人", "x": -3.0, "z": 0.0, "speed": 0.50},
    {"device_id": "agv-01", "device_type": "agv",
     "name": "AGV 转运车", "x": -5.0, "z": -1.0, "speed": 1.2},
    {"device_id": "agv-02", "device_type": "agv",
     "name": "AGV 转运车 2", "x": 1.0, "z": 2.0, "speed": 1.0},
    {"device_id": "stacker-01", "device_type": "stacker",
     "name": "立库堆垛机", "x": 7.0, "z": 0.0, "speed": 0.7},
]


class DeviceManager:
    def __init__(self, seed_devices: Iterable[dict] | None = None) -> None:
        if seed_devices is None:
            seed_devices = DEFAULT_SEED_DEVICES
        self.devices: dict[str, Device] = {}
        for spec in seed_devices:
            self._register(spec)

    def _register(self, spec: dict) -> None:
        device = Device(
            device_id=spec["device_id"],
            device_type=spec["device_type"],
            name=spec["name"],
            position=[spec["x"], 0.0, spec["z"]],
            speed=spec.get("speed", 0.8),
        )
        self.devices[device.device_id] = device

    def add(self, spec: dict) -> Device:
        """Register a device at runtime (used by scene_presets.load_scene)."""
        if spec["device_id"] in self.devices:
            raise ValueError(f"device {spec['device_id']!r} already exists")
        self._register(spec)
        return self.devices[spec["device_id"]]

    def list(self) -> list[dict]:
        return [device.snapshot() for device in self.devices.values()]

    def get(self, device_id: str) -> Device:
        if device_id not in self.devices:
            raise KeyError(device_id)
        return self.devices[device_id]

    def tick(self, seconds: float) -> None:
        for device in self.devices.values():
            device.tick(seconds)
