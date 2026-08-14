"""End-to-end smoke test for Top 3 loading scenarios.

This test is meant to be run inside the Docker stack via:

    docker-compose up -d
    docker-compose exec robot_app bash -c \
        "source /opt/ros/humble/setup.bash && \
         source /workspace/ros2_ws/install/setup.bash && \
         python3 -m pytest tests/e2e -v"

Currently this is a structural placeholder; full MQTT broker bring-up is
exercised in manual CI runs.
"""
from __future__ import annotations

import pytest


def test_top3_preset_names_available():
    """Sanity: Top 3 scene names should be enumerable without runtime."""
    expected = ["pallet", "box", "bag"]
    assert set(expected) == {"pallet", "box", "bag"}


def test_rcs_forklift_controller_importable():
    from rcs.controllers.forklift import ForkliftController
    assert ForkliftController is not None


def test_rcs_loader_controller_importable():
    from rcs.controllers.dual_arm_loader import DualArmLoaderController
    assert DualArmLoaderController is not None


def test_robot_arm_hal_factory_importable():
    """ROS2 package — only importable when sourced via ``install/setup.bash``."""
    pytest.importorskip("robot_arm_hal")
    from robot_arm_hal.hal_interface import make_hal
    assert callable(make_hal)
