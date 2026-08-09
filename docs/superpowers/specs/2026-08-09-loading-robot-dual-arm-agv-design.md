# 装卸机器人（AGV + 双臂）App 端程序与电气系统设计

- **日期**: 2026-08-09
- **状态**: 已确认
- **目标 ROS 2 发行版**: Jazzy Jalisco (LTS) / Humble Hawksbill (LTS)
- **范围**: 在 `robot-app` 目录中设计适合「AGV 底盘 + 双臂抱拿」配置的应用程序架构与实现方案，并输出电气系统设计草图

---

## 1. 背景与目标

### 1.1 现状

四子工程拆分（2026-08-07）与端到端运动链路（2026-08-09）已落地：

- `robot-app/ros2_ws/src/` 包含 5 个 ROS 2 包：`robot_arm_hal`（单臂 6 轴 + 夹爪 URDF/ros2_control）、`robot_msgs`（dataclass 契约）、`robot_gateway`（MQTT 桥接，急停独立通路）、`robot_decision`（占位）、`robot_perception`（占位）
- 通信契约 `shared/contracts`：按 `device_id` 寻址，命令类型 `move_j/move_l/stop/home/estop/recover`
- RCS 设备注册表：`robot-01`（6 轴臂）、`agv-01`、`stacker-01`，各自独立 device_id
- 端到端链路：RCS → MQTT → `robot_gateway` → `robot_decision`（MoveIt 规划） → `controller_manager` → 仿真可视化

### 1.2 新机型配置

装卸机器人 = **AGV 移动底盘 + 2 个协作机械臂**，双臂协同「抱拿」货箱（hug grasp）。与现有单臂固定基座配置的关键差异：

| 维度 | 现有单臂配置 | 新双臂配置 |
|---|---|---|
| 底盘 | 固定基座 | AGV 差速移动底盘 |
| 臂数量 | 1 | 2（左右对称） |
| 末端执行 | 单夹爪 | 双臂弧形抱板协同抱拿 |
| 设备建模 | 单 device_id 直通 move_j/move_l | 整车单 device_id + 任务级命令 |
| 协调需求 | 无 | 双臂同步 + 车臂互锁 |

### 1.3 目标

1. 在 `robot-app` 目录中设计适合双臂 + AGV 配置的应用程序架构
2. 设计双臂 HAL 管理双臂协调控制
3. 设计适合抱拿货物操作的控制逻辑与状态管理
4. 确保 AGV 移动与机械臂动作的协调控制
5. 输出电气系统设计草图（AGV 驱动、双臂控制、电源分配、安全系统、传感器布线）

### 1.4 非目标

- 真实硬件 HAL 实现（本期仍为仿真优先，HAL 接口为真机预留）
- Nav2 全栈集成（架构 Nav2-ready，本期实现到安全执行层）
- VLA 模型训练（仅预留接入点）
- `robot_perception` 算法实现（保持占位）
- 多机器人协调（RCS 侧已有能力，本期不涉及）

---

## 2. 已确认的决策

| 决策项 | 选择 | 理由 |
|---|---|---|
| 设备建模 | 整车单 device_id（如 `loader-01`） + 任务级命令 | 抱拿协调延迟最低、一致性最好；RCS 下发任务级命令，本机 onboard 协调 |
| AGV 驱动形式 | 双轮差速 + 万向轮 | 结构简单、成本低、载重好；ros2_control `diff_drive_controller` 成熟 |
| 臂规格 | 2×16-20kg 级 6 轴协作臂（遨博 i20 级） | 双臂抱拿共持约 15-30kg；与散货技术方案选型体系一致 |
| 导航范围 | Nav2-ready，本期到安全执行层 | 差速 HAL + 航点跟随 + 激光安全停障；Nav2 作为可选插件预留 |
| 协调机制 | 分层状态机 | 与 08-09 已确认的 e2e 链路同构，纯 Python 可单测，不增依赖 |
| URDF 重构范围 | 保留现有单臂 URDF，新增 `robot_dual_arm_hal` 包 | 避免破坏现有单臂配置和 simulation underlay 引用；双臂 URDF 独立演进 |
| MoveIt 配置迁移 | 本次设计负责迁移 `simulation/` 的 SRDF 和控制器配置 | 双臂规划组、控制器命名变更需要跨工作区同步 |
| AUBO 臂接口 | 以太网 TCP/IP（AUBO SDK） | AUBO-i20 控制柜对外标准接口；IPC 通过 SDK 与臂控制器通信 |
| 任务命令抽象 | 通用 `execute_task` 命令（替代硬编码命令枚举） | 扩展性好：新增任务类型只需扩展 `task_type`，不破坏契约结构 |
| dual_arm 规划降级 | 接受"分时单臂规划"作为超时降级方案 | dual_arm（12-DOF）规划超时（>5s）时，自动降级为分时单臂规划（牺牲严格同步换取规划速度） |

