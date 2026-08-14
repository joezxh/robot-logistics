# Top 3 装卸场景 RCS + Robot-App 端到端实现设计

> 在《Top 3 装卸场景仿真模块设计》(docs/superpowers/specs/2026-08-14-top3-simulation-design.md) 定义的 3 个场景（pallet / box / bag）基础上，把仿真从"前端 3D 演示"升级为**完整的端到端控制链路**：RCS 机器人控制系统 + ROS2 Robot-App 设备驱动与任务执行器。
>
> 设计约束：**完全通过 MQTT 桥接**（RCS ↔ ROS2 ↔ Robot-App 全部用现有 MQTT 契约）；**Forklift 控制器三关节独立 PID**；**Robot-App 同时支持 SIM_HAL 与真实硬件**。
>
> 立项依据：见用户需求 brief（`/brainstorming` 任务）与仿真设计文档第 5 章 3 个场景详情。

---

## 0. 阅读指南

- **第 1 章**：背景、目标、非目标
- **第 2 章**：端到端架构（分层 + 数据流）
- **第 3 章**：RCS 机器人控制系统（控制器 + MQTT 适配 + 场景预设）
- **第 4 章**：Robot-App ROS2 架构（驱动 + 决策 + 感知 + 桥接）
- **第 5 章**：3 个场景的端到端任务流
- **第 6 章**：SIM_HAL 与真实硬件双模式
- **第 7 章**：错误处理 + 测试 + 验收

---

## 1. 背景与目标

### 1.1 背景

仿真设计文档（2026-08-14）已经实现：

- 仿真后端 `simulation/backend/`：3 个场景预设（pallet/box/bag）、`/api/scenes/*` REST 端点、Three.js 渲染
- Runtime：scene_presets、`load_scene()`、KPI 计算、虚拟 sensor 生成
- Frontend：`/scenes` 路由、ScenePallet/Box/Bag 三个 Vue 组件、设备 3D 模型

**当前缺口**：仿真只是 3D 演示，没有真正的"控制回路"。要打通端到端链路，需要：

1. 在 `rcs/` 中实现 Top 3 设备的**真实控制器**（Forklift/DualArmLoader），用 PID 闭环而非 open-loop 计时
2. 在 `robot-app/` 中用 ROS2 包实现**真实设备驱动**和**任务执行器**（含运动规划算法）
3. 用 MQTT 桥接 RCS 与 ROS2，让两者解耦、可独立测试、可对接真实硬件

### 1.2 目标

实现端到端控制链路：

```
仿真/真实业务信号 (Runtime) 
    → REST/MQTT 
    → RCS 控制器 (Python 闭环控制) 
    → MQTT 契约 
    → ROS2 MQTT Bridge 
    → ROS2 Topic 
    → Robot-App Executor (FSM) 
    → Planner (轨迹算法) 
    → Driver (HAL 接口) 
    → SIM_HAL 或真实硬件
```

每个场景必须满足：

| 场景 | 单件节拍 | 成功率 | 精度 | 吞吐量 |
|------|---------|--------|------|--------|
| 托盘 | ≤ 12s | ≥ 98% | ±5mm | ≥ 5 托盘/h |
| 箱装 | ≤ 5s | ≥ 99.5% | ±3mm | ≥ 12 件/min |
| 袋装 | ≤ 8s | ≥ 99% | ±10mm | ≥ 8 包/min |

### 1.3 非目标

- 不引入新的物理引擎（仍沿用现有几何 + 状态机仿真）
- 不接入 VLA 大模型
- 不实现其他 14 个场景（仅 Top 3）
- 不改动 `shared/contracts/command.schema.json` 已有的 `type` 枚举值；新增设备专用命令通过 `task_type` + `parameters` 扩展（参考现有 `execute_task` 模式）

---

## 2. 端到端架构

### 2.1 分层架构图

