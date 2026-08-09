# 机器人智能仓储物流系统原型 - 设计文档

> **创建日期**：2026-07-23  
> **文档类型**：技术方案设计  
> **版本**：v1.0

---

## 1. 项目概述

### 1.1 项目目标

基于现有算法文档（`docs/algorithm/`），构建可演示的Web原型系统，覆盖月台装卸、AGV转运、立体仓储、数字孪生4个核心场景，验证算法方案的可行性。

### 1.2 范围限定

| 包含 | 不包含 |
|------|--------|
| 核心算法原型实现 | 生产级硬件集成 |
| 4个场景的模拟演示 | 真实机械臂控制 |
| 前后端完整框架 | 真实WMS/TMS集成 |
| 单元/集成测试 | 部署运维脚本 |
| 文档与README | 性能压测 |

### 1.3 成功标准

1. **可演示性**：4个场景均能在浏览器中可视化运行
2. **算法可观察**：RRT*规划、任务调度过程可在前端观察
3. **数据真实感**：模拟数据接近真实业务场景
4. **代码可维护**：模块化设计，单文件不超过300行

---

## 2. 架构设计

### 2.1 总体架构（方案A：分层单体架构）

```
┌──────────────────────────────────────────────────┐
│  应用层 (Application Layer)                       │
│  前端 (Vue 3 + Three.js + Vite)                  │
│  ├── 数字孪生3D场景（Three.js）                   │
│  ├── 监控仪表盘（ECharts）                        │
│  └── 任务管理面板                                 │
└──────────────┬───────────────────────────────────┘
               │ WebSocket实时 / REST API
┌──────────────▼───────────────────────────────────┐
│  API网关层 (FastAPI)                              │
│  ├── REST 路由（设备/任务/仿真控制）              │
│  └── WebSocket 推送服务                          │
└──────────────┬───────────────────────────────────┘
┌──────────────▼───────────────────────────────────┐
│  业务服务层 (Service Layer)                       │
│  ├── 订单服务（OrderService）                     │
│  ├── 调度服务（DispatchService）                  │
│  ├── 库存服务（InventoryService）                 │
│  ├── 设备服务（DeviceService）                    │
│  └── 监控服务（MonitoringService）                │
└──────────────┬───────────────────────────────────┘
┌──────────────▼───────────────────────────────────┐
│  算法服务层 (Algorithm Layer)                     │
│  ├── 设备模拟器（机器人/AGV/堆垛机）              │
│  ├── 任务调度器（拓扑排序+优先级队列）            │
│  ├── 运动规划器（RRT*简化版）                     │
│  └── 感知模块（模拟检测+云端mock）                │
└──────────────┬───────────────────────────────────┘
┌──────────────▼───────────────────────────────────┐
│  数据层 (Data Layer)                              │
│  ├── SQLite（设备状态/任务/库存持久化）           │
│  └── 内存缓存（实时状态高频读写）                 │
└──────────────────────────────────────────────────┘
```

### 2.2 数据流

1. **用户操作** → 前端UI → REST API → API网关 → 业务服务层 → 算法服务层 → 数据层
2. **设备状态** → 算法服务层 → 业务服务层 → WebSocket → API网关 → 前端3D场景
3. **算法执行** → 算法服务层 → 业务服务层 → 状态更新 → WebSocket推送
4. **数据持久化** → 数据层（SQLite用于状态恢复，内存缓存用于高频读写）

---

## 3. 模块设计

### 3.1 API网关层 (`backend/api/`)

#### REST API 端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/devices` | GET | 获取所有设备状态 |
| `/api/devices/{id}` | GET | 获取指定设备状态 |
| `/api/tasks` | GET/POST | 获取/创建任务 |
| `/api/tasks/{id}` | GET/DELETE | 获取/取消任务 |
| `/api/orders` | GET/POST | 获取/创建订单 |
| `/api/inventory` | GET | 查询库存 |
| `/api/sim/start` | POST | 启动仿真 |
| `/api/sim/stop` | POST | 停止仿真 |
| `/api/sim/status` | GET | 获取仿真状态 |
| `/api/metrics` | GET | 获取监控指标 |
| `/api/logs` | GET | 查询日志（trace_id/task_id过滤） |
| `/api/logs/trace/{trace_id}` | GET | 获取调用链日志 |
| `/api/logs/task/{task_id}` | GET | 获取任务生命周期日志 |
| `/api/logs/stats` | GET | 日志统计信息 |
| `/ws/realtime` | WS | 实时状态推送 |
| `/ws/logs` | WS | 实时日志推送 |

#### Swagger/OpenAPI 文档

FastAPI 自动生成 OpenAPI 规范，提供以下文档端点：

| 端点 | 用途 |
|------|------|
| `/docs` | Swagger UI（交互式API文档） |
| `/redoc` | ReDoc（只读API文档，更美观） |
| `/openapi.json` | OpenAPI规范JSON（可导入Postman等工具） |

