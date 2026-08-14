"""In-memory business runtime used by the prototype API."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import asyncio
import time
from typing import Any
from uuid import uuid4

from backend.algorithm.scheduler.scheduler import TaskScheduler
from backend.algorithm.scheduler.task import Task, TaskPriority
from backend.algorithm.simulator.device_manager import DeviceManager
from backend.algorithm.simulator.site_manager import SiteManager, Site
from backend.algorithm.simulator.point_cloud_gen import PointCloudGenerator
from backend.algorithm.simulator.laser_scan_gen import LaserScanGenerator


class Runtime:
    def __init__(self) -> None:
        self.devices = DeviceManager()
        self.scheduler = TaskScheduler()
        self.sites = SiteManager()
        self.tasks: dict[str, dict[str, Any]] = {}
        self.logs: list[dict[str, Any]] = []
        self.reverted_tasks: dict[str, dict[str, Any]] = {}
        self.started_at: float | None = None
        self.running = False
        self.current_scene: str | None = None
        # observability: pub/sub for SSE consumers
        self._subscribers: list[asyncio.AbstractEventLoop] = []
        self._last_log_index = 0
        # joint state cache: device_id -> latest joint data dict
        self._joint_cache: dict[str, dict[str, Any]] = {}
        # synthetic sensor generators
        self._pc_gen = PointCloudGenerator()
        self._scan_gen = LaserScanGenerator()
        self._detections: dict[str, list] = {}
        self._nav_paths: dict[str, dict[str, Any]] = {}
        self._seed_tasks()

    def _seed_tasks(self) -> None:
        self.create_task("dock_loading", "container unload", TaskPriority.HIGH, "robot-01")
        self.create_task("agv_transport", "warehouse move", TaskPriority.NORMAL, "agv-01")
        self.create_task("warehouse_storage", "putaway", TaskPriority.NORMAL, "stacker-01")

    def create_task(self, task_type: str, description: str, priority: TaskPriority, device_id: str) -> dict[str, Any]:
        task_id = f"task-{uuid4().hex[:8]}"
        task = Task(task_id, task_type, priority)
        self.scheduler.add_task(task)
        record = {
            "task_id": task_id,
            "type": task_type,
            "description": description,
            "priority": int(priority),
            "status": "pending",
            "device_id": device_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "trace_id": self.trace_id(),
        }
        self.tasks[task_id] = record
        self.log(record["trace_id"], task_id, "task", f"created: {task_type}")
        return record

    def reset(self) -> None:
        """Clear runtime state without touching the synthetic sensor generators.

        - Wipe devices (next load_scene will re-seed).
        - Wipe sites, tasks, logs, reverted tasks.
        - Reset started_at; keep running flag as-is.
        - Drop any cached sensor / joint state.
        """
        self.devices = DeviceManager(seed_devices=[])
        self.sites = SiteManager(seed=False)
        self.tasks.clear()
        self.logs.clear()
        self.reverted_tasks.clear()
        self._detections.clear()
        self._nav_paths.clear()
        self._joint_cache.clear()
        self.started_at = None
        self.log(self.trace_id(), None, "runtime", "reset")

    def load_scene(self, name: str) -> dict[str, Any]:
        """Apply a scene preset: reset runtime then register preset sites / devices / tasks."""
        from backend.services.scene_presets import get_scene

        preset = get_scene(name)  # raises KeyError for unknown scenes
        self.reset()
        # Register sites
        for site_spec in preset["sites"]:
            self.sites.add(site_spec)
        # Register devices
        for device_spec in preset["devices"]:
            self.devices.add(device_spec)
        # Create tasks
        for task_spec in preset["tasks"]:
            try:
                priority = TaskPriority(task_spec["priority"])
            except ValueError:
                priority = TaskPriority.NORMAL
            self.create_task(
                task_spec["type"],
                task_spec["description"],
                priority,
                task_spec["device_id"],
            )
        self.current_scene = name
        self.log(self.trace_id(), None, "scene_presets", f"loaded scene {name!r}")
        return {
            "scene": name,
            "devices": self.devices.list(),
            "sites": self.sites.list(),
        }

    def start(self) -> dict[str, Any]:
        self.running = True
        self.started_at = self.started_at or time.time()
        for task in self.scheduler.get_next_batch():
            self._start_task(task.task_id)
        self.log(self.trace_id(), None, "simulation", "simulation started")
        return self.status()

    def stop(self) -> dict[str, Any]:
        self.running = False
        self.log(self.trace_id(), None, "simulation", "simulation stopped")
        return self.status()

    def tick(self, seconds: float = 0.5) -> None:
        if not self.running:
            return
        self.devices.tick(seconds)
        for task_id, record in self.tasks.items():
            if record["status"] != "running":
                continue
            record["progress"] = min(100, record.get("progress", 0) + seconds * 12)
            if record["progress"] >= 100:
                record["status"] = "completed"
                self.scheduler.mark_completed(task_id)
                self.log(record["trace_id"], task_id, "task", "completed")
        for task in self.scheduler.get_next_batch():
            self._start_task(task.task_id)
        # Generate synthetic sensor data for each device
        boxes = self._get_scene_boxes()
        for device_id, device in self.devices.devices.items():
            pc_data = self._pc_gen.generate(device.position, 0.0, boxes)
            self._detections[device_id] = pc_data.get("ground_truth", [])

    def _start_task(self, task_id: str) -> None:
        record = self.tasks[task_id]
        if record["status"] != "pending":
            return
        record["status"] = "running"
        record["progress"] = 0
        device = self.devices.get(record["device_id"])
        # Snapshot device state before executing so we can roll back.
        record["snapshot"] = {
            "position": list(device.position),
            "battery": device.battery,
            "status": device.status.value,
            "route": [list(point) for point in device.route],
        }
        start = device.position
        route = [start, [0.0, 0.0, 0.0], [5.0, 0.0, 2.0]]
        device.start(task_id, route)
        self.log(record["trace_id"], task_id, "scheduler", f"assigned to {device.device_id}")

    def rollback_task(self, task_id: str) -> dict[str, Any]:
        """Revert a completed task and restore device state from snapshot."""
        record = self.tasks.get(task_id)
        if record is None:
            raise KeyError(task_id)
        if record["status"] not in ("completed", "failed"):
            raise RuntimeError(f"task {task_id} is {record['status']!r}; only terminal tasks can be rolled back")
        snapshot = record.get("snapshot")
        device = self.devices.get(record["device_id"])
        if snapshot:
            device.position = list(snapshot["position"])
            device.battery = float(snapshot["battery"])
            device.status = snapshot["status"]
            device.route = [list(point) for point in snapshot["route"]]
            device.current_task = None
            device.progress = 0.0
        record["status"] = "reverted"
        record["rolled_back_at"] = datetime.now(timezone.utc).isoformat()
        self.reverted_tasks[task_id] = {
            "task": dict(record),
            "device_id": record["device_id"],
            "rolled_back_at": record["rolled_back_at"],
        }
        self.log(record["trace_id"], task_id, "rollback", f"task {task_id} reverted")
        return self.reverted_tasks[task_id]

    def rollback_recent(self, limit: int = 5) -> list[dict[str, Any]]:
        rolled_back: list[dict[str, Any]] = []
        terminal = [r for r in self.tasks.values() if r["status"] in ("completed", "failed")]
        terminal.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        for record in terminal[:limit]:
            try:
                rolled_back.append(self.rollback_task(record["task_id"]))
            except (KeyError, RuntimeError):
                continue
        return rolled_back

    def rollback_devices(self, device_ids: list[str], limit_per_device: int = 5) -> dict[str, Any]:
        """Roll back up to N terminal tasks per device in a single call."""
        results: list[dict[str, Any]] = []
        per_device_done: dict[str, int] = {d: 0 for d in device_ids}
        terminal = [r for r in self.tasks.values() if r["status"] in ("completed", "failed")]
        terminal.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        for record in terminal:
            dev = record["device_id"]
            if dev not in per_device_done:
                continue
            if per_device_done[dev] >= limit_per_device:
                continue
            try:
                results.append(self.rollback_task(record["task_id"]))
                per_device_done[dev] += 1
            except (KeyError, RuntimeError):
                continue
        return {
            "rolled_back": results,
            "per_device_done": per_device_done,
            "total": len(results),
        }

    def status(self) -> dict[str, Any]:
        return {
            "running": self.running,
            "uptime_seconds": round(time.time() - self.started_at, 1) if self.started_at else 0,
            "device_count": len(self.devices.devices),
            "task_count": len(self.tasks),
        }

    def metrics(self) -> dict[str, Any]:
        tasks = list(self.tasks.values())
        completed = sum(item["status"] == "completed" for item in tasks)
        running = sum(item["status"] == "running" for item in tasks)
        return {
            "throughput_per_hour": 42 + completed * 3,
            "success_rate": round(completed / len(tasks) * 100, 1) if tasks else 100,
            "active_tasks": running,
            "energy_kwh": round(sum(100 - device.battery for device in self.devices.devices.values()) * 0.02, 2),
        }

    def stats(self) -> dict[str, Any]:
        """Detailed per-status / per-type task counts plus uptime."""
        tasks = list(self.tasks.values())
        by_status: dict[str, int] = {}
        by_type: dict[str, int] = {}
        for t in tasks:
            by_status[t["status"]] = by_status.get(t["status"], 0) + 1
            by_type[t["type"]] = by_type.get(t["type"], 0) + 1
        per_device_battery = {
            d.device_id: round(d.battery, 1) for d in self.devices.devices.values()
        }
        return {
            "by_status": by_status,
            "by_type": by_type,
            "per_device_battery": per_device_battery,
            "uptime_seconds": round(time.time() - self.started_at, 1) if self.started_at else 0,
            "running": self.running,
            "reverted_count": len(self.reverted_tasks),
        }

    def _scene_kpi(self, name: str) -> dict[str, Any]:
        """Compute scene-specific KPI snapshot (used by /api/scenes/{name}/kpi)."""
        tasks = list(self.tasks.values())
        completed = sum(t["status"] == "completed" for t in tasks)
        failed = sum(t["status"] == "failed" for t in tasks)
        total = len(tasks) or 1
        success_rate = round((completed / total) * 100, 1)
        throughput_per_hour = 42 + completed * 3  # 沿用 metrics() 的占位算法
        return {
            "scene": name,
            "throughput_per_hour": throughput_per_hour,
            "success_rate": success_rate,
            "active_tasks": sum(1 for t in tasks if t["status"] == "running"),
            "completed_tasks": completed,
            "failed_tasks": failed,
        }

    @staticmethod
    def trace_id() -> str:
        return f"{datetime.now().strftime('%Y%m%d-%H%M')}-{uuid4().hex[:8]}"

    def log(self, trace_id: str, task_id: str | None, module: str, message: str) -> dict[str, Any]:
        entry = {
            "trace_id": trace_id,
            "task_id": task_id,
            "module": module,
            "message": message,
            "level": "INFO",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.logs.append(entry)
        self.logs = self.logs[-500:]
        # notify SSE listeners (best-effort; ignore if no loop)
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(entry)
            except Exception:
                pass
        return entry

    def subscribe(self) -> "asyncio.Queue[dict[str, Any]]":
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=200)
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    # --- joint state cache --------------------------------------------------

    def update_joint_state(self, device_id: str, data: dict[str, Any]) -> None:
        """Store latest joint state from MQTT for SSE consumers."""
        self._joint_cache[device_id] = data

    def get_joint_state(self, device_id: str) -> dict[str, Any] | None:
        """Retrieve cached joint state for a device."""
        return self._joint_cache.get(device_id)

    # --- task state machine -------------------------------------------------

    _VALID_TRANSITIONS: dict[str, set[str]] = {
        "pending": {"command_sent", "failed"},
        "command_sent": {"running", "failed"},
        "running": {"completed", "failed"},
    }

    def _transition(self, task_id: str, new_status: str, reason: str = "") -> None:
        record = self.tasks[task_id]
        old = record["status"]
        allowed = self._VALID_TRANSITIONS.get(old, set())
        if new_status not in allowed:
            raise RuntimeError(
                f"task {task_id}: cannot transition {old!r} → {new_status!r}"
            )
        record["status"] = new_status
        if reason:
            record["status_reason"] = reason
        self.log(self.trace_id(), task_id, "state_machine", f"{old} → {new_status} {reason}")

    def advance_task(self, task_id: str, new_status: str) -> None:
        """Advance task to the next valid state."""
        self._transition(task_id, new_status)

    def complete_task(self, task_id: str) -> None:
        """Mark task as completed (only valid from 'running')."""
        self._transition(task_id, "completed")
        self.scheduler.mark_completed(task_id)

    def fail_task(self, task_id: str, reason: str) -> None:
        """Mark task as failed from any non-terminal state."""
        self._transition(task_id, "failed", reason)

    # --- synthetic sensor data ------------------------------------------------

    def _get_scene_boxes(self) -> list[dict[str, Any]]:
        """Convert warehouse sites to box list for point cloud generation."""
        boxes: list[dict[str, Any]] = []
        for site in self.sites.list():
            if site["kind"] == "warehouse":
                boxes.append({
                    "id": site["id"],
                    "position": site["position"],
                    "size": [site["width"], site["depth"], site["height"]],
                })
        return boxes

    def get_detections(self, device_id: str) -> list:
        """Retrieve latest detection data for a device."""
        return self._detections.get(device_id, [])

    def get_nav_path(self, device_id: str) -> dict[str, Any]:
        """Retrieve latest navigation path for a device."""
        return self._nav_paths.get(device_id, {})

    def update_nav_path(self, device_id: str, path: dict[str, Any]) -> None:
        """Store a navigation path for SSE consumers."""
        self._nav_paths[device_id] = path


runtime = Runtime()
