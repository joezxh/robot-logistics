# Robot Logic — RCS 机器人控制系统 设计规范（RCS-1 运动控制）

> **创建日期**：2026-07-24
> **文档类型**：技术方案设计（RCS-1 · 运动控制子系统）
> **版本**：v0.1（草案）
> **关联文档**：
> - `docs/superpowers/specs/2026-07-23-robot-logic-prototype-design.md`（Phase 1–4：FastAPI + 模拟器原型）
> - `docs/superpowers/specs/2026-07-23-robot-logic-phase5-design.md`（Phase 5：Gazebo/ROS2 集成）
> - `docs/algorithm/02-motion-planning.md`（运动规划算法参考）
> - `docs/algorithm/04-task-scheduling.md`（后续 RCS-3 任务调度的上游）

> **范围说明**：本规范只覆盖 RCS-1（运动控制子系统）。完整 RCS 包含 5 个能力柱（运动 / 感知 / 调度 / 安全 / HMI），其余 4 个柱按各自 spec 落地。RCS-1 是第一个落地柱，本规范定义其与 FastAPI、HAL、上层业务的边界与最小可用形态。RCS-1 不感知 Phase 5 Gazebo/真机——HAL 接口预留，Gazebo HAL 在 Phase 5 后续迭代中以新增 `hal_gazebo` 子包实现，**不修改本规范定义的 `controllers/`、`loop.py`、`service.py`**。

---

## 0. RCS 总览与拆分（README 必读）

完整 RCS 是一个完整控制平面；本次只做 RCS-1 运动控制。

| 柱 | 名称 | 关键职责 | 本期是否在 RCS-1 |
|----|------|----------|------------------|
| RCS-1 | 运动控制 | 运动学/轨迹/闭环/状态机 | **本规范** |
| RCS-2 | 感知融合 | 视觉/6D 位姿/PlanningScene | 后续 spec |
| RCS-3 | 任务调度 | 多机编排/优先级/抢占 | 后续 spec |
| RCS-4 | 安全联锁 | 急停/区域互锁/碰撞 | 后续 spec（与 Phase 5 §3 协同） |
| RCS-5 | HMI 集成 | 边缘视角/控制面板/审计 | 后续 spec |

**RCS-1 在工程中的位置**：`backend/rcs/` 独立子包，对外只暴露 FastAPI 路由（REST + WS）。Phase 1–5 已有代码完全不动；`backend/main.py` 仅在 `lifespan` 中加 `await rcs.startup()` / `await rcs.shutdown()` 与一行 `app.include_router(rcs_router)`。

**与 Phase 5 的关系**：Phase 5 §1.1 的 Gateway 收到"任务级 Action"（PickPlace/Navigate/Pause/Resume）后，将来可调用 RCS-1 的 REST 接口来下发给具体设备。本期 Phase 5 与 RCS-1 不互联（Phase 5 spec 中 Gateway 直发 ROS2 Action；RCS-1 走纯算法/服务路径），二者通过 `DeviceHAL` 协议在未来汇合——Phase 5 实现 `arm_hal_gazebo` 时把 HAL 实现替换为 Gazebo 实现，RCS-1 控制器与上层无感。

---

## 1. 架构总览

```
┌──────────────────────────────────────────────────────────────┐
│  Web (Vue)  ──沿用 Phase 1–5 UI，本期新加 RCS-1 概览面板 ──       │
│      │  REST / WS  (新加 /api/rcs/* 与 /ws/rcs/*)              │
│      ▼                                                        │
│  FastAPI 主进程 (现有 main.py)                                  │
│      │  include_router(rcs_router)  ← 仅此一行侵入               │
│      ▼                                                        │
│  backend/rcs/  (新包，独立子包)                                  │
│      ├─ service.py   REST + WS 路由                            │
│      ├─ loop.py      ControlLoop 协程 (1 kHz 机械臂 / 50 Hz AGV)│
│      ├─ registry.py  构型→Controller 映射                       │
│      ├─ controllers/ ArmController / AgvController /           │
│      │              StackerController                          │
│      ├─ planning/    FK/IK/Trajectory/Interpolator             │
│      ├─ hal/         DeviceHAL 协议 + SimHAL 实现 (本期唯一)     │
│      └─ state/       共享 dataclass (JointState/Pose6D/...)     │
└──────────────────────────────────────────────────────────────┘
```

