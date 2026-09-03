"""Microduck deployment contract (spec §7) + variant registry.

This module holds all Microduck-specific constants so that the engine, env,
ONNX bridge and frontend can share ONE source of truth:

* :data:`POLICY_JOINTS`    14 actuator/joint names in the official policy order
* :data:`HOME_POSE`        home angle (rad) per joint
* :data:`VARIANTS`         all 7 MJCF variants with their file + flags
* helper math: ``build_microduck_obs``, ``policy_action_to_motor_targets``,
  ``home_pose_vector``, ``quat_wxyz_to_rot``
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Sequence

import numpy as np

# Assets live at <repo>/simulation/backend/assets/robots/microduck (vendored T1).
_ASSETS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))
MICRODUCK_DIR = os.path.join(_ASSETS_ROOT, "robots", "microduck")

# 7 official variants from microduck_rl (nu == 14 for all of them).
MICRODUCK_VARIANTS = {
    "walk": "robot_walk.xml",
    "groundcontact": "robot_groundcontact.xml",
    "allcollisions": "robot_allcollisions.xml",
    "groundcontact_rollers": "robot_groundcontact_rollers.xml",
    "walk_backlash": "robot_walk_backlash.xml",
    "groundcontact_backlash": "robot_groundcontact_backlash.xml",
    "groundcontact_rollers_backlash": "robot_groundcontact_rollers_backlash.xml",
}

# The 14 joint/actuator names in the EXACT order the official policy expects.
# trunk_base_freejoint is the 6-DOF floating base (NOT a controllable actuator).
POLICY_JOINTS: tuple[str, ...] = (
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
    "neck_pitch",
    "head_pitch", "head_yaw", "head_roll",
    "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle",
)

# Home angles (rad) per joint. neck_pitch 0.35 lifts the head; legs slightly bent.
HOME_POSE: Dict[str, float] = {
    "left_hip_yaw": 0.0, "left_hip_roll": 0.0, "left_hip_pitch": 0.05,
    "left_knee": -0.1, "left_ankle": 0.05,
    "neck_pitch": 0.35,
    "head_pitch": 0.0, "head_yaw": 0.0, "head_roll": 0.0,
    "right_hip_yaw": 0.0, "right_hip_roll": 0.0, "right_hip_pitch": 0.05,
    "right_knee": -0.1, "right_ankle": 0.05,
}

# Observation / action contract dimensions (spec §7.1 / §7.3).
MICRODUCK_NU = 14          # == number of position actuators
N_OBS = 61
N_ACTION = 14

# Observation layout (slice indices into the 61-dim vector).
OBS_GYRO = slice(0, 3)         # body-frame angular velocity
OBS_GRAVITY = slice(3, 6)      # projected gravity (body frame)
OBS_JOINT_POS = slice(6, 20)   # 14 joint angles relative to home
OBS_JOINT_VEL = slice(20, 34)  # 14 joint velocities
OBS_LAST_ACTION = slice(34, 48)
OBS_COMMAND = slice(48, 61)    # 13-dim command block

GRAVITY_WORLD = np.array([0.0, 0.0, -9.81], dtype=float)


@dataclass(frozen=True)
class VariantConfig:
    xml: str
    mjcf_path: str
    has_backlash: bool
    has_rollers: bool


def _variant_config(name: str, xml: str) -> VariantConfig:
    return VariantConfig(
        xml=xml,
        mjcf_path=os.path.join(MICRODUCK_DIR, xml),
        has_backlash="backlash" in name,
        has_rollers="rollers" in name,
    )


VARIANTS: Dict[str, VariantConfig] = {
    name: _variant_config(name, xml) for name, xml in MICRODUCK_VARIANTS.items()
}


def build_microduck_obs(
    qpos: np.ndarray,
    qvel: np.ndarray,
    last_action: np.ndarray,
    command: np.ndarray,
    joint_qpos_addr: Sequence[int],
    joint_qvel_addr: Sequence[int],
) -> np.ndarray:
    """Assemble the 61-dim observation (spec §7.1).

    ``qpos``/``qvel`` are the full floating-base vectors (nq=21/nv=20); the
    joint addresses index into them. The first 7 entries of ``qpos`` are the
    freejoint (x,y,z, quat_wxyz).
    """
    rot = quat_wxyz_to_rot(qpos[3:7])            # world <- body
    gyro_body = rot.T @ qvel[3:6]
    # Normalized projected gravity (unit vector) — matches the official policy
    # contract (spec §7.1) and keeps the observation scale-invariant.
    proj_gravity = rot.T @ (GRAVITY_WORLD / np.linalg.norm(GRAVITY_WORLD))

    joint_pos = np.array([qpos[a] for a in joint_qpos_addr], dtype=float)
    joint_vel = np.array([qvel[a] for a in joint_qvel_addr], dtype=float)
    home = np.array([HOME_POSE[j] for j in POLICY_JOINTS], dtype=float)

    obs = np.zeros(N_OBS, dtype=float)
    obs[OBS_GYRO] = gyro_body
    obs[OBS_GRAVITY] = proj_gravity
    obs[OBS_JOINT_POS] = joint_pos - home
    obs[OBS_JOINT_VEL] = joint_vel
    obs[OBS_LAST_ACTION] = np.asarray(last_action, dtype=float).reshape(-1)
    obs[OBS_COMMAND] = np.asarray(command, dtype=float).reshape(-1)
    return obs


def policy_action_to_motor_targets(action: np.ndarray, action_scale: float = 0.5) -> np.ndarray:
    """Map a 14-dim policy action to 14 home-relative joint targets."""
    a = np.asarray(action, dtype=float).reshape(-1)
    home = np.array([HOME_POSE[j] for j in POLICY_JOINTS], dtype=float)
    return home + action_scale * np.clip(a, -1.0, 1.0)


def home_pose_vector(joint_names: Sequence[str], variant: "VariantConfig") -> np.ndarray:
    """Per-joint home angle in model joint order (skips the freejoint).

    Passive/non-actuated joints (e.g. the rollers variant's ``passive_*_wheel``)
    are not in :data:`HOME_POSE` and are skipped, so the returned vector always
    covers the 14 controller joints regardless of variant.
    """
    out = []
    for n in joint_names:
        if n == "trunk_base_freejoint":
            continue
        if n not in HOME_POSE:
            continue
        out.append(float(HOME_POSE[n]))
    return np.array(out, dtype=float)


def quat_wxyz_to_rot(q: np.ndarray) -> np.ndarray:
    """Rotation matrix (body<-world) from a wxyz quaternion."""
    w, x, y, z = (float(v) for v in q)
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
        [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
        [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
    ], dtype=float)
