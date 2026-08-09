# Robot Logic — Phase 5 设计规范（实跑/Gazebo+ROS2 集成）

> **创建日期**：2026-07-23
> **文档类型**：技术方案设计（Phase 5 · 仿真真跑）
> **版本**：v0.1（草案）
> **关联文档**：
> - `docs/superpowers/specs/2026-07-23-robot-logic-prototype-design.md`（Phase 1–4：FastAPI + 模拟器原型）
> - `docs/superpowers/plans/2026-07-23-robot-logic-prototype.md`（实施计划 Phase 1–4）
> - `docs/algorithm/02-motion-planning.md` · `03-perception.md` · `04-task-scheduling.md`

> **范围说明**：本规范仅针对 Phase 5，不修改也不替代 Phase 1–4 的范围与数据约定；后端与前端在 Phase 5 中**新增**与 Gazebo/ROS2 通信的部件（Gateway、WS、边缘视角组件），不重写 Phase 1–4 的业务服务、模拟器、数据层。约定 "Gateway 在下游；上层业务代码不变"。

---

## 0. 与 Phase 1–4 的边界（README 必读）

| 项 | Phase 1–4（已存） | Phase 5（新增） |
|----|------------------|----------------|
| 设备 | `RobotSimulator` / `AGVSimulator` 等内存模拟器 | Gazebo 中运行的 URDF 设备；`arm_hal` 抽象 |
| 通信 | FastAPI ↔ 前端 | FastAPI ↔ Gateway (新增) ↔ ROS2 节点 ↔ Gazebo |
| 任务下发 | DispatchService → 内部 scheduler | Gateway 接收任务级 Action，桥接到 ROS2 Action |
| 数据 | SQLite（device/task/trace） | 同上不变；增加 `override_log`（人工覆盖审计） |
| 视觉 | Three.js 数字孪生 | Three.js 数字孪生 + 边缘视角嵌入 Gazebo |
| 急停 | 不存在 | 本地 HMI 严格胜出；Web 不暴露清零按钮 |

---

## 1. 集成边界（5 节汇总之第 1 节）

### 1.1 部件与职责

```
┌───────────────────────────────────────────────────────────────┐
│  Web (Vue) — 沿用 Phase 1–4                                   │
│      │  REST / WS                                             │
│      ▼                                                        │
│  FastAPI Gateway (新增 Phase 5)                               │
│      │  Action 接口 + WS 状态回流                              │
│      ▼                                                        │
│  ROS2 Action Server (robot_gateway)                           │
│      │  /robot_gateway/pick_place                             │
│      ▼                                                        │
│  robot_decision → robot_perception → robot_arm_hal            │
│      │  MoveGroup · ExecuteTrajectory · camera/* · estop     │
│      ▼                                                        │
│  Gazebo (gz sim Fortress)                                     │
└───────────────────────────────────────────────────────────────┘
```

### 1.2 关键约束

- **Gateway 只下发任务级 Action**（PickPlace/Navigate/Pause/Resume）；关节级限位、碰撞、速度、加速度保护保留在 `ros2_control` 内部。
- **Gazebo 与真实硬件共享 `arm_hal`**：启动参数按设备 ID 选择 `arm_hal_gazebo` / `arm_hal_ethercat`，决策层不感知差异。
- **Web 实时状态**：事件触发拉取（Action feedback） + 1 Hz 心跳；WS 失联 ≥30 s 黄色提示 + 上次状态快照，不自动跳转。
- **任务幂等**：所有 Action 请求带 `task_id`，网络恢复时可重放或取消。

---

## 2. ROS2 接口契约（第 2 节）

### 2.1 包列表

```
robot_msgs/         # Action/Message/Srv 公共定义
robot_bringup/      # launch + config
robot_moveit_config/# MoveIt SRDF + controllers.yaml
robot_arm_hal/      # 控制器抽象（含 arm_hal_gazebo 与 arm_hal_ethercat）
robot_perception/   # 相机驱动 + 检测 + 6D 位姿 + PlanningScene 更新
robot_decision/     # 状态机 + 故障恢复
robot_gateway/      # ROS2 Action Server (桥接到 FastAPI Gateway)
```

