# 装卸机器人（AGV + 双臂）实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `robot-app` 目录中实现 AGV 底盘 + 双臂抱拿配置的应用程序架构，包括双臂 URDF、任务协调器、抱拿控制器、安全互锁，并迁移 MoveIt 配置。

**Architecture:** 保留现有单臂 URDF 不变，新增 `robot_dual_arm_hal` 和 `robot_base_hal` 包。通信契约采用通用 `execute_task` 命令模式。`robot_decision` 实现分层状态机协调器，子系统执行器（底盘、双臂、抱拿）独立可测。MoveIt 配置迁移到 `simulation/` 工作区。

**Tech Stack:** ROS 2 Jazzy/Humble, xacro, MoveIt 2, ros2_control, Python 3.10+, pytest, Pydantic v2, MQTT (Mosquitto)

## Global Constraints

- ROS 2 发行版: Jazzy Jalisco (LTS) / Humble Hawksbill (LTS)
- `robot_arm_hal` 包完全不变，保持现有单臂 URDF 和 ros2_control 配置
- 通信契约保持零 rclpy 依赖（`robot_msgs/contracts.py` 和 `shared/python/robot_contracts/payloads.py`）
- 双臂 URDF 关节名必须带 `left_`/`right_` 前缀（避免重复关节名）
- `execute_task` 命令为通用模式，新增 task_type 不破坏契约结构
- dual_arm 规划超时 5s，超时后降级为分时单臂规划
- AUBO-i20 臂接口：以太网 TCP/IP（AUBO SDK）
- 安全停障不经过协调器，独立通路

---

## Task 1: 通信契约扩展 — JSON Schema

**Files:**
- Modify: `shared/contracts/command.schema.json`
- Modify: `shared/contracts/state.schema.json`
- Modify: `shared/contracts/telemetry.schema.json`

**Interfaces:**
- Consumes: 现有 command/state/telemetry schema
- Produces: 扩展后的 schema，支持 `execute_task` 命令、base/hug 状态字段、电池/温度遥测

- [ ] **Step 1: 扩展 command.schema.json — 新增 execute_task**

在 `shared/contracts/command.schema.json` 中：
1. `type` 字段的 enum 新增 `"execute_task"`
2. 新增 `task_type` 字段（string，可选）
3. 新增 `parameters` 字段（object，可选，free-form）
4. 新增 `group` 字段（string，可选，用于调试直通的 arm 选择）

```json
{
  "type": {
    "type": "string",
    "enum": ["move_j", "move_l", "stop", "home", "estop", "recover", "execute_task"]
  },
  "task_type": {
    "type": ["string", "null"],
    "description": "Task type for execute_task commands: goto, dock, pick_box, place_box, transport, hug_close, hug_release, home_all"
  },
  "parameters": {
    "type": ["object", "null"],
    "description": "Free-form task parameters (target_pose, hug_params, etc.)"
  },
  "group": {
    "type": ["string", "null"],
    "description": "Target group for debug passthrough: left, right, base, both"
  }
}
```

- [ ] **Step 2: 扩展 state.schema.json — 新增 base/hug 字段**

在 `shared/contracts/state.schema.json` 中：
1. 新增 `base` 字段（object，可选）：`velocity`, `odom`, `battery_soc`
2. 新增 `hug` 字段（object，可选）：`pressure_l`, `pressure_r`, `state`
3. `ctrl` 新增 `phase` 字段（string，可选）

```json
{
  "base": {
    "type": ["object", "null"],
    "properties": {
      "velocity": { "type": "array", "items": { "type": "number" } },
      "odom": {
        "type": ["object", "null"],
        "properties": {
          "x": { "type": "number" },
          "y": { "type": "number" },
          "yaw": { "type": "number" }
        }
      },
      "battery_soc": { "type": "number" }
    }
  },
  "hug": {
    "type": ["object", "null"],
    "properties": {
      "pressure_l": { "type": "number" },
      "pressure_r": { "type": "number" },
      "state": { "type": "string", "enum": ["closed", "holding", "open"] }
    }
  },
  "ctrl": {
    "type": ["object", "null"],
    "properties": {
      "mode": { "type": "string" },
      "phase": { "type": ["string", "null"] },
      "active_command_id": { "type": ["string", "null"] },
      "last_error": { "type": ["string", "null"] }
    }
  }
}
```

- [ ] **Step 3: 扩展 telemetry.schema.json — 新增遥测指标**

在 `shared/contracts/telemetry.schema.json` 的 `metrics` 描述中明确新增指标：
- `battery_voltage`, `battery_soc`
- `motor_temp_l`, `motor_temp_r`
- `drive_temp_l`, `drive_temp_r`

在 `status` 描述中明确新增状态：
- `base_state`（navigating/following/stopped）
- `hug_state`（closing/holding/opening）

- [ ] **Step 4: 验证 JSON Schema 语法正确**

Run: `python -c "import json; json.load(open('shared/contracts/command.schema.json'))"`
Expected: 无报错

Run: `python -c "import json; json.load(open('shared/contracts/state.schema.json'))"`
Expected: 无报错

Run: `python -c "import json; json.load(open('shared/contracts/telemetry.schema.json'))"`
Expected: 无报错

- [ ] **Step 5: Commit**

```bash
git add shared/contracts/command.schema.json shared/contracts/state.schema.json shared/contracts/telemetry.schema.json
git commit -m "feat: extend contracts for execute_task, base/hug state, telemetry metrics"
```

---

## Task 2: 通信契约扩展 — robot_msgs dataclass

**Files:**
- Modify: `robot-app/ros2_ws/src/robot_msgs/robot_msgs/contracts.py`
- Test: `robot-app/ros2_ws/src/robot_msgs/tests/test_contracts.py`

**Interfaces:**
- Consumes: Task 1 的 schema 定义
- Produces: `TaskCommandMsg`, `HugParamsMsg`, `BaseStateMsg`, `HugStateMsg`, 扩展的 `RobotStateMsg`

- [ ] **Step 1: 编写 dataclass 扩展测试**

在 `robot-app/ros2_ws/src/robot_msgs/tests/test_contracts.py` 中新增：

```python
"""Tests for dual-arm contract extensions."""
import pytest
from robot_msgs.contracts import (
    TaskCommandMsg, HugParamsMsg, BaseStateMsg, HugStateMsg,
    RobotStateMsg, Pose6DMsg,
)


def test_task_command_msg_creation():
    msg = TaskCommandMsg(
        command_id="cmd-001",
        task_type="pick_box",
        parameters={"target_pose": {"x": 0.5, "y": 0.0, "z": 0.3}},
    )
    assert msg.task_type == "pick_box"
    assert msg.speed_scale == 1.0


def test_task_command_msg_invalid_type():
    with pytest.raises(ValueError):
        TaskCommandMsg(command_id="cmd-001", task_type="invalid_task")


def test_hug_params_msg():
    msg = HugParamsMsg(pressure_target=50.0, approach_speed=0.2, close_speed=0.05)
    assert msg.pressure_target == 50.0


def test_base_state_msg():
    msg = BaseStateMsg(velocity=[0.5, 0.1], odom={"x": 1.0, "y": 2.0, "yaw": 0.3}, battery_soc=0.85)
    d = msg.to_dict()
    assert d["battery_soc"] == 0.85


def test_hug_state_msg():
    msg = HugStateMsg(pressure_l=30.0, pressure_r=32.0, state="holding")
    assert msg.state == "holding"


def test_robot_state_msg_with_base_and_hug():
    msg = RobotStateMsg(
        device_id="loader-01",
        base=BaseStateMsg(velocity=[0.0, 0.0], odom={"x": 0, "y": 0, "yaw": 0}, battery_soc=1.0),
        hug=HugStateMsg(pressure_l=0.0, pressure_r=0.0, state="open"),
    )
    d = msg.to_dict()
    assert "base" in d
    assert "hug" in d
    assert d["hug"]["state"] == "open"
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd robot-app/ros2_ws/src/robot_msgs && python -m pytest tests/test_contracts.py -v`
Expected: FAIL — `TaskCommandMsg`, `HugParamsMsg` 等未定义

- [ ] **Step 3: 实现 dataclass 扩展**

在 `robot-app/ros2_ws/src/robot_msgs/robot_msgs/contracts.py` 中新增：