```
┌──────────────────────────────────────────────────────────────────────┐
│ Layer 1: 仿真后端  (simulation/backend/)                              │
│   FastAPI Runtime ←─ Scene Presets (pallet/box/bag) ─→ 3D 状态          │
│   POST /api/scenes/load/{name} | /api/scenes/{name}/kpi              │
└─────────────────────┬────────────────────────────────────────────────┘
                      │ MQTT (broker: localhost:1883)
                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Layer 2: RCS 机器人控制系统  (rcs/rcs/)                                │
│   ┌──────────────────┬──────────────────┬──────────────────┐         │
│   │ Forklift         │ DualArmLoader    │ Arm / AGV        │         │
│   │ Controller       │ Controller       │ Controller       │         │
│   │ (3-PID 闭环)     │ (双 PD 闭环)     │ (沿用)           │         │
│   └────────┬─────────┴────────┬─────────┴────────┬─────────┘         │
│            │ MQTT Adapter    │                  │                    │
│            ▼                 ▼                  ▼                    │
│   rcs/mqtt/forklift_adapter  loader_adapter  arm_adapter (沿用)       │
└─────────────────────┬────────────────────────────────────────────────┘
                      │ MQTT Topic: rcs/{device_id}/command
                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Layer 3: ROS2 MQTT Bridge  (robot-app/ros2_ws/src/mqtt_bridge/)       │
│   mqtt_bridge_node                                                    │
│   - 订阅: rcs/{device_id}/command → /{device_id}/command              │
│   - 发布: /{device_id}/status → rcs/{device_id}/status                │
└─────────────────────┬────────────────────────────────────────────────┘
                      │ ROS2 Topic
                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Layer 4: Robot-App  (robot-app/ros2_ws/src/{robot_decision,           │
│                                                robot_arm_hal,         │
│                                                robot_perception})      │
│   ┌──────────────────┬──────────────────┬──────────────────┐         │
│   │ PalletExecutor   │ BoxExecutor      │ BagExecutor      │         │
│   │ (FSM 4 阶段)     │ (FSM 4 阶段)     │ (FSM 4 阶段)     │         │
│   └────────┬─────────┴────────┬─────────┴────────┬─────────┘         │
│            │ Trajectory      │                  │                    │
│            ▼                 ▼                  ▼                    │
│   ForkliftMotionPlanner  DualArmOptimizer  BagTrajectoryGenerator    │
│            │                 │                  │                    │
│            └─────────────────┼──────────────────┘                    │
│                              ▼                                       │
│   ┌──────────────────────────────────────────────────────────┐       │
│   │ HAL Abstraction Layer (HALInterface)                     │       │
│   │   ├─ SimHalDriver (仿真模式，默认)                       │       │
│   │   └─ RealHardwareDriver (真实硬件，通过参数切换)         │       │
│   └──────────────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 关键设计原则

1. **完全 MQTT 桥接**：RCS 与 ROS2 之间不共享进程内存、不直连 gRPC，仅通过 MQTT 契约通信。符合用户确认的设计选择。
2. **PID 闭环**：Forklift 3 个关节（行驶/升降/伸出）各自独立 PID；DualArmLoader 双臂各关节独立 PD（参考 `ArmController` 现有 `kp=0.3 / kd=0.5`）。
3. **HAL 抽象**：Robot-App 通过 `HALInterface` 抽象，运行时根据 `HAL_MODE` 环境变量选择 `SimHalDriver` 或 `RealHardwareDriver`。
4. **状态可观测**：每个层都有 SSE 通道向仿真后端上报状态，便于 Dashboard 调试。

---

## 3. RCS 机器人控制系统

### 3.1 文件结构

```
rcs/
├── presets/                         # 新增（场景预设，扩展 simulation/backend/services/scene_presets.py 的概念）
│   ├── __init__.py
│   └── top3.py                      # Top3PresetManager：RCS 侧的设备 + 控制器 + MQTT 配置
├── devices/                         # 新增（设备模型）
│   ├── __init__.py
│   ├── base.py                      # DeviceModel 抽象基类
│   ├── pallet_forklift.py           # 叉车设备模型（关节：行驶/升降/伸出）
│   └── loading_robot.py             # 双臂装卸机器人设备模型
├── controllers/                     # 已有（扩展）
│   ├── base.py                      # 保持不变
│   ├── arm.py                       # 保持不变（PD 闭环参考）
│   ├── agv.py                       # 保持不变
│   ├── stacker.py                   # 保持不变
│   ├── forklift.py                  # 新增：ForkliftController（3 关节独立 PID）
│   └── dual_arm_loader.py           # 新增：DualArmLoaderController（双 PD）
└── mqtt/                            # 已有（扩展）
    ├── __init__.py
    ├── forklift_adapter.py          # 新增：叉车专用命令
    └── loader_adapter.py            # 新增：双臂机器人专用命令
