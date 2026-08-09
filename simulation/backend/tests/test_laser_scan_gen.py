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
        walls = [{"type": "wall", "x": 2.0, "y_min": -5, "y_max": 5}]
        result = self.gen.generate([0, 0, 0], 0.0, walls)
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
        walls = [{"type": "wall", "x": 0.01, "y_min": -5, "y_max": 5}]
        result = self.gen.generate([0, 0, 0], 0.0, walls)
        for r in result["ranges"]:
            assert r >= self.gen.range_min

    def test_robot_yaw_changes_scan(self):
        """Rotating the robot should shift which wall distances appear."""
        walls = [{"type": "wall", "x": 3.0, "y_min": -5, "y_max": 5}]
        r0 = self.gen.generate([0, 0, 0], 0.0, walls)
        r90 = self.gen.generate([0, 0, 0], math.pi / 2, walls)
        assert r0["ranges"] != r90["ranges"]

    def test_intensities_present(self):
        result = self.gen.generate([0, 0, 0], 0.0, [])
        assert all(i >= 0 for i in result["intensities"])