```python
# Task types for execute_task command
TASK_TYPES: tuple[str, ...] = (
    "goto",
    "dock",
    "pick_box",
    "place_box",
    "transport",
    "hug_close",
    "hug_release",
    "home_all",
)

# Hug states
HUG_STATES: tuple[str, ...] = ("closed", "holding", "open")


@dataclass(slots=True)
class HugParamsMsg:
    """Parameters for hug grasp control."""
    pressure_target: float = 50.0
    approach_speed: float = 0.2
    close_speed: float = 0.05

    def to_dict(self) -> dict[str, float]:
        return {
            "pressure_target": self.pressure_target,
            "approach_speed": self.approach_speed,
            "close_speed": self.close_speed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HugParamsMsg":
        return cls(
            pressure_target=float(data.get("pressure_target", 50.0)),
            approach_speed=float(data.get("approach_speed", 0.2)),
            close_speed=float(data.get("close_speed", 0.05)),
        )


@dataclass(slots=True)
class TaskCommandMsg:
    """Task-level command for execute_task."""
    command_id: str = ""
    task_type: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    speed_scale: float = 1.0
    group: str | None = None

    def __post_init__(self) -> None:
        if self.task_type and self.task_type not in TASK_TYPES:
            raise ValueError(
                f"unknown task_type {self.task_type!r}; expected one of {TASK_TYPES}"
            )
        if not 0.0 <= self.speed_scale <= 10.0:
            raise ValueError(f"speed_scale out of range: {self.speed_scale}")


@dataclass(slots=True)
class BaseStateMsg:
    """AGV base state."""
    velocity: list[float] = field(default_factory=lambda: [0.0, 0.0])
    odom: dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "yaw": 0.0})
    battery_soc: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "velocity": list(self.velocity),
            "odom": dict(self.odom),
            "battery_soc": self.battery_soc,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseStateMsg":
        return cls(
            velocity=[float(v) for v in data.get("velocity", [0.0, 0.0])],
            odom={k: float(v) for k, v in (data.get("odom") or {"x": 0, "y": 0, "yaw": 0}).items()},
            battery_soc=float(data.get("battery_soc", 1.0)),
        )


@dataclass(slots=True)
class HugStateMsg:
    """Hug grasp state."""
    pressure_l: float = 0.0
    pressure_r: float = 0.0
    state: str = "open"

    def __post_init__(self) -> None:
        if self.state not in HUG_STATES:
            raise ValueError(f"unknown hug state {self.state!r}; expected one of {HUG_STATES}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "pressure_l": self.pressure_l,
            "pressure_r": self.pressure_r,
            "state": self.state,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HugStateMsg":
        return cls(
            pressure_l=float(data.get("pressure_l", 0.0)),
            pressure_r=float(data.get("pressure_r", 0.0)),
            state=str(data.get("state", "open")),
        )
```

扩展 `RobotStateMsg`：

```python
@dataclass(slots=True)
class RobotStateMsg:
    device_id: str
    joint: JointStateMsg = field(default_factory=JointStateMsg)
    err: TrackingErrorMsg = field(default_factory=TrackingErrorMsg)
    ctrl: ControllerStateMsg = field(default_factory=ControllerStateMsg)
    base: BaseStateMsg | None = None
    hug: HugStateMsg | None = None
    iso_ts: str = ""
    degraded: bool = False

    def __post_init__(self) -> None:
        if not self.iso_ts:
            self.iso_ts = utc_now_iso()

    def to_dict(self) -> dict[str, Any]:
        result = {
            "device_id": self.device_id,
            "joint": self.joint.to_dict(),
            "err": self.err.to_dict(),
            "ctrl": self.ctrl.to_dict(),
            "iso_ts": self.iso_ts,
            "degraded": self.degraded,
        }
        if self.base is not None:
            result["base"] = self.base.to_dict()
        if self.hug is not None:
            result["hug"] = self.hug.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RobotStateMsg":
        return cls(
            device_id=str(data["device_id"]),
            joint=JointStateMsg.from_dict(data.get("joint") or {}),
            err=TrackingErrorMsg.from_dict(data.get("err") or {}),
            ctrl=ControllerStateMsg.from_dict(data.get("ctrl") or {}),
            base=BaseStateMsg.from_dict(data["base"]) if "base" in data else None,
            hug=HugStateMsg.from_dict(data["hug"]) if "hug" in data else None,
            iso_ts=str(data.get("iso_ts", "")),
            degraded=bool(data.get("degraded", False)),
        )
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd robot-app/ros2_ws/src/robot_msgs && python -m pytest tests/test_contracts.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add robot-app/ros2_ws/src/robot_msgs/robot_msgs/contracts.py robot-app/ros2_ws/src/robot_msgs/tests/test_contracts.py
git commit -m "feat: add TaskCommandMsg, HugParamsMsg, BaseStateMsg, HugStateMsg; extend RobotStateMsg"
```

---

## Task 3: Pydantic 契约扩展

**Files:**
- Modify: `shared/python/robot_contracts/payloads.py`
- Test: `shared/python/tests/test_payloads.py`

**Interfaces:**
- Consumes: Task 1 的 schema 定义
- Produces: `TaskCommandPayload`, `HugParamsPayload`, `BaseStatePayload`, `HugStatePayload`, 扩展的 `StatePayload`

- [ ] **Step 1: 编写 Pydantic 扩展测试**

在 `shared/python/tests/test_payloads.py` 中新增：

```python
"""Tests for dual-arm payload extensions."""
import pytest
from robot_contracts.payloads import (
    TaskCommandPayload, HugParamsPayload, BaseStatePayload, HugStatePayload,
    CommandTypeEnum, StatePayload,
)


def test_execute_task_in_command_type_enum():
    assert CommandTypeEnum.EXECUTE_TASK == "execute_task"


def test_task_command_payload():
    p = TaskCommandPayload(
        command_id="cmd-001",
        task_type="pick_box",
        parameters={"target_pose": {"x": 0.5}},
    )
    assert p.task_type == "pick_box"


def test_hug_params_payload():
    p = HugParamsPayload(pressure_target=50.0, approach_speed=0.2, close_speed=0.05)
    assert p.pressure_target == 50.0


def test_base_state_payload():
    p = BaseStatePayload(velocity=[0.5, 0.1], odom={"x": 1.0, "y": 2.0, "yaw": 0.3}, battery_soc=0.85)
    d = p.model_dump()
    assert d["battery_soc"] == 0.85


def test_hug_state_payload():
    p = HugStatePayload(pressure_l=30.0, pressure_r=32.0, state="holding")
    assert p.state == "holding"


def test_state_payload_with_base_and_hug():
    p = StatePayload(
        device_id="loader-01",
        iso_ts="2026-08-09T00:00:00Z",
        base=BaseStatePayload(velocity=[0.0, 0.0], odom={"x": 0, "y": 0, "yaw": 0}, battery_soc=1.0),
        hug=HugStatePayload(pressure_l=0.0, pressure_r=0.0, state="open"),
    )
    d = p.model_dump()
    assert "base" in d
    assert "hug" in d
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd shared/python && python -m pytest tests/test_payloads.py -v`
Expected: FAIL — 新类未定义

- [ ] **Step 3: 实现 Pydantic 扩展**

在 `shared/python/robot_contracts/payloads.py` 中：

1. `CommandTypeEnum` 新增 `EXECUTE_TASK = "execute_task"`
2. 新增 `HugParamsPayload`, `BaseStatePayload`, `HugStatePayload`
3. 新增 `TaskCommandPayload`
4. `StatePayload` 新增 `base`, `hug` 字段（可选）
5. `ControllerStatePayload` 新增 `phase` 字段（可选）

```python
class HugParamsPayload(BaseModel):
    pressure_target: float = 50.0
    approach_speed: float = 0.2
    close_speed: float = 0.05


class TaskCommandPayload(BaseModel):
    command_id: str | None = None
    task_type: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    speed_scale: float = Field(default=1.0, ge=0.0, le=10.0)
    group: str | None = None


class BaseStatePayload(BaseModel):
    velocity: list[float] = Field(default_factory=lambda: [0.0, 0.0])
    odom: dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0, "yaw": 0.0})
    battery_soc: float = 1.0


class HugStatePayload(BaseModel):
    pressure_l: float = 0.0
    pressure_r: float = 0.0
    state: str = "open"
```

扩展 `StatePayload`：
```python
class StatePayload(BaseModel):
    device_id: str
    joint: JointStatePayload | None = None
    err: TrackingErrorPayload | None = None
    ctrl: ControllerStatePayload | None = None
    base: BaseStatePayload | None = None
    hug: HugStatePayload | None = None
    iso_ts: str
    degraded: bool = False
    model_config = {"extra": "allow"}
```

扩展 `ControllerStatePayload`：
```python
class ControllerStatePayload(BaseModel):
    mode: str
    phase: str | None = None
    active_command_id: str | None = None
    last_error: str | None = None
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd shared/python && python -m pytest tests/test_payloads.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add shared/python/robot_contracts/payloads.py shared/python/tests/test_payloads.py
git commit -m "feat: add TaskCommandPayload, HugParamsPayload, BaseStatePayload, HugStatePayload"
```

---

## Task 4: Gateway 契约解码与桥接扩展

**Files:**
- Modify: `robot-app/ros2_ws/src/robot_gateway/robot_gateway/contract.py`
- Modify: `robot-app/ros2_ws/src/robot_gateway/robot_gateway/bridge.py`
- Test: `robot-app/ros2_ws/src/robot_gateway/tests/test_contract.py`
- Test: `robot-app/ros2_ws/src/robot_gateway/tests/test_bridge.py`

**Interfaces:**
- Consumes: Task 2 的 `TaskCommandMsg`；Task 3 的 `TaskCommandPayload`
- Produces: `decode_task_command()`, `MqttBridge` 新增 `task_sink` 参数

- [ ] **Step 1: 编写 gateway 扩展测试**

在 `robot-app/ros2_ws/src/robot_gateway/tests/test_contract.py` 中新增：

```python
"""Tests for execute_task decoding."""
import json
import pytest
from robot_gateway.contract import decode_task_command, ContractError


def test_decode_execute_task_pick_box():
    raw = json.dumps({
        "type": "execute_task",
        "command_id": "cmd-001",
        "task_type": "pick_box",
        "parameters": {"target_pose": {"x": 0.5, "y": 0.0, "z": 0.3}},
        "speed_scale": 0.8,
    }).encode()
    msg = decode_task_command(raw)
    assert msg.task_type == "pick_box"
    assert msg.speed_scale == 0.8
    assert msg.parameters["target_pose"]["x"] == 0.5


def test_decode_execute_task_invalid_task_type():
    raw = json.dumps({
        "type": "execute_task",
        "task_type": "invalid_task",
    }).encode()
    with pytest.raises(ContractError):
        decode_task_command(raw)
```

