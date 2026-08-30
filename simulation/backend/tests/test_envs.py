"""P2.3/P2.4/P3 tests: configs, scenes, Gym capabilities.

Headless-safe: real engine construction needs mujoco + rcs.sim; skips otherwise.
"""
from __future__ import annotations

import numpy as np

try:
    import pytest
except ModuleNotFoundError:  # pytest optional at import time
    pytest = None


def _ready() -> bool:
    try:
        from rcs import sim  # noqa: F401
        import mujoco  # noqa: F401
        return True
    except Exception:
        return False


# apply skipif only when pytest is available
def _maybe_skip(fn):
    if pytest is not None:
        return pytest.mark.skipif(not _ready(), reason="mujoco / rcs.sim unavailable")(fn)
    return fn


@_maybe_skip
def test_configs_roster():
    from backend.rcs_env.envs.configs import get_config, ROBOT_ASSETS

    for name in ROBOT_ASSETS:
        cfg = get_config(name)
        assert cfg.mjcf_path and cfg.robot_type is not None


@_maybe_skip
def test_scenes_build_envconfig():
    from backend.rcs_env.envs.scenes import get_scene, SCENES

    for sname in SCENES:
        cfg = get_scene(sname)
        assert cfg.scene is not None
        assert len(cfg.scene.robots) >= 1


@_maybe_skip
def test_scene_composes_and_runs():
    from backend.rcs_env.envs.scenes import get_scene
    from backend.rcs_env.envs.creator import SimEnvCreator

    env = SimEnvCreator(get_scene("tabletop_pick"))()
    obs, info = env.reset()
    assert obs.shape == (3 + 4 + env.engine.dof + 1,)
    env.step(env.engine.qpos() + 0.02)
    env.close()


@_maybe_skip
def test_gym_register_and_ik_reward():
    from backend.rcs_env.envs.base import register_envs, make_env

    register_envs()
    env = make_env("rcs/tabletop_stack-v0")
    raw = env.unwrapped  # gym.make wraps in OrderEnforcing
    obs, info = env.reset()
    assert "goal_ee" in info
    # IK round-trip
    q = raw.engine.inverse_kinematics(info["goal_ee"], raw.engine.qpos())
    assert q is not None and q.shape == (raw.engine.dof,)
    o2, r, term, trunc, _ = env.step(raw.engine.qpos() + 0.05)
    assert isinstance(r, float) and isinstance(term, bool)
    env.close()
