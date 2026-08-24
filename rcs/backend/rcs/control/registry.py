"""Device registry + controller/HAL singletons.

RCS-aligned: the registry keys each device to a ``RobotType`` (unifying RCS stock
arms with robot-logic logistics morphologies) so the control plane can be driven
identically whether the backend is a simulation env or real hardware.
"""
from __future__ import annotations
import json
import os
from typing import Iterable

from robot_contracts import RobotType

from .hal import DeviceHAL, SimHAL
from .controllers import Controller, ArmController, AgvController, StackerController
from .state.profile import DeviceProfile, Morphology, Limits


_DEFAULT_PROFILES: list[DeviceProfile] = [
    DeviceProfile(
        device_id="robot-01",
        morphology=Morphology.ARM,
        num_joints=6,
        control_hz=1000,
        limits=Limits(
            pos_lower=[-3.14159] * 6,
            pos_upper=[3.14159] * 6,
            vel_max=[2.5] * 6,
            acc_max=[5.0] * 6,
        ),
        home_joints=[0.0] * 6,
    ),
    DeviceProfile(
        device_id="agv-01",
        morphology=Morphology.AGV,
        num_joints=2,
        control_hz=50,
        limits=Limits(
            pos_lower=[-2.0, -2.0],
            pos_upper=[2.0, 2.0],
            vel_max=[1.0, 1.0],
            acc_max=[2.0, 2.0],
        ),
        home_joints=[0.0, 0.0],
    ),
    DeviceProfile(
        device_id="stacker-01",
        morphology=Morphology.STACKER,
        num_joints=2,
        control_hz=50,
        limits=Limits(
            pos_lower=[-5.0, -10.0],
            pos_upper=[5.0, 10.0],
            vel_max=[1.0, 2.0],
            acc_max=[2.0, 4.0],
        ),
        home_joints=[0.0, 0.0],
    ),
]


class Registry:
    def __init__(self) -> None:
        self._profiles: dict[str, DeviceProfile] = {}
        self._controllers: dict[str, Controller] = {}
        self._hal: DeviceHAL = SimHAL()
        self._loaded = False

    def _build_controller(self, profile: DeviceProfile) -> Controller:
        if profile.morphology == Morphology.ARM:
            return ArmController(profile)
        if profile.morphology == Morphology.AGV:
            return AgvController(profile)
        if profile.morphology == Morphology.STACKER:
            return StackerController(profile)
        raise ValueError(f"unsupported morphology: {profile.morphology}")

    def load(self, profiles: Iterable[DeviceProfile] | None = None) -> None:
        if self._loaded:
            return
        env = os.environ.get("RCS_DEVICE_PROFILES", "").strip()
        if env:
            data = json.loads(env)
            profiles = [_profile_from_dict(item) for item in data]
        else:
            profiles = profiles or _DEFAULT_PROFILES
        for p in profiles:
            self._profiles[p.device_id] = p
            self._controllers[p.device_id] = self._build_controller(p)
            self._hal.register(p)
        self._loaded = True

    def list_devices(self) -> list[DeviceProfile]:
        return list(self._profiles.values())

    def get_profile(self, device_id: str) -> DeviceProfile:
        return self._profiles[device_id]

    def get_controller(self, device_id: str) -> Controller:
        return self._controllers[device_id]

    def get_hal(self) -> DeviceHAL:
        return self._hal

    def robot_type(self, device_id: str) -> RobotType:
        prof = self.get_profile(device_id)
        return prof.robot_type or prof.morphology.to_robot_type()

    def base_pose(self, device_id: str):
        from robot_contracts import Pose

        return self._hal.base_pose(device_id) if hasattr(self._hal, "base_pose") else Pose()

    def _reset_for_tests(self) -> None:
        self._profiles.clear()
        self._controllers.clear()
        self._hal = SimHAL()
        self._loaded = False


def _profile_from_dict(d: dict) -> DeviceProfile:
    lim = d.get("limits", {})
    rt = d.get("robot_type")
    robot_type = RobotType(rt) if rt else None
    bp = d.get("base_pose_in_world")
    base_pose = None
    if bp:
        from robot_contracts import Pose

        base_pose = Pose.from_dict(bp)
    return DeviceProfile(
        device_id=d["device_id"],
        morphology=Morphology(d["morphology"]),
        num_joints=d["num_joints"],
        control_hz=d["control_hz"],
        limits=Limits(
            pos_lower=lim.get("pos_lower", []),
            pos_upper=lim.get("pos_upper", []),
            vel_max=lim.get("vel_max", []),
            acc_max=lim.get("acc_max", []),
            rad_th=lim.get("rad_th", 0.05),
            pos_th=lim.get("pos_th", 0.01),
        ),
        home_joints=d.get("home_joints", []),
        locked=d.get("locked", False),
        robot_type=robot_type,
        base_pose_in_world=base_pose,
    )


registry = Registry()
