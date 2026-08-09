# 端到端运动链路实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 打通 RCS → MQTT → robot_gateway → robot_decision (MoveIt) → controller_manager → 仿真前端可视化的完整运动命令链路。

**Architecture:** Simulation Backend 通过 paho-mqtt 与 Mosquitto broker 通信，将任务转换为运动命令下发给 robot_gateway。Gateway 将命令 JSON 序列化后通过 `std_msgs/msg/String` 发布到 `~/motion_command` topic。robot_decision 的 MotionPlannerNode 订阅该 topic，调用 MoveIt 规划轨迹，通过 `FollowJointTrajectory` action 发送到 controller_manager 执行。关节状态通过 `joint_state_broadcaster` → Decision → Gateway → MQTT → Backend → SSE → Three.js 形成闭环。

**Tech Stack:** ROS 2 (Jazzy/Humble LTS), MoveIt 2, ros2_control, paho-mqtt, FastAPI, Three.js, Vue 3, pytest

**Spec:** `docs/superpowers/specs/2026-08-09-e2e-motion-chain-design.md`

## Global Constraints

- ROS 2 发行版: Jazzy Jalisco (LTS) 或 Humble Hawksbill (LTS)
- Planning group 名称: `manipulator`（必须与 `robot.srdf` 一致）
- Action namespace: `/arm_controller/follow_joint_trajectory`
- 跨节点 topic 通信使用 `std_msgs/msg/String` + JSON 序列化
- `robot_msgs` 保持 `ament_python`，不新增 `.msg` 文件
- 前端阶段1使用程序化几何体，不使用 GLTF
- 完成判定阈值: `max_joint_error < 0.05 rad`
- `SIM_MQTT_ENABLED` 默认 `false`

---

## File Structure

### 新增文件

| 文件 | 职责 |
|---|---|
| `simulation/backend/services/mqtt_bridge.py` | 仿真后端 MQTT 适配器（paho-mqtt loop_start 线程模型） |
| `simulation/backend/services/motion_commander.py` | 任务→运动命令桥接 + 坐标转换 |
| `simulation/backend/tests/test_mqtt_bridge.py` | MQTT 桥接单元测试 |
| `simulation/backend/tests/test_motion_commander.py` | 运动命令映射 + 坐标转换测试 |
| `simulation/backend/tests/test_runtime_joints.py` | Runtime 状态机 + joint cache 测试 |
| `simulation/frontend/src/three/RobotArm.ts` | 3D 机械臂类（程序化几何体） |
| `robot_decision/robot_decision/moveit_client.py` | MoveIt MoveGroupInterface 封装 |
| `robot_decision/robot_decision/motion_planner.py` | 运动规划节点 |
| `robot_decision/config/motion_planner.yaml` | 节点参数 |
| `robot_decision/tests/test_command_conversion.py` | 命令转换测试 |
| `robot_decision/tests/test_moveit_client.py` | MoveIt 客户端测试 |

### 改动文件

| 文件 | 变更 |
|---|---|
| `simulation/backend/config.py` | 新增 MQTT 配置项 |
| `simulation/backend/requirements.txt` | 新增 paho-mqtt |
| `simulation/backend/main.py` | 新增 joints SSE 端点 |
| `simulation/backend/services/runtime.py` | 任务状态机 + joint cache |
| `simulation/frontend/src/three/WarehouseScene.vue` | 集成机械臂可视化 |
| `robot_decision/setup.py` | 添加入口点 + config data_files |
| `robot_decision/package.xml` | 添加依赖 |
| `robot_gateway/robot_gateway/mqtt_bridge_node.py` | 增强命令转发 + 状态上报 |

---

## Task 1: Simulation Backend — MQTT 配置 + 桥接

**Files:**
- Modify: `simulation/backend/config.py`
- Modify: `simulation/backend/requirements.txt`
- Create: `simulation/backend/services/mqtt_bridge.py`
- Test: `simulation/backend/tests/test_mqtt_bridge.py`

**Interfaces:**
- Consumes: `simulation/backend/config.py` settings
- Produces: `SimulationMqttBridge` class — `publish_command(topic, payload)`, `subscribe_state(topic, callback)`, `start()`, `stop()`

- [ ] **Step 1: 添加 paho-mqtt 到 requirements.txt**

在 `simulation/backend/requirements.txt` 末尾追加:

```
paho-mqtt==1.6.1
```

- [ ] **Step 2: 添加 MQTT 配置到 config.py**

在 `simulation/backend/config.py` 的 `Settings` 类中，在 `rcs_service_url` 行之后添加:

```python
    # MQTT bridge to Mosquitto (shared with RCS / robot-app).
    # Disabled by default — most dev environments don't run a broker.
    sim_mqtt_enabled: bool = False
    sim_mqtt_host: str = "127.0.0.1"
    sim_mqtt_port: int = 1883
```

- [ ] **Step 3: 编写 SimulationMqttBridge 测试**

创建 `simulation/backend/tests/test_mqtt_bridge.py`:

```python
"""Unit tests for SimulationMqttBridge — no broker required."""
import json
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from backend.services.mqtt_bridge import SimulationMqttBridge


class TestSimulationMqttBridge:
    """Tests that the bridge publishes commands and dispatches state callbacks."""

    def _make_bridge(self, enabled: bool = True) -> SimulationMqttBridge:
        bridge = SimulationMqttBridge(
            host="127.0.0.1",
            port=1883,
            enabled=enabled,
        )
        # Replace the real paho client with a mock
        bridge._client = MagicMock()
        bridge._client.publish = MagicMock(return_value=MagicMock(rc=0))
        bridge._connected = True
        return bridge

    def test_disabled_bridge_does_not_publish(self):
        bridge = SimulationMqttBridge(host="127.0.0.1", port=1883, enabled=False)
        bridge.start()
        result = bridge.publish_command("rcs/robot-01/command", {"type": "move_l"})
        assert result is False

    def test_publish_command_sends_json(self):
        bridge = self._make_bridge()
        bridge.start()
        payload = {"command_id": "cmd-1", "type": "move_l", "target_joints": []}
        ok = bridge.publish_command("rcs/robot-01/command", payload)
        assert ok is True
        bridge._client.publish.assert_called_once()
        args = bridge._client.publish.call_args
        assert args[0][0] == "rcs/robot-01/command"
        sent = json.loads(args[0][1])
        assert sent["command_id"] == "cmd-1"

    def test_state_callback_dispatched(self):
        bridge = self._make_bridge()
        received = []
        bridge.subscribe_state("rcs/robot-01/state", lambda msg: received.append(msg))
        bridge.start()
        # Simulate an incoming message
        fake_msg = MagicMock()
        fake_msg.topic = "rcs/robot-01/state"
        fake_msg.payload = json.dumps({"device_id": "robot-01", "joint": {"positions": [0.0] * 6}}).encode()
        bridge._on_message(None, None, fake_msg)
        assert len(received) == 1
        assert received[0]["device_id"] == "robot-01"

    def test_stop_disconnects(self):
        bridge = self._make_bridge()
        bridge.start()
        bridge.stop()
        bridge._client.loop_stop.assert_called_once()
        bridge._client.disconnect.assert_called_once()
```

