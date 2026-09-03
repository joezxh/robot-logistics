"""Microduck biped locomotion environment (floating base).

Implements the official deployment contract from
``docs/superpowers/specs/2026-09-03-microduck-design.md`` §7:
* observation: 61 dims (gyro, projected gravity, joint pos/vel, last action, command)
* action: 14 dims, interpreted as an offset around ``home_pose`` scaled by ``action_scale``

Deliberately does NOT inherit :class:`rcs_env.envs.base.SimEnv` — that class is
arm-oriented (EE-pose observation, gripper, OMPL planner).
"""
from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np

from ..freebase_engine import FreeBaseMuJoCoEngine
from .microduck_cfg import (
    GRAVITY_WORLD,
    HOME_POSE,
    N_ACTION,
    N_OBS,
    OBS_COMMAND,
    OBS_GRAVITY,
    OBS_GYRO,
    OBS_JOINT_POS,
    OBS_JOINT_VEL,
    OBS_LAST_ACTION,
    POLICY_JOINTS,
    VARIANTS,
    home_pose_vector,
    quat_wxyz_to_rot,
)

# Reward weights (spec §5.5 initial defaults)
W_LIN_VEL = 1.0
W_ANG_VEL = 0.5
W_ALIVE = 0.1
W_UPRIGHT = -0.2
W_JOINT_LIMIT = -0.1
W_ACTION_RATE = -0.01
W_ENERGY = -0.001
W_SLIP = -0.05

LIN_VEL_SIGMA = 0.25
MIN_TRUNK_HEIGHT = 0.07      # m — trunk base fall threshold (model stands ~0.099 m)
MAX_TILT_DEG = 60.0
MAX_EPISODE_STEPS = 1000     # control steps (20 s at 50 Hz)


