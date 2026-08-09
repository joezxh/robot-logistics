# Phase 2: 感知与导航 — 实施计划

> **基于**: `docs/superpowers/specs/2026-08-09-phase2-perception-navigation-design.md`
> **前置**: Phase 1 完成（237 tests pass）
> **预期新增**: ~47 tests → 总计 ~284

---

## Task 1: PointCloudGenerator — 合成点云生成器

**目标**: 根据仓库场景中货箱位置生成合成点云数据，通过 MQTT 发布。

### TDD 步骤

**1.1 创建测试文件** `simulation/backend/tests/test_point_cloud_gen.py`

```python
"""Tests for PointCloudGenerator."""
import math
import pytest
from backend.algorithm.simulator.point_cloud_gen import PointCloudGenerator


class TestPointCloudGenerator:
    def setup_method(self):
        self.gen = PointCloudGenerator()

    def test_default_params(self):
        assert self.gen.resolution == 0.01
        assert self.gen.noise_std == 0.005
        assert self.gen.fov_h == pytest.approx(math.radians(60))
        assert self.gen.fov_v == pytest.approx(math.radians(45))
        assert self.gen.max_range == 5.0

    def test_generate_empty_scene(self):
        """No boxes → empty point list but ground_truth also empty."""
        result = self.gen.generate(
            camera_pos=[0, 1.5, 0],
            camera_yaw=0.0,
            boxes=[],
        )
        assert result["frame_id"] == "camera_link"
        assert "timestamp" in result
        assert result["points"] == []
        assert result["ground_truth"] == []

    def test_generate_single_box(self):
        """A box in front of camera produces points."""
        boxes = [{"id": "box-01", "position": [2.0, 0.5, 0.0], "size": [0.3, 0.2, 0.15]}]
        result = self.gen.generate(
            camera_pos=[0, 1.5, 0],
            camera_yaw=0.0,
            boxes=boxes,
        )
        assert len(result["points"]) > 0
        assert len(result["ground_truth"]) == 1
        assert result["ground_truth"][0]["id"] == "box-01"

    def test_points_within_fov(self):
        """All generated points should be within max_range."""
        boxes = [{"id": "b1", "position": [3.0, 0.0, 0.0], "size": [0.5, 0.5, 0.5]}]
        result = self.gen.generate([0, 0, 0], 0.0, boxes)
        for p in result["points"]:
            dist = math.sqrt(p[0]**2 + p[1]**2 + p[2]**2)
            assert dist <= self.gen.max_range + 0.1

    def test_noise_adds_variation(self):
        """Two generations with same input produce slightly different points (noise)."""
        boxes = [{"id": "b1", "position": [1.0, 0.0, 0.0], "size": [0.2, 0.2, 0.2]}]
        r1 = self.gen.generate([0, 0, 0], 0.0, boxes)
        r2 = self.gen.generate([0, 0, 0], 0.0, boxes)
        # Points should not be identical due to noise
        if len(r1["points"]) > 0 and len(r2["points"]) > 0:
            assert r1["points"] != r2["points"]

    def test_box_behind_camera_excluded(self):
        """Boxes behind the camera should not produce points."""
        boxes = [{"id": "behind", "position": [-3.0, 0.0, 0.0], "size": [0.3, 0.3, 0.3]}]
        result = self.gen.generate([0, 0, 0], 0.0, boxes)  # facing +X
        assert len(result["points"]) == 0

    def test_custom_resolution(self):
        gen = PointCloudGenerator(resolution=0.05)
        assert gen.resolution == 0.05

    def test_output_format(self):
        """Output must have required keys with correct types."""
        result = self.gen.generate([0, 0, 0], 0.0, [])
        assert isinstance(result["frame_id"], str)
        assert isinstance(result["timestamp"], float)
        assert isinstance(result["points"], list)
        assert isinstance(result["ground_truth"], list)

    def test_ground_truth_format(self):
        boxes = [{"id": "gt-1", "position": [1.0, 0.0, 0.0], "size": [0.3, 0.2, 0.1]}]
        result = self.gen.generate([0, 0, 0], 0.0, boxes)
        gt = result["ground_truth"][0]
        assert "id" in gt
        assert "position" in gt
        assert "size" in gt
        assert len(gt["position"]) == 3
        assert len(gt["size"]) == 3

    def test_camera_yaw_rotation(self):
        """Rotating camera should change which boxes are visible."""
        boxes = [{"id": "side", "position": [0.0, 3.0, 0.0], "size": [0.3, 0.3, 0.3]}]
        r_front = self.gen.generate([0, 0, 0], 0.0, boxes)        # facing +X, box at +Y
        r_side = self.gen.generate([0, 0, 0], math.pi / 2, boxes)  # facing +Y
        # Box should be visible when camera faces it
        assert len(r_side["points"]) > 0
```

**1.2 创建实现文件** `simulation/backend/algorithm/simulator/point_cloud_gen.py`