---

## 3. 软件架构

### 3.1 包结构（robot-app/ros2_ws/src）

```
robot-app/ros2_ws/src/
├── robot_arm_hal/      【保持不变】单臂 HAL（simulation underlay 引用）
├── robot_dual_arm_hal/ 【新增】双臂 URDF + ros2_control 配置
│   └── urdf/           dual_arm.ros2_control.xacro：双臂宏实例化（arm_id=left/right）
│                       loader.urdf.xacro：整车组合（底盘 + 双臂）
├── robot_base_hal/     【新增】差速底盘 HAL
│   └── urdf/           base.ros2_control.xacro（2 驱动轮速度接口）
├── robot_msgs/         契约扩展：execute_task 命令、抱拿参数、底盘状态（仍零 rclpy 依赖）
├── robot_gateway/      四层结构不变；contract.py 扩展 execute_task 解码，
│                       bridge.py 新增 task_sink（与 motion_sink / estop_sink 并列）
├── robot_decision/     【核心新增】任务协调器（分层状态机）+ 双臂规划 + 抱拿控制 + 底盘执行 + 安全互锁
└── robot_perception/   保持占位，预留抱拿目标识别接入点
```

**关键设计决策**：

- `robot_arm_hal` 包**完全不变**，保持现有单臂 URDF 和 ros2_control 配置，避免破坏 `simulation/ros2_ws` 的 colcon underlay 引用
- 新增 `robot_dual_arm_hal` 包，职责：双臂 URDF（关节名带 `left_`/`right_` 前缀）+ 整车组合 URDF（`loader.urdf.xacro`）
- 新增 `robot_base_hal` 包，职责：差速底盘 ros2_control 配置 + 底盘 URDF
- 整车 URDF 组合文件 `loader.urdf.xacro` 放 `robot_dual_arm_hal/urdf/`，因为该包是双臂配置的入口
- `simulation/` 的 SRDF 和 `ros2_controllers.yaml` 由本次设计负责迁移（新增双臂规划组、控制器配置）

### 3.2 端到端数据流

```
RCS ──MQTT──▶ robot_gateway ──~/task_command──▶ robot_decision 任务协调器(FSM)
                ▲ estop 独立通路                    ├─▶ 底盘执行器 ──/cmd_vel──▶ diff_drive_controller
                │                                   ├─▶ 双臂规划器 ──MoveIt──▶ left/right_arm_controller (JTC)
                │                                   ├─▶ 抱拿控制器 ──────────▶ left/right_paddle_controller
                │                                   └─▶ 安全互锁监控（贯穿所有阶段）
                └──MQTT state/telemetry◀──~/robot_state◀── 状态聚合（/joint_states + /odom + 抱板压力）
```

### 3.3 HAL 设计

#### 3.3.1 ros2_control 硬件系统

| 子系统 | 硬件系统 | 关节 | 控制器 | 接口 |
|---|---|---|---|---|
| 左臂 | `left_arm` | 6 旋转关节 + 1 抱板开合（prismatic） | `left_arm_controller` (JTC) + `left_paddle_controller` | position |
| 右臂 | `right_arm` | 同上 | `right_arm_controller` + `right_paddle_controller` | position |
| 底盘 | `base` | 2 驱动轮 | `diff_drive_controller`（~50Hz，输出 /odom + TF） | velocity (cmd_vel) |

**关节总数**：16（双臂 12 + 双抱板 2 + 底盘 2 驱动轮 = 16；底盘轮为速度接口，不进入 `/joint_states`；实际 `/joint_states` 发布 14 关节：双臂 12 + 双抱板 2）