```

### 3.2 设备模型

#### 3.2.1 `devices/pallet_forklift.py`

```python
@dataclass
class ForkliftSpec:
    """叉车设备规格 - 3 关节独立控制"""
    device_id: str
    travel_range_m: float = 50.0      # 行驶范围 ±50m
    lift_range_m: float = 3.0         # 升降范围 0-3m
    extend_range_m: float = 0.5       # 货叉伸出范围 0-0.5m
    payload_kg: float = 2000.0        # 最大载重
    fork_width_m: float = 0.6         # 单叉宽度
    fork_length_m: float = 1.2        # 单叉长度
    max_travel_speed_mps: float = 1.5
    max_lift_speed_mps: float = 0.3
    max_extend_speed_mps: float = 0.2
    # PID 参数（3 关节独立）
    kp_travel: float = 0.6
    kd_travel: float = 0.1
    kp_lift: float = 0.5
    kd_lift: float = 0.15
    kp_extend: float = 0.4
    kd_extend: float = 0.1
```

#### 3.2.2 `devices/loading_robot.py`

```python
@dataclass
class DualArmLoaderSpec:
    """双臂装卸机器人 - 双臂各 6 DOF + 夹爪"""
    device_id: str
    num_joints_per_arm: int = 6
    num_gripper_joints: int = 1      # 夹爪开合自由度
    payload_per_arm_kg: float = 30.0
    dual_arm_sync_tolerance_m: float = 0.003  # 双臂同步误差 ±3mm
    # PD 参数（沿用 ArmController）
    kp: float = 0.3
    kd: float = 0.5
```

### 3.3 ForkliftController（3 关节独立 PID）

**接口契约**（继承 `Controller` 基类）：

| 方法 | 输入 | 输出 | 说明 |
|------|------|------|------|
| `on_command(cmd)` | `Command` | None | 解析 `task_type` 与 `parameters` |
| `update(hal_state)` | `JointState` | `JointState` | 3 关节独立 PID 计算 |
| `tracking_error(...)` | `JointState, JointState` | `TrackingError` | 任一关节超阈值则 `halt()` |

**支持的 task_type**（通过 `Command.task_type` 扩展，不改 `type` 枚举）：

| task_type | parameters | 说明 |
|-----------|-----------|------|
| `extend_fork` | `{"extension_m": 0.3}` | 伸出/缩回货叉（伸出关节） |
| `lift_fork` | `{"height_m": 1.5}` | 升降货叉（升降关节） |
| `move_to` | `{"x": 5.0, "z": 2.0}` | 行驶到目标位置（行驶关节） |
| `drop_pallet` | `{"stage": "lower"}` | 放下托盘序列（联动升降+伸出） |
| `pick_pallet` | `{"stage": "insert"}` | 取托盘序列（联动升降+伸出+行驶） |

**3 关节独立 PID 实现**（伪代码）：

```python
def update(self, hal_state: JointState) -> JointState:
    if self._interp is not None and not self._interp.done:
        target = self._interp.next()  # 3 元素：[travel, lift, extend]
    else:
        target = self._q
    
    # 3 关节独立 PID（不共享增益）
    travel_err = target[0] - self._q[0]
    lift_err = target[1] - self._q[1]
    extend_err = target[2] - self._q[2]
    
    self._q[0] += self.kp_travel * travel_err - self.kd_travel * self._qdot[0]
    self._q[1] += self.kp_lift * lift_err - self.kd_lift * self._qdot[1]
    self._q[2] += self.kp_extend * extend_err - self.kd_extend * self._qdot[2]
    
    # 更新关节限位
    self._q = clip_to_limits(self._q, [0.0, 0.0, 0.0], 
                                    [self.travel_range, self.lift_range, self.extend_range])
    return JointState(positions=self._q, velocities=self._qdot, ...)
