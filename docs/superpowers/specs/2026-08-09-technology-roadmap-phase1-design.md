# 全局技术路线图 & Phase 1 实施规格书

- **日期**: 2026-08-09
- **状态**: 待确认
- **前置**: 端到端运动链路已完成（205 tests）、装卸机器人设计规格书已确认

---

## 第一部分：全局路线图（原型 → 生产）

### 当前基线

| 子系统 | 成熟度 | 测试 | 关键能力 |
|---|---|---|---|
| rcs/ | 生产就绪 | 85 | 设备注册、控制循环、MQTT 适配、FK/IK/轨迹规划 |
| simulation/backend | 功能原型 | 68 | 任务调度、设备管理、MQTT bridge、关节缓存、SSE |
| simulation/frontend | 功能原型 | - | Three.js 仓库可视化、单臂程序化几何 |
| robot-app/gateway | 功能完整 | 44 | MQTT↔ROS2 桥接、命令转发、状态上报、急停通路 |
| robot-app/decision | 功能完整 | 8 | MoveItClient + MotionPlannerNode（单臂） |
| robot-app/perception | 空占位 | 0 | — |
| shared/ | 稳定 | - | JSON Schema + Python 契约 |
| vla-training/ | 骨架 | 5 | 数据管线 + LoRA 微调 + 导出 |

### Phase 1 — 装卸机器人核心实现（2-3 周）

**目标**：双臂 + AGV 底盘的协调控制仿真可运行

| 交付物 | 子系统 | 验证标准 |
|---|---|---|
| 契约扩展（任务命令 + 底盘/抱拿状态） | shared/ | round-trip 测试通过 |
| robot_base_hal（差速底盘 URDF + ros2_control） | robot-app/ | xacro 解析无错 |
| 双臂 URDF 扩展 | robot_arm_hal/ | 左右臂实例化正确 |
| TaskCoordinator（分层状态机） | robot_decision/ | FSM 单测覆盖全阶段 |
| HugController（双臂同步抱拿） | robot_decision/ | 抱合/保持/释放单测 |
| SafetyMonitor（安全互锁） | robot_decision/ | 互锁规则单测 |
| Gateway task_sink | robot_gateway/ | 任务命令路由测试 |
| 前端双臂可视化 | simulation/frontend/ | 双臂 + 底盘渲染 |
| 技术债清理 | 多子系统 | wildcard topic、TS 告警 |

**里程碑**：RCS → MQTT → gateway → decision（协调器 9 动作阶段 + ABORTING）→ 双臂 MoveIt + diff_drive → 前端可视化

### Phase 2 — 感知与导航（3-4 周）

| 交付物 | 子系统 | 说明 |
|---|---|---|
| robot_perception 基础 | robot-app/ | 3D 目标检测节点（点云 → 货箱位姿） |
| 抱拿目标识别 | robot_perception/ | 基于深度/点云的货箱姿态估计 |
| BaseExecutor 增强 | robot_decision/ | 航点跟随 + 激光避障 |
| Nav2 插件接口 | robot_decision/ | costmap_converter 适配（可选启用） |
| 前端感知可视化 | simulation/frontend/ | 检测框、导航路径叠加 |

**里程碑**：货箱识别 → 规划抱拿路径 → 底盘自主导航到目标 → 执行抱拿

### Phase 3 — 硬件在环与生产化（4-6 周）

| 交付物 | 说明 |
|---|---|
| 真实 HAL 适配 | EtherCAT 臂控制、CANopen 底盘驱动、IO 模块 |
| 安全 PLC 集成 | 急停回路、激光雷达安全停障、抱拿力控异常回退 |
| VLA 推理接入 | 导出模型 → robot_decision 推理节点 |
| 性能优化 | 控制周期 < 1ms、状态发布 100Hz |
| 部署流水线 | Docker 多阶段构建、CI/CD |

**里程碑**：真实装卸机器人在仓库环境中完成自主抱拿操作

### 阶段依赖关系

```
Phase 1 (双臂协调) ──▶ Phase 2 (感知+导航) ──▶ Phase 3 (硬件+生产)
       │                      │                       │
       └── 技术债清理 ────────┘                       │
                                                      │
       契约扩展 ──────────────────────────────────────┘
```

