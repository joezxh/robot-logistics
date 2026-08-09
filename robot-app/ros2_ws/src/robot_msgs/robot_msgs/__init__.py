"""Message contracts shared across the robot-side ROS 2 packages.

This package is built with ``ament_python``, which cannot run the ``rosidl``
generators, so the contracts are expressed as plain typed dataclasses rather
than ``.msg``/``.action`` files. They mirror ``shared/contracts/*.schema.json``
field-for-field so the ROS 2 side and the RCS side cannot drift apart.

Should these ever need to become real ROS interfaces, the package has to be
converted to ``ament_cmake`` with ``rosidl_default_generators``; the dataclasses
below then map 1:1 onto the generated types.
"""
from .contracts import (
    COMMAND_TYPES,
    TASK_TYPES,
    HUG_STATES,
    ALERT_KINDS,
    AlertMsg,
    BaseStateMsg,
    CommandMsg,
    ControllerStateMsg,
    HugParamsMsg,
    HugStateMsg,
    JointStateMsg,
    MoveCommandGoal,
    MoveCommandResult,
    Pose6DMsg,
    RobotStateMsg,
    RobotTelemetryMsg,
    TaskCommandMsg,
    TrackingErrorMsg,
    utc_now_iso,
)

__all__ = [
    "COMMAND_TYPES",
    "TASK_TYPES",
    "HUG_STATES",
    "ALERT_KINDS",
    "AlertMsg",
    "BaseStateMsg",
    "CommandMsg",
    "ControllerStateMsg",
    "HugParamsMsg",
    "HugStateMsg",
    "JointStateMsg",
    "MoveCommandGoal",
    "MoveCommandResult",
    "Pose6DMsg",
    "RobotStateMsg",
    "RobotTelemetryMsg",
    "TaskCommandMsg",
    "TrackingErrorMsg",
    "utc_now_iso",
]