#### 3.3.2 双臂协调关键机制

MoveIt SRDF 定义三个规划组：

- `left_arm`：左臂 6 关节（独立动作）
- `right_arm`：右臂 6 关节（独立动作）
- `dual_arm`：双臂 12 关节组合（抱合/抬升等协同动作，**同步规划同步执行**）

抱拿动作用 `dual_arm` 组保证同步；独立动作（如单臂避让）走单臂组。

#### 3.3.3 力闭环

抱拿夹持力由抱板压力传感器 + 臂端力矩估计闭环，在 `robot_decision` 的 `HugController` 里以 10-50Hz 调节 paddle position。仿真阶段简化为位置阈值（抱板闭合到目标开度即停）。

#### 3.3.4 安全分层

安全停障**不经过协调器**——`safety_monitor` 直接订阅雷达 `/scan`，越限直接拦截 `cmd_vel` 与轨迹执行；急停沿用 gateway 已有的独立通路，贯穿到底盘与双臂。

---

## 4. 任务协调与状态管理

### 4.1 协调器状态机（TaskCoordinator）

```
IDLE → NAVIGATING → DOCKING → APPROACHING → HUGGING → LIFTING
  → TRANSPORTING → PLACING → RETREATING → IDLE
任意状态 ──(超时/安全触发/RCS取消)──▶ ABORTING → IDLE
```

每个阶段派发给子系统执行器（各自也是小状态机 / action client）。

### 4.2 子系统执行器

| 执行器 | 职责 | 关键接口 |
|---|---|---|
| `BaseExecutor` | 航点跟随 + 速度指令 | cmd_vel → diff_drive_controller；/odom 反馈 |
| `ArmExecutor` (×2) | 单臂 MoveIt 规划 + 执行 | `/left_arm_controller/follow_joint_trajectory`、`/right_arm_controller/...` |
| `HugController` | 双臂同步抱拿 | dual_arm planning group；抱板压力传感器力闭环 |
| `SafetyMonitor` | 贯穿所有阶段的安全互锁 | /scan、/estop；**独立通路**，不经过协调器 |

**HugController 子状态**：

- `APPROACHING`：dual_arm 规划到抱拿起始位姿
- `CLOSING`：抱板同步闭合，力控闭环
- `HOLDING`：维持夹持力，监控力反馈
- `OPENING`：同步释放

### 4.3 互锁规则（显式编码）

| 条件 | 约束 |
|---|---|
| 底盘运动中 | 双臂必须收拢或抱紧（不允许中间姿态） |
| 臂运动中 | 底盘速度指令强制 0 |
| 抱合中任一臂异常 | 双臂同步释放 + 整车停 |
| 急停触发 | 所有执行器立即停（独立通路，不经过协调器） |
| 雷达安全停障 | 底盘 cmd_vel 直接拦截；臂执行中的轨迹可继续完成当前关键帧后停 |

### 4.4 状态聚合（~/robot_state 扩展）

`robot_decision` 聚合 `/joint_states`（双臂 12 关节 + 双抱板 2 关节）+ `/odom` + 抱板压力 → 扩展后的 `RobotStateMsg`：

| 字段 | 内容 |
|---|---|
| `joint` | 合并双臂关节（positions/velocities/efforts，共 14 个） |
| `base` | 新增：`{velocity: [vx, wz], odom: {x, y, yaw}, battery_soc}` |
| `hug` | 新增：`{pressure_l, pressure_r, state: closed/holding/open}` |
| `ctrl.phase` | 顶层状态机当前阶段（替代原 mode） |
| `err` / `degraded` / `iso_ts` | 保留 |

### 4.5 抱拿任务时序示例

```
RCS ──MQTT──▶ pick_box {target_pose, hug_params}
  gateway task_sink ──▶ decision coordinator
    [APPROACHING]  base_executor FOLLOWING → /cmd_vel（双臂收拢，互锁通过）
    [HUGGING]      base 停 → hug_controller APPROACHING (dual_arm MoveIt plan)
                   → CLOSING (paddle 同步闭合，力闭环) → HOLDING
    [LIFTING]      dual_arm MoveIt plan 抬升
    [TRANSPORTING] base FOLLOWING → 放置点
    [PLACING]      dual_arm 放置位姿 → hug_controller OPENING
    [RETREATING]   双臂收拢 → base FOLLOWING → 退出位 → IDLE
```

