"""RobotType enum coverage tests (Microduck P1, Task 2)."""
from __future__ import annotations

from robot_contracts import RobotType


def test_robot_type_has_microduck():
    assert RobotType.MICRODUCK.value == "Microduck"
    assert "microduck" in [rt.value.lower() for rt in RobotType.get_all()]
