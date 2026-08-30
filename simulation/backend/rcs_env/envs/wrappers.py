"""Gym-compatible wrappers for :class:`SimEnv` (P3.2).

These wrappers extend the base :class:`SimEnv` (flat-Box goal-conditioned obs)
with robot- and task-specific channels, mirroring the RCS ``rcs.envs.wrappers``
surface so downstream training/teleop code can compose envs identically.

All wrappers are standard ``gym.Wrapper`` subclasses and can be passed via
``SimEnvCreatorConfig.wrappers`` (the factory applies them in order) or wrapped
manually::

    env = GripperWrapper(HandWrapper(SimEnvCreator(cfg)()))

Implemented wrappers
--------------------
* :class:`GripperWrapper`     — appends gripper open/close state to the obs and
                               accepts a trailing gripper action (0=open,1=close),
                               forwarded to the engine gripper when present.
* :class:`HandWrapper`       — appends dexterous-hand finger joint angles (zeros
                               placeholder on gripper-only robots) so VLA/teleop
                               policies see the full end-effector.
* :class:`StorageWrapper`    — appends warehouse storage context (rack/bin
                               occupancy) sourced from the env topology when
                               available; zeros placeholder otherwise.
* :class:`DigitalTwinWrapper`— stamps every step with a digital-twin telemetry
                               record (robot type, qpos, ee pose) for replay,
                               leaving obs/action spaces unchanged.
"""
from __future__ import annotations

from collections import deque
from typing import Any, Mapping, Sequence

import gymnasium as gym
import numpy as np

from robot_contracts import RobotType


class _SimEnvWrapper(gym.Wrapper):
    """Base wrapper that safely reaches the underlying :class:`SimEnv` engine."""

    @property
    def _simenv(self):
        env = self.env
        while hasattr(env, "env"):
            if type(env).__name__ == "SimEnv":
                return env
            env = env.env
        return env


class _BoxObsWrapper(_SimEnvWrapper):
    """Helper that concatenates extra channels to a flat-Box observation."""

    def _extend_obs_space(self, extra_low: np.ndarray, extra_high: np.ndarray):
        base = self.env.observation_space
        low = np.concatenate([np.asarray(base.low, dtype=float), extra_low])
        high = np.concatenate([np.asarray(base.high, dtype=float), extra_high])
        self.observation_space = gym.spaces.Box(low=low, high=high, dtype=float)

    def _augment_obs(self, obs: np.ndarray, extra: Sequence[float]) -> np.ndarray:
        return np.concatenate([np.asarray(obs, dtype=float).reshape(-1), extra])


class GripperWrapper(_BoxObsWrapper):
    """Expose the gripper as an extra obs channel + an extra action dimension.

    The gripper action is the last element of the wrapped action (0 = open,
    1 = close). It is forwarded to the engine gripper when one exists; otherwise
    it is recorded for telemetry only.
    """

    def __init__(self, env: gym.Env) -> None:
        super().__init__(env)
        self._extend_obs_space(np.array([0.0]), np.array([1.0]))
        base = env.action_space
        self.action_space = gym.spaces.Box(
            low=np.concatenate([np.asarray(base.low, dtype=float), [0.0]]),
            high=np.concatenate([np.asarray(base.high, dtype=float), [1.0]]),
            dtype=float,
        )
        self._gripper_state = 0.0

    def reset(self, *, seed=None, options=None):
        obs, info = self.env.reset(seed=seed, options=options)
        self._gripper_state = 0.0
        return self._augment_obs(obs, [self._gripper_state]), info

    def step(self, action: Sequence[float]):
        action = np.asarray(action, dtype=float).reshape(-1)
        grip = float(np.clip(action[-1], 0.0, 1.0))
        arm_action = action[:-1]
        self._gripper_state = grip

        engine = getattr(self._simenv, "engine", None)
        gripper = getattr(engine, "gripper", None) if engine is not None else None
        if gripper is not None:
            try:
                gripper.set_state(grip)
            except Exception:
                pass

        obs, reward, terminated, truncated, info = self.env.step(arm_action)
        info = dict(info)
        info["gripper_state"] = self._gripper_state
        return self._augment_obs(obs, [self._gripper_state]), reward, terminated, truncated, info


