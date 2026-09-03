"""Digital-twin telemetry + run-length tests for Microduck (P4 T4)."""
import numpy as np

from rcs_env.envs.microduck import MicroduckEnv
from rcs_env.envs.twin import DigitalTwinSink, InMemoryTransport
from rcs_env.envs.wrappers import DigitalTwinWrapper


def test_env_emits_digital_twin_record():
    """Every reset/step stamps a digital-twin record pushed to the sink."""
    env = DigitalTwinWrapper(MicroduckEnv(variant="walk"), history=1)
    transport = InMemoryTransport()
    sink = DigitalTwinSink(device_id="microduck-01", transport=transport, rate=0)
    env.sink = sink
    obs, info = env.reset(seed=0)
    assert "digital_twin" in info
    assert len(info["digital_twin"]) == 1
    rec0 = info["digital_twin"][0]
    assert rec0["robot_type"] == "microduck"
    assert len(rec0["qpos"]) == 21
    n0 = len(transport)
    assert n0 >= 1
    env.step(env.action_space.sample())
    assert len(transport) > n0
    env.close()


def test_digital_twin_history_window():
    """history=1 keeps exactly the most recent record per info dict."""
    env = DigitalTwinWrapper(MicroduckEnv(variant="walk"), history=1)
    obs, info = env.reset(seed=0)
    recs = info["digital_twin"]
    for _ in range(3):
        obs, reward, term, trunc, info = env.step(env.action_space.sample())
        recs = info["digital_twin"]
    assert len(recs) == 1
    env.close()


def test_run_len_wraps_to_one():
    """_n_steps counts control steps and resets to 1 on env.reset (spec §7.1)."""
    env = MicroduckEnv(variant="walk")
    obs, _ = env.reset(seed=0)
    assert env._n_steps == 1
    for _ in range(2):
        env.step(env.action_space.sample())
    assert env._n_steps == 3
    obs, _ = env.reset(seed=1)
    assert env._n_steps == 1
    env.close()
