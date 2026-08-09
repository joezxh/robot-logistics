# 端到端运动链路设计文档

- **日期**: 2026-08-09
- **状态**: 已确认
- **目标 ROS 2 发行版**: Jazzy Jalisco (LTS) / Humble Hawksbill (LTS)
- **范围**: 打通 RCS → MQTT → robot_gateway → robot_decision (MoveIt) → controller_manager → 仿真前端可视化 的完整运动命令链路

---

## 1. 背景与目标

### 1.1 现状

四子工程拆分（2026-08-07）已完成结构分离和 MQTT 桥接落地。当前各子系统的成熟度如下：

| 子系统 | 成熟度 | 关键缺失 |
|---|---|---|
| `rcs/` | 较高 | 控制回路 1kHz、MQTT 适配器、双模式均已实现 |
| `simulation/` | 中等 | 任务执行是进度条，无真实运动仿真 |
| `robot-app/` | 部分 | Gateway 只 log 命令不执行；Decision/Perception 为空 |
| `vla-training/` | 骨架 | 数据管道就绪，模型加载/训练步骤未实现 |

**核心断点**：RCS 下发的运动命令到达 `robot_gateway` 后，`MqttBridgeNode._on_motion_command` 仅打印日志，不转发给任何执行器。`robot_decision` 和 `robot_arm_hal` 均为空壳。仿真后端的任务执行是线性进度条（`progress += seconds * 12`），前端看不到真实机械臂运动。

### 1.2 目标

打通端到端的运动命令链路，让 RCS 下发的命令能真正驱动机械臂运动（仿真环境），并在前端实时可视化。

### 1.3 非目标（本次不做）

- 真实硬件 HAL 实现
- VLA 模型训练执行（仅预留接入点）
- `robot_perception` 实现
- 多机器人协调
- 碰撞避让（MoveIt OMPL 提供基础能力，但不做场景级碰撞建模）

---

## 2. 已确认的决策

| 决策项 | 选择 | 理由 |
|---|---|---|
| 优化目标 | 端到端链路优先 | 先打通完整命令链路，再逐步补全各子系统 |
| 执行环境 | 纯仿真 | 不依赖真实硬件，用仿真环境快速验证 |
| Decision 角色 | MoveIt 集成 | 规划能力最强，标准 ROS 2 接口，未来可迁移到真实硬件 |
| MoveIt 部署 | 远程调用 | robot_decision 通过 ROS 2 Action 调用 simulation 工作区的 move_group |
| 前端可视化 | 实时关节可视化 | Three.js 场景中展示机械臂实时关节运动 |
| 实现方案 | 方案 A：完整 ROS 2 Action 链 | 标准接口、松耦合、可独立测试 |

---

## 3. 整体架构

### 3.1 端到端数据流

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Simulation Backend (FastAPI)                                           │
│  task → MotionCommander → MQTT publish                                  │
│  MQTT subscribe ← state/telemetry ←──────────────────────┐              │
└──────────────────────────────┬───────────────────────────┼──────────────┘
                               │ MQTT                      │ MQTT
                          ┌────▼───────────────────────────┼───┐
                          │         Mosquitto Broker        │   │
                          └────┬───────────────────────────▲───┘
                               │ rcs/{dev}/command         │ rcs/{dev}/state
                          ┌────▼───────────────────────────┼───┐
                          │  robot_gateway (ROS 2 node)    │   │
                          │  MqttBridgeNode                │   │
                          │  ↓ decode → MoveAction         │   │
                          └────┬───────────────────────────▲───┘
                               │ ~/motion_command          │ ~/robot_state
                          ┌────▼───────────────────────────┼───┐
                          │  robot_decision (ROS 2 node)   │   │
                          │  ↓ MoveAction → MoveIt plan    │   │
                          │  → FollowJointTrajectory goal  │   │
                          └────┬───────────────────────────▲───┘
                               │ /arm_controller/follow_joint_trajectory  │ /joint_states
                          ┌────▼───────────────────────────┼───┐
                          │  controller_manager (sim ws)      │   │
                          │  ↓ trajectory execution            │   │
                          │  → mock_components/GenericSystem   │   │
                          │  + joint_state_broadcaster         │   │
                          └────────────────────────────────────┘
                               │
                          ┌────▼────────────────────────────────┐
                          │  move_group (MoveIt, sim ws)        │
                          │  OMPL planning + kinematics         │
                          └─────────────────────────────────────┘
