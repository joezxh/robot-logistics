"""Factory for :class:`SimEnv` — mirrors ``robot-control-stack.rcs.envs.SimEnvCreator``.

RCS exposes ``SimEnvCreator(env_config: SimEnvCreatorConfig)`` returning a callable
that builds an env. We keep the same entry point so downstream code (robot-app,
vla-training) can construct sims identically to RCS.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from robot_contracts import RobotType

from .base import SimEnv
from ..ompl import Planner


@dataclass
class SimEnvCreatorConfig:
    """Per-environment construction config (RCS ``SimEnvCreatorConfig`` parity)."""

    robot_type: RobotType = RobotType.ARM
    mjcf_path: str | None = None
    logic_device_id: str | None = None
    planner: Planner = Planner.RRTConnect
    dt: float = 0.002
    seed: int = 0
    has_camera: bool = False
    has_gripper: bool = True
    render_mode: str | None = None
    wrappers: list[Callable[[SimEnv], SimEnv]] = field(default_factory=list)


class SimEnvCreator:
    """Builds a :class:`SimEnv` (optionally wrapped) from a config."""

    def __init__(self, env_config: SimEnvCreatorConfig) -> None:
        self.env_config = env_config

    def __call__(self) -> SimEnv:
        env = SimEnv(
            robot_type=self.env_config.robot_type,
            mjcf_path=self.env_config.mjcf_path,
            logic_device_id=self.env_config.logic_device_id,
            planner=self.env_config.planner,
            dt=self.env_config.dt,
            seed=self.env_config.seed,
            render_mode=self.env_config.render_mode,
        )
        for wrap in self.env_config.wrappers:
            env = wrap(env)
        return env


__all__ = ["SimEnvCreator", "SimEnvCreatorConfig"]
