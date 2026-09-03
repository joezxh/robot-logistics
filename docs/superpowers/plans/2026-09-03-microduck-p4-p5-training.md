# Microduck Training Implementation Plan (P4 SB3 训练 + P5 ONNX 导入)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Microduck learnable inside robot-logic with SB3 PPO (P4), and make externally trained ONNX policies (e.g. from the upstream `microduck_rl` / mjlab pipeline) playable in the same environment (P5).

**Architecture:** P4 wraps the registered `rcs/microduck-walk-v0` env in `make_sb3_vec_env` and trains PPO, mirroring `rcs_env/training/example.py`. P5 adds an `OnnxPolicy` wrapper that enforces the `[1,61] → [1,14]` contract and can be plugged into either an evaluation rollout or the P3 SSE stream.

**Tech Stack:** Python 3.11, stable-baselines3 2.9.0, Gymnasium 1.3.0, NumPy, onnxruntime (installed in P5), pytest

### Prerequisites

- **P1 + P2 complete** (plan `2026-09-03-microduck-p1-p2-backend.md`): `rcs/microduck-walk-v0` registered, 61-dim obs / 14-dim action contract tested.
- **P3 not required** for P4/P5, but P5 Task 6 (browser playback) reuses the P3 SSE server.
- Environment:

```powershell
$env:PYTHONPATH = "d:/projects/robot-logic/simulation/backend"
Set-Location d:/projects/robot-logic/simulation/backend
$PY = "d:/projects/robot-logic/simulation/backend/rcs_sim_core/.venv/Scripts/python.exe"
```

### Expectation setting (from the approved spec §8)

- Biped locomotion RL is sensitive to parallel-environment count. SB3 PPO on CPU with a handful of envs will likely produce **standing/balancing** rather than a clean gait. This is expected; the ONNX track (P5) is the fallback for a high-quality gait.
- The MJCF uses plain `<position>` actuators while the upstream policy was trained with BAM voltage actuators + domain randomization, so an imported ONNX policy may walk degraded. P5 records this rather than silently hiding it.

---

## File Structure

| File | Responsibility |
|---|---|
| `simulation/backend/rcs_env/envs/microduck.py` | Add command sampling at reset (P4 prerequisite) |
| `simulation/backend/rcs_env/training/train_microduck.py` | **New** — PPO training + evaluation + model save |
| `simulation/backend/rcs_env/envs/microduck_policy.py` | **New** — `OnnxPolicy` wrapper enforcing the contract |
| `simulation/backend/rcs_env/serve/microduck_stream.py` | Add `--policy` flag for ONNX playback (P5) |
| `simulation/backend/rcs_env/tests/test_microduck.py` | Command sampling + ONNX contract tests |

---

### Task 1: Sample velocity commands at reset (P4 prerequisite)

**Why:** the command block is currently always zeros, so the reward only ever credits
tracking zero velocity — the policy would learn to stand still, never to walk.

**Files:**
- Modify: `simulation/backend/rcs_env/envs/microduck.py` (`__init__`, `reset`)
- Test: `simulation/backend/rcs_env/tests/test_microduck.py`

- [ ] **Step 1: Write the failing test**

```python
def test_reset_samples_a_nonzero_velocity_command():
    from rcs_env.envs.microduck import MicroduckEnv
    env = MicroduckEnv(variant="walk")
    seen = set()
    for seed in range(8):
        obs, _ = env.reset(seed=seed)
        seen.add(round(float(obs[48]), 4))          # cmd vx
    assert len(seen) > 1, "command vx is not being randomised"
    assert all(0.0 <= v <= 0.4 for v in seen), f"vx out of range: {seen}"


def test_command_block_keeps_13_slots():
    from rcs_env.envs.microduck import MicroduckEnv
    env = MicroduckEnv(variant="walk")
    obs, _ = env.reset(seed=1)
    assert obs[48:61].shape == (13,)
    # body x, y, yaw stay pinned to zero (spec 7.1)
    assert obs[55] == 0.0 and obs[56] == 0.0 and obs[60] == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v -k command`
