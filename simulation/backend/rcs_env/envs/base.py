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
    """Gym env backed by a robot-logic physics engine (RCS parity).

    P3 additions (Gym capability completeness):
    * goal-conditioned task: ``goal_ee`` (target EE pose) + dense reward
      (negative EE-position distance) + success termination on close reach
    * ``reset`` samples a random collision-free goal when none is set
    * ``render`` returns an ``rgb_array`` frame (shaped HxWx3) when a renderer
      is available, else ``None``
    * ``close`` releases the engine (avoids the CRT heap-corruption at exit)
    * ``metadata`` / ``spec`` for gym registry compatibility
    """

    metadata = {"render_modes": ["rgb_array", "human"], "render_fps": 30}

    # distance (m) at which the EE is considered to have reached the goal
    GOAL_TOLERANCE = 0.02

    def __init__(
        self,
        robot_type: RobotType = RobotType.ARM,
        mjcf_path: str | None = None,
        logic_device_id: str | None = None,
        planner: Planner = Planner.RRTConnect,
        dt: float = 0.002,
        seed: int = 0,
        render_mode: str | None = None,
        goal_ee: "Pose | None" = None,
    ) -> None:
        super().__init__()
        self.render_mode = render_mode
        self.config_planner = planner
        self.config = EngineConfig(
            robot_type=robot_type, mjcf_path=mjcf_path,
            logic_device_id=logic_device_id, dt=dt, seed=seed,
        )
        self.engine = build_engine(self.config)
        self.ompl = MjOMPL(self.engine, planner=planner)
        self._goal_ee = goal_ee

        low, high = self.engine.joint_limits()
        self.action_space = gym.spaces.Box(low=low, high=high, dtype=np.float64)
        # obs: [ee_xyz (3), ee_quat_xyzw (4), joints (dof), gripper (1)]
        obs_dim = 3 + 4 + self.engine.dof + 1
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float64
        )
        self._gripper = 0.0  # 0 closed, 1 open
        self._rng = np.random.default_rng(seed)

    def _build_planner(self) -> "MjOMPL":
        """(Re)build the OMPL planner bound to the current engine."""
        return MjOMPL(self.engine, planner=self.config_planner)

    # ---- Gym API ----------------------------------------------------------- #
    def reset(self, *, seed: int | None = None, options: dict | None = None) -> tuple[np.ndarray, dict]:
        super().reset(seed=seed)
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        self.engine.reset()
        self._gripper = 0.0
        # Sample a goal if none supplied (tabletop reach band)
        if self._goal_ee is None:
            self._goal_ee = self._sample_goal()
        return self._observe(), self._info()

    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool, bool, dict]:
        action = np.asarray(action, dtype=float)
        # collision-aware clamp: drop infeasible commands (RCS guard)
        if not self.ompl.collision_free(action):
            action = np.clip(action, *self.engine.joint_limits())
        self.engine.step(action)
        obs = self._observe()
        reward = self.compute_reward(obs)
        terminated = self.compute_terminated(obs)
        truncated = False
        return obs, reward, terminated, truncated, self._info()

    # ---- task / reward ------------------------------------------------------ #
    def _ee_pose(self) -> Pose:
        return self.engine.forward_kinematics(self.engine.qpos())

    def _sample_goal(self) -> Pose:
        """Sample a collision-free EE goal within a reasonable tabletop band."""
        for _ in range(40):
            xyz = self._rng.uniform([0.3, -0.3, 0.2], [0.6, 0.3, 0.6])
            goal = Pose.from_keywords(x=float(xyz[0]), y=float(xyz[1]), z=float(xyz[2]))
            # validate via IK feasibility: forward kinematics of a solved config
            try:
                q = self.engine.inverse_kinematics(goal, self.engine.qpos())
            except Exception:
                q = None
            if q is not None and self.ompl.collision_free(list(q)):
                return goal
        return Pose.from_keywords(x=0.5, y=0.0, z=0.4)

    def compute_reward(self, obs: np.ndarray | None = None) -> float:
        """Dense reward: -||EE_pos - goal_pos|| (with a success bonus)."""
        if self._goal_ee is None:
            return 0.0
        ee = self._ee_pose()
        dist = float(np.linalg.norm(np.asarray(ee.translation) - np.asarray(self._goal_ee.translation)))
        reward = -dist
        if dist < self.GOAL_TOLERANCE:
            reward += 10.0  # success bonus
        return float(reward)

    def compute_terminated(self, obs: np.ndarray | None = None) -> bool:
        if self._goal_ee is None:
            return False
        ee = self._ee_pose()
        dist = float(np.linalg.norm(np.asarray(ee.translation) - np.asarray(self._goal_ee.translation)))
        return dist < self.GOAL_TOLERANCE

    # ---- helpers ------------------------------------------------------------ #
    def _observe(self) -> np.ndarray:
        ee: Pose = self._ee_pose()
        joints = self.engine.qpos()
        return np.concatenate([ee.translation, ee.quaternion, joints, [self._gripper]])

    def _info(self) -> dict:
        return {
            "ee_pose": self._ee_pose(),
            "goal_ee": self._goal_ee,
            "joints": self.engine.qpos(),
            "gripper": self._gripper,
        }

    def plan_to(self, goal_qpos: np.ndarray, planner: Planner | None = None) -> list[np.ndarray]:
        """RCS convenience: solve a joint-space path and return waypoints."""
        return self.ompl.plan(self.engine.qpos(), goal_qpos, planner)

    def plan_to_pose(self, goal_pose: np.ndarray, planner: Planner | None = None) -> list[np.ndarray]:
        """RCS convenience: solve a Cartesian goal via IK + planner."""
        return self.ompl.plan_SE3(goal_pose, planner)

    def render(self) -> Any:
        """Return an rgb_array frame (HxWx3) if a renderer is attached, else None."""
        if getattr(self, "_renderer", None) is not None:
            frame = self._renderer.render()
            if isinstance(frame, dict) and "rgb" in frame:
                return frame["rgb"]
        return self.engine.render()

    def close(self) -> None:
        """Release the engine explicitly (prevents CRT heap corruption at exit)."""
        try:
            self.engine.close()
        except Exception:
            pass
        self.engine = None