**关键不变量**

1. **RCS-1 不可知**：RCS-1 不读、不写 `algorithm/simulator/`、`services/runtime.py`、SQLite、HAL 之外的任何业务服务。`SimHAL` 内部用纯数学模型（连杆参数 + 简单动力学），与 `algorithm/simulator/` 的设备并存但解耦。
2. **HAL 解耦**：闭环控制指令（位置/速度/扭矩）只走 `DeviceHAL.write()`；上层业务只通过 REST/WS 看状态、下发"任务级指令"。Gazebo/真机接入只换 HAL 实现，控制器与上层业务无感。
3. **控制频率分档**：按构型区分——机械臂 1 kHz，AGV/堆垛机 50 Hz。频率由 `DeviceProfile.control_hz` 声明，`ControlLoop` 启动时按声明起 tick 协程。
4. **不写历史数据**：本期 RCS-1 不写 SQLite，不写 `override_log`（与 Phase 5 §4.6 留待 Phase 5 HMI spec 统一处理）。所有命令与状态在 `EventBus` 内可被订阅者拿走，本期不接 AlertEngine。

---

## 2. 数据流

### 2.1 指令路径（上层下发）

```
HTTP POST /api/rcs/{device_id}/command
   body: { command_id: uuid, type: "move_j" | "move_l" | "stop" | "home" | "estop" | "recover", ... }
   ↓
RCSService.queue_command()                 # 入控制器命令队列 (asyncio.Queue, maxsize=1024)
   ↓
Controller.execute()                       # 在 ControlLoop tick 中消费
   ├─ planning.IK.solve()                  # 末端→关节（move_l）
   ├─ planning.Trajectory.from_waypoints() # 生成轨迹点序列
   └─ hal.write(state) → 下一 tick 跟踪
```

### 2.2 控制环 tick（每构型独立协程，频率可配）

```
loop.ControlLoop.tick():
    hal_state = await hal.read(device_id)              # 读反馈
    target    = controller.update(hal_state)           # 计算下一拍参考
    err       = controller.tracking_error()            # 用于告警 + 状态回流
    if not is_finite(target):                          # NaN/Inf 防御
        return                                          # 丢弃本 tick
    await hal.write(device_id, target)                  # 写指令
    if err.max_joint_error > rad_th or err.position_error_m > pos_th:
        controller.halt()                               # 跟随误差超限 → 停
    state_stream.publish(device_id, hal_state, err)    # 给 WS 订阅者
```

### 2.3 状态回流路径

```
state_stream (内存 broadcast)  ──push──▶  WS /ws/rcs/{id}        (10 Hz 限频)
                                ──push──▶  WS /ws/rcs/overview   (10 Hz 限频)
                                ──push──▶  GET /api/rcs/{id}/state (REST 拉取)
                                ──event──▶  EventBus (本期无订阅者)
```

**WS 限频规则**：每个设备每 100 ms 最多发 1 帧（10 Hz）。多 tick 的状态合并为最新一帧；超过 64 KB 自动降级——只发关节角/位姿/模式，去掉调试字段。降级状态通过 `state.degraded: true` 告知前端。

**幂等性**：所有 `Command` 带 `command_id`（UUID）。控制器在执行前查重；同一 `command_id` 第二次进入直接返回原结果，不重复执行。

### 2.4 数据契约核心类型（`backend/rcs/state/`）

| 类型 | 关键字段 |
|---|---|
| `JointState` | positions, velocities, efforts, timestamp, device_id |
| `Pose6D` | position(3), orientation(四元数 [w,x,y,z]) |
| `TrackingError` | max_joint_error, position_error_m, timestamp |
| `Command` | command_id, type, target_pose?, target_joints?, speed_scale, constraints |
| `DeviceProfile` | morphology (`arm|agv|stacker`), num_joints, limits, control_hz |
| `ControllerState` | mode (`idle|running|halted|fault|e_stop`), active_command_id, last_error |

每个字段为 dataclass + `to_dict()`，FastAPI 直接序列化；时间戳统一 `time.monotonic_ns()`。