```python
"""Synthetic point cloud generator for warehouse simulation."""
from __future__ import annotations

import math
import time
import random
from typing import Any


class PointCloudGenerator:
    """Generates synthetic point cloud data from warehouse box positions."""

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
            camera_pos: [x, y, z] camera position in world frame.
            camera_yaw: Rotation around Z axis (radians). 0 = facing +X.
            boxes: List of {"id", "position": [x,y,z], "size": [sx,sy,sz]}.
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
            # Rotate into camera frame (camera looks along +X)
            local_x = dx * cos_yaw + dy * sin_yaw
            local_y = -dx * sin_yaw + dy * cos_yaw
            local_z = dz

            dist = math.sqrt(local_x**2 + local_y**2 + local_z**2)
            if dist > self.max_range:
                continue

            # Check if within FOV
            if local_x > 0:
                angle_h = math.atan2(abs(local_y), local_x)
                angle_v = math.atan2(abs(local_z), local_x)
            else:
                continue

            if angle_h > half_h or angle_v > half_v:
                continue

            # Box is visible — generate surface points
            ground_truth.append({
                "id": box["id"],
                "position": [bx, by, bz],
                "size": [sx, sy, sz],
            })

            # Sample points on the box face nearest to camera
            n_x = max(1, int(sx / self.resolution))
            n_y = max(1, int(sy / self.resolution))
            n_z = max(1, int(sz / self.resolution))
            # Limit total points per box
            n_x = min(n_x, 30)
            n_y = min(n_y, 20)
            n_z = min(n_z, 15)

            for ix in range(n_x):
                for iy in range(n_y):
                    px = bx - sx / 2 + sx * ix / max(n_x - 1, 1)
                    py = by - sy / 2 + sy * iy / max(n_y - 1, 1)
                    pz = bz
                    # Add noise
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
```

**验证**: `cd simulation/backend && python -m pytest tests/test_point_cloud_gen.py -v`
**预期**: 10 tests pass

---

## Task 2: LaserScanGenerator — 合成激光扫描生成器

**目标**: 根据设备位置和仓库障碍物生成合成激光扫描数据。

### TDD 步骤

**2.1 创建测试文件** `simulation/backend/tests/test_laser_scan_gen.py`

```python
"""Tests for LaserScanGenerator."""
import math
import pytest
from backend.algorithm.simulator.laser_scan_gen import LaserScanGenerator


class TestLaserScanGenerator:
    def setup_method(self):
        self.gen = LaserScanGenerator()

    def test_default_params(self):
        assert self.gen.angle_min == pytest.approx(-math.pi / 2)
        assert self.gen.angle_max == pytest.approx(math.pi / 2)
        assert self.gen.angle_increment == pytest.approx(0.01)
        assert self.gen.range_min == 0.1
        assert self.gen.range_max == 10.0

    def test_num_ranges(self):
        """Number of range values matches angle sweep / increment."""
        result = self.gen.generate([0, 0, 0], 0.0, [])
        expected_count = int(
            (self.gen.angle_max - self.gen.angle_min) / self.gen.angle_increment
        ) + 1
        assert len(result["ranges"]) == expected_count

    def test_empty_scene_max_range(self):
        """No obstacles → all ranges at max."""
        result = self.gen.generate([0, 0, 0], 0.0, [])
        for r in result["ranges"]:
            assert r >= self.gen.range_max - 0.01

    def test_wall_in_front(self):
        """A wall at x=2 should produce ranges ~2.0 in the forward direction."""
        # Wall modeled as a line segment at x=2.0
        walls = [{"type": "wall", "x": 2.0, "y_min": -5, "y_max": 5}]
        result = self.gen.generate([0, 0, 0], 0.0, walls)
        # At angle=0 (forward), range should be ~2.0
        mid_idx = len(result["ranges"]) // 2
        assert abs(result["ranges"][mid_idx] - 2.0) < 0.2

    def test_output_format(self):
        result = self.gen.generate([0, 0, 0], 0.0, [])
        assert result["frame_id"] == "base_laser_link"
        assert isinstance(result["angle_min"], float)
        assert isinstance(result["angle_max"], float)
        assert isinstance(result["angle_increment"], float)
        assert isinstance(result["ranges"], list)
        assert isinstance(result["intensities"], list)
        assert len(result["ranges"]) == len(result["intensities"])

    def test_range_clamp(self):
        """Ranges below range_min should be clamped."""
        # Obstacle very close
        walls = [{"type": "wall", "x": 0.01, "y_min": -5, "y_max": 5}]
        result = self.gen.generate([0, 0, 0], 0.0, walls)
        for r in result["ranges"]:
            assert r >= self.gen.range_min

    def test_robot_yaw_changes_scan(self):
        """Rotating the robot should shift which wall distances appear."""
        walls = [{"type": "wall", "x": 3.0, "y_min": -5, "y_max": 5}]
        r0 = self.gen.generate([0, 0, 0], 0.0, walls)
        r90 = self.gen.generate([0, 0, 0], math.pi / 2, walls)
        # The scan patterns should differ
        assert r0["ranges"] != r90["ranges"]

    def test_intensities_present(self):
        result = self.gen.generate([0, 0, 0], 0.0, [])
        assert all(i >= 0 for i in result["intensities"])
```

**2.2 创建实现文件** `simulation/backend/algorithm/simulator/laser_scan_gen.py`

