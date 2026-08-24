"""Standard DH forward kinematics for a 6-DOF arm.

DH tuple order matches the implementation: (a, d, alpha, theta_offset).
`fk(q, dh)` adds `q[i] + theta_offset[i]` as the joint angle and uses
`a`, `d`, `alpha` for the link geometry.
"""
from __future__ import annotations
import numpy as np


def _dh_matrix(dh: tuple[float, float, float, float], theta: float) -> np.ndarray:
    a, d, alpha, _theta_offset = dh
    angle = theta + _theta_offset
    ct, st = np.cos(angle), np.sin(angle)
    ca, sa = np.cos(alpha), np.sin(alpha)
    return np.array([
        [ct, -st * ca,  st * sa, a * ct],
        [st,  ct * ca, -ct * sa, a * st],
        [0.0, sa,       ca,      d     ],
        [0.0, 0.0,      0.0,     1.0   ],
    ])


def fk(q: list[float], dh_params: list[tuple[float, float, float, float]]) -> np.ndarray:
    if len(q) != len(dh_params):
        raise ValueError(f"q length {len(q)} != dh length {len(dh_params)}")
    T = np.eye(4)
    for qi, dh in zip(q, dh_params):
        T = T @ _dh_matrix(dh, qi)
    return T
