"""VLA 推理引擎

支持两种策略：
- ScriptedPolicy：快速验证
- VLAPolicy：真实模型推理
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .policy import Policy, ScriptedPolicy


class VLAInferenceEngine:
    """VLA 推理引擎
    
    支持两种策略：
    - ScriptedPolicy：快速验证
    - VLAPolicy：真实模型推理
    """
    
    def __init__(
        self,
        model_path: str | Path | None = None,
        device: str = "cuda",
        action_dim: int = 6,
        robot_type: str = "ARM",
    ):
        self._policy = load_policy(
            path=str(model_path) if model_path else None,
            kind="vla" if model_path else "scripted",
            action_dim=action_dim,
            robot_type=robot_type,
            device=device,
        )
        
    def predict(self, obs: dict) -> np.ndarray:
        """从 observation 预测动作
        
        Args:
            obs: Gymnasium observation dict，包含：
                - state: 关节状态
                - rgb: RGB 图像（可选）
                - depth: 深度图像（可选）
                
        Returns:
            np.ndarray: 动作向量
        """
        return self._policy(obs)
        
    def reset(self) -> None:
        """重置策略状态"""
        self._policy.reset()
        
    def __call__(self, obs: dict) -> np.ndarray:
        return self.predict(obs)


def load_policy(
    path: str | None = None,
    kind: str = "scripted",
    **kwargs
) -> Policy:
    """策略加载工厂
    
    Args:
        path: 模型权重路径
        kind: 策略类型，"scripted" | "vla"
        **kwargs: 传递给策略的额外参数
        
    Returns:
        Policy 实例
    """
    if path is None or kind == "scripted":
        return ScriptedPolicy(
            action_dim=kwargs.get("action_dim", 6),
            gain=kwargs.get("gain", 0.5),
        )
    if kind == "vla":
        from .policy import VLAPolicy
        return VLAPolicy(
            path=path,
            robot_type=kwargs.get("robot_type", "ARM"),
            device=kwargs.get("device", "cuda"),
            action_dim=kwargs.get("action_dim", 6),
        )
    raise ValueError(f"unknown policy kind: {kind}")


__all__ = ["VLAInferenceEngine", "load_policy"]
