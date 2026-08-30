"""Digital-twin telemetry bridge for :mod:`rcs_env` (P3.4).

The :class:`~rcs_env.envs.wrappers.DigitalTwinWrapper` attaches a
``info["digital_twin"]`` record (robot_type / qpos / ee_pose / gripper_state) to
every step. This module turns those records into **wire-format telemetry for the
real RCS device backend**:

    robot/{device_id}/telemetry   (QoS 0, uplink, robot-app -> RCS)

The transport is injectable so the sim stack stays dependency-light (no MQTT /
pydantic required for training):

* :class:`InMemoryTransport` — ring buffer, used by tests and headless runs.
* :class:`LoopbackTransport` — in-process pub/sub used when no broker is running
  (validates the full serialize -> topic -> parse pipeline without a network).
* :class:`MqttTransport` — lazily imports the canonical ``robot_contracts``
  (root ``shared/python/robot_contracts``: pydantic ``TelemetryPayload``) and
  ``paho.mqtt`` only when first used, then publishes on the contract topic.
  Drop-in for the real RCS telemetry consumer.

Usage::

    sink = DigitalTwinSink(device_id="fr3-01", transport=InMemoryTransport())
    env = DigitalTwinWrapper(make_env("rcs/fr3-reach-v0"), sink=sink)
    # ... train ...
    sink.flush()  # or push every step automatically
"""
from __future__ import annotations

import os
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Sequence

import numpy as np


@dataclass
class TwinRecord:
    """A single digital-twin sample (one env step)."""

    robot_type: str = "arm"
    qpos: list[float] = field(default_factory=list)
    qvel: list[float] = field(default_factory=list)
    ee_pose: list[float] | None = None  # [x,y,z, qw,qx,qy,qz]
    gripper_state: float | None = None
    sim_time: float = 0.0
    episode: int = 0
    step: int = 0
    timestamp_ns: int = 0

    @classmethod
    def from_info(cls, rec: dict) -> "TwinRecord":
        return cls(
            robot_type=str(rec.get("robot_type", "arm")),
            qpos=list(rec.get("qpos", []) or []),
            qvel=[float(x) for x in (rec.get("qvel") or [])],
            ee_pose=list(rec["ee_pose"]) if rec.get("ee_pose") else None,
            gripper_state=rec.get("gripper_state"),
            sim_time=float(rec.get("sim_time", 0.0) or 0.0),
            episode=int(rec.get("episode", 0) or 0),
            step=int(rec.get("step", 0) or 0),
            timestamp_ns=rec.get("timestamp_ns", 0) or 0,
        )


class Transport:
    """Protocol for pushing a :class:`TwinRecord` to the real backend."""

    def publish(self, record: TwinRecord) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def close(self) -> None:  # pragma: no cover - interface
        pass


class InMemoryTransport(Transport):
    """In-process ring buffer (default; no external broker needed)."""

    def __init__(self, maxlen: int = 1024) -> None:
        self._buf: deque = deque(maxlen=maxlen)

    def publish(self, record: TwinRecord) -> None:
        self._buf.append(record)

    def latest(self) -> TwinRecord | None:
        return self._buf[-1] if self._buf else None

    def all(self) -> list[TwinRecord]:
        return list(self._buf)

    def __len__(self) -> int:
        return len(self._buf)


class LoopbackTransport(Transport):
    """In-process MQTT-topic emulation for broker-less end-to-end testing.

    Mimics the contract wire path: records are serialized to a
    ``TelemetryPayload`` JSON on ``robot/{device_id}/telemetry`` and pushed to
    registered subscribers, exactly as a real broker would deliver them. This
    lets :class:`TelemetryIngest` (or any handler) be exercised without a
    running Mosquitto instance.
    """

    def __init__(self, device_id: str, prefix: str = "") -> None:
        self.device_id = device_id
        self.prefix = prefix
        self._subs: list[Callable[[str, bytes], None]] = []
        self._sent = 0

    def subscribe(self, handler: Callable[[str, bytes], None]) -> None:
        self._subs.append(handler)

    def publish(self, record: TwinRecord) -> None:
        topic, payload = _serialize_telemetry(self.device_id, self.prefix, record)
        self._sent += 1
        for h in list(self._subs):
            try:
                h(topic, payload)
            except Exception:
                pass