在 `robot-app/ros2_ws/src/robot_gateway/tests/test_bridge.py` 中新增：

```python
"""Tests for task_sink routing."""
from unittest.mock import MagicMock
from robot_gateway.bridge import MqttBridge
from robot_msgs import TaskCommandMsg


def test_bridge_routes_execute_task_to_task_sink():
    link = MagicMock()
    motion_sink = MagicMock()
    task_sink = MagicMock()
    bridge = MqttBridge(
        link, device_id="loader-01",
        motion_sink=motion_sink, task_sink=task_sink,
    )
    # Simulate inbound execute_task command
    raw = json.dumps({
        "type": "execute_task",
        "command_id": "cmd-001",
        "task_type": "goto",
        "parameters": {"target_pose": {"x": 1.0, "y": 2.0, "z": 0.0}},
    }).encode()
    bridge.handle_command_message("rcs/loader-01/command", raw)
    task_sink.assert_called_once()
    motion_sink.assert_not_called()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd robot-app/ros2_ws/src/robot_gateway && python -m pytest tests/test_contract.py tests/test_bridge.py -v`
Expected: FAIL — `decode_task_command`, `task_sink` 未定义

- [ ] **Step 3: 实现 contract.py 扩展**

在 `robot-app/ros2_ws/src/robot_gateway/robot_gateway/contract.py` 中新增：

```python
from robot_msgs import TaskCommandMsg


def decode_task_command(raw: bytes) -> TaskCommandMsg:
    """Decode an execute_task command payload."""
    data = _loads(raw)
    task_type = str(data.get("task_type", ""))
    if not task_type:
        raise ContractError("execute_task requires task_type")
    try:
        return TaskCommandMsg(
            command_id=str(data.get("command_id") or ""),
            task_type=task_type,
            parameters=dict(data.get("parameters") or {}),
            speed_scale=float(data.get("speed_scale", 1.0)),
            group=data.get("group"),
        )
    except (ValueError, TypeError) as exc:
        raise ContractError(f"invalid execute_task payload: {exc}") from exc
```

- [ ] **Step 4: 实现 bridge.py 扩展**

在 `robot-app/ros2_ws/src/robot_gateway/robot_gateway/bridge.py` 中：

1. `MqttBridge.__init__` 新增 `task_sink` 参数
2. `handle_command_message` 路由逻辑：`execute_task` → `task_sink`

```python
def __init__(
    self,
    link: SupportsPublish,
    *,
    device_id: str,
    motion_sink: Callable[[CommandMsg], None],
    estop_sink: Callable[[CommandMsg], None] | None = None,
    task_sink: Callable[[TaskCommandMsg], None] | None = None,
    topic_prefix: str = "",
) -> None:
    self._link = link
    self._device_id = device_id
    self._motion_sink = motion_sink
    self._estop_sink = estop_sink or motion_sink
    self._task_sink = task_sink
    self._topic_prefix = topic_prefix
    # ... counters ...
```

在 `handle_command_message` 中：

```python
# Route execute_task to task_sink
if command.type == "execute_task":
    if self._task_sink is None:
        self.commands_rejected += 1
        logger.warning("execute_task received but no task_sink configured")
        return
    try:
        task_msg = decode_task_command(raw)
    except ContractError as exc:
        self.commands_rejected += 1
        logger.warning("execute_task payload rejected: %s", exc)
        return
    try:
        self._task_sink(task_msg)
    except Exception:
        self.commands_rejected += 1
        logger.exception("task_sink raised for %s", task_msg.task_type)
        return
    self.commands_accepted += 1
    return

# Existing routing for move_j/move_l/estop/etc.
sink = self._estop_sink if command.is_emergency else self._motion_sink
```

- [ ] **Step 5: 运行测试验证通过**

Run: `cd robot-app/ros2_ws/src/robot_gateway && python -m pytest tests/test_contract.py tests/test_bridge.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add robot-app/ros2_ws/src/robot_gateway/
git commit -m "feat: add task_sink to MqttBridge, decode_task_command for execute_task"
```

---

## Task 5: robot_base_hal 包创建

**Files:**
- Create: `robot-app/ros2_ws/src/robot_base_hal/urdf/base.ros2_control.xacro`
- Create: `robot-app/ros2_ws/src/robot_base_hal/urdf/base.urdf.xacro`
- Create: `robot-app/ros2_ws/src/robot_base_hal/robot_base_hal/__init__.py`
- Create: `robot-app/ros2_ws/src/robot_base_hal/setup.py`
- Create: `robot-app/ros2_ws/src/robot_base_hal/package.xml`
- Create: `robot-app/ros2_ws/src/robot_base_hal/resource/index/ament_index_resource_path`

**Interfaces:**
- Consumes: 无
- Produces: 差速底盘 URDF + ros2_control 配置（2 驱动轮速度接口）

- [ ] **Step 1: 创建包结构**

```bash
cd robot-app/ros2_ws/src
mkdir -p robot_base_hal/urdf robot_base_hal/robot_base_hal robot_base_hal/resource
touch robot_base_hal/robot_base_hal/__init__.py
touch robot_base_hal/resource/ament_index_resource_path
echo "share" > robot_base_hal/resource/ament_index_resource_path
```

- [ ] **Step 2: 创建 package.xml**

```xml
<?xml version="1.0"?>
<package format="3">
  <name>robot_base_hal</name>
  <version>0.1.0</version>
  <description>AGV diff-drive base HAL for loading robot</description>
  <maintainer email="dev@robot-logic">robot-logic</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <exec_depend>xacro</exec_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

- [ ] **Step 3: 创建 setup.py (空，ament_cmake 包)**

```python
from setuptools import setup
setup()
```

- [ ] **Step 4: 创建 base.ros2_control.xacro**

```xml
<?xml version="1.0"?>
<!--
  base.ros2_control.xacro
  Diff-drive base hardware interface for AGV loading robot.
  Two wheel joints (left_wheel, right_wheel) with velocity command interfaces.
-->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <xacro:macro name="base_ros2_control" params="name use_fake_hardware:=true use_gazebo:=false">

    <ros2_control name="${name}" type="system">

      <xacro:if value="${use_gazebo}">
        <hardware>
          <plugin>gz_ros2_control/GzSystem</plugin>
        </hardware>
      </xacro:if>

      <xacro:unless value="${use_gazebo}">
        <hardware>
          <plugin>mock_components/GenericSystem</plugin>
          <param name="mock_sensor_commands">true</param>
        </hardware>
      </xacro:unless>

      <joint name="left_wheel">
        <command_interface name="velocity">
          <param name="min">-10.0</param>
          <param name="max">10.0</param>
        </command_interface>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
      </joint>

      <joint name="right_wheel">
        <command_interface name="velocity">
          <param name="min">-10.0</param>
          <param name="max">10.0</param>
        </command_interface>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
      </joint>

    </ros2_control>
  </xacro:macro>
</robot>
```

- [ ] **Step 5: 创建 base.urdf.xacro**

```xml
<?xml version="1.0"?>
<!--
  base.urdf.xacro
  AGV diff-drive base URDF. base_link is the TF root of the whole robot.
  Includes ros2_control hardware interface.
-->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="robot_base">

  <xacro:include filename="$(find robot_base_hal)/urdf/base.ros2_control.xacro"/>

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.8 0.6 0.3"/>
      </geometry>
      <origin xyz="0 0 0.15" rpy="0 0 0"/>
    </visual>
    <collision>
      <geometry>
        <box size="0.8 0.6 0.3"/>
      </geometry>
      <origin xyz="0 0 0.15" rpy="0 0 0"/>
    </collision>
    <inertial>
      <mass value="100.0"/>
      <inertia ixx="5.0" ixy="0" ixz="0" iyy="5.0" iyz="0" izz="5.0"/>
    </inertial>
  </link>

  <!-- Left wheel -->
  <link name="left_wheel_link">
    <visual>
      <geometry><cylinder radius="0.1" length="0.05"/></geometry>
    </visual>
    <collision>
      <geometry><cylinder radius="0.1" length="0.05"/></geometry>
    </collision>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </link>

  <joint name="left_wheel" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel_link"/>
    <origin xyz="0 0.3 0.1" rpy="-1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- Right wheel -->
  <link name="right_wheel_link">
    <visual>
      <geometry><cylinder radius="0.1" length="0.05"/></geometry>
    </visual>
    <collision>
      <geometry><cylinder radius="0.1" length="0.05"/></geometry>
    </collision>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </link>

  <joint name="right_wheel" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel_link"/>
    <origin xyz="0 -0.3 0.1" rpy="-1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <!-- Caster wheel (passive, no actuation) -->
  <link name="caster_link">
    <visual>
      <geometry><sphere radius="0.05"/></geometry>
    </visual>
    <collision>
      <geometry><sphere radius="0.05"/></geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <joint name="caster_joint" type="fixed">
    <parent link="base_link"/>
    <child link="caster_link"/>
    <origin xyz="-0.3 0 0.05" rpy="0 0 0"/>
  </joint>

  <!-- Torso mount point for dual arms -->
  <link name="torso_mount"/>
  <joint name="torso_mount_joint" type="fixed">
    <parent link="base_link"/>
    <child link="torso_mount"/>
    <origin xyz="0 0 0.3" rpy="0 0 0"/>
  </joint>

  <!-- ros2_control hardware interface -->
  <xacro:base_ros2_control name="base" use_fake_hardware="true" use_gazebo="false"/>