# --------------------------------------------------------------------------- #
# Gym registry — P3: stable env IDs (call register_envs() once at import)
# --------------------------------------------------------------------------- #
_REGISTERED = False


def register_envs() -> None:
    """Register goal-conditioned env IDs into ``gymnasium``'s registry.

    IDs: ``"rcs/{robot}-reach-v0"`` for each robot in the roster, plus scene IDs.
    """
    global _REGISTERED
    if _REGISTERED:
        return
    from .configs import ROBOT_ASSETS, get_config
    from .scenes import SCENES

    for name, asset in ROBOT_ASSETS.items():
        cfg = get_config(name)
        gym.register(
            id=f"rcs/{name}-reach-v0",
            entry_point="rcs_env.envs.base:SimEnv",
            kwargs={"robot_type": asset.robot_type, "mjcf_path": cfg.mjcf_path},
        )
    for scene_name in SCENES:
        gym.register(
            id=f"rcs/{scene_name}-v0",
            entry_point="rcs_env.envs.base:_scene_entry",
            kwargs={"scene_name": scene_name},
        )

    from .microduck_cfg import VARIANTS

    for variant_name in VARIANTS:
        gym.register(
            id=f"rcs/microduck-{variant_name}-v0",
            entry_point="rcs_env.envs.microduck:MicroduckEnv",
            kwargs={"variant": variant_name},
        )
    _REGISTERED = True


def make_env(task_id: str) -> "SimEnv":
    """Build an env from a registered task id via ``gym.make``."""
    register_envs()
    return gym.make(task_id)


def _scene_entry(scene_name: str) -> "SimEnv":
    """Entry point for scene-based env IDs (builds SceneEnv from a preset)."""
    from .scenes import get_scene
    from .creator import SimEnvCreator

    cfg = get_scene(scene_name)
    return SimEnvCreator(cfg)()
