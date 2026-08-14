"""Commands submitted to a Controller."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .pose import Pose6D


class CommandType(str, Enum):
    MOVE_J = "move_j"
    MOVE_L = "move_l"
    STOP = "stop"
    HOME = "home"
    ESTOP = "estop"
    RECOVER = "recover"
    EXECUTE_TASK = "execute_task"


@dataclass
class Command:
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: CommandType = CommandType.STOP
    target_pose: Pose6D | None = None
    target_joints: list[float] | None = None
    speed_scale: float = 1.0
    constraints: dict | None = None

    def to_dict(self) -> dict:
        return {
            "command_id": self.command_id,
            "type": self.type.value,
            "target_pose": self.target_pose.to_dict() if self.target_pose else None,
            "target_joints": list(self.target_joints) if self.target_joints else None,
            "speed_scale": self.speed_scale,
            "constraints": self.constraints,
        }