class MqttTransport(Transport):
    """Publish to the real RCS backend via the canonical contract.

    Dependencies (``paho.mqtt``, and the canonical ``robot_contracts`` with
    pydantic) are imported lazily so the sim venv does not need them to train.
    The canonical contract path is injected via ``contract_path`` (defaults to the
    repo-root ``shared/python`` package). ``broker_host``/``broker_port`` default
    to ``localhost:1883`` but can be overridden by the ``RCB_MQTT_HOST`` /
    ``RCB_MQTT_PORT`` environment variables.

    On connect failure the transport degrades to a no-op (logged once) so a
    broker outage never crashes a training loop.
    """

    def __init__(
        self,
        device_id: str,
        broker_host: str | None = None,
        broker_port: int | None = None,
        prefix: str = "",
        client_id: str | None = None,
        contract_path: str | None = None,
        keepalive: int = 30,
    ) -> None:
        self.device_id = device_id
        self.broker_host = broker_host or os.getenv("RCB_MQTT_HOST", "localhost")
        self.broker_port = int(broker_port if broker_port is not None else os.getenv("RCB_MQTT_PORT", "1883"))
        self.prefix = prefix
        self.client_id = client_id or f"rcs-sim-{device_id}"
        self._contract_path = contract_path
        self._keepalive = keepalive
        self._client = None
        self._rc = None
        self._disabled = False

    def _ensure(self):
        if self._client is not None or self._disabled:
            return
        try:
            import paho.mqtt.client as mqtt  # lazy
            # Inject canonical contract path ahead of the sim-side stub so that
            # `import robot_contracts` resolves to the pydantic payload definitions.
            import sys
            cp = self._contract_path or _contract_path_for(None)
            if cp and cp not in sys.path:
                sys.path.insert(0, cp)
            # Drop any cached stub (numpy-only sim-side package) so the canonical
            # pydantic contract wins for this import.
            sys.modules.pop("robot_contracts", None)
            for _m in list(sys.modules):
                if _m.startswith("robot_contracts."):
                    sys.modules.pop(_m, None)
            from robot_contracts import TelemetryPayload  # canonical
            from robot_contracts.topics import telemetry_topic

            self._rc = {
                "TelemetryPayload": TelemetryPayload,
                "telemetry_topic": telemetry_topic,
            }
            self._client = mqtt.Client(client_id=self.client_id, clean_session=True)
            self._client.on_connect = self._on_connect
            self._client.on_disconnect = self._on_disconnect
            # Blocking connect: raises (→ self._disabled) immediately when no broker
            # is reachable, so publish() can never falsely report "sent to broker".
            self._client.connect(self.broker_host, self.broker_port, self._keepalive)
            self._client.loop_start()
        except Exception as exc:  # pragma: no cover - network/broker dependent
            self._disabled = True
            _log_once(f"MqttTransport disabled (broker {self.broker_host}:{self.broker_port} unavailable): {exc}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc != 0:  # pragma: no cover - broker dependent
            self._disabled = True
            _log_once(f"MqttTransport connect refused rc={rc}")

    def _on_disconnect(self, client, userdata, rc):  # pragma: no cover - broker dependent
        if rc != 0:
            _log_once("MqttTransport disconnected; will retry via reconnect")

    def publish(self, record: TwinRecord) -> None:
        self._ensure()
        if self._client is None or self._disabled or not self._client.is_connected():
            return
        topic, payload = _serialize_telemetry(self.device_id, self.prefix, record)
        # Best-effort: a broker outage must not crash the training loop.
        try:
            info = self._client.publish(topic, payload, qos=0)
            if info.rc != 0:  # pragma: no cover - broker dependent
                _log_once(f"MqttTransport publish failed rc={info.rc}")
        except Exception as exc:  # pragma: no cover - broker dependent
            _log_once(f"MqttTransport publish error: {exc}")

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass


def _serialize_telemetry(device_id: str, prefix: str, record: TwinRecord):
    """Build the (topic, json-bytes) for a :class:`TelemetryPayload`.

    The canonical contract is the single source of truth for the wire format,
    so we always go through ``robot_contracts.TelemetryPayload`` when available.
    A tiny fallback payload keeps headless tests working without pydantic.
    """
    ts = record.timestamp_ns or time.time_ns()
    iso = _iso(ts)
    # metrics holds only scalars (battery, temp, gripper %...); pose arrays live in
    # the dedicated twin fields so the canonical TelemetryPayload validates.
    metrics = {}
    if record.gripper_state is not None:
        metrics["gripper_state"] = float(record.gripper_state)
    status = {"robot_type": record.robot_type, "episode": str(record.episode), "step": str(record.step)}
    try:
        if _contract_path_for(None) is not None:
            import sys
            cp = _contract_path_for(None)
            if cp and cp not in sys.path:
                sys.path.insert(0, cp)
            # Drop any cached stub (numpy-only sim-side package) so the canonical
            # pydantic contract wins for this import.
            sys.modules.pop("robot_contracts", None)
            for _m in list(sys.modules):
                if _m.startswith("robot_contracts."):
                    sys.modules.pop(_m, None)
        from robot_contracts import TelemetryPayload
        from robot_contracts.topics import telemetry_topic

        telem = TelemetryPayload(
            device_id=device_id,
            iso_ts=iso,
            metrics=metrics,
            status=status,
            robot_type=record.robot_type,
            qpos=[float(x) for x in record.qpos],
            qvel=[float(x) for x in record.qvel],
            ee_pose=list(record.ee_pose) if record.ee_pose else [],
            sim_time=float(record.sim_time),
            episode=int(record.episode),
            step=int(record.step),
        )
        payload = telem.model_dump_json().encode()
        topic = telemetry_topic(device_id, prefix)
    except Exception:
        # Fallback: minimal JSON that the backend can still route by topic.
        import json

        topic = f"{prefix + '/' if prefix else ''}robot/{device_id}/telemetry"
        payload = json.dumps(
            {
                "device_id": device_id,
                "iso_ts": iso,
                "metrics": metrics,
                "status": status,
                "robot_type": record.robot_type,
                "qpos": [float(x) for x in record.qpos],
                "qvel": [float(x) for x in record.qvel],
                "ee_pose": list(record.ee_pose) if record.ee_pose else [],
                "sim_time": float(record.sim_time),
                "episode": int(record.episode),
                "step": int(record.step),
            }
        ).encode()
    return topic, payload


_CONTRACT_PATH_CACHE = None


def _contract_path_for(contract_path: str | None) -> str | None:
    global _CONTRACT_PATH_CACHE
    if contract_path is not None:
        return contract_path
    if _CONTRACT_PATH_CACHE is None:
        # Repo-root shared/python is the canonical contract package.
        here = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.normpath(os.path.join(here, "..", "..", "..", "..", "shared", "python"))
        _CONTRACT_PATH_CACHE = candidate if os.path.isdir(os.path.join(candidate, "robot_contracts")) else None
    return _CONTRACT_PATH_CACHE


def _iso(ts_ns: int) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(ts_ns / 1e9, tz=timezone.utc).isoformat()


_LOG_STATE: dict[str, bool] = {}


def _log_once(msg: str) -> None:
    import logging

    if msg in _LOG_STATE:
        return
    _LOG_STATE[msg] = True
    logging.getLogger(__name__).warning(msg)


class DigitalTwinSink:
    """Collects ``info["digital_twin"]`` records and forwards them to a transport.

    Attach to :class:`DigitalTwinWrapper` via ``sink=`` so every step is pushed
    automatically, or call :meth:`push` from a training loop. ``rate`` limits how
    many steps-per-second are emitted (0 = every step).

    If ``device_id`` is omitted it is auto-derived from the wrapped env's
    ``unwrapped`` ``device_id`` / ``robot_type`` when available.
    """

    def __init__(
        self,
        device_id: str | None = None,
        transport: Transport | None = None,
        rate: int = 0,
        push_history: int = 1,
        env=None,
    ) -> None:
        if device_id is None and env is not None:
            device_id = _infer_device_id(env)
        self.device_id = device_id or "sim-twin"
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


def _infer_device_id(env) -> str | None:
    simenv = getattr(env, "unwrapped", env)
    for attr in ("device_id", "robot_id"):
        val = getattr(simenv, attr, None)
        if val:
            return str(val)
    cfg = getattr(simenv, "config", None)
    rt = getattr(cfg, "robot_type", None)
    if rt is not None:
        return f"{getattr(rt, 'value', str(rt))}-twin"
    return None


__all__ = [
    "TwinRecord",
    "Transport",
    "InMemoryTransport",
    "LoopbackTransport",
    "MqttTransport",
    "DigitalTwinSink",
    "_serialize_telemetry",
]
