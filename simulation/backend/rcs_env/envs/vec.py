"""Vectorized env factory for :mod:`rcs_env` (P3.3 / P3.4).

Gymnasium ships ``gymnasium.vector`` (``SyncVectorEnv`` / ``AsyncVectorEnv``) so
we do **not** depend on ``stable-baselines3`` for vectorization. This module
provides a single convenience factory :func:`make_vec_env` that mirrors the
RCS ``rcs.envs.make_vec_env`` surface: it builds ``n_envs`` copies of a task,
optionally stacks the P3.2 wrappers onto each copy, and returns a Gymnasium
vector env ready for rollouts / SB3 consumption.

Multiprocessing note (P3.4)
---------------------------
``AsyncVectorEnv`` spawns worker *processes*. The underlying ``rcs.sim.Sim`` is a
C++/MuJoCo object that does **not** pickle, so the sub-env factory must be
reproducible from a *picklable spec* (task id + wrapper classes + seed), and each
worker builds its own fresh ``Sim``. :class:`_EnvFactory` is a module-level,
picklable callable holding only that spec — it never closes over a live Sim.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import gymnasium as gym
import numpy as np

from .base import make_env, register_envs


@dataclass
class _EnvFactory:
    """Picklable sub-env factory for vector envs.

    Holds only a task string, a list of wrapper *classes*, and an integer seed —
    all picklable — and builds a brand-new env (with its own Sim) on each call.
    """

    task_id: str
    wrappers: tuple = ()
    seed: int | None = None

    def __call__(self) -> gym.Env:
        env = make_env(self.task_id)
        for W in self.wrappers:
            env = W(env)
        if self.seed is not None:
            env.reset(seed=self.seed)
        return env


def make_vec_env(
    task_id: str,
    n_envs: int = 1,
    *,
    wrappers: Sequence[Callable[[gym.Env], gym.Env]] | None = None,
    seed: int | None = None,
    async_: bool = False,
) -> gym.vector.VectorEnv:
    """Create a vectorized env with ``n_envs`` parallel copies of ``task_id``.

    Args:
        task_id: a registered ``rcs/...`` id (see :func:`register_envs`).
        n_envs: number of parallel environments.
        wrappers: optional sequence of wrapper *classes/factories* applied (in
            order) to every sub-env, e.g. ``[GripperWrapper, HandWrapper]``.
        seed: base seed; sub-env ``i`` is seeded with ``seed + i``.
        async_: if True, use ``AsyncVectorEnv`` (multiprocess). Each worker builds
            its own Sim from ``task_id`` — nothing unpicklable crosses the boundary.

    Returns:
        A Gymnasium ``VectorEnv`` with batched obs/action spaces.
    """
    register_envs()
    wrappers = tuple(wrappers or ())
    factories = [
        _EnvFactory(task_id=task_id, wrappers=wrappers, seed=(seed + i) if seed is not None else None)
        for i in range(n_envs)
    ]
    if async_:
        return gym.vector.AsyncVectorEnv(factories)
    return gym.vector.SyncVectorEnv(factories)


def random_rollout(
    vec_env: gym.vector.VectorEnv,
    steps: int = 256,
    *,
    render: bool = False,
) -> dict:
    """Run a uniform-random policy for ``steps`` and return aggregate stats.

    Useful as a smoke test for vectorized training pipelines and as a baseline
    before plugging in an RL algorithm.
    """
    out = vec_env.reset()
    obs = out[0] if isinstance(out, tuple) else out
    ep_ret = np.zeros(vec_env.num_envs, dtype=float)
    ep_len = np.zeros(vec_env.num_envs, dtype=int)
    totals = np.zeros(vec_env.num_envs, dtype=float)
    lengths = np.zeros(vec_env.num_envs, dtype=int)

    for _ in range(steps):
        action = np.asarray(vec_env.action_space.sample(), dtype=float)
        out = vec_env.step(action)
        if len(out) == 5:
            obs, reward, terminated, truncated, _info = out
            done = np.logical_or(terminated, truncated)
        else:  # SB3 VecEnv: (obs, reward, done, info)
            obs, reward, done, _info = out
        reward = np.asarray(reward, dtype=float)
        totals += reward
        lengths += 1
        ep_ret += reward
        ep_len += 1
        for k in np.where(done)[0]:
            totals[k] = ep_ret[k]
            lengths[k] = ep_len[k]
            ep_ret[k] = 0.0
            ep_len[k] = 0
        if render and hasattr(vec_env, "render"):
            vec_env.render()

    return {
        "mean_episode_return": float(np.mean(totals)) if vec_env.num_envs else 0.0,
        "mean_episode_length": float(np.mean(lengths)) if vec_env.num_envs else 0.0,
        "num_envs": vec_env.num_envs,
        "steps": steps,
    }


def make_sb3_vec_env(
    task_id: str,
    n_envs: int = 1,
    *,
    wrappers: Sequence[Callable[[gym.Env], gym.Env]] | None = None,
    seed: int | None = None,
    async_: bool = False,
):
    """SB3-native vector env (``DummyVecEnv`` / ``SubprocVecEnv``).

    stable-baselines3 rejects a raw ``gymnasium.vector.VectorEnv`` (its env-patch
    expects an OpenAI-Gym-derived env). This factory builds the SB3 vector env
    from the same picklable :class:`_EnvFactory` spec, so it is accepted by
    ``PPO``/``SAC`` directly. Use this for RL training; use :func:`make_vec_env`
    for generic Gymnasium vectorization.
    """
    from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv

    wrappers = tuple(wrappers or ())
    env_fns = [
        _EnvFactory(
            task_id=task_id,
            wrappers=wrappers,
            seed=(seed + i) if seed is not None else None,
        )
        for i in range(n_envs)
    ]
    if async_:
        return SubprocVecEnv(env_fns)
    return DummyVecEnv(env_fns)


__all__ = ["make_vec_env", "random_rollout", "make_sb3_vec_env", "_EnvFactory"]
