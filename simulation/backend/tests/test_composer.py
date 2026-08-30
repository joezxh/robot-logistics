"""Phase 2 tests: ModelComposer + SimEnvCreator(scene) 重组。

Headless 安全：需要 mujoco + rcs.sim 时才真正运行，否则 skip。
"""
from __future__ import annotations

import numpy as np
import pytest

from robot_contracts import Pose, RobotType

from backend.rcs_env import MuJoCoEngine, ModelComposer, EnvConfig
from backend.rcs_env.envs.composer import RobotSpec, ObjectSpec, CameraSpec
from backend.rcs_env.envs.creator import SimEnvCreatorConfig, SimEnvCreator


def _mujoco_ready() -> bool:
    try:
        from rcs import sim  # noqa: F401
        import mujoco  # noqa: F401
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _mujoco_ready(), reason="mujoco / rcs.sim unavailable")
def test_composer_builds_fr3_engine(tmp_path):
    # 用最小 MJCF 验证 ModelComposer 拼装 + 引擎加载
    robot_xml = tmp_path / "robot.xml"
    robot_xml.write_text("""
    <mujoco model="robot">
      <worldbody>
        <body name="base" pos="0 0 0.1">
          <joint name="j1" type="hinge" axis="0 0 1"/>
          <geom type="box" size="0.05 0.05 0.05"/>
        </body>
      </worldbody>
    </mujoco>
    """)
    composer = ModelComposer(model_name="t")
    composer.add_robot(str(robot_xml), "r1_", Pose.from_keywords(x=0.0, z=0.2))
    engine = composer.build_engine()
    assert isinstance(engine, MuJoCoEngine)
    assert engine.dof >= 1


@pytest.mark.skipif(not _mujoco_ready(), reason="mujoco / rcs.sim unavailable")
def test_sim_env_creator_with_scene(tmp_path):
    robot_xml = tmp_path / "robot.xml"
    robot_xml.write_text("""
    <mujoco model="robot">
      <worldbody>
        <body name="base" pos="0 0 0.1">
          <joint name="j1" type="hinge" axis="0 0 1"/>
          <joint name="j2" type="hinge" axis="1 0 0"/>
          <geom type="box" size="0.05 0.05 0.05"/>
        </body>
      </worldbody>
    </mujoco>
    """)
    scene = EnvConfig(
        name="scene1",
        robots=[RobotSpec(xml_path=str(robot_xml), prefix="r1_", pose=Pose.from_keywords(z=0.1))],
        cameras=[CameraSpec(name="cam0", resolution=(64, 48))],
    )
    cfg = SimEnvCreatorConfig(robot_type=RobotType.ARM, scene=scene)
    env = SimEnvCreator(cfg)()
    assert env.engine.dof >= 2
    # camera 注入
    from backend.rcs_env.envs.wrappers import CameraSetWrapper

    wrapped = CameraSetWrapper(env, engine=env.engine, width=64, height=48)
    obs, _ = wrapped.reset()
    assert obs["rgb"].shape == (48, 64, 3)
