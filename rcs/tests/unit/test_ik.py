import math
import numpy as np
import pytest
from rcs.planning.fk import fk
from rcs.planning.ik import ik, NoSolution


# 6-DOF arm DH parameters in implementation order: (a, d, alpha, theta_offset).
# Matches the ARM_DH used in test_fk.py. See rcs.planning.fk for
# the parameter convention.
ARM_DH = [
    (0.0,  0.10,  math.pi / 2, 0.0),
    (0.3,  0.0,   0.0,         0.0),
    (0.2,  0.0,   math.pi / 2, 0.0),
    (0.0,  0.10, -math.pi / 2, 0.0),
    (0.0,  0.05,  math.pi / 2, 0.0),
    (0.0,  0.04,  0.0,         0.0),
]

LOWER = [-2*math.pi, -math.pi, -math.pi, -2*math.pi, -2*math.pi, -2*math.pi]
UPPER = [ 2*math.pi,  math.pi,  math.pi,  2*math.pi,  2*math.pi,  2*math.pi]


def test_ik_roundtrip_from_zero():
    q_seed = [0.0] * 6
    T = fk(q_seed, ARM_DH)
    q = ik(q_seed, ARM_DH, T, LOWER, UPPER)
    T2 = fk(list(q), ARM_DH)
    np.testing.assert_allclose(T2, T, atol=1e-4)


def test_ik_far_pose_no_solution():
    # Position 1000 m away is unreachable for the test arm (workspace ~0.5 m).
    T = np.eye(4)
    T[0, 3] = 1000.0
    with pytest.raises(NoSolution):
        ik([0.0] * 6, ARM_DH, T, LOWER, UPPER, max_iter=50)


def test_ik_respects_limits_when_solution_exists():
    # Pose reachable from zero pose with limits that exclude the seed.
    # The solver should still return a valid in-limits solution.
    q_seed = [0.0] * 6
    T = fk(q_seed, ARM_DH)
    q = ik(q_seed, ARM_DH, T, LOWER, UPPER)
    for qi, lo, hi in zip(q, LOWER, UPPER):
        assert lo - 1e-6 <= qi <= hi + 1e-6
