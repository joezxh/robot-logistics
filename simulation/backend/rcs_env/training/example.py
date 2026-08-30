"""Training example / smoke test for :mod:`rcs_env` (P3.3 / P3.4).

Demonstrates the full pipeline end to end:

1. ``make_vec_env`` — wrap N parallel ``rcs/fr3-reach-v0`` copies (optionally with
   P3.2 wrappers, optionally async via ``AsyncVectorEnv``) into a Gymnasium
   ``VectorEnv``.
2. ``random_rollout`` — uniform-random baseline to validate the vector pipeline.
3. ``train_ppo`` — train a real SB3 ``PPO`` policy on the reach task (SB3 is now a
   hard dependency of this example) and report mean episode return. A
   ``DigitalTwinSink`` is attached so the trained policy's telemetry is mirrored
   to the real RCS device backend (``robot/{device_id}/telemetry``) via MQTT.

Run:
    python -m rcs_env.training.example                 # random baseline + PPO
    python -m rcs_env.training.example --n-envs 4 --timesteps 20000
    python -m rcs_env.training.example --async          # multiprocess envs
    python -m rcs_env.training.example --mqtt --device-id fr3-01   # push to real backend
"""
from __future__ import annotations

import argparse

from rcs_env.envs.vec import make_sb3_vec_env, random_rollout
from rcs_env.envs.twin import DigitalTwinSink, InMemoryTransport
from rcs_env.envs.wrappers import DigitalTwinWrapper


def build_vec_env(
    n_envs: int,
    *,
    with_gripper: bool = False,
    async_: bool = False,
    sink=None,
):
    """Construct the training vector env for the FR3 reach task (SB3-native)."""
    wrappers = []
    if with_gripper:
        from rcs_env.envs.wrappers import GripperWrapper
        wrappers.append(GripperWrapper)
    # The digital-twin telemetry wrapper always attaches (sink may be None).
    wrappers.append(lambda e: DigitalTwinWrapper(e, sink=sink))
    return make_sb3_vec_env(
        "rcs/fr3-reach-v0", n_envs=n_envs, wrappers=wrappers, seed=0, async_=async_
    )


def train_ppo(vec_env, total_timesteps: int = 20_000):
    """Train a PPO policy with stable-baselines3 and return the model."""
    from stable_baselines3 import PPO

    model = PPO(
        "MlpPolicy",
        vec_env,
        verbose=1,
        n_steps=256,
        batch_size=128,
        learning_rate=3e-4,
        device="cpu",
    )
    model.learn(total_timesteps=total_timesteps)
    return model


def evaluate(model, vec_env, steps: int = 256) -> dict:
    """Greedy (deterministic) evaluation rollout of a trained policy."""
    out = vec_env.reset()
    obs = out[0] if isinstance(out, tuple) else out
    totals = None
    lengths = None
    for _ in range(steps):
        action, _ = model.predict(obs, deterministic=True)
        out = vec_env.step(action)
        if len(out) == 5:
            obs, reward, terminated, truncated, _ = out
        else:  # SB3 VecEnv: (obs, reward, done, info)
            obs, reward, done, _ = out
        import numpy as np
        reward = np.asarray(reward, dtype=float)
        totals = reward.copy() if totals is None else totals + reward
        lengths = np.zeros(vec_env.num_envs, dtype=float) if lengths is None else lengths + 1
    return {
        "mean_episode_return": float(np_mean(totals)),
        "mean_episode_length": float(np_mean(lengths)),
    }


def np_ones(vec_env):
    import numpy as np
    return np.zeros(vec_env.num_envs, dtype=float)


def np_mean(a):
    import numpy as np
    return np.mean(a) if a is not None else 0.0


def main() -> None:
    ap = argparse.ArgumentParser(description="rcs_env P3.3/P3.4 training example")
    ap.add_argument("--n-envs", type=int, default=2)
    ap.add_argument("--steps", type=int, default=256)
    ap.add_argument("--timesteps", type=int, default=20_000)
    ap.add_argument("--gripper", action="store_true")
    ap.add_argument("--async", dest="async_", action="store_true")
    ap.add_argument("--no-ppo", action="store_true")
    ap.add_argument("--mqtt", action="store_true", help="push telemetry to real RCS backend")
    ap.add_argument("--device-id", default="fr3-01")
    ap.add_argument("--broker", default="localhost")
    ap.add_argument("--contract-path", default=None,
                    help="path to canonical robot_contracts (root shared/python)")
    args = ap.parse_args()

    # Digital-twin sink: real MQTT backend, or in-memory for headless runs.
    if args.mqtt:
        from rcs_env.envs.twin import MqttTransport
        transport = MqttTransport(
            device_id=args.device_id, broker_host=args.broker,
            contract_path=args.contract_path,
        )
    else:
        transport = InMemoryTransport()
    sink = DigitalTwinSink(device_id=args.device_id, transport=transport, rate=0)

    vec_env = build_vec_env(
        args.n_envs, with_gripper=args.gripper, async_=args.async_, sink=sink
    )
    print(f"[vec] {args.n_envs} x rcs/fr3-reach-v0 "
          f"(async={args.async_})  obs={vec_env.observation_space.shape} "
          f"act={vec_env.action_space.shape}")

    stats = random_rollout(vec_env, steps=args.steps)
    print(f"[random] mean_ep_return={stats['mean_episode_return']:.3f} "
          f"mean_ep_len={stats['mean_episode_length']:.1f}")

    if not args.no_ppo:
        model = train_ppo(vec_env, total_timesteps=args.timesteps)
        ev = evaluate(model, vec_env, steps=args.steps)
        print(f"[ppo] mean_ep_return={ev['mean_episode_return']:.3f} "
              f"mean_ep_len={ev['mean_episode_length']:.1f}")

    if args.mqtt:
        transport.close()
    else:
        print(f"[twin] {len(transport)} telemetry records buffered in-memory")
    vec_env.close()
    print("[done]")


if __name__ == "__main__":
    main()
