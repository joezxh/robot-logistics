"""Scene presets — mirrors ``robot-control-stack.rcs.envs.scenes``.

A scene groups an EnvConfig with task/obstacle metadata. robot-logic scenes are
the logistics presets already defined in ``backend.algorithm``, surfaced here so
the RCS-aligned stack can load them by name.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .configs import EnvConfig, get_config


@dataclass(frozen=True)
class Scene:
    name: str
    env_config: EnvConfig
    description: str = ""
    tasks: list[str] = field(default_factory=list)


SCENES: dict[str, Scene] = {
    "pallet": Scene("pallet", get_config("LogisticsArm"), "Palletizing with forklift + AGV",
                    tasks=["pallet_pick", "pallet_place"]),
    "box": Scene("box", get_config("LogisticsArm"), "Mixed carton handling",
                 tasks=["box_pick", "box_stow"]),
    "bag": Scene("bag", get_config("LogisticsArm"), "Soft bag manipulation",
                 tasks=["bag_grasp"]),
    "fr3_grasp": Scene("fr3_grasp", get_config("EmptyWorldFR3"), "RCS FR3 pick-and-place",
                       tasks=["grasp_demo"]),
}


def get_scene(name: str) -> Scene:
    if name not in SCENES:
        raise KeyError(f"unknown scene {name!r}; available: {sorted(SCENES)}")
    return SCENES[name]


__all__ = ["Scene", "SCENES", "get_scene"]