### 2.2 Action

```
# robot_msgs/action/PickPlace.action
# Goal
string task_id
string device_id
geometry_msgs/PoseStamped target
geometry_msgs/PoseStamped place
int8 grasp_topology
string constraints_json
---
# Result
int8 code            # SUCCESS=0 / FAULT=10 / NO_PLAN=20 / ESTOP_ACK=30 / ...
string message
int32 stage_index
---
# Feedback
int32 stage_index
string stage_name
float32 stage_progress
geometry_msgs/PoseStamped tcp_pose
```

### 2.3 Topic

| Topic | Type | QoS | 用途 |
|-------|------|-----|------|
| `/camera/{device_id}/color/image_raw` | Image | BE | RGB 流 |
| `/camera/{device_id}/depth/image_rect_raw` | Image | BE | 深度流 |
| `/perception/{device_id}/detections` | DetectionArray | BE | 检测结果 |
| `/perception/{device_id}/poses` | PoseArray | BE | 6D 位姿 |
| `/perception/{device_id}/scene_delta` | PlanningScene | BE | MoveIt 场景差量 |
| `/robot/{device_id}/state` | JointState + 自定义状态 | RV+TL | 设备实时状态 |
| `/estop` | Bool | RV | 急停全局广播（上升沿有效） |
| `/planning_scene_motion` | DisplayTrajectory | BE | 可视化轨迹 |

### 2.4 TF

```
world → map → robot_base → arm_base → link1 → link2 → link3 → link4 → link5 → link6 → gripper_frame
```

### 2.5 QoS 速记

- **BE**：相机/检测/轨迹（事件触发，最新即可）。
- **RV+TL**：状态、阶段反馈（要最近 10 s）。
- **RV**：急停、清零、override（强一致）。

---

## 3. 安全与恢复（第 3 节）

### 3.1 任务级安全边界

- Gateway 不进入 `ros2_control`；限位/碰撞/速度由 ros2_control 保证。
- 指令带幂等 `task_id`；网络恢复时可重放或取消。
- 急停全局广播：任何节点收到立刻停机；仅本地 HMI 可清除 `e_stop`。

### 3.2 阶段状态机（PickPlace）

```
idle → perceive → grasp_plan → approach → pre_grasp → grasp → lift
     → transit → place_plan → place → retreat → done
```

每阶段：`pre_check` → `execute` → `post_check`；任一阶段失败 → `recover_safe_home` → 错误处理。

### 3.3 `arm_state_mode`（7 态）

```
idle → planning → moving
moving ⇄ halted ⇄ fault
any → e_stop     # 仅本地可清除
fault → recovered # 仅本地可清除
```

### 3.4 故障分类

| 类别 | 默认策略 | 网关语义（result.code/message） |
|------|----------|--------------------------------|
| 通信超时 | 进入 halted，cancel | TIMEOUT（可重试） |
| 关节跟踪误差 | 立即停止 → fault | FAULT（需本地确认） |
| 规划失败 | 单次重试 → 备选抓取 → 失败 | NO_FEASIBLE_PLAN |
| 夹具未响应 | 阶段重试 + 释放/再夹 | GRIPPER_RECOVERED |
| 感知失效 | 退待机（联立采样 N 帧一致后才驱动） | REOBSERVE_REQUIRED |
| 急停 | 物理停机 | ESTOP_ACK |

### 3.5 恢复策略

- **自动恢复**：通信超时、感知失效、规划失败（单次）。
- **半自动恢复**：夹具、跟踪误差 → HMI 一键恢复。
- **人工恢复**：`e_stop`、碰撞事件 → 仅本地 HMI 复位。
- 自动恢复前必须回到 `home_safe` 才允许重试。

### 3.6 多机调度抽象（Phase 6 预留）

Phase 5 顶层调度 Action 收敛为四个：
- `PickPlace` / `Navigate` / `Pause` / `Resume`

---

## 4. Web 交互与边缘视角（第 4 节）

### 4.1 页面骨架（沿用 Phase 1–4）