---

## 第二部分：Phase 1 详细规格书

### 1. 范围

**在范围内**：
- 契约扩展（shared/ + robot_msgs/）
- robot_base_hal 新增包
- robot_dual_arm_hal 双臂 URDF 扩展（robot_arm_hal 单臂作为 underlay 保留）
- robot_decision 核心模块（TaskCoordinator、BaseExecutor、ArmExecutor、HugController、SafetyMonitor）
- robot_gateway task_sink 扩展
- simulation 后端双臂支持
- simulation 前端双臂可视化
- 已知技术债清理

**不在范围内**（Phase 2+）：
- 真实硬件 HAL
- Nav2 全栈
- 感知算法
- VLA 推理

### 2. 契约扩展

#### 2.1 command.schema.json

新增任务级命令类型：

| 命令类型 | 用途 | 关键字段 |
|---|---|---|
| `goto` | 导航到目标位姿 | `target_pose: {x, y, yaw}` |
| `pick_box` | 抱拿货箱 | `target_pose` + `hug_params` |
| `place_box` | 放置货箱 | `target_pose` + `release_strategy` |
| `home_all` | 双臂+底盘回零 | 无 |

保留现有 `move_j/move_l/stop/home/estop/recover` 作为调试直通。新增可选字段 `group: "left" | "right" | "base" | "both"` 指定执行组。

`hug_params` 结构：
```json
{
  "pressure_target": 50.0,
  "approach_speed": 0.3,
  "close_speed": 0.1
}
```

#### 2.2 state.schema.json

扩展字段：
- `joint.positions/velocities` 长度扩展到 14（双臂 12 + 双抱板 2）
- 新增 `base`: `{velocity: [vx, wz], odom: {x, y, yaw}, battery_soc: float}`
- 新增 `hug`: `{pressure_l: float, pressure_r: float, state: "open"|"closing"|"holding"|"opening"}`
- `ctrl.phase` 替代 `mode`，枚举值：`idle | navigating | docking | approaching | hugging | lifting | transporting | placing | retreating | aborting`

#### 2.3 telemetry.schema.json

metrics 新增：`battery_voltage`, `battery_soc`, `motor_temp_l`, `motor_temp_r`, `drive_temp_l`, `drive_temp_r`

status 新增：`base_state`, `hug_state`

#### 2.4 robot_msgs dataclass 扩展

新增 dataclass（零 rclpy 依赖）：
- `TaskCommandMsg`: 任务级命令
- `HugParamsMsg`: 抱拿参数
- `BaseStateMsg`: 底盘状态
- `HugStateMsg`: 抱拿状态
- `RobotStateMsg` 扩展：新增 `base: BaseStateMsg`, `hug: HugStateMsg` 可选字段

### 3. 包结构变更

```
robot-app/ros2_ws/src/
├── robot_arm_hal/      单臂 HAL（包名保留，作为 underlay）
├── robot_dual_arm_hal/ 双臂 HAL（arm_id=left/right 实例化）
│   └── urdf/           dual_arm.ros2_control.xacro（宏按 arm_id=left/right 实例化）
├── robot_base_hal/     【新增】差速底盘 HAL
│   ├── urdf/           base.ros2_control.xacro + loader.urdf.xacro
│   ├── robot_base_hal/ __init__.py
│   ├── config/         diff_drive.yaml
│   ├── setup.py / package.xml
│   └── tests/
├── robot_msgs/         契约扩展
├── robot_gateway/      task_sink 扩展
├── robot_decision/     核心新增
│   ├── robot_decision/
│   │   ├── task_coordinator.py   分层状态机
│   │   ├── base_executor.py      底盘航点执行器
│   │   ├── arm_executor.py       单臂 MoveIt 执行器
│   │   ├── hug_controller.py     双臂同步抱拿
│   │   ├── safety_monitor.py     安全互锁
│   │   └── motion_planner.py     保留（单臂直通模式）
│   ├── config/         task_coordinator.yaml
│   └── tests/
└── robot_perception/   保持占位
```

### 4. 核心组件设计

#### 4.1 TaskCoordinator（分层状态机）

