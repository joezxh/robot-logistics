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


def test_freebase_engine_loads_walk():
    from rcs_env.freebase_engine import FreeBaseMuJoCoEngine
    eng = FreeBaseMuJoCoEngine.from_variant("walk")
    eng.reset()
    assert eng.nq == 21 and eng.nu == 14 and eng.nv == 20
    # freejoint quaternion must be valid (unit length) after reset ...
    assert np.isclose(np.linalg.norm(eng.qpos()[3:7]), 1.0, atol=1e-6)
    # ... and must survive a ctrl step. A 14-element command must NOT be written
    # into qpos (that is what MuJoCoEngine.step() does, and it would clobber the
    # freejoint pose because nq=21 > nu=14).
    eng.step_ctrl(np.zeros(14))
    assert eng.qpos().shape == (21,)
    assert np.isclose(np.linalg.norm(eng.qpos()[3:7]), 1.0, atol=1e-6)


def test_freebase_engine_ctrl_moves_joints_toward_target():
    from rcs_env.freebase_engine import FreeBaseMuJoCoEngine
    from rcs_env.envs.microduck_cfg import HOME_POSE, POLICY_JOINTS
    eng = FreeBaseMuJoCoEngine.from_variant("walk")
    eng.reset()
    target = np.array([HOME_POSE[j] for j in POLICY_JOINTS])
    err_before = float(np.abs(eng.joint_qpos(POLICY_JOINTS) - target).max())
    for _ in range(2000):
        eng.step_ctrl(target)
    err_after = float(np.abs(eng.joint_qpos(POLICY_JOINTS) - target).max())
    assert err_after < err_before, f"no convergence: {err_before} -> {err_after}"
    assert err_after < 0.1, f"tracking error too large: {err_after}"


def test_env_observation_is_61_dim():
    from rcs_env.envs.microduck import MicroduckEnv
    env = MicroduckEnv(variant="walk")
    obs, _ = env.reset(seed=0)
    assert env.observation_space.shape == (61,)
    assert env.action_space.shape == (14,)
    assert obs.shape == (61,)
    assert np.all(np.isfinite(obs))


def test_env_observation_blocks_are_correct():
    from rcs_env.envs.microduck import MicroduckEnv
    env = MicroduckEnv(variant="walk")
    obs, _ = env.reset(seed=0)
    g = obs[3:6]
    assert np.isclose(np.linalg.norm(g), 1.0, atol=1e-6)   # projected gravity is unit
    assert np.allclose(obs[6:20], 0.0, atol=1e-6)          # joint pos == home at reset
    assert np.allclose(obs[20:34], 0.0, atol=1e-6)         # zero velocity
    assert np.allclose(obs[34:48], 0.0)                    # no previous action
    # command block (last 13 = 61-48); body-pose stays pinned at 0 per spec §7.1
    assert obs[48:61].shape == (13,)
    assert obs[55] == 0.0 and obs[56] == 0.0 and obs[60] == 0.0
    assert -0.5 <= obs[48] <= 0.5                         # sampled forward twist in range


def test_env_step_returns_five_tuple_and_terminates_on_fall():
    from rcs_env.envs.microduck import MicroduckEnv
    env = MicroduckEnv(variant="walk")
    env.reset(seed=0)
    obs, reward, term, trunc, info = env.step(np.zeros(14))
    assert obs.shape == (61,)
    assert isinstance(float(reward), float)
    assert isinstance(bool(term), bool) and isinstance(bool(trunc), bool)
    # holding home pose should NOT immediately terminate
    assert not term, "robot should survive at least one control step at home pose"


def test_env_terminates_when_trunk_drops():
    from rcs_env.envs.microduck import MicroduckEnv
    env = MicroduckEnv(variant="walk")
    env.reset(seed=0)
    env.set_state_qpos_base_z(0.05)      # slam the trunk below the 0.15 m floor
    assert env._terminated()


def test_microduck_gym_ids_registered():
    import gymnasium as gym
    from rcs_env.envs.base import register_envs
    register_envs()
    for variant in ("walk", "groundcontact", "groundcontact_rollers"):
        env = gym.make(f"rcs/microduck-{variant}-v0")
        obs, _ = env.reset(seed=0)
        assert obs.shape == (61,)
        env.close()


def test_reset_samples_a_nonzero_velocity_command():
    """P4 T1: reset() samples a forward velocity command (spec §7.1)."""
    from rcs_env.envs.microduck import MicroduckEnv

    env = MicroduckEnv(variant="walk")
    seen = set()
    for seed in range(5):
        obs, _ = env.reset(seed=seed)
        assert obs.shape == (61,)
        vx = float(obs[48])
        assert 0.0 <= vx <= 0.4, f"cmd vx out of range at seed {seed}: {vx}"
        seen.add(round(vx, 6))
    # different seeds must produce different commands (non-degenerate sampling)
    assert len(seen) >= 2, f"command sampling looks degenerate: {seen}"
    env.close()


def test_command_block_keeps_13_slots():
    """P4 T1: command block occupies exactly 13 slots; body pose pinned at 0."""
    from rcs_env.envs.microduck import MicroduckEnv

    env = MicroduckEnv(variant="walk")
    obs, _ = env.reset(seed=1)
    assert obs[48:61].shape == (13,)
    assert obs[55] == 0.0 and obs[56] == 0.0 and obs[60] == 0.0
    env.close()
