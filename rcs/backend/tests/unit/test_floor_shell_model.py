"""Pydantic models for floor blueprint."""
from rcs_backend.models.floor_shell import (
    WallSegment, Zone, Facility, Dock, Corridor, Marking, FloorShell, Floor,
)


def test_wall_segment_full():
    wall = WallSegment(id="w1", x0=0, z0=0, x1=10, z1=0)
    assert wall.h == 3.5
    assert wall.kind == "wall"
    assert wall.length() == pytest.approx(10.0)


def test_zone_with_cold_chain_metadata():
    zone = Zone(
        id="z1", ref="A1", type="cold_zone",
        x=0, z=0, w=10, d=10,
        temperature_range={"min": 2, "max": 8},
        batch_tracking=True,
        current_load_pct=75.0,
    )
    assert zone.temperature_range.max == 8
    assert zone.batch_tracking is True
    assert zone.current_load_pct == 75.0


def test_floor_shell_minimal():
    shell = FloorShell(bounds={"w": 100.0, "d": 80.0})
    assert shell.walls == []
    assert shell.zones == []
    assert shell.bounds.w == 100.0


def test_floor_shell_with_multi_floor():
    f1 = Floor(id="L1", z=0, bounds={"w": 80, "d": 60})
    shell = FloorShell(bounds={"w": 80, "d": 60, "h": 12}, floors=[f1])
    assert len(shell.floors) == 1
    assert shell.floors[0].z == 0


def test_zone_type_v2_2_covers_scenarios():
    """v2.2 must accept all 23 zone types from spec §13.3.2."""
    from rcs_backend.models.floor_shell import ZONE_TYPES
    expected = {
        # E-commerce
        "flow_rack", "high_rack", "mezzanine", "automated", "temp", "temp_bagged", "returns",
        # Manufacturing
        "production_line", "wip_buffer", "parts_storage", "staging",
        # Cold-chain
        "cold_zone", "frozen_zone", "ambient_zone", "loading_bay",
        # Port
        "container_yard", "customs_area",
        # Reverse logistics
        "returns_received", "qc_staging", "reshelving", "disposal",
        # Multi-floor
        "floor_1", "floor_2", "floor_3", "elevator_shaft",
    }
    assert expected.issubset(ZONE_TYPES)


import pytest  # noqa: E402  (used in test_wall_segment_full)
