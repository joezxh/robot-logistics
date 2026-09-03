import os

import mujoco
import numpy as np

# Assets live at <repo>/simulation/backend/assets/robots/microduck (see
# microduck_cfg._ASSETS_ROOT). test file is at rcs_env/tests/, so go up 3 levels.
MICRODUCK_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets", "robots", "microduck",
)

VARIANT_XMLS = (
    "robot_walk.xml",
    "robot_groundcontact.xml",
    "robot_allcollisions.xml",
    "robot_groundcontact_rollers.xml",
    "robot_walk_backlash.xml",
    "robot_groundcontact_backlash.xml",
    "robot_groundcontact_rollers_backlash.xml",
)


def test_all_variants_present_and_load():
    for xml in VARIANT_XMLS:
        path = os.path.join(MICRODUCK_DIR, xml)
        assert os.path.exists(path), f"missing MJCF: {path}"
        m = mujoco.MjModel.from_xml_path(path)
        assert m.nu == 14, f"{xml}: expected nu=14, got {m.nu}"


def test_walk_joint_order_matches_policy_order():
    # microduck_cfg is created in Task 3 (P1+P2 backend plan); skip until then.
    try:
        from rcs_env.envs.microduck_cfg import POLICY_JOINTS
    except ModuleNotFoundError:
        import pytest
        pytest.skip("microduck_cfg not yet created (Task 3)")
    m = mujoco.MjModel.from_xml_path(os.path.join(MICRODUCK_DIR, "robot_walk.xml"))
    joints = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
    assert joints[0] == "trunk_base_freejoint"
    assert tuple(joints[1:]) == POLICY_JOINTS


def test_servo_to_actuator_drop_mouth():
    from rcs_env.envs.microduck_cfg import (
        POLICY_JOINTS, HOME_POSE, policy_action_to_motor_targets,
    )
    a = np.linspace(-0.5, 0.5, 14)
    targets = policy_action_to_motor_targets(a)
    assert targets.shape == (14,)
    home = np.array([HOME_POSE[j] for j in POLICY_JOINTS])
    assert np.allclose(targets, home + 0.5 * a, atol=1e-9)


def test_command_roundtrip():
    from rcs_env.envs.microduck_cfg import build_microduck_obs, OBS_GRAVITY, N_OBS
    qpos = np.zeros(21); qpos[2] = 0.2; qpos[3:7] = (1.0, 0, 0, 0)
    qvel = np.zeros(20); qvel[3:6] = (0.1, 0.0, -0.2)
    addr = list(range(7, 21))   # 14 revolute joints
    dof = list(range(6, 20))
    obs = build_microduck_obs(qpos, qvel, np.zeros(14), np.zeros(13), addr, dof)
    assert obs.shape == (N_OBS,)
    assert np.all(np.isfinite(obs))
    # identity rotation -> projected gravity equals world gravity normalized
    assert np.allclose(obs[OBS_GRAVITY], (0.0, 0.0, -1.0), atol=1e-9)


def test_variant_registry_covers_all_seven():
    from rcs_env.envs.microduck_cfg import VARIANTS, MICRODUCK_DIR
    assert set(VARIANTS) == {
        "walk", "groundcontact", "allcollisions",
        "groundcontact_rollers", "walk_backlash",
        "groundcontact_backlash", "groundcontact_rollers_backlash",
    }
    for name, v in VARIANTS.items():
        assert os.path.exists(v.mjcf_path), v.mjcf_path