```

### 3.4 DualArmLoaderController

**支持的 task_type**：

| task_type | parameters | 说明 |
|-----------|-----------|------|
| `open_grip` | `{"gripper": "left"\|"right"\|"both"}` | 张开夹爪 |
| `close_grip` | `{"gripper": ..., "force_n": 50.0}` | 闭合夹爪（带力控） |
| `hug_grasp` | `{"object_width_m": 0.4, "approach_speed": 0.1}` | 抱夹抓取（双臂） |
| `dual_arm_sync` | `{"target_pose": ...}` | 双臂同步到同一目标位姿 |

双臂各 6 关节 + 夹爪 1 关节 = 13 维关节向量。复用 `ArmController` 的 PD 控制逻辑，左右臂各跑一个 `ArmController` 实例，统一调度。

### 3.5 MQTT 适配器

#### 3.5.1 `mqtt/forklift_adapter.py`

```python
class ForkliftMqttAdapter:
    """Forklift MQTT 命令适配器
    
    Topic: rcs/forklift-{id}/command  (订阅，RCS → Forklift Controller)
           rcs/forklift-{id}/status   (发布，Controller → 上层)
    
    命令载荷（兼容现有 command.schema.json）：
    {
      "type": "execute_task",
      "task_type": "extend_fork" | "lift_fork" | "move_to" | "drop_pallet" | "pick_pallet",
      "parameters": {...}
    }
    """
    
    FORKLIFT_TASK_TYPES = {"extend_fork", "lift_fork", "move_to", "drop_pallet", "pick_pallet"}
    
    def parse_command(self, payload: dict) -> Command: ...
    def format_status(self, joint_state: JointState) -> dict: ...
```

#### 3.5.2 `mqtt/loader_adapter.py`

```python
class LoaderMqttAdapter:
    """双臂装卸机器人 MQTT 命令适配器"""
    
    LOADER_TASK_TYPES = {"open_grip", "close_grip", "hug_grasp", "dual_arm_sync"}
    # ...