</robot>
```

- [ ] **Step 6: 验证 xacro 解析**

Run: `xacro robot-app/ros2_ws/src/robot_base_hal/urdf/base.urdf.xacro`
Expected: 输出有效 URDF XML

- [ ] **Step 7: Commit**

```bash
git add robot-app/ros2_ws/src/robot_base_hal/
git commit -m "feat: add robot_base_hal package with diff-drive URDF and ros2_control"
```

---

## Task 6: robot_dual_arm_hal 包创建

**Files:**
- Create: `robot-app/ros2_ws/src/robot_dual_arm_hal/urdf/dual_arm.ros2_control.xacro`
- Create: `robot-app/ros2_ws/src/robot_dual_arm_hal/urdf/loader.urdf.xacro`
- Create: `robot-app/ros2_ws/src/robot_dual_arm_hal/robot_dual_arm_hal/__init__.py`
- Create: `robot-app/ros2_ws/src/robot_dual_arm_hal/setup.py`
- Create: `robot-app/ros2_ws/src/robot_dual_arm_hal/package.xml`

**Interfaces:**
- Consumes: `robot_base_hal` 的底盘 URDF；`robot_arm_hal` 的单臂宏（复用几何定义）
- Produces: 双臂 URDF（关节名带 `left_`/`right_` 前缀）+ 整车组合 URDF

- [ ] **Step 1: 创建包结构**

```bash
cd robot-app/ros2_ws/src
mkdir -p robot_dual_arm_hal/urdf robot_dual_arm_hal/robot_dual_arm_hal
touch robot_dual_arm_hal/robot_dual_arm_hal/__init__.py
```

- [ ] **Step 2: 创建 package.xml**

```xml
<?xml version="1.0"?>
<package format="3">
  <name>robot_dual_arm_hal</name>
  <version>0.1.0</version>
  <description>Dual-arm HAL for AGV loading robot (left/right 6-DOF arms)</description>
  <maintainer email="dev@robot-logic">robot-logic</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <exec_depend>xacro</exec_depend>
  <exec_depend>robot_base_hal</exec_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

- [ ] **Step 3: 创建 dual_arm.ros2_control.xacro**

关键：所有关节名带 `${arm_id}_` 前缀（`left_shoulder_pan`, `right_shoulder_pan` 等），避免双臂实例化时关节名冲突。

```xml
<?xml version="1.0"?>
<!--
  dual_arm.ros2_control.xacro
  Dual-arm ros2_control hardware interface.
  Macro instantiates twice with arm_id=left/right.
  All joint names are prefixed with ${arm_id}_ to avoid duplicates.
-->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <xacro:macro name="dual_arm_ros2_control" params="arm_id use_fake_hardware:=true use_gazebo:=false">

    <ros2_control name="${arm_id}_arm" type="system">

      <xacro:if value="${use_gazebo}">
        <hardware>
          <plugin>gz_ros2_control/GzSystem</plugin>
        </hardware>
      </xacro:if>

      <xacro:unless value="${use_gazebo}">
        <hardware>
          <plugin>mock_components/GenericSystem</plugin>
          <param name="mock_sensor_commands">true</param>
        </hardware>
      </xacro:unless>

      <joint name="${arm_id}_shoulder_pan">
        <command_interface name="position"><param name="min">-3.14</param><param name="max">3.14</param></command_interface>
        <command_interface name="velocity"><param name="min">-3.15</param><param name="max">3.15</param></command_interface>
        <state_interface name="position"/><state_interface name="velocity"/>
      </joint>
      <joint name="${arm_id}_shoulder_lift">
        <command_interface name="position"><param name="min">-3.14</param><param name="max">3.14</param></command_interface>
        <command_interface name="velocity"><param name="min">-3.15</param><param name="max">3.15</param></command_interface>
        <state_interface name="position"/><state_interface name="velocity"/>
      </joint>
      <joint name="${arm_id}_elbow">
        <command_interface name="position"><param name="min">-3.14</param><param name="max">3.14</param></command_interface>
        <command_interface name="velocity"><param name="min">-3.15</param><param name="max">3.15</param></command_interface>
        <state_interface name="position"/><state_interface name="velocity"/>
      </joint>
      <joint name="${arm_id}_wrist_1">
        <command_interface name="position"><param name="min">-3.14</param><param name="max">3.14</param></command_interface>
        <command_interface name="velocity"><param name="min">-6.28</param><param name="max">6.28</param></command_interface>
        <state_interface name="position"/><state_interface name="velocity"/>
      </joint>
      <joint name="${arm_id}_wrist_2">
        <command_interface name="position"><param name="min">-3.14</param><param name="max">3.14</param></command_interface>
        <command_interface name="velocity"><param name="min">-6.28</param><param name="max">6.28</param></command_interface>
        <state_interface name="position"/><state_interface name="velocity"/>
      </joint>
      <joint name="${arm_id}_wrist_3">
        <command_interface name="position"><param name="min">-3.14</param><param name="max">3.14</param></command_interface>
        <command_interface name="velocity"><param name="min">-6.28</param><param name="max">6.28</param></command_interface>
        <state_interface name="position"/><state_interface name="velocity"/>
      </joint>
      <joint name="${arm_id}_paddle">
        <command_interface name="position"><param name="min">0.0</param><param name="max">0.15</param></command_interface>
        <state_interface name="position"/>
      </joint>

    </ros2_control>
  </xacro:macro>
</robot>
```

- [ ] **Step 4: 创建 loader.urdf.xacro（整车组合）**

```xml
<?xml version="1.0"?>
<!--
  loader.urdf.xacro
  Whole-robot composition: base + left arm + right arm.
  This is the entry URDF for the dual-arm AGV loading robot.
  TF tree: base_link -> torso_mount -> left_arm_base / right_arm_base
-->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="loading_robot">

  <!-- Base -->
  <xacro:include filename="$(find robot_base_hal)/urdf/base.urdf.xacro"/>

  <!-- Dual-arm ros2_control -->
  <xacro:include filename="$(find robot_dual_arm_hal)/urdf/dual_arm.ros2_control.xacro"/>

  <!-- Left arm kinematic chain -->
  <xacro:macro name="arm_chain" params="arm_id parent *origin">
    <link name="${arm_id}_arm_base"/>
    <joint name="${arm_id}_arm_mount" type="fixed">
      <xacro:insert_block name="origin"/>
      <parent link="${parent}"/>
      <child link="${arm_id}_arm_base"/>
    </joint>

    <link name="${arm_id}_shoulder_link">
      <visual><geometry><cylinder radius="0.06" length="0.15"/></geometry></visual>
      <collision><geometry><cylinder radius="0.06" length="0.15"/></geometry></collision>
      <inertial><mass value="5.0"/><inertia ixx="0.02" ixy="0" ixz="0" iyy="0.02" iyz="0" izz="0.01"/></inertial>
    </link>
    <joint name="${arm_id}_shoulder_pan" type="revolute">
      <parent link="${arm_id}_arm_base"/>
      <child link="${arm_id}_shoulder_link"/>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
      <axis xyz="0 0 1"/><limit lower="-3.14" upper="3.14" velocity="3.15" effort="100"/>
    </joint>

    <link name="${arm_id}_upper_arm_link">
      <visual><geometry><cylinder radius="0.05" length="0.3"/></geometry></visual>
      <collision><geometry><cylinder radius="0.05" length="0.3"/></geometry></collision>
      <inertial><mass value="8.0"/><inertia ixx="0.05" ixy="0" ixz="0" iyy="0.05" iyz="0" izz="0.01"/></inertial>
    </link>
    <joint name="${arm_id}_shoulder_lift" type="revolute">
      <parent link="${arm_id}_shoulder_link"/>
      <child link="${arm_id}_upper_arm_link"/>
      <origin xyz="0 0 0.15" rpy="0 0 0"/>
      <axis xyz="0 1 0"/><limit lower="-3.14" upper="3.14" velocity="3.15" effort="100"/>
    </joint>

    <link name="${arm_id}_forearm_link">
      <visual><geometry><cylinder radius="0.04" length="0.25"/></geometry></visual>
      <collision><geometry><cylinder radius="0.04" length="0.25"/></geometry></collision>
      <inertial><mass value="5.0"/><inertia ixx="0.03" ixy="0" ixz="0" iyy="0.03" iyz="0" izz="0.005"/></inertial>
    </link>
    <joint name="${arm_id}_elbow" type="revolute">
      <parent link="${arm_id}_upper_arm_link"/>
      <child link="${arm_id}_forearm_link"/>
      <origin xyz="0 0 0.3" rpy="0 0 0"/>
      <axis xyz="0 1 0"/><limit lower="-3.14" upper="3.14" velocity="3.15" effort="100"/>
    </joint>

    <link name="${arm_id}_wrist_1_link">
      <visual><geometry><cylinder radius="0.035" length="0.1"/></geometry></visual>
      <collision><geometry><cylinder radius="0.035" length="0.1"/></geometry></collision>
      <inertial><mass value="2.0"/><inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.002"/></inertial>
    </link>
    <joint name="${arm_id}_wrist_1" type="revolute">
      <parent link="${arm_id}_forearm_link"/>
      <child link="${arm_id}_wrist_1_link"/>
      <origin xyz="0 0 0.25" rpy="0 0 0"/>
      <axis xyz="0 1 0"/><limit lower="-3.14" upper="3.14" velocity="6.28" effort="50"/>
    </joint>

    <link name="${arm_id}_wrist_2_link">
      <visual><geometry><cylinder radius="0.03" length="0.08"/></geometry></visual>
      <collision><geometry><cylinder radius="0.03" length="0.08"/></geometry></collision>
      <inertial><mass value="1.5"/><inertia ixx="0.003" ixy="0" ixz="0" iyy="0.003" iyz="0" izz="0.001"/></inertial>
    </link>
    <joint name="${arm_id}_wrist_2" type="revolute">
      <parent link="${arm_id}_wrist_1_link"/>
      <child link="${arm_id}_wrist_2_link"/>
      <origin xyz="0 0 0.1" rpy="0 0 0"/>
      <axis xyz="0 0 1"/><limit lower="-3.14" upper="3.14" velocity="6.28" effort="50"/>
    </joint>

    <link name="${arm_id}_wrist_3_link">
      <visual><geometry><cylinder radius="0.025" length="0.06"/></geometry></visual>
      <collision><geometry><cylinder radius="0.025" length="0.06"/></geometry></collision>
      <inertial><mass value="1.0"/><inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.0005"/></inertial>
    </link>
    <joint name="${arm_id}_wrist_3" type="revolute">
      <parent link="${arm_id}_wrist_2_link"/>
      <child link="${arm_id}_wrist_3_link"/>
      <origin xyz="0 0 0.08" rpy="0 0 0"/>
      <axis xyz="0 1 0"/><limit lower="-3.14" upper="3.14" velocity="6.28" effort="50"/>
    </joint>

    <!-- TCP frame (tool center point) -->
    <link name="${arm_id}_tcp_frame"/>
    <joint name="${arm_id}_tcp_joint" type="fixed">
      <parent link="${arm_id}_wrist_3_link"/>
      <child link="${arm_id}_tcp_frame"/>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
    </joint>

    <!-- Paddle (hug grasp end-effector) -->
    <link name="${arm_id}_paddle_link">
      <visual><geometry><box size="0.15 0.02 0.1"/></geometry></visual>
      <collision><geometry><box size="0.15 0.02 0.1"/></geometry></collision>
      <inertial><mass value="0.5"/><inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.0005"/></inertial>
    </link>
    <joint name="${arm_id}_paddle" type="prismatic">
      <parent link="${arm_id}_tcp_frame"/>
      <child link="${arm_id}_paddle_link"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <axis xyz="0 1 0"/><limit lower="0" upper="0.15" velocity="0.5" effort="50"/>
    </joint>
  </xacro:macro>

  <!-- Instantiate left arm -->
  <xacro:arm_chain arm_id="left" parent="torso_mount">
    <origin xyz="0 0.2 0.1" rpy="0 0 1.5708"/>
  </xacro:arm_chain>

  <!-- Instantiate right arm -->
  <xacro:arm_chain arm_id="right" parent="torso_mount">
    <origin xyz="0 -0.2 0.1" rpy="0 0 -1.5708"/>
  </xacro:arm_chain>

  <!-- ros2_control for both arms -->
  <xacro:dual_arm_ros2_control arm_id="left" use_fake_hardware="true" use_gazebo="false"/>
  <xacro:dual_arm_ros2_control arm_id="right" use_fake_hardware="true" use_gazebo="false"/>

</robot>
```

