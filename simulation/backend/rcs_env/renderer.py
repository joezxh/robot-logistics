"""SimRenderer — offscreen 渲染器（基于官方 mujoco.Renderer）

提供 RGB/Depth 帧渲染能力：
* 使用官方 ``mujoco.Renderer``（GL 后端，单相机/多相机 RGB+Depth）
* 当 mujoco / OpenGL 不可用时返回零帧占位，保持 headless 兼容

替代旧版 ``rcs.sim.SimCameraSet`` 实现——不再依赖 C++ ``rcs`` 扩展，直接走
官方 ``mujoco`` Python 绑定，渲染回调在 ``render`` 时通过 ``Renderer.render``
驱动。
"""
from __future__ import annotations

from typing import Mapping

import numpy as np


class SimRenderer:
    """Offscreen 渲染器，封装官方 ``mujoco.Renderer``。

    Args:
        model: ``mujoco.MjModel`` 实例。
        data: ``mujoco.MjData`` 实例（可随仿真步进更新；render 时同步）。
        cameras: 相机配置 ``{name: (camera_name, frame_rate, width, height)}``。
            ``camera_name`` 为 MJCF 中的相机名（默认取首个可用相机）。
    """

    def __init__(
        self,
        model,
        data=None,
        cameras: Mapping[str, tuple] | None = None,
    ) -> None:
        self._model = model
        self._data = data
        self._cameras = cameras or {"default": ("default", 30, 320, 240)}
        self._renderer = None  # 延迟构建（需要 GL）
        self._width = 0
        self._height = 0
        self._cam_names = []
        for _name, (cam, _fr, w, h) in self._cameras.items():
            self._cam_names.append(cam)
            self._width = max(self._width, w)
            self._height = max(self._height, h)

    # ---- 构建 ---------------------------------------------------------------- #
    def _ensure_renderer(self) -> None:
        if self._renderer is not None:
            return
        if not self.available():
            raise RuntimeError("mujoco.Renderer unavailable (no GL backend)")
        import mujoco

        # 单相机渲染器：取第一个配置的相机
        cam = self._cam_names[0] if self._cam_names else None
        if cam in (None, "default"):
            cam = self._model.camera(0).name if self._model.ncam > 0 else None
        self._renderer = mujoco.Renderer(
            self._model,
            width=self._width or 320,
            height=self._height or 240,
        )
        self._active_cam = cam

    # ---- 渲染 ---------------------------------------------------------------- #
    def render(self) -> dict[str, np.ndarray]:
        """渲染当前帧，返回 ``{"rgb": HxWx3 uint8, "depth": HxWx1 float32}``。"""
        if not self.available():
            return self._zero_frames()
        self._ensure_renderer()
        if self._data is not None:
            self._renderer.update_scene(self._data, camera=self._active_cam)
        else:
            self._renderer.update_scene(self._model, camera=self._active_cam)
        rgb = self._renderer.render()
        depth = self._renderer.render_depth()
        if depth.ndim == 2:
            depth = depth[:, :, None]
        return {"rgb": np.asarray(rgb, dtype=np.uint8), "depth": np.asarray(depth, dtype=np.float32)}

    def render_all(self) -> Mapping[str, dict[str, np.ndarray]]:
        """渲染所有相机，返回 ``{name: {"rgb", "depth"}}``。"""
        if not self.available():
            return {name: self._zero_frames() for name in self._cameras}
        self._ensure_renderer()
        out: dict[str, dict[str, np.ndarray]] = {}
        for name, (cam, _fr, w, h) in self._cameras.items():
            if self._data is not None:
                self._renderer.update_scene(self._data, camera=cam)
            else:
                self._renderer.update_scene(self._model, camera=cam)
            rgb = self._renderer.render()
            depth = self._renderer.render_depth()
            if depth.ndim == 2:
                depth = depth[:, :, None]
            out[name] = {"rgb": np.asarray(rgb, dtype=np.uint8), "depth": np.asarray(depth, dtype=np.float32)}
        return out

    # ---- 占位 ---------------------------------------------------------------- #
    def _zero_frames(self) -> dict[str, np.ndarray]:
        w = self._width or 320
        h = self._height or 240
        return {
            "rgb": np.zeros((h, w, 3), dtype=np.uint8),
            "depth": np.zeros((h, w, 1), dtype=np.float32),
        }

    @staticmethod
    def available() -> bool:
        """检查官方 mujoco.Renderer 是否可用（导入级判断）。"""
        try:
            import mujoco  # noqa: F401
        except Exception:
            return False
        return True


__all__ = ["SimRenderer"]
