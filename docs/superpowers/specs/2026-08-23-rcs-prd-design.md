# RCS 机器人控制系统需求规格说明书（PRD）

> **项目**: Robot Logic RCS
> **日期**: 2026-08-23
> **状态**: 已批准
> **读者**: 内部研发团队
> **核心设备**: 双臂装卸机器人（场景锚点）
> **深度模块**: M2 订单拆解 / M3 设备调度 / M4 任务编排
> **后端基线**: `robot-logic/rcs` (FastAPI, 端口 8100)

## 1. 项目背景与目标

### 1.1 RCS 在智能仓储物流中的定位

RCS（Robot Control System）是**多源异构机器人集群调度中枢**，定位介于上层业务管理系统（WMS / MES / ERP）与底层设备执行单元（PLC / 单机控制器）之间。

```
┌──────────────────────────────────────────────────────────────────┐
│                   上层业务系统                                    │
│   WMS（仓储管理） / MES（制造执行） / ERP（企业资源）              │
└────────────────────┬─────────────────────────────────────────────┘
                     │  REST / MQTT（订单、库存、计划）
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│          RCS 机器人控制系统（本 PRD 范围）                          │
│  • 订单拆解 + 任务 DAG                                             │
│  • 多设备调度 + 路径规划                                          │
│  • 异常处理 + 安全联锁                                            │
│  • 监控与可观测                                                   │
└────────────────────┬─────────────────────────────────────────────┘
                     │  MQTT / HAL（命令、状态、遥测）
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│              底层设备执行单元                                      │
│  AGV / 立库 / 装卸机器人 / 输送带 / 四向穿梭车 / 电梯 / PLC        │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 核心价值主张

RCS 解决当前物流自动化中的四类核心问题：

| 问题 | 当前现状 | RCS 方案 |
|------|---------|----------|
| **设备异构** | 每类设备独立调度，互不联通 | HAL 抽象层 + 统一设备台账 |
| **协同调度** | 人工编排，效率低、错误率高 | DAG 任务图 + 自动拓扑排序 |
| **SLO 约束** | 无统一优先级 | deadline-driven + utility function |
| **可观测** | 各厂商监控分散 | 统一事件总线 + WebSocket 实时推送 |

### 1.3 与现有 `rcs` 模块的关系

**继承**（不修改现有能力）：
- `rcs/rcs/hal/base.py` `HardwareHAL` 抽象与 `HALState` 数据结构
- `rcs/rcs/state/command.py` `Command` / `CommandType` 枚举
- `rcs/rcs/controllers/` 5 类设备控制器（臂 / AGV / 堆垛机 / 叉车 / 双臂装卸）
- `rcs/rcs/service.py` REST 路由 + WebSocket 端点
- `rcs/rcs/mqtt/` MQTT 适配器

**新增**（在 `rcs/` 内扩展模块）：
- `rcs/scheduler/` 调度核心（EDF + 关键路径）
- `rcs/dispatcher/` 任务编排与冲突仲裁
- `rcs/dag/` 任务 DAG 表达与持久化
- `rcs/topology/` 站点地图与路径规划
- `rcs/observability/` 统一监控指标

**不修改**：
- 仿真后端（`simulation/`）
- 共享契约层（`shared/`）
- 边缘 APP（`robot-app/`）

### 1.4 业务场景与目标客户

| 场景 | 设备组合 | 核心 SLO |
|------|---------|----------|
| **A：集装箱拆装箱**（双臂装卸，**核心场景**） | 双臂装卸机器人 + AGV + 门机 | 每箱 ≤ 3 分钟，成功率 ≥ 99.5% |
| **B：仓储拣选** | AMR + 叉车 + 分拣输送带 | 每 SKU ≤ 30 秒，200 SKU/小时 |
| **C：月台装卸** | 装卸机器人 + 叉车 + 传送带 | 每车次 ≤ 15 分钟 |
| **D：跨楼层运输** | AGV + 电梯调度 + 堆垛机 | 端到端 ≤ 5 分钟 |

**目标客户**：大型物流园区 / 港口集装箱码头 / 智能仓储中心。

---

## 2. 功能需求

### 2.1 订单接收与拆解（M2 — 深度定义）

#### 2.1.1 订单来源与契约

RCS 接收三类订单：

| 订单类型 | 来源 | 协议 | 字段 |
|---------|------|------|------|
| 入库单 | WMS | REST POST `/api/rcs/orders/inbound` | `order_id`, `sku_list[]`, `target_location`, `priority`, `deadline` |
| 出库单 | WMS | REST POST `/api/rcs/orders/outbound` | `order_id`, `sku_list[]`, `source_location`, `priority`, `deadline` |
| 移库单 | WMS / MES | MQTT Topic `rcs/order/transfer` | 同上 |

**契约约束**：订单 schema 与 `shared/python/robot_contracts/` 的 Pydantic 模型保持双向校验；不匹配返回 HTTP 400 + 错误码 `invalid_order`。

#### 2.1.2 拆解规则

订单 → 任务 DAG 拆解算法：

```
订单（多 SKU）
   │
   ├─► 节点 1：AGV 取料（source_location → staging_area）
   ├─► 节点 2：装卸机器人抓取（staging_area → 装载位）
   ├─► 节点 3：AGV 搬运（装载位 → target_location）
   └─► 节点 4：装卸机器人放置（target_location）