- [ ] **Step 5: 验证 xacro 解析**

Run: `xacro robot-app/ros2_ws/src/robot_dual_arm_hal/urdf/loader.urdf.xacro`
Expected: 输出有效 URDF XML，包含 `left_shoulder_pan`, `right_shoulder_pan` 等关节

- [ ] **Step 6: Commit**

```bash
git add robot-app/ros2_ws/src/robot_dual_arm_hal/
git commit -m "feat: add robot_dual_arm_hal with left/right arm URDF and loader composition"
```

---

## Task 7: MoveIt SRDF 迁移

**Files:**
- Modify: `simulation/ros2_ws/src/robot_moveit_config/config/robot.srdf`

**Interfaces:**
- Consumes: Task 6 的双臂 URDF（关节名 `left_*`, `right_*`）
- Produces: 新增 `left_arm`, `right_arm`, `dual_arm` 规划组 + `disable_collisions` + `group_state`

- [ ] **Step 1: 备份现有 SRDF**

```bash
cp simulation/ros2_ws/src/robot_moveit_config/config/robot.srdf simulation/ros2_ws/src/robot_moveit_config/config/robot.srdf.bak
```

- [ ] **Step 2: 扩展 SRDF — 新增规划组**

在 `simulation/ros2_ws/src/robot_moveit_config/config/robot.srdf` 中，保留现有 `manipulator` 和 `gripper` 组，新增：

```xml
  <!-- Dual-arm planning groups -->
  <group name="left_arm">
    <chain base_link="left_arm_base" tip_link="left_tcp_frame"/>
  </group>

  <group name="right_arm">
    <chain base_link="right_arm_base" tip_link="right_tcp_frame"/>
  </group>

  <group name="dual_arm">
    <joint name="left_shoulder_pan"/>
    <joint name="left_shoulder_lift"/>
    <joint name="left_elbow"/>
    <joint name="left_wrist_1"/>
    <joint name="left_wrist_2"/>
    <joint name="left_wrist_3"/>
    <joint name="right_shoulder_pan"/>
    <joint name="right_shoulder_lift"/>
    <joint name="right_elbow"/>
    <joint name="right_wrist_1"/>
    <joint name="right_wrist_2"/>
    <joint name="right_wrist_3"/>
  </group>

  <!-- End-effectors for dual arms -->
  <end_effector name="left_paddle_ee" parent_link="left_tcp_frame" parent_group="left_arm"/>
  <end_effector name="right_paddle_ee" parent_link="right_tcp_frame" parent_group="right_arm"/>
```

- [ ] **Step 3: 扩展 disable_collisions**

新增双臂之间、臂与底盘之间的自碰撞对：

```xml
  <!-- Cross-arm disable collisions -->
  <disable_collisions link1="left_shoulder_link" link2="right_shoulder_link" reason="never"/>
  <disable_collisions link1="left_upper_arm_link" link2="right_upper_arm_link" reason="never"/>
  <disable_collisions link1="left_forearm_link" link2="right_forearm_link" reason="never"/>
  <disable_collisions link1="left_wrist_1_link" link2="right_wrist_1_link" reason="never"/>
  <disable_collisions link1="left_wrist_2_link" link2="right_wrist_2_link" reason="never"/>
  <disable_collisions link1="left_wrist_3_link" link2="right_wrist_3_link" reason="never"/>
  <disable_collisions link1="left_paddle_link" link2="right_paddle_link" reason="never"/>

  <!-- Arm-to-base disable collisions -->
  <disable_collisions link1="base_link" link2="left_shoulder_link" reason="never"/>
  <disable_collisions link1="base_link" link2="left_upper_arm_link" reason="never"/>
  <disable_collisions link1="base_link" link2="right_shoulder_link" reason="never"/>
  <disable_collisions link1="base_link" link2="right_upper_arm_link" reason="never"/>
  <disable_collisions link1="torso_mount" link2="left_shoulder_link" reason="never"/>
  <disable_collisions link1="torso_mount" link2="right_shoulder_link" reason="never"/>
```

- [ ] **Step 4: 新增 group_state**

```xml
  <group_state name="left_home" group="left_arm">
    <joint name="left_shoulder_pan" value="0"/>
    <joint name="left_shoulder_lift" value="-1.57"/>
    <joint name="left_elbow" value="1.57"/>
    <joint name="left_wrist_1" value="-1.57"/>
    <joint name="left_wrist_2" value="-1.57"/>
    <joint name="left_wrist_3" value="0"/>
  </group_state>

  <group_state name="right_home" group="right_arm">
    <joint name="right_shoulder_pan" value="0"/>
    <joint name="right_shoulder_lift" value="-1.57"/>
    <joint name="right_elbow" value="1.57"/>
    <joint name="right_wrist_1" value="-1.57"/>
    <joint name="right_wrist_2" value="-1.57"/>
    <joint name="right_wrist_3" value="0"/>
  </group_state>

  <group_state name="stowed" group="dual_arm">
    <joint name="left_shoulder_pan" value="0"/>
    <joint name="left_shoulder_lift" value="-1.57"/>
    <joint name="left_elbow" value="1.57"/>
    <joint name="left_wrist_1" value="-1.57"/>
    <joint name="left_wrist_2" value="-1.57"/>
    <joint name="left_wrist_3" value="0"/>
    <joint name="right_shoulder_pan" value="0"/>
    <joint name="right_shoulder_lift" value="-1.57"/>
    <joint name="right_elbow" value="1.57"/>
    <joint name="right_wrist_1" value="-1.57"/>
    <joint name="right_wrist_2" value="-1.57"/>
    <joint name="right_wrist_3" value="0"/>
  </group_state>
```

- [ ] **Step 5: 验证 SRDF XML 语法**

Run: `python -c "import xml.etree.ElementTree as ET; ET.parse('simulation/ros2_ws/src/robot_moveit_config/config/robot.srdf')"`
Expected: 无报错

- [ ] **Step 6: Commit**

```bash
git add simulation/ros2_ws/src/robot_moveit_config/config/robot.srdf
git commit -m "feat: migrate SRDF for dual-arm (left_arm/right_arm/dual_arm groups)"
```

---

## Task 8: MoveIt 控制器配置迁移

**Files:**
- Modify: `simulation/ros2_ws/src/robot_moveit_config/config/ros2_controllers.yaml`
- Modify: `simulation/ros2_ws/src/robot_moveit_config/config/kinematics.yaml`
- Modify: `simulation/ros2_ws/src/robot_moveit_config/config/ompl_planning.yaml`
- Modify: `simulation/ros2_ws/src/robot_moveit_config/config/joint_limits.yaml`