---

## 3. 组件职责与接口

### 3.1 `DeviceHAL` 协议（`backend/rcs/hal/protocol.py`）

```python
class DeviceHAL(Protocol):
    async def read(self, device_id: str) -> JointState: ...
    async def write(self, device_id: str, target: JointState) -> None: ...
    async def estop(self, device_id: str) -> None: ...
    def profile(self, device_id: str) -> DeviceProfile: ...
```

- **唯一本期实现**：`SimHAL`（`backend/rcs/hal/sim.py`）。内部用数学模型——机械臂用连杆参数 + DH，AGV 用差速运动学，堆垛机用升降+行走双轴。不调真实硬件。
- **未来实现**：Phase 5 接入 Gazebo 时，新增 `backend/rcs/hal/gazebo.py`，**不修改** `controllers/` 与 `loop.py`。

### 3.2 `Controller` 抽象（`backend/rcs/controllers/base.py`）

```python
class Controller(ABC):
    morphology: ClassVar[Morphology]
    @abstractmethod
    def update(self, hal_state: JointState) -> JointState: ...
    @abstractmethod
    def tracking_error(self) -> TrackingError: ...
    def on_command(self, cmd: Command) -> None: ...
    def halt(self) -> None: ...
    def recover(self) -> None: ...
    @property
    def mode(self) -> ControllerMode: ...
```

- **`ArmController`**：6DOF，关节空间 PD 控制（默认 kp=80, kd=8，可在 profile 覆盖）；IK 解析解（不带奇异规避，超出奇异区由 `error.message` 提示）。1 kHz。
- **`AgvController`**：差速底盘，速度指令 + 里程计反馈；控制律用 P 控制 + 速度前馈。50 Hz。
- **`StackerController`**：升降+行走双轴，独立伺服；控制律同 AgvController，复用轨迹时间最优缩放。50 Hz。
- **共用代码** `controllers/_common.py`：限位裁剪（关节/速度/加速度）、误差阈值、命令队列、HALT/RECOVER 转换。

### 3.3 `ControlLoop`（`backend/rcs/loop.py`）

- 启动时按 `DeviceProfile.control_hz` 为每个设备起一个 tick 协程。
- tick 周期用 `asyncio.sleep(1/hz)` + 单调时间补偿；用 `asyncio.gather(..., return_exceptions=True)` 防单设备异常拖垮全局。
- 关闭时 `loop.cancel_all()`；`main.py` 现有 `lifespan` 钩子里挂上 `await rcs.shutdown()`。

**单进程限频策略**：

- `loop.py` 提供 `tick_guard(hz, max_drift=0.05)` 装饰器；若累计漂移 > 5%，自动降级该设备的实际频率并打 WARN 日志。
- 全局一个 `LoopHealth` 指标对象（不在 Prometheus exporter 范围；仅 `/api/rcs/_health` 内部使用），记录每个设备的实际频率、漂移、ticks 数。

### 3.4 `RCSService`（`backend/rcs/service.py`）

- **REST**：
  - `POST /api/rcs/{id}/command` 提交指令（带 `Depends(get_current_user)`）
  - `GET /api/rcs/{id}/state` 拉取当前状态
  - `GET /api/rcs/registry` 列出所有设备与构型
  - `POST /api/rcs/{id}/estop` 急停（任何已认证用户）
  - `POST /api/rcs/{id}/clear_estop` 清急停（**Phase 4 当前无角色模型**——本期清急停仅以"调用方知道设备 ID + 持有有效 API-key"为限；角色判定待 Phase 5 HMI spec 统一加 RBAC 后再收紧）
  - `GET /api/rcs/_health` 内部健康
- **WS**：
  - `/ws/rcs/{id}` 单设备状态（10 Hz）
  - `/ws/rcs/overview` 全部设备概览（10 Hz）
- 不实现认证/限流——复用 Phase 4 的 `security.py`，通过 `Depends(get_current_user)` 注入。

### 3.5 `registry.py`