**Swagger配置要求：**

| 配置项 | 值 | 说明 |
|--------|-----|------|
| API标题 | 机器人智能仓储物流系统 API | 显示在Swagger顶部 |
| API版本 | 1.0.0 | 语义化版本号 |
| API描述 | 系统所有REST端点的中文说明 | Markdown格式 |
| 联系信息 | joezxh@qq.com | 团队邮箱 |
| 服务器URL | http://localhost:8000 | 开发环境 |

**Pydantic模型文档化：**

所有请求/响应模型必须包含：
- 字段类型注解
- 字段描述（中文）
- 字段示例值
- 必填/可选标记
- 验证约束（min/max/pattern）

**API标签分组：**

| 标签 | 端点 | 说明 |
|------|------|------|
| 设备管理 | `/api/devices*` | 设备CRUD接口 |
| 任务调度 | `/api/tasks*` | 任务管理接口 |
| 订单管理 | `/api/orders*` | 订单接口 |
| 库存管理 | `/api/inventory*` | 库存查询 |
| 仿真控制 | `/api/sim/*` | 仿真启停 |
| 监控指标 | `/api/metrics` | KPI查询 |
| WebSocket | `/ws/*` | 实时推送 |

**Swagger使用场景：**

1. **开发联调**：前后端通过Swagger对齐接口
2. **测试验证**：浏览器直接调用API测试
3. **文档生成**：自动生成API文档
4. **客户端SDK**：使用openapi-generator生成TypeScript SDK

### 3.2 业务服务层 (`backend/services/`)

| 类 | 职责 | 依赖 |
|------|------|------|
| `OrderService` | 订单创建、查询、状态管理 | InventoryService, DispatchService |
| `DispatchService` | 任务分解、依赖解析、调度 | TaskScheduler, DeviceService |
| `InventoryService` | 库存管理、货位分配 | SQLite |
| `DeviceService` | 设备统一管理、状态聚合 | DeviceManager |
| `MonitoringService` | 实时指标统计、KPI计算 | Redis/Cache |

### 3.3 算法服务层 (`backend/algorithm/`)

#### 设备模拟器 (`backend/algorithm/simulator/`)

| 类 | 职责 |
|------|------|
| `DeviceBase` | 设备基类（位置、状态、回调） |
| `RobotSimulator` | 模拟工业机器人运动状态 |
| `AGVSimulator` | 模拟AGV小车移动和路径跟踪 |
| `StackerSimulator` | 模拟堆垛机升降和移动 |
| `DeviceManager` | 统一管理所有设备实例 |

#### 任务调度器 (`backend/algorithm/scheduler/`)

**完全参考 `docs/algorithm/04-task-scheduling.md` 实现**，采用 Kahn拓扑排序+优先级队列。

| 类 | 职责 |
|------|------|
| `Task` | 任务数据结构（task_id/type/source_pose/target_pose/priority/dependencies） |
| `TaskPriority` | 优先级枚举（CRITICAL=1/HIGH=2/NORMAL=3/LOW=4） |
| `ExecutionStatus` | 执行状态（pending/running/completed/failed） |
| `TaskScheduler` | **Kahn拓扑排序+heapq优先级队列** |
| `DecisionEngine` | 决策引擎（置信度→路径选择） |

##### 任务调度关键算法

**1. 任务建模**

```python
Task {
    task_id: str                # 唯一标识
    task_type: str              # pick / place / move
    source_pose: Pose6D         # 起始位姿
    target_pose: Pose6D         # 目标位姿
    object_class: str           # 物体类别
    priority: TaskPriority      # CRITICAL/HIGH/NORMAL/LOW
    dependencies: List[str]     # 前置任务ID列表
    estimated_duration: float   # 预估时长
    created_time: float         # 创建时间
}
```

**2. 调度算法：Kahn拓扑排序 + 优先级队列**

| 步骤 | 操作 | 目的 |
|------|------|------|
| 1. 依赖解析 | 构建DAG | 确定执行顺序约束 |
| 2. 拓扑排序 | Kahn算法（BFS） | 消除依赖获得执行序列 |
| 3. 优先级排序 | `(priority.value, created_time)` | 同层任务优先级 |
| 4. 批次调度 | 按`max_concurrent`分配 | 资源高效利用 |

**3. 优先级队列实现**

Python `heapq` 最小堆 + Task `__lt__` 方法：
- CRITICAL (value=1) 优先于 LOW (value=4)
- 同优先级按创建时间排序（FIFO）

**4. 决策引擎（DecisionEngine）**

