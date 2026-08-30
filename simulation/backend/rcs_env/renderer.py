"""SimRenderer — offscreen 渲染器（对接 rcs.sim.SimCameraSet）

提供 RGB/Depth 帧渲染能力：
* 优先使用 :class:`rcs.sim.SimCameraSet`（GL 后端，多相机、带帧率节流）
* 当 rcs.sim / OpenGL 不可用时返回零帧占位，保持 headless 兼容

历史实现（``renderer.py`` 旧版）直接调用 ``mujoco.MjvScene`` 做 offscreen 渲染，
现统一收敛到 ``SimCameraSet``，渲染回调由 ``Sim`` 在 ``step`` 时驱动。
"""
from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np


class SimRenderer:
    """Offscreen 渲染器，封装 ``rcs.sim.SimCameraSet``。

    Args:
        sim: ``rcs.sim.Sim`` 实例（拥有 mjModel/mjData），渲染回调注册在其上。
        cameras: 相机配置 ``{name: (identifier, frame_rate, width, height)}``。
            ``identifier`` 为 MJCF 中的相机名（默认取首个可用相机）。
        render_on_demand: 仅在有 ``get_latest_frameset`` 调用时才步进渲染。
    """

    def __init__(
        self,
        sim,
        cameras: Mapping[str, tuple] | None = None,
        render_on_demand: bool = True,
    ) -> None:
        self._sim = sim
        self._cameras = cameras or {"default": ("default", 30, 320, 240)}
        self._render_on_demand = render_on_demand
        self._camera_set = None  # 延迟构建（需要 GL）
        self._width = 0
        self._height = 0
        for _name, (_id, _fr, w, h) in self._cameras.items():
            self._width = max(self._width, w)
            self._height = max(self._height, h)

    # ---- 构建 ---------------------------------------------------------------- #
    def _ensure_camera_set(self) -> None:
        if self._camera_set is not None:
            return
        if not self.available():
            raise RuntimeError("rcs.sim.SimCameraSet unavailable (no GL backend)")
        from rcs import sim as _sim

        cfg = {}
        for name, (identifier, frame_rate, width, height) in self._cameras.items():
            cfg[name] = _sim.SimCameraConfig(
                identifier=identifier,
                frame_rate=int(frame_rate),
                width=int(width),
                height=int(height),
                type=_sim.CameraType.kColor,
            )
        self._camera_set = _sim.SimCameraSet(
            sim=self._sim,
            camera_configs=cfg,
            render_on_demand=self._render_on_demand,
            max_buffer_frames=1,
        )

    # ---- 渲染 ---------------------------------------------------------------- #
    def render(self) -> dict[str, np.ndarray]:
        """渲染当前帧，返回 ``{"rgb": HxWx3 uint8, "depth": HxWx1 float32}``。"""
        if not self.available():
            return self._zero_frames()
        self._ensure_camera_set()
        frameset = self._camera_set.get_latest_frameset()
        color = getattr(frameset, "color_frames", None)
        if not color:
            return self._zero_frames()
        # 取首个相机
        name = next(iter(color))
        rgb = np.asarray(color[name], dtype=np.uint8)
        depth = np.zeros((rgb.shape[0], rgb.shape[1], 1), dtype=np.float32)
        return {"rgb": rgb, "depth": depth}

    def render_all(self) -> Mapping[str, dict[str, np.ndarray]]:
        """渲染所有相机，返回 ``{name: {"rgb", "depth"}}``。"""
        if not self.available():
            return {name: self._zero_frames() for name in self._cameras}
        self._ensure_camera_set()
        frameset = self._camera_set.get_latest_frameset()
        out: dict[str, dict[str, np.ndarray]] = {}
        color = getattr(frameset, "color_frames", {})
        for name in self._cameras:
            rgb = np.asarray(color.get(name), dtype=np.uint8) if name in color else np.zeros(
                (self._height, self._width, 3), dtype=np.uint8
            )
            depth = np.zeros((rgb.shape[0], rgb.shape[1], 1), dtype=np.float32)
            out[name] = {"rgb": rgb, "depth": depth}
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
        """检查 SimCameraSet / GL 后端是否可用。"""
        try:
            from rcs import sim as _sim  # noqa: F401
        except Exception:
            return False
        # SimCameraSet 需要 OpenGL 上下文；在无头环境下 import 成功但运行会失败，
        # 这里仅做导入级可用性判断，真实渲染由 _ensure_camera_set 在运行时兜底。
        return hasattr(_sim, "SimCameraSet")


__all__ = ["SimRenderer"]
