"""ONNX export + inference bridge for the Microduck PPO policy (P5).

Exports an SB3 ``MlpPolicy`` *deterministic* actor network to ONNX (obs in ->
actions out) and runs it with onnxruntime for low-latency CPU inference. The
digital-twin telemetry server (``rcs_env/serve/sse_qpos.py``) uses this to drive
the robot in real time from a trained policy without a torch runtime.
"""
from __future__ import annotations

import numpy as np


def export_microduck_onnx(model, path, opset: int = 13) -> str:
    """Export the *deterministic* policy actor network to ``path`` as ONNX.

    ``model`` is an SB3 ``BaseAlgorithm`` (e.g. ``PPO``). We export only the
    deterministic mean actor (``action_net`` of the latent), which is exactly
    what ``model.predict(obs, deterministic=True)`` returns for a Gaussian policy.
    Exporting the full ``policy.forward`` is avoided on purpose: SB3 builds a
    ``Normal`` distribution there, and torch 2.x's dynamo ONNX exporter cannot
    guard the resulting data-dependent shapes. The exported graph is a plain MLP,
    so it matches torch within float32 tolerance and loads cleanly in onnxruntime.
    """
    import torch

    policy = model.policy
    policy.eval()

    class _ActorMean(torch.nn.Module):
        def __init__(self, p):
            super().__init__()
            self.p = p

        def forward(self, obs):
            features = self.p.extract_features(obs)
            latent_pi, _ = self.p.mlp_extractor(features)
            return self.p.action_net(latent_pi)

    m = _ActorMean(policy)
    m.eval()
    device = policy.device
    obs_space = policy.observation_space
    dummy = torch.as_tensor(obs_space.sample()[None].astype(np.float32), device=device)
    torch.onnx.export(
        m,
        dummy,
        path,
        input_names=["obs"],
        output_names=["actions"],
        opset_version=opset,
    )
    return path


class MicroduckOnnxPolicy:
    """Minimal onnxruntime wrapper mirroring SB3 ``policy.predict(obs)``."""

    def __init__(self, path: str, providers=("CPUExecutionProvider",)):
        import onnxruntime as ort

        self.session = ort.InferenceSession(path, providers=list(providers))
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def predict(self, obs, deterministic: bool = True):
        obs = np.asarray(obs, dtype=np.float32)
        single = obs.ndim == 1
        if single:
            obs = obs[None]
        actions = self.session.run([self.output_name], {self.input_name: obs})[0]
        if single:
            actions = actions[0]
        return actions