```

### 3.2 端到端时序

```
1.  用户在前端点击"创建任务"
2.  Backend → runtime.create_task() → MotionCommander 生成 move_l 命令
3.  SimulationMqttBridge → MQTT publish → rcs/robot-01/command
4.  MqttBridgeNode → 收到命令 → 发布 ~/motion_command
5.  MotionPlannerNode → 收到命令 → MoveIt plan() → trajectory
6.  MotionPlannerNode → FollowJointTrajectory → controller_manager
7.  controller_manager → 插值执行 → joint_state_broadcaster 发布 /joint_states
8.  MotionPlannerNode → 编码 RobotStateMsg → 发布 ~/robot_state
9.  MqttBridgeNode → 收到状态 → MQTT publish → rcs/robot-01/state
10. SimulationMqttBridge → 收到状态 → 更新 runtime
11. Frontend SSE → 收到关节更新 → Three.js 渲染机械臂运动
12. 任务完成 → Backend 标记 completed
```

### 3.3 依赖方向

```
robot_arm_hal  ← (提供 URDF + ros2_control 配置，独立包)
     ↑ controller_manager 使用其 URDF 和 config
robot_decision ← moveit_msgs, control_msgs, sensor_msgs
     ↑ ~/motion_command topic
robot_gateway  ← robot_msgs (dataclass), robot_contracts
     ↑ MQTT