基于置信度的感知决策：
```
检测结果 → 置信度判断
├─ ≥0.8 闭集 → 本地快速规划（CRITICAL优先级）
├─ 开集/低置信度 → 云端深度感知（HIGH优先级）
├─ 云端不可用 → 本地降级（HIGH优先级）
├─ 多目标冲突 → 优先级排序（NORMAL）
└─ 执行失败 → 重试/跳过（LOW）
```

**5. 任务生命周期状态机**

```
pending → running → completed (成功)
   ↓         ↓
   └─────→ failed (失败，可重试)
```

#### 运动规划器 (`backend/algorithm/planner/`)

**核心升级：从2D简化版升级为完整6D规划**，参考 `docs/algorithm/` 下完整规范。

| 类 | 职责 |
|------|------|
| `Pose6D` | 末端6自由度位姿（3D位置+四元数姿态） |
| `JointState` | 关节状态（位置/速度/加速度/力矩） |
| `KinematicsBase` | 运动学基类（FK/IK/Jacobian接口） |
| `AnalyticKinematics` | 解析运动学实现（DH参数+逆解） |
| `RRTStarPlanner` | **6D位姿空间RRT*** 全局规划 |
| `TrajectoryOptimizer` | **6D轨迹优化**（梯度下降+随机） |
| `TrajectoryInterpolator` | **S曲线/线性插补**（125Hz/250Hz） |
| `Trajectory` | 关节空间轨迹数据结构 |
| `PathOptimizer` | 简单梯度下降优化 |

##### 6D规划完整架构

```
┌─────────────────────────────────────────────────────────┐
│                运动规划器 (MotionPlanner)                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │   共用基础层 (foundation.py)                     │    │
│  │   - Pose6D (3D位置+四元数)                       │    │
│  │   - JointState (位置/速度/加速度/力矩)         │    │
│  │   - RobotConfig + JointLimits                   │    │
│  │   - Trajectory + TrajectoryPoint                │    │
│  │   - CollisionWorld (碰撞检测)                    │    │
│  └─────────────────────────────────────────────────┘    │
│           ↓                                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │   运动学层 (kinematics.py)                      │    │
│  │   - Forward Kinematics (FK)                     │    │
│  │   - Inverse Kinematics (IK)                     │    │
│  │   - Jacobian Matrix                             │    │
│  │   - DH参数支持                                  │    │
│  └─────────────────────────────────────────────────┘    │
│           ↓                                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │   全局规划层 (global_planner.py)                │    │
│  │   - 6D位姿空间RRT*采样                          │    │
│  │   - Steer扩展 + 重连线 + 重布线                 │    │
│  │   - 渐进最优                                    │    │
│  └─────────────────────────────────────────────────┘    │
│           ↓                                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │   局部优化层 (local_optimizer.py)               │    │
│  │   - 梯度下降（高精度）                          │    │
│  │   - 随机优化（高速）                            │    │
│  │   - 平滑度+碰撞+限位 代价函数                   │    │
│  └─────────────────────────────────────────────────┘    │
│           ↓                                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │   轨迹插补层 (interpolator.py)                  │    │
│  │   - S曲线时间参数化                              │    │
│  │   - 弧长参数化插值                               │    │
│  │   - 125Hz/250Hz控制频率                         │    │
│  │   - JointState序列输出                           │    │
│  └─────────────────────────────────────────────────┘    │
│           ↓                                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │   控制器接口 (controller.py)                    │    │
│  │   - EtherCAT/Mock接口                           │    │
│  │   - 紧急停止                                    │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

##### 6D规划关键技术点

**1. 6D位姿表示**
```python
Pose6D:
    position: ndarray[3]      # [x, y, z] 米
    orientation: ndarray[4]   # 四元数 [w, x, y, z]
    
方法:
    from_matrix(4x4齐次矩阵)
    to_matrix() → 4x4齐次矩阵
    distance_to(other_pose) → 6D度量距离