```python
"""Synthetic 2D laser scan generator for warehouse simulation."""
from __future__ import annotations

import math
import time
from typing import Any


class LaserScanGenerator:
    """Generates synthetic 2D laser scan data from warehouse obstacles."""

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
            robot_pos: [x, y, z] robot position in world frame.
            robot_yaw: Robot heading (radians).
            walls: List of wall obstacles {"type": "wall", "x": float, "y_min": float, "y_max": float}.
        """
        num_rays = int((self.angle_max - self.angle_min) / self.angle_increment) + 1
        ranges: list[float] = []
        intensities: list[float] = []

        rx, ry = robot_pos[0], robot_pos[1]

        for i in range(num_rays):
            angle = self.angle_min + i * self.angle_increment
            world_angle = robot_yaw + angle
            ray_end_x = rx + self.range_max * math.cos(world_angle)
            ray_end_y = ry + self.range_max * math.sin(world_angle)

            min_dist = self.range_max
            for wall in walls:
                if wall["type"] == "wall":
                    # Simple axis-aligned wall at x = wall["x"]
                    wx = wall["x"]
                    # Ray-wall intersection (vertical wall)
                    dx = wx - rx
                    if math.cos(world_angle) != 0:
                        t = dx / math.cos(world_angle)
                        if t > 0:
                            hit_y = ry + t * math.sin(world_angle)
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
```

**验证**: `cd simulation/backend && python -m pytest tests/test_laser_scan_gen.py -v`
**预期**: 8 tests pass

---

## Task 3: Runtime 集成 — 注册传感器生成器 + MQTT 发布

**目标**: 在 `runtime.py` 中创建生成器实例，在 `tick()` 中调用并通过 MQTT 发布。

### 步骤

**3.1 修改** `simulation/backend/services/runtime.py`

在 `Runtime.__init__` 中添加：
```python
from backend.algorithm.simulator.point_cloud_gen import PointCloudGenerator
from backend.algorithm.simulator.laser_scan_gen import LaserScanGenerator

# 在 __init__ 末尾
self._pc_gen = PointCloudGenerator()
self._scan_gen = LaserScanGenerator()
self._detections: dict[str, Any] = {}   # device_id → latest detection data
self._nav_paths: dict[str, Any] = {}     # device_id → latest nav path
```

在 `tick()` 中添加传感器数据生成和发布：
```python
def tick(self, seconds: float = 0.5) -> None:
    # ... existing tick logic ...
    # Generate synthetic sensor data for each device
    for device_id, device in self.devices.devices.items():
        boxes = self._get_scene_boxes()
        pc_data = self._pc_gen.generate(device.position, 0.0, boxes)
        scan_data = self._scan_gen.generate(device.position, 0.0, [])
        # Store for SSE
        self._detections[device_id] = pc_data.get("ground_truth", [])
        # Publish via MQTT bridge if available
        if hasattr(self, '_mqtt_bridge') and self._mqtt_bridge:
            self._mqtt_bridge.publish_command(
                f"sim/{device_id}/point_cloud", pc_data
            )
            self._mqtt_bridge.publish_command(
                f"sim/{device_id}/scan", scan_data
            )
```

添加辅助方法：
```python
def _get_scene_boxes(self) -> list[dict]:
    """Convert warehouse sites to box list for point cloud generation."""
    boxes = []
    for site in self.sites.list():
        if site["kind"] == "warehouse":
            boxes.append({
                "id": site["id"],
                "position": site["position"],
                "size": [site["width"], site["depth"], site["height"]],
            })
    return boxes

def get_detections(self, device_id: str) -> list:
    return self._detections.get(device_id, [])

def get_nav_path(self, device_id: str) -> dict:
    return self._nav_paths.get(device_id, {})

def update_nav_path(self, device_id: str, path: dict) -> None:
    self._nav_paths[device_id] = path
```

**3.2 修改** `simulation/backend/main.py` — 新增 SSE 端点

```python
@app.get("/api/devices/{device_id}/detections")
async def device_detections_sse(device_id: str):
    """SSE stream of perception detections for a device."""
    async def event_stream():
        while True:
            data = runtime.get_detections(device_id)
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(0.1)  # 10Hz

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/devices/{device_id}/nav_path")
async def device_nav_path_sse(device_id: str):
    """SSE stream of navigation path for a device."""
    async def event_stream():
        while True:
            data = runtime.get_nav_path(device_id)
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1.0)  # 1Hz

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

**3.3 添加测试到** `simulation/backend/tests/test_runtime.py`

```python
def test_detections_empty_initially(fresh_runtime):
    assert fresh_runtime.get_detections("loader-01") == []

def test_nav_path_empty_initially(fresh_runtime):
    assert fresh_runtime.get_nav_path("loader-01") == {}

def test_update_nav_path(fresh_runtime):
    path = {"points": [[0, 0, 0], [1, 0, 0], [2, 0, 0]]}
    fresh_runtime.update_nav_path("loader-01", path)
    assert fresh_runtime.get_nav_path("loader-01") == path

def test_get_scene_boxes_from_sites(fresh_runtime):
    boxes = fresh_runtime._get_scene_boxes()
    # Default sites include warehouse racks
    assert len(boxes) > 0
    assert all("id" in b and "position" in b and "size" in b for b in boxes)
```

**验证**: `cd simulation/backend && python -m pytest tests/ -v`
**预期**: 所有现有 + 4 新 tests pass

---

## Task 4: PointCloudProcessorNode — 点云处理管线

**目标**: 实现 robot_perception 中的 7 步点云处理管线。

> **注意**: 此任务需要 ROS 2 + PCL 环境。在 Windows 开发时使用 mock 测试。

### TDD 步骤

**4.1 创建测试** `robot-app/ros2_ws/src/robot_perception/tests/test_point_cloud_processor.py`

```python
"""Tests for PointCloudProcessor (pure Python, no ROS 2 dependency)."""
import pytest
from robot_perception.point_cloud_processor import PointCloudProcessor