```
IDLE → NAVIGATING → DOCKING → APPROACHING → HUGGING → LIFTING
  → TRANSPORTING → PLACING → RETREATING → IDLE
任意状态 ──(超时/安全触发/RCS取消)──▶ ABORTING → IDLE
```

**接口**：
- `on_task_command(msg: TaskCommandMsg)` — 接收入口
- `get_phase() -> str` — 当前阶段查询
- `abort(reason: str)` — 中止当前任务
- `set_executor(name: str, executor)` — 注册子系统执行器

**派发规则**：
- NAVIGATING/TRANSPORTING/RETREATING → BaseExecutor
- DOCKING/APPROACHING → ArmExecutor (dual_arm group)
- HUGGING → HugController
- LIFTING/PLACING → ArmExecutor (dual_arm group)

**实现约束**：
- 纯 Python，不依赖 rclpy（便于单测）
- 状态转换通过 `_VALID_TRANSITIONS` 字典约束
- 每阶段有超时（可配置），超时触发 ABORTING

#### 4.2 BaseExecutor

**职责**：航点跟随 + 速度指令

**接口**：
- `execute_waypoint(target: Pose2D) -> None` — 发布 cmd_vel
- `get_feedback() -> BaseStateMsg` — /odom 反馈
- `stop() -> None` — 紧急停车

**实现**：
- 订阅 `/odom`（nav_msgs/Odometry）
- 发布 `/cmd_vel`（geometry_msgs/Twist）
- 简易 PID 航点跟随（仿真阶段不需要完整 Nav2）

#### 4.3 ArmExecutor

**职责**：单臂或双臂 MoveIt 规划 + FollowJointTrajectory 执行

**接口**：
- `plan_and_execute(group_name: str, target: Any) -> bool`
- `stop() -> None`

**实现**：
- 复用现有 `MoveItClient`
- 支持 planning group: `left_arm`, `right_arm`, `dual_arm`
- 通过 FollowJointTrajectory action 发送到对应 controller

#### 4.4 HugController

**职责**：双臂同步抱拿控制

**子状态**：
```
IDLE → APPROACHING → CLOSING → HOLDING → OPENING → IDLE
```

**接口**：
- `start_hug(params: HugParamsMsg) -> None`
- `release() -> None`
- `get_state() -> HugStateMsg`

**仿真简化**：
- 位置阈值模式：抱板闭合到目标开度即停
- `pressure_target` 映射为抱板 prismatic 关节目标位置
- 力闭环在 Phase 3 真实硬件时启用

#### 4.5 SafetyMonitor

**职责**：贯穿所有阶段的安全互锁，**独立通路，不经过协调器**

**接口**：
- `is_safe() -> bool` — 当前是否允许运动
- `on_scan(msg: LaserScan)` — 雷达回调
- `on_estop(active: bool)` — 急停状态
- `intercept_cmd_vel(vel: Twist) -> Twist` — cmd_vel 拦截

**互锁规则**（显式编码）：

| 条件 | 约束 |
|---|---|
| 底盘运动中 | 双臂必须收拢或抱紧 |
| 臂运动中 | 底盘速度强制 0 |
| 抱合中任一臂异常 | 双臂同步释放 + 整车停 |
| 急停触发 | 所有执行器立即停 |
| 雷达安全停障 | cmd_vel 直接拦截 |

### 5. 数据流

```
RCS ──MQTT──▶ robot_gateway ──~/task_command──▶ TaskCoordinator (FSM)
                ▲ estop 独立通路                    ├─▶ BaseExecutor ──/cmd_vel──▶ diff_drive_controller
                │                                   ├─▶ ArmExecutor ──MoveIt──▶ left/right/dual_arm_controller
                │                                   ├─▶ HugController ────────▶ left/right_paddle_controller
                │                                   └─▶ SafetyMonitor（贯穿）
                └──MQTT state/telemetry◀──~/robot_state◀── 状态聚合
```

### 6. 仿真后端变更

#### 6.1 Runtime 扩展

- 新增 `loader-01` 设备类型（AGV + 双臂）
- 关节缓存支持 14 关节
- MotionCommander 扩展任务级命令映射

#### 6.2 前端双臂可视化