---

## 5. 通信契约变更（shared/）

### 5.1 command.schema.json 扩展

采用通用 `execute_task` 命令模式（替代硬编码命令枚举）：

```json
{
  "type": "execute_task",
  "command_id": "cmd-001",
  "task_type": "pick_box",
  "parameters": {
    "target_pose": {"x": 0.5, "y": 0.0, "z": 0.3, "rx": 0, "ry": 0, "rz": 0},
    "hug_params": {"pressure_target": 50.0, "approach_speed": 0.2, "close_speed": 0.05}
  },
  "speed_scale": 1.0
}
```

**task_type 枚举**（可扩展，新增任务类型不破坏契约结构）：

| task_type | 用途 | parameters 关键字段 |
|---|---|---|
| `goto` | 导航到目标位姿 | `target_pose` |
| `dock` | 对接装货位 | `target_pose`, `dock_id` |
| `pick_box` | 抱拿货箱 | `target_pose`, `hug_params` |
| `place_box` | 放置货箱 | `target_pose`, `release_strategy` |
| `transport` | 运输到目标 | `target_pose` |
| `hug_close` / `hug_release` | 调试直通：抱合/释放 | `hug_params` |
| `home_all` | 双臂+底盘回零 | `target_joints`（可选） |

**向后兼容**：保留现有 `move_j` / `move_l` / `stop` / `home` / `estop` / `recover` 作为调试直通，通过可选 `group` 字段指定 `left` / `right` / `base` / `both`。网关路由逻辑：`execute_task` → `task_sink`；`move_j/move_l` 带 `group` → `task_sink`（协调器处理）；`estop` → `estop_sink`。

### 5.2 state.schema.json 扩展

- `joint.positions/velocities` 长度扩展到 14（双臂 12 + 双抱板 2）
- 新增 `base` 字段：`{velocity: [vx, wz], odom: {x, y, yaw}, battery_soc}`
- 新增 `hug` 字段：`{pressure_l, pressure_r, state}`
- `ctrl.phase` 替代 `mode`，枚举值对应协调器状态机阶段

### 5.3 telemetry.schema.json 扩展

metrics 新增：

- `battery_voltage`、`battery_soc`
- `motor_temp_l`、`motor_temp_r`（臂电机温度）
- `drive_temp_l`、`drive_temp_r`（底盘驱动温度）

status 新增：

- `base_state`（导航/跟随/停止）
- `hug_state`（抱合/保持/释放）

### 5.4 robot_msgs dataclass 扩展

`robot_msgs/contracts.py` 同步扩展 dataclass（保持零 rclpy 依赖）：

- `TaskCommandMsg`：任务级命令 dataclass
- `HugParamsMsg`：抱拿参数
- `BaseStateMsg`：底盘状态
- `HugStateMsg`：抱拿状态
- `RobotStateMsg` 扩展：新增 `base`、`hug` 字段

### 5.5 MoveIt 配置迁移（simulation/ 工作区）

本次设计负责迁移 `simulation/ros2_ws/src/` 的 MoveIt 配置，以适配双臂 + 底盘：

**SRDF 迁移**（`robot_moveit_config/config/robot.srdf`）：

- 保留现有单臂 `manipulator` 组（向后兼容）
- 新增 `left_arm` 组：`<chain base_link="left_arm_base" tip_link="left_tcp_frame"/>`
- 新增 `right_arm` 组：`<chain base_link="right_arm_base" tip_link="right_tcp_frame"/>`
- 新增 `dual_arm` 组：包含左臂 6 关节 + 右臂 6 关节（12 关节联合规划）
- 新增 `base` 组：差速底盘虚拟关节（如有）
- 扩展 `disable_collisions`：双臂之间、臂与底盘之间的自碰撞对
- 新增 `group_state`：`left_home`、`right_home`、`dual_home`、`stowed`（双臂收拢姿态）

**ros2_controllers.yaml 迁移**（`robot_moveit_config/config/ros2_controllers.yaml`）：

