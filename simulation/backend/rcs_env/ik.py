"""MjIK — pure-Python damped-least-squares (DLS) inverse kinematics for MuJoCo.

Drop-in replacement for the C++ ``rcs.sim.SimRobot.get_ik()`` / ``MjIK`` solver,
implemented directly on top of the official ``mujoco`` package. It uses the site
Jacobian (``mj_jacSite``) and the same DLS update the native solver used:

    q_{k+1} = q_k + J^+ (x_des - x_k),   J^+ = J^T (J J^T + lambda^2 I)^{-1}

A small ``lambda`` (damping) keeps the update well-conditioned near singularities.
TCP error is measured in SE(3): 3D position + rotation (axis-angle from the
orientation residual).

This module has **no ``rcs`` / C++-core dependency** — only ``mujoco`` + numpy.
"""
from __future__ import annotations

import numpy as np


class MjIK:
    """Damped-least-squares IK solver bound to a MuJoCo model/data."""

    def __init__(
        self,
        model,
        data,
        tcp_site: str = "tcp",
        pos_tol: float = 1e-3,
        rot_tol: float = 1e-3,
        max_iters: int = 200,
        damping: float = 0.02,
    ) -> None:
        self._mj = __import__("mujoco")
        self._model = model
        self._data = data
        self._tcp_site = tcp_site
        self._pos_tol = pos_tol
        self._rot_tol = rot_tol
        self._max_iters = max_iters
        self._damping = damping
        self._site_id = self._mj.mj_name2id(
            model, self._mj.mjtObj.mjOBJ_SITE, tcp_site
        )
        # actuated joint ids (arm joints driven by JOINT actuators)
        self._arm_jids = self._actuated_joint_ids(model)

    # ------------------------------------------------------------------ #
    @staticmethod
    def _actuated_joint_ids(model) -> list[int]:
        jids = []
        for a in range(model.nu):
            if int(model.actuator_trntype[a]) == 0:  # mjTRN_JOINT
                jids.append(int(model.actuator_trnid[a, 0]))
        # de-dup, preserve order
        seen, out = set(), []
        for j in jids:
            if j not in seen:
                seen.add(j)
                out.append(j)
        return out

    # ------------------------------------------------------------------ #
    def solve(
        self,
        target_pos: np.ndarray,
        target_quat_xyzw: np.ndarray,
        q_init: np.ndarray,
        max_iters: int | None = None,
        tol: float | None = None,
    ) -> "np.ndarray | None":
        """Solve for joint angles reaching (target_pos, target_quat_xyzw).

        Args:
            target_pos: (3,) desired TCP position (world frame).
            target_quat_xyzw: (4,) desired TCP orientation, **xyzw** order
                (robot_contracts.Pose convention).
            q_init: (DoF,) seed configuration.
            max_iters / tol: override the constructor defaults.

        Returns:
            (DoF,) joint vector on convergence, else ``None``.
        """
        max_iters = int(max_iters if max_iters is not None else self._max_iters)
        tol = float(tol if tol is not None else self._pos_tol)

        q = np.asarray(q_init, dtype=float).reshape(-1).copy()
        dof = len(self._arm_jids)
        if q.shape[0] != dof:
            # pad / truncate to the actuated dof
            q_full = np.zeros(dof, dtype=float)
            n = min(q.shape[0], dof)
            q_full[:n] = q[:n]
            q = q_full

        target_pos = np.asarray(target_pos, dtype=float).reshape(3)
        target_wxyz = np.array(
            [target_quat_xyzw[3], *target_quat_xyzw[:3]], dtype=float
        )

        for _ in range(max_iters):
            err_pos, err_rot = self._pose_error(q, target_pos, target_wxyz)
            if np.linalg.norm(err_pos) < tol and np.linalg.norm(err_rot) < self._rot_tol:
                return q
            # full 6D residual
            err = np.concatenate([err_pos, err_rot])  # (6,)
            J = self._jacobian(q)  # (6, dof)
            # DLS update: dq = J^T (J J^T + lambda^2 I)^-1 err
            JT = J.T
            JJt = J @ JT
            lam2 = self._damping ** 2
            A = JJt + lam2 * np.eye(6)
            dq = JT @ np.linalg.solve(A, err)
            # limit step for stability
            step = np.clip(dq, -0.2, 0.2)
            q = q + step
            # clamp to joint limits
            low, high = self._limits()
            q = np.clip(q, low, high)
        return None

    # ------------------------------------------------------------------ #
    def _pose_error(self, q, target_pos, target_wxyz):
        """Return (err_pos (3,), err_rot (3,)) in world frame."""
        self._set_qpos(q)
        self._mj.mj_forward(self._model, self._data)
        pos = self._data.site_xpos[self._site_id].copy()
        rot = self._data.site_xmat[self._site_id].reshape(3, 3).copy()
        cur_wxyz = self._rot_to_quat_wxyz(rot)
        err_pos = target_pos - pos
        # rotation residual: R_err = R_target * R_cur^T -> axis-angle
        R_t = self._quat_to_rot(target_wxyz)
        R_c = self._quat_to_rot(cur_wxyz)
        R_err = R_t @ R_c.T
        err_rot = self._rot_to_axis_angle(R_err)
        return err_pos, err_rot

    def _jacobian(self, q) -> np.ndarray:
        self._set_qpos(q)
        self._mj.mj_forward(self._model, self._data)
        Jp = np.zeros((3, self._model.nv))
        Jr = np.zeros((3, self._model.nv))
        self._mj.mj_jacSite(self._model, self._data, Jp, Jr, self._site_id)
        # keep only the actuated joint columns (nv may include free joints)
        cols = self._arm_jids  # assume 1 dof per arm joint (nv == nq for arms)
        if len(cols) == Jp.shape[1]:
            J_full = np.vstack([Jp, Jr])  # (6, nv)
        else:
            J_full = np.vstack([Jp, Jr])[:, cols]
        return J_full  # (6, dof)

    def _set_qpos(self, q) -> None:
        for i, jid in enumerate(self._arm_jids):
            if jid < self._model.nq:
                self._data.qpos[jid] = q[i]

    def _limits(self):
        low, high = [], []
        for jid in self._arm_jids:
            rng = self._model.jnt_range[jid]
            low.append(rng[0])
            high.append(rng[1])
        return np.asarray(low), np.asarray(high)

    # ------------------------------------------------------------------ #
    @staticmethod
    def _rot_to_quat_wxyz(rot: np.ndarray) -> np.ndarray:
        r = np.asarray(rot, dtype=float)
        w = np.sqrt(max(0.0, 1.0 + r[0, 0] + r[1, 1] + r[2, 2])) / 2.0
        x = np.sqrt(max(0.0, 1.0 + r[0, 0] - r[1, 1] - r[2, 2])) / 2.0
        y = np.sqrt(max(0.0, 1.0 - r[0, 0] + r[1, 1] - r[2, 2])) / 2.0
        z = np.sqrt(max(0.0, 1.0 - r[0, 0] - r[1, 1] + r[2, 2])) / 2.0
        if r[2, 1] - r[1, 2] < 0:
            x = -x
        if r[0, 2] - r[2, 0] < 0:
            y = -y
        if r[1, 0] - r[0, 1] < 0:
            z = -z
        return np.array([w, x, y, z], dtype=float)

    @staticmethod
    def _quat_to_rot(q_wxyz: np.ndarray) -> np.ndarray:
        w, x, y, z = q_wxyz
        n = w * w + x * x + y * y + z * z
        s = 2.0 / n if n > 0 else 0.0
        return np.array([
            [1 - s * (y * y + z * z), s * (x * y - z * w), s * (x * z + y * w)],
            [s * (x * y + z * w), 1 - s * (x * x + z * z), s * (y * z - x * w)],
            [s * (x * z - y * w), s * (y * z + x * w), 1 - s * (x * x + y * y)],
        ])

    @staticmethod
    def _rot_to_axis_angle(rot: np.ndarray) -> np.ndarray:
        r = np.asarray(rot, dtype=float)
        cos_t = (r[0, 0] + r[1, 1] + r[2, 2] - 1.0) / 2.0
        cos_t = float(np.clip(cos_t, -1.0, 1.0))
        ang = np.arccos(cos_t)
        if ang < 1e-8:
            return np.zeros(3)
        rx = r[2, 1] - r[1, 2]
        ry = r[0, 2] - r[2, 0]
        rz = r[1, 0] - r[0, 1]
        axis = np.array([rx, ry, rz])
        n = np.linalg.norm(axis)
        if n < 1e-12:
            return np.zeros(3)
        return axis / n * ang


__all__ = ["MjIK"]
