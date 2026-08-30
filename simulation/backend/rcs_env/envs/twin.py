"""Digital-twin telemetry bridge for :mod:`rcs_env` (P3.4).

The :class:`~rcs_env.envs.wrappers.DigitalTwinWrapper` attaches a
``info["digital_twin"]`` record (robot_type / qpos / ee_pose / gripper_state) to
every step. This module turns those records into **wire-format telemetry for the
real RCS device backend**:

    robot/{device_id}/telemetry   (QoS 0, uplink, robot-app -> RCS)

The transport is injectable so the sim stack stays dependency-light (no MQTT /
pydantic required for training):

* :class:`InMemoryTransport` — ring buffer, used by tests and headless runs.
* :class:`MqttTransport` — lazily imports the canonical ``robot_contracts``
  (root ``shared/python/robot_contracts``: pydantic ``JointStatePayload`` +
  ``TelemetryPayload``) and ``paho.mqtt`` only when first used, then publishes on
  the contract topic. Drop-in for the real RCS telemetry consumer.

Usage::

    sink = DigitalTwinSink(device_id="fr3-01", transport=InMemoryTransport())
    env = DigitalTwinWrapper(make_env("rcs/fr3-reach-v0"), sink=sink)
    # ... train ...
    sink.flush()  # or push every step automatically
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Sequence

import numpy as np


@dataclass
class TwinRecord:
    """A single digital-twin sample (one env step)."""

    robot_type: str = "arm"
    qpos: list[float] = field(default_factory=list)
    ee_pose: list[float] | None = None  # [x,y,z, qw,qx,qy,qz]
    gripper_state: float | None = None
    timestamp_ns: int = 0

    @classmethod
    def from_info(cls, rec: dict) -> "TwinRecord":
        return cls(
            robot_type=str(rec.get("robot_type", "arm")),
            qpos=list(rec.get("qpos", []) or []),
            ee_pose=list(rec["ee_pose"]) if rec.get("ee_pose") else None,
            gripper_state=rec.get("gripper_state"),
            timestamp_ns=rec.get("timestamp_ns", 0) or 0,
        )


class Transport:
    """Protocol for pushing a :class:`TwinRecord` to the real backend."""

    def publish(self, record: TwinRecord) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class InMemoryTransport(Transport):
    """In-process ring buffer (default; no external broker needed)."""

    def __init__(self, maxlen: int = 1024) -> None:
        from collections import deque
        self._buf: deque = deque(maxlen=maxlen)

    def publish(self, record: TwinRecord) -> None:
        self._buf.append(record)

    def latest(self) -> TwinRecord | None:
        return self._buf[-1] if self._buf else None

    def all(self) -> list[TwinRecord]:
        return list(self._buf)

    def __len__(self) -> int:
        return len(self._buf)


class MqttTransport(Transport):
    """Publish to the real RCS backend via the canonical contract.

    Dependencies (``paho.mqtt``, and the canonical ``robot_contracts`` with
    pydantic) are imported lazily so the sim venv does not need them to train.
    The canonical contract path is injected via ``contract_path`` (defaults to the
    repo-root ``shared/python`` package).
    """

    def __init__(
        self,
        device_id: str,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        prefix: str = "",
        contract_path: str | None = None,
    ) -> None:
        self.device_id = device_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.prefix = prefix
        self._contract_path = contract_path
        self._client = None
        self._rc = None

    def _ensure(self):
        if self._client is not None:
            return
        import paho.mqtt.client as mqtt  # lazy
        # Inject canonical contract path ahead of the sim-side stub so that
        # `import robot_contracts` resolves to the pydantic payload definitions.
        if self._contract_path:
            import sys
            if self._contract_path not in sys.path:
                sys.path.insert(0, self._contract_path)
        from robot_contracts import JointStatePayload, TelemetryPayload  # canonical
        from robot_contracts.topics import telemetry_topic
        self._rc = {
            "JointStatePayload": JointStatePayload,
            "TelemetryPayload": TelemetryPayload,
            "telemetry_topic": telemetry_topic,
        }
        self._client = mqtt.Client()
        self._client.connect(self.broker_host, self.broker_port, keepalive=30)
        self._client.loop_start()

    def publish(self, record: TwinRecord) -> None:
        self._ensure()
        ts = record.timestamp_ns or time.time_ns()
        iso = _iso(ts)
        joint = self._rc["JointStatePayload"](
            device_id=self.device_id,
            positions=[float(x) for x in record.qpos],
            timestamp_ns=ts,
        )
        metrics = {"ee_pose": record.ee_pose} if record.ee_pose else {}
        if record.gripper_state is not None:
            metrics["gripper_state"] = float(record.gripper_state)
        telem = self._rc["TelemetryPayload"](
            device_id=self.device_id,
            iso_ts=iso,
            metrics={k: (v if isinstance(v, float) else list(v)) for k, v in metrics.items()},
            status={"robot_type": record.robot_type},
        )
        topic = self._rc["telemetry_topic"](self.device_id, self.prefix)
        # Best-effort: a broker outage must not crash the training loop.
        try:
            self._client.publish(topic, joint.model_dump_json(), qos=0)
            self._client.publish(topic, telem.model_dump_json(), qos=0)
        except Exception:
            pass

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass


def _iso(ts_ns: int) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts_ns / 1e9, tz=timezone.utc).isoformat()


class DigitalTwinSink:
    """Collects ``info["digital_twin"]`` records and forwards them to a transport.

    Attach to :class:`DigitalTwinWrapper` via ``sink=`` so every step is pushed
    automatically, or call :meth:`push` from a training loop. ``rate`` limits how
    many steps-per-second are emitted (0 = every step).
    """

    def __init__(
        self,
        device_id: str,
        transport: Transport | None = None,
        rate: int = 0,
        push_history: int = 1,
    ) -> None:
        self.device_id = device_id
        self.transport = transport if transport is not None else InMemoryTransport()
        self.rate = int(rate)
        self.push_history = max(1, int(push_history))
        self._step = 0

    def push(self, info: dict) -> None:
        recs = info.get("digital_twin")
        if not recs:
            return
        for rec in recs[-self.push_history:]:
            self._emit(TwinRecord.from_info(rec))

    def _emit(self, record: TwinRecord) -> None:
        self._step += 1
        if self.rate and (self._step % self.rate != 0):
            return
        self.transport.publish(record)

    def flush(self) -> None:
        pass  # transport handles its own buffering; hook for future batching.


__all__ = [
    "TwinRecord",
    "Transport",
    "InMemoryTransport",
    "MqttTransport",
    "DigitalTwinSink",
]
