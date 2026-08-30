"""Factory for :class:`SimEnv` — mirrors ``robot-control-stack.rcs.envs.SimEnvCreator``.

RCS exposes ``SimEnvCreator(env_config: SimEnvCreatorConfig)`` returning a callable
that builds an env. We keep the same entry point so downstream code (robot-app,
vla-training) can construct sims identically to RCS.

Phase 2 扩展：``SimEnvCreatorConfig`` 现在可携带 :class:`EnvConfig`（`scene` 字段）。
当 `scene` 给定而 `mjcf_path` 为空时，工厂先用 :class:`ModelComposer` 拼装场景，
再据此构建引擎 —— 实现"配置即场景"的 envs 重组。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from robot_contracts import RobotType

from .base import SimEnv
from .composer import EnvConfig, compose_env
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
    # Phase 2: 场景组合配置；优先于 mjcf_path 使用
    scene: EnvConfig | None = None


class SimEnvCreator:
    """Builds a :class:`SimEnv` (optionally wrapped) from a config."""

    def __init__(self, env_config: SimEnvCreatorConfig) -> None:
        self.env_config = env_config

    def __call__(self) -> SimEnv:
        # Phase 2: 若提供 EnvConfig 场景，先经 ModelComposer 拼装出引擎
        if self.env_config.scene is not None and self.env_config.mjcf_path is None:
            engine = compose_env(
                self.env_config.scene,
                robot_type=self.env_config.robot_type,
                dt=self.env_config.dt,
            )
            env = SimEnv(
                robot_type=self.env_config.robot_type,
                logic_device_id=self.env_config.logic_device_id,
                planner=self.env_config.planner,
                dt=self.env_config.dt,
                seed=self.env_config.seed,
                render_mode=self.env_config.render_mode,
            )
            # 用组合出的引擎替换默认引擎
            env.config.mjcf_path = engine.config.mjcf_path
            env.engine = engine
            env.ompl = env._build_planner()
        else:
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


__all__ = ["SimEnvCreator", "SimEnvCreatorConfig", "EnvConfig"]