**Interfaces:**
- Consumes: Task 6 的双臂 URDF（关节名）；Task 7 的 SRDF 规划组
- Produces: 双臂控制器配置（left/right_arm_controller, paddle_controllers, diff_drive_controller）

- [ ] **Step 1: 扩展 ros2_controllers.yaml**

在 `simulation/ros2_ws/src/robot_moveit_config/config/ros2_controllers.yaml` 中新增：

```yaml
    left_arm_controller:
      type: joint_trajectory_controller/JointTrajectoryController

    right_arm_controller:
      type: joint_trajectory_controller/JointTrajectoryController

    left_paddle_controller:
      type: position_controllers/JointGroupPositionController

    right_paddle_controller:
      type: position_controllers/JointGroupPositionController

    diff_drive_controller:
      type: diff_drive_controller/DiffDriveController

left_arm_controller:
  ros__parameters:
    joints:
      - left_shoulder_pan
      - left_shoulder_lift
      - left_elbow
      - left_wrist_1
      - left_wrist_2
      - left_wrist_3
    command_interfaces: [position]
    state_interfaces: [position, velocity]
    state_publish_rate: 100.0
    action_monitor_rate: 20.0
    allow_partial_joints_goal: false
    open_loop_control: true
    constraints:
      stopped_velocity_tolerance: 0.01
      left_shoulder_pan: { trajectory: 0.20, goal: 0.05 }
      left_shoulder_lift: { trajectory: 0.20, goal: 0.05 }
      left_elbow: { trajectory: 0.20, goal: 0.05 }
      left_wrist_1: { trajectory: 0.30, goal: 0.08 }
      left_wrist_2: { trajectory: 0.30, goal: 0.08 }
      left_wrist_3: { trajectory: 0.30, goal: 0.08 }

right_arm_controller:
  ros__parameters:
    joints:
      - right_shoulder_pan
      - right_shoulder_lift
      - right_elbow
      - right_wrist_1
      - right_wrist_2
      - right_wrist_3
    command_interfaces: [position]
    state_interfaces: [position, velocity]
    state_publish_rate: 100.0
    action_monitor_rate: 20.0
    allow_partial_joints_goal: false
    open_loop_control: true
    constraints:
      stopped_velocity_tolerance: 0.01
      right_shoulder_pan: { trajectory: 0.20, goal: 0.05 }
      right_shoulder_lift: { trajectory: 0.20, goal: 0.05 }
      right_elbow: { trajectory: 0.20, goal: 0.05 }
      right_wrist_1: { trajectory: 0.30, goal: 0.08 }
      right_wrist_2: { trajectory: 0.30, goal: 0.08 }
      right_wrist_3: { trajectory: 0.30, goal: 0.08 }

left_paddle_controller:
  ros__parameters:
    joints: [left_paddle]

right_paddle_controller:
  ros__parameters:
    joints: [right_paddle]

diff_drive_controller:
  ros__parameters:
    left_wheel_names: [left_wheel]
    right_wheel_names: [right_wheel]
    wheel_separation: 0.6
    wheel_radius: 0.1
    publish_rate: 50.0
    odom_frame_id: odom
    base_frame_id: base_link
    pose_covariance_diagonal: [0.001, 0.001, 0.001, 0.001, 0.001, 0.01]
    twist_covariance_diagonal: [0.001, 0.001, 0.001, 0.01, 0.01, 0.01]
    enable_odom_tf: true
```

- [ ] **Step 2: 扩展 kinematics.yaml**

```yaml
/**:
  ros__parameters:
    manipulator:
      kinematics_solver: kdl_kinematics_plugin/KDLKinematicsPlugin
      kinematics_solver_search_resolution: 0.005
      kinematics_solver_timeout: 0.05
      kinematics_solver_attempts: 3
    left_arm:
      kinematics_solver: kdl_kinematics_plugin/KDLKinematicsPlugin
      kinematics_solver_search_resolution: 0.005
      kinematics_solver_timeout: 0.05
      kinematics_solver_attempts: 3
    right_arm:
      kinematics_solver: kdl_kinematics_plugin/KDLKinematicsPlugin
      kinematics_solver_search_resolution: 0.005
      kinematics_solver_timeout: 0.05
      kinematics_solver_attempts: 3
    dual_arm:
      kinematics_solver: kdl_kinematics_plugin/KDLKinematicsPlugin
      kinematics_solver_search_resolution: 0.005
      kinematics_solver_timeout: 0.1
      kinematics_solver_attempts: 3
```

- [ ] **Step 3: 扩展 ompl_planning.yaml**

```yaml
/**:
  ros__parameters:
    ompl:
      planning_plugins: ["ompl_interface/OMPLPlanner"]
      default_planner_config: RRTConnectConfigDefault
      planner_configs:
        RRTConnectConfigDefault:
          type: geometric::RRTConnect
          range: 0.5
          goal_bias: 0.05
        RRTstarkConfigDefault:
          type: geometric::RRTstar
          range: 0.5
          goal_bias: 0.05
          delay_collision_checking: 1
        AnytimeConfigDefault:
          type: geometric::AnytimePathShortening
          shortcut: true
          hybridize: true
          max_hybridization: 10
          simplify_solutions: true
      # Per-group planner overrides
      left_arm:
        planner_configs:
          - RRTConnectConfigDefault
      right_arm:
        planner_configs:
          - RRTConnectConfigDefault
      dual_arm:
        planner_configs:
          - RRTstarkConfigDefault
```

- [ ] **Step 4: 扩展 joint_limits.yaml**

```yaml
/**:
  ros__parameters:
    robot_description_planning:
      joint_limits:
        # ... existing single-arm limits ...
        left_shoulder_pan:
          has_position_limits: true
          min_position: -3.14
          max_position: 3.14
          has_velocity_limits: true
          max_velocity: 3.15
          has_acceleration_limits: true
          max_acceleration: 5.0
        left_shoulder_lift:
          has_position_limits: true
          min_position: -3.14
          max_position: 3.14
          has_velocity_limits: true
          max_velocity: 3.15
          has_acceleration_limits: true
          max_acceleration: 5.0
        left_elbow:
          has_position_limits: true
          min_position: -3.14
          max_position: 3.14
          has_velocity_limits: true
          max_velocity: 3.15
          has_acceleration_limits: true
          max_acceleration: 5.0
        left_wrist_1:
          has_position_limits: true
          min_position: -3.14
          max_position: 3.14
          has_velocity_limits: true
          max_velocity: 6.28
          has_acceleration_limits: true
          max_acceleration: 8.0
        left_wrist_2:
          has_position_limits: true
          min_position: -3.14
          max_position: 3.14
          has_velocity_limits: true
          max_velocity: 6.28
          has_acceleration_limits: true
          max_acceleration: 8.0
        left_wrist_3:
          has_position_limits: true
          min_position: -3.14
          max_position: 3.14
          has_velocity_limits: true
          max_velocity: 6.28
          has_acceleration_limits: true
          max_acceleration: 8.0
        left_paddle:
          has_position_limits: true
          min_position: 0.0
          max_position: 0.15
          has_velocity_limits: true
          max_velocity: 0.5
          has_acceleration_limits: true
          max_acceleration: 1.0
        right_shoulder_pan:
          has_position_limits: true
          min_position: -3.14
          max_position: 3.14
          has_velocity_limits: true
          max_velocity: 3.15
          has_acceleration_limits: true
          max_acceleration: 5.0
        right_shoulder_lift:
          has_position_limits: true
          min_position: -3.14
          max_position: 3.14
          has_velocity_limits: true
          max_velocity: 3.15
          has_acceleration_limits: true
          max_acceleration: 5.0
        right_elbow:
          has_position_limits: true
          min_position: -3.14
          max_position: 3.14
          has_velocity_limits: true
          max_velocity: 3.15
          has_acceleration_limits: true
          max_acceleration: 5.0
        right_wrist_1:
          has_position_limits: true
          min_position: -3.14
          max_position: 3.14
          has_velocity_limits: true
          max_velocity: 6.28
          has_acceleration_limits: true
          max_acceleration: 8.0
        right_wrist_2:
          has_position_limits: true
          min_position: -3.14
          max_position: 3.14
          has_velocity_limits: true
          max_velocity: 6.28
          has_acceleration_limits: true
          max_acceleration: 8.0
        right_wrist_3:
          has_position_limits: true
          min_position: -3.14
          max_position: 3.14
          has_velocity_limits: true
          max_velocity: 6.28
          has_acceleration_limits: true
          max_acceleration: 8.0
        right_paddle:
          has_position_limits: true
          min_position: 0.0
          max_position: 0.15
          has_velocity_limits: true
          max_velocity: 0.5
          has_acceleration_limits: true
          max_acceleration: 1.0
```

- [ ] **Step 5: 验证 YAML 语法**

Run: `python -c "import yaml; yaml.safe_load(open('simulation/ros2_ws/src/robot_moveit_config/config/ros2_controllers.yaml'))"`
Expected: 无报错

- [ ] **Step 6: Commit**

```bash
git add simulation/ros2_ws/src/robot_moveit_config/config/
git commit -m "feat: migrate MoveIt config for dual-arm (controllers, kinematics, OMPL, joint limits)"
```

---

## Task 9: robot_decision — TaskCoordinator 状态机

**Files:**
- Create: `robot-app/ros2_ws/src/robot_decision/robot_decision/task_coordinator.py`
- Test: `robot-app/ros2_ws/src/robot_decision/tests/test_task_coordinator.py`

**Interfaces:**
- Consumes: `TaskCommandMsg`（Task 2）
- Produces: `TaskCoordinator` 类，状态机驱动，派发任务到子系统执行器