- [ ] **Step 4: 运行测试确认失败**

Run: `cd simulation/backend && python -m pytest tests/test_mqtt_bridge.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.services.mqtt_bridge'`

- [ ] **Step 5: 实现 SimulationMqttBridge**

创建 `simulation/backend/services/mqtt_bridge.py`:

```python
"""MQTT bridge for the simulation backend.

Connects to the same Mosquitto broker used by RCS and robot-app so that
simulation tasks can flow through the real command/state pipeline.

Uses paho-mqtt ``loop_start()`` for background I/O.  State callbacks run in
the paho thread; callers that need to touch asyncio state should use
``asyncio.run_coroutine_threadsafe()``.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class SimulationMqttBridge:
    """Lightweight MQTT adapter for the simulation backend."""

    def __init__(self, *, host: str, port: int, enabled: bool = True) -> None:
        self._host = host
        self._port = port
        self._enabled = enabled
        self._client: Any = None
        self._connected = False
        self._state_callbacks: dict[str, Callable[[dict], None]] = {}

    # --- lifecycle ----------------------------------------------------------

    def start(self) -> None:
        if not self._enabled:
            logger.info("MQTT bridge disabled")
            return
        try:
            import paho.mqtt.client as mqtt
            self._client = mqtt.Client(client_id="simulation-backend", clean_session=True)
            self._client.on_connect = self._on_connect
            self._client.on_disconnect = self._on_disconnect
            self._client.on_message = self._on_message
            self._client.connect_async(self._host, self._port, 60)
            self._client.loop_start()
            logger.info("MQTT bridge connecting to %s:%s", self._host, self._port)
        except Exception as exc:
            logger.warning("MQTT bridge failed to start: %s", exc)

    def stop(self) -> None:
        if self._client is not None:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass
        self._connected = False

    # --- pub / sub ----------------------------------------------------------

    def publish_command(self, topic: str, payload: dict) -> bool:
        if not self._enabled or self._client is None or not self._connected:
            return False
        data = json.dumps(payload).encode()
        info = self._client.publish(topic, data, qos=1)
        return info.rc == 0

    def subscribe_state(self, topic: str, callback: Callable[[dict], None]) -> None:
        self._state_callbacks[topic] = callback
        if self._client is not None and self._connected:
            self._client.subscribe(topic, qos=0)

    # --- paho callbacks -----------------------------------------------------

    def _on_connect(self, client: Any, userdata: Any, flags: Any, rc: int) -> None:
        if rc == 0:
            self._connected = True
            logger.info("MQTT bridge connected")
            for topic in self._state_callbacks:
                client.subscribe(topic, qos=0)
        else:
            logger.warning("MQTT bridge connect refused, rc=%s", rc)

    def _on_disconnect(self, client: Any, userdata: Any, rc: int) -> None:
        self._connected = False
        if rc != 0:
            logger.warning("MQTT bridge lost (rc=%s); reconnecting", rc)

    def _on_message(self, client: Any, userdata: Any, msg: Any) -> None:
        cb = self._state_callbacks.get(msg.topic)
        if cb is not None:
            try:
                payload = json.loads(msg.payload.decode())
                cb(payload)
            except Exception:
                logger.exception("state callback failed for %s", msg.topic)
```

- [ ] **Step 6: 运行测试确认通过**

Run: `cd simulation/backend && python -m pytest tests/test_mqtt_bridge.py -v`
Expected: 4 passed

- [ ] **Step 7: Commit**

```bash
git add simulation/backend/config.py simulation/backend/requirements.txt \
       simulation/backend/services/mqtt_bridge.py \
       simulation/backend/tests/test_mqtt_bridge.py
git commit -m "feat(sim): add MQTT bridge with paho-mqtt loop_start model"
```

---

## Task 2: MotionCommander — 任务到运动命令桥接

**Files:**
- Create: `simulation/backend/services/motion_commander.py`
- Test: `simulation/backend/tests/test_motion_commander.py`

**Interfaces:**
- Consumes: `SimulationMqttBridge.publish_command()`, `SiteManager.get()`
- Produces: `MotionCommander.on_task_started(task_record) -> dict | None`

- [ ] **Step 1: 编写 MotionCommander 测试**

创建 `simulation/backend/tests/test_motion_commander.py`:

```python
"""Tests for MotionCommander — task-to-motion-command mapping."""
import pytest

from backend.services.motion_commander import MotionCommander


class FakeBridge:
    def __init__(self):
        self.published = []

    def publish_command(self, topic: str, payload: dict) -> bool:
        self.published.append((topic, payload))
        return True


class TestMotionCommander:
    def _make(self) -> tuple[MotionCommander, FakeBridge]:
        from backend.algorithm.simulator.site_manager import SiteManager
        bridge = FakeBridge()
        sites = SiteManager()
        cmdr = MotionCommander(bridge, sites)
        return cmdr, bridge

    def test_dock_loading_publishes_move_l(self):
        cmdr, bridge = self._make()
        task = {"task_id": "t1", "type": "dock_loading", "device_id": "robot-01"}
        result = cmdr.on_task_started(task)
        assert result is not None
        assert len(bridge.published) == 1
        topic, payload = bridge.published[0]
        assert topic == "rcs/robot-01/command"
        assert payload["type"] == "move_l"
        assert "target_pose" in payload

    def test_agv_transport_publishes_move_j(self):
        cmdr, bridge = self._make()
        task = {"task_id": "t2", "type": "agv_transport", "device_id": "robot-01"}
        result = cmdr.on_task_started(task)
        assert result is not None
        topic, payload = bridge.published[0]
        assert payload["type"] == "move_j"
        assert "target_joints" in payload

    def test_warehouse_storage_publishes_move_l(self):
        cmdr, bridge = self._make()
        task = {"task_id": "t3", "type": "warehouse_storage", "device_id": "robot-01"}
        result = cmdr.on_task_started(task)
        assert result is not None
        _, payload = bridge.published[0]
        assert payload["type"] == "move_l"

    def test_unknown_task_type_returns_none(self):
        cmdr, bridge = self._make()
        task = {"task_id": "t4", "type": "unknown_type", "device_id": "robot-01"}
        result = cmdr.on_task_started(task)
        assert result is None
        assert len(bridge.published) == 0

    def test_tcp_pose_within_arm_reach(self):
        """SiteManager warehouse coords must be converted to arm-reachable poses."""
        cmdr, bridge = self._make()
        task = {"task_id": "t5", "type": "dock_loading", "device_id": "robot-01"}
        cmdr.on_task_started(task)
        _, payload = bridge.published[0]
        pose = payload["target_pose"]
        import math
        reach = math.sqrt(pose["x"]**2 + pose["y"]**2 + pose["z"]**2)
        assert reach < 1.5, f"TCP pose out of arm reach: {reach:.2f}m"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd simulation/backend && python -m pytest tests/test_motion_commander.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 实现 MotionCommander**

创建 `simulation/backend/services/motion_commander.py`:

```python
"""Bridge from simulation tasks to motion commands.

Converts high-level task types (dock_loading, agv_transport, warehouse_storage)
into MoveCommand payloads published via MQTT.

Coordinate transform
--------------------
SiteManager stores warehouse-scale coordinates (e.g. x=-6.0, z=7.0) which are
far outside the arm's ~0.8m reach.  We predefine a fixed ``T_base_to_site``
offset that maps each site to a TCP pose reachable from the arm base.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from backend.algorithm.simulator.site_manager import SiteManager
from backend.services.mqtt_bridge import SimulationMqttBridge

logger = logging.getLogger(__name__)

# Predefined arm-base-to-site TCP poses (metres, in arm base frame).
# These are placeholder values for the prototype; real values come from
# calibration or CAD.
_SITE_TCP_POSES: dict[str, dict[str, float]] = {
    "dock_loading": {"x": 0.50, "y": 0.00, "z": 0.30, "rx": 0.0, "ry": 1.57, "rz": 0.0},
    "warehouse_storage": {"x": 0.40, "y": -0.30, "z": 0.50, "rx": 0.0, "ry": 1.57, "rz": 0.0},
}

# Default joint configuration for agv_transport (radians).
_TRANSPORT_JOINTS: list[float] = [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]


class MotionCommander:
    """Converts task records into motion commands published via MQTT."""

    def __init__(self, mqtt_bridge: SimulationMqttBridge, site_manager: SiteManager) -> None:
        self._bridge = mqtt_bridge
        self._sites = site_manager

    def on_task_started(self, task_record: dict[str, Any]) -> dict[str, Any] | None:
        task_type = task_record["type"]
        device_id = task_record["device_id"]
        command = self._build_command(task_type, device_id)
        if command is None:
            return None
        topic = f"rcs/{device_id}/command"
        self._bridge.publish_command(topic, command)
        logger.info("published %s command for %s: %s", task_type, device_id, command["type"])
        return command

    def _build_command(self, task_type: str, device_id: str) -> dict[str, Any] | None:
        command_id = f"cmd-{uuid.uuid4().hex[:8]}"
        if task_type == "dock_loading":
            return {
                "command_id": command_id,
                "type": "move_l",
                "target_pose": _SITE_TCP_POSES["dock_loading"],
                "target_joints": [],
                "speed_scale": 0.5,
            }
        elif task_type == "agv_transport":
            return {
                "command_id": command_id,
                "type": "move_j",
                "target_joints": list(_TRANSPORT_JOINTS),
                "target_pose": None,
                "speed_scale": 0.8,
            }
        elif task_type == "warehouse_storage":
            return {
                "command_id": command_id,
                "type": "move_l",
                "target_pose": _SITE_TCP_POSES["warehouse_storage"],
                "target_joints": [],
                "speed_scale": 0.5,
            }
        else:
            logger.warning("unknown task type %r — no motion command generated", task_type)
            return None
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd simulation/backend && python -m pytest tests/test_motion_commander.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add simulation/backend/services/motion_commander.py \
       simulation/backend/tests/test_motion_commander.py
git commit -m "feat(sim): add MotionCommander with coordinate transform"
```

---

## Task 3: Runtime 状态机 + Joint Cache

**Files:**
- Modify: `simulation/backend/services/runtime.py`
- Test: `simulation/backend/tests/test_runtime_joints.py`

**Interfaces:**
- Consumes: existing `Runtime` class
- Produces: `runtime.update_joint_state(device_id, joint_data)`, `runtime.get_joint_state(device_id) -> dict | None`, enhanced task state machine

- [ ] **Step 1: 编写 Runtime joint + 状态机测试**

创建 `simulation/backend/tests/test_runtime_joints.py`:

```python
"""Tests for Runtime joint cache and task state machine enhancements."""
import pytest

from backend.services.runtime import Runtime


class TestRuntimeJointCache:
    def test_update_and_get_joint_state(self):
        rt = Runtime()
        data = {
            "device_id": "robot-01",
            "joint_names": ["j1", "j2", "j3", "j4", "j5", "j6"],
            "positions": [0.0, -1.57, 1.57, -1.57, -1.57, 0.0],
            "velocities": [0.0] * 6,
            "timestamp_ns": 1234567890,
        }
        rt.update_joint_state("robot-01", data)
        result = rt.get_joint_state("robot-01")
        assert result is not None
        assert result["positions"] == [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]

    def test_get_joint_state_unknown_device(self):
        rt = Runtime()
        assert rt.get_joint_state("nonexistent") is None


class TestRuntimeTaskStateMachine:
    def test_task_starts_as_pending(self):
        rt = Runtime()
        # _seed_tasks creates 3 tasks, all pending
        for task in rt.tasks.values():
            assert task["status"] == "pending"

    def test_advance_task_to_command_sent(self):
        rt = Runtime()
        task_id = list(rt.tasks.keys())[0]
        rt.advance_task(task_id, "command_sent")
        assert rt.tasks[task_id]["status"] == "command_sent"

    def test_advance_task_to_running(self):
        rt = Runtime()
        task_id = list(rt.tasks.keys())[0]
        rt.advance_task(task_id, "command_sent")
        rt.advance_task(task_id, "running")
        assert rt.tasks[task_id]["status"] == "running"

    def test_fail_task_from_any_state(self):
        rt = Runtime()
        task_id = list(rt.tasks.keys())[0]
        rt.fail_task(task_id, "planning failed")
        assert rt.tasks[task_id]["status"] == "failed"

    def test_complete_task_requires_running(self):
        rt = Runtime()
        task_id = list(rt.tasks.keys())[0]
        # pending → completed should fail
        with pytest.raises(RuntimeError):
            rt.complete_task(task_id)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd simulation/backend && python -m pytest tests/test_runtime_joints.py -v`
Expected: FAIL — `AttributeError: 'Runtime' object has no attribute 'update_joint_state'`

- [ ] **Step 3: 在 Runtime 中添加 joint cache 和状态机方法**

在 `simulation/backend/services/runtime.py` 的 `Runtime.__init__` 方法中，在 `self._seed_tasks()` 之前添加:

```python
        # joint state cache: device_id -> latest joint data dict
        self._joint_cache: dict[str, dict[str, Any]] = {}
```

在 `Runtime` 类末尾（`unsubscribe` 方法之后、`runtime = Runtime()` 之前）添加:

```python
    # --- joint state cache --------------------------------------------------

    def update_joint_state(self, device_id: str, data: dict[str, Any]) -> None:
        """Store latest joint state from MQTT for SSE consumers."""
        self._joint_cache[device_id] = data

    def get_joint_state(self, device_id: str) -> dict[str, Any] | None:
        """Retrieve cached joint state for a device."""
        return self._joint_cache.get(device_id)

    # --- task state machine -------------------------------------------------

    _VALID_TRANSITIONS = {
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
        self._transition(task_id, new_status)

    def complete_task(self, task_id: str) -> None:
        self._transition(task_id, "completed")
        self.scheduler.mark_completed(task_id)

    def fail_task(self, task_id: str, reason: str) -> None:
        self._transition(task_id, "failed", reason)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd simulation/backend && python -m pytest tests/test_runtime_joints.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add simulation/backend/services/runtime.py \
       simulation/backend/tests/test_runtime_joints.py
git commit -m "feat(sim): add joint cache + task state machine to Runtime"
```

---

## Task 4: SSE 关节状态端点

**Files:**
- Modify: `simulation/backend/main.py`

**Interfaces:**
- Consumes: `runtime.get_joint_state(device_id)`
- Produces: `GET /api/devices/{device_id}/joints` — SSE stream

- [ ] **Step 1: 在 main.py 中添加 joints SSE 端点**

在 `simulation/backend/main.py` 中，在现有 SSE 端点（`/stream`）附近添加新端点:

```python
@app.get("/api/devices/{device_id}/joints")
async def device_joints_sse(device_id: str):
    """SSE stream of real-time joint positions for a device."""
    async def event_stream():
        while True:
            data = runtime.get_joint_state(device_id)
            if data is not None:
                yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1.0 / 30)  # 30Hz max

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

- [ ] **Step 2: 在 /api/devices 响应中增加 joints 字段**

找到 `GET /api/devices` 端点的返回逻辑，在设备 dict 中增加:

```python
# 在设备信息 dict 构建中增加:
joints = runtime.get_joint_state(device_id)
if joints:
    device_info["joints"] = joints
```

- [ ] **Step 3: 手动验证（需要运行服务）**

```bash
cd simulation/backend && uvicorn backend.main:app --reload
# 另一个终端:
curl -N http://localhost:8000/api/devices/robot-01/joints
```

- [ ] **Step 4: Commit**

```bash
git add simulation/backend/main.py
git commit -m "feat(sim): add SSE endpoint for real-time joint state"
```

---

## Task 5: robot_decision 包配置

**Files:**
- Modify: `robot_decision/setup.py`
- Modify: `robot_decision/package.xml`
- Create: `robot_decision/config/motion_planner.yaml`

- [ ] **Step 1: 更新 setup.py — 添加入口点 + config data_files**

修改 `robot-app/ros2_ws/src/robot_decision/setup.py`:

```python
"""Setup script for robot_decision."""
from glob import glob

from setuptools import setup

PACKAGE_NAME = "robot_decision"

setup(
    name=PACKAGE_NAME,
    version="0.1.0",
    packages=[PACKAGE_NAME],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + PACKAGE_NAME]),
        ("share/" + PACKAGE_NAME, ["package.xml"]),
        ("share/" + PACKAGE_NAME + "/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="joezxh",
    maintainer_email="joezxh@qq.com",
    description="MoveIt motion planning node (Phase 5 M3)",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "motion_planner_node = robot_decision.motion_planner:main",
        ],
    },
)
```

- [ ] **Step 2: 更新 package.xml — 添加依赖**

在 `robot-app/ros2_ws/src/robot_decision/package.xml` 中，在 `<exec_depend>moveit_ros_planning_interface</exec_depend>` 之后添加:

```xml
  <exec_depend>moveit_msgs</exec_depend>
  <exec_depend>control_msgs</exec_depend>
  <exec_depend>sensor_msgs</exec_depend>
  <exec_depend>trajectory_msgs</exec_depend>
  <exec_depend>std_msgs</exec_depend>
```

同时删除重复的 `<exec_depend>rclpy</exec_depend>` 行（现有两行）。

- [ ] **Step 3: 创建 config/motion_planner.yaml**

创建 `robot-app/ros2_ws/src/robot_decision/config/motion_planner.yaml`:

```yaml
motion_planner_node:
  ros__parameters:
    planning_group: manipulator       # must match robot.srdf <group name>
    end_effector_link: tcp_frame      # must match robot.urdf.xacro
    moveit_timeout: 5.0               # seconds
    device_id: robot-01
    state_publish_hz: 10.0
```

- [ ] **Step 4: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/setup.py \
       robot-app/ros2_ws/src/robot_decision/package.xml \
       robot-app/ros2_ws/src/robot_decision/config/motion_planner.yaml
git commit -m "chore(decision): configure package deps, entry point, config"
```

---

## Task 6: MoveItClient — MoveGroupInterface 封装

**Files:**
- Create: `robot_decision/robot_decision/moveit_client.py`
- Test: `robot_decision/tests/test_moveit_client.py`

**Interfaces:**
- Consumes: `moveit_ros_planning_interface.MoveGroupInterface`
- Produces: `MoveItClient` class with `plan_joint_target()`, `plan_pose_target()`, `plan_named_target()`, `stop()`

- [ ] **Step 1: 编写 MoveItClient 测试**

创建 `robot-app/ros2_ws/src/robot_decision/tests/test_moveit_client.py`:

```python
"""Tests for MoveItClient — mocked MoveGroupInterface."""
import pytest
from unittest.mock import MagicMock, patch


class TestMoveItClient:
    """Test planning logic without a real MoveGroup connection."""

    def _make_client(self):
        # Patch MoveGroupInterface so no ROS 2 connection is needed
        with patch("robot_decision.moveit_client.MoveGroupInterface") as MockMGI:
            mock_group = MagicMock()
            MockMGI.return_value = mock_group
            # plan() returns a MoveItSuccess with trajectory
            mock_plan = MagicMock()
            mock_plan.error_code.val = 1  # SUCCESS
            mock_plan.trajectory.joint_trajectory = MagicMock()
            mock_group.plan.return_value = mock_plan

            from robot_decision.moveit_client import MoveItClient
            client = MoveItClient(group_name="manipulator", ee_link="tcp_frame", timeout=5.0)
            client._group = mock_group
            return client, mock_group

    def test_plan_joint_target_sets_joint_goal(self):
        client, mock_group = self._make_client()
        joints = [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]
        traj = client.plan_joint_target(joints)
        mock_group.set_joint_value_target.assert_called_once_with(joints)
        mock_group.plan.assert_called_once()
        assert traj is not None

    def test_plan_pose_target_sets_pose_goal(self):
        client, mock_group = self._make_client()
        from robot_msgs import Pose6DMsg
        pose = Pose6DMsg(x=0.5, y=0.0, z=0.3, rx=0.0, ry=1.57, rz=0.0)
        traj = client.plan_pose_target(pose)
        mock_group.set_pose_target.assert_called_once()
        assert traj is not None

    def test_plan_returns_none_on_failure(self):
        client, mock_group = self._make_client()
        mock_plan = MagicMock()
        mock_plan.error_code.val = -1  # FAILURE
        mock_group.plan.return_value = mock_plan
        traj = client.plan_joint_target([0.0] * 6)
        assert traj is None

    def test_stop_calls_stop_on_group(self):
        client, mock_group = self._make_client()
        client.stop()
        mock_group.stop.assert_called_once()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_moveit_client.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: 实现 MoveItClient**

创建 `robot-app/ros2_ws/src/robot_decision/robot_decision/moveit_client.py`:

```python
"""Thin wrapper around MoveIt's MoveGroupInterface.

