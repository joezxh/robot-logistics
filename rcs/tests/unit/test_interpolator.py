from rcs.planning.trajectory import plan_trapezoidal
from rcs.planning.interpolator import Interpolator


def test_interpolator_emits_step_count():
    traj = plan_trapezoidal([0.0], [1.0], [1.0], [2.0])
    it = Interpolator(traj, step_s=0.001)
    count = 0
    while not it.done:
        _ = it.next()
        count += 1
    expected = int(round(traj.duration_s / 0.001))
    assert abs(count - expected) <= 2


def test_interpolator_first_sample_matches_start():
    traj = plan_trapezoidal([0.0, 0.0], [1.0, -1.0], [1.0, 1.0], [2.0, 2.0])
    it = Interpolator(traj, step_s=0.001)
    s0 = it.next()
    assert abs(s0[0]) < 1e-9 and abs(s0[1]) < 1e-9


def test_interpolator_last_sample_matches_goal():
    traj = plan_trapezoidal([0.0, 0.0], [1.0, -1.0], [1.0, 1.0], [2.0, 2.0])
    it = Interpolator(traj, step_s=0.001)
    last = None
    while not it.done:
        last = it.next()
    assert last is not None
    assert abs(last[0] - 1.0) < 1e-3
    assert abs(last[1] + 1.0) < 1e-3
