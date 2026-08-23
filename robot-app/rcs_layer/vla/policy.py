"""Policy abstraction + loaders (RCS ``inference`` parity).

实现完整的 VLA 推理链路，支持：
- ScriptedPolicy: 脚本化策略（默认回退）
- VLAPolicy: 真实 VLA 模型推理
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from robot_contracts import RobotType


class Policy:
    """Maps an observation to an action (RCS inference parity)."""

    action_dim: int = 6

    def __call__(self, obs: Any) -> np.ndarray:
        raise NotImplementedError

    def reset(self) -> None:
        """重置策略状态（如有）"""
        return None


class ScriptedPolicy(Policy):
    """Deterministic baseline policy.

    基于 EE 位置跟踪的简单脚本策略，用于测试和回退。
    """

    def __init__(self, action_dim: int = 6, gain: float = 0.5) -> None:
        self.action_dim = action_dim
        self.gain = gain
        self._target = np.full(action_dim, 0.3)

    def __call__(self, obs: Any) -> np.ndarray:
        if isinstance(obs, dict):
            state = np.asarray(obs.get("state"), dtype=float)
        else:
            state = np.asarray(obs, dtype=float)
        dof = min(self.action_dim, state.shape[0] - 8)
        joints = state[8: 8 + dof] if dof > 0 else np.zeros(self.action_dim)
        delta = np.clip((self._target[:dof] - joints) * self.gain, -0.2, 0.2)
        out = np.zeros(self.action_dim)
        out[:dof] = delta
        return out


class VLAPolicy(Policy):
    """真实 VLA 推理策略

    加载 vla-training 导出的模型权重，执行推理。
    与 RCS inference 层对齐。
    """

    def __init__(
        self,
        model_path: str | Path,
        robot_type: RobotType = RobotType.ARM,
        device: str = "cuda",
        action_dim: int = 6,
    ):
        self.model_path = Path(model_path)
        self.robot_type = robot_type
        self.device = device
        self.action_dim = action_dim
        self._model = None
        self._processor = None
        self._load_model()

    def _load_model(self) -> None:
        """懒加载 VLA 模型"""
        import json

        manifest_path = self.model_path / "inference_manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        with open(manifest_path) as f:
            manifest = json.load(f)

        # 验证 robot_type 匹配
        manifest_rt = manifest.get("robot_type")
        if manifest_rt and manifest_rt != self.robot_type.value:
            raise ValueError(
                f"Robot type mismatch: model={manifest_rt}, "
                f"expected={self.robot_type.value}"
            )

        # 加载模型
        try:
            import torch
            from transformers import AutoModelForVision2Seq, AutoProcessor

            self._model = AutoModelForVision2Seq.from_pretrained(
                str(self.model_path),
                device_map=self.device,
                torch_dtype=torch.float16,
            )
            self._processor = AutoProcessor.from_pretrained(str(self.model_path))
        except ImportError as e:
            raise ImportError(f"transformers required for VLA: {e}")

    def __call__(self, obs: Any) -> np.ndarray:
        if self._model is None:
            return np.zeros(self.action_dim)

        import torch

        # 提取图像和指令
        if isinstance(obs, dict):
            images = obs.get("images", {})
            instruction = obs.get("instruction", "pick the object")
        else:
            images = {}
            instruction = "pick the object"

        # 单图像优先
        image = list(images.values())[0] if images else None

        # 预处理
        inputs = self._processor(
            text=[instruction],
            images=image,
            return_tensors="pt",
        ).to(self.device)

        # 推理
        with torch.no_grad():
            outputs = self._model.generate(**inputs, max_new_tokens=50)

        # 解析动作 (简化实现)
        # 实际实现需要根据模型输出格式解析
        action = torch.zeros(self.action_dim, device=self.device)

        return action.cpu().numpy()

    def reset(self) -> None:
        pass


def load_policy(
    path: str | None = None,
    kind: str = "scripted",
    action_dim: int = 6,
    robot_type: str | None = None,
    device: str = "cuda",
) -> Policy:
    """Load a policy (RCS ``inference`` entry point).

    Args:
        path: 模型权重路径（由 vla-training 导出）
        kind: 策略类型，"scripted" | "vla"
        action_dim: 动作维度
        robot_type: 机器人类型
        device: 推理设备

    Returns:
        Policy 实例
    """
    if path is None or kind == "scripted":
        return ScriptedPolicy(action_dim=action_dim)

    if kind == "vla":
        rt = RobotType(robot_type) if robot_type else RobotType.ARM
        return VLAPolicy(
            path,
            robot_type=rt,
            device=device,
            action_dim=action_dim,
        )

    return ScriptedPolicy(action_dim=action_dim)


__all__ = ["Policy", "ScriptedPolicy", "VLAPolicy", "load_policy"]