- 保留现有 `arm_controller` 和 `gripper_controller`（单臂兼容）
- 新增 `left_arm_controller` (JointTrajectoryController, 6 关节)
- 新增 `right_arm_controller` (JointTrajectoryController, 6 关节)
- 新增 `left_paddle_controller` (PositionController, 1 关节)
- 新增 `right_paddle_controller` (PositionController, 1 关节)
- 新增 `diff_drive_controller` (DiffDriveController, 2 驱动轮)
- 保留 `joint_state_broadcaster`（统一发布 /joint_states）

**MoveIt 配置文件迁移**：

- `kinematics.yaml`：新增 `left_arm`、`right_arm`、`dual_arm` 规划组的运动学求解器配置
- `ompl_planning.yaml`：新增双臂规划组的 OMPL 规划器配置（RRTConnect 用于单臂，BIT* 用于 dual_arm）
- `joint_limits.yaml`：新增双臂关节限速

---

## 6. 电气系统设计草图

### 6.1 系统配电（48V DC 母线）

```
┌─────────────────────────────────────────────────────────────────────┐
│                       装卸机器人电气系统                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  48V 电池组 (LFP, 48V 150Ah = 7.2kWh) ──┬──▶ 主接触器 ──▶ 48V 母线│
│  (BMS: CAN 通信，遥测 SOC/温度)          │                          │
│                                          ├─▶ DC/DC 24V/20A ──▶ 安全PLC/IO│
│                                          ├─▶ DC/DC 24V/10A ──▶ 传感器/雷达│
│                                          ├─▶ DC/AC 逆变器 3kW ──▶ 220V AC│
│                                          │         │               │
│                                          │         ├─▶ 左臂控制柜 (AUBO)│
│                                          │         └─▶ 右臂控制柜 (AUBO)│
│                                          ├─▶ 底盘伺服驱动×2 (48V DC, CANopen)│
│                                          └─▶ DC/DC 19V ──▶ 车载 IPC (工控机)│
│                                                                     │
│  功耗预算（峰值/平均）：                                            │
│    2× 臂控制器+伺服：2kW / 1kW                                     │
│    底盘驱动：800W / 400W                                           │
│    IPC+传感器+雷达：300W / 200W                                    │
│    合计峰值 3.1kW，平均 1.6kW → 续航 ~4.5h                        │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 AGV 驱动系统电气连接

```
48V 母线 ──▶ 左伺服驱动 (48V DC) ──▶ 左驱动电机 (1kW, 增量编码器)
           ──▶ 右伺服驱动 (48V DC) ──▶ 右驱动电机 (1kW, 增量编码器)
           
通信：CANopen (CiA 402) ──▶ 两驱动共享 CAN 总线 ──▶ IPC (CAN 卡)
里程计：左右电机编码器 ──▶ 驱动模块 ──▶ CAN ──▶ IPC (/odom 发布)
万向轮：被动，无电气
```

### 6.3 双臂控制系统电气布局

```
220V AC (逆变器输出) ──▶ 左臂控制柜 (AUBO 自带) ──▶ 左臂 6 关节伺服
                       ──▶ 右臂控制柜 (AUBO 自带) ──▶ 右臂 6 关节伺服

关节控制：AUBO SDK 以太网 TCP/IP（IPC ↔ 臂控制器）；臂控制器内部关节通信为 AUBO 私有协议
力矩反馈：臂内置 6 轴力矩传感器 ──▶ 臂控制器 ──▶ AUBO SDK ──▶ IPC
抱板控制：抱板开合气缸 ──▶ 比例阀（24V DC）──▶ IPC (IO 模块)
抱板压力：薄膜压力传感器×4/臂 ──▶ RS485 采集模块 ──▶ IPC

双臂控制器 IPC 接入：Ethernet (1Gbps, TCP/IP, AUBO SDK) ──▶ IPC (ROS 2 节点)

