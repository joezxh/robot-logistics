# Architecture — Robot Logic Monorepo

This document describes the four sub-projects, their dependency directions, and
the communication matrix between them. It is the companion to the
[four-subproject split design spec](superpowers/specs/2026-08-07-four-subproject-split-design.md).

> **Last updated**: 2026-08-09 — Phase 2 (感知与导航) Task 1-6 完成；合成传感器、Runtime 集成、SSE 端点、PointCloudProcessor、Nav2 BaseExecutor、Nav2 参数配置已落地。

## Dependency direction (enforced)

```
        shared/  (zero-dep contracts)
          ▲   ▲
          │   │
   rcs/ ──┘   └── robot-app/
     ▲
     │ (embedded via router, or standalone via HTTP/MQTT)
     │
 simulation/ ──────────────┐
                            │ (colcon underlay overlay)
                     robot-app/robot_arm_hal (单臂 underlay)
                     robot-app/robot_dual_arm_hal (双臂，叠加于 underlay)

 vla-training/  (standalone pipeline, deploys artifacts to robot-app/robot_decision)
```

Rules:

- `shared/` depends on **neither** `rcs/` nor `robot-app/`. It is pure
  data — JSON Schemas + a dependency-free Python package.
- `rcs/` must **not** import the simulation backend. It owns its own
  `config.py` / `security.py`.
- `robot-app/` depends on `shared/` for wire contracts, and on
  `robot_arm_hal` (单臂 6-DOF，作为 colcon underlay 由 simulation 工作区提供)
  与 `robot_dual_arm_hal`（双臂，关节名带 left_/right_ 前缀，叠加于 underlay）。
- `vla-training/` is decoupled; it only emits inference artifacts consumed by
  `robot-app/robot_decision`.

These directions are checked by `scripts/verify_split.sh`.

## Sub-project responsibilities

### `rcs/` — Robot Control System

- **Core**: device registry, control loop (`loop.py`), controllers
  (arm/agv/stacker), kinematics + planning (`planning/`), simulated HAL
  (`hal/`), state + event types (`state/`, `events.py`).
- **Dual mode**:
  - *Embedded* — the simulation backend mounts `rcs.router()` under
    `/api/rcs` and drives `rcs.lifespan()`.
  - *Standalone* — `rcs.app.create_app()` builds a self-contained FastAPI app
    on its own port (default `8100`).
- **MQTT adapter** (`rcs/mqtt/`): republishes `StateStream` (downsampled, QoS 0)
  and `EventBus` alerts (QoS 1); subscribes command topics (QoS 1) and routes
  them through the **same** `on_command()` path as REST. Never touches the
  1 kHz tick.
- **Tests**: 85 passed。

### `simulation/` — Logistics simulation