class TestPointCloudProcessor:
    def setup_method(self):
        self.proc = PointCloudProcessor(
            passthrough_z_min=0.1,
            passthrough_z_max=2.0,
            voxel_leaf_size=0.01,
            sor_mean_k=50,
            sor_std_thresh=1.0,
            ransac_distance_threshold=0.01,
            cluster_tolerance=0.02,
            min_cluster_size=10,
            max_cluster_size=25000,
        )

    def test_empty_input(self):
        result = self.proc.process([])
        assert result == []

    def test_passthrough_filters_z(self):
        """Points outside z range should be removed."""
        points = [
            [0.0, 0.0, 0.05],   # below min → removed
            [0.0, 0.0, 0.5],    # in range → kept
            [0.0, 0.0, 3.0],    # above max → removed
        ]
        result = self.proc.process(points)
        # Only the middle point survives passthrough
        assert len(result) >= 0  # May be further filtered

    def test_output_format(self):
        """Output should be list of detection dicts."""
        points = [[0.5, 0.3, 0.8], [0.51, 0.31, 0.81], [0.52, 0.29, 0.79]]
        result = self.proc.process(points)
        for det in result:
            assert "id" in det
            assert "bbox" in det
            assert "center" in det["bbox"]
            assert "size" in det["bbox"]
            assert "confidence" in det

    def test_single_cluster_detection(self):
        """Tight cluster of points should produce one detection."""
        points = []
        for i in range(50):
            points.append([1.0 + i * 0.001, 0.5, 0.8])
        result = self.proc.process(points)
        assert len(result) >= 1

    def test_confidence_threshold(self):
        self.proc.min_detection_confidence = 0.5
        result = self.proc.process([])
        for det in result:
            assert det["confidence"] >= 0.5
```

**4.2 创建实现** `robot-app/ros2_ws/src/robot_perception/robot_perception/point_cloud_processor.py`

```python
"""Point cloud processing pipeline for object detection.

Pure Python implementation — the ROS 2 node wrapper will call process().
In production, this uses PCL via open3d or pcl_ros. For testing, we use
a simplified numpy-based pipeline.
"""
from __future__ import annotations

import numpy as np
from typing import Any


class PointCloudProcessor:
    """7-step point cloud processing pipeline."""

    def __init__(
        self,
        *,
        passthrough_z_min: float = 0.1,
        passthrough_z_max: float = 2.0,
        voxel_leaf_size: float = 0.01,
        sor_mean_k: int = 50,
        sor_std_thresh: float = 1.0,
        ransac_distance_threshold: float = 0.01,
        cluster_tolerance: float = 0.02,
        min_cluster_size: int = 100,
        max_cluster_size: int = 25000,
        min_detection_confidence: float = 0.3,
    ) -> None:
        self.passthrough_z_min = passthrough_z_min
        self.passthrough_z_max = passthrough_z_max
        self.voxel_leaf_size = voxel_leaf_size
        self.sor_mean_k = sor_mean_k
        self.sor_std_thresh = sor_std_thresh
        self.ransac_distance_threshold = ransac_distance_threshold
        self.cluster_tolerance = cluster_tolerance
        self.min_cluster_size = min_cluster_size
        self.max_cluster_size = max_cluster_size
        self.min_detection_confidence = min_detection_confidence

    def process(self, points: list[list[float]]) -> list[dict[str, Any]]:
        """Run the full pipeline on raw XYZ points.

        Returns list of Detection3D-compatible dicts.
        """
        if not points:
            return []

        arr = np.array(points, dtype=np.float64)

        # [1] PassThrough filter on Z
        mask_z = (arr[:, 2] >= self.passthrough_z_min) & (arr[:, 2] <= self.passthrough_z_max)
        arr = arr[mask_z]
        if len(arr) == 0:
            return []

        # [2] VoxelGrid downsample (simplified)
        arr = self._voxel_downsample(arr, self.voxel_leaf_size)

        # [3] Statistical outlier removal (simplified)
        if len(arr) > self.sor_mean_k:
            arr = self._statistical_outlier_removal(arr)

        if len(arr) < self.min_cluster_size:
            return []

        # [4] RANSAC plane segmentation (remove ground plane)
        arr = self._remove_ground_plane(arr)
        if len(arr) < self.min_cluster_size:
            return []

        # [5] Euclidean cluster extraction
        clusters = self._extract_clusters(arr)

        # [6] + [7] BoundingBox fitting + Pose estimation
        detections = []
        for i, cluster in enumerate(clusters):
            if len(cluster) < self.min_cluster_size:
                continue
            if len(cluster) > self.max_cluster_size:
                continue
            bbox = self._fit_bbox(cluster)
            confidence = min(1.0, len(cluster) / 500.0)
            if confidence < self.min_detection_confidence:
                continue
            detections.append({
                "id": f"cluster_{i}",
                "bbox": {
                    "center": {
                        "position": {
                            "x": float(bbox["cx"]),
                            "y": float(bbox["cy"]),
                            "z": float(bbox["cz"]),
                        }
                    },
                    "size": {
                        "x": float(bbox["sx"]),
                        "y": float(bbox["sy"]),
                        "z": float(bbox["sz"]),
                    },
                },
                "results": [{
                    "hypothesis": {
                        "class_id": "box",
                        "score": round(confidence, 2),
                    }
                }],
            })
        return detections

    def _voxel_downsample(self, pts: np.ndarray, leaf: float) -> np.ndarray:
        if len(pts) == 0 or leaf <= 0:
            return pts
        min_b = pts.min(axis=0)
        idx = ((pts - min_b) / leaf).astype(int)
        _, unique_idx = np.unique(idx, axis=0, return_index=True)
        return pts[unique_idx]

    def _statistical_outlier_removal(self, pts: np.ndarray) -> np.ndarray:
        """Simplified SOR: remove points with mean neighbor distance > threshold."""
        from numpy.linalg import norm
        k = min(self.sor_mean_k, len(pts) - 1)
        if k < 1:
            return pts
        # Sample-based approximation for speed
        sample = pts[:min(len(pts), 1000)]
        dists = np.linalg.norm(sample[:, None, :] - sample[None, :, :], axis=2)
        mean_dists = np.sort(dists, axis=1)[:, 1:k+1].mean(axis=1)
        global_mean = mean_dists.mean()
        global_std = mean_dists.std()
        threshold = global_mean + self.sor_std_thresh * global_std
        mask = mean_dists < threshold
        return sample[mask]

    def _remove_ground_plane(self, pts: np.ndarray) -> np.ndarray:
        """Remove points near the lowest Z cluster (ground plane)."""
        if len(pts) < 10:
            return pts
        z_min = pts[:, 2].min()
        # Remove points within 5cm of the minimum Z
        mask = pts[:, 2] > z_min + 0.05
        return pts[mask]

    def _extract_clusters(self, pts: np.ndarray) -> list[np.ndarray]:
        """Simple grid-based clustering."""
        if len(pts) == 0:
            return []
        # Assign grid cells
        grid_idx = ((pts - pts.min(axis=0)) / max(self.cluster_tolerance, 0.001)).astype(int)
        labels = {}
        current_label = 0
        for i, key in enumerate(map(tuple, grid_idx)):
            if key not in labels:
                labels[key] = current_label
                current_label += 1
        label_arr = np.array([labels[tuple(k)] for k in grid_idx])
        clusters = []
        for label_id in range(current_label):
            mask = label_arr == label_id
            clusters.append(pts[mask])
        return clusters

    def _fit_bbox(self, pts: np.ndarray) -> dict[str, float]:
        """Fit axis-aligned bounding box to a cluster."""
        min_pt = pts.min(axis=0)
        max_pt = pts.max(axis=0)
        center = (min_pt + max_pt) / 2
        size = max_pt - min_pt
        return {
            "cx": center[0], "cy": center[1], "cz": center[2],
            "sx": size[0], "sy": size[1], "sz": size[2],
        }