```

**拆解规则**：
1. 每个 SKU 对应一条完整路径（取 → 抓 → 运 → 放）
2. 同一订单内多 SKU 可**并行**（不互斥资源时）
3. 同一装载位的 SKU 必须**串行**（互斥资源）
4. 拆解结果输出 DAG 节点集合 + 边依赖关系

#### 2.1.3 多 SKU 合并/拆分

- **合并**：相邻目的地的同类型 SKU 合并为单个 transport 任务
- **拆分**：超过 AGV 容量（典型 ≤ 1000 kg）的订单自动拆为多个子订单

### 2.2 设备调度与协同控制（M3 — 深度定义）

#### 2.2.1 调度策略

RCS 采用 **EDF（Earliest Deadline First）+ 关键路径加权** 调度：

```
utility(task) = w1 * (1 / time_to_deadline)
              + w2 * critical_path_priority
              + w3 * device_affinity_score
              - w4 * estimated_overrun_penalty
```

| 权重 | 默认值 | 含义 |
|------|-------|------|
| `w1` | 0.5 | 紧迫度 |
| `w2` | 0.3 | 关键路径加成 |
| `w3` | 0.15 | 设备亲和度 |
| `w4` | 0.05 | 超时惩罚 |

调度器每 100ms 重新计算所有 pending 任务，选取 utility 最高的可执行任务。

#### 2.2.2 多设备冲突仲裁

冲突类型与仲裁策略：

| 冲突类型 | 仲裁策略 |
|---------|----------|
| 共享路径 | 时间窗口预约（reservation table） |
| 互斥资源（同一货位） | 优先级 + 等待队列 |
| 设备争用 | utility function + 等待成本 |
| 电梯/门机占用 | FIFO + 紧急插队标识 |

#### 2.2.3 设备选择与分配

候选设备评分：

```
score(device, task) = speed_match * 0.4
                    + load_capacity_match * 0.3
                    + distance_to_task * 0.2
                    + current_utilization_penalty * 0.1
```

选择得分最高且状态为 IDLE 的设备。若所有候选 BUSY，则等待或降级分配（参考 2.6.3）。

### 2.3 任务编排与地图管理（M4 — 深度定义）

#### 2.3.1 DAG 任务图规范

DAG 节点结构：

```python
@dataclass
class TaskNode:
    task_id: str
    type: Literal["transport", "pick", "place", "wait", "sync"]
    device_id: str | None
    params: dict
    dependencies: list[str]  # 依赖的 task_id
    deadline: datetime | None
    slo_class: Literal["hard", "soft", "best-effort"]