class MicroduckEnv(gym.Env):
    """Velocity-tracking locomotion env for the Microduck biped."""

    metadata = {"render_modes": ["rgb_array"], "render_fps": 50}

    def __init__(
        self,
        variant: str = "walk",
        dt: float = 0.002,
        control_dt: float = 0.02,
        action_scale: float = 0.5,
        render_mode: str | None = None,
        seed: int = 0,
    ) -> None:
        super().__init__()
        if variant not in VARIANTS:
            raise KeyError(f"Unknown variant '{variant}'. Known: {sorted(VARIANTS)}")
        self.variant_name = variant
        self.variant = VARIANTS[variant]
        self.action_scale = float(action_scale)
        self.render_mode = render_mode

        self.engine = FreeBaseMuJoCoEngine.from_variant(variant, dt=dt)
        self._control_steps = max(1, int(round(control_dt / dt)))

        # Fail fast: actuator order must match the policy joint order.
        act = [a for a in self.engine.actuator_names() if a]
        if tuple(act) != POLICY_JOINTS:
            raise ValueError(
                f"{self.variant.xml}: actuator order {act} != POLICY_JOINTS {POLICY_JOINTS}"
            )

        joint_names = self.engine.joint_names()
        self._home_vec = home_pose_vector(joint_names, self.variant)
        self._qpos_addr = [self.engine.qpos_addr[n] for n in POLICY_JOINTS]
        self._qvel_addr = [self.engine.qvel_addr[n] for n in POLICY_JOINTS]

        self.action_space = gym.spaces.Box(
            low=-1.0, high=1.0, shape=(N_ACTION,), dtype=np.float64
        )
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(N_OBS,), dtype=np.float64
        )

        self._last_action = np.zeros(N_ACTION, dtype=float)
        self._command = np.zeros(13, dtype=float)
        self._steps = 0
        self._rng = np.random.default_rng(seed)
        self._base_z = self._compute_standing_height()

    # ---- helpers ---------------------------------------------------------- #
    def _compute_standing_height(self) -> float:
        """Base z that puts the lowest geom exactly on the floor at home pose."""
        saved = self.engine.qpos().copy()
        q = saved.copy()
        for addr, name in zip(self._qpos_addr, POLICY_JOINTS):
            q[addr] = HOME_POSE[name]
        q[0:3] = 0.0
        q[3:7] = (1.0, 0.0, 0.0, 0.0)
        self.engine.reset(qpos=q)
        z = -self.engine.lowest_geom_z()
        self.engine.reset(qpos=saved)
        return float(z)

    def set_command(self, command: np.ndarray) -> None:
        """Set the 13-dim command block: twist(3) + head_pose(4) + body_pose(6)."""
        c = np.asarray(command, dtype=float).reshape(-1)
        if c.shape[0] != 13:
            raise ValueError(f"command must have 13 entries, got {c.shape[0]}")
        self._command = c.copy()

    def set_state_qpos_base_z(self, z: float) -> None:
        """Test hook: move the trunk to an absolute height (for termination tests)."""
        q = self.engine.qpos().copy()
        q[2] = float(z)
        self.engine.reset(qpos=q, qvel=np.zeros(self.engine.nv))

    # ---- observation ------------------------------------------------------ #
    def _get_obs(self) -> np.ndarray:
        qpos = self.engine.data.qpos
        qvel = self.engine.data.qvel
        rot = quat_wxyz_to_rot(qpos[3:7])          # world <- body

        gyro_body = rot.T @ qvel[3:6]              # world ang. vel -> body frame
        # Normalized projected gravity (unit vector) — matches the contract.
        proj_gravity = rot.T @ (GRAVITY_WORLD / np.linalg.norm(GRAVITY_WORLD))

        joint_pos = np.array([qpos[a] for a in self._qpos_addr])
        joint_vel = np.array([qvel[a] for a in self._qvel_addr])
        home = np.array([HOME_POSE[j] for j in POLICY_JOINTS])

        obs = np.zeros(N_OBS, dtype=np.float64)
        obs[OBS_GYRO] = gyro_body
        obs[OBS_GRAVITY] = proj_gravity
        obs[OBS_JOINT_POS] = joint_pos - home
        obs[OBS_JOINT_VEL] = joint_vel
        obs[OBS_LAST_ACTION] = self._last_action
        obs[OBS_COMMAND] = self._command
        return obs

    # ---- termination / reward --------------------------------------------- #
    def _terminated(self) -> bool:
        qpos = self.engine.data.qpos
        if float(qpos[2]) < MIN_TRUNK_HEIGHT:
            return True
        rot = quat_wxyz_to_rot(qpos[3:7])
        proj = rot.T @ (GRAVITY_WORLD / np.linalg.norm(GRAVITY_WORLD))
        tilt = float(np.degrees(np.arccos(np.clip(-proj[2], -1.0, 1.0))))
        return tilt > MAX_TILT_DEG

    def _reward(self) -> float:
        qpos = self.engine.data.qpos
        qvel = self.engine.data.qvel
        rot = quat_wxyz_to_rot(qpos[3:7])
        lin_vel_body = rot.T @ qvel[0:3]

        cmd_vx, cmd_vy, cmd_vyaw = self._command[0], self._command[1], self._command[2]
        lin_err = (lin_vel_body[0] - cmd_vx) ** 2 + (lin_vel_body[1] - cmd_vy) ** 2
        ang_err = (qvel[5] - cmd_vyaw) ** 2
        r_track = W_LIN_VEL * float(np.exp(-lin_err / LIN_VEL_SIGMA))
        r_ang = W_ANG_VEL * float(np.exp(-ang_err / LIN_VEL_SIGMA))

        proj = rot.T @ (GRAVITY_WORLD / np.linalg.norm(GRAVITY_WORLD))
        r_up = W_UPRIGHT * float(np.linalg.norm(proj[0:2]))

        joint_pos = np.array([qpos[a] for a in self._qpos_addr])
        home = np.array([HOME_POSE[j] for j in POLICY_JOINTS])
        r_limit = W_JOINT_LIMIT * float(np.sum(np.abs(joint_pos - home) > 0.9))

        r_rate = W_ACTION_RATE * float(np.sum(self._last_action ** 2))
        r_energy = W_ENERGY * float(np.sum(np.abs(self.engine.data.qfrc_actuator[self._qvel_addr])))

        return float(
            r_track + r_ang + W_ALIVE + r_up + r_limit + r_rate + r_energy
        )

    # ---- Gym API ---------------------------------------------------------- #
    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        q = np.zeros(self.engine.nq, dtype=float)
        q[2] = self._base_z
        q[3:7] = (1.0, 0.0, 0.0, 0.0)
        for addr, name in zip(self._qpos_addr, POLICY_JOINTS):
            q[addr] = HOME_POSE[name]
        self.engine.reset(qpos=q, qvel=np.zeros(self.engine.nv))
        self._last_action = np.zeros(N_ACTION, dtype=float)
        self._command = np.zeros(13, dtype=float)
        self._steps = 0
        return self._get_obs(), {}

    def step(self, action: np.ndarray):
        a = np.asarray(action, dtype=float).reshape(-1)
        if a.shape[0] != N_ACTION:
            raise ValueError(f"action must have {N_ACTION} entries, got {a.shape[0]}")
        a = np.clip(a, -1.0, 1.0)

        home = np.array([HOME_POSE[j] for j in POLICY_JOINTS])
        targets = home + self.action_scale * a

        for _ in range(self._control_steps):
            self.engine.step_ctrl(targets)

        self._last_action = a.copy()
        self._steps += 1

        obs = self._get_obs()
        reward = self._reward()
        terminated = self._terminated()
        truncated = self._steps >= MAX_EPISODE_STEPS
        info: dict[str, Any] = {
            "trunk_height": float(self.engine.data.qpos[2]),
            "steps": self._steps,
        }
        return obs, reward, bool(terminated), bool(truncated), info

    def close(self) -> None:
        self.engine.close()