Expected: FAIL — `vx is not being randomised`.

- [ ] **Step 3: Implement**

In `MicroduckEnv.__init__`, add command-range parameters after `action_scale`:

```python
        cmd_vx_range: tuple[float, float] = (0.0, 0.4),
        cmd_vy_range: tuple[float, float] = (-0.1, 0.1),
        cmd_vyaw_range: tuple[float, float] = (-0.3, 0.3),
```

store them:

```python
        self.cmd_vx_range = cmd_vx_range
        self.cmd_vy_range = cmd_vy_range
        self.cmd_vyaw_range = cmd_vyaw_range
```

In `reset()`, replace `self._command = np.zeros(13, dtype=float)` with a sampled command:

```python
        self._command = np.zeros(13, dtype=float)
        self._command[0] = self._rng.uniform(*self.cmd_vx_range)    # vx  (m/s)
        self._command[1] = self._rng.uniform(*self.cmd_vy_range)    # vy  (m/s)
        self._command[2] = self._rng.uniform(*self.cmd_vyaw_range)  # vyaw (rad/s)
```

(`self._rng` is reseeded from `seed` earlier in `reset`, so runs stay reproducible.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v`
Expected: PASS (full microduck suite, no regression).

- [ ] **Step 5: Commit**

```bash
git add rcs_env/envs/microduck.py rcs_env/tests/test_microduck.py
git commit -m "feat(microduck): sample velocity commands at reset (P4)"
```

---

### Task 2: PPO training script

**Files:**
- Create: `simulation/backend/rcs_env/training/train_microduck.py`

- [ ] **Step 1: Implement**

```python
"""PPO training for Microduck (P4).

Mirrors ``rcs_env.training.example`` but targets the locomotion task:

    PYTHONPATH=<repo>/simulation/backend \
      <venv>/python -m rcs_env.training.train_microduck \
      --variant walk --n-envs 4 --timesteps 200000
"""
from __future__ import annotations

import argparse

import numpy as np

from rcs_env.envs.vec import make_sb3_vec_env, random_rollout
from rcs_env.envs.twin import DigitalTwinSink, InMemoryTransport


def build_vec_env(variant: str, n_envs: int, seed: int = 0, sink=None):
    """SB3-native vector env for the Microduck locomotion task."""
    from rcs_env.envs.wrappers import DigitalTwinWrapper

    wrappers = [lambda e: DigitalTwinWrapper(e, sink=sink)]
    return make_sb3_vec_env(
        f"rcs/microduck-{variant}-v0",
        n_envs=n_envs,
        wrappers=wrappers,
        seed=seed,
    )


def train_ppo(vec_env, total_timesteps: int, seed: int = 0):
    from stable_baselines3 import PPO

    model = PPO(
        "MlpPolicy",
        vec_env,
        verbose=1,
        n_steps=512,
        batch_size=256,
        learning_rate=3e-4,
        gamma=0.99,
        gae_lambda=0.95,
        ent_coef=0.01,
        device="cpu",
        seed=seed,
    )
    model.learn(total_timesteps=total_timesteps)
    return model


def evaluate(model, vec_env, steps: int = 512) -> dict:
    out = vec_env.reset()
    obs = out[0] if isinstance(out, tuple) else out
    totals = None
    lengths = None
    for _ in range(steps):
        action, _ = model.predict(obs, deterministic=True)
        res = vec_env.step(action)
        if len(res) == 5:
            obs, reward, terminated, truncated, _ = res
        else:  # SB3 VecEnv: (obs, reward, done, info)
            obs, reward, done, _ = res
        reward = np.asarray(reward, dtype=float)
        totals = reward.copy() if totals is None else totals + reward
        lengths = np.zeros(vec_env.num_envs) if lengths is None else lengths + 1
    return {
        "mean_episode_return": float(np.mean(totals)),
        "mean_episode_length": float(np.mean(lengths)),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Microduck PPO training (P4)")
    ap.add_argument("--variant", default="walk")
    ap.add_argument("--n-envs", type=int, default=4)
    ap.add_argument("--steps", type=int, default=256, help="random baseline steps")
    ap.add_argument("--timesteps", type=int, default=200_000)
    ap.add_argument("--eval-steps", type=int, default=512)
    ap.add_argument("--out", default="microduck_ppo")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    transport = InMemoryTransport()
    sink = DigitalTwinSink(device_id="microduck-01", transport=transport, rate=0)

    vec_env = build_vec_env(args.variant, args.n_envs, seed=args.seed, sink=sink)
    print(f"[vec] {args.n_envs} x rcs/microduck-{args.variant}-v0 "
          f"obs={vec_env.observation_space.shape} act={vec_env.action_space.shape}")

    stats = random_rollout(vec_env, steps=args.steps)
    print(f"[random] mean_ep_return={stats['mean_episode_return']:.3f} "
          f"mean_ep_len={stats['mean_episode_length']:.1f}")

    model = train_ppo(vec_env, total_timesteps=args.timesteps, seed=args.seed)
    ev = evaluate(model, vec_env, steps=args.eval_steps)
    print(f"[ppo] mean_ep_return={ev['mean_episode_return']:.3f} "
          f"mean_ep_len={ev['mean_episode_length']:.1f}")

    path = f"{args.out}_{args.variant}"
    model.save(path)
    print(f"[save] {path}.zip")
    print(f"[twin] {len(transport)} telemetry records buffered in-memory")
    vec_env.close()
    print("[done]")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-run a short training**

Run:
```powershell
& $PY -m rcs_env.training.train_microduck --n-envs 2 --timesteps 2000 --eval-steps 128
```
Expected: prints `[vec] ... obs=(2, 61) act=(2, 14)`, trains 2000 steps, prints `[ppo]` stats and
saves `microduck_ppo_walk.zip`. No exceptions.

- [ ] **Step 3: Commit**

```bash
git add rcs_env/training/train_microduck.py
git commit -m "feat(microduck): PPO training script for locomotion (P4)"
```

---

### Task 3: Full training run + result record (P4 acceptance)

- [ ] **Step 1: Run the real training**

```powershell
& $PY -m rcs_env.training.train_microduck --n-envs 4 --timesteps 200000
```

- [ ] **Step 2: Record the outcome honestly**

Create `docs/microduck-training-notes.md` recording: env count, timesteps, wall time,
final mean episode return/length, and a qualitative verdict (stands / shuffles / walks).

```markdown
# Microduck P4 training notes

- Date / commit:
- Envs / timesteps / wall time:
- Final mean episode return / length:
- Verdict: <stands only | shuffles | walks>
- Reward weights & command ranges used:
```

This file must state the result even if the robot only stands — the spec §8 already
flags that CPU SB3 may not produce a clean gait.

- [ ] **Step 3: Commit**

```bash
git add docs/microduck-training-notes.md
git commit -m "docs(microduck): record P4 training outcome"
```

---

### Task 4: Install onnxruntime

- [ ] **Step 1: Install**

```powershell
& d:/projects/robot-logic/simulation/backend/rcs_sim_core/.venv/Scripts/python.exe `
  -m pip install onnxruntime -i https://pypi.tuna.tsinghua.edu.cn/simple
```

- [ ] **Step 2: Verify**

Run: `& $PY -c "import onnxruntime; print(onnxruntime.__version__)"`
Expected: prints a version (e.g. `1.x.y`).

- [ ] **Step 3: Commit the dependency**

```bash
git add simulation/backend/requirements.txt
git commit -m "chore(microduck): add onnxruntime for policy import (P5)"
```

(Add `onnxruntime` to `simulation/backend/requirements.txt`.)

---

### Task 5: `OnnxPolicy` wrapper

**Files:**
- Create: `simulation/backend/rcs_env/envs/microduck_policy.py`
- Test: `simulation/backend/rcs_env/tests/test_microduck.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_onnx_policy_rejects_wrong_io_shapes(tmp_path):
    """A model whose I/O is not [1,61]/[1,14] must be refused, not silently run."""
    import numpy as np
    import onnx
    from onnx import TensorProto, helper

    # minimal model with WRONG shapes (16 in / 3 out)
    inp = helper.make_tensor_value_info("obs", TensorProto.FLOAT, [1, 16])
    out = helper.make_tensor_value_info("act", TensorProto.FLOAT, [1, 3])
    node = helper.make_node("Identity", ["obs"], ["act"])
    graph = helper.make_graph([node], "bad", [inp], [out])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
    p = tmp_path / "bad.onnx"
    onnx.save(model, str(p))

    from rcs_env.envs.microduck_policy import OnnxPolicy
    import pytest
    with pytest.raises(ValueError, match="61"):
        OnnxPolicy(str(p))


def test_onnx_policy_accepts_correct_shapes_and_predicts(tmp_path):
    import numpy as np
    import onnx
    from onnx import TensorProto, helper

    inp = helper.make_tensor_value_info("obs", TensorProto.FLOAT, [1, 61])
    out = helper.make_tensor_value_info("act", TensorProto.FLOAT, [1, 14])
    node = helper.make_node("Identity", ["obs"], ["act"])
    graph = helper.make_graph([node], "ok", [inp], [out])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
    p = tmp_path / "ok.onnx"
    onnx.save(model, str(p))

    from rcs_env.envs.microduck_policy import OnnxPolicy
    pol = OnnxPolicy(str(p))
    assert pol.input_dim == 61 and pol.output_dim == 14
    action = pol.predict(np.zeros(61, dtype=np.float32))
    assert action.shape == (14,)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v -k onnx`
Expected: FAIL — `ModuleNotFoundError: rcs_env.envs.microduck_policy`.

- [ ] **Step 3: Implement**

```python
"""ONNX policy wrapper for Microduck (P5).

Enforces the deployment contract from
``docs/superpowers/specs/2026-09-03-microduck-design.md`` §7.4:
input ``[1, 61]``, output ``[1, 14]``, warm-up before the first control tick.

The upstream policy is trained with BAM voltage actuators + domain randomization
while the vendored MJCF uses plain ``<position>`` actuators, so an imported policy
may perform differently from upstream — this wrapper validates shape/type only and
does not hide that gap.
"""
from __future__ import annotations

import numpy as np

from .microduck_cfg import N_ACTION, N_OBS


class OnnxPolicy:
    """Thin inference wrapper over an ONNX walking policy."""

    def __init__(self, model_path: str) -> None:
        import onnxruntime as ort

        self.model_path = model_path
        self.session = ort.InferenceSession(
            model_path, providers=["CPUExecutionProvider"]
        )
        inputs = self.session.get_inputs()
        outputs = self.session.get_outputs()
        if len(inputs) != 1 or len(outputs) != 1:
            raise ValueError(
                f"{model_path}: expected exactly 1 input and 1 output, "
                f"got {len(inputs)}/{len(outputs)}"
            )
        in_shape = list(inputs[0].shape)
        out_shape = list(outputs[0].shape)
        if in_shape != [1, N_OBS]:
            raise ValueError(
                f"{model_path}: input shape must be [1, {N_OBS}] (got {in_shape}). "
                "The 61-dim layout is what lets policies be swapped."
            )
        if out_shape != [1, N_ACTION]:
            raise ValueError(
                f"{model_path}: output shape must be [1, {N_ACTION}] (got {out_shape})"
            )
        self.input_name = inputs[0].name
        self.input_dim = N_OBS
        self.output_dim = N_ACTION
        # Warm-up: keep the first-call latency out of the 20 ms control budget.
        self.predict(np.zeros(N_OBS, dtype=np.float32))

    def predict(self, obs: np.ndarray) -> np.ndarray:
        x = np.asarray(obs, dtype=np.float32).reshape(1, N_OBS)
        (y,) = self.session.run(None, {self.input_name: x})
        return np.asarray(y, dtype=np.float64).reshape(N_ACTION)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `& $PY -m pytest rcs_env/tests/test_microduck.py -v -k onnx`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add rcs_env/envs/microduck_policy.py rcs_env/tests/test_microduck.py
git commit -m "feat(microduck): OnnxPolicy wrapper enforcing 61/14 contract (P5)"
```

---

### Task 6: ONNX playback in the SSE stream (P5 acceptance)

**Files:**
- Modify: `simulation/backend/rcs_env/serve/microduck_stream.py`

- [ ] **Step 1: Add `--policy` support**

Replace the scripted-sinusoid block in `Handler.do_GET` with a policy-driven loop:

```python
        env, period = _make_env(self.variant, self.hz)
        policy = None
        if self.policy_path:
            from rcs_env.envs.microduck_policy import OnnxPolicy
            policy = OnnxPolicy(self.policy_path)

        try:
            obs, _ = env.reset(seed=0)
            while True:
                if policy is not None:
                    action = policy.predict(obs)
                else:
                    action = np.zeros(14, dtype=float)
                    action[0] = 0.3 * np.sin(time.time())
                obs, _reward, term, trunc, _info = env.step(action)
                if term or trunc:
                    obs, _ = env.reset()
                qpos = env.engine.qpos()
                payload = json.dumps({"qpos": [float(v) for v in qpos]})
                self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                self.wfile.flush()
                time.sleep(period)
        except (BrokenPipeError, ConnectionResetError):
            pass
```

Add the class attribute and CLI flag:

```python
class Handler(BaseHTTPRequestHandler):
    variant = "walk"
    hz = 50.0
    policy_path: str | None = None
```

```python
    ap.add_argument("--policy", default=None, help="path to an ONNX policy (skips the scripted motion)")
```

```python
    Handler.policy_path = args.policy
```

- [ ] **Step 2: Verify with the shape-checked dummy ONNX from Task 5**

Build the placeholder 61→14 ONNX (Task 5 test code) and run:

```powershell
& $PY -m rcs_env.serve.microduck_stream --port 8110 --policy <path-to-onnx>
```

Expected: server starts and streams 21-value `qpos` frames without raising.

- [ ] **Step 3: Browser check**

With the frontend running (`npm run dev`) and the **🦆 Microduck** tab open, click
**▶ 实时遥测**. The duck is driven by the ONNX policy. Note in
`docs/microduck-training-notes.md` whether the imported policy walks or falls.

- [ ] **Step 4: Commit**

```bash
git add rcs_env/serve/microduck_stream.py
git commit -m "feat(microduck): ONNX policy playback in SSE stream (P5)"
```

---

## Self-Review Notes

- **Spec coverage**: §5.5 reward (wired in P1–P2, command sampling added here), §5.7 domain randomization — **deliberately deferred**: with only a few CPU envs, aggressive DR hurts more than it helps. Revisit only if the P4 verdict is "walks".
- **Spec coverage**: §7.4 ONNX contract (T5), D1 SB3 training (T2/T3), D2 ONNX import + playback (T4/T5/T6), §9 P4/P5 acceptance (T3/T6).
- **Known gap**: `W_SLIP` (foot-slip penalty) is still defined but unwired — it needs contact detection, which requires a ground plane. Tracked: add a floor to the composed scene, then wire the penalty.
- **Known gap**: no SB3→ONNX export. The spec's ONNX track is explicitly about importing *external* (upstream/mjlab) policies, so exporting our own PPO model is out of scope for P5.
- **Type consistency**: `OnnxPolicy.predict` returns a 14-vector of float64, matching `MicroduckEnv.step`'s 14-dim action; `MicroduckEnv.step` accepts exactly 14 entries (validated in P2).