simulation backend ← paho-mqtt (新增)
```

标准 ROS 2 组件（simulation 工作区启动）：
- `controller_manager` — 使用 `robot_arm_hal` 的 URDF + `ros2_controllers.yaml`
- `joint_state_broadcaster` — 发布 `/joint_states`（100Hz）
- `arm_controller` (JointTrajectoryController) — 提供 `/arm_controller/follow_joint_trajectory` action server
- `move_group` (MoveIt) — OMPL 规划 + 通过 controller manager 执行

跨工作区依赖（运行时，通过 ROS 2 DDS 发现）：
- `robot_decision` → `move_group`（simulation 工作区，规划）
- `robot_decision` → `controller_manager`（simulation 工作区，`/arm_controller/follow_joint_trajectory`）
- 无编译时依赖

---

## 4. ROS 2 接口契约

### 4.1 Gateway → Decision：`~/motion_command`

使用 `robot_msgs` 中现有的 Python dataclass 作为消息契约（`MoveCommandGoal` 等），通过 JSON 序列化 + `std_msgs/msg/String` 在 ROS 2 topic 上传输（`ros2 topic echo` 可直接阅读）。

**逻辑字段定义**（实际传输为 JSON 字符串，类型列为 Python dataclass 字段类型）：

| 字段 | Python 类型 | JSON 示例 | 说明 |
|---|---|---|---|
| `command_id` | `str` | `"cmd-001"` | 命令唯一标识 |
| `type` | `str` | `"move_j"` | `move_j` / `move_l` / `stop` / `home` |
| `target_joints` | `list[float]` | `[0.0, -1.57, ...]` | 目标关节角（move_j/home 时使用） |
| `target_pose` | `Pose6DMsg \| None` | `{"x":0.5,"y":0,...}` | 目标位姿（move_l 时使用） |
| `speed_scale` | `float` | `0.8` | 速度缩放因子 |

### 4.2 Decision → controller_manager：标准 ROS 2 接口

| 接口 | 类型 | 用途 |
|---|---|---|
| `/arm_controller/follow_joint_trajectory` | `control_msgs/FollowJointTrajectory.action` | 轨迹执行（由 controller_manager 提供） |
| `/joint_states` | `sensor_msgs/JointState` | 关节状态发布（由 joint_state_broadcaster 提供） |
| `/robot_description` | `std_msgs/String` | URDF 发布（由 robot_state_publisher 提供） |

### 4.3 Decision → Gateway：`~/robot_state`

Decision 将 `/joint_states` 编码为 `robot_msgs/RobotState` 消息，发布到此 topic 供 Gateway 读取。

### 4.4 Topic 命名规范

| Topic | 发布者 | 订阅者 | 消息类型 |
|---|---|---|---|
| `~/motion_command` | Gateway | Decision | `std_msgs/msg/String` (JSON) |
| `~/robot_state` | Decision | Gateway | `std_msgs/msg/String` (JSON) |
| `/joint_states` | joint_state_broadcaster | Decision, Gateway | `sensor_msgs/JointState` |
| `/arm_controller/follow_joint_trajectory` | Decision | controller_manager | `control_msgs/FollowJointTrajectory.action` |
| `/robot_description` | robot_state_publisher | (any) | `std_msgs/String` |

---

## 5. 各节点详细设计

### 5.1 `robot_arm_hal` — URDF 与 ros2_control 配置

**职责**：提供机械臂 URDF 描述和 ros2_control 控制器配置。实际的轨迹执行和关节状态发布由 simulation 工作区启动的标准 `controller_manager` + `joint_state_broadcaster` + `arm_controller` 完成。

**无需新增节点**。现有文件已包含完整配置：
- `urdf/arm_hal.ros2_control.xacro` — 7 关节 ros2_control 硬件接口声明（6 revolute arm + 1 prismatic gripper）
- `robot_moveit_config/config/ros2_controllers.yaml` — controller_manager 配置：
  - `joint_state_broadcaster` (JointStateBroadcaster) → 发布 `/joint_states` @ 100Hz
  - `arm_controller` (JointTrajectoryController) → 提供 `/arm_controller/follow_joint_trajectory` action server，6 关节
  - `gripper_controller` (JointGroupPositionController) → gripper 控制

**关键设计决策**：不实现自定义 TrajectoryExecutorNode，原因：
1. `ros2_control` 的 `JointTrajectoryController` 已提供标准 `FollowJointTrajectory` action server
2. `joint_state_broadcaster` 已统一处理 `/joint_states` 发布，避免多发布者冲突
3. `mock_components/GenericSystem` 硬件插件在纯仿真环境下模拟关节响应

**关节覆盖范围**：
- arm 的 6 个关节：`shoulder_pan, shoulder_lift, elbow, wrist_1, wrist_2, wrist_3`
- gripper 的 1 个关节：`gripper_left`（独立 controller，本次不纳入运动链路）

**改动文件**：无（现有配置已满足需求）

### 5.2 `robot_decision` — MoveIt 运动规划节点

**职责**：接收高层运动命令 → 调用 MoveIt 规划 → 发送轨迹到 controller_manager 执行。

**新增文件**：

**`robot_decision/robot_decision/motion_planner.py`**

```python
MotionPlannerNode(Node):
    # Subscriber
    ~/motion_command (robot_msgs/MoveAction)

    # Action client
    /arm_controller/follow_joint_trajectory → controller_manager

    # MoveIt
    MoveGroupInterface("manipulator")  # 与 robot.srdf 中 <group name="manipulator"> 一致

    # Publisher
    ~/robot_state (供 Gateway 读取)

    命令处理:
    move_j:
        1. 设置 MoveGroup joint target
        2. plan() → 获取 trajectory
        3. execute via controller_manager action client

    move_l:
        1. 设置 MoveGroup pose target
        2. plan() → 获取 trajectory
        3. execute via controller_manager action client

    home:
        1. 设置 named target "home"
        2. plan + execute

    stop:
        1. MoveGroup stop()
        2. 取消 controller_manager 正在执行的 action

    状态上报:
    - 订阅 /joint_states (来自 joint_state_broadcaster)
    - 构造 RobotStateMsg:
      - device_id: 从节点参数读取
      - joint: 直接从 /joint_states 映射 positions/velocities
      - err: 计算目标关节与实际关节的误差 (从当前 action goal 获取目标)
      - ctrl: 根据当前状态机阶段填充 (planning/executing/idle)
      - iso_ts: 当前时间戳
    - 发布到 ~/robot_state

    规划失败处理:
    - MoveIt plan() 返回空 → 发布 alert 到 ~/alert
    - action 执行超时 → 取消 goal + 发布 alert
    - 所有异常 → 记录日志 + 发布 alert
