"""Synthetic point cloud generator for warehouse simulation."""
from __future__ import annotations

import math
import random
import time
from typing import Any


class PointCloudGenerator:
    """Generates synthetic point cloud data from warehouse box positions.

    Simulates a depth-camera-style sensor that produces XYZ point clouds
    from the known positions of boxes in the warehouse scene.  Gaussian
    noise is added to mimic real sensor imperfections.
    """

    def __init__(
        self,
        *,
        resolution: float = 0.01,
        noise_std: float = 0.005,
        fov_h_deg: float = 60.0,
        fov_v_deg: float = 45.0,
        max_range: float = 5.0,
        publish_rate: float = 10.0,
    ) -> None:
        self.resolution = resolution
        self.noise_std = noise_std
        self.fov_h = math.radians(fov_h_deg)
        self.fov_v = math.radians(fov_v_deg)
        self.max_range = max_range
        self.publish_rate = publish_rate

    def generate(
        self,
        camera_pos: list[float],
        camera_yaw: float,
        boxes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate synthetic point cloud from box list.

        Args:
            camera_pos: ``[x, y, z]`` camera position in world frame.
            camera_yaw: Rotation around Z axis (radians). 0 = facing +X.
            boxes: List of ``{"id", "position": [x,y,z], "size": [sx,sy,sz]}``.

        Returns:
            Dict with keys ``frame_id``, ``timestamp``, ``points`` (list of
            ``[x, y, z]``), and ``ground_truth`` (visible box metadata).
        """
        cx, cy, cz = camera_pos
        cos_yaw = math.cos(camera_yaw)
        sin_yaw = math.sin(camera_yaw)
        half_h = self.fov_h / 2
        half_v = self.fov_v / 2

        points: list[list[float]] = []
        ground_truth: list[dict[str, Any]] = []

        for box in boxes:
            bx, by, bz = box["position"]
            sx, sy, sz = box["size"]

            # Transform box center to camera frame
            dx = bx - cx
            dy = by - cy
            dz = bz - cz
            local_x = dx * cos_yaw + dy * sin_yaw
            local_y = -dx * sin_yaw + dy * cos_yaw
            local_z = dz

            dist = math.sqrt(local_x**2 + local_y**2 + local_z**2)
            if dist > self.max_range or local_x <= 0:
                continue

            # Check if within FOV
            angle_h = math.atan2(abs(local_y), local_x)
            angle_v = math.atan2(abs(local_z), local_x)
            if angle_h > half_h or angle_v > half_v:
                continue

            # Box is visible — record ground truth
            ground_truth.append({
                "id": box["id"],
                "position": [bx, by, bz],
                "size": [sx, sy, sz],
            })

            # Sample points on the box face nearest to camera
            n_x = min(max(1, int(sx / self.resolution)), 30)
            n_y = min(max(1, int(sy / self.resolution)), 20)

            for ix in range(n_x):
                for iy in range(n_y):
                    px = bx - sx / 2 + sx * ix / max(n_x - 1, 1)
                    py = by - sy / 2 + sy * iy / max(n_y - 1, 1)
                    pz = bz
                    # Add Gaussian noise
                    px += random.gauss(0, self.noise_std)
                    py += random.gauss(0, self.noise_std)
                    pz += random.gauss(0, self.noise_std)
                    points.append([round(px, 4), round(py, 4), round(pz, 4)])

        return {
            "frame_id": "camera_link",
            "timestamp": time.time(),
            "points": points,
            "ground_truth": ground_truth,
        }
