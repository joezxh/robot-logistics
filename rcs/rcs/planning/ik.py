"""Numerical IK via damped least squares (no singularity avoidance).

Used for the prototype; production hardware (real UR5 etc.) would swap in
the vendor's analytical solver. The solver returns the first in-limits
solution; if none found within max_iter, raises NoSolution.
"""
from __future__ import annotations
import numpy as np

from .fk import fk


class NoSolution(Exception):
    pass


def _axis_angle(R_err: np.ndarray) -> np.ndarray:
    angle = np.arccos(max(-1.0, min(1.0, (np.trace(R_err) - 1.0) / 2.0)))
    if abs(angle) < 1e-9:
        return np.zeros(3)
    axis = np.array([
        R_err[2, 1] - R_err[1, 2],
        R_err[0, 2] - R_err[2, 0],
        R_err[1, 0] - R_err[0, 1],
    ])
    n = np.linalg.norm(axis)
    if n < 1e-12:
        return np.zeros(3)
    return axis / n * angle


def _geometric_jacobian(q: list[float], dh_params) -> np.ndarray:
    T = np.eye(4)
    origins = [T[:3, 3].copy()]
    z_axes = [T[:3, 2].copy()]
    for qi, dh in zip(q, dh_params):
        a, d, alpha, _theta = dh
        ct, st = np.cos(qi), np.sin(qi)
        ca, sa = np.cos(alpha), np.sin(alpha)
        Ti = np.array([
            [ct, -st * ca,  st * sa, a * ct],
            [st,  ct * ca, -ct * sa, a * st],
            [0.0, sa,       ca,      d     ],
            [0.0, 0.0,      0.0,     1.0   ],
        ])
        T = T @ Ti
        origins.append(T[:3, 3].copy())
        z_axes.append(T[:3, 2].copy())
    J = np.zeros((6, len(q)))
    for i in range(len(q)):
        z = z_axes[i]
        o = origins[i]
        J[:3, i] = np.cross(z, T[:3, 3] - o)
        J[3:, i] = z
    return J


def _clip(q: np.ndarray, lower, upper) -> np.ndarray:
    return np.minimum(np.maximum(q, lower), upper)


def ik(
    q_seed: list[float],
    dh_params,
    T_target: np.ndarray,
    lower: list[float],
    upper: list[float],
    max_iter: int = 200,
    tol: float = 1e-4,
) -> np.ndarray:
    q = np.array(q_seed, dtype=float)
    lb = np.array(lower, dtype=float)
    ub = np.array(upper, dtype=float)
    q = _clip(q, lb, ub)
    p_target = T_target[:3, 3]
    R_target = T_target[:3, :3]
    damping = 1e-4
    for _ in range(max_iter):
        T = fk(list(q), dh_params)
        pos_err = p_target - T[:3, 3]
        rot_err = _axis_angle(R_target @ T[:3, :3].T)
        err = np.concatenate([pos_err, rot_err])
        if np.linalg.norm(err) < tol:
            return q
        J = _geometric_jacobian(list(q), dh_params)
        JJt = J @ J.T + damping * np.eye(6)
        dq = J.T @ np.linalg.solve(JJt, err)
        q = _clip(q + dq, lb, ub)
    raise NoSolution("ik did not converge within max_iter")