```

**2. 运动学（FK/IK/Jacobian）**
- **Forward Kinematics (FK)**: 关节角度 → 末端6D位姿
- **Inverse Kinematics (IK)**: 末端6D位姿 → 关节角度（多解）
- **Jacobian**: 关节速度 ↔ 末端线速度/角速度
- **DH参数**: 标准Denavit-Hartenberg建模

**3. 6D RRT* 全局规划**
- 在**6D位姿空间**采样（而非关节空间）
- 通过IK将6D位姿转为关节配置
- 碰撞检测调用FK + 几何检查
- 支持 start_pose → goal_pose 的规划

**4. 6D轨迹优化**
- 同时优化**位置**（x,y,z）和**姿态**（四元数）
- 平滑度代价：加速度范数平方积分
- 碰撞代价：FK后几何碰撞检测
- 限位代价：关节角度边界约束

**5. 轨迹插补**
- S曲线（高精度）：加减速平滑，125Hz
- 线性插补（高速）：恒定速度，250Hz
- 输出 JointState 序列（含位置/速度/加速度/时间戳）

##### 运动规划完整文件清单

| 文件 | 职责 |
|------|------|
| `foundation.py` | JointState/Pose6D/RobotConfig/JointLimits/Trajectory/CollisionWorld |
| `kinematics.py` | FK/IK/Jacobian/DH参数 |
| `global_planner.py` | 6D RRT* 采样规划 |
| `local_optimizer.py` | 6D 轨迹优化（梯度+随机） |
| `interpolator.py` | S曲线/线性插补 |
| `controller.py` | EtherCAT/Mock 控制器接口 |
| `motion_planner.py` | 完整流水线集成 |

##### 规划API端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/planner/plan` | POST | 6D位姿规划（start_pose, goal_pose） |
| `/api/planner/optimize` | POST | 轨迹优化 |
| `/api/planner/interpolate` | POST | 轨迹插补 |
| `/api/planner/kinematics/fk` | POST | 正运动学（关节→位姿） |
| `/api/planner/kinematics/ik` | POST | 逆运动学（位姿→关节） |
| `/api/planner/config` | GET/PUT | 规划配置查询/修改 |

##### 参考实现

**所有算法实现严格参考 `docs/algorithm/` 下5个文档**，逐一对应：

| 参考文档 | 算法模块 | 实现内容 |
|---------|---------|---------|
| `01-overview.md` | 整体架构 | RobotConfig/PlanningConfig 参数化配置 |
| `01-overview.md` §1.4 | 配置派生 | `PlanningConfig.from_robot_config()` |
| `01-overview.md` §1.5 | 云边协同 | 边缘检测+云端深度感知架构 |
| `01-overview.md` §1.6 | 规划流程 | MotionPlanner流水线集成 |
| `02-motion-planning.md` §2.1 | 共用基础层 | JointState/Pose6D/Limits/Trajectory/CollisionWorld |
| `02-motion-planning.md` §2.2 | 全局规划 | 6D RRT* + Steer + 重布线 |
| `02-motion-planning.md` §2.3 | 局部优化 | 6D TrajectoryOptimizer（梯度/随机） |
| `02-motion-planning.md` §2.4 | 轨迹插补 | S曲线/线性 + 125Hz/250Hz |
| `02-motion-planning.md` §2.5 | 运动规划器 | 完整MotionPlanner集成 |
| `03-perception.md` §3.1 | 视觉预处理 | RGBDPreprocessor + PointCloudProcessor |
| `03-perception.md` §3.2 | 目标检测 | UnifiedDetector（YOLOv8+YOLO-World） |
| `03-perception.md` §3.3 | 云端感知 | PerceptionCoordinator + GraspNet/CosyPose mock |
| `04-task-scheduling.md` §3.4 | 任务调度 | TaskScheduler（Kahn+heapq） |
| `04-task-scheduling.md` §3.5 | 决策引擎 | DecisionEngine（置信度决策） |
| `05-deployment.md` §4.1 | 配置模板 | robot_config.yaml 加载 |
| `05-deployment.md` §4.2 | 性能指标 | 延迟预算 <3s 端到端 |
| `05-deployment.md` §4.3 | 部署架构 | 边缘GPU+云端A100 |
| `05-deployment.md` §4.4 | 网络延迟 | 560ms本地 / 700ms云端 |
| `05-deployment.md` §4.5 | 可靠性 | 三级降级模式 |

##### 参数化配置派生

```python
PlanningConfig.from_robot_config(robot_config):
    # 高精度场景
    if robot_config.position_accuracy_mm < 1.0:
        max_iterations=10000, step_size=0.05, rewire_radius=0.3,
        smoothness_weight=0.6, collision_weight=2.0, mode="s_curve"
    
    # 高速场景
    elif robot_config.max_velocity_mps > 2.0:
        max_iterations=5000, step_size=0.1, rewire_radius=0.5,
        smoothness_weight=0.3, collision_weight=1.0, mode="linear"
    
    # 默认场景
    else:
        max_iterations=7000, step_size=0.08, rewire_radius=0.4,
        smoothness_weight=0.5, collision_weight=1.5, mode="s_curve"
```

#### 感知模块 (`backend/algorithm/perception/`)

**完全参考 `docs/algorithm/03-perception.md` 实现**，包括视觉预处理、目标检测、云端深度感知。

