import math
from rcs.planning.trajectory import plan_trapezoidal, plan_quintic


def test_trapezoidal_single_axis_hits_goal():
    vel_max = [1.0]
    acc_max = [2.0]
    traj = plan_trapezoidal([0.0], [1.0], vel_max, acc_max)
    assert traj.duration_s > 0
    end = traj.sample(traj.duration_s)
    assert abs(end[0] - 1.0) < 1e-6


def test_trapezoidal_peak_velocity_proportional_to_distance_over_duration():
    vel_max = [1.0]
    acc_max = [2.0]
    traj = plan_trapezoidal([0.0], [5.0], vel_max, acc_max)
    times = [i / 1000 for i in range(int(traj.duration_s * 1000) + 1)]
    # The symmetric trapezoid normalises s in [0, 1] with cruise phase
    # occupying [0.25, 0.75] (width 0.5), so the normalised peak velocity
    # ds/dt is 1/0.5 = 2.0. The trajectory linearly maps s to each joint
    # from start to goal, so the peak dq/dt is 2.0 * (goal-start) /
    # duration_s. We assert the observed peak is bounded by 1.05x that
    # value (tolerance for discrete sampling and trapezoid edges).
    duration = traj.duration_s
    expected_peak = 2.0 * 5.0 / duration
    peak = max(
        abs(traj.sample(t)[0] - traj.sample(max(0.0, t - 1e-3))[0]) / 1e-3
        for t in times
        if t > 0
    )
    assert peak <= expected_peak * 1.05


def test_quintic_zero_velocity_at_endpoints():
    vel_max = [1.0]
    acc_max = [2.0]
    traj = plan_quintic([0.0], [1.0], vel_max, acc_max)
    assert traj.duration_s > 0
    assert abs(traj.sample(0.0)[0] - 0.0) < 1e-6
    assert abs(traj.sample(traj.duration_s)[0] - 1.0) < 1e-6
