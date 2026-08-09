"""Synthetic 2D laser scan generator for warehouse simulation."""
from __future__ import annotations

import math
import time
from typing import Any


class LaserScanGenerator:
    """Generates synthetic 2D laser scan data from warehouse obstacles.

    Simulates a planar LIDAR sensor that casts rays in a 2D arc and
    reports the distance to the nearest obstacle for each ray angle.
    """

    def __init__(
        self,
        *,
        angle_min: float = -math.pi / 2,
        angle_max: float = math.pi / 2,
        angle_increment: float = 0.01,
        range_min: float = 0.1,
        range_max: float = 10.0,
        publish_rate: float = 10.0,
    ) -> None:
        self.angle_min = angle_min
        self.angle_max = angle_max
        self.angle_increment = angle_increment
        self.range_min = range_min
        self.range_max = range_max
        self.publish_rate = publish_rate

    def generate(
        self,
        robot_pos: list[float],
        robot_yaw: float,
        walls: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate synthetic laser scan.

        Args:
            robot_pos: ``[x, y, z]`` robot position in world frame.
            robot_yaw: Robot heading (radians).
            walls: List of wall obstacles.  Each wall is
                ``{"type": "wall", "x": float, "y_min": float, "y_max": float}``
                representing an infinite-length vertical wall at the given X
                coordinate spanning ``y_min`` to ``y_max``.

        Returns:
            Dict with keys ``frame_id``, ``timestamp``, ``angle_min``,
            ``angle_max``, ``angle_increment``, ``ranges``, ``intensities``.
        """
        num_rays = int((self.angle_max - self.angle_min) / self.angle_increment) + 1
        ranges: list[float] = []
        intensities: list[float] = []

        rx, ry = robot_pos[0], robot_pos[1]

        for i in range(num_rays):
            angle = self.angle_min + i * self.angle_increment
            world_angle = robot_yaw + angle
            cos_a = math.cos(world_angle)
            sin_a = math.sin(world_angle)

            min_dist = self.range_max
            for wall in walls:
                if wall["type"] == "wall":
                    wx = wall["x"]
                    # Ray-wall intersection (vertical wall at x = wx)
                    if abs(cos_a) < 1e-9:
                        continue
                    t = (wx - rx) / cos_a
                    if t > 0:
                        hit_y = ry + t * sin_a
                        if wall["y_min"] <= hit_y <= wall["y_max"]:
                            min_dist = min(min_dist, t)

            clamped = max(self.range_min, min(min_dist, self.range_max))
            ranges.append(round(clamped, 4))
            intensities.append(100.0 if clamped < self.range_max else 10.0)

        return {
            "frame_id": "base_laser_link",
            "timestamp": time.time(),
            "angle_min": self.angle_min,
            "angle_max": self.angle_max,
            "angle_increment": self.angle_increment,
            "ranges": ranges,
            "intensities": [round(v, 1) for v in intensities],
        }