```

**`robot_decision/robot_decision/moveit_client.py`**

```python
MoveItClient:
    plan_joint_target(joints) → JointTrajectory
    plan_pose_target(pose) → JointTrajectory
    plan_named_target(name) → JointTrajectory
    stop()
    错误处理: 规划失败返回空轨迹 + 错误信息
```

**改动文件**：
- `setup.py` — 添加入口点
- `package.xml` — 添加 `moveit_msgs`, `control_msgs`, `sensor_msgs`, `trajectory_msgs` 依赖
- `config/motion_planner.yaml` — MoveIt 参数：
  ```yaml
  planning_group: manipulator    # 必须与 robot.srdf 一致
  end_effector_link: tcp_frame   # 必须与 robot.urdf.xacro 一致
  moveit_timeout: 5.0
  ```

### 5.3 `robot_gateway` — 增强执行逻辑

**改动文件**：`mqtt_bridge_node.py`

```python
变更点:
1. _on_motion_command:
   - 不再只 log
   - 将 CommandMsg 转换为 MoveAction
   - 发布到 ~/motion_command topic

2. 新增状态上报:
   - 订阅 ~/robot_state (from Decision)
   - 编码为 wire contract
   - 通过 MqttBridge.publish_state() 发布到 MQTT

3. 新增告警处理:
   - 订阅 ~/alert (from Decision, on planning failure)
   - 通过 MqttBridge 发布到 rcs/{dev}/alert
```

---

## 6. 仿真后端集成

### 6.1 MotionCommander — 任务到运动命令桥接

**新增文件**：`simulation/backend/services/motion_commander.py`

```python
MotionCommander:
    __init__(mqtt_bridge, site_manager)
    on_task_started(task) → 生成并发布运动命令
    on_state_update(device_id, state) → 更新任务进度
    _build_command(task_type, device_id, site) → CommandPayload

    命令类型映射:
    dock_loading → move_l(target_pose=dock_tcp_pose)
    agv_transport → move_j(target_joints=transport_config)
    warehouse_storage → move_l(target_pose=shelf_tcp_pose)

    坐标转换（关键）:
    SiteManager 的 dock/warehouse 坐标是仓库级坐标（如 x=-6.0, z=7.0），
    远超出机械臂臂展（~0.8m）。必须通过预定义的 arm-to-site 偏移矩阵
    将仓库坐标转换为机械臂基坐标系下的可达 TCP 位姿：
      tcp_pose = T_base_to_site * site.position + offset_tcp
    偏移参数在 motion_commander 配置中定义，本次使用固定值。
```

### 6.2 SimulationMqttBridge — 仿真后端 MQTT 适配器

**新增文件**：`simulation/backend/services/mqtt_bridge.py`

```python
SimulationMqttBridge:
    连接 Mosquitto broker (与 RCS/robot-app 相同)
    发布命令: rcs/{device_id}/command (QoS 1)
    订阅状态: rcs/{device_id}/state (QoS 0)
    订阅遥测: robot/{device_id}/telemetry (QoS 0)
    可选启用: SIM_MQTT_ENABLED 环境变量
    不可用时静默降级
