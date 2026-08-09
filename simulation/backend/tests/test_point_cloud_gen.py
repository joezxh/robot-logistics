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
            dist = math.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2)
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
        r_front = self.gen.generate([0, 0, 0], 0.0, boxes)  # facing +X, box at +Y
        r_side = self.gen.generate([0, 0, 0], math.pi / 2, boxes)  # facing +Y
        # Box should be visible when camera faces it
        assert len(r_side["points"]) > 0