- **backend/**: FastAPI orchestration — devices, tasks, sites, alerts, logs,
  metrics (SSE). Embeds RCS when `RCS_EMBEDDED=true`. Includes
  `SimulationMqttBridge` for MQTT communication with `robot-app`.
  Supports 5 devices: `robot-01`, `loader-01`, `agv-01`, `agv-02`, `stacker-01`.
  **Phase 2 new**: `PointCloudGenerator`（合成深度相机点云）、
  `LaserScanGenerator`（合成 2D LIDAR）、Runtime 集成传感器数据生成、
  SSE 端点 `/api/devices/{id}/detections`（10Hz）+ `/nav_path`（1Hz）。
- **frontend/**: Vue 3 + Vite + Three.js dashboard. Calls `/api/*` and `/ws`
  relative paths — unchanged by the split. Renders `LoaderRobot` (dual-arm AGV
  with `AgvBase` + dual `RobotArm` + hug paddles), `RobotArm`, and warehouse
  scene. SSE joint endpoint at `/api/devices/{device_id}/joints` (30Hz).
  **Phase 2 plan**: `DetectionOverlay`、`NavPathOverlay`、`CostmapOverlay` 组件。
- **ros2_ws/**: `robot_bringup` (depends on `robot_arm_hal` via underlay) and
  `robot_moveit_config`.
- **Tests**: 89 passed (backend)。

### `robot-app/` — Robot-side application

- **robot_gateway**: MQTT ↔ ROS 2 bridge. Receives commands (QoS 1) from RCS,
  forwards to local ROS 2 graph via `~/motion_command` and `~/task_command`;
  publishes state (QoS 0) via `~/robot_state` and telemetry (QoS 0).
  Buffers while the broker is unreachable. Includes `task_sink` routing for
  `execute_task` commands → `TaskCoordinator`.
- **robot_msgs**: local message contracts mirroring `shared/contracts`.
  Dataclasses: `CommandMsg`, `MoveCommandGoal`, `Pose6DMsg`, `RobotStateMsg`,
  `RobotTelemetryMsg`, `TaskCommandMsg`, `HugParamsMsg`, `BaseStateMsg`,
  `HugStateMsg`. Zero rclpy dependency.
- **robot_decision**: behavior layer — `TaskCoordinator` (9-phase FSM + ABORTING),
  `TaskCoordinatorNode` (ROS 2 wrapper with adapter layer), `BaseExecutor`
  (waypoint following), `ArmExecutor` (MoveIt), `HugController` (dual-arm
  synchronous hug), `SafetyMonitor` (independent safety interlocks),
  `MoveItClient`, `MotionPlannerNode`.
- **robot_dual_arm_hal**: 双臂 HAL — `arm_hal.ros2_control.xacro` (6-DOF macro)
  + `dual_arm.ros2_control.xacro` (left/right instantiation via `arm_id`)；
  `robot_arm_hal` 单臂作为 underlay 保持不变。
- **robot_base_hal**: diff-drive base HAL — `base.ros2_control.xacro` +
  `loader.urdf.xacro` + `diff_drive.yaml` controller config.
- **robot_perception**: 7 步点云处理管线 — `PointCloudProcessor`
  （PassThrough → VoxelGrid → StatisticalOutlier → RANSAC → EuclideanCluster
  (Union-Find 26-邻域连通分量) → BBox → Pose），纯 Python + numpy 实现，
  输出 `Detection3DArray` 兼容 dict。配置文件
  `config/point_cloud_processor.yaml`。
- **Tests**: 43 passed (decision), 44 passed (gateway), 7 passed (perception)。

### `vla-training/` — VLA pipeline (skeleton)

Data collection → conversion (RLDS/LeRobot-style) → LoRA fine-tune →
evaluation → inference export. Declares `torch`/`transformers`/`peft` but does
**not** download weights or run training. Export target: `robot-app/robot_decision`.
- **Tests**: 40 passed。

### `shared/` — Communication contracts

- `contracts/*.schema.json`: command / state / alert / telemetry JSON Schemas.
- `python/robot_contracts/`: topic builders + Pydantic payload models, kept in
  lock-step with the schemas. Imported by both `rcs/` and `robot-app/`.

## Communication matrix

| Channel | From → To | Topic | QoS | Notes |
| --- | --- | --- | --- | --- |
| Command | RCS → robot | `rcs/{device_id}/command` | 1 | validated, queued, back-pressured |
| State | robot/RCS → broker | `rcs/{device_id}/state` | 0 | downsampled (default 10 Hz) |
| Alert | RCS → broker | `rcs/{device_id}/alert` | 1 | `EventBus` events |
| Telemetry | robot → broker | `robot/{device_id}/telemetry` | 0 | battery/temp/connectivity |

**Command types** (in `command.schema.json`):

| type | purpose | key fields |
| --- | --- | --- |
| `move_j` | joint-space motion | `target_joints[]`, `speed_scale` |
| `move_l` | Cartesian linear motion | `target_pose{x,y,z,rx,ry,rz}` |
| `execute_task` | task-level command | `task_type`, `parameters`, `group` |
| `estop` | emergency stop | independent fast path |
| `stop` / `home` / `recover` | debug passthrough | — |

**Task types** (`execute_task.task_type`):

| task_type | FSM entry phase | executor |
| --- | --- | --- |
| `goto` | navigating | BaseExecutor |
| `pick_box` | navigating → ... → hugging | ArmExecutor + HugController |
| `place_box` | navigating → ... → placing | ArmExecutor + HugController |
| `home_all` | retreating → idle | all executors |

REST surface (embedded under `/api/rcs`, standalone on `:8100`):

- `GET  /api/rcs/registry`
- `POST /api/rcs/{device_id}/command`
- `GET  /api/rcs/{device_id}/state`
- `POST /api/rcs/{device_id}/estop` / `clear_estop`
- `GET  /api/rcs/_health` and `GET /health` (standalone only)

SSE endpoints (simulation backend):

- `GET /api/devices/{device_id}/joints` — real-time joint positions (30Hz)
- `GET /api/devices/{device_id}/detections` — perception detections (10Hz) ✨ Phase 2
- `GET /api/devices/{device_id}/nav_path` — navigation path (1Hz) ✨ Phase 2
- `GET /api/logs/stream` — live log entries
- `GET /api/alerts/stream` — alert state transitions

See [`API.md`](API.md) for full request/response shapes.

## Roadmap — Phase 2

Phase 2 (感知与导航) adds synthetic sensor data, a PCL point cloud pipeline,
Nav2 integration, and frontend perception overlays. Target: ~308 total tests.

| Area | Change | Status |
| --- | --- | --- |
| Simulation backend | `PointCloudGenerator` + `LaserScanGenerator` + Runtime 集成 | ✅ 完成 |
| SSE 端点 | `/api/devices/{id}/detections` (10Hz), `/nav_path` (1Hz) | ✅ 完成 |
| robot_perception | 7 步 numpy 管线 → `Detection3DArray`（Union-Find 聚类） | ✅ 完成 |
| robot_decision | `BaseExecutor` 重构为 Nav2 `NavigateToPose` action client | ✅ 完成 |
| Nav2 参数 | `config/nav2_params.yaml`（costmap, DWB, recovery） | ✅ 完成 |
| Frontend | `DetectionOverlay` (3D bbox), `NavPathOverlay`, `CostmapOverlay` | 🔲 进行中 |
| WarehouseScene | 集成 Overlay 组件到 3D 场景 | 🔲 待开始 |
| 集成测试 | 端到端感知-导航闭环验证 | 🔲 待开始 |

Full plan: [`docs/superpowers/plans/2026-08-09-phase2-perception-navigation.md`](superpowers/plans/2026-08-09-phase2-perception-navigation.md).