class HandWrapper(_BoxObsWrapper):
    """Append dexterous-hand finger joint angles to the observation.

    Reads finger state from ``engine.hand`` when present (so-101 / allegro style
    hands); zeros placeholder otherwise so downstream input shapes stay stable.
    """

    def __init__(self, env: gym.Env, n_fingers: int = 6) -> None:
        super().__init__(env)
        self.n_fingers = int(n_fingers)
        self._extend_obs_space(np.zeros(self.n_fingers), np.ones(self.n_fingers))
        self.action_space = env.action_space

    def reset(self, *, seed=None, options=None):
        obs, info = self.env.reset(seed=seed, options=options)
        return self._augment_obs(obs, self._finger_state()), info

    def step(self, action: Sequence[float]):
        obs, reward, terminated, truncated, info = self.env.step(action)
        return self._augment_obs(obs, self._finger_state()), reward, terminated, truncated, info

    def _finger_state(self) -> np.ndarray:
        engine = getattr(self._simenv, "engine", None)
        hand = getattr(engine, "hand", None) if engine is not None else None
        if hand is not None:
            try:
                q = np.asarray(hand.get_joint_position(), dtype=float).reshape(-1)
                if q.size >= self.n_fingers:
                    return q[: self.n_fingers]
            except Exception:
                pass
        return np.zeros(self.n_fingers)


class StorageWrapper(_BoxObsWrapper):
    """Append warehouse storage context (rack/bin occupancy) to the observation.

    Sourced from the env's ``topology`` plan (occupied bins / target bin) when
    available; zeros placeholder otherwise. Keeps pick / put-away policies aware
    of the logistic layout.
    """

    def __init__(self, env: gym.Env, n_bins: int = 8) -> None:
        super().__init__(env)
        self.n_bins = int(n_bins)
        self._extend_obs_space(np.zeros(self.n_bins), np.ones(self.n_bins))
        self.action_space = env.action_space

    def reset(self, *, seed=None, options=None):
        obs, info = self.env.reset(seed=seed, options=options)
        return self._augment_obs(obs, self._bin_state()), info

    def step(self, action: Sequence[float]):
        obs, reward, terminated, truncated, info = self.env.step(action)
        return self._augment_obs(obs, self._bin_state()), reward, terminated, truncated, info

    def _bin_state(self) -> np.ndarray:
        topo = getattr(self._simenv, "topology", None)
        if topo is not None:
            try:
                occ = np.asarray(getattr(topo, "bin_occupancy", []), dtype=float)
                if occ.size:
                    return np.pad(occ, (0, max(0, self.n_bins - occ.size)))[: self.n_bins]
            except Exception:
                pass
        return np.zeros(self.n_bins)


class DigitalTwinWrapper(_SimEnvWrapper):
    """Stamp every step with a digital-twin telemetry record.

    The record carries the robot type, joint state, and end-effector pose so the
    same episode can be replayed / mirrored into the real robot-control-stack
    device backend. Obs/action spaces are unchanged; the record lives in
    ``info["digital_twin"]``.

    If a ``sink`` (:class:`~rcs_env.envs.twin.DigitalTwinSink`) is provided, each
    step's record is also forwarded to the real backend transport automatically.
    """

    def __init__(
        self,
        env: gym.Env,
        history: int = 1,
        sink=None,
    ) -> None:
        super().__init__(env)
        self.history = max(1, int(history))
        self.sink = sink
        self._buf: deque = deque(maxlen=self.history)

    def reset(self, *, seed=None, options=None):
        obs, info = self.env.reset(seed=seed, options=options)
        self._buf.clear()
        info = dict(info)
        # Emit an initial telemetry record so consumers see state at t=0 too.
        record = self._build_record()
        self._buf.append(record)
        info["digital_twin"] = list(self._buf)
        if self.sink is not None:
            self.sink.push(info)
        return obs, info

    def _build_record(self) -> dict:
        engine = getattr(self._simenv, "engine", None)
        simenv = self._simenv
        robot_type = getattr(simenv, "config", None)
        rt = RobotType.ARM
        if robot_type is not None:
            rt = getattr(robot_type, "robot_type", RobotType.ARM)
        record = {
            "robot_type": rt.value if hasattr(rt, "value") else str(rt),
            "qpos": engine.qpos().tolist() if engine is not None else [],
            "ee_pose": None,
        }
        if engine is not None:
            try:
                ee = engine.forward_kinematics(engine.qpos())
                t = ee.translation
                q = ee.quaternion  # xyzw
                record["ee_pose"] = [t[0], t[1], t[2], q[3], q[0], q[1], q[2]]
            except Exception:
                pass
        return record

    def step(self, action: Sequence[float]):
        obs, reward, terminated, truncated, info = self.env.step(action)
        record = self._build_record()
        self._buf.append(record)
        info = dict(info)
        info["digital_twin"] = list(self._buf)
        if self.sink is not None:
            self.sink.push(info)
        return obs, reward, terminated, truncated, info


__all__ = [
    "GripperWrapper",
    "HandWrapper",
    "StorageWrapper",
    "DigitalTwinWrapper",
]