```

边结构：`depends_on` 关系，调度器按拓扑序执行。

#### 2.3.2 站点地图（SiteMap）

统一坐标系：参考 `shared/contracts/pose.md`（`Pose6D` + `SiteTCPPose`）。

```
SiteMap = {
    nodes: dict[str, SiteNode],       # 货位、站台、充电桩
    edges: dict[str, list[SiteEdge]], # 拓扑路径
    zones: list[Zone],                # 功能区（拣选区、暂存区、装卸区）
    speed_limits: dict[str, float],   # 区域限速
}
```

#### 2.3.3 多设备协同时序

| 协同模式 | 规则 |
|---------|------|
| **等待**（wait） | 任务 A 完成后才解锁任务 B（依赖边） |
| **同步**（sync） | 多个设备在同一时刻执行（双臂协同抓取） |
| **超车** | 高优先级任务可中断低优先级路径（需释放资源） |

### 2.4 指令下发与执行（M5 — 适度收敛）

#### 2.4.1 MQTT Topic 树约定

对齐 `rcs/rcs/mqtt/` 已有命名空间：

```
rcs/cmd/{device_id}             # 命令下发（QoS 1）
rcs/state/{device_id}           # 设备状态（QoS 0，50Hz）
rcs/alert/{severity}            # 告警（QoS 1）
rcs/telemetry/{device_id}       # 遥测（QoS 0）
```

#### 2.4.2 命令队列与回压

- 控制器队列容量：`COMMAND_QUEUE_MAXSIZE = 1024`（对齐 `dispatch.py`）
- 队列满时返回 `queue_full` → HTTP 503 + `Retry-After: 1`
- ESTOP / RECOVER 命令**绕过队列**（对齐 `dispatch.py:55-56`）

#### 2.4.3 执行状态跟踪

```
CommandState = queued → dispatched → running → completed | failed | cancelled
                                       └──→ estopped
```

每条命令在 WebSocket 流中广播状态变更事件。

### 2.5 设备统一接入（M1 — 适度收敛）

#### 2.5.1 HAL 抽象接口

对齐 `rcs/rcs/hal/base.py` `HardwareHAL` 抽象基类：

| 方法 | 用途 |
|------|------|
| `connect()` | 建立硬件连接 |
| `disconnect()` | 断开连接 |
| `read_state(timeout_ms)` | 读取当前状态（含 joints / pose / wrench） |
| `send_command(joints/efforts/gripper)` | 下发控制指令 |

状态数据：`HALState` 统一包含 `joint_positions` / `cartesian_pose` / `wrench` / `timestamp`。

#### 2.5.2 设备台账注册

设备启动时调用 `POST /api/rcs/registry` 注册：

```json
{
  "device_id": "loader-01",
  "type": "dual_arm_loader",
  "hal_class": "SimHAL",
  "spec": { "payload_per_arm_kg": 30, ... },
  "home_pose": { "x": 0, "y": 0, "z": 0, ... }
}
```

#### 2.5.3 心跳与健康检测

- 设备每 1s 发送一次心跳（MQTT `rcs/state/{id}` 含 `timestamp`）
- 心跳丢失 > 5s 标记为 `UNREACHABLE`
- 心跳丢失 > 30s 触发降级分配（参考 2.6.3）

### 2.6 异常处理与安全（M6 — 适度收敛）

#### 2.6.1 急停联锁（ESTOP 链路）

- 任意设备 `estop()` 调用 → 触发全局 ESTOP 信号
- 所有在执行任务标记为 `cancelled`，已下发命令进入安全姿态
- 恢复需 `clear_estop` + 设备 `recover()`（对齐 `service.py:99-106`）

#### 2.6.2 故障分类

| 等级 | 类型 | 处理 |
|------|------|------|
| L1 | 传感器噪声 / 单次命令失败 | 自动重试（≤3 次） |
| L2 | 关节超限 / 通信超时 | 任务暂停 + 告警 + 人工介入 |
| L3 | 碰撞 / 安全围栏触发 | 立即 ESTOP + 锁定设备 |
| L4 | 硬件损坏 | 设备下线 + 调度器重路由 |

#### 2.6.3 SLO 降级链路

```
正常模式 ──(设备故障率 > 20%)──► 降级模式 ──(超时率 > 5%)──► 紧急模式
   │                              │                              │
   ▼                              ▼                              ▼
