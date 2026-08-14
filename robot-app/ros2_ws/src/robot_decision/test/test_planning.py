"""Tests for motion planners."""
from __future__ import annotations

from robot_decision.planning import (
    ForkliftMotionPlanner,
    DualArmOptimizer,
    BagTrajectoryGenerator,
)


def test_forklift_plan_insert_pallet():
    planner = ForkliftMotionPlanner()
    traj = planner.plan_insert_pallet(pallet_x=5.0, pallet_z=2.0, pallet_height=0.15)
    assert len(traj.waypoints) == 5
    assert traj.waypoints[-1].travel == 5.0
    assert traj.waypoints[-1].extend == 0.0


def test_forklift_plan_drop_pallet():
    planner = ForkliftMotionPlanner()
    traj = planner.plan_drop_pallet(drop_x=0.0, drop_z=0.0)
    assert len(traj.waypoints) == 4
    assert traj.waypoints[-1].lift == 0.0


def test_dual_arm_optimizer_syncs_joint_zero():
    opt = DualArmOptimizer(num_steps=20)
    traj = opt.optimize(left_target=[0.5, 0.0, 0.0, 0.0, 0.0, 0.0],
                        right_target=[0.3, 0.0, 0.0, 0.0, 0.0, 0.0])
    assert len(traj.left_arm) == 21
    for t_idx in range(len(traj.left_arm)):
        # after sync correction both arms should have same joint 0
        assert abs(traj.left_arm[t_idx][0] - traj.right_arm[t_idx][0]) < 1e-9


def test_bag_trajectory_generator_endpoints():
    gen = BagTrajectoryGenerator(num_steps=10)
    traj = gen.generate(start=(0, 0, 1), end=(2, 0, 1))
    assert traj.waypoints[0] == (0, 0, 1)
    assert abs(traj.waypoints[-1][0] - 2.0) < 0.1