| 类 | 职责 |
|------|------|
| `RGBDFrame` | RGB-D图像帧（rgb/depth/intrinsic/extrinsic/timestamp） |
| `PointCloud` | 点云数据（points/colors/timestamp） |
| `PreprocessingConfig` | 预处理配置（深度缩放/双边滤波/体素） |
| `RGBDPreprocessor` | 深度图处理（缩放+无效过滤+双边滤波） |
| `PointCloudProcessor` | 点云生成+降采样+离群点移除 |
| `BoundingBox` | 检测框（含IoU计算） |
| `DetectedObject` | 检测目标（含source字段） |
| `DetectionConfig` | 检测配置（模型路径/置信度阈值） |
| `UnifiedDetector` | **混合检测器（YOLOv8+YOLO-World）** |
| `Object6DPose` | 物体6D位姿（rotation/translation/confidence） |
| `GraspPoint` | 抓取点（position/approach/gripper_width/score） |
| `GraspPose` | 完整抓取姿态（pre/grasp/post三阶段） |
| `CloudServiceClient` | 云端HTTP客户端（pose_estimation/grasp_planning） |
| `LocalGraspPlanner` | 本地降级（顶面检测+几何抓取） |
| `PerceptionCoordinator` | 感知协调器（按置信度动态选择路径） |

##### 感知模块关键算法

**1. 视觉预处理（`preprocessing.py`）**

完全按规范实现：
- 深度缩放：`depth / 1000.0` → 米
- 无效值过滤：阈值 + NaN处理
- 双边滤波：`scipy.ndimage.bilateral_filter`
- 点云生成：针孔相机模型反投影
- 体素降采样：`floor(coord / leaf_size)` + `unique` + mean
- 离群点移除：KDTree + 统计阈值

**2. 目标检测（`detector.py`）**

闭集+开集混合检测：
```
闭集检测（YOLOv8m） → 加权×1.2 → 提高置信度
开集检测（YOLO-World） → IoU<0.5填补空白 → 扩展覆盖
NMS去重（IoU>0.45抑制） → 最终输出
```

**3. 云端深度感知（`pose_estimator.py`）**

```
检测结果 → 按置信度决策
├─ ≥0.8 闭集 → 本地LocalGraspPlanner（快速响应）
├─ <0.8/开集 → 云端CosyPose（精确6-DoF）→ GraspNet（多候选抓取）
└─ 云端故障 → 本地降级（顶面中心+尺寸估计）
```

抓取三阶段：
```
Pre-grasp (高度+15cm) → Grasp (下降执行) → Post-grasp (高度+30cm)
```

### 3.4 数据层 (`backend/data/`)

| 组件 | 用途 |
|------|------|
| `db.py` | SQLite数据库连接管理 |
| `models.py` | SQLAlchemy ORM模型 |
| `cache.py` | 内存缓存（设备实时状态） |
| `repositories/` | 仓储模式封装数据访问 |

### 3.5 Trace日志模块 (`backend/logging/`)

#### 设计目标

完整的trace日志系统，记录**每个任务动作**和**算法执行的完整过程**，支持问题排查和系统分析。

#### 核心组件

| 组件 | 职责 |
|------|------|
| `trace_logger.py` | Trace ID生成与上下文管理 |
| `task_logger.py` | 任务全生命周期日志记录 |
| `algorithm_logger.py` | 算法执行过程详细日志 |
| `log_formatter.py` | 自定义日志格式（JSON+可读） |
| `log_query.py` | 日志查询API（按trace_id/任务ID） |

#### Trace ID 机制

每个请求/任务分配唯一 trace_id，贯穿整个调用链：

```
HTTP请求 → API网关 → 业务服务 → 算法服务 → 数据层
   │           │          │          │         │
trace_id    trace_id   trace_id   trace_id  trace_id
(同一ID全程传递)
```

**Trace ID生成规则：**
- 格式：`{timestamp}-{uuid4前8位}`，例：`20260723-1430-a1b2c3d4`
- HTTP请求：从 `X-Trace-ID` header 读取，无则自动生成
- 任务调度：每个 Task 创建时生成新 trace_id
- 算法执行：复用上游 trace_id

#### 日志层级

| 层级 | 内容 | 示例 |
|------|------|------|
| **TRACE** | 算法内部循环迭代 | RRT* 第152次采样 |
| **DEBUG** | 关键步骤详情 | 检测到3个目标，置信度0.87 |
| **INFO** | 业务事件 | 任务task_001创建，优先级HIGH |
| **WARNING** | 异常但可恢复 | 设备device_03响应超时，使用备用 |
| **ERROR** | 失败事件 | RRT*规划1000次未找到路径 |
| **CRITICAL** | 系统级故障 | 数据库连接断开 |

#### 任务生命周期日志

每个Task记录完整的生命周期事件：