全功能调度                    跳过可选任务                  仅保留硬 SLO 任务
```

### 2.7 监控与可视化（M7 — 适度收敛）

#### 2.7.1 WebSocket 实时状态

复用 `rcs/rcs/service.py` 现有端点：
- `ws_overview`：全量状态流（来自 `_loop.stream`）
- `ws_device(device_id)`：单设备状态流

前端鉴权方案待与后端协商（query `api_key` vs Header）。

#### 2.7.2 告警规则

| 告警 | 触发条件 | 严重度 |
|------|---------|--------|
| 设备离线 | 心跳丢失 > 30s | L2 |
| 命令超时 | P95 延迟 > 1s | L2 |
| ESTOP 触发 | 任意设备急停 | L3 |
| SLO 违约 | 任务超 deadline | L1 |
| 队列饱和 | 队列使用率 > 80% | L1 |

---

## 3. 非功能需求

### 3.1 实时性

| 指标 | 目标 | 测量点 |
|------|------|--------|
| 调度器决策 P95 | ≤ 200ms | 任务提交到下发 |
| 命令下发 P95 | ≤ 100ms | REST 到 MQTT |
| 状态推流延迟 P95 | ≤ 50ms | 设备状态到 WebSocket |
| 急停响应 P95 | ≤ 30ms | ESTOP 触发到设备生效 |

### 3.2 可靠性

- **可用性**：≥ 99.9%（月度停机 ≤ 43 分钟）
- **任务成功率**：≥ 99.5%（端到端，排除硬件损坏）
- **数据持久化**：任务记录、告警保留 ≥ 90 天

### 3.3 可扩展性

- **设备类型**：新增设备类型仅需实现 `DeviceModel` + `Controller`（不修改核心调度）
- **并发规模**：单集群支持 ≥ 200 台设备、≥ 1000 个并发任务
- **水平扩展**：RCS 调度核心支持多实例部署（leader election）

### 3.4 多租户隔离

- **namespace**：每个租户独立 namespace（设备、任务、告警）
- **RBAC**：基于角色的访问控制（admin / operator / viewer）
- **资源配额**：单租户设备数上限、QPS 上限

---

## 4. 接口规范

### 4.1 HAL 层接口

对齐 `rcs/rcs/hal/base.py`：

```python
class HardwareHAL(ABC):
    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
    def read_state(self, timeout_ms: int = 1000) -> HALState: ...
    def send_command(self, joint_positions, joint_efforts, gripper_position): ...