```

### 3.6 Top 场景预设

**`presets/top3.py`**：与 `simulation/backend/services/scene_presets.py` 对齐，但提供 RCS 视角的设备 + 控制器配置：

```python
TOP3_PRESETS = {
    "pallet": {
        "devices": {
            "forklift-01": {"device_type": "pallet_forklift", "spec": ForkliftSpec(...)},
            "forklift-02": {"device_type": "pallet_forklift", "spec": ForkliftSpec(...)},
            "agv-01":      {"device_type": "agv", "spec": ...},
        },
        "controllers": {
            "forklift-01": ForkliftController,
            "forklift-02": ForkliftController,
            "agv-01":      AgvController,
        },
        "mqtt_topics": {
            "forklift-01/command": "rcs/forklift-01/command",
            "forklift-01/status":  "rcs/forklift-01/status",
        },
    },
    "box":    { ... },  # loader-01 + 2×agv + stacker
    "bag":    { ... },  # loader-01 + agv + stacker
}
```

**加载流程**：`Top3PresetManager.load("pallet")` → 实例化 DeviceManager + ControllerManager + MQTT topic 注册 → Robot-App 侧 `mqtt_bridge_node` 通过相同 topic 订阅命令。

---

## 4. Robot-App ROS2 架构

### 4.1 包结构

```
robot-app/
├── README.md                       # 已有，更新
├── requirements.txt                # 新增（Python 依赖）
├── ros2_ws/
│   └── src/
│       ├── robot_arm_hal/          # 设备驱动包（HAL 抽象 + 双模式）
│       │   ├── CMakeLists.txt
│       │   ├── package.xml
│       │   ├── setup.py
│       │   └── robot_arm_hal/
│       │       ├── __init__.py
│       │       ├── hal_interface.py    # HALInterface 抽象基类
│       │       ├── sim_hal_driver.py   # SimHalDriver（仿真，默认）
│       │       ├── real_hw_driver.py   # RealHardwareDriver（真实硬件）
│       │       ├── forklift_driver.py  # 叉车驱动节点
│       │       └── gripper_driver.py   # 夹爪驱动节点
│       ├── robot_decision/         # 决策与控制包
│       │   ├── CMakeLists.txt
│       │   ├── package.xml
│       │   ├── setup.py
│       │   ├── msg/
│       │   │   ├── TaskCommand.msg
│       │   │   └── TaskFeedback.msg
│       │   ├── action/
│       │   │   └── ExecuteTask.action
│       │   └── robot_decision/
│       │       ├── __init__.py
│       │       ├── pallet_task_executor.py   # 托盘任务执行器
│       │       ├── box_task_executor.py      # 箱装任务执行器
│       │       ├── bag_task_executor.py      # 袋装任务执行器
│       │       ├── state_machine.py          # 通用 FSM
│       │       └── planning/
│       │           ├── __init__.py
│       │           ├── forklift_motion_planner.py
│       │           ├── dual_arm_optimizer.py
│       │           └── bag_trajectory_generator.py
│       ├── robot_perception/       # 感知包
│       │   ├── CMakeLists.txt
│       │   ├── package.xml
│       │   ├── setup.py
│       │   └── robot_perception/
│       │       ├── pallet_detector.py
│       │       ├── gripper_monitor.py
│       │       └── collision_avoidance.py
│       └── mqtt_bridge/            # MQTT 桥接包
│           ├── CMakeLists.txt
│           ├── package.xml
│           ├── setup.py
│           └── mqtt_bridge/
│               ├── mqtt_bridge_node.py
│               └── topic_mapping.yaml
└── docker/                        # Dockerfile (ros2 + python deps)
```

### 4.2 ROS2 Topic 列表

| Topic | 类型 | 方向 | 说明 |
|-------|------|------|------|
| `/forklift/command` | `std_msgs/String` (JSON) | Decision → Driver | RCS 下发的命令（经桥接） |
| `/forklift/joint_states` | `sensor_msgs/JointState` | Driver → Decision | 叉车 3 关节状态 |
| `/gripper/command` | `std_msgs/String` | Decision → Driver | 夹爪命令 |
| `/gripper/wrench` | `geometry_msgs/WrenchStamped` | Driver → Decision | 夹爪力矩 |
| `/task/goal` | `robot_decision/ExecuteTask.action` | Client → Executor | 任务 Action 入口 |
| `/task/feedback` | `robot_decision/ExecuteTaskFeedback` | Executor → Client | 阶段反馈 |
| `/perception/pallets` | `vision_msgs/Detection3DArray` | Detector → Decision | 托盘检测结果 |
| `/collision/stop` | `std_msgs/Bool` | Monitor → All | 急停广播 |

### 4.3 节点架构

#### 4.3.1 `mqtt_bridge_node`（桥接层）

```python
class MqttBridgeNode(Node):
    """ROS2 ↔ MQTT 双向桥接"""
    
    def __init__(self):
        super().__init__('mqtt_bridge_node')
        self.mqtt_client = mqtt.Client()  # paho-mqtt
        self.mqtt_client.connect('localhost', 1883)
        
        # MQTT → ROS2（命令）
        self.cmd_subs = {
            'forklift': self.create_subscription(String, '/forklift/command', self.fk_cmd_cb, 10),
            'gripper':  self.create_subscription(String, '/gripper/command', self.grip_cmd_cb, 10),
        }
        
        # ROS2 → MQTT（状态）
        self.status_pubs = {
            'forklift': self.create_publisher(String, '/forklift/status', 10),
            'gripper':  self.create_publisher(String, '/gripper/status', 10),
        }
```

**Topic 映射**（`topic_mapping.yaml`）：
```yaml
mqtt_to_ros:
  "rcs/forklift-01/command": "/forklift/command"
  "rcs/forklift-01/status":  "/forklift/status"
  "rcs/loader-01/command":   "/gripper/command"
ros_to_mqtt:
  "/forklift/joint_states":  "rcs/forklift-01/joint_states"
  "/gripper/wrench":         "rcs/loader-01/wrench"
