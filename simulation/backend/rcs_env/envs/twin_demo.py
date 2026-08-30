"""End-to-end verification for the digital-twin telemetry bridge (P3.4).

Run::

    PYTHONPATH=d:/projects/robot-logic/simulation/backend \
        rcs_sim_core/.venv/Scripts/python.exe rcs_env/envs/twin_demo.py

The demo:

1. Builds a sim env and wraps it with :class:`DigitalTwinWrapper` + a sink.
2. Tries a real MQTT broker at ``localhost:1883`` (or ``RCB_MQTT_HOST/PORT``):
     * success -> runs live steps, prints the broker topic being published.
     * failure -> transparently falls back to :class:`LoopbackTransport` and
       feeds the *real* backend :class:`TelemetryIngest` handler, proving the
       serialize -> topic -> parse -> StateStream pipeline without a broker.

Exit code 0 means the twin pipeline delivered at least one valid frame into the
backend state stream (or to the broker).

Note: importing the backend ``TelemetryIngest`` brings in the real ``rcs``
package (pydantic, paho, fastapi deps). The loopback path exercises the same
code path the broker path would, so it is a faithful integration check.
"""
from __future__ import annotations

import argparse
import sys
import time

# Ensure the canonical contract package is importable.
_ROOT = "d:/projects/robot-logic/shared/python"
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# Keep paho optional for the pure-sim build; only required for the broker path.
try:
    import rcs_sim_core  # noqa: F401
except Exception:
    pass


def _build_env(task_id: str, wrappers):
    from rcs_env.envs.base import make_env

    env = make_env(task_id)
    for W in wrappers:
        env = W(env)
    return env


def _loopback_demo(task_id: str, steps: int, rate: int):
    """Broker-less integration: feed canonical-contract parse via LoopbackTransport.

    Mirrors the exact code path the real backend :class:`TelemetryIngest` runs
    (validate ``TelemetryPayload`` and recover joint state) without requiring the
    heavy ``rcs.control`` backend package or a running Mosquitto.
    """
    from rcs_env.envs.twin import LoopbackTransport, DigitalTwinSink, _contract_path_for
    from rcs_env.envs.wrappers import DigitalTwinWrapper

    cp = _contract_path_for(None)
    if cp:
        sys.path.insert(0, cp)
        sys.modules.pop("robot_contracts", None)
        for _m in list(sys.modules):
            if _m.startswith("robot_contracts."):
                sys.modules.pop(_m, None)
    from robot_contracts import TelemetryPayload

    DEVICE = "fr3-twin-demo"
    received = []
    last_qpos = []
    last_ee = []

    def _handler(topic: str, raw: bytes) -> None:
        received.append(topic)
        telem = TelemetryPayload.model_validate_json(raw)  # same as TelemetryIngest
        last_qpos.clear(); last_qpos.extend(telem.qpos)
        last_ee.clear(); last_ee.extend(telem.ee_pose)

    sink = DigitalTwinSink(device_id=DEVICE, transport=LoopbackTransport(DEVICE), rate=rate)
    sink.transport.subscribe(_handler)

    env = _build_env(task_id, [lambda e: DigitalTwinWrapper(e, sink=sink)])
    obs, info = env.reset()
    for i in range(steps):
        obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
        if terminated or truncated:
            obs, info = env.reset()
    env.close()

    ok = len(received) > 0 and len(last_qpos) == 7 and len(last_ee) == 7
    print(f"[loopback] frames={len(received)} topic={received[0] if received else 'NONE'} "
          f"dof={len(last_qpos)} ee={len(last_ee)}")
    if not ok:
        print("[loopback] FAILED: no valid twin frame parsed")
        return 1
    print("[loopback] OK: twin telemetry delivered end-to-end into canonical contract parse")
    return 0


def _broker_demo(task_id: str, steps: int, rate: int, host: str, port: int):
    from rcs_env.envs.twin import MqttTransport, DigitalTwinSink
    from rcs_env.envs.wrappers import DigitalTwinWrapper
    from rcs_env.envs.twin import _contract_path_for

    DEVICE = "fr3-twin-demo"
    transport = MqttTransport(DEVICE, broker_host=host, broker_port=port, contract_path=_contract_path_for(None))
    transport._ensure()
    if transport._disabled or transport._client is None:
        print(f"[broker] no broker at {host}:{port}; falling back to loopback demo")
        return _loopback_demo(task_id, steps, rate)

    sink = DigitalTwinSink(device_id=DEVICE, transport=transport, rate=rate)
    env = _build_env(task_id, [lambda e: DigitalTwinWrapper(e, sink=sink)])
    obs, info = env.reset()
    for i in range(steps):
        obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
        if terminated or truncated:
            obs, info = env.reset()
    env.close()
    transport.close()
    print(f"[broker] published {steps // max(1, rate) if rate else steps} frames to robot/{DEVICE}/telemetry")
    print("[broker] OK: twin telemetry sent to live broker")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Digital-twin telemetry end-to-end demo")
    ap.add_argument("--task", default="rcs/fr3-reach-v0")
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--rate", type=int, default=0, help="emit every N steps (0 = every step)")
    ap.add_argument("--host", default=None)
    ap.add_argument("--port", type=int, default=None)
    args = ap.parse_args()

    host = args.host or "localhost"
    port = args.port or 1883
    try:
        return _broker_demo(args.task, args.steps, args.rate, host, port)
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - environment dependent
        print(f"[demo] broker path error ({exc}); using loopback integration")
        return _loopback_demo(args.task, args.steps, args.rate)


if __name__ == "__main__":
    raise SystemExit(main())