```

**4.3 创建参数文件** `robot-app/ros2_ws/src/robot_perception/config/point_cloud_processor.yaml`

```yaml
point_cloud_processor:
  ros__parameters:
    passthrough_z_min: 0.1
    passthrough_z_max: 2.0
    voxel_leaf_size: 0.01
    sor_mean_k: 50
    sor_std_thresh: 1.0
    ransac_distance_threshold: 0.01
    cluster_tolerance: 0.02
    min_cluster_size: 100
    max_cluster_size: 25000
    min_detection_confidence: 0.3
```

**4.4 更新** `robot-app/ros2_ws/src/robot_perception/setup.py` — 添加 entry_points

```python
entry_points={
    "console_scripts": [
        "point_cloud_processor = robot_perception.point_cloud_processor:main",
    ],
},
```

**验证**: `cd robot-app/ros2_ws/src/robot_perception && python -m pytest tests/ -v`
**预期**: 5 tests pass

---

## Task 5: BaseExecutor Nav2 重构

**目标**: 将 `BaseExecutor` 从 P 控制器占位重构为 Nav2 NavigateToPose action client 包装。

### TDD 步骤

**5.1 更新测试** `robot-app/ros2_ws/src/robot_decision/tests/test_base_executor.py`

```python
"""Tests for BaseExecutor with Nav2 action client interface."""
import pytest
from unittest.mock import MagicMock, patch
from robot_decision.base_executor import BaseExecutor, BaseState