Handles planning only — execution is delegated to controller_manager via
the FollowJointTrajectory action (see motion_planner.py).
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from moveit.planning_interface import MoveGroupInterface
except ImportError:
    MoveGroupInterface = None  # type: ignore[assignment,misc]
    logger.warning("MoveGroupInterface not available — running without MoveIt")


class MoveItClient:
    """Plans trajectories via MoveIt MoveGroupInterface."""

    def __init__(self, *, group_name: str, ee_link: str, timeout: float = 5.0) -> None:
        self._group_name = group_name
        self._ee_link = ee_link
        self._timeout = timeout
        self._group: Any = None
        self._init_group()

    def _init_group(self) -> None:
        if MoveGroupInterface is None:
            logger.error("MoveGroupInterface unavailable")
            return
        try:
            self._group = MoveGroupInterface(self._group_name)
            self._group.set_pose_reference_frame("base_link")
            self._group.set_planning_time(self._timeout)
            self._group.set_max_velocity_scaling_factor(0.5)
            self._group.set_max_acceleration_scaling_factor(0.5)
            logger.info("MoveItClient ready: group=%s ee=%s", self._group_name, self._ee_link)
        except Exception:
            logger.exception("failed to initialise MoveGroupInterface")

    @property
    def ready(self) -> bool:
        return self._group is not None

    def plan_joint_target(self, joints: list[float]) -> Any | None:
        """Plan to joint-space target. Returns JointTrajectory or None."""
        if not self.ready:
            return None
        self._group.set_joint_value_target(joints)
        return self._plan_and_extract()

    def plan_pose_target(self, pose: Any) -> Any | None:
        """Plan to Cartesian pose target (Pose6DMsg). Returns JointTrajectory or None."""
        if not self.ready:
            return None
        from geometry_msgs.msg import PoseStamped
        ps = PoseStamped()
        ps.header.frame_id = "base_link"
        ps.pose.position.x = pose.x
        ps.pose.position.y = pose.y
        ps.pose.position.z = pose.z
        # Convert RPY to quaternion (simplified — use tf_transformations in production)
        import math
        cy = math.cos(pose.rz * 0.5)
        sy = math.sin(pose.rz * 0.5)
        cp = math.cos(pose.ry * 0.5)
        sp = math.sin(pose.ry * 0.5)
        cr = math.cos(pose.rx * 0.5)
        sr = math.sin(pose.rx * 0.5)
        ps.pose.orientation.w = cr * cp * cy + sr * sp * sy
        ps.pose.orientation.x = sr * cp * cy - cr * sp * sy
        ps.pose.orientation.y = cr * sp * cy + sr * cp * sy
        ps.pose.orientation.z = cr * cp * sy - sr * sp * cy
        self._group.set_pose_target(ps)
        return self._plan_and_extract()

    def plan_named_target(self, name: str) -> Any | None:
        """Plan to a named target defined in the SRDF."""
        if not self.ready:
            return None
        self._group.set_named_target(name)
        return self._plan_and_extract()

    def stop(self) -> None:
        if self.ready:
            self._group.stop()

    def _plan_and_extract(self) -> Any | None:
        plan_result = self._group.plan()
        if plan_result is None or plan_result.error_code.val != 1:
            logger.warning("MoveIt planning failed: error_code=%s",
                           getattr(plan_result, "error_code", "None"))
            return None
        return plan_result.trajectory.joint_trajectory
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_moveit_client.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/robot_decision/moveit_client.py \
       robot-app/ros2_ws/src/robot_decision/tests/test_moveit_client.py