**注**：AUBO-i20 控制柜对外标准接口为以太网 TCP/IP，通过 AUBO SDK（Windows/Linux C++ 库）提供关节控制、力矩反馈、状态监控等 API。臂控制器内部关节通信为 AUBO 私有协议，对上层透明。
```

### 6.4 安全系统

```
┌─────────────────────────────────────────────────────────────────────┐
│                       安全回路                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  急停按钮×3 (车体两侧 + 远程) ──串联──▶ 安全继电器 ──▶ 主接触器线圈│
│  (任一触发 → 切断 48V 母线，臂/驱动/IPC 全部断电)                  │
│                                                                     │
│  2D 安全激光雷达×2 (前/后, SIL2/PLe) ──▶ 安全 PLC                 │
│  (检测到人员进入保护区域 → 减速/停障，不直接切主电源)              │
│                                                                     │
│  安全 PLC (独立于 IPC)：                                            │
│    - 监控急停、激光雷达、底盘碰撞传感器                            │
│    - 控制安全继电器                                                 │
│    - CAN 通信 ──▶ IPC (安全状态上报)                                │
│                                                                     │
│  抱拿安全：                                                         │
│    - 抱板压力异常 → IPC 协调器触发安全回退（同步释放 + 整车停）   │
│    - 臂端力矩异常 → 臂控制器内置碰撞检测 → 急停                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.5 传感器与执行器布线

| 传感器/执行器 | 数量 | 接口 | 布线 |
|---|---|---|---|
| 2D 安全激光雷达 | 2 | Ethernet (IP67) | 前/后各一，走车体顶部线槽 |
| 3D 避障雷达 | 1 | Ethernet | 顶部，IP65 |
| IMU | 1 | RS422/USB | 车体中心，短走线 |
| 底盘编码器 | 2 | 增量式，接驱动模块 | 电机尾端，短走线 |
| 抱板薄膜压力传感器 | 8 (4/臂) | RS485 采集模块 | 抱板内走线，柔性拖链 |
| 臂端力矩传感器 | 2 (6轴/臂) | EtherCAT (臂控制器内) | 臂内走线 |
| 电池 BMS | 1 | CAN | 电池仓内 |
| 抱板开合气缸 | 2 | 24V DC 比例阀 + IO | 抱板附近，短走线 |

### 6.6 控制柜布局

```
┌─────────────────────────────────────────────────────────────────────┐
│                       主控制柜 (车体中部, IP54)                     │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ 48V 电池组   │  │ 主接触器     │  │ DC/DC 24V    │              │
│  │ 150Ah LFP    │  │ + 断路器     │  │ ×2 (20A/10A) │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ DC/AC 逆变器 │  │ 安全 PLC     │  │ 安全继电器   │              │
│  │ 3kW          │  │              │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ 底盘伺服驱动 │  │ 车载 IPC     │  │ IO 模块      │              │
│  │ ×2 (CANopen) │  │ (Ubuntu+ROS2)│  │ (RS485/24V)  │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘

左臂控制柜 (AUBO 自带, 挂装于躯干左侧)
右臂控制柜 (AUBO 自带, 挂装于躯干右侧)
```

---

## 7. 测试策略

| 层级 | 测试内容 | 工具 |
|---|---|---|
| L1 单元 | 协调器 FSM 单测、抱拿力闭环仿真、底盘航点执行器、契约扩展 | pytest |
| L2 集成 | 协调器 + 双臂 MoveIt 仿真（mock_components）、协调器 + 底盘 diff_drive | launch_testing |
| L3 端到端 | RCS → MQTT → gateway → decision → controller_manager (Gazebo) → 前端可视化 | docker-compose + 集成测试 |
| 安全测试 | 急停响应 < 100ms、雷达停障 < 200ms、抱拿力控异常回退 | 硬件在环 |

---

## 8. 风险与缓解

| 风险 | 缓解 |
|---|---|
| 双臂 MoveIt 同步规划延迟 | dual_arm planning group 异步规划，超时阈值 5s；超时后自动降级为分时单臂规划（先规划左臂轨迹，再规划右臂轨迹，按序执行）；牺牲严格同步换取规划速度 |
| 48V 逆变器谐波干扰臂控制器 | EMI 隔离、屏蔽线缆、独立接地；臂控制器 220V AC 走独立绕组 |
| 抱拿力闭环抖动 | 薄膜压力传感器低通滤波 + 力控死区；异常阈值分级（预警/回退/急停） |
| 底盘急停惯性（500kg 级） | 安全激光雷达提前减速区 + 限速（最大 1.5m/s）；机械缓冲 |
| 双臂与底盘 TF 链同步 | 统一 TF tree（base_link → left_arm_base / right_arm_base）；odom 与 arm 状态时间戳对齐 |

