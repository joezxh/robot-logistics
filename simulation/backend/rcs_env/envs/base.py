"""Base Gymnasium environment over a :class:`PhysicsEngine`.

Mirrors ``robot-control-stack.rcs.envs.base.BaseEnv``:
* ``reset`` / ``step`` return (obs, info) / (obs, reward, terminated, truncated, info)
* the env owns the engine + an optional :class:`MjOMPL` planner
* observation = EE pose (world frame) + joint state + gripper state
* action = target joint positions (RCS ``JointsDictType``) by default

The environment is engine-agnostic — it never imports MuJoCo directly.
"""
from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np

from robot_contracts import Pose, RobotType

from ..engine import EngineConfig, build_engine
from ..ompl import MjOMPL, Planner


class SimEnv(gym.Env):
    """Gym env backed by a robot-logic physics engine (RCS parity)."""

    metadata = {"render_modes": ["rgb_array", "human"], "render_fps": 30}

    def __init__(
        self,
        robot_type: RobotType = RobotType.ARM,
        mjcf_path: str | None = None,
        logic_device_id: str | None = None,
        planner: Planner = Planner.RRTConnect,
        dt: float = 0.002,
        seed: int = 0,
        render_mode: str | None = None,
    ) -> None:
        super().__init__()
        self.render_mode = render_mode
        self.config = EngineConfig(
            robot_type=robot_type, mjcf_path=mjcf_path,
            logic_device_id=logic_device_id, dt=dt, seed=seed,
        )
        self.engine = build_engine(self.config)
        self.ompl = MjOMPL(self.engine, planner=planner)

        low, high = self.engine.joint_limits()
        self.action_space = gym.spaces.Box(low=low, high=high, dtype=np.float64)
        # obs: [ee_xyz (3), ee_quat_xyzw (4), joints (dof), gripper (1)]
        obs_dim = 3 + 4 + self.engine.dof + 1
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float64
        )
        self._gripper = 0.0  # 0 closed, 1 open
        self._rng = np.random.default_rng(seed)

    # ---- Gym API ----------------------------------------------------------- #
    def reset(self, *, seed: int | None = None, options: dict | None = None) -> tuple[np.ndarray, dict]:
        super().reset(seed=seed)
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        self.engine.reset()
        self._gripper = 0.0
        return self._observe(), self._info()

    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool, bool, dict]:
        action = np.asarray(action, dtype=float)
        # collision-aware clamp: drop infeasible commands (RCS guard)
        if not self.ompl.collision_free(action):
            action = np.clip(action, *self.engine.joint_limits())
        self.engine.step(action)
        obs = self._observe()
        reward = self._reward()
        terminated = False
        truncated = False
        return obs, reward, terminated, truncated, self._info()

    # ---- helpers ------------------------------------------------------------ #
    def _observe(self) -> np.ndarray:
        ee: Pose = self.engine.forward_kinematics(self.engine.qpos())
        joints = self.engine.qpos()
        return np.concatenate([ee.translation, ee.quaternion, joints, [self._gripper]])

    def _info(self) -> dict:
        return {
            "ee_pose": self.engine.forward_kinematics(self.engine.qpos()),
            "joints": self.engine.qpos(),
            "gripper": self._gripper,
        }

    def _reward(self) -> float:
        return 0.0

    def plan_to(self, goal_qpos: np.ndarray, planner: Planner | None = None) -> list[np.ndarray]:
        """RCS convenience: solve a joint-space path and return waypoints."""
        return self.ompl.plan(self.engine.qpos(), goal_qpos, planner)

    def plan_to_pose(self, goal_pose: np.ndarray, planner: Planner | None = None) -> list[np.ndarray]:
        """RCS convenience: solve a Cartesian goal via IK + planner."""
        return self.ompl.plan_SE3(goal_pose, planner)

    def render(self) -> Any:
        return self.engine.render()
