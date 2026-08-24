"""Device model abstract base class."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class DeviceModel(ABC):
    """Abstract base for all RCS-controllable device models.

    Subclasses must declare ``num_joints`` and provide ``home_joints``.
    """
    device_id: str
    position: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    num_joints: int = 0
    home_joints: list[float] = field(default_factory=list)

    @abstractmethod
    def joint_limits(self) -> tuple[list[float], list[float]]:
        """Return (pos_lower, pos_upper) per joint."""