```python
# 任务执行示例日志流
[task_001] INFO  2026-07-23 14:30:01 trace=20260723-1430-a1b2c3d4  任务创建 type=PICK priority=HIGH
[task_001] INFO  2026-07-23 14:30:01  依赖检查 依赖任务[task_000]=completed ✓
[task_001] INFO  2026-07-23 14:30:02  调度器选择设备 device_robot_01
[task_001] DEBUG 2026-07-23 14:30:02  调用检测器 UnifiedDetector
[task_001] DEBUG 2026-07-23 14:30:03  检测结果 targets=3 confidence=[0.87,0.76,0.92]
[task_001] DEBUG 2026-07-23 14:30:03  调用规划器 RRTStarPlanner start→goal
[task_001] TRACE 2026-07-23 14:30:04  RRT* iter=1 sample=[0.12,1.45,0.78]
[task_001] TRACE 2026-07-23 14:30:04  RRT* iter=2 sample=[0.34,1.23,0.56]
...
[task_001] DEBUG 2026-07-23 14:30:05  RRT* found path nodes=87 length=12.4
[task_001] DEBUG 2026-07-23 14:30:05  调用优化器 TrajectoryOptimizer
[task_001] DEBUG 2026-07-23 14:30:06  优化完成 iterations=100 smoothness=0.23
[task_001] INFO  2026-07-23 14:30:06  下发轨迹 joints=6 points=125 duration=2.5s
[task_001] INFO  2026-07-23 14:30:08  执行完成 status=SUCCESS duration=7.2s
```

#### 算法执行日志

每个算法模块记录关键执行步骤：

| 算法 | 记录内容 |
|------|---------|
| **RRT*** | 迭代次数、采样点、节点数、路径长度 |
| **任务调度** | 队列长度、就绪任务、调度决策、并发数 |
| **设备模拟** | 位置更新、状态转换、故障事件 |
| **目标检测** | 输入尺寸、推理时间、检测数、置信度 |
| **位姿估计** | 输入点云大小、估计时间、误差 |

#### 日志存储

| 存储 | 格式 | 用途 |
|------|------|------|
| **控制台** | 彩色文本 | 实时观察 |
| **文件** | JSON Lines | 持久化、可解析 |
| **SQLite** | 关系表 | 结构化查询（按trace_id/时间） |
| **WebSocket** | 实时推送 | 前端日志面板 |

**日志表结构：**

```sql
CREATE TABLE trace_logs (
    id INTEGER PRIMARY KEY,
    trace_id TEXT NOT NULL,
    task_id TEXT,
    device_id TEXT,
    level TEXT NOT NULL,        -- TRACE/DEBUG/INFO/WARNING/ERROR/CRITICAL
    module TEXT NOT NULL,       -- 模块名
    message TEXT NOT NULL,      -- 日志消息
    context JSON,               -- 附加上下文（JSON）
    timestamp REAL NOT NULL,    -- Unix时间戳
    duration_ms REAL            -- 耗时（如适用）
);

CREATE INDEX idx_trace_id ON trace_logs(trace_id);
CREATE INDEX idx_task_id ON trace_logs(task_id);
CREATE INDEX idx_timestamp ON trace_logs(timestamp);
```

#### 日志查询API

| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/logs` | GET | 查询日志（支持trace_id/task_id/时间范围过滤） |
| `/api/logs/trace/{trace_id}` | GET | 获取完整调用链日志 |
| `/api/logs/task/{task_id}` | GET | 获取任务生命周期日志 |
| `/api/logs/stats` | GET | 日志统计（数量、级别分布） |

#### 前端日志面板

新增 `frontend/src/panel/LogViewer.vue`：
- 实时日志流（WebSocket订阅）
- 按trace_id过滤
- 按日志级别过滤
- 时间范围筛选
- 日志详情展开

#### 性能考虑

| 措施 | 说明 |
|------|------|
| **异步写入** | 日志写入不阻塞业务流程 |
| **批量刷盘** | 累积100条或1秒批量写文件 |
| **采样日志** | TRACE级日志每10次采样1次 |
| **日志轮转** | 单文件超100MB自动轮转 |
| **保留策略** | 7天自动清理，重要日志永久保存 |

### 3.2 前端模块

#### 3D场景 (`frontend/src/three/`)

| 组件 | 职责 |
|------|------|
| `SceneManager` | Three.js场景管理 |
| `RobotModel` | 机器人3D模型 |
| `AGVModel` | AGV 3D模型 |
| `StackerModel` | 堆垛机3D模型 |
| `WarehouseLayout` | 仓库布局渲染 |

#### 仪表盘 (`frontend/src/dashboard/`)

| 组件 | 职责 |
|------|------|
| `DeviceStatusPanel` | 设备状态卡片 |
| `TaskQueueChart` | 任务队列图表 |
| `ThroughputChart` | 吞吐量统计 |
| `KPIPanel` | 关键指标展示 |

#### 任务面板 (`frontend/src/panel/`)

| 组件 | 职责 |
|------|------|
| `TaskCreateForm` | 创建任务表单 |
| `TaskList` | 任务列表展示 |
| `DeviceControl` | 设备控制按钮 |

---

## 4. 4个演示场景

### 4.1 月台装卸场景

**数据流**：车辆到达 → 机器人识别 → 抓取 → 码垛

**关键元素**：
- 集装箱模型
- 门架式机器人
- 托盘运动
- 视觉检测框

**演示动作**：
1. 模拟车辆到达月台
2. 机器人视觉识别货物位置
3. 规划抓取轨迹
4. 执行抓取并放置到托盘

### 4.2 AGV转运场景

**数据流**：任务下发 → 路径规划 → 避障 → 到达

**关键元素**：
- AGV小车模型
- 动态路径线
- 交通管制区
- 货架目标点

**演示动作**：
1. 用户创建转运任务
2. AGV调度器规划路径
3. AGV沿路径移动并避开其他AGV
4. 到达目标并完成任务

### 4.3 立体仓储场景

**数据流**：入库指令 → 堆垛机移动 → 存取

**关键元素**：
- 立体货架模型
- 堆垛机轨道
- 货位网格
- 托盘位置

**演示动作**：
1. 选择入库货位
2. 堆垛机移动到目标位置
3. 托盘存入或取出

### 4.4 数字孪生场景

**数据流**：物理设备状态 → 实时映射 → 3D同步

**关键元素**：
- 全场景3D渲染
- 实时数据流显示
- 设备状态悬浮提示
- 时间轴回放

**演示动作**：
1. 所有设备状态实时同步到3D场景
2. 点击设备查看详细数据
3. 可暂停/继续/加速仿真

---

## 5. 错误处理

### 5.1 故障处理表

| 故障类型 | 检测方法 | 处理策略 |
|---------|---------|---------|
| 算法规划超时 | 计时器监控 | 跳过任务，标记重试 |
| 设备故障模拟 | 随机故障注入（5%） | 触发备用设备 |
| WebSocket断连 | 心跳超时 | 自动重连+状态恢复 |
| 前端加载失败 | 资源监控 | 显示降级提示 |
| 任务依赖死锁 | DAG环检测 | 移除冲突依赖 |

### 5.2 降级模式

```
┌─────────────────────────────────────────────┐
│           正常模式                          │
│  全功能运行 + 实时推送                      │
└─────────────────────────────────────────────┘
                    ↓ 检测到故障
