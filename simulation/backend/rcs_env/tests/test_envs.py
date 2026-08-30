"""Integration tests for rcs_env (P2.3/P2.4/P3.1/P3.2 + FR3 home fix).

Run:
    python -m rcs_env.tests.test_envs
or
    pytest simulation/backend/rcs_env/tests/test_envs.py
(pytest is optional; falls back to plain asserts when unavailable.)
"""
from __future__ import annotations

import sys

import numpy as np

from rcs_env.envs.configs import ROBOT_ASSETS
from rcs_env.envs.scenes import SCENES, get_scene
from rcs_env.envs.base import register_envs, make_env, SimEnv
from rcs_env.envs.wrappers import (
    GripperWrapper,
    HandWrapper,
    StorageWrapper,
    DigitalTwinWrapper,
)
from rcs_env.envs.vec import make_vec_env, random_rollout
from rcs_env.envs.twin import (
    DigitalTwinSink,
    InMemoryTransport,
    LoopbackTransport,
    TwinRecord,
    _serialize_telemetry,
)


def _maybe_skip(fn):
    return fn


def test_roster_complete():
    assert "fr3" in ROBOT_ASSETS
    assert "panda" in ROBOT_ASSETS
    assert "so101" in ROBOT_ASSETS
    print("[OK] roster complete:", sorted(ROBOT_ASSETS))


def test_scenes_build():
    for name in SCENES:
        cfg = get_scene(name)
        assert cfg.scene is not None
    print("[OK] scenes build:", sorted(SCENES))


def test_fr3_reset_no_collision():
    """FR3 should reset into its 'home' keyframe, free of self-collision."""
    env = make_env("rcs/fr3-reach-v0")
    env.reset()
    ncon = int(env.unwrapped.engine.ncon())
    assert ncon == 0, f"FR3 reset self-collides (ncon={ncon}) — home keyframe not applied"
    # home pose should be the FR3 ready qpos, not all-zero
    qpos = env.unwrapped.engine.qpos()
    assert not np.allclose(qpos, 0.0), "FR3 reset fell back to all-zero qpos"
    print(f"[OK] fr3 reset collision-free (ncon={ncon}), home qpos[2]={qpos[2]:.3f}")
    env.close()


def test_gym_make_and_ik():
    env = make_env("rcs/fr3-reach-v0")
    obs, _ = env.reset()
    assert obs.shape[0] == env.observation_space.shape[0]
    goal = env.unwrapped._goal_ee
    q = env.unwrapped.engine.inverse_kinematics(goal)
    assert q is not None and len(q) == 7
    t = goal.translation
    print(f"[OK] gym.make + IK (goal_ee xyz={t[0]:.2f},{t[1]:.2f},{t[2]:.2f})")
    env.close()


def test_wrappers_compose():
    """Gripper+Hand+Storage+DigitalTwin wrappers compose and preserve shapes."""
    base = make_env("rcs/fr3-reach-v0")
    env = DigitalTwinWrapper(StorageWrapper(HandWrapper(GripperWrapper(base))))
    obs, info = env.reset()
    # base fr3-reach obs = 3+4+dof(7)+1 = 15; wrappers append 1+6+8 = 15 -> 30
    assert obs.shape[0] == 15 + 1 + 6 + 8, f"obs dim {obs.shape[0]} unexpected"
    action = np.zeros(env.action_space.shape[0])
    obs2, reward, terminated, truncated, info2 = env.step(action)
    assert obs2.shape[0] == obs.shape[0]
    assert "gripper_state" in info2
    assert "digital_twin" in info2 and len(info2["digital_twin"]) == 1
    dt = info2["digital_twin"][0]
    assert dt["robot_type"] in ("arm", "fr3")
    assert "qpos" in dt
    print(f"[OK] wrappers compose (obs_dim={obs.shape[0]}, "
          f"dt_robot={dt['robot_type']}, ee_pose={dt['ee_pose'] is not None})")
    env.close()


