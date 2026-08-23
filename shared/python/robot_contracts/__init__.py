"""Shared communication contracts between RCS and the robot-side application.

This package has **zero runtime dependencies on any subproject**. The dependency
direction is strictly one-way:

    rcs/       -> shared/
    robot-app/ -> shared/

Never the reverse. Changing anything here is a breaking change for both sides;
see ``shared/README.md`` for the change procedure.
"""
from .topics import (
    QOS_ALERT,
    QOS_COMMAND,
    QOS_STATE,
    QOS_TELEMETRY,
    RETAIN_ALERT,
    RETAIN_COMMAND,
    RETAIN_STATE,
    RETAIN_TELEMETRY,
    alert_topic,
    alert_topic_filter,
    command_topic,
    command_topic_filter,
    device_id_from_topic,
    state_topic,
    state_topic_filter,
    telemetry_topic,
    telemetry_topic_filter,
)
from .payloads import (
    AlertEventEnum,
    AlertPayload,
    CommandPayload,
    CommandTypeEnum,
    ControllerStatePayload,
    JointStatePayload,
    Pose6DPayload,
    StatePayload,
    TelemetryPayload,
    TrackingErrorPayload,
)
from .kinematics import (
    Pose,
    RobotType,
    GripperType,
    RobotPlatform,
    get_base_pose_in_world_coordinates,
    to_pose_in_world_coordinates,
    to_pose_in_robot_coordinates,
)
from .site_tcp import (
    SiteTCPPose,
    DEFAULT_SITE_PROFILES,
    get_site_profile,
    register_site_profile,
)

__version__ = "1.1.0"

__all__ = [
    "__version__",
    # topics
    "QOS_COMMAND",
    "QOS_STATE",
    "QOS_ALERT",
    "QOS_TELEMETRY",
    "RETAIN_COMMAND",
    "RETAIN_STATE",
    "RETAIN_ALERT",
    "RETAIN_TELEMETRY",
    "command_topic",
    "state_topic",
    "alert_topic",
    "telemetry_topic",
    "command_topic_filter",
    "state_topic_filter",
    "alert_topic_filter",
    "telemetry_topic_filter",
    "device_id_from_topic",
    # payloads
    "CommandTypeEnum",
    "Pose6DPayload",
    "CommandPayload",
    "JointStatePayload",
    "TrackingErrorPayload",
    "ControllerStatePayload",
    "StatePayload",
    "AlertEventEnum",
    "AlertPayload",
    "TelemetryPayload",
    # kinematics (RCS-aligned primitives)
    "Pose",
    "RobotType",
    "GripperType",
    "RobotPlatform",
    "get_base_pose_in_world_coordinates",
    "to_pose_in_world_coordinates",
    "to_pose_in_robot_coordinates",
    # site TCP poses
    "SiteTCPPose",
    "DEFAULT_SITE_PROFILES",
    "get_site_profile",
    "register_site_profile",
]
