"""Scene presets (RCS parity). P2.4 deliverable.

Each scene returns a :class:`SimEnvCreatorConfig` whose ``scene`` is an
:class:`EnvConfig` (assembled by :class:`ModelComposer`). Scenes reuse the shared
``assets/scenes/empty_world`` base and the per-robot / object assets.

Scenes:
* ``empty_world``        — base world + one robot (default FR3), no objects
* ``tabletop_pick``      — robot + a green cube on the table to pick
* ``tabletop_stack``     — robot + two cubes to stack
* ``duo``                — two FR3 arms on the shared ``fr3_duo_mount``
* ``hand_manipulation``  — robot + a small object for in-hand manipulation
"""
from __future__ import annotations

import os
import numpy as np

from robot_contracts import Pose, RobotType

from .composer import EnvConfig, RobotSpec, ObjectSpec, CameraSpec, compose_env
from .configs import ROBOT_ASSETS, _ROBOTS_DIR
from .creator import SimEnvCreatorConfig

_ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))
_BASE_WORLD = os.path.join(_ASSETS_DIR, "scenes", "empty_world", "scene.xml")
_OBJECTS_DIR = os.path.join(_ASSETS_DIR, "objects")


def _robot_spec(name: str, pose: Pose, gripper: bool = True) -> RobotSpec:
    asset = ROBOT_ASSETS[name]
    spec = RobotSpec(
        xml_path=os.path.join(_ROBOTS_DIR, asset.mjcf),
        prefix=f"{name}_",
        pose=pose,
    )
    return spec


def _obj_spec(name: str, prefix: str, pose: Pose) -> ObjectSpec:
    return ObjectSpec(
        xml_path=os.path.join(_OBJECTS_DIR, name, f"{name}.xml"),
        prefix=prefix,
        pose=pose,
    )


# --------------------------------------------------------------------------- #
# Scene builders — each returns a SimEnvCreatorConfig
# --------------------------------------------------------------------------- #
def empty_world(robot: str = "fr3", dt: float = 0.002, **kw) -> SimEnvCreatorConfig:
    scene = EnvConfig(
        name=f"empty_{robot}",
        base_xml=_BASE_WORLD,
        robots=[_robot_spec(robot, Pose.from_keywords())],
    )
    return SimEnvCreatorConfig(robot_type=ROBOT_ASSETS[robot].robot_type, scene=scene, dt=dt, **kw)


def tabletop_pick(robot: str = "fr3", dt: float = 0.002, **kw) -> SimEnvCreatorConfig:
    cube = _obj_spec("green_cube", "cube_", Pose.from_keywords(x=0.5, y=0.0, z=0.3))
    scene = EnvConfig(
        name=f"pick_{robot}",
        base_xml=_BASE_WORLD,
        robots=[_robot_spec(robot, Pose.from_keywords())],
        objects=[cube],
        cameras=[CameraSpec(name="cam0", resolution=(320, 240), pose=Pose.from_keywords(x=0.0, y=0.8, z=1.0))],
    )
    return SimEnvCreatorConfig(robot_type=ROBOT_ASSETS[robot].robot_type, scene=scene, dt=dt, **kw)


def tabletop_stack(robot: str = "fr3", dt: float = 0.002, **kw) -> SimEnvCreatorConfig:
    cube_a = _obj_spec("green_cube", "cube_a_", Pose.from_keywords(x=0.5, y=0.0, z=0.3))
    cube_b = _obj_spec("green_cube", "cube_b_", Pose.from_keywords(x=0.5, y=0.0, z=0.6))
    scene = EnvConfig(
        name=f"stack_{robot}",
        base_xml=_BASE_WORLD,
        robots=[_robot_spec(robot, Pose.from_keywords())],
        objects=[cube_a, cube_b],
    )
    return SimEnvCreatorConfig(robot_type=ROBOT_ASSETS[robot].robot_type, scene=scene, dt=dt, **kw)


def duo(dt: float = 0.002, **kw) -> SimEnvCreatorConfig:
    # Two FR3 arms mounted on the shared duo mount (base scene already places it)
    mount_xml = os.path.join(_OBJECTS_DIR, "fr3_duo_mount", "fr3_duo_mount.xml")
    scene = EnvConfig(
        name="duo_fr3",
        base_xml=_BASE_WORLD,
        robots=[
            _robot_spec("fr3", Pose.from_keywords(x=-0.3, y=0.0, z=0.0)),
            _robot_spec("fr3", Pose.from_keywords(x=0.3, y=0.0, z=0.0)),
        ],
    )
    # mount is part of the duo base scene; robots are placed relative to world
    return SimEnvCreatorConfig(robot_type=RobotType.FR3, scene=scene, dt=dt, **kw)


def hand_manipulation(robot: str = "fr3", dt: float = 0.002, **kw) -> SimEnvCreatorConfig:
    obj = _obj_spec("green_cube", "obj_", Pose.from_keywords(x=0.5, y=0.0, z=0.4))
    scene = EnvConfig(
        name=f"hand_{robot}",
        base_xml=_BASE_WORLD,
        robots=[_robot_spec(robot, Pose.from_keywords())],
        objects=[obj],
    )
    return SimEnvCreatorConfig(robot_type=ROBOT_ASSETS[robot].robot_type, scene=scene, dt=dt, **kw)


# Registry
SCENES: dict[str, Callable[..., SimEnvCreatorConfig]] = {
    "empty_world": empty_world,
    "tabletop_pick": tabletop_pick,
    "tabletop_stack": tabletop_stack,
    "duo": duo,
    "hand_manipulation": hand_manipulation,
}


def get_scene(name: str, **kw) -> SimEnvCreatorConfig:
    if name not in SCENES:
        raise KeyError(f"Unknown scene '{name}'. Known: {sorted(SCENES)}")
    return SCENES[name](**kw)


__all__ = ["SCENES", "get_scene", "empty_world", "tabletop_pick", "tabletop_stack", "duo", "hand_manipulation"]