def test_p3_3_vecenv():
    """P3.3: vectorized env + random rollout smoke test."""
    vec = make_vec_env("rcs/fr3-reach-v0", n_envs=2, seed=0)
    assert vec.num_envs == 2
    # gymnasium batches the vector observation_space; single env is (15,)
    assert vec.single_observation_space.shape[0] == 15  # 3+4+dof(7)+1
    # batched obs from reset
    obs, _ = vec.reset()
    assert obs.shape == (2, 15)
    stats = random_rollout(vec, steps=128)
    assert stats["num_envs"] == 2
    assert stats["steps"] == 128
    print(f"[OK] P3.3 vecenv (obs={vec.single_observation_space.shape}, "
          f"mean_ep_return={stats['mean_episode_return']:.3f}, "
          f"mean_ep_len={stats['mean_episode_length']:.1f})")
    vec.close()


def test_p3_3_vecenv_with_gripper():
    """P3.3: wrappers applied inside the vector env extend obs by +1."""
    vec = make_vec_env(
        "rcs/fr3-reach-v0", n_envs=1, wrappers=[GripperWrapper], seed=0
    )
    obs, _ = vec.reset()
    assert obs.shape == (1, 15 + 1), f"gripper vec obs {obs.shape} unexpected"
    vec.close()
    print("[OK] P3.3 vecenv + GripperWrapper (obs_dim=16)")


def test_p3_4_twin_sink():
    """P3.4: DigitalTwinWrapper pushes records to a sink (in-memory backend)."""
    sink = DigitalTwinSink(device_id="fr3-01", transport=InMemoryTransport())
    base = make_env("rcs/fr3-reach-v0")
    env = DigitalTwinWrapper(base, sink=sink)
    obs, info = env.reset()
    assert "digital_twin" in info
    # step a few times; sink should buffer telemetry records
    for _ in range(4):
        obs, reward, terminated, truncated, info = env.step(np.zeros(env.action_space.shape[0]))
        if terminated or truncated:
            env.reset()
    # 1 reset record + 4 step records
    assert len(sink.transport) == 5, f"sink buffered {len(sink.transport)} records"
    rec = sink.transport.latest()
    assert rec.robot_type in ("arm", "fr3")
    assert len(rec.qpos) == 7  # FR3 dof
    assert rec.ee_pose is not None and len(rec.ee_pose) == 7
    print(f"[OK] P3.4 twin sink (records={len(sink.transport)}, "
          f"robot={rec.robot_type}, ee_pose={rec.ee_pose is not None})")
    env.close()


def test_p3_4_async_vecenv():
    """P3.4: AsyncVectorEnv (multiprocess) builds fresh Sims from task_id spec."""
    vec = make_vec_env("rcs/fr3-reach-v0", n_envs=2, async_=True, seed=0)
    assert vec.num_envs == 2
    obs, _ = vec.reset()
    assert obs.shape == (2, 15), f"async reset obs {obs.shape} unexpected"
    stats = random_rollout(vec, steps=64)
    assert stats["num_envs"] == 2
    print(f"[OK] P3.4 async vecenv (obs={obs.shape}, "
          f"mean_ep_return={stats['mean_episode_return']:.3f})")
    vec.close()