┌─────────────────────────────────────────────┐
│           降级模式                          │
│  - 暂停非关键任务                           │
│  - 保留基本查看功能                         │
│  - 显示故障提示                             │
└─────────────────────────────────────────────┘
                    ↓ 严重故障
┌─────────────────────────────────────────────┐
│           安全模式                          │
│  - 所有设备紧急停止                         │
│  - 仅显示静态状态                           │
│  - 等待人工恢复                             │
└─────────────────────────────────────────────┘
```

---

## 6. 测试策略

### 6.1 测试分层

| 层级 | 范围 | 工具 | 覆盖率目标 |
|------|------|------|-----------|
| 单元测试 | 算法函数、数据结构 | pytest | 80% |
| API测试 | REST接口、错误码 | httpx | 100% |
| 集成测试 | 任务执行完整流程 | pytest-asyncio | 关键路径 |
| 前端组件 | Vue组件、Three.js | vitest | 60% |

### 6.2 测试用例示例

- `test_rrt_star_finds_path`：验证RRT*能找到无碰撞路径
- `test_scheduler_priority`：验证高优先级任务先执行
- `test_device_simulator_movement`：验证设备按规划移动
- `test_api_create_task`：验证创建任务API
- `test_websocket_realtime`：验证WebSocket推送频率

---

## 7. 项目结构

```
robot-logic/
├── backend/
│   ├── api/                        # API网关层
│   │   ├── __init__.py
│   │   ├── routes.py               # REST路由
│   │   ├── websocket.py            # WebSocket推送
│   │   ├── dependencies.py         # 依赖注入
│   │   └── openapi.py              # Swagger/OpenAPI配置
│   ├── services/                   # 业务服务层
│   │   ├── __init__.py
│   │   ├── order_service.py
│   │   ├── dispatch_service.py
│   │   ├── inventory_service.py
│   │   ├── device_service.py
│   │   └── monitoring_service.py
│   ├── algorithm/                  # 算法服务层
│   │   ├── simulator/
│   │   │   ├── __init__.py
│   │   │   ├── device_base.py
│   │   │   ├── robot.py
│   │   │   ├── agv.py
│   │   │   ├── stacker.py
│   │   │   └── device_manager.py
│   │   ├── scheduler/
│   │   │   ├── __init__.py
│   │   │   ├── task.py
│   │   │   └── scheduler.py
│   │   ├── planner/
│   │   │   ├── __init__.py
│   │   │   ├── rrt_star.py
│   │   │   └── trajectory.py
│   │   └── perception/
│   │       ├── __init__.py
│   │       ├── detector.py
│   │       └── pose.py
│   ├── data/                       # 数据层
│   │   ├── __init__.py
│   │   ├── db.py                   # SQLite连接
│   │   ├── models.py               # ORM模型
│   │   ├── cache.py                # 内存缓存
│   │   └── repositories/
│   ├── logging/                    # Trace日志模块
│   │   ├── __init__.py
│   │   ├── trace_logger.py         # Trace ID管理
│   │   ├── task_logger.py          # 任务生命周期日志
│   │   ├── algorithm_logger.py     # 算法执行日志
│   │   ├── log_formatter.py        # 日志格式化
│   │   └── log_query.py            # 日志查询接口
│   ├── tests/
│   │   ├── test_rrt_star.py
│   │   ├── test_scheduler.py
│   │   ├── test_simulator.py
│   │   ├── test_services.py
│   │   ├── test_logging.py
│   │   └── test_api.py
│   ├── main.py                     # FastAPI入口
│   ├── config.py                   # 配置加载
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── three/
│   │   │   ├── scene.ts
│   │   │   ├── models.ts
│   │   │   └── warehouse.ts
│   │   ├── dashboard/
│   │   │   ├── DeviceStatus.vue
│   │   │   ├── TaskQueue.vue
│   │   │   └── Throughput.vue
│   │   ├── panel/
│   │   │   ├── TaskCreate.vue
│   │   │   ├── DeviceControl.vue
│   │   │   └── LogViewer.vue       # 日志查看面板
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── App.vue
│   │   └── main.ts
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docs/
│   ├── algorithm/                  # 已有算法文档
│   └── superpowers/
│       ├── specs/                  # 设计文档
│       └── plans/                  # 实施计划
├── data/
│   └── prototype.db                # SQLite数据库
├── README.md
└── .gitignore
```

### 7.1 层次依赖关系

```
前端 (Vue 3)
    │
    ▼ HTTP/WS
