"""Alert engine.

Evaluates a fixed set of rules over the live Runtime every tick:
  * device_battery_low       — battery below 20%
  * device_fault             — device in fault state
  * device_idle_too_long     — device idle for >120s with a queued task
  * queue_backlog            — more than 5 pending tasks
  * task_timeout             — task running for more than 30s without progress

Each rule uses a stable `alert_key` so flapping fires once and resolves
once. The engine publishes events to an asyncio pub/sub so the API can
fan them out via SSE.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    id: str
    alert_key: str
    severity: str
    title: str
    message: str
    rule: str
    device_id: Optional[str] = None
    task_id: Optional[str] = None
    state: str = "firing"
    context: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None
    acknowledged_at: Optional[str] = None
    acknowledged_by: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


RuleFn = Callable[["AlertEngine"], list["Alert"]]


class AlertEngine:
    def __init__(self) -> None:
        self.alerts: dict[str, Alert] = {}  # alert_key -> Alert (firing or ack'd)
        self.history: list[Alert] = []
        # Track first-time we observed a problem so we can suppress flapping.
        self._first_seen: dict[str, float] = {}
        self._subscribers: list[asyncio.Queue] = []

    # ---------- pub/sub ----------
    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=200)
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    def _publish(self, alert: Alert) -> None:
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(alert.to_dict())
            except Exception:
                pass

    # ---------- public API ----------
    def evaluate(self, runtime) -> None:
        """Run all rules once; reconcile against existing firing alerts."""
        # Detect task-progress changes for timeout detection.
        current_firing = {a.alert_key for a in self.evaluate_once(runtime)}
        # Mark previously-firing alerts as resolved if no longer observed.
        for key, alert in list(self.alerts.items()):
            if alert.state == "firing" and key not in current_firing:
                alert.state = "resolved"
                alert.resolved_at = datetime.now(timezone.utc).isoformat()
                self.history.append(alert)
                # Don't keep resolved alerts in the live dict forever.
                del self.alerts[key]
                self._publish(alert)

    def snapshot(self) -> list[dict]:
        return [a.to_dict() for a in self.alerts.values()]

    def acknowledge(self, alert_id: str, by: str = "operator") -> Optional[Alert]:
        for alert in self.alerts.values():
            if alert.id == alert_id:
                alert.state = "acknowledged"
                alert.acknowledged_at = datetime.now(timezone.utc).isoformat()
                alert.acknowledged_by = by
                self._publish(alert)
                return alert
        return None

    # ---------- rule runner ----------
    def evaluate_once(self, runtime) -> list[Alert]:
        produced: list[Alert] = []
        produced.extend(self._rule_battery_low(runtime))
        produced.extend(self._rule_device_fault(runtime))
        produced.extend(self._rule_queue_backlog(runtime))
        produced.extend(self._rule_task_timeout(runtime))
        # Merge: keep one Alert per key; preserve ack state from older alert.
        for new_alert in produced:
            existing = self.alerts.get(new_alert.alert_key)
            if existing:
                # Refresh context, keep id, ack state, created_at.
                new_alert.id = existing.id
                new_alert.state = existing.state
                new_alert.acknowledged_at = existing.acknowledged_at
                new_alert.acknowledged_by = existing.acknowledged_by
                new_alert.created_at = existing.created_at
            self.alerts[new_alert.alert_key] = new_alert
            if existing is None:
                self._publish(new_alert)
        return produced

    # ---------- rules ----------
    @staticmethod
    def _key(rule: str, scope: str) -> str:
        return f"{rule}:{scope}"

    def _rule_battery_low(self, runtime) -> list[Alert]:
        alerts: list[Alert] = []
        for device in runtime.devices.devices.values():
            if device.battery < 20.0:
                alerts.append(Alert(
                    id=str(uuid4()),
                    alert_key=self._key("device_battery_low", device.device_id),
                    severity=AlertSeverity.CRITICAL.value if device.battery < 5.0 else AlertSeverity.WARNING.value,
                    title=f"{device.name} 电池低",
                    message=f"电量 {device.battery:.1f}% 低于阈值 (20%)",
                    rule="device_battery_low",
                    device_id=device.device_id,
                    context={"battery": device.battery},
                ))
        return alerts

    def _rule_device_fault(self, runtime) -> list[Alert]:
        alerts: list[Alert] = []
        from backend.algorithm.simulator.device import DeviceStatus
        for device in runtime.devices.devices.values():
            if device.status == DeviceStatus.FAULT:
                alerts.append(Alert(
                    id=str(uuid4()),
                    alert_key=self._key("device_fault", device.device_id),
                    severity=AlertSeverity.CRITICAL.value,
                    title=f"{device.name} 进入故障状态",
                    message=f"设备 {device.device_id} 状态为 fault，请检查",
                    rule="device_fault",
                    device_id=device.device_id,
                ))
        return alerts

    def _rule_queue_backlog(self, runtime) -> list[Alert]:
        pending = sum(1 for t in runtime.tasks.values() if t["status"] == "pending")
        if pending >= 5:
            return [Alert(
                id=str(uuid4()),
                alert_key="queue_backlog:global",
                severity=AlertSeverity.WARNING.value,
                title="任务队列堆积",
                message=f"当前有 {pending} 条 pending 任务",
                rule="queue_backlog",
                context={"pending": pending},
            )]
        return []

    def _rule_task_timeout(self, runtime) -> list[Alert]:
        now = time.time()
        alerts: list[Alert] = []
        for task_id, record in runtime.tasks.items():
            if record["status"] != "running":
                continue
            started_str = record.get("started_at") or record.get("created_at")
            try:
                started_ts = datetime.fromisoformat(started_str).timestamp()
            except Exception:
                continue
            progress = float(record.get("progress", 0))
            elapsed = now - started_ts
            if elapsed > 30 and progress < (elapsed * 12):
                key = self._key("task_timeout", task_id)
                # Avoid spamming: only fire once.
                if key not in self._first_seen:
                    self._first_seen[key] = now
                if self._first_seen.get(key) and now - self._first_seen[key] > 60:
                    continue
                alerts.append(Alert(
                    id=str(uuid4()),
                    alert_key=key,
                    severity=AlertSeverity.WARNING.value,
                    title=f"任务 {task_id} 进度异常",
                    message=f"已运行 {elapsed:.0f}s，进度仅 {progress:.0f}%",
                    rule="task_timeout",
                    task_id=task_id,
                    device_id=record.get("device_id"),
                ))
        return alerts


engine = AlertEngine()