- 启动时从环境变量 `RCS_DEVICE_PROFILES`（JSON 数组）加载设备清单；缺省时按 `device_id` 哈希分到三种构型（开发态）。
- 提供 `get_controller(device_id) -> Controller` 与 `get_hal() -> DeviceHAL` 单例。
- 设备清单 schema：

  ```json
  [
    { "device_id": "robot-01", "morphology": "arm", "control_hz": 1000, "limits": {...} },
    { "device_id": "agv-01",   "morphology": "agv",  "control_hz": 50,   "limits": {...} }
  ]
  ```

### 3.6 `planning/`

- **`fk.py`**：6DOF 标准 DH 正运动学；位姿→变换矩阵。
- **`ik.py`**：6DOF 解析解（无奇异规避）；超出工作空间或奇异区时返 `NoSolution` 而非抛异常。
- **`trajectory.py`**：梯形/五次多项式插值 + 时间最优缩放（基于速度/加速度限位）。返 `Trajectory` 序列。
- **`interpolator.py`**：把轨迹离散成 1 ms 步长点；`Controller.update()` 取下一拍参考。

**依赖清单**（`backend/requirements.txt` 新增）：

- `uvloop==0.19.0`（asyncio 加速，仅在 `main.py` 检测到则替换 `asyncio.run` 事件循环）
- `numpy`（已在）
- `scipy`（仅 `Rotation` 工具；如未在 requirements 中则加入；版本随 scipy 主线）

---

## 4. 错误处理 / 安全 / 告警

### 4.1 指令层错误（FastAPI 4xx/5xx）

| 错误 | HTTP | 处理 |
|---|---|---|
| 设备不存在 | 404 | `registry.lookup` miss |
| 设备被 lock | 423 | Phase 5 后续：复用 `lock_device` 概念，本期留字段 `profile.locked` 不实现 |
| 指令参数非法 | 422 | pydantic 校验 |
| 控制器 HALTED | 409 | 提示先发 `recover` |
| 队列满（>1024） | 503 | backpressure，返回 `Retry-After: 1` |

### 4.2 控制环错误（运行时保护）

| 类别 | 检测 | 动作 |
|---|---|---|
| 跟随误差超限 | `max_joint_error > rad_th` 或 `position_error_m > pos_th` | 自动 HALT；进入 `halted` 态 |
| 指令 NaN/Inf | 写前校验（`numpy.isfinite`） | 丢弃该 tick，不写 HAL |
| HAL read 超时 | `asyncio.wait_for(hal.read, 0.05)` | 单次重试；连续 3 次 → `fault` |
| HAL write 失败 | 异常向上 | 当前 tick 跳过；连续 5 次 → `fault` |
| 轨迹超时 | 累计执行时间 > plan ×1.5 | HALT + 上报 |

阈值（默认值，可在 `DeviceProfile.limits` 覆盖）：

- `rad_th = 0.05 rad`
- `pos_th = 0.01 m`
- `read_timeout = 0.05 s`（机械臂）/`0.2 s`（AGV/堆垛机）
- `write_timeout = 0.02 s`（机械臂）/`0.1 s`（AGV/堆垛机）

`halted` 态可由 REST `recover` 恢复；`fault` 态只能本地 HMI 清（与 Phase 5 §3.5 一致——RCS-1 本期无 HMI，留接口 `clear_fault`）。

### 4.3 告警出口

RCS-1 **不直连** AlertEngine。它把以下事件以 `asyncio.Event` 形式投到内部 `EventBus`（`backend/rcs/events.py`）：

- `tracking_error_over_threshold`
- `hal_read_timeout`
- `hal_write_failure`
- `controller_halted`
- `controller_fault`
- `estop_pressed` / `estop_cleared`

`EventBus` 暴露 `subscribe(event_name, callback)` 接口。**本期不实现订阅者**，避免侵入 AlertEngine；Phase 5 后续由 `services/alerts.py` 订阅。

### 4.4 急停

RCS-1 暴露 `POST /api/rcs/{id}/estop`（任何已认证用户可调）。`clear_estop` 任何已认证用户可调，但要求 API-key 与设备绑定关系由 Phase 5 RBAC 统一收紧（Phase 4 `security.py` 当前无角色模型）。本地 HMI 清零在 Phase 5 实现。

急停链路：

1. HTTP `estop` → `controller.estop()`（立即置 `mode = e_stop`）。
2. tick 协程检测到 `e_stop` 模式 → 跳过 `update()`，不写 HAL。
3. 状态推流：mode 变更立即推 1 帧（不受 10 Hz 限频），保证 UI 实时反应。