git commit -m "feat(decision): add MoveItClient wrapper for MoveGroupInterface"
```

---

## Task 7: MotionPlannerNode — 运动规划节点

**Files:**
- Create: `robot_decision/robot_decision/motion_planner.py`
- Test: `robot_decision/tests/test_command_conversion.py`

**Interfaces:**
- Consumes: `MoveItClient`, `std_msgs/msg/String` on `~/motion_command`
- Produces: `std_msgs/msg/String` on `~/robot_state`, `FollowJointTrajectory` goal to controller_manager

- [ ] **Step 1: 编写命令转换测试**

创建 `robot-app/ros2_ws/src/robot_decision/tests/test_command_conversion.py`:

```python
"""Tests for motion command JSON deserialization and dispatch logic."""
import json
import pytest

from robot_msgs import MoveCommandGoal, Pose6DMsg


class TestCommandConversion:
    def test_deserialize_move_j(self):
        raw = json.dumps({
            "command_id": "cmd-001",
            "type": "move_j",
            "target_joints": [0.0, -1.57, 1.57, -1.57, -1.57, 0.0],
            "target_pose": None,
            "speed_scale": 0.8,
        })
        data = json.loads(raw)
        goal = MoveCommandGoal(
            command_id=data["command_id"],
            type=data["type"],
            target_joints=data.get("target_joints", []),
            target_pose=Pose6DMsg.from_dict(data["target_pose"]) if data.get("target_pose") else None,
            speed_scale=data.get("speed_scale", 1.0),
        )
        assert goal.type == "move_j"
        assert len(goal.target_joints) == 6
        assert goal.target_pose is None

    def test_deserialize_move_l_with_pose(self):
        raw = json.dumps({
            "command_id": "cmd-002",
            "type": "move_l",
            "target_joints": [],
            "target_pose": {"x": 0.5, "y": 0.0, "z": 0.3, "rx": 0.0, "ry": 1.57, "rz": 0.0},
            "speed_scale": 0.5,
        })
        data = json.loads(raw)
        goal = MoveCommandGoal(
            command_id=data["command_id"],
            type=data["type"],
            target_joints=data.get("target_joints", []),
            target_pose=Pose6DMsg.from_dict(data["target_pose"]) if data.get("target_pose") else None,
            speed_scale=data.get("speed_scale", 1.0),
        )
        assert goal.type == "move_l"
        assert goal.target_pose is not None
        assert goal.target_pose.x == 0.5

    def test_deserialize_home(self):
        raw = json.dumps({
            "command_id": "cmd-003",
            "type": "home",
            "target_joints": [],
            "target_pose": None,
            "speed_scale": 1.0,
        })
        data = json.loads(raw)
        goal = MoveCommandGoal(
            command_id=data["command_id"],
            type=data["type"],
            target_joints=[],
            speed_scale=1.0,
        )
        assert goal.type == "home"