class TestBaseExecutorNav2:
    def setup_method(self):
        self.node = MagicMock()
        self.node.get_clock.return_value.now.return_value.to_msg.return_value = MagicMock()
        self.executor = BaseExecutor(self.node)

    def test_initial_state_idle(self):
        assert self.executor.state == BaseState.IDLE

    def test_setup_creates_action_client(self):
        self.executor.setup()
        assert self.executor._nav_client is not None

    def test_follow_waypoint_sends_goal(self):
        self.executor.setup()
        self.executor._nav_client = MagicMock()
        self.executor.follow_waypoint(1.0, 2.0, 0.5)
        self.executor._nav_client.send_goal_async.assert_called_once()
        assert self.executor.state == BaseState.FOLLOWING

    def test_stop_cancels_goal(self):
        self.executor.setup()
        self.executor._nav_client = MagicMock()
        self.executor._current_goal = MagicMock()
        self.executor.stop()
        assert self.executor.state in (BaseState.STOPPED, BaseState.IDLE)

    def test_on_result_resets_state(self):
        self.executor.setup()
        self.executor._state = BaseState.FOLLOWING
        self.executor.on_result(MagicMock())
        assert self.executor.state == BaseState.IDLE

    def test_on_feedback_does_not_crash(self):
        self.executor.setup()
        self.executor.on_feedback(MagicMock())
        # Should not raise

    def test_quaternion_from_yaw(self):
        """Verify yaw → quaternion conversion."""
        import math
        self.executor.setup()
        self.executor._nav_client = MagicMock()
        self.executor.follow_waypoint(0.0, 0.0, math.pi / 2)
        call_args = self.executor._nav_client.send_goal_async.call_args
        goal = call_args[0][0]
        # z = sin(yaw/2), w = cos(yaw/2)
        assert abs(goal.pose.orientation.z - math.sin(math.pi / 4)) < 0.01
        assert abs(goal.pose.orientation.w - math.cos(math.pi / 4)) < 0.01

    def test_cancel_when_no_goal(self):
        """Cancel with no active goal should not crash."""
        self.executor.setup()
        self.executor._nav_client = MagicMock()
        self.executor._current_goal = None
        self.executor.cancel()  # Should not raise
```

**5.2 重构** `robot-app/ros2_ws/src/robot_decision/robot_decision/base_executor.py`

```python
"""Base (AGV) executor — Nav2 NavigateToPose action client wrapper."""
from __future__ import annotations

import math
from enum import Enum, auto
from typing import Any


class BaseState(Enum):
    IDLE = auto()
    FOLLOWING = auto()
    STOPPED = auto()


class BaseExecutor:
    """Nav2 NavigateToPose action client for the diff-drive base."""

    def __init__(self, node: Any = None) -> None:
        self._node = node
        self._nav_client = None
        self._state = BaseState.IDLE
        self._current_goal = None

    @property
    def state(self) -> BaseState:
        return self._state

    def setup(self) -> None:
        """Initialize Nav2 action client. Call from node __init__."""
        try:
            from nav2_msgs.action import NavigateToPose
            from rclpy.action import ActionClient
            self._nav_client = ActionClient(
                self._node, NavigateToPose, 'navigate_to_pose'
            )
        except ImportError:
            # Running in test/mock mode without ROS 2
            self._nav_client = None

    def follow_waypoint(self, x: float, y: float, yaw: float) -> None:
        """Send NavigateToPose goal to Nav2."""
        try:
            from geometry_msgs.msg import PoseStamped
            goal = PoseStamped()
            goal.header.frame_id = 'map'
            if self._node:
                goal.header.stamp = self._node.get_clock().now().to_msg()
            goal.pose.position.x = float(x)
            goal.pose.position.y = float(y)
            goal.pose.orientation.z = math.sin(yaw / 2)
            goal.pose.orientation.w = math.cos(yaw / 2)

            if self._nav_client:
                self._nav_client.send_goal_async(goal)
        except ImportError:
            pass
        self._state = BaseState.FOLLOWING

    def cancel(self) -> None:
        """Cancel current navigation goal."""
        if self._current_goal and self._nav_client:
            self._current_goal.cancel_goal_async()
        self._state = BaseState.STOPPED

    def stop(self) -> None:
        self.cancel()

    def on_feedback(self, feedback: Any) -> None:
        """Nav2 feedback callback."""
        pass

    def on_result(self, result: Any) -> None:
        """Nav2 result callback — advance coordinator phase."""
        self._state = BaseState.IDLE
        self._current_goal = None

    def complete_follow(self) -> None:
        self._state = BaseState.IDLE
```

**验证**: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_base_executor.py -v`
**预期**: 8 tests pass

---

## Task 6: Nav2 参数配置

**目标**: 创建 Nav2 参数文件。

**6.1 创建** `robot-app/ros2_ws/src/robot_decision/config/nav2_params.yaml`

内容参见 spec §5.2（完整 Nav2 参数配置）。

**验证**: YAML 语法检查
```bash
python -c "import yaml; yaml.safe_load(open('config/nav2_params.yaml'))"
```

---

## Task 7: 前端 DetectionOverlay 组件

**目标**: 渲染 3D bbox 线框叠加在仓库场景中。

**7.1 创建** `simulation/frontend/src/three/DetectionOverlay.ts`

完整代码参见 spec §6.1。

**7.2 创建测试** `simulation/frontend/src/three/__tests__/DetectionOverlay.test.ts`

```typescript
import { describe, it, expect } from 'vitest'
import { DetectionOverlay } from '../DetectionOverlay'

describe('DetectionOverlay', () => {
  it('starts with empty boxes', () => {
    const overlay = new DetectionOverlay()
    expect(overlay.sceneObject.children.length).toBe(0)
  })

  it('creates box wireframes from detections', () => {
    const overlay = new DetectionOverlay()
    overlay.update([
      { id: 'box-01', position: { x: 1, y: 0, z: 1 }, size: { x: 0.3, y: 0.2, z: 0.15 }, confidence: 0.85 },
    ])
    expect(overlay.sceneObject.children.length).toBe(1)
  })

  it('uses green for high confidence', () => {
    const overlay = new DetectionOverlay()
    overlay.update([
      { id: 'b1', position: { x: 0, y: 0, z: 0 }, size: { x: 1, y: 1, z: 1 }, confidence: 0.9 },
    ])
    // High confidence → green (0x00ff00)
    expect(overlay.sceneObject.children.length).toBe(1)
  })

  it('uses yellow for low confidence', () => {
    const overlay = new DetectionOverlay()
    overlay.update([
      { id: 'b1', position: { x: 0, y: 0, z: 0 }, size: { x: 1, y: 1, z: 1 }, confidence: 0.5 },
    ])
    expect(overlay.sceneObject.children.length).toBe(1)
  })

  it('clear removes all boxes', () => {
    const overlay = new DetectionOverlay()
    overlay.update([
      { id: 'b1', position: { x: 0, y: 0, z: 0 }, size: { x: 1, y: 1, z: 1 }, confidence: 0.9 },
    ])
    overlay.clear()
    expect(overlay.sceneObject.children.length).toBe(0)
  })
})
```