```

#### 4.3.2 `forklift_driver`（HAL 层）

```python
class ForkliftDriverNode(Node):
    def __init__(self):
        super().__init__('forklift_driver')
        self.hal = self._create_hal()  # 根据 HAL_MODE 选择 SimHalDriver / RealHardwareDriver
        
        self.cmd_sub = self.create_subscription(String, '/forklift/command', self.cmd_cb, 10)
        self.joint_pub = self.create_publisher(JointState, '/forklift/joint_states', 10)
        
        self.timer = self.create_timer(0.02, self.tick)  # 50Hz 控制循环
    
    def _create_hal(self) -> HALInterface:
        mode = os.environ.get('HAL_MODE', 'sim')
        if mode == 'real':
            return RealHardwareDriver()
        return SimHalDriver()
    
    def tick(self):
        joint_state = self.hal.read_state()  # 读取（仿真返回 mock，真实从 PLC 读）
        cmd = self._pending_cmd
        if cmd:
            self.hal.send_command(cmd)       # 写入（仿真返回 mock，真实下发到 PLC）
        self.joint_pub.publish(joint_state)
```

#### 4.3.3 `pallet_task_executor`（决策层）

```python
class PalletTaskExecutorNode(Node):
    """托盘任务执行器 - 4 阶段 FSM"""
    
    STATES = ['idle', 'approach', 'engage', 'lift', 'transfer', 'place']  # 6 状态，含 idle
    
    def __init__(self):
        super().__init__('pallet_executor')
        self.planner = ForkliftMotionPlanner()
        
        self._server = ActionExecutor(self, ExecuteTask, self.execute_task_callback)
        self.joint_sub = self.create_subscription(JointState, '/forklift/joint_states', self.joint_cb, 10)
    
    def execute_task_callback(self, goal_handle):
        """FSM: approach → engage → lift → transfer → place → return"""
        for stage in ['approach', 'engage', 'lift', 'transfer', 'place']:
            target = self.planner.compute_target(stage, goal_handle.request)
            trajectory = self.planner.plan(target)
            self.execute_trajectory(trajectory)
            goal_handle.publish_feedback(...)
        goal_handle.succeed()
```

### 4.4 运动规划算法

#### 4.4.1 `forklift_motion_planner.py`

- 行驶关节：纯位移轨迹（梯形速度曲线，复用 `rcs.planning.trajectory.plan_trapezoidal`）
- 升降关节：S 曲线（避免货叉突然升降导致货物抖动）
- 伸出关节：与行驶联动（插入货叉时行驶 + 伸出同时插补）

```python
class ForkliftMotionPlanner:
    def plan_insert_pallet(self, pallet_pose: Pose) -> Trajectory:
        """规划插入托盘：行驶到 pallet 前 0.5m + 升降到 pallet 高度 + 伸出到 pallet 底部"""
        return Trajectory([
            {'joint': 'travel', 'waypoints': [...]},
            {'joint': 'lift',   'waypoints': [...]},
            {'joint': 'extend', 'waypoints': [...]},
        ])
