"""Integration tests for the RCS-aligned simulation layer."""
from __future__ import annotations

import numpy as np
import pytest

from robot_contracts import RobotType

from backend.rcs_env import SimEnv, SimEnvCreator, SimEnvCreatorConfig, MjOMPL, Planner
from backend.rcs_env.envs.configs import get_config
from backend.rcs_env.extensions import all_extensions, available_robots


def test_env_reset_step_logistics_arm():
    env = SimEnv(robot_type=RobotType.ARM, logic_device_id="robot-01")
    obs, info = env.reset()
    assert obs.shape == env.observation_space.shape
    assert info["ee_pose"].translation.shape == (3,)
    action = env.action_space.sample()
    obs2, reward, terminated, truncated, info2 = env.step(action)
    assert obs2.shape == obs.shape
    assert not terminated and not truncated


def test_planner_solves_joint_path():
    env = SimEnv(robot_type=RobotType.ARM, logic_device_id="robot-01")
    env.reset()
    start = env.engine.qpos()
    goal = np.full(env.engine.dof, 0.3)
    path = env.ompl.plan(start, goal, Planner.RRTConnect)
    assert isinstance(path, list)
    # logic engine has no obstacles -> RRTConnect should connect
    assert len(path) >= 2
    assert np.allclose(path[-1], goal, atol=0.05)


def test_sim_env_creator_factory():
    cfg = SimEnvCreatorConfig(robot_type=RobotType.AGV, logic_device_id="agv-01")
    env = SimEnvCreator(cfg)()
    assert env.engine.dof == 2


def test_config_and_scene_lookup():
    assert get_config("LogisticsArm").robot_type == RobotType.ARM


def test_extensions_registered():
    robots = available_robots()
    keys = {e.key for e in all_extensions()}
    assert {"container_robot", "agv", "stacker"}.issubset(keys)
    assert len(robots) >= 4


def test_camera_wrapper_with_renderer():
    """CameraSetWrapper + SimRenderer 集成测试"""
    from rcs_env.renderer import SimRenderer
    from rcs_env.envs.wrappers import CameraSetWrapper

    if not SimRenderer.available():
        pytest.skip("MuJoCo not available")

    import mujoco
    model = mujoco.MjModel.from_xml_string("""
    <mujoco model="test">
        <worldbody>
            <body name="test_body" pos="0 0 0.5">
                <geom type="box" size="0.1 0.1 0.1"/>
            </body>
        </worldbody>
    </mujoco>
    """)
    data = mujoco.MjData(model)
    renderer = SimRenderer(model, data, width=160, height=120)

    # 创建 mock env
    class MockEnv:
        def reset(self):
            return np.zeros(14), {}
        def step(self, action):
            return np.zeros(14), 0.0, False, False, {}
        observation_space = gym.spaces.Box(low=-1, high=1, shape=(14,))

    import gymnasium as gym
    env = MockEnv()
    wrapped = CameraSetWrapper(env, renderer=renderer, width=160, height=120)

    obs, _ = wrapped.reset()

    assert "rgb" in obs
    assert obs["rgb"].shape == (120, 160, 3)
    assert obs["rgb"].dtype == np.uint8


def test_camera_wrapper_without_renderer():
    """CameraSetWrapper 无 renderer 时返回零帧"""
    from rcs_env.envs.wrappers import CameraSetWrapper

    import gymnasium as gym

    class MockEnv:
        def reset(self):
            return np.zeros(14), {}
        def step(self, action):
            return np.zeros(14), 0.0, False, False, {}
        observation_space = gym.spaces.Box(low=-1, high=1, shape=(14,))

    env = MockEnv()
    wrapped = CameraSetWrapper(env, renderer=None, width=160, height=120)

    obs, _ = wrapped.reset()

    assert "rgb" in obs
    assert obs["rgb"].shape == (120, 160, 3)
    assert np.all(obs["rgb"] == 0)  # 零帧