### 4.5 审计

`override_log`（Phase 5 §4.6）**不写**——RCS-1 的所有命令自然落入 `command_log`（WS 旁路），覆盖期同样不需人工 override。审计由 Phase 5 统一处理。

---

## 5. 测试与验收

### 5.1 单元测试（`backend/rcs/tests/`）

| 模块 | 用例 | 关键断言 |
|---|---|---|
| `fk` | 已知位姿正反解闭环 | `FK(IK(p)) == p`（容差 1e-6） |
| `ik` | 奇异区、超出工作空间 | 返 `NoSolution` 而非异常 |
| `trajectory` | 梯形/五次多项式在限位内 | 峰值速度/加速度 ≤ 限位 |
| `controller` | 阶跃响应 | 稳态误差 < 0.01 rad |
| `sim_hal` | read/write 往返 | 写后 read 与目标一致 |
| `loop` | 1 kHz 周期性 | 1000 tick 实测耗时 ∈ [0.95, 1.05] s |
| `event_bus` | subscribe 接收 | 事件投递 ≤ 1 ms |

### 5.2 集成测试（`backend/rcs/tests/integration/`）

| 场景 | 步骤 | 通过条件 |
|---|---|---|
| 端到端 `move_j` | POST /command → 等 1 s → 拉 state | 关节角进入目标 ±0.01 rad |
| 端到端 `move_l` | POST → 拉 state | TCP 位姿与目标 ≤ 5 mm |
| 急停链路 | POST estop → 拉 state | `state.mode == e_stop` |
| 跟随误差注入 | 测试桩 HAL 注入偏差 | 控制器进入 `halted` |
| WS 10 Hz | 订阅 `/ws/rcs/overview` 1 s | 收到 8–12 帧 |
| 幂等 | 同一 `command_id` 发两次 | 第二次返回原结果，不重复执行 |
| 队列背压 | 1 kHz 灌入 >1024 条 | 第 1025 条返 503 |

### 5.3 验收脚本（`scripts/verify_rcs1.sh`）

- 启动后端 → 等就绪 → 跑 5 个集成测试 → 收 1 s WS 帧 → 输出 JSON 验收单（与 Phase 5 `verify_m5.sh` 同款风格）。
- 阈值：闭环成功率 ≥ 95%（本地 sim）；1 kHz 抖动 < 5%。
- 产物：`docs/superpowers/specs/verify_artifacts/rcs1-{timestamp}.json`。

### 5.4 回归与现有测试

- 现有 32 个 pytest 测试（Phase 4 提交 `4a322f5`）必须全过。
- RCS-1 测试与现有测试解耦（不同目录、不同 fixture，不共享 mutable 全局）。
- 验证方式：`pytest backend/tests backend/rcs/tests`。

### 5.5 不在本期范围

- Gazebo/真机硬件集成（HAL 协议已定义，实现后续）
- 与 AlertEngine 的事件订阅实现（只留 EventBus）
- supervisor HMI / lock 业务（仅留字段）
- IK 奇异规避
- 与 Phase 5 Gateway 的互联（Phase 5 spec 中 Gateway 直发 ROS2 Action）

---

## 6. 文件落点（与现有工程共存，不侵入）