- [ ] **Step 1: 编写 TaskCoordinator 测试**

```python
"""Tests for TaskCoordinator FSM."""
import pytest
from robot_decision.task_coordinator import TaskCoordinator, CoordinationPhase


def test_initial_state_is_idle():
    coord = TaskCoordinator()
    assert coord.phase == CoordinationPhase.IDLE


def test_transition_to_navigating_on_goto():
    coord = TaskCoordinator()
    coord.execute_task("goto", {"target_pose": {"x": 1.0, "y": 2.0, "z": 0.0}})
    assert coord.phase == CoordinationPhase.NAVIGATING


def test_transition_to_hugging_on_pick_box():
    coord = TaskCoordinator()
    coord.execute_task("pick_box", {"target_pose": {"x": 0.5}, "hug_params": {}})
    assert coord.phase == CoordinationPhase.APPROACHING


def test_abort_from_any_phase():
    coord = TaskCoordinator()
    coord.execute_task("goto", {"target_pose": {"x": 1.0}})
    coord.abort("safety_trigger")
    assert coord.phase == CoordinationPhase.ABORTING


def test_abort_returns_to_idle():
    coord = TaskCoordinator()
    coord.execute_task("goto", {"target_pose": {"x": 1.0}})
    coord.abort("safety_trigger")
    coord.complete_abort()
    assert coord.phase == CoordinationPhase.IDLE


def test_invalid_task_type_raises():
    coord = TaskCoordinator()
    with pytest.raises(ValueError):
        coord.execute_task("invalid_task", {})
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_task_coordinator.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 TaskCoordinator**

```python
"""Task coordinator FSM for dual-arm AGV loading robot."""
from __future__ import annotations
from enum import Enum, auto
from typing import Any, Callable


class CoordinationPhase(Enum):
    IDLE = auto()
    NAVIGATING = auto()
    DOCKING = auto()
    APPROACHING = auto()
    HUGGING = auto()
    LIFTING = auto()
    TRANSPORTING = auto()
    PLACING = auto()
    RETREATING = auto()
    ABORTING = auto()


# Task type -> initial phase mapping
_TASK_PHASE_MAP: dict[str, CoordinationPhase] = {
    "goto": CoordinationPhase.NAVIGATING,
    "dock": CoordinationPhase.DOCKING,
    "pick_box": CoordinationPhase.APPROACHING,
    "place_box": CoordinationPhase.PLACING,
    "transport": CoordinationPhase.TRANSPORTING,
    "hug_close": CoordinationPhase.HUGGING,
    "hug_release": CoordinationPhase.RETREATING,
    "home_all": CoordinationPhase.RETREATING,
}


class TaskCoordinator:
    """Layered FSM coordinating base + dual-arm + hug grasp."""

    def __init__(self) -> None:
        self._phase = CoordinationPhase.IDLE
        self._current_task: str | None = None
        self._abort_reason: str | None = None

    @property
    def phase(self) -> CoordinationPhase:
        return self._phase

    def execute_task(self, task_type: str, parameters: dict[str, Any]) -> None:
        """Start a new task. Transitions FSM to the appropriate initial phase."""
        if task_type not in _TASK_PHASE_MAP:
            raise ValueError(f"unknown task_type: {task_type}")
        self._current_task = task_type
        self._phase = _TASK_PHASE_MAP[task_type]

    def advance_phase(self, next_phase: CoordinationPhase) -> None:
        """Advance to the next phase (called by sub-executors on completion)."""
        self._phase = next_phase

    def complete_task(self) -> None:
        """Mark current task as complete, return to IDLE."""
        self._phase = CoordinationPhase.IDLE
        self._current_task = None

    def abort(self, reason: str) -> None:
        """Abort from any phase."""
        self._abort_reason = reason
        self._phase = CoordinationPhase.ABORTING

    def complete_abort(self) -> None:
        """Complete abort, return to IDLE."""
        self._phase = CoordinationPhase.IDLE
        self._current_task = None
        self._abort_reason = None
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_task_coordinator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/
git commit -m "feat: add TaskCoordinator FSM with phase transitions and abort"
```

---

## Task 10: robot_decision — BaseExecutor

**Files:**
- Create: `robot-app/ros2_ws/src/robot_decision/robot_decision/base_executor.py`
- Test: `robot-app/ros2_ws/src/robot_decision/tests/test_base_executor.py`

**Interfaces:**
- Consumes: 目标位姿、/odom 反馈
- Produces: cmd_vel 速度指令

- [ ] **Step 1: 编写 BaseExecutor 测试**

```python
"""Tests for BaseExecutor."""
import pytest
from robot_decision.base_executor import BaseExecutor, BaseState


def test_initial_state_is_idle():
    executor = BaseExecutor()
    assert executor.state == BaseState.IDLE


def test_follow_waypoint_transitions_to_following():
    executor = BaseExecutor()
    executor.follow_waypoint(x=1.0, y=2.0, yaw=0.0)
    assert executor.state == BaseState.FOLLOWING


def test_stop_transitions_to_stopped():
    executor = BaseExecutor()
    executor.follow_waypoint(x=1.0, y=2.0, yaw=0.0)
    executor.stop()
    assert executor.state == BaseState.STOPPED


def test_get_cmd_vel_returns_zero_when_stopped():
    executor = BaseExecutor()
    executor.stop()
    vx, wz = executor.get_cmd_vel()
    assert vx == 0.0 and wz == 0.0
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_base_executor.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 BaseExecutor**

```python
"""Base (AGV) executor for waypoint following."""
from __future__ import annotations
from enum import Enum, auto


class BaseState(Enum):
    IDLE = auto()
    FOLLOWING = auto()
    STOPPED = auto()


class BaseExecutor:
    """Executes waypoint following for the diff-drive base."""

    def __init__(self) -> None:
        self._state = BaseState.IDLE
        self._target_x = 0.0
        self._target_y = 0.0
        self._target_yaw = 0.0

    @property
    def state(self) -> BaseState:
        return self._state

    def follow_waypoint(self, x: float, y: float, yaw: float) -> None:
        self._target_x = x
        self._target_y = y
        self._target_yaw = yaw
        self._state = BaseState.FOLLOWING

    def stop(self) -> None:
        self._state = BaseState.STOPPED

    def get_cmd_vel(self) -> tuple[float, float]:
        """Return (vx, wz) velocity command. Zero when stopped or idle."""
        if self._state != BaseState.FOLLOWING:
            return (0.0, 0.0)
        # Simple P-controller placeholder (real impl uses /odom feedback)
        return (0.0, 0.0)

    def complete_follow(self) -> None:
        self._state = BaseState.IDLE
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_base_executor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/
git commit -m "feat: add BaseExecutor for diff-drive waypoint following"
```

---

## Task 11: robot_decision — ArmExecutor

**Files:**
- Create: `robot-app/ros2_ws/src/robot_decision/robot_decision/arm_executor.py`
- Test: `robot-app/ros2_ws/src/robot_decision/tests/test_arm_executor.py`

**Interfaces:**
- Consumes: 目标关节位置或笛卡尔位姿
- Produces: MoveIt FollowJointTrajectory action 调用

- [ ] **Step 1: 编写 ArmExecutor 测试**

```python
"""Tests for ArmExecutor."""
import pytest
from robot_decision.arm_executor import ArmExecutor, ArmState


def test_initial_state_is_idle():
    executor = ArmExecutor(arm_id="left")
    assert executor.state == ArmState.IDLE
    assert executor.arm_id == "left"


def test_plan_and_execute_transitions_to_planning():
    executor = ArmExecutor(arm_id="right")
    executor.plan_and_execute(target_joints=[0.0] * 6)
    assert executor.state == ArmState.PLANNING


def test_cancel_transitions_to_idle():
    executor = ArmExecutor(arm_id="left")
    executor.plan_and_execute(target_joints=[0.0] * 6)
    executor.cancel()
    assert executor.state == ArmState.IDLE
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_arm_executor.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 ArmExecutor**

```python
"""Single-arm MoveIt executor."""
from __future__ import annotations
from enum import Enum, auto
from typing import Any


class ArmState(Enum):
    IDLE = auto()
    PLANNING = auto()
    EXECUTING = auto()
    ERROR = auto()


class ArmExecutor:
    """Plans and executes single-arm motions via MoveIt."""

    def __init__(self, arm_id: str) -> None:
        self._arm_id = arm_id
        self._state = ArmState.IDLE

    @property
    def arm_id(self) -> str:
        return self._arm_id

    @property
    def state(self) -> ArmState:
        return self._state

    def plan_and_execute(self, target_joints: list[float]) -> None:
        self._state = ArmState.PLANNING
        # Placeholder: real impl calls MoveIt action
        # /{arm_id}_arm_controller/follow_joint_trajectory

    def cancel(self) -> None:
        self._state = ArmState.IDLE

    def complete_plan(self) -> None:
        self._state = ArmState.EXECUTING

    def complete_execution(self) -> None:
        self._state = ArmState.IDLE

    def set_error(self) -> None:
        self._state = ArmState.ERROR
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_arm_executor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/
git commit -m "feat: add ArmExecutor for single-arm MoveIt planning"
```

---

## Task 12: robot_decision — HugController

**Files:**
- Create: `robot-app/ros2_ws/src/robot_decision/robot_decision/hug_controller.py`
- Test: `robot-app/ros2_ws/src/robot_decision/tests/test_hug_controller.py`

**Interfaces:**
- Consumes: 抱拿参数（HugParamsMsg）、双臂规划组
- Produces: paddle position 指令、力闭环控制

- [ ] **Step 1: 编写 HugController 测试**

```python
"""Tests for HugController."""
import pytest
from robot_decision.hug_controller import HugController, HugPhase