def test_p3_4b_twin_ingest_parse():
    """P3.4: a serialized twin frame parses into the canonical TelemetryPayload."""
    rec = TwinRecord(
        robot_type="fr3",
        qpos=[0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7],
        qvel=[0.0] * 7,
        ee_pose=[0.4, 0.1, 0.5, 1.0, 0.0, 0.0, 0.0],
        gripper_state=0.0,
        sim_time=1.234,
        episode=2,
        step=42,
        timestamp_ns=1_700_000_000_000_000_000,
    )
    # TelemetryPayload is the single wire-format source of truth; require it.
    # The sim venv may have a numpy-only stub on PYTHONPATH; force the canonical
    # contract package (repo-root shared/python) ahead of any cached stub.
    import sys as _sys
    from rcs_env.envs.twin import _contract_path_for

    _cp = _contract_path_for(None)
    if _cp:
        _sys.path.insert(0, _cp)
        _sys.modules.pop("robot_contracts", None)
        _sys.modules.pop("robot_contracts.payloads", None)
        _sys.modules.pop("robot_contracts.topics", None)
    from robot_contracts import TelemetryPayload

    topic, payload = _serialize_telemetry("fr3-demo", "", rec)
    assert topic == "robot/fr3-demo/telemetry", topic
    telem = TelemetryPayload.model_validate_json(payload)
    assert telem.device_id == "fr3-demo"
    assert telem.robot_type == "fr3"
    assert list(telem.qpos) == rec.qpos
    assert list(telem.ee_pose) == rec.ee_pose
    assert telem.sim_time == 1.234
    assert telem.episode == 2 and telem.step == 42
    print(f"[OK] P3.4b twin ingest parse (topic={topic}, qpos={len(telem.qpos)}, ee={len(telem.ee_pose)})")


def test_p3_4b_end_to_end_loopback():
    """P3.4: sim twin -> LoopbackTransport -> canonical contract parse (broker path).

    Exercises the exact serialize -> topic -> parse pipeline the real backend
    :class:`TelemetryIngest` runs, without a running Mosquitto or the heavy
    ``rcs.control`` backend package. We subscribe a handler that mirrors what the
    backend ingest does (validate ``TelemetryPayload`` and recover joint state).
    """
    sys.path.insert(0, "d:/projects/robot-logic/shared/python")
    sys.modules.pop("robot_contracts", None)
    for _m in list(sys.modules):
        if _m.startswith("robot_contracts."):
            sys.modules.pop(_m, None)
    from robot_contracts import TelemetryPayload

    DEVICE = "fr3-e2e"
    received_topic = []
    last_qpos = []
    last_ee = []

    def _handler(topic: str, raw: bytes) -> None:
        received_topic.append(topic)
        telem = TelemetryPayload.model_validate_json(raw)  # same as TelemetryIngest
        last_qpos.clear(); last_qpos.extend(telem.qpos)
        last_ee.clear(); last_ee.extend(telem.ee_pose)

    loop = LoopbackTransport(DEVICE)
    loop.subscribe(_handler)

    sink = DigitalTwinSink(device_id=DEVICE, transport=loop)
    env = DigitalTwinWrapper(make_env("rcs/fr3-reach-v0"), sink=sink)
    obs, info = env.reset()
    for _ in range(6):
        obs, reward, terminated, truncated, info = env.step(np.zeros(env.action_space.shape[0]))
        if terminated or truncated:
            env.reset()
    env.close()

    assert len(received_topic) > 0, "no frames delivered through loopback transport"
    assert received_topic[0] == f"robot/{DEVICE}/telemetry", received_topic[0]
    assert len(last_qpos) == 7, f"joint positions={len(last_qpos)}"
    assert len(last_ee) == 7, f"ee_pose={len(last_ee)}"
    print(f"[OK] P3.4b end-to-end loopback (frames={len(received_topic)}, "
          f"topic={received_topic[0]}, dof={len(last_qpos)})")


def main():
    register_envs()
    tests = [
        test_roster_complete,
        test_scenes_build,
        test_fr3_reset_no_collision,
        test_gym_make_and_ik,
        test_wrappers_compose,
        test_p3_3_vecenv,
        test_p3_3_vecenv_with_gripper,
        test_p3_4_twin_sink,
        test_p3_4_async_vecenv,
        test_p3_4b_twin_ingest_parse,
        test_p3_4b_end_to_end_loopback,
    ]
    for t in tests:
        _maybe_skip(t)()
    print("\nALL TESTS PASSED")


if __name__ == "__main__":
    sys.exit(main())
