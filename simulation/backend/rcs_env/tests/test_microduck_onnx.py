"""ONNX export/inference bridge tests for Microduck (P4 T5).

Requires ``onnxruntime`` + ``torch`` (pulled by stable-baselines3). Skipped when
either is missing so the base suite stays runnable on a minimal install.
"""
import numpy as np
import pytest

from rcs_env.envs.vec import make_sb3_vec_env
from rcs_env.onnx.microduck_onnx import MicroduckOnnxPolicy, export_microduck_onnx


def _have_onnx_stack():
    try:
        import onnxruntime  # noqa: F401
        import torch  # noqa: F401
        return True
    except ModuleNotFoundError:
        return False


@pytest.mark.skipif(not _have_onnx_stack(), reason="needs onnxruntime + torch")
def test_onnx_policy_matches_torch(tmp_path):
    from stable_baselines3 import PPO

    model = PPO(
        "MlpPolicy",
        make_sb3_vec_env("rcs/microduck-walk-v0", n_envs=1),
        device="cpu", n_steps=64, batch_size=32, learning_rate=3e-4,
    )
    model.learn(total_timesteps=256)

    path = tmp_path / "md.onnx"
    export_microduck_onnx(model, str(path))

    onnx_policy = MicroduckOnnxPolicy(str(path))
    obs = np.zeros(61, dtype=np.float32)
    torch_act, _ = model.predict(obs, deterministic=True)
    onnx_act = onnx_policy.predict(obs)
    assert torch_act.shape == onnx_act.shape
    assert np.allclose(torch_act, onnx_act, atol=1e-3)