```
┌──────────────────────────────────────────────────────────────┐
│ 顶栏：设备 · 任务 · 告警 · 日志     角色：operator/supervisor │
├──────────────────────┬───────────────────────────────────────┤
│  设备列表            │  Three.js 仓库视角（WarehouseScene）   │
│  · robot-01 ●        │   · 点击设备 → 边缘视角               │
│  · robot-02 ◐        │   · 浮动检测框 · 任务阶段标签         │
├──────────────────────┴───────────────────────────────────────┤
│  日志抽屉（LogViewer）：告警 / 事件 / WS 状态                │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 边缘视角

- **左 70%**：Gazebo 第一人称 + 点云 + 检测叠加（上限 10 Hz）。
- **右 30%**：任务阶段时间线 + `arm_state_mode` + 限速 + 控制面板。
- **顶部状态条**：连接质量 / 最近心跳 / 当前阶段。
- **底部**：仅观察者模式的"录制"按钮（仿真用）。

### 4.3 权限

| 角色 | 看 | 下发 | 锁定 | 急停清零 |
|------|----|------|------|----------|
| observer | ✓ | × | × | × |
| operator | ✓ | PickPlace/Navigate/Pause/Resume | × | × |
| supervisor | ✓ | + lock_device | ✓ | × |
| local_hmi | — | — | — | **仅本地可清** |

### 4.4 下发任务流程（二段确认）

1. 选择目标 + 放置区
2. 勾选安全约束
3. "确认下发"按钮
4. UI 切到"待接收"→ Action feedback 推进阶段进度

### 4.5 WS 通道

| 通道 | 用途 |
|------|------|
| `/ws/devices` | 设备总览（state · stage） |
| `/ws/edge/{id}` | 边缘视角（camera · 点云 · detection · scene） |
| `/ws/alerts` | 告警全局广播 |
| `/ws/logs` | 审计日志（仅 supervisor 可见） |

### 4.6 supervisor 独占面板

- **PG/SQL 状态面板**（只读）：连接池、慢查询数、SQLite 行数估算、近 1 h 错误码分布。
- **手动 override** 入口：带原因输入，写 `override_log`（who/what/why/before-after 快照）。

### 4.7 渲染频率与降级

- 边缘视角上限 **10 Hz**；过载自动降到 5 Hz；点位只推增量。
- 优先级：相机流 > 点云 > 检测叠加。
- WS 失联 ≥30 s → 黄色提示 + 上次状态快照（不自动跳转）。

---

## 5. 里程碑与验收（第 5 节）

### 5.1 里程碑（按依赖顺序）

| 里程碑 | 范围 | 验收脚本 | 通过条件 |
|--------|------|---------|---------|
| **M0** | ROS2 工作区 + `robot_*` 包骨架 + `robot_bringup` + Gazebo 空世界 | `scripts/verify_m0.sh` | 空世界启动 + 核心话题可列 |
| **M1** | URDF/SRDF + MoveIt + `ros2_control` + `arm_hal_gazebo` | `scripts/verify_m1.sh` | `ExecuteJointTrajectory` 实现 home → target → home |
| **M2** | 相机 + 检测 + 6D 位姿 + PlanningScene 同步 | `scripts/verify_m2.sh` | rosbag2 播放 → 检测与人工标注差 ≤ 阈值 |
| **M3** | 状态机 + PickPlace 闭环 + 故障注入 | `scripts/verify_m3.sh` | `PickPlace` Action + Gazebo 回放闭环 |
| **M4** | FastAPI Gateway + WS + 边缘视角 + supervisor 面板 | `scripts/verify_m4.sh` | 提交任务 → UI 阶段进度 → 审计日志匹配 |
| **M5** | 一键全链 + 录像 + 验收单 | `scripts/verify_m5.sh` | 一键启动 + mp4 + json 验收单 |

### 5.2 度量阈值

- 闭环成功率 **≥ 90%**（CI 中自动跑 10 次）。
- 动作最长周期 **≤ 90 s**。
- 急停 → 停机响应 **≤ 200 ms**。
- WS 重连后 UI **≤ 2 s** 对齐。

### 5.3 CI 集成

- 每个里程碑 PR 必需通过 `verify_*.sh`。
- `nightly.yml` 跑 M5 全链路，产出 artifacts（rosbag2 + mp4 + 验收单 JSON）。
- nightly 仅记录耗时与产出，不阻断 PR；命中率超过 20% 失败率自动报警。

### 5.4 风险与回退

| 风险 | 回退开关 |
|------|----------|
| URDF/SRDF 与 MoveIt 不一致 | `disable_collision_objects` |
| 感知误报 | 联立采样门控 → 关闭感知仍可走纯位置轨迹 |
| `ros2_control` 在 Gazebo 与真实硬件差异 | `arm_hal` 双实现 |
| WS 失联 | UI "上次已知状态" 快照 |

---

## 6. 文件落点（与 Phase 1–4 共存，不侵入）

```
robot-logic/
├── backend/
│   ├── gateway/                # 新增 Phase 5
│   │   ├── __init__.py
│   │   ├── ws_devices.py       # /ws/devices
│   │   ├── ws_edge.py          # /ws/edge/{id}
│   │   ├── ws_alerts.py        # /ws/alerts
│   │   ├── ws_logs.py          # /ws/logs（仅 supervisor）
│   │   ├── tasks.py            # /api/devices/{id}/tasks（任务级 Action 桥接）
│   │   ├── supervisor.py       # PG/SQL 状态 + override
│   │   └── override_log.py     # 审计写入
│   └── （Phase 1–4 内容保持不变）
├── frontend/
│   ├── src/
│   │   ├── edge/                # 新增 Phase 5
│   │   │   ├── EdgeView.vue
│   │   │   ├── CameraOverlay.vue
│   │   │   ├── PointCloudOverlay.vue
│   │   │   ├── StageTimeline.vue
│   │   │   └── SafetyPanel.vue
│   │   └── supervisor/          # 新增 Phase 5
│   │       ├── DbStatus.vue
│   │       └── ManualOverride.vue
│   └── （Phase 1–4 内容保持不变）
├── ros2_ws/                     # 新增 Phase 5
│   └── src/
│       ├── robot_msgs/
│       ├── robot_bringup/
│       ├── robot_moveit_config/
│       ├── robot_arm_hal/
│       ├── robot_perception/
│       ├── robot_decision/
│       └── robot_gateway/
├── scripts/                     # 新增 Phase 5
│   ├── verify_m0.sh
│   ├── verify_m1.sh
│   ├── verify_m2.sh
│   ├── verify_m3.sh
│   ├── verify_m4.sh
│   └── verify_m5.sh
├── data/
│   ├── rosbag2/                 # 新增 Phase 5
│   └── verify_artifacts/        # 新增 Phase 5
└── docs/
    ├── superpowers/
    │   ├── specs/
    │   │   ├── 2026-07-23-robot-logic-prototype-design.md  # 已存
    │   │   └── 2026-07-23-robot-logic-phase5-design.md    # 本文件
    │   ├── plans/
    │   │   ├── 2026-07-23-robot-logic-prototype.md         # 已存
    │   │   └── 2026-07-23-robot-logic-phase5-plan.md       # 后续另写
    │   └── instructions/
    │       └── phase5-handoff.md
    └── algorithm/                # 已存（继续参考）
```

---

## 7. 待办与未决项（写到 Phase 5 实施计划前收敛）

1. M0：选择 `ros_distro`（Humble 默认）与 Gazebo 版本（Fortress 推荐；Gz Harmonic 在 ROS2 Jazzy 才默认）。
2. M1：是否在 Phase 5 中引入 `ros2_controllers` 的 `joint_trajectory_controller` 与 `gripper_action_controller` 的示例。
3. M2：检测模型采用预训练权重是否允许在 PR 携带大型文件？若否，使用云端 mock。
4. M3：故障注入接口的位置（建议在 `robot_decision` 中加 `fault_injection` 服务，仅 CI 启用）。
5. M4：WS 反压策略——单条消息 ≥ 64 KB 自动截断。
6. M5：录像格式 mp4 H.264 5 Mbps + 验收单 JSON（包含每个阶段耗时 + 关节误差）。