```

- [ ] **Step 2: 运行测试确认通过（纯 dataclass 测试，无需实现节点）**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_command_conversion.py -v`
Expected: 3 passed

- [ ] **Step 3: 实现 MotionPlannerNode**

创建 `robot-app/ros2_ws/src/robot_decision/robot_decision/motion_planner.py`:

```python
"""Motion planner ROS 2 node.

Subscribes to ``~/motion_command`` (std_msgs/msg/String, JSON), plans via
MoveIt, executes via FollowJointTrajectory action to controller_manager,
and publishes ``~/robot_state`` (std_msgs/msg/String, JSON).
"""
from __future__ import annotations

import json
import time
from typing import Any

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from sensor_msgs.msg import JointState
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from robot_msgs import (
    MoveCommandGoal,
    Pose6DMsg,
    RobotStateMsg,
    JointStateMsg,
    TrackingErrorMsg,
    ControllerStateMsg,
)

from .moveit_client import MoveItClient


class MotionPlannerNode(Node):
    """Plans and executes motion commands via MoveIt + controller_manager."""

    def __init__(self) -> None:
        super().__init__("motion_planner_node")

        # Parameters
        self.declare_parameter("planning_group", "manipulator")
        self.declare_parameter("end_effector_link", "tcp_frame")
        self.declare_parameter("moveit_timeout", 5.0)
        self.declare_parameter("device_id", "robot-01")
        self.declare_parameter("state_publish_hz", 10.0)

        group = self.get_parameter("planning_group").value
        ee = self.get_parameter("end_effector_link").value
        timeout = float(self.get_parameter("moveit_timeout").value)
        self._device_id = self.get_parameter("device_id").value
        hz = float(self.get_parameter("state_publish_hz").value)

        # MoveIt client (planning only)
        self._moveit = MoveItClient(group_name=group, ee_link=ee, timeout=timeout)

        # Action client for trajectory execution
        self._traj_client = ActionClient(
            self, FollowJointTrajectory,
            "/arm_controller/follow_joint_trajectory",
        )

        # Subscribers
        self._cmd_sub = self.create_subscription(
            String, "~/motion_command", self._on_motion_command, 10,
        )
        self._joint_sub = self.create_subscription(
            JointState, "/joint_states", self._on_joint_states, 10,
        )

        # Publishers
        self._state_pub = self.create_publisher(String, "~/robot_state", 10)
        self._alert_pub = self.create_publisher(String, "~/alert", 10)

        # State
        self._current_goal: MoveCommandGoal | None = None
        self._phase = "idle"  # idle | planning | executing
        self._latest_joints: JointState | None = None
        self._target_joints: list[float] = []

        # State publish timer
        self._state_timer = self.create_timer(1.0 / hz, self._publish_state)

        self.get_logger().info(
            f"MotionPlanner ready: group={group} ee={ee} device={self._device_id}"
        )

    # --- command handling ---------------------------------------------------

    def _on_motion_command(self, msg: String) -> None:
        try:
            data = json.loads(msg.data)
        except json.JSONDecodeError:
            self.get_logger().error("invalid JSON on ~/motion_command")
            return

        goal = MoveCommandGoal(
            command_id=data.get("command_id", ""),
            type=data.get("type", ""),
            target_joints=data.get("target_joints", []),
            target_pose=Pose6DMsg.from_dict(data["target_pose"]) if data.get("target_pose") else None,
            speed_scale=data.get("speed_scale", 1.0),
        )
        self._current_goal = goal
        self._execute(goal)

    def _execute(self, goal: MoveCommandGoal) -> None:
        self._phase = "planning"
        trajectory = None

        try:
            if goal.type == "move_j":
                trajectory = self._moveit.plan_joint_target(goal.target_joints)
                self._target_joints = goal.target_joints
            elif goal.type == "move_l" and goal.target_pose:
                trajectory = self._moveit.plan_pose_target(goal.target_pose)
            elif goal.type == "home":
                trajectory = self._moveit.plan_named_target("home")
                self._target_joints = [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]
            elif goal.type == "stop":
                self._moveit.stop()
                self._phase = "idle"
                return
            else:
                self.get_logger().warn(f"unknown command type: {goal.type}")
                self._phase = "idle"
                return
        except Exception:
            self.get_logger().exception("planning exception")
            self._publish_alert(f"planning exception for {goal.type}")
            self._phase = "idle"
            return

        if trajectory is None:
            self.get_logger().error(f"planning failed for {goal.type}")
            self._publish_alert(f"planning failed: {goal.type}")
            self._phase = "idle"
            return

        self._phase = "executing"
        self._send_trajectory(trajectory)

    def _send_trajectory(self, trajectory: JointTrajectory) -> None:
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = trajectory
        goal_msg.joint_names = trajectory.joint_names

        self._traj_client.send_goal_async(
            goal_msg,
        ).add_done_callback(self._on_trajectory_result)

    def _on_trajectory_result(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("trajectory goal rejected")
            self._publish_alert("trajectory rejected")
            self._phase = "idle"
            return
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._on_trajectory_done)

    def _on_trajectory_done(self, future) -> None:
        result = future.result()
        if result.status == 4:  # SUCCEEDED
            self.get_logger().info("trajectory executed successfully")
        else:
            self.get_logger().error(f"trajectory failed: status={result.status}")
            self._publish_alert("trajectory execution failed")
        self._phase = "idle"
        self._current_goal = None

    # --- joint state + state publishing ------------------------------------

    def _on_joint_states(self, msg: JointState) -> None:
        self._latest_joints = msg

    def _publish_state(self) -> None:
        if self._latest_joints is None:
            return
        js = self._latest_joints
        joint = JointStateMsg(
            positions=list(js.position[:6]),
            velocities=list(js.velocity[:6]) if js.velocity else [0.0] * 6,
            timestamp_ns=js.header.stamp.sec * 10**9 + js.header.stamp.nanosec,
            device_id=self._device_id,
        )
        # Compute tracking error
        err = TrackingErrorMsg()
        if self._target_joints and len(joint.positions) == len(self._target_joints):
            errors = [abs(a - b) for a, b in zip(joint.positions, self._target_joints)]
            err.max_joint_error = max(errors) if errors else 0.0

        ctrl = ControllerStateMsg(mode=self._phase)
        if self._current_goal:
            ctrl.active_command_id = self._current_goal.command_id

        state = RobotStateMsg(
            device_id=self._device_id,
            joint=joint,
            err=err,
            ctrl=ctrl,
        )
        msg = String()
        msg.data = json.dumps(state.to_dict())
        self._state_pub.publish(msg)

    def _publish_alert(self, message: str) -> None:
        msg = String()
        msg.data = json.dumps({
            "device_id": self._device_id,
            "event": "planning_failure",
            "error": message,
        })
        self._alert_pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MotionPlannerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/robot_decision/motion_planner.py \
       robot-app/ros2_ws/src/robot_decision/tests/test_command_conversion.py
git commit -m "feat(decision): add MotionPlannerNode with MoveIt + action client"
```