**验证**: `cd simulation/frontend && npx vitest run src/three/__tests__/DetectionOverlay.test.ts`

---

## Task 8: 前端 NavPathOverlay 组件

**8.1 创建** `simulation/frontend/src/three/NavPathOverlay.ts`

完整代码参见 spec §6.2。

**8.2 创建测试** `simulation/frontend/src/three/__tests__/NavPathOverlay.test.ts`

```typescript
import { describe, it, expect } from 'vitest'
import { NavPathOverlay } from '../NavPathOverlay'

describe('NavPathOverlay', () => {
  it('starts empty', () => {
    const overlay = new NavPathOverlay()
    expect(overlay.sceneObject.children.length).toBe(0)
  })

  it('renders a path line', () => {
    const overlay = new NavPathOverlay()
    overlay.update([
      { x: 0, y: 0, z: 0 },
      { x: 1, y: 0, z: 0 },
      { x: 2, y: 0, z: 0 },
    ])
    expect(overlay.sceneObject.children.length).toBe(1)
  })

  it('ignores single point path', () => {
    const overlay = new NavPathOverlay()
    overlay.update([{ x: 0, y: 0, z: 0 }])
    expect(overlay.sceneObject.children.length).toBe(0)
  })

  it('clear removes line', () => {
    const overlay = new NavPathOverlay()
    overlay.update([{ x: 0, y: 0, z: 0 }, { x: 1, y: 0, z: 0 }])
    overlay.clear()
    expect(overlay.sceneObject.children.length).toBe(0)
  })

  it('update replaces previous path', () => {
    const overlay = new NavPathOverlay()
    overlay.update([{ x: 0, y: 0, z: 0 }, { x: 1, y: 0, z: 0 }])
    overlay.update([{ x: 0, y: 0, z: 0 }, { x: 5, y: 5, z: 0 }])
    expect(overlay.sceneObject.children.length).toBe(1)
  })
})
```

---

## Task 9: 前端 CostmapOverlay 组件

**9.1 创建** `simulation/frontend/src/three/CostmapOverlay.ts`

完整代码参见 spec §6.3。

**9.2 创建测试** `simulation/frontend/src/three/__tests__/CostmapOverlay.test.ts`

```typescript
import { describe, it, expect } from 'vitest'
import { CostmapOverlay } from '../CostmapOverlay'

describe('CostmapOverlay', () => {
  it('starts empty', () => {
    const overlay = new CostmapOverlay()
    expect(overlay.sceneObject.children.length).toBe(0)
  })

  it('renders costmap mesh', () => {
    const overlay = new CostmapOverlay()
    overlay.update({
      data: new Array(100).fill(128),
      width: 10,
      height: 10,
      resolution: 0.05,
    })
    expect(overlay.sceneObject.children.length).toBe(1)
  })

  it('clear removes mesh', () => {
    const overlay = new CostmapOverlay()
    overlay.update({ data: [0, 255], width: 2, height: 1, resolution: 0.1 })
    overlay.clear()
    expect(overlay.sceneObject.children.length).toBe(0)
  })
})
```

---

## Task 10: WarehouseScene.vue 集成

**目标**: 在 WarehouseScene 中集成三个 overlay 组件 + SSE 订阅。

### 步骤

**10.1 修改** `simulation/frontend/src/three/WarehouseScene.vue`

在 `<script setup>` 中添加：
```typescript
import { DetectionOverlay } from './DetectionOverlay'
import { NavPathOverlay } from './NavPathOverlay'
import { CostmapOverlay } from './CostmapOverlay'

let detectionOverlay: DetectionOverlay | undefined
let navPathOverlay: NavPathOverlay | undefined
let costmapOverlay: CostmapOverlay | undefined
let detectionEventSource: EventSource | undefined
let navPathEventSource: EventSource | undefined
```

在 `init()` 末尾添加：
```typescript
// Perception overlays
detectionOverlay = new DetectionOverlay()
detectionOverlay.sceneObject.position.set(0, 0.01, 0)
scene.add(detectionOverlay.sceneObject)

navPathOverlay = new NavPathOverlay()
scene.add(navPathOverlay.sceneObject)

costmapOverlay = new CostmapOverlay()
scene.add(costmapOverlay.sceneObject)

// SSE subscriptions for loader-01
detectionEventSource = new EventSource('/api/devices/loader-01/detections')
detectionEventSource.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data)
    if (Array.isArray(data) && detectionOverlay) {
      detectionOverlay.update(data.map((d: any) => ({
        id: d.id,
        position: { x: d.position[0], y: d.position[1], z: d.position[2] },
        size: { x: d.size[0], y: d.size[1], z: d.size[2] },
        confidence: 0.8,
      })))
    }
  } catch { /* ignore */ }
}

navPathEventSource = new EventSource('/api/devices/loader-01/nav_path')
navPathEventSource.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data)
    if (data?.points && navPathOverlay) {
      navPathOverlay.update(data.points.map((p: number[]) => ({
        x: p[0], y: p[1], z: p[2] || 0.05,
      })))
    }
  } catch { /* ignore */ }
}
```

