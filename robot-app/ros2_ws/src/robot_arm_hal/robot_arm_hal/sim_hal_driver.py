"""In-memory simulation HAL (default)."""
from __future__ import annotations

import threading
from typing import Optional

from .hal_interface import HALInterface, JointStateMsg, CommandMsg


class SimHalDriver(HALInterface):
    """In-memory mock driver — used for end-to-end testing without hardware."""

    def __init__(self, device_id: str, num_joints: int) -> None:
        self.device_id = device_id
        self.num_joints = num_joints
        self._lock = threading.Lock()
        self._positions: list[float] = [0.0] * num_joints
        self._velocities: list[float] = [0.0] * num_joints
        self._estopped = False
        self._last_cmd: CommandMsg | None = None
        self._cmd_count = 0

    def read_state(self) -> JointStateMsg:
        with self._lock:
            return JointStateMsg(
                positions=list(self._positions),
                velocities=list(self._velocities),
                efforts=[0.0] * self.num_joints,
                device_id=self.device_id,
            )

    def send_command(self, cmd: CommandMsg) -> bool:
        with self._lock:
            if self._estopped:
                return False
            self._last_cmd = cmd
            self._cmd_count += 1
            return True

    def estop(self) -> None:
        with self._lock:
            self._estopped = True

    def recover(self) -> None:
        with self._lock:
            self._estopped = False

    # --- test helpers ---
    def inject_state(self, positions: list[float], velocities: Optional[list[float]] = None) -> None:
        """Manually set positions for testing."""
        with self._lock:
            self._positions = list(positions)
            self._velocities = list(velocities or [0.0] * len(positions))

    def get_command_count(self) -> int:
        with self._lock:
            return self._cmd_count