```

### 4.2 MQTT 通信协议

| Topic | 方向 | QoS | 保留 |
|-------|------|-----|------|
| `rcs/cmd/{device_id}` | RCS → Device | 1 | 否 |
| `rcs/state/{device_id}` | Device → RCS | 0 | 否 |
| `rcs/alert/{severity}` | Device → RCS | 1 | 是 |
| `rcs/telemetry/{device_id}` | Device → RCS | 0 | 否 |
| `rcs/order/transfer` | WMS → RCS | 1 | 是 |

**遗嘱消息**（Last Will）：设备断连时发布 `online=false` 到 `rcs/state/{device_id}`。

### 4.3 外部系统接口

**WMS（仓储管理）**：
- REST：`/api/rcs/orders/{type}`（type ∈ {inbound, outbound, transfer}）
- 鉴权：`X-API-Key` Header（对齐 `require_api_key`）

**MES（制造执行）**：
- MQTT：`rcs/order/transfer` 订阅
- REST：`/api/rcs/tasks/{id}/report`（任务执行报告回传）

**ERP（企业资源）**：
- 只读 REST：`/api/rcs/kpi`（KPI 指标查询）

---

## 5. 性能指标（行业领先基准）

参考菜鸟（500+ AGV 集群调度）、京东物流（1.5 万 SKU/小时）的公开数据设定目标。

### 5.1 并发处理能力

| 指标 | 目标 | 参考 |
|------|------|------|
| 单集群设备并发 | ≥ 200 台 | 菜鸟单仓 AGV 规模 |
| 单集群任务并发 | ≥ 1000 个 | 行业大型仓库 |
| 单设备命令队列容量 | 1024 条 | 对齐 `COMMAND_QUEUE_MAXSIZE` |
| 调度 QPS | ≥ 500 req/s | 单实例基准 |
| WebSocket 并发连接 | ≥ 500 客户端 | 运营大屏 + 客户端 |

**队列容量说明**：单设备命令队列 1024 条 × 200 设备 = 20 万条命令峰值。实际稳态运行下，单设备命令队列深度 P95 ≤ 32 条（参考 `arm_controller.py` 队列行为），总内存占用约 200 × 32 × 256B ≈ 1.6 MB。

### 5.2 响应延迟

| 场景 | P50 | P95 | P99 |
|------|-----|-----|-----|
| 调度决策 | 50ms | 200ms | 500ms |
| 命令下发 | 30ms | 100ms | 300ms |
| 状态推流（50Hz） | 10ms | 30ms | 80ms |
| 急停响应 | 10ms | 30ms | 80ms |

### 5.3 任务成功率

| 任务类型 | 目标 |
|---------|------|
| 装卸任务 | ≥ 99.5% |
| 搬运任务 | ≥ 99.9% |
| 拣选任务 | ≥ 99.7% |
| 整体端到端 | ≥ 99.5% |

### 5.4 资源占用

| 角色 | CPU | 内存 | 网络 |
|------|-----|------|------|
| RCS 调度核心（单实例） | ≤ 2 核 | ≤ 4 GB | 100 Mbps |
| MQTT Broker | ≤ 1 核 | ≤ 2 GB | 1 Gbps |
| WebSocket 网关 | ≤ 1 核 | ≤ 2 GB | 1 Gbps |

---

## 6. 部署方案

### 6.1 Docker Compose 单机部署

参考 `rcs/Dockerfile` 已有镜像，新增前端与数据库服务。

```yaml
services:
  rcs-core:
    build: ./rcs
    ports: ["8100:8100"]
    environment:
      RCS_MQTT_ENABLED: "true"
      RCS_CORS_ORIGINS: "*"
  mqtt-broker:
    image: eclipse-mosquitto:2
    ports: ["1883:1883"]
  rcs-mysql:
    image: mysql:8
    environment:
      MYSQL_DATABASE: rcs
```

### 6.2 Kubernetes 部署

| 资源 | 配置 | 说明 |
|------|------|------|
| Namespace | `rcs-prod` | 生产环境隔离 |
| Deployment | `rcs-core` × 3 replicas | HPA 触发条件：CPU > 70% |
| ConfigMap | `rcs-config` | 调度参数、MQTT 地址 |
| Secret | `rcs-secret` | API Key、DB 密码 |
| Service | `ClusterIP` | 内部访问 |
| Ingress | `nginx` + TLS | 外部 WMS / ERP 接入 |

### 6.3 硬件要求

**边缘节点**（每个物流园区）：
- CPU：≥ 4 核 x86_64（Intel Xeon 或同级）
- 内存：≥ 8 GB
- 存储：≥ 256 GB SSD（任务历史 + 告警）
- 网络：≥ 1 Gbps，< 5ms 园区内延迟
- 操作系统：Ubuntu 22.04 LTS

**云端控制平面**（多园区汇聚）：
- CPU：≥ 8 核
- 内存：≥ 16 GB
- 数据库：MySQL 8 或 PostgreSQL 15

### 6.4 与 ROADMAP.md 的里程碑映射

| 里程碑 | 时间 | PRD 覆盖范围 |
|--------|------|-------------|
| M1 | 2026-11 | 2.4-2.7 + 6.1 部署骨架（场景 B MVP） |
| M2 | 2027-02 | 2.1-2.3 + 7.1-7.4（场景 A 装卸机器人） |
| M3 | 2027-08 | 3.4 多租户 + 6.2 K8s 部署 |

---

## 7. 装卸机器人端到端场景示例（重点章节）

### 7.1 场景定义

**集装箱拆装箱场景 A**：将集装箱内的货物卸到立体仓库。

| 元素 | 内容 |
|------|------|
| 输入 | 集装箱（内有 N 箱货物，已贴 SKU 标签） |
| 输出 | 立体仓库指定货位 |
| 设备 | 双臂装卸机器人（loader-01）+ AGV（agv-01）+ 立体仓库堆垛机 |
| 物理布局 | 集装箱 → 装卸工作台 → AGV → 仓库入口 |

### 7.2 任务流程（DAG）

```
订单 (container_id=CN-2026-001, sku_list=[A,B,C,D])
   │
   ├─► T1: agv-01 移动至装卸工作台（staging）
   ├─► T2: loader-01 双臂抓取 A + B（同步执行）
   ├─► T3: loader-01 放置 A + B 至工作台
   ├─► T4: agv-01 装载 A + B（等待 T3 完成）
   ├─► T5: agv-01 移动至仓库入口
   ├─► T6: stacker-01 入库 A + B 至指定货位
   ├─► T7: loader-01 抓取 C + D
   └─► T8: ...（循环 T3-T6）