```

#### 4.4.2 `dual_arm_optimizer.py`

- CHOMP/STOMP 算法（参考 `docs/algorithm/02-motion-planning.md`）
- 双臂同步约束：左右臂末端距离误差 ≤ `dual_arm_sync_tolerance_m`
- 障碍物避让：复用现有碰撞检测（Octomap）

#### 4.4.3 `bag_trajectory_generator.py`

- 摆动抑制控制（输入整形 / notch filter）
- 防甩动轨迹：速度限制 + 加加速度限制

### 4.5 感知与反馈

| 包 | 节点 | 功能 |
|----|------|------|
| `robot_perception` | `pallet_detector` | 点云聚类识别托盘位姿（仿真模式：返回 mock 位姿；真实：订阅 RealSense） |
| `robot_perception` | `gripper_monitor` | 夹爪力矩/位置双重反馈 |
| `robot_perception` | `collision_avoidance` | 实时碰撞检测，触发 `/collision/stop` |

---

## 5. 3 个场景的端到端任务流

### 5.1 场景 1：托盘（pallet）

**设备链**：
```
[forklift-01] → [agv-01] → [warehouse-01]
[forklift-02] → [agv-01] → [warehouse-02]
```

**任务流**（forklift 4 阶段，参考用户 brief）：
1. **插入货叉**：forklift-01 行驶至 dock-01 前 → 升降立柱到托盘高度 → 伸出货叉插入托盘（行驶+升降+伸出联动）
2. **提升货物**：升降关节提升 0.3m
3. **移动到 AGV**：行驶关节移动至 agv-01 位置
4. **放下托盘**：伸出关节回收 → 升降关节下降 → 完成

**KPI**：

| 指标 | 目标 | 测量方式 |
|------|------|---------|
| 单托盘节拍 | ≤ 12s | 从 stage "approach" 到 "place" 完成 |
| 叉车插入成功率 | ≥ 98% | 伸出关节到达目标位置阈值（±5mm） |
| AGV 对接精度 | ±5mm | forklift 与 agv 位置误差 |
| 吞吐量 | ≥ 5 托盘/h | 完成的任务数 / 时间窗 |

### 5.2 场景 2：箱装（box）

**设备链**：
```
[loader-01] → [agv-01] / [agv-02] → [stacker-01] → [warehouse-01]
```

**任务流**（loader 4 阶段）：
1. **识别箱体位姿**：`pallet_detector`（复用为 box_detector）返回 6D pose
2. **夹取**：`hug_grasp`（双臂同步，力控闭合）
3. **双臂协同搬运**：`dual_arm_optimizer` 规划双臂轨迹
4. **放入立体库**：stacker-01 接收 → 入库

**KPI**：节拍 ≤ 5s，抓取成功率 ≥ 99.5%，压溃率 = 0%（双臂同步误差 ≤ 3mm）

### 5.3 场景 3：袋装（bag）

**设备链**：
```
[loader-01（防滑齿夹爪）] → [agv-01] → [stacker-01] → [warehouse-01]
                            └→ [pallet-area]（吨袋暂存）
```

**任务流**（loader 4 阶段）：
1. **检测货物边界**：力矩传感器触发 → 检测袋装是否满
2. **防滑夹持**：`close_grip` 带防滑齿（参数 `grip_pattern="anti_slip"`）
3. **防甩动控制**：`bag_trajectory_generator` 输入整形轨迹
4. **放置**：力控下降到接触面 → 释放

**KPI**：节拍 ≤ 8s，破袋率 ≤ 0.5%，滑动率 < 1%

---

## 6. SIM_HAL 与真实硬件双模式

### 6.1 HAL 抽象层

```python
# robot_arm_hal/hal_interface.py
class HALInterface(ABC):
    @abstractmethod
    def read_state(self) -> JointState: ...
    @abstractmethod
    def send_command(self, cmd: Command) -> bool: ...
    @abstractmethod
    def estop(self) -> None: ...
    @abstractmethod
    def recover(self) -> None: ...
