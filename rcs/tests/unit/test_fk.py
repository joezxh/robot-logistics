import math
import numpy as np
from rcs.planning.fk import fk


# DH parameters in implementation order: (a, d, alpha, theta_offset).
# a = link length along x_{i-1}; d = offset along x_{i-1}; alpha = twist
# about x_{i-1}; theta_offset = static joint angle (added to q at each step).
# These particular values are a 6-DOF arm used to exercise FK; they are
# not the canonical UR5 (whose DH parameters are sensitive to convention
# and out of scope for this prototype). The tests assert only the
# mathematical invariants the implementation is responsible for: 4x4
# homogeneous transforms, proper rotation matrices, and a non-degenerate
# chain that moves the end-effector.
ARM_DH = [
    (0.0,  0.10,  math.pi / 2, 0.0),
    (0.3,  0.0,   0.0,         0.0),
    (0.2,  0.0,   math.pi / 2, 0.0),
    (0.0,  0.10, -math.pi / 2, 0.0),
    (0.0,  0.05,  math.pi / 2, 0.0),
    (0.0,  0.04,  0.0,         0.0),
]


def test_fk_returns_4x4_homogeneous():
    q = [0.0] * 6
    T = fk(q, ARM_DH)
    assert T.shape == (4, 4)
    # Last row is (0, 0, 0, 1).
    np.testing.assert_allclose(T[3, :], [0.0, 0.0, 0.0, 1.0], atol=1e-12)


def test_fk_rotation_is_proper_orthogonal():
    q = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    T = fk(q, ARM_DH)
    R = T[:3, :3]
    np.testing.assert_allclose(R @ R.T, np.eye(3), atol=1e-9)
    np.testing.assert_allclose(np.linalg.det(R), 1.0, atol=1e-9)


def test_fk_nonzero_joint_changes_end_effector_position():
    T0 = fk([0.0] * 6, ARM_DH)
    T1 = fk([0.5, 0.0, 0.0, 0.0, 0.0, 0.0], ARM_DH)
    # Any joint movement should produce a measurable end-effector translation
    # (i.e. the kinematic chain is not degenerate).
    pos_diff = np.linalg.norm(T1[:3, 3] - T0[:3, 3])
    assert pos_diff > 1e-3