---

## Task 8: robot_gateway 增强

**Files:**
- Modify: `robot_gateway/robot_gateway/mqtt_bridge_node.py`

**Interfaces:**
- Consumes: `CommandMsg` from MQTT, `std_msgs/msg/String` on `~/robot_state`
- Produces: `std_msgs/msg/String` on `~/motion_command`, state via `MqttBridge.publish_state()`

- [ ] **Step 1: 修改 mqtt_bridge_node.py — 命令转发 + 状态上报**

修改 `robot-app/ros2_ws/src/robot_gateway/robot_gateway/mqtt_bridge_node.py`:

在 import 区域添加:

```python
import json
from std_msgs.msg import String
from robot_msgs import MoveCommandGoal, Pose6DMsg, RobotStateMsg
```

在 `MqttBridgeNode.__init__` 中，在 `self._telemetry_timer` 创建之后添加:

```python
        # ROS 2 topics for Decision communication
        self._motion_cmd_pub = self.create_publisher(String, "~/motion_command", 10)
        self._robot_state_sub = self.create_subscription(
            String, "~/robot_state", self._on_robot_state, 10
        )
        self._alert_sub = self.create_subscription(
            String, "~/alert", self._on_alert, 10
        )
```

替换 `_on_motion_command` 方法:

```python
    def _on_motion_command(self, command: CommandMsg) -> None:
        """Forward a motion command to robot_decision via ~/motion_command."""
        goal = MoveCommandGoal(
            command_id=command.command_id,
            type=command.type,
            target_joints=command.target_joints or [],
            target_pose=command.target_pose,
            speed_scale=command.speed_scale,
        )
        # Serialize to JSON for std_msgs/msg/String transport
        payload = {
            "command_id": goal.command_id,
            "type": goal.type,
            "target_joints": goal.target_joints,
            "target_pose": goal.target_pose.to_dict() if goal.target_pose else None,
            "speed_scale": goal.speed_scale,
        }
        msg = String()
        msg.data = json.dumps(payload)
        self._motion_cmd_pub.publish(msg)
        self.get_logger().info(
            f"forwarded {command.type} (id={command.command_id}) to ~/motion_command"
        )
```

在 `_on_estop_command` 之后添加:

```python
    def _on_robot_state(self, msg: String) -> None:
        """Forward robot state from Decision to MQTT."""
        try:
            data = json.loads(msg.data)
            state = RobotStateMsg.from_dict(data)
            self._bridge.publish_state(state)
        except Exception:
            self.get_logger().exception("failed to forward robot state to MQTT")

    def _on_alert(self, msg: String) -> None:
        """Forward alert from Decision to MQTT."""
        try:
            data = json.loads(msg.data)
            payload = json.dumps(data).encode()
            self._link.publish(
                f"rcs/{self._device_id}/alert", payload, qos=1
            )
            self.get_logger().warn(f"alert forwarded: {data.get('error', '')}")
        except Exception:
            self.get_logger().exception("failed to forward alert to MQTT")
```

- [ ] **Step 2: Commit**

```bash
git add robot-app/ros2_ws/src/robot_gateway/robot_gateway/mqtt_bridge_node.py
git commit -m "feat(gateway): forward commands to Decision + report state to MQTT"
```

---

## Task 9: 前端机械臂可视化

**Files:**
- Create: `simulation/frontend/src/three/RobotArm.ts`
- Modify: `simulation/frontend/src/three/WarehouseScene.vue`

- [ ] **Step 1: 创建 RobotArm.ts**

创建 `simulation/frontend/src/three/RobotArm.ts`:

```typescript
/**
 * Procedural 6-DOF robot arm built from basic Three.js geometries.
 * Phase 1: simple cylinders/boxes aligned with URDF link dimensions.
 * Phase 2: replace with GLTF model.
 */
import * as THREE from 'three'

const LINK_DIMS = {
  base: { radius: 0.08, height: 0.1 },
  shoulder: { radius: 0.06, height: 0.15 },
  upper_arm: { radius: 0.05, height: 0.425 },
  forearm: { radius: 0.04, height: 0.392 },
  wrist: { radius: 0.03, height: 0.08 },
}

const JOINT_NAMES = [
  'shoulder_pan', 'shoulder_lift', 'elbow',
  'wrist_1', 'wrist_2', 'wrist_3',
]

export type ArmStatus = 'idle' | 'moving' | 'error' | 'estop'

const STATUS_COLORS: Record<ArmStatus, number> = {
  idle: 0x888888,
  moving: 0x3b82f6,
  error: 0xef4444,
  estop: 0xff0000,
}

export class RobotArm {
  public group: THREE.Group
  private joints: THREE.Group[] = []
  private targets: number[] = new Array(6).fill(0)
  private current: number[] = new Array(6).fill(0)
  private status: ArmStatus = 'idle'
  private meshes: THREE.Mesh[] = []
  private lerpAlpha = 0.3

  constructor() {
    this.group = new THREE.Group()
    this.group.name = 'RobotArm'
    this.build()
  }

  private build() {
    const mat = new THREE.MeshStandardMaterial({ color: STATUS_COLORS.idle })

    // base_link
    const base = new THREE.Mesh(
      new THREE.CylinderGeometry(LINK_DIMS.base.radius, LINK_DIMS.base.radius, LINK_DIMS.base.height, 16),
      mat.clone()
    )
    base.position.y = LINK_DIMS.base.height / 2
    this.group.add(base)
    this.meshes.push(base)

    // Build kinematic chain: each joint is a Group that rotates around Y or Z
    const jointAxes: ('y' | 'z')[] = ['y', 'z', 'z', 'z', 'y', 'z']
    const links = [
      { name: 'shoulder', r: LINK_DIMS.shoulder.radius, h: LINK_DIMS.shoulder.height },
      { name: 'upper_arm', r: LINK_DIMS.upper_arm.radius, h: LINK_DIMS.upper_arm.height },
      { name: 'forearm', r: LINK_DIMS.forearm.radius, h: LINK_DIMS.forearm.height },
      { name: 'wrist_1', r: LINK_DIMS.wrist.radius, h: LINK_DIMS.wrist.height },
      { name: 'wrist_2', r: LINK_DIMS.wrist.radius, h: LINK_DIMS.wrist.height },
      { name: 'wrist_3', r: LINK_DIMS.wrist.radius, h: LINK_DIMS.wrist.height },
    ]

    let parent = this.group
    for (let i = 0; i < 6; i++) {
      const pivot = new THREE.Group()
      pivot.name = JOINT_NAMES[i]
      // Position pivot at top of previous link
      if (i === 0) {
        pivot.position.y = LINK_DIMS.base.height
      } else {
        pivot.position.y = links[i - 1].h
      }
      parent.add(pivot)
      this.joints.push(pivot)

      const link = links[i]
      const mesh = new THREE.Mesh(
        new THREE.CylinderGeometry(link.r, link.r, link.h, 12),
        mat.clone()
      )
      mesh.position.y = link.h / 2
      // Rotate mesh so cylinder aligns with joint axis
      if (jointAxes[i] === 'z') {
        mesh.rotation.x = Math.PI / 2
        mesh.position.y = 0
        mesh.position.z = link.h / 2
      }
      pivot.add(mesh)
      this.meshes.push(mesh)
      parent = pivot
    }
  }

  /** Set target joint positions (radians). Actual positions lerp toward targets. */
  setJointPositions(positions: number[]) {
    for (let i = 0; i < Math.min(positions.length, 6); i++) {
      this.targets[i] = positions[i]
    }
  }

  setStatus(status: ArmStatus) {
    if (this.status === status) return
    this.status = status
    const color = STATUS_COLORS[status]
    this.meshes.forEach(m => {
      (m.material as THREE.MeshStandardMaterial).color.setHex(color)
    })
  }

  /** Per-frame update: lerp joints toward targets. */
  update(_dt: number) {
    for (let i = 0; i < 6; i++) {
      this.current[i] += (this.targets[i] - this.current[i]) * this.lerpAlpha
      const axis = i === 0 || i === 4 ? 'y' : 'z'
      ;(this.joints[i].rotation as any)[axis] = this.current[i]
    }
  }

  addToScene(scene: THREE.Scene, position?: THREE.Vector3) {
    if (position) this.group.position.copy(position)
    scene.add(this.group)
  }
}
```

- [ ] **Step 2: 修改 WarehouseScene.vue — 集成机械臂**

在 `<script setup>` 的 import 区域添加:

```typescript
import { RobotArm } from './RobotArm'
```

在 `const deviceMeshes` 声明附近添加:

```typescript
let robotArm: RobotArm | undefined
let jointEventSource: EventSource | undefined
```

在 `init()` 函数末尾（场景构建完成后）添加:

```typescript
  // Robot arm (Phase 1: procedural geometry)
  robotArm = new RobotArm()
  robotArm.addToScene(scene!, new THREE.Vector3(-6, 0, 5))  // near dock area

  // SSE subscription for joint updates
  jointEventSource = new EventSource('/api/devices/robot-01/joints')
  jointEventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.positions && robotArm) {
        robotArm.setJointPositions(data.positions)
        robotArm.setStatus('moving')
      }
    } catch { /* ignore parse errors */ }
  }
```

在 `animate()` / `update()` 函数中添加:

```typescript
  if (robotArm) robotArm.update(dt)
```

在 `onUnmounted` 中添加清理:

```typescript
  jointEventSource?.close()
```

- [ ] **Step 3: 手动验证**

```bash
cd simulation/frontend && npm run dev
# 浏览器打开 http://localhost:5173
# 应看到 dock 区域附近的简化机械臂模型
```

- [ ] **Step 4: Commit**

```bash
git add simulation/frontend/src/three/RobotArm.ts \
       simulation/frontend/src/three/WarehouseScene.vue
git commit -m "feat(frontend): add procedural robot arm with SSE joint updates"
```

---

## Task 10: 集成验证

**Files:** 无新增文件

- [ ] **Step 1: 运行所有后端单元测试**

```bash
cd simulation/backend && python -m pytest tests/ -v
```

Expected: 所有测试通过（包括 test_mqtt_bridge, test_motion_commander, test_runtime_joints）

- [ ] **Step 2: 运行 robot_decision 测试**

```bash
cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/ -v
```

Expected: test_command_conversion (3) + test_moveit_client (4) 全部通过

- [ ] **Step 3: 端到端冒烟测试（需要完整环境）**

前置条件:
- Mosquitto broker 运行中
- ROS 2 环境已 source
- Simulation backend 运行中 (`SIM_MQTT_ENABLED=true`)

```bash
# Terminal 1: ROS 2 arm bringup
ros2 launch robot_bringup arm.launch.py use_gazebo:=false

# Terminal 2: MoveIt
ros2 launch robot_moveit_config move_group.launch.py

# Terminal 3: robot_gateway
ros2 run robot_gateway mqtt_bridge_node --ros-args -p device_id:=robot-01

# Terminal 4: robot_decision
ros2 run robot_decision motion_planner_node

# Terminal 5: Simulation backend
cd simulation/backend && SIM_MQTT_ENABLED=true uvicorn backend.main:app --reload

# Terminal 6: Verify
curl -X POST http://localhost:8000/api/tasks -H "Content-Type: application/json" \
  -d '{"type":"dock_loading","description":"test","priority":3,"device_id":"robot-01"}'
```

- [ ] **Step 4: 最终 Commit**

```bash
git add -A
git commit -m "feat: end-to-end motion chain — RCS→MQTT→Gateway→Decision→controller→frontend"
```