```

### 6.2 仿真驱动（默认）

`SimHalDriver`：通过 MQTT 订阅 RCS 状态作为"真实传感器"，把关节命令写入内存字典。便于在 Docker 中跑端到端测试，无需任何硬件。

### 6.3 真实硬件驱动

`RealHardwareDriver`：通过 `paho-mqtt`（PLC 网关）或 `pycomm3`（EtherCAT）连接真实 PLC。CLI 参数 `--plc-ip`、`--plc-port` 配置连接。

### 6.4 切换方式

环境变量 `HAL_MODE`：
- `sim`（默认）：SimHalDriver
- `real`：RealHardwareDriver，强制要求 `PLC_IP` 与 `PLC_PORT` 环境变量

启动示例：
```bash
HAL_MODE=sim ros2 launch robot_arm_hal forklift_driver.launch.py
HAL_MODE=real PLC_IP=192.168.1.10 PLC_PORT=44818 ros2 launch robot_arm_hal forklift_driver.launch.py
```

---

## 7. 错误处理 + 测试 + 验收

### 7.1 错误处理矩阵

| 层 | 错误 | 处理 |
|----|------|------|
| RCS 控制器 | PID 发散（关节超限） | `halt()` + 报警 |
| RCS MQTT | payload 缺字段 | `MQTTAdapterError` → 丢弃 + 日志 |
| MQTT Bridge | 断连 | 自动重连（paho-mqtt 内置） |
| ROS2 Driver | HAL 读取超时 | `estop()` + `/collision/stop=True` |
| Task Executor | 关节未到位（>5mm 误差，>3s） | FSM 进入 `failed` + 回滚到 idle |
| 感知 | 检测不到托盘 | 重新扫描，最多 3 次 → 失败 |
| 碰撞 | 触发安全距离 | 立即 `estop()` + 全链路停止 |

### 7.2 测试矩阵

| 层 | 类型 | 文件 | 覆盖 |
|----|------|------|------|
| RCS 控制器 | unit | `tests/unit/test_forklift_controller.py` | 3 关节 PID 收敛、限位、超限 halt |
| RCS 控制器 | unit | `tests/unit/test_dual_arm_loader_controller.py` | 双 PD、同步约束 |
| RCS MQTT | unit | `tests/mqtt/test_forklift_adapter.py` | payload 解析、错误载荷丢弃 |
| RCS Preset | unit | `tests/unit/test_top3_presets.py` | 3 场景设备配置完整性 |
| ROS2 Driver | unit | `tests/test_forklift_driver.py` | SIM/REAL 切换、HAL 调用 |
| ROS2 Executor | integration | `tests/test_pallet_executor.py` | 4 阶段 FSM 流转 |
| ROS2 Planner | unit | `tests/test_forklift_planner.py` | 轨迹插补计算正确性 |
| MQTT Bridge | integration | `tests/test_mqtt_bridge.py` | ROS2↔MQTT 双向消息 |
| E2E | manual | — | 浏览器 Dashboard + REST + ROS2 联动 |

### 7.3 验收标准

**功能验收**
- [ ] `rcs/controllers/forklift.py` 实现 3 关节独立 PID
- [ ] `rcs/controllers/dual_arm_loader.py` 实现双 PD 闭环
- [ ] `rcs/mqtt/forklift_adapter.py` 与 `loader_adapter.py` 通过现有 command.schema.json 校验
- [ ] `rcs/presets/top3.py` 包含 3 个场景的完整设备 + 控制器配置
- [ ] `robot-app/ros2_ws/src/robot_arm_hal/` 实现 HAL 抽象 + SIM/REAL 双驱动
- [ ] `robot_decision/{pallet,box,bag}_task_executor.py` 实现 4 阶段 FSM
- [ ] `robot_decision/planning/` 实现 3 类轨迹规划算法
- [ ] `mqtt_bridge/` 实现 ROS2↔MQTT 双向桥接
- [ ] 所有新增代码通过 pytest 测试（覆盖率达 90%+）
- [ ] `HAL_MODE=sim` 与 `HAL_MODE=real` 两种模式均能启动并跑通

**性能验收**
- [ ] Forklift PID 收敛时间 < 0.5s（step response）
- [ ] 双臂同步误差 < ±3mm（重复精度）
- [ ] MQTT 端到端延迟 < 50ms（本地 broker）
- [ ] ROS2 控制循环 50Hz（20ms 周期）

**质量验收**
- [ ] 所有新增文件含 docstring + 中英双语注释
- [ ] Python 遵循 PEP8 + 项目现有风格
- [ ] ROS2 包遵循 ament_python 标准
- [ ] Git commit 遵循约定式提交（feat/fix/refactor/test/docs）

---

## 附录 A：与其他文档的引用关系

- **仿真设计依据**：`docs/superpowers/specs/2026-08-14-top3-simulation-design.md`
- **现有 RCS 控制器**：`rcs/rcs/controllers/arm.py`（PD 参考实现）
- **现有 MQTT 契约**：`shared/contracts/command.schema.json`（保留 `type:execute_task` + `task_type` 扩展）
- **现有 HAL**：`rcs/rcs/hal/sim.py`（作为 ROS2 SimHalDriver 参考）
- **场景评估**：`docs/装卸场景与机器人适配选型.md` 第 3.7 节

## 附录 B：版本日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-08-14 | 初版：Top 3 装卸场景 RCS + Robot-App 端到端设计 |