```

### 7.3 状态机时序

```
T=0    订单接收 → 调度器分配 agv-01
T=2s   T1 执行完成（agv-01 至工作台）
T=3s   T2 启动（loader-01 双臂同步）
T=15s  T2 完成（双臂抓取 A+B）
T=17s  T3 完成（放置工作台）
T=18s  T4 完成（agv 装载）
T=20s  T5 启动（agv 移动）
T=80s  T5 完成（agv 至仓库入口）
T=85s  T6 完成（stacker 入库）
T=85s+ T7 启动（循环下一组 SKU）
```

### 7.4 异常处理剧本

| 异常 | 检测点 | 恢复动作 |
|------|--------|----------|
| 双臂抓取失败（夹爪空） | T2 完成事件 payload 含 `gripped=false` | 重试（≤3 次），失败则标记 SKU 异常，跳过 |
| AGV 路径冲突 | T5 路径规划失败 | 重新规划路径，若仍失败则降级分配（换 agv-02） |
| 货物超重（>30kg） | T2 抓取前力矩检测 | 切换至单臂抓取模式 |
| ESTOP 触发 | 全局信号 | 所有任务 `cancelled`，双臂回安全姿态，AGV 就近停车 |

---

## 附录 A. 术语表

| 术语 | 含义 |
|------|------|
| RCS | Robot Control System，机器人控制系统 |
| HAL | Hardware Abstraction Layer，硬件抽象层 |
| DAG | Directed Acyclic Graph，有向无环图（任务编排） |
| EDF | Earliest Deadline First，最早截止时间优先 |
| SLO | Service Level Objective，服务等级目标 |
| WMS | Warehouse Management System，仓储管理系统 |
| MES | Manufacturing Execution System，制造执行系统 |
| ERP | Enterprise Resource Planning，企业资源计划 |

## 附录 B. 引用文档矩阵

| 文档 | 用途 |
|------|------|
| `docs/algorithm/06-platform.md` | 平台架构、数据流、状态机定义 |
| `docs/technical/ROADMAP.md` | 12 月演进路线图 |
| `docs/research/SLO-SCHEDULING-RESEARCH.md` | 调度策略研究 |
| `docs/research/VLA-INTEGRATION-RESEARCH.md` | VLA 集成研究 |
| `rcs/rcs/hal/base.py` | HALState / HardwareHAL 定义 |
| `rcs/rcs/state/command.py` | Command / CommandType 定义 |
| `rcs/rcs/service.py` | REST/WebSocket 端点 |
| `rcs/rcs/dispatch.py` | 调度分发逻辑 |
| `rcs/rcs/events.py` | 事件总线 |
| `shared/contracts/pose.md` | 坐标系统一规范 |
| `shared/python/robot_contracts/` | Pydantic 共享模型 |

## 附录 C. Open Questions

| # | 问题 | 负责方 | 状态 |
|---|------|--------|------|
| 1 | WebSocket 鉴权方案（query api_key vs Header） | 后端 + 前端 | 待讨论 |
| 2 | 多租户 namespace 实现机制（DB schema 隔离 vs 字段隔离） | 后端 | M3 决策 |
| 3 | 调度器 leader election 实现（etcd vs Redis） | SRE | M3 决策 |
| 4 | 站点地图编辑器（独立工具 vs RCS 内嵌） | 产品 | M2 决策 |