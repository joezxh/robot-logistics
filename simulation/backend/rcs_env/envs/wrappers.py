"""Gym env wrappers — mirrors ``robot-control-stack.rcs.envs`` wrapper stack.

Each wrapper mirrors an RCS wrapper:
* :class:`RobotWrapper`     — robot control-mode action space (joint/cartesian/TQuat)
* :class:`GripperWrapper`   — directly injects gripper command
* :class:`CameraSetWrapper` — injects RGB/depth frames into the observation
* :class:`TaskWrapper`      — binds a logistics task (pallet/box/bag) as a reward fn
"""
from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np

from robot_contracts import Pose, RobotType


class RobotWrapper(gym.Wrapper):
    """Adds a control-mode action head (RCS ``RobotWrapper`` parity)."""

    def __init__(self, env: gym.Env, robot_type: RobotType = RobotType.ARM) -> None:
        super().__init__(env)
        self.robot_type = robot_type


class GripperWrapper(gym.Wrapper):
    """Maps a gripper command into the obs/action (RCS ``GripperWrapper`` parity)."""

    def __init__(self, env: gym.Env) -> None:
        super().__init__(env)
        self.action_space = gym.spaces.Dict(
            {
                "arm": env.action_space,
                "gripper": gym.spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32),
            }
        )

    def step(self, action: dict) -> tuple[Any, float, bool, bool, dict]:
        arm = np.asarray(action["arm"], dtype=float)
        obs, reward, terminated, truncated, info = self.env.step(arm)
        info["gripper"] = float(np.asarray(action["gripper"]).reshape(-1)[0])
        return obs, reward, terminated, truncated, info


class CameraSetWrapper(gym.Wrapper):
    """Injects RGB/depth camera frames into the observation dict.

    Mirrors RCS ``CameraSetWrapper`` data-injection for vision policies
    (used by vla-training / robot-app inference).

    Args:
        env: Base Gymnasium environment
        renderer: SimRenderer instance for rendering. If None, returns zero frames.
        height: Image height in pixels
        width: Image width in pixels
        color_dim: Number of color channels (3 for RGB)
        include_depth: Whether to include depth channel
    """

    RGB_KEY = "rgb"
    DEPTH_KEY = "depth"

    def __init__(
        self,
        env: gym.Env,
        renderer: "SimRenderer | None" = None,
        height: int = 240,
        width: int = 320,
        color_dim: int = 3,
        include_depth: bool = True,
    ) -> None:
        super().__init__(env)
        self._renderer = renderer
        self.height = height
        self.width = width
        self.color_dim = color_dim
        self.include_depth = include_depth

        # 构建观测空间
        self.observation_space = gym.spaces.Dict({
            "state": env.observation_space,
            self.RGB_KEY: gym.spaces.Box(
                low=0, high=255,
                shape=(height, width, color_dim),
                dtype=np.uint8
            ),
        })
        if include_depth:
            self.observation_space.spaces[self.DEPTH_KEY] = gym.spaces.Box(
                low=0.0, high=10.0,
                shape=(height, width, 1),
                dtype=np.float32
            )

    def reset(self, **kwargs):  # type: ignore[override]
        obs, info = self.env.reset(**kwargs)
        frames = self._render_frames()
        return {"state": obs, **frames}, info

    def step(self, action):  # type: ignore[override]
        obs, reward, terminated, truncated, info = self.env.step(action)
        frames = self._render_frames()
        return {"state": obs, **frames}, reward, terminated, truncated, info

    def _render_frames(self) -> dict:
        if self._renderer is None:
            frames: dict = {
                self.RGB_KEY: np.zeros(
                    (self.height, self.width, self.color_dim), dtype=np.uint8
                ),
            }
            if self.include_depth:
                frames[self.DEPTH_KEY] = np.zeros(
                    (self.height, self.width, 1), dtype=np.float32
                )
            return frames
        result = self._renderer.render()
        frames = {
            self.RGB_KEY: result.get("rgb", np.zeros((self.height, self.width, self.color_dim), dtype=np.uint8)),
        }
        if self.include_depth:
            frames[self.DEPTH_KEY] = result.get(
                "depth", np.zeros((self.height, self.width, 1), dtype=np.float32)
            )
        return frames


class TaskWrapper(gym.Wrapper):
    """Binds a logistics task as the reward/termination signal.

    Mirrors RCS ``TaskWrapper``: a task object supplies ``reward(obs, info)`` and
    ``done(obs, info)``. robot-app provides concrete logistics tasks
    (pallet / box / bag) implementing this protocol.
    """

    def __init__(self, env: gym.Env, task: Any) -> None:
        super().__init__(env)
        self.task = task

    def reset(self, **kwargs):  # type: ignore[override]
        obs, info = self.env.reset(**kwargs)
        if hasattr(self.task, "reset"):
            self.task.reset()
        return obs, info

    def step(self, action):  # type: ignore[override]
        obs, reward, terminated, truncated, info = self.env.step(action)
        if hasattr(self.task, "reward"):
            reward = float(self.task.reward(info))
        if hasattr(self.task, "done") and self.task.done(info):
            terminated = True
        return obs, reward, terminated, truncated, info


__all__ = ["RobotWrapper", "GripperWrapper", "CameraSetWrapper", "TaskWrapper"]
