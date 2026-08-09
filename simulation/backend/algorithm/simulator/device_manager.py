from __future__ import annotations

from .device import Device


class DeviceManager:
    def __init__(self) -> None:
        self.devices = {
            "robot-01": Device("robot-01", "container_robot", "集装箱装卸机器人", [-8.0, 0.0, 2.0], speed=0.55),
            "loader-01": Device("loader-01", "loading_robot", "双臂AGV装卸机器人", [-3.0, 0.0, 0.0], speed=0.50),
            "agv-01": Device("agv-01", "agv", "AGV 转运车", [-5.0, 0.0, -1.0], speed=1.2),
            "agv-02": Device("agv-02", "agv", "AGV 转运车 2", [1.0, 0.0, 2.0], speed=1.0),
            "stacker-01": Device("stacker-01", "stacker", "立库堆垛机", [7.0, 0.0, 0.0], speed=0.7),
        }

    def list(self) -> list[dict]:
        return [device.snapshot() for device in self.devices.values()]

    def get(self, device_id: str) -> Device:
        if device_id not in self.devices:
            raise KeyError(device_id)
        return self.devices[device_id]

    def tick(self, seconds: float) -> None:
        for device in self.devices.values():
            device.tick(seconds)