def test_initial_state_is_open():
    ctrl = HugController()
    assert ctrl.phase == HugPhase.OPEN


def test_approach_transitions_to_approaching():
    ctrl = HugController()
    ctrl.approach(target_pose={"x": 0.5, "y": 0.0, "z": 0.3})
    assert ctrl.phase == HugPhase.APPROACHING


def test_close_transitions_to_closing():
    ctrl = HugController()
    ctrl.close(pressure_target=50.0, approach_speed=0.2, close_speed=0.05)
    assert ctrl.phase == HugPhase.CLOSING


def test_reach_target_pressure_transitions_to_holding():
    ctrl = HugController()
    ctrl.close(pressure_target=50.0, approach_speed=0.2, close_speed=0.05)
    ctrl.update_feedback(pressure_l=49.0, pressure_r=51.0)
    assert ctrl.phase == HugPhase.HOLDING


def test_release_transitions_to_opening_then_open():
    ctrl = HugController()
    ctrl.close(pressure_target=50.0)
    ctrl.release()
    assert ctrl.phase == HugPhase.OPENING
    ctrl.complete_release()
    assert ctrl.phase == HugPhase.OPEN


def test_abort_returns_to_open():
    ctrl = HugController()
    ctrl.close(pressure_target=50.0)
    ctrl.abort()
    assert ctrl.phase == HugPhase.OPEN
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_hug_controller.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 HugController**

```python
"""Hug grasp controller for dual-arm coordinated manipulation."""
from __future__ import annotations
from enum import Enum, auto


class HugPhase(Enum):
    OPEN = auto()
    APPROACHING = auto()
    CLOSING = auto()
    HOLDING = auto()
    OPENING = auto()


class HugController:
    """Coordinates dual-arm hug grasp with force闭环."""

    def __init__(self, pressure_threshold: float = 45.0) -> None:
        self._phase = HugPhase.OPEN
        self._pressure_target = 50.0
        self._pressure_threshold = pressure_threshold

    @property
    def phase(self) -> HugPhase:
        return self._phase

    def approach(self, target_pose: dict) -> None:
        """Plan dual_arm MoveIt to hug starting pose."""
        self._phase = HugPhase.APPROACHING

    def close(self, pressure_target: float = 50.0,
              approach_speed: float = 0.2, close_speed: float = 0.05) -> None:
        """Start closing paddles with force control."""
        self._pressure_target = pressure_target
        self._phase = HugPhase.CLOSING

    def update_feedback(self, pressure_l: float, pressure_r: float) -> None:
        """Update force feedback. Transitions to HOLDING when target reached."""
        if self._phase == HugPhase.CLOSING:
            avg_pressure = (pressure_l + pressure_r) / 2.0
            if avg_pressure >= self._pressure_threshold:
                self._phase = HugPhase.HOLDING

    def release(self) -> None:
        """Start releasing."""
        self._phase = HugPhase.OPENING

    def complete_release(self) -> None:
        self._phase = HugPhase.OPEN

    def abort(self) -> None:
        """Emergency release."""
        self._phase = HugPhase.OPEN
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_hug_controller.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/
git commit -m "feat: add HugController for dual-arm hug grasp with force闭环"
```

---

## Task 13: robot_decision — SafetyMonitor

**Files:**
- Create: `robot-app/ros2_ws/src/robot_decision/robot_decision/safety_monitor.py`
- Test: `robot-app/ros2_ws/src/robot_decision/tests/test_safety_monitor.py`

**Interfaces:**
- Consumes: /scan 雷达数据、急停状态
- Produces: 安全互锁决策（cmd_vel 拦截、轨迹暂停）

- [ ] **Step 1: 编写 SafetyMonitor 测试**

```python
"""Tests for SafetyMonitor."""
import pytest
from robot_decision.safety_monitor import SafetyMonitor, SafetyState


def test_initial_state_is_safe():
    monitor = SafetyMonitor()
    assert monitor.state == SafetyState.SAFE


def test_estop_trigger_transitions_to_emergency():
    monitor = SafetyMonitor()
    monitor.trigger_estop()
    assert monitor.state == SafetyState.EMERGENCY


def test_scan_dangerous_transitions_to_slowdown():
    monitor = SafetyMonitor()
    monitor.update_scan(min_distance=0.3)  # Below safety threshold
    assert monitor.state == SafetyState.SLOWDOWN


def test_scan_safe_returns_to_safe():
    monitor = SafetyMonitor()
    monitor.update_scan(min_distance=0.3)
    monitor.update_scan(min_distance=2.0)  # Back to safe distance
    assert monitor.state == SafetyState.SAFE


def test_estop_blocks_cmd_vel():
    monitor = SafetyMonitor()
    monitor.trigger_estop()
    assert monitor.is_cmd_vel_allowed() is False


def test_safe_allows_cmd_vel():
    monitor = SafetyMonitor()
    assert monitor.is_cmd_vel_allowed() is True


def test_recovery_from_estop():
    monitor = SafetyMonitor()
    monitor.trigger_estop()
    monitor.reset_estop()
    assert monitor.state == SafetyState.SAFE
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_safety_monitor.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 SafetyMonitor**

```python
"""Safety monitor for independent safety interlocks."""
from __future__ import annotations
from enum import Enum, auto


class SafetyState(Enum):
    SAFE = auto()
    SLOWDOWN = auto()
    EMERGENCY = auto()


class SafetyMonitor:
    """Independent safety monitor — bypasses the task coordinator."""

    SLOWDOWN_DISTANCE = 0.5  # metres
    STOP_DISTANCE = 0.2  # metres

    def __init__(self) -> None:
        self._state = SafetyState.SAFE
        self._estop_active = False

    @property
    def state(self) -> SafetyState:
        return self._state

    def trigger_estop(self) -> None:
        self._estop_active = True
        self._state = SafetyState.EMERGENCY

    def reset_estop(self) -> None:
        self._estop_active = False
        self._state = SafetyState.SAFE

    def update_scan(self, min_distance: float) -> None:
        if self._estop_active:
            return
        if min_distance < self.STOP_DISTANCE:
            self._state = SafetyState.EMERGENCY
        elif min_distance < self.SLOWDOWN_DISTANCE:
            self._state = SafetyState.SLOWDOWN
        else:
            self._state = SafetyState.SAFE

    def is_cmd_vel_allowed(self) -> bool:
        return self._state == SafetyState.SAFE

    def is_trajectory_allowed(self) -> bool:
        """Arms can continue current trajectory unless estop."""
        return not self._estop_active
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/test_safety_monitor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add robot-app/ros2_ws/src/robot_decision/
git commit -m "feat: add SafetyMonitor for independent safety interlocks"
```

---

## Task 14: 集成验证 — 包构建与契约一致性

**Files:**
- 无新增文件

**Interfaces:**
- Consumes: Task 1-13 的所有产出
- Produces: 验证整个系统可构建、契约一致

- [ ] **Step 1: 验证 robot_msgs 契约一致性**

Run: `cd robot-app/ros2_ws/src/robot_msgs && python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 2: 验证 gateway 契约解码**

Run: `cd robot-app/ros2_ws/src/robot_gateway && python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 3: 验证 robot_decision 所有组件**

Run: `cd robot-app/ros2_ws/src/robot_decision && python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 4: 验证 xacro 解析（base）**

Run: `xacro robot-app/ros2_ws/src/robot_base_hal/urdf/base.urdf.xacro > /dev/null`
Expected: 无报错

- [ ] **Step 5: 验证 xacro 解析（dual-arm loader）**

Run: `xacro robot-app/ros2_ws/src/robot_dual_arm_hal/urdf/loader.urdf.xacro > /dev/null`
Expected: 无报错

- [ ] **Step 6: 验证 MoveIt 配置 YAML 语法**

Run: `python -c "import yaml; [yaml.safe_load(open(f'simulation/ros2_ws/src/robot_moveit_config/config/{f}')) for f in ['ros2_controllers.yaml', 'kinematics.yaml', 'ompl_planning.yaml', 'joint_limits.yaml']]"`
Expected: 无报错

- [ ] **Step 7: 最终 Commit**

```bash
git add -A
git commit -m "chore: integration verification for dual-arm AGV loading robot"
```

---

## 计划总结

| Task | 组件 | 文件数 | 依赖 |
|---|---|---|---|
| 1 | JSON Schema 扩展 | 3 | 无 |
| 2 | robot_msgs dataclass | 2 | Task 1 |
| 3 | Pydantic 契约 | 2 | Task 1 |
| 4 | Gateway 桥接 | 4 | Task 2, 3 |
| 5 | robot_base_hal | 5 | 无 |
| 6 | robot_dual_arm_hal | 4 | Task 5 |
| 7 | MoveIt SRDF | 1 | Task 6 |
| 8 | MoveIt 控制器 | 4 | Task 6, 7 |
| 9 | TaskCoordinator | 2 | Task 2 |
| 10 | BaseExecutor | 2 | 无 |
| 11 | ArmExecutor | 2 | 无 |
| 12 | HugController | 2 | 无 |
| 13 | SafetyMonitor | 1 | 无 |
| 14 | 集成验证 | 0 | Task 1-13 |

**并行机会**：Task 1→2→3 串行；Task 5→6→7→8 串行；Task 9-13 可并行（仅依赖 Task 2 的类型定义）。Task 4 依赖 Task 2+3。
