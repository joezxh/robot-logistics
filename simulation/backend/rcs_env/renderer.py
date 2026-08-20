"""SimRenderer - MuJoCo offscreen 渲染器

提供 RGB/Depth 帧渲染能力，当 MuJoCo 不可用时返回零帧占位。
"""
from __future__ import annotations

from typing import Any

import numpy as np


class SimRenderer:
    """MuJoCo offscreen 渲染器

    当 MuJoCo 可用时提供真实 RGB/Depth 渲染，
    否则返回零帧占位以保持兼容性。
    """

    def __init__(
        self,
        mj_model,
        mj_data,
        camera_name: str = "default",
        width: int = 320,
        height: int = 240,
    ):
        self._model = mj_model
        self._data = mj_data
        self._camera_name = camera_name
        self._width = width
        self._height = height

    def render(self) -> dict[str, np.ndarray]:
        """渲染当前帧

        Returns:
            dict: {"rgb": HxWx3 uint8, "depth": HxWx1 float32}
        """
        if not self.available():
            return self._zero_frames()

        import mujoco

        # 查找相机 ID
        camera_id = self._get_camera_id()

        # 配置渲染上下文
        scene = mujoco.MjvScene(self._model, maxgeom=100)
        mujoco.mjv_updateScene(
            self._model, self._data, None, None, None,
            mujoco.MjvOption(), camera_id, mujoco.MjvCatOpt.mjCAT_ALL, scene
        )

        # offscreen 渲染
        rgb = np.zeros((self._height, self._width, 3), dtype=np.uint8)
        depth = np.zeros((self._height, self._width, 1), dtype=np.float32)

        ctx = mujoco.MjrContext(self._model, mujoco.mjtFontScale.mjFONTSCALE_150)

        viewport = mujoco.MjrRect(0, 0, self._width, self._height)
        mujoco.mjr_render(viewport, scene, ctx)
        mujoco.mjr_readPixels(rgb, depth, viewport, ctx)

        return {"rgb": rgb, "depth": depth}

    def _get_camera_id(self) -> int:
        """获取相机 ID"""
        if not self.available():
            return 0
        import mujoco
        camera_id = mujoco.mj_name2id(
            self._model, mujoco.mjtObj.mjOBJ_CAMERA, self._camera_name
        )
        return max(0, camera_id)

    def _zero_frames(self) -> dict[str, np.ndarray]:
        """返回零帧占位"""
        return {
            "rgb": np.zeros((self._height, self._width, 3), dtype=np.uint8),
            "depth": np.zeros((self._height, self._width, 1), dtype=np.float32),
        }

    @staticmethod
    def available() -> bool:
        """检查 MuJoCo 渲染是否可用"""
        try:
            import mujoco
            return hasattr(mujoco, "mjr_readPixels")
        except ImportError:
            return False


__all__ = ["SimRenderer"]
