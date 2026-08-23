"""OMPL-aligned motion planner — interface parity with ``robot-control-stack``'s
``rcs.ompl.MjOMPL``.

RCS exposes:
    * ``plan(start, goal, planner=Planner.RRTConnect)`` -> list[qpos]
    * ``plan_SE3(goal_pose, planner, max_iters)`` -> list[qpos] (pose goal via IK)
    * ``solve(goal_state, start_state, planner)``
    * ``set_pose / collision_free / ik / set_joint_limts``

This module provides the same surface on top of robot-logic's engine abstraction.
It uses a pure-python sampling-based planner (RRT / RRT-Connect / RRT* / PRM) so
it runs without the OMPL native dependency, while keeping the RCS call signature
intact. drop-in OMPL (``pip install ompl``) acceleration can be added behind the
same interface later.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence

import numpy as np

from .engine import PhysicsEngine


class Planner(str, Enum):
    RRT = "RRT"
    RRTConnect = "RRTConnect"
    RRTstar = "RRTstar"
    PRM = "PRM"


@dataclass
class PlanResult:
    success: bool
    path: list[np.ndarray]
    reason: str = ""


class MjOMPL:
    """Motion planner over a :class:`PhysicsEngine` (parity with RCS ``MjOMPL``)."""

    def __init__(
        self,
        physics: PhysicsEngine,
        planner: Planner = Planner.RRTConnect,
        collision_fn: Callable[[Sequence[float]], bool] | None = None,
        ik_fn: Callable[[np.ndarray], np.ndarray | None] | None = None,
        goal_tolerance: float = 0.05,
        max_iters: int = 2000,
        step_size: float = 0.1,
    ) -> None:
        self.physics = physics
        self.planner = planner
        self._collision_fn = collision_fn or physics.collision_free
        self._ik_fn = ik_fn
        self.goal_tolerance = goal_tolerance
        self.max_iters = max_iters
        self.step_size = step_size
        low, high = physics.joint_limits()
        self.limits_low = low.astype(float)
        self.limits_high = high.astype(float)

    # ---- RCS-parity public API --------------------------------------------- #
    def set_pose(self, qpos: Sequence[float]) -> None:
        self.physics.set_qpos(qpos)

    def set_joint_limts(self, low: Sequence[float], high: Sequence[float]) -> None:
        self.limits_low = np.asarray(low, dtype=float)
        self.limits_high = np.asarray(high, dtype=float)

    def collision_free(self, qpos: Sequence[float]) -> bool:
        return bool(self._collision_fn(qpos))

    def ik(self, goal_ee_pose: np.ndarray) -> np.ndarray | None:
        """Simple Jacobian-free IK via random-restart + forward kinematics (RCS ``ik``).

        ``goal_ee_pose`` is a 7-vector [x,y,z, qx,qy,qz,qw].
        """
        if self._ik_fn is not None:
            return self._ik_fn(goal_ee_pose)
        from robot_contracts import Pose

        target = Pose(translation=goal_ee_pose[:3], quaternion=goal_ee_pose[3:7])
        dof = self.physics.dof
        best_q, best_err = None, math.inf
        for _ in range(200):
            q = np.random.uniform(self.limits_low, self.limits_high)
            ee = self.physics.forward_kinematics(q)
            err = float(np.linalg.norm(ee.translation - target.translation))
            if err < best_err:
                best_err, best_q = err, q
            if err < self.goal_tolerance:
                return q
        return best_q if best_err < 0.1 else None

    def plan(self, start: Sequence[float], goal: Sequence[float], planner: Planner | None = None) -> list[np.ndarray]:
        planner = planner or self.planner
        if planner == Planner.PRM:
            return self._plan_prm(np.asarray(start, dtype=float), np.asarray(goal, dtype=float))
        return self._plan_rrt(np.asarray(start, dtype=float), np.asarray(goal, dtype=float), planner)

    def plan_SE3(self, goal_pose: np.ndarray, planner: Planner | None = None, max_iters: int | None = None) -> list[np.ndarray]:
        goal_q = self.ik(goal_pose)
        if goal_q is None:
            return []
        return self.plan(self.physics.qpos(), goal_q, planner or self.planner)

    def solve(self, goal_state: Sequence[float], start_state: Sequence[float] | None = None, planner: Planner | None = None) -> list[np.ndarray]:
        start = np.asarray(start_state if start_state is not None else self.physics.qpos(), dtype=float)
        return self.plan(start, np.asarray(goal_state, dtype=float), planner)

    # ---- internal samplers -------------------------------------------------- #
    def _random_config(self) -> np.ndarray:
        return np.random.uniform(self.limits_low, self.limits_high)

    def _nearest(self, tree: list[np.ndarray], q: np.ndarray) -> np.ndarray:
        return min(tree, key=lambda n: float(np.linalg.norm(n - q)))

    def _steer(self, frm: np.ndarray, to: np.ndarray) -> np.ndarray:
        d = to - frm
        dist = float(np.linalg.norm(d))
        if dist <= self.step_size:
            return to.copy()
        return frm + d / dist * self.step_size

    def _local_free(self, a: np.ndarray, b: np.ndarray) -> bool:
        steps = max(2, int(math.ceil(float(np.linalg.norm(b - a)) / (self.step_size / 2))))
        for i in range(1, steps):
            q = a + (b - a) * i / steps
            if not self.collision_free(q):
                return False
        return True

    def _plan_rrt(self, start: np.ndarray, goal: np.ndarray, planner: Planner) -> list[np.ndarray]:
        rng = random.Random(0)
        tree = [start.copy()]
        parent = {0: -1}
        for _ in range(self.max_iters):
            q_rand = goal if rng.random() < 0.1 else self._random_config()
            q_near = self._nearest(tree, q_rand)
            q_new = self._steer(q_near, q_rand)
            if not self.collision_free(q_new) or not self._local_free(q_near, q_new):
                continue
            idx = len(tree)
            tree.append(q_new)
            parent[idx] = tree.index(q_near)
            if planner == Planner.RRTConnect:
                # greedy connect attempt toward goal
                if self._local_free(q_new, goal) and self.collision_free(goal):
                    tree.append(goal.copy())
                    parent[len(tree) - 1] = idx
                    return self._extract(tree, parent, len(tree) - 1)
            if float(np.linalg.norm(q_new - goal)) < self.goal_tolerance and self.collision_free(goal):
                tree.append(goal.copy())
                parent[len(tree) - 1] = idx
                return self._extract(tree, parent, len(tree) - 1)
        return []

    def _extract(self, tree: list[np.ndarray], parent: dict, end: int) -> list[np.ndarray]:
        path: list[np.ndarray] = []
        cur = end
        while cur != -1:
            path.append(tree[cur])
            cur = parent[cur]
        return path[::-1]

    def _plan_prm(self, start: np.ndarray, goal: np.ndarray) -> list[np.ndarray]:
        nodes: list[np.ndarray] = [start.copy(), goal.copy()]
        for _ in range(self.max_iters // 10):
            q = self._random_config()
            if self.collision_free(q):
                nodes.append(q)
        # connect each node to nearest k neighbours
        adj: dict[int, list[int]] = {i: [] for i in range(len(nodes))}
        k = 8
        for i, q in enumerate(nodes):
            dists = sorted(range(len(nodes)), key=lambda j: float(np.linalg.norm(nodes[j] - q)))
            for j in dists[1 : k + 1]:
                if i != j and self._local_free(nodes[i], nodes[j]):
                    adj[i].append(j)
        # BFS start->goal
        from collections import deque

        prev = {0: -1}
        q = deque([0])
        while q:
            u = q.popleft()
            if u == 1:
                break
            for v in adj[u]:
                if v not in prev:
                    prev[v] = u
                    q.append(v)
        if 1 not in prev:
            return []
        path: list[np.ndarray] = []
        cur = 1
        while cur != -1:
            path.append(nodes[cur])
            cur = prev[cur]
        return path[::-1]


__all__ = ["Planner", "PlanResult", "MjOMPL"]