```
robot-logic/
├── backend/
│   ├── rcs/                    # 新增 RCS-1
│   │   ├── __init__.py
│   │   ├── service.py          # FastAPI 路由 + WS
│   │   ├── loop.py             # ControlLoop
│   │   ├── registry.py         # 设备清单 + 单例
│   │   ├── events.py           # EventBus
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # Controller 抽象
│   │   │   ├── _common.py      # 限位裁剪/误差阈值/队列
│   │   │   ├── arm.py
│   │   │   ├── agv.py
│   │   │   └── stacker.py
│   │   ├── planning/
│   │   │   ├── __init__.py
│   │   │   ├── fk.py
│   │   │   ├── ik.py
│   │   │   ├── trajectory.py
│   │   │   └── interpolator.py
│   │   ├── hal/
│   │   │   ├── __init__.py
│   │   │   ├── protocol.py     # DeviceHAL
│   │   │   └── sim.py          # SimHAL (本期唯一)
│   │   ├── state/
│   │   │   ├── __init__.py
│   │   │   ├── joint.py
│   │   │   ├── pose.py
│   │   │   ├── command.py
│   │   │   ├── error.py
│   │   │   ├── profile.py
│   │   │   └── controller_state.py
│   │   └── tests/
│   │       ├── conftest.py
│   │       ├── unit/
│   │       └── integration/
│   └── （Phase 1–5 内容保持不变；仅 main.py lifespan 注入 rcs.startup/shutdown 与 include_router）
├── frontend/
│   └── （本期不新增面板；后续 RCS-5 HMI spec 统一处理）
├── scripts/
│   └── verify_rcs1.sh          # 新增
├── docs/
│   ├── superpowers/
│   │   ├── specs/
│   │   │   ├── 2026-07-23-robot-logic-prototype-design.md  # 已存
│   │   │   ├── 2026-07-23-robot-logic-phase5-design.md    # 已存
│   │   │   └── 2026-07-24-rcs-1-motion-control-design.md  # 本文件
│   │   ├── plans/
│   │   │   └── 2026-07-24-rcs-1-motion-control.md         # 后续另写
│   │   └── instructions/
│   │       └── rcs-1-handoff.md
│   └── algorithm/                # 已存（继续参考）
└── （其它全部保持不变）
```

**`main.py` 唯一修改点**（参考示意，最终以实施计划为准）：

```python
# 在 create_app() 末尾：
from backend.rcs.service import rcs_router
from backend.rcs import rcs
app.include_router(rcs_router, prefix="/api/rcs")

# 在 lifespan 上下文：
async with rcs.lifespan():
    yield
```

---

## 7. 待办与未决项（写到 RCS-1 实施计划前收敛）

1. **HMI 面板** 本期不写 Vue 面板——是否在 Phase 5 spec 中合并入 RCS-5 HMI spec？建议：是。
2. **uvloop** 兼容性——`uvloop` 在 Windows + Python 3.11 已知工作；如生产在 Linux，建议同时启用 Windows 回退到原生 asyncio。需要在实施计划中明确。
3. **`lock_device` 字段** 本期仅在 `DeviceProfile` 留 `locked: bool` 字段，不实现"已锁设备拒绝指令"逻辑。Phase 5 lock 业务由谁实现需在 Phase 5 spec 更新时定。
4. **AGV/堆垛机规划** 简化为点对点梯形速度/加速度轨迹，不做地图级规划（地图规划属 RCS-3 任务调度）。
5. **故障恢复脚本** `controller_fault` 状态由 `clear_fault` 清除，本期留接口不实现 HMI 入口。
6. **CI 集成** `verify_rcs1.sh` 是否纳入 nightly？建议：先 PR 阶段跑，nightly 第二迭代再纳入。
7. **多设备同构型隔离** 不同设备独立 controller 实例，但共用 `SimHAL`；HAL 内部按 `device_id` 隔离状态，避免串扰。

---

## 8. 验收单模板

`scripts/verify_rcs1.sh` 产出 JSON：

```json
{
  "ts": "2026-07-24T22:00:00+08:00",
  "spec": "rcs-1-motion-control v0.1",
  "results": {
    "fk_ik_roundtrip": { "pass": true, "max_err_m": 1e-7 },
    "trajectory_within_limits": { "pass": true, "max_vel_ratio": 0.92 },
    "controller_step_response": { "pass": true, "steady_state_err_rad": 0.003 },
    "loop_1khz_jitter": { "pass": true, "actual_hz": 998, "drift_pct": 0.2 },
    "e2e_move_j": { "pass": true, "final_err_rad": 0.005 },
    "e2e_move_l": { "pass": true, "final_err_m": 0.003 },
    "estop_link": { "pass": true, "latency_ms": 12 },
    "tracking_error_inject": { "pass": true, "halted_within_ms": 100 },
    "ws_10hz": { "pass": true, "frames_per_s": 10.1 },
    "idempotency": { "pass": true },
    "queue_backpressure": { "pass": true }
  },
  "summary": { "total": 11, "passed": 11, "failed": 0 }
}
```
