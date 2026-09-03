"""Microduck PPO training + ONNX export entry point (P4 / P5).

Enough to train a locomotion policy end-to-end, evaluate a saved policy, and
export the actor network to ONNX for the digital-twin telemetry server.

Examples
--------
    # train (SB3 PPO, CPU)
    python -m rcs_env.training.train_microduck --total-timesteps 200000 \\
        --out models/microduck-walk-ppo.zip

    # resume
    python -m rcs_env.training.train_microduck --resume --out models/microduck-walk-ppo.zip

    # evaluate a saved policy
    python -m rcs_env.training.train_microduck --eval --policy models/microduck-walk-ppo.zip

    # export to ONNX (onnxruntime required)
    python -m rcs_env.training.train_microduck --export \\
        --policy models/microduck-walk-ppo.zip --out models/microduck-walk-ppo.onnx
"""
from __future__ import annotations

import argparse
import os

import numpy as np


def train(task_id, total_timesteps, out, resume=None, seed=0):
    from stable_baselines3 import PPO
    from stable_baselines3.common.callbacks import EvalCallback

    from rcs_env.envs.twin import DigitalTwinSink, InMemoryTransport
    from rcs_env.envs.vec import make_sb3_vec_env
    from rcs_env.envs.wrappers import DigitalTwinWrapper

    # Telemetry sink: every rollout step stamps a digital-twin record (P5 path).
    sink = DigitalTwinSink(device_id="microduck-01", transport=InMemoryTransport(), rate=0)
    wrapper = lambda e: DigitalTwinWrapper(e, sink=sink, history=1)

    vec = make_sb3_vec_env(task_id, n_envs=4, seed=seed, wrappers=[wrapper])
    if resume and os.path.exists(resume):
        model = PPO.load(resume, env=vec, device="cpu")
    else:
        model = PPO(
            "MlpPolicy", vec, device="cpu",
            n_steps=512, batch_size=128,
            learning_rate=3e-4, gamma=0.99, verbose=1,
        )
    eval_env = make_sb3_vec_env(task_id, n_envs=1, seed=seed + 1, wrappers=[wrapper])
    eval_cb = EvalCallback(
        eval_env, eval_freq=max(2000, total_timesteps // 20), n_eval_episodes=3,
        best_model_save_path=os.path.dirname(out) or ".",
        log_path=os.path.dirname(out) or ".",
    )
    model.learn(total_timesteps=total_timesteps, callback=eval_cb,
                reset_num_timesteps=resume is None)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    model.save(out)
    print(f"[train] saved -> {out}")
    return model


def evaluate(task_id, policy, max_steps=1000, seed=0, render=False):
    from rcs_env.training.microduck_rollout import random_rollout

    roll = random_rollout(
        task_id, n_envs=1, n_steps=max_steps, seed=seed, render=render, policy=policy,
    )
    ret = float(np.mean(roll["episode_returns"])) if roll["episode_returns"] else float(roll["mean_episode_return"])
    print(f"[eval] mean episode return: {ret:.3f} "
          f"({len(roll['episode_returns'])} episodes)")
    return ret


def export(policy, out):
    from rcs_env.onnx.microduck_onnx import export_microduck_onnx
    from stable_baselines3 import PPO

    if not policy.endswith(".zip"):
        raise SystemExit("--export requires a .zip SB3 policy as --policy")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    model = PPO.load(policy, device="cpu")
    export_microduck_onnx(model, out)
    print(f"[export] ONNX -> {out}")


def main():
    ap = argparse.ArgumentParser(description="Microduck PPO train/eval/export")
    ap.add_argument("--task", default="rcs/microduck-walk-v0")
    ap.add_argument("--out", default="models/microduck-walk-ppo.zip")
    ap.add_argument("--policy", default=None, help=".zip SB3 policy (resume/eval/export)")
    ap.add_argument("--total-timesteps", type=int, default=200_000)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--eval", action="store_true")
    ap.add_argument("--export", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if args.export:
        export(args.policy or args.out, args.out)
    elif args.eval:
        evaluate(args.task, args.policy or args.out)
    else:
        resume = args.out if args.resume else None
        train(args.task, args.total_timesteps, args.out, resume=resume, seed=args.seed)


if __name__ == "__main__":
    main()