- `RobotArm` 类扩展：支持左右双臂实例
- 新增 `AgvBase` 类：差速底盘程序化几何（扁平盒体 + 双驱动轮）
- `LoaderRobot` 组合类：底盘 + 双臂 + 抱板
- SSE 关节数据扩展到 14 关节 + 底盘 odom

### 7. 技术债清理（Phase 1 顺手解决）

| 问题 | 位置 | 修复 |
|---|---|---|
| wildcard topic 匹配缺失 | simulation/backend/services/mqtt_bridge.py | `_on_message` 改用 `topic_matches()` 通配符匹配 |
| TS `window` 窄化为 never | simulation/frontend/src/three/WarehouseScene.vue:119 | 添加 `typeof window !== 'undefined'` 守卫或 `as Window` 断言 |

### 8. 测试策略

| 层级 | 测试内容 | 工具 | 预期数量 |
|---|---|---|---|
| L1 单元 | 协调器 FSM、抱拿控制、底盘执行器、安全互锁、契约扩展 | pytest | ~40 |
| L2 集成 | 协调器 + 双臂 MoveIt 仿真、协调器 + 底盘 | pytest + mock | ~10 |
| L3 端到端 | RCS → MQTT → gateway → decision → controller → 前端 | docker-compose | 手动验证 |

### 9. 新增/改动文件清单

**新增**：

| 文件 | 说明 |
|---|---|
| `shared/contracts/command.schema.json` | 扩展任务级命令（新增字段，不破坏现有） |
| `shared/contracts/state.schema.json` | 扩展 base/hug 字段 |
| `shared/contracts/telemetry.schema.json` | 扩展电池/温度指标 |
| `shared/python/robot_contracts/payloads.py` | 同步扩展 |
| `robot-app/ros2_ws/src/robot_base_hal/` | 新包（URDF + ros2_control + setup） |
| `robot_dual_arm_hal/urdf/dual_arm.ros2_control.xacro` | 双臂实例化 |
| `robot_decision/robot_decision/task_coordinator.py` | 分层状态机 |
| `robot_decision/robot_decision/base_executor.py` | 底盘执行器 |
| `robot_decision/robot_decision/arm_executor.py` | 臂执行器 |
| `robot_decision/robot_decision/hug_controller.py` | 抱拿控制器 |
| `robot_decision/robot_decision/safety_monitor.py` | 安全互锁 |
| `robot_decision/config/task_coordinator.yaml` | 协调器参数 |
| `robot_decision/tests/test_task_coordinator.py` | FSM 单测 |
| `robot_decision/tests/test_hug_controller.py` | 抱拿单测 |
| `robot_decision/tests/test_safety_monitor.py` | 互锁单测 |
| `robot_decision/tests/test_base_executor.py` | 底盘单测 |
| `simulation/frontend/src/three/LoaderRobot.ts` | 双臂+底盘组合 |

**改动**：

| 文件 | 变更 |
|---|---|
| `robot_msgs/robot_msgs/contracts.py` | 新增 TaskCommandMsg、HugParamsMsg、BaseStateMsg、HugStateMsg |
| `robot_gateway/robot_gateway/contract.py` | 任务命令解码 |
| `robot_gateway/robot_gateway/bridge.py` | 新增 task_sink |
| `robot_gateway/robot_gateway/mqtt_bridge_node.py` | task_sink 接线 |
| `simulation/backend/services/runtime.py` | loader-01 设备、14 关节 |
| `simulation/backend/services/motion_commander.py` | 任务级命令映射 |
| `simulation/backend/services/mqtt_bridge.py` | wildcard topic 修复 |
| `simulation/frontend/src/three/WarehouseScene.vue` | LoaderRobot 集成 + TS 修复 |

### 10. 风险

| 风险 | 缓解 |
|---|---|
| 双臂 MoveIt 同步规划延迟 | dual_arm group 异步规划 + 超时回退；预留单臂分时降级路径 |
| 协调器状态机复杂度 | 纯 Python FSM + 显式转换表；每阶段独立单测 |
| 契约扩展向后兼容 | 新字段全部 optional；现有命令类型保留直通 |
| 仿真双臂 URDF 缺失 | Phase 1 先用 mock_components/GenericSystem；Gazebo 模型 Phase 3 |