---

## 9. 新增/改动文件清单

### 新增文件

| 文件 | 说明 |
|---|---|
| `robot_dual_arm_hal/urdf/dual_arm.ros2_control.xacro` | 双臂 ros2_control 配置（关节名带 left_/right_ 前缀） |
| `robot_dual_arm_hal/urdf/loader.urdf.xacro` | 整车组合 URDF（底盘 + 双臂） |
| `robot_dual_arm_hal/robot_dual_arm_hal/__init__.py` | 包初始化 |
| `robot_dual_arm_hal/setup.py` / `package.xml` | 包配置 |
| `robot_base_hal/urdf/base.ros2_control.xacro` | 差速底盘 ros2_control 配置 |
| `robot_base_hal/urdf/base.urdf.xacro` | 底盘 URDF |
| `robot_base_hal/robot_base_hal/__init__.py` | 包初始化 |
| `robot_base_hal/setup.py` / `package.xml` | 包配置 |
| `robot_decision/robot_decision/task_coordinator.py` | 任务协调器（分层状态机） |
| `robot_decision/robot_decision/base_executor.py` | 底盘航点执行器 |
| `robot_decision/robot_decision/arm_executor.py` | 单臂 MoveIt 执行器（×2 实例） |
| `robot_decision/robot_decision/hug_controller.py` | 双臂同步抱拿控制器 |
| `robot_decision/robot_decision/safety_monitor.py` | 安全互锁监控 |
| `robot_decision/config/task_coordinator.yaml` | 协调器参数 |
| `robot_decision/tests/test_task_coordinator.py` | 协调器 FSM 单测 |
| `robot_decision/tests/test_hug_controller.py` | 抱拿控制单测 |

### 改动文件

| 文件 | 变更 |
|---|---|
| `shared/contracts/command.schema.json` | 新增 `execute_task` 命令类型 + `task_type`/`parameters` 字段 |
| `shared/contracts/state.schema.json` | 新增 base/hug 字段；joint 扩展到 14；ctrl.phase 替代 mode |
| `shared/contracts/telemetry.schema.json` | 新增 battery/motor_temp/drive_temp 指标 |
| `shared/python/robot_contracts/payloads.py` | 同步扩展 |
| `robot_msgs/robot_msgs/contracts.py` | 新增 TaskCommandMsg、HugParamsMsg、BaseStateMsg、HugStateMsg；扩展 RobotStateMsg |
| `robot_gateway/robot_gateway/contract.py` | 扩展任务命令解码 |
| `robot_gateway/robot_gateway/bridge.py` | 新增 task_sink |
| `robot_gateway/tests/test_bridge.py` | 扩展测试覆盖 execute_task 命令 |

### simulation/ 工作区改动文件

| 文件 | 变更 |
|---|---|
| `simulation/ros2_ws/src/robot_moveit_config/config/robot.srdf` | 新增 left_arm/right_arm/dual_arm 规划组 + disable_collisions + group_state |
| `simulation/ros2_ws/src/robot_moveit_config/config/ros2_controllers.yaml` | 新增 left/right_arm_controller、paddle_controller、diff_drive_controller |
| `simulation/ros2_ws/src/robot_moveit_config/config/kinematics.yaml` | 新增双臂规划组运动学求解器配置 |
| `simulation/ros2_ws/src/robot_moveit_config/config/ompl_planning.yaml` | 新增双臂规划组 OMPL 规划器配置 |
| `simulation/ros2_ws/src/robot_moveit_config/config/joint_limits.yaml` | 新增双臂关节限速 |
| `simulation/ros2_ws/src/robot_bringup/urdf/robot.urdf.xacro` | 保持不变（单臂配置）；双臂配置使用 robot_dual_arm_hal 的 loader.urdf.xacro |

---

## 10. 明确不在本次范围内

- 真实硬件 HAL 实现（本期仍为仿真优先）
- Nav2 全栈集成（架构预留，本期不实现）
- VLA 模型训练（仅预留接入点）
- `robot_perception` 算法实现（保持占位）
- 多机器人协调（RCS 侧已有能力，本期不涉及）
- 前端 3D 可视化扩展（现有单臂可视化本期不动；双臂可视化作为后续任务）