```

### 6.3 Runtime 任务状态机增强

**改动文件**：`simulation/backend/services/runtime.py`

```
任务状态机:
pending → command_sent (命令已发布, 等待执行反馈)
command_sent → running (收到关节运动反馈)
running → completed (max_joint_error < 0.05 rad，与 ros2_controllers.yaml goal tolerance 对齐)
任意状态 → failed (超时 30s / 规划失败 / action 返回 ABORTED)
```

### 6.4 关节状态 SSE 端点

**改动文件**：`simulation/backend/main.py`

```
新增端点:
GET /api/devices/{device_id}/joints — SSE 流，实时推送关节状态

响应格式 (SSE data):
{
  "device_id": "robot-01",
  "joint_names": ["shoulder_pan","shoulder_lift","elbow","wrist_1","wrist_2","wrist_3"],
  "positions": [0.0, -1.57, 1.57, -1.57, -1.57, 0.0],
  "velocities": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  "timestamp_ns": 1234567890
}

数据来源:
- SimulationMqttBridge 收到 rcs/robot-01/state 后解析 joint.positions
- 存入 runtime 内存中的 device joint cache
- SSE 端点从该 cache 读取并推送

改动端点:
GET /api/devices — 响应中增加 joints 字段 (如果可用)
```

---

## 7. 仿真前端可视化

### 7.1 机械臂 3D 模型

**改动文件**：`simulation/frontend/src/three/WarehouseScene.vue`

**前置依赖（需确认）**：机械臂 3D 模型来源尚未确定。当前方案分两阶段：

**阶段 1（本次实现）**：使用 Three.js 基本几何体程序化构建简化机械臂模型，与 URDF 的 link 尺寸对齐：
- base_link: CylinderGeometry
- shoulder/upper_arm/forearm: CylinderGeometry（长度与 URDF 一致：0.425m / 0.392m）
- wrist_1/2/3: BoxGeometry (0.08m)
- 每个 link 作为独立 THREE.Group，关节旋转轴与 URDF `<axis>` 对齐

**阶段 2（后续）**：替换为专业 GLTF 模型（需确认来源：开源 UR5 模型 / 自建 / 采购）

```
变更点:
1. 程序化构建机械臂模型 (阶段 1):
   - 6 个 link Group + 关节 pivot point
   - 关节映射表显式定义: joint_name → THREE.Group + rotation axis
   - 放置在 dock 区域附近

2. 关节驱动:
   - 订阅 Section 6.4 的 SSE 端点 `/api/devices/{device_id}/joints`
   - 解析 joint_names + positions 数据
   - 每帧更新 6 个关节的旋转角度
   - 插值平滑 (lerp, alpha=0.3)

3. 状态指示:
   - 空闲: 灰色
   - 运动中: 蓝色
   - 错误: 红色闪烁
   - E-Stop: 整体红色
```

### 7.2 RobotArm 类

**新增文件**：`simulation/frontend/src/three/RobotArm.ts`

```typescript
RobotArm class:
    load(): 加载 3D 模型
    setJointPositions(positions: number[]): 更新关节角度
    setStatus(status: 'idle' | 'moving' | 'error' | 'estop'): 状态指示
    update(dt: number): 帧更新 (平滑插值)