API网关层 (FastAPI)
    │
    ▼ 服务调用
业务服务层 (Services)
    │
    ▼ 算法调用
算法服务层 (Algorithms)
    │
    ▼ 数据访问
数据层 (SQLite + Cache)
```

依赖原则：**上层可以调用下层，下层不能调用上层**

---

## 8. 依赖清单

### 8.1 后端依赖

```
fastapi==0.104.0
uvicorn[standard]==0.24.0
numpy==1.26.0
scipy==1.11.0
pydantic==2.4.0
sqlalchemy==2.0.23
aiosqlite==0.19.0
websockets==12.0
python-multipart==0.0.6
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.25.0

# Swagger/OpenAPI增强（可选）
swagger-ui-bundle==0.0.9

# Trace日志（Python标准库足够，loguru为可选增强）
loguru==0.7.0  # 可选：更强大的日志库
```

**FastAPI内置Swagger特性：**
- 自动生成 OpenAPI 3.0 规范
- 内置 Swagger UI（无需额外依赖）
- 内置 ReDoc（无需额外依赖）
- 支持自定义 OpenAPI schema
- 支持 API tag 分组
- 支持 Pydantic model 自动文档化

**Trace日志特性：**
- 基于 Python 标准库 `logging` 模块（无需额外依赖即可工作）
- `loguru` 作为可选增强（更简洁的API、自动轮转）
- SQLite 存储结构化日志（与主库共享）
- WebSocket 实时推送日志到前端

### 8.2 前端依赖

```json
{
  "vue": "^3.4.0",
  "three": "^0.158.0",
  "echarts": "^5.4.0",
  "vue-echarts": "^6.5.0",
  "axios": "^1.6.0",
  "vite": "^5.0.0",
  "@vitejs/plugin-vue": "^4.4.0",
  "typescript": "^5.2.0"
}
```

---

## 9. 开发里程碑

| 阶段 | 时长 | 交付物 |
|------|------|--------|
| M1: 项目骨架 | 3天 | 后端目录结构 + 前端Vite项目 |
| M2: 数据层 | 3天 | SQLite + ORM模型 + 仓储模式 |
| M3: 算法层 | 1周 | 设备模拟器 + RRT* + 任务调度 |
| M4: 业务层 | 1周 | 5个服务 + 业务编排 |
| M5: API层 | 3天 | REST路由 + WebSocket |
| M6: 前端框架 | 1周 | Vue3 + Three.js + ECharts |
| M7: 场景集成 | 1周 | 4个场景可视化 |
| M8: 测试与文档 | 3天 | 单元测试 + README |

---

## 10. 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| Three.js性能问题 | 3D卡顿 | 降低模型精度、限制渲染频率 |
| WebSocket不稳定 | 实时数据丢失 | 心跳重连 + 状态快照恢复 |
| 算法执行慢 | 仿真卡顿 | 简化算法（2D RRT*） + 异步执行 |
| 前端依赖冲突 | 构建失败 | 锁定依赖版本 + 容器化构建 |

---

**下一步**：等待用户确认设计文档后，进入实现计划阶段（writing-plans skill）。