"""Random-policy rollout + digital-twin smoke test for Microduck (P2 / P5).

Adds a ``task_id``-friendly :func:`random_rollout` helper (random or SB3 policy)
and wires the digital-twin telemetry sink into the smoke-test so the P5 record
path is exercised on every run.
"""
from __future__ import annotations

import argparse

import numpy as np

from rcs_env.envs.twin import DigitalTwinSink, InMemoryTransport
from rcs_env.envs.vec import make_vec_env
from rcs_env.envs.wrappers import DigitalTwinWrapper


def random_rollout(task_id, n_envs=1, n_steps=200, seed=0, render=False,
                   policy=None, sink=None):
    """Run a uniform-random (or SB3 ``policy``) rollout and return episode stats.

    If ``sink`` is given, every sub-env is wrapped with :class:`DigitalTwinWrapper`
    so telemetry records are stamped into the sink during the rollout.
    """
    wrappers = [lambda e: DigitalTwinWrapper(e, sink=sink, history=1)] if sink is not None else None
    vec = make_vec_env(task_id, n_envs=n_envs, seed=seed, wrappers=wrappers)
    model = None
    if policy is not None:
        from stable_baselines3 import PPO
        model = PPO.load(policy, device="cpu")
    obs, _info = vec.reset(seed=seed)
    ep_ret = np.zeros(n_envs, dtype=float)
    returns: list[float] = []
    for _ in range(n_steps):
        if model is not None:
            action, _ = model.predict(obs, deterministic=True)
        else:
            action = vec.action_space.sample()
        obs, reward, term, trunc, _info = vec.step(action)
        reward = np.asarray(reward, dtype=float)
        ep_ret += reward
        done = np.logical_or(term, trunc)
        for k in np.where(done)[0]:
            returns.append(float(ep_ret[k]))
            ep_ret[k] = 0.0
    vec.close()
    mean_ret = float(np.mean(returns)) if returns else 0.0
    return {
        "mean_episode_return": mean_ret,
        "episode_returns": returns,
        "num_envs": n_envs,
        "steps": n_steps,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="walk")
    ap.add_argument("--n-envs", type=int, default=2)
    ap.add_argument("--steps", type=int, default=64)
    args = ap.parse_args()

    transport = InMemoryTransport()
    sink = DigitalTwinSink(device_id="microduck-01", transport=transport, rate=0)

    stats = random_rollout(
        f"rcs/microduck-{args.variant}-v0",
        n_envs=args.n_envs,
        n_steps=args.steps,
        seed=0,
        sink=sink,
    )
    print(f"[vec] {args.n_envs} x rcs/microduck-{args.variant}-v0")
    print(f"[random] mean_ep_return={stats['mean_episode_return']:.3f} "
          f"episodes={len(stats['episode_returns'])}")
    print(f"[twin] {len(transport)} telemetry records buffered in-memory")
    print("[done]")


if __name__ == "__main__":
    main()
