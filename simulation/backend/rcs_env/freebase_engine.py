"""Floating-base MuJoCo engine (ctrl-driven) for freejoint robots.

Why this exists: :class:`rcs_env.engine.MuJoCoEngine` is arm-oriented — its
``step()`` writes ``data.qpos`` directly (teleporting the robot instead of
driving actuators) and its ``_detect_robot_config()`` injects a TCP site and
reloads the MJCF. Both are wrong for a freejoint biped, whose 14-element action
would otherwise overwrite the 7-element freejoint pose.

This engine is purely additive: it drives ``data.ctrl`` and integrates with
``mj_step``, and exposes the full ``qpos``/``qvel`` including the freejoint.
"""
from __future__ import annotations

from typing import Sequence

import mujoco
import numpy as np

from .envs.microduck_cfg import VARIANTS


class FreeBaseMuJoCoEngine:
    """MuJoCo wrapper for floating-base robots driven through ``data.ctrl``."""

    def __init__(self, model: "mujoco.MjModel", dt: float = 0.002) -> None:
        self.model = model
        self.data = mujoco.MjData(model)
        self.dt = float(dt)
        model.opt.timestep = self.dt
        self.qpos_addr: dict[str, int] = {}
        self.qvel_addr: dict[str, int] = {}
        self._cache_addresses()

    # ---- construction ----------------------------------------------------- #
    @classmethod
    def from_mjcf(cls, mjcf_path: str, dt: float = 0.002) -> "FreeBaseMuJoCoEngine":
        return cls(mujoco.MjModel.from_xml_path(mjcf_path), dt=dt)

    @classmethod
    def from_variant(cls, variant: str, dt: float = 0.002) -> "FreeBaseMuJoCoEngine":
        if variant not in VARIANTS:
            raise KeyError(f"Unknown Microduck variant '{variant}'. Known: {sorted(VARIANTS)}")
        return cls.from_mjcf(VARIANTS[variant].mjcf_path, dt=dt)

    def _cache_addresses(self) -> None:
        for i in range(self.model.njnt):
            name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, i)
            if not name:
                continue
            self.qpos_addr[name] = int(self.model.jnt_qposadr[i])
            self.qvel_addr[name] = int(self.model.jnt_dofadr[i])

    # ---- dimensions ------------------------------------------------------- #
    @property
    def nq(self) -> int:
        return int(self.model.nq)

    @property
    def nv(self) -> int:
        return int(self.model.nv)

    @property
    def nu(self) -> int:
        return int(self.model.nu)

    # ---- state ------------------------------------------------------------ #
    def reset(self, qpos: "np.ndarray | None" = None, qvel: "np.ndarray | None" = None) -> None:
        mujoco.mj_resetData(self.model, self.data)
        # mj_resetData can leave an all-zero (invalid) freejoint quaternion when
        # the MJCF declares no default rotation; force a valid identity quat.
        if self.model.nq >= 7 and not np.any(self.data.qpos[3:7]):
            self.data.qpos[3:7] = (1.0, 0.0, 0.0, 0.0)
        if qpos is not None:
            self.data.qpos[:] = np.asarray(qpos, dtype=float).reshape(-1)
        if qvel is not None:
            self.data.qvel[:] = np.asarray(qvel, dtype=float).reshape(-1)
        mujoco.mj_forward(self.model, self.data)

    def step_ctrl(self, ctrl: Sequence[float]) -> None:
        """Write actuator commands and integrate real dynamics."""
        c = np.asarray(ctrl, dtype=float).reshape(-1)
        if c.shape[0] != self.nu:
            raise ValueError(f"ctrl must have {self.nu} entries, got {c.shape[0]}")
        self.data.ctrl[:] = c
        mujoco.mj_step(self.model, self.data)

    def qpos(self) -> np.ndarray:
        """Full generalized position INCLUDING the freejoint."""
        return self.data.qpos.copy()

    def qvel(self) -> np.ndarray:
        """Full generalized velocity INCLUDING the freejoint."""
        return self.data.qvel.copy()

    def joint_qpos(self, names: Sequence[str]) -> np.ndarray:
        return np.array([self.data.qpos[self.qpos_addr[n]] for n in names])

    def joint_qvel(self, names: Sequence[str]) -> np.ndarray:
        return np.array([self.data.qvel[self.qvel_addr[n]] for n in names])

    def actuator_names(self) -> list[str]:
        return [
            mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, i) or ""
            for i in range(self.nu)
        ]

    def joint_names(self) -> list[str]:
        return [
            mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, i) or ""
            for i in range(self.model.njnt)
        ]

    def lowest_geom_z(self) -> float:
        """Lowest world-z over all geoms (used to stand the robot on the floor)."""
        mujoco.mj_forward(self.model, self.data)
        return float(np.min(self.data.geom_xpos[:, 2]))

    def close(self) -> None:
        self.model = None  # type: ignore[assignment]
        self.data = None  # type: ignore[assignment]
