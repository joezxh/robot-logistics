from __future__ import annotations

import numpy as np


class RGBDPreprocessor:
    def __init__(self, depth_scale: float = 0.001, max_depth_m: float = 12.0) -> None:
        self.depth_scale = depth_scale
        self.max_depth_m = max_depth_m

    def process_depth(self, depth_raw: np.ndarray) -> np.ndarray:
        depth = np.asarray(depth_raw, dtype=float) * self.depth_scale
        depth[(depth <= 0.0) | (depth > self.max_depth_m)] = 0.0
        return depth


class PointCloudProcessor:
    def depth_to_pointcloud(
        self,
        depth: np.ndarray,
        fx: float,
        fy: float,
        cx: float,
        cy: float,
    ) -> np.ndarray:
        rows, columns = np.indices(depth.shape)
        valid = depth > 0.0
        z = depth[valid]
        x = (columns[valid] - cx) * z / fx
        y = (rows[valid] - cy) * z / fy
        return np.column_stack((x, y, z))

    def voxel_downsample(self, points: np.ndarray, voxel_size: float = 0.02) -> np.ndarray:
        if not len(points):
            return points
        cells = np.floor(points / voxel_size).astype(int)
        _, indices = np.unique(cells, axis=0, return_index=True)
        return points[np.sort(indices)]