```

---

## 8. 测试计划

### 8.1 分层测试

| 层级 | 测试内容 | 工具 |
|---|---|---|
| L1: 单元 | 各节点内部逻辑 | pytest + launch_testing |
| L2: 集成 | 节点间 ROS 2 通信 | launch_testing |
| L3: 端到端 | 完整 MQTT → ROS 2 → MQTT 链路 | docker-compose + 集成测试 |

### 8.2 L1 单元测试

| 测试 | 文件 | 验证内容 |
|---|---|---|
| Decision 命令转换 | `robot_decision/tests/test_command_conversion.py` | MoveAction → MoveIt goal 转换 |
| Decision MoveIt 客户端 | `robot_decision/tests/test_moveit_client.py` | plan_joint_target / plan_pose_target 模拟 |
| Gateway 路由 | `robot_gateway/tests/test_bridge_routing.py` | 命令转发、状态上报、estop 优先级 |
| MotionCommander | `simulation/backend/tests/test_motion_commander.py` | task_type → 运动命令映射 |

### 8.3 L2 集成测试

| 测试 | 验证内容 |
|---|---|
| Decision + controller_manager | MoveIt 规划 → FollowJointTrajectory → arm_controller 执行 → joint_states 发布 |
| Gateway + Decision | MQTT 命令 → ROS 2 执行 → 状态回报 |

### 8.4 L3 端到端测试

```python
test_e2e_motion_chain:
    1. 启动 Mosquitto (docker)
    2. 启动 simulation backend (embedded RCS + MQTT bridge)
    3. ros2 launch robot_bringup arm.launch.py use_gazebo:=false
       # 启动: robot_state_publisher + ros2_control_node + controller_manager
       #        + joint_state_broadcaster + arm_controller + gripper_controller
    4. ros2 launch robot_moveit_config move_group.launch.py
    5. 启动 robot_gateway + robot_decision (robot-app ros2_ws)
    6. 通过 REST API 创建 dock_loading 任务
    7. 等待: MQTT 命令 → MoveIt 规划 → controller_manager 执行
    8. 断言: /joint_states 变化, max_joint_error < 0.05 rad
    9. 断言: 任务状态变为 completed
    10. 断言: 前端 SSE 收到关节更新