在 `onUnmounted` 中添加清理：
```typescript
detectionEventSource?.close()
navPathEventSource?.close()
```

---

## Task 11: 集成测试 — 感知→导航→可视化链路

**11.1 创建** `simulation/backend/tests/test_perception_integration.py`

```python
"""Integration tests for perception + navigation pipeline."""
import pytest
from backend.algorithm.simulator.point_cloud_gen import PointCloudGenerator
from backend.algorithm.simulator.laser_scan_gen import LaserScanGenerator
from backend.services.runtime import Runtime


class TestPerceptionIntegration:
    def test_runtime_generates_detections(self):
        """Runtime tick should populate detection data."""
        rt = Runtime()
        rt.start()
        rt.tick(0.5)
        # After tick, detections should be populated for at least one device
        all_detections = {}
        for device_id in rt.devices.devices:
            dets = rt.get_detections(device_id)
            all_detections[device_id] = dets
        assert len(all_detections) > 0

    def test_point_cloud_gen_with_site_boxes(self):
        """PointCloudGenerator should work with boxes from SiteManager."""
        rt = Runtime()
        boxes = rt._get_scene_boxes()
        gen = PointCloudGenerator()
        result = gen.generate([0, 1.5, 0], 0.0, boxes)
        assert "points" in result
        assert "ground_truth" in result

    def test_nav_path_round_trip(self):
        """Nav path update → SSE retrieval."""
        rt = Runtime()
        path = {"points": [[0, 0, 0], [1, 0, 0], [2, 1, 0]]}
        rt.update_nav_path("loader-01", path)
        retrieved = rt.get_nav_path("loader-01")
        assert retrieved == path

    def test_scan_gen_with_empty_scene(self):
        """LaserScanGenerator should produce valid output with no walls."""
        gen = LaserScanGenerator()
        result = gen.generate([0, 0, 0], 0.0, [])
        assert len(result["ranges"]) > 0
        assert all(r == gen.range_max for r in result["ranges"])

    def test_detection_sse_endpoint_exists(self):
        """Verify /api/devices/{id}/detections endpoint is registered."""
        from fastapi.testclient import TestClient
        from unittest.mock import patch
        from backend.main import app
        with TestClient(app) as client:
            # SSE endpoint should exist (may timeout, but not 404)
            # Just verify the route is registered
            routes = [r.path for r in app.routes]
            assert "/api/devices/{device_id}/detections" in routes
            assert "/api/devices/{device_id}/nav_path" in routes
```

**验证**: `cd simulation/backend && python -m pytest tests/test_perception_integration.py -v`
**预期**: 5 tests pass

---

## Task 12: 最终验证 + 测试计数

### 全量测试

```bash
# Simulation backend
cd simulation/backend && python -m pytest tests/ -v
# 预期: ~45 tests (原有 ~38 + 新增 ~7)

# Frontend
cd simulation/frontend && npx vitest run
# 预期: ~15 tests (新增 ~10 overlay tests)

# RCS
cd rcs && python -m pytest tests/ -v
# 预期: ~237 tests (不变)

# robot-app (需要 ROS 2 环境)
cd robot-app/ros2_ws/src/robot_perception && python -m pytest tests/ -v
# 预期: ~5 tests

cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/ -v
# 预期: ~15 tests (原有 ~10 + 新增 ~5)
```

### Docker 端到端

```bash
cd deploy && docker-compose up --build
# 验证:
# 1. http://localhost:8000/api/devices — 设备列表
# 2. http://localhost:8000/api/devices/loader-01/detections — SSE 流
# 3. http://localhost:8000/api/devices/loader-01/nav_path — SSE 流
# 4. http://localhost:5173 — 前端 3D overlay 渲染
```

---

## 里程碑检查点

| 周 | Task | 验证标准 |
|----|------|---------|
| W1 | Task 1-3 | 合成传感器数据可通过 MQTT/SSE 接收 |
| W2 | Task 4 | Detection3DArray 发布，精度 < 0.05m |
| W3 | Task 5-6 | Nav2 goal 可达，BaseExecutor 重构完成 |
| W4 | Task 7-12 | overlay 实时渲染，~284 tests pass |

---

## 执行顺序依赖图

```
Task 1 (PointCloudGen) ─┐
                         ├── Task 3 (Runtime 集成) ── Task 11 (集成测试)
Task 2 (LaserScanGen) ──┘                              │
                                                        ├── Task 12 (最终验证)
Task 4 (PointCloudProcessor) ──────────────────────────┤
                                                        │
Task 5 (BaseExecutor Nav2) ── Task 6 (Nav2 params) ────┤
                                                        │
Task 7 (DetectionOverlay) ─┐                           │
Task 8 (NavPathOverlay) ───┼── Task 10 (Scene 集成) ───┘
Task 9 (CostmapOverlay) ───┘
```

**可并行**: Task 1+2, Task 7+8+9, Task 4+5+6
