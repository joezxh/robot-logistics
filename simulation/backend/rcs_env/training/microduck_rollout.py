"""Random-policy rollout + digital-twin smoke test for Microduck (P2 acceptance)."""
from __future__ import annotations

import argparse

import numpy as np

from rcs_env.envs.twin import DigitalTwinSink, InMemoryTransport
from rcs_env.envs.vec import make_vec_env, random_rollout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="walk")
    ap.add_argument("--n-envs", type=int, default=2)
    ap.add_argument("--steps", type=int, default=64)
    args = ap.parse_args()

    transport = InMemoryTransport()
    sink = DigitalTwinSink(device_id="microduck-01", transport=transport, rate=0)

    vec_env = make_vec_env(
        f"rcs/microduck-{args.variant}-v0", n_envs=args.n_envs, seed=0
    )
    print(f"[vec] {args.n_envs} x rcs/microduck-{args.variant}-v0 "
          f"obs={vec_env.single_observation_space.shape} "
          f"act={vec_env.single_action_space.shape}")

    stats = random_rollout(vec_env, steps=args.steps)
    print(f"[random] mean_ep_return={stats['mean_episode_return']:.3f} "
          f"mean_ep_len={stats['mean_episode_length']:.1f}")

    print(f"[twin] {len(transport)} telemetry records buffered in-memory")
    vec_env.close()
    print("[done]")


if __name__ == "__main__":
    main()