```

---

## 9. 子系统接入点（预留，本次不实现）

### 9.1 RCS 子系统

| RCS 能力 | RCS 侧状态 | 接入预留点 |
|---|---|---|
| EventBus 告警 → MQTT alert | RCS 已实现 | Decision 规划失败时发布到 `~/alert`，Gateway 转发到 MQTT |
| 背压控制 (queue_full) | RCS 已实现 | Gateway 转发命令时复用 `COMMAND_QUEUE_MAXSIZE` |
| 幂等命令 (command_id 去重) | RCS 已实现 | **需新增**: Decision 侧维护 command_id 缓存 (LRU, TTL=60s) |
| 多设备支持 | registry 已支持 | Decision 按 device_id 过滤命令，只处理本机命令 |

### 9.2 VLA-Training 子系统

| 接入点 | 位置 | 说明 |
|---|---|---|
| VLA 推理替代 MoveIt | `robot_decision/motion_planner.py` | 配置切换：VLA 推理 vs MoveIt 规划 |
| 仿真数据采集 | `simulation/backend/services/motion_commander.py` | 执行过程导出为 VLA 训练 episode |
| InferenceManifest 验证 | `robot_decision/` | 加载时调用 `validate_against_robot()` |

---

## 10. 配置与环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `SIM_MQTT_ENABLED` | `false` | 仿真后端 MQTT 桥接开关（默认关闭，避免无 broker 时启动报错） |
| `SIM_MQTT_HOST` | `127.0.0.1` | Mosquitto 地址 |
| `SIM_MQTT_PORT` | `1883` | Mosquitto 端口 |
| `DECISION_PLANNING_GROUP` | `manipulator` | MoveIt planning group 名称（必须与 robot.srdf 一致） |
| `DECISION_END_EFFECTOR_LINK` | `tcp_frame` | 末端执行器 link（必须与 robot.urdf.xacro 一致） |
| `DECISION_MOVEIT_TIMEOUT` | `5.0` | MoveIt 规划超时(秒) |

**paho-mqtt 集成说明**：`SimulationMqttBridge` 使用 `paho.mqtt.client.Client.loop_start()` 后台线程模型。回调在 paho 线程中执行，通过 `asyncio.run_coroutine_threadsafe()` 将状态更新转发到 FastAPI 的 asyncio 事件循环，避免线程安全问题。

---

## 11. 风险与缓解

| 风险 | 缓解 |
|---|---|
| MoveIt move_group 启动慢（10-30s） | Decision 节点等待 move_group ready 后再接受命令；超时则报错 |
| controller_manager 启动依赖 URDF | 启动脚本确保 robot_state_publisher 先于 controller_manager 启动 |
| 跨工作区 ROS 2 通信需 source 两个 setup.bash | 文档化启动脚本；docker-compose 统一环境；ROS_DOMAIN_ID 一致 |
| 机械臂 3D 模型与 URDF 不一致 (阶段 1) | 程序化几何体直接读取 URDF 尺寸参数；关节映射表显式定义 |
| mock_components 与真实硬件行为差异 | 接口严格遵循 FollowJointTrajectory 标准；切换到真实硬件时只需替换 hardware plugin |
| MQTT 消息延迟导致前端卡顿 | 前端做插值平滑 (lerp)；SSE 推送频率与 controller_manager 的 100Hz 解耦，限制为 30Hz |
| paho-mqtt 线程与 asyncio 事件循环竞争 | 通过 run_coroutine_threadsafe 安全跨线程调度；runtime 数据访问加锁 |
| MoveIt 规划失败无反馈路径 | 规划失败 → Decision 发布 ~/alert → Gateway 转发到 MQTT → Backend 标记任务 failed |

---

## 12. 新增/改动文件清单

### 新增文件

| 文件 | 说明 |
|---|---|
| `robot_decision/robot_decision/motion_planner.py` | 运动规划节点（MoveIt + action client） |
| `robot_decision/robot_decision/moveit_client.py` | MoveIt MoveGroupInterface 封装 |
| `robot_decision/config/motion_planner.yaml` | 节点参数（planning_group: manipulator） |
| `simulation/backend/services/motion_commander.py` | 任务→运动命令桥接 |
| `simulation/backend/services/mqtt_bridge.py` | 仿真后端 MQTT 适配器（paho-mqtt loop_start 线程模型） |
| `simulation/frontend/src/three/RobotArm.ts` | 3D 机械臂类（阶段 1: 程序化几何体） |
| `robot_decision/tests/test_command_conversion.py` | 命令转换测试 |
| `robot_decision/tests/test_moveit_client.py` | MoveIt 客户端模拟测试 |
| `simulation/backend/tests/test_motion_commander.py` | 运动命令映射测试 |

**注意**：`robot_msgs` 保持 `ament_python` 构建类型，继续使用 Python dataclass 作为消息契约（`MoveCommandGoal`、`RobotStateMsg` 等已存在）。不新增 `.msg` 文件。ROS 2 跨节点 topic 通信使用 `std_msgs/msg/String` 传输 JSON 序列化后的 dataclass，`ros2 topic echo` 可直接阅读。

### 改动文件

| 文件 | 变更 |
|---|---|
| `robot_decision/setup.py` | 添加 motion_planner 入口点 + config data_files 安装规则 |
| `robot_decision/package.xml` | 添加 moveit_msgs, control_msgs, sensor_msgs, trajectory_msgs 依赖（已有 moveit_ros_planning_interface） |
| `robot_gateway/robot_gateway/mqtt_bridge_node.py` | 增强：命令转发到 ~/motion_command + 订阅 ~/robot_state 上报 MQTT |
| `simulation/backend/main.py` | 新增 `/api/devices/{device_id}/joints` SSE 端点 |
| `simulation/backend/services/runtime.py` | 任务状态机增强（pending → command_sent → running → completed/failed）+ joint cache |
| `simulation/backend/config.py` | 新增 MQTT 配置项（mqtt_enabled, mqtt_host, mqtt_port） |
| `simulation/frontend/src/three/WarehouseScene.vue` | 集成机械臂可视化（RobotArm 实例化 + SSE 订阅） |
