"""Forklift motion planner: 3-joint coordinated trajectory."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Waypoint:
    travel: float
    lift: float
    extend: float
    time_s: float


@dataclass
class Trajectory:
    waypoints: list[Waypoint]


class ForkliftMotionPlanner:
    """Plans forklift trajectories with decoupled trapezoidal velocity profiles."""

    def __init__(self, v_max: float = 1.5, a_max: float = 2.0) -> None:
        self.v_max = v_max
        self.a_max = a_max

    def plan_insert_pallet(self, pallet_x: float, pallet_z: float, pallet_height: float = 0.15) -> Trajectory:
        """Plan to insert fork into a pallet at given position.

        Stages:
            1. Travel to pallet front (0.5m before pallet)
            2. Lift fork to pallet height
            3. Extend fork to pallet depth
            4. Lift pallet by 0.3m
            5. Retract fork
        """
        approach_x = pallet_x - 0.5
        return Trajectory([
            Waypoint(travel=approach_x, lift=0.0,            extend=0.0, time_s=0.0),
            Waypoint(travel=approach_x, lift=pallet_height,   extend=0.0, time_s=2.0),
            Waypoint(travel=pallet_x,    lift=pallet_height,  extend=0.4, time_s=4.0),
            Waypoint(travel=pallet_x,    lift=pallet_height + 0.3, extend=0.4, time_s=5.0),
            Waypoint(travel=pallet_x,    lift=pallet_height + 0.3, extend=0.0, time_s=6.0),
        ])

    def plan_drop_pallet(self, drop_x: float, drop_z: float) -> Trajectory:
        """Plan to drop pallet at destination."""
        return Trajectory([
            Waypoint(travel=drop_x, lift=0.5, extend=0.4, time_s=0.0),
            Waypoint(travel=drop_x, lift=0.1, extend=0.4, time_s=2.0),
            Waypoint(travel=drop_x, lift=0.1, extend=0.0, time_s=3.0),
            Waypoint(travel=drop_x, lift=0.0, extend=0.0, time_s=4.0),
        ])