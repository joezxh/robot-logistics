# 综合物流园区机器人调度 SLO 弹性调度算法调研报告

**项目**: robot-logic 物流机器人控制系统  
**日期**: 2026-08-23  
**版本**: v1.0  
**状态**: 调研报告（供技术选型参考）

---

## 摘要

本报告针对综合物流园区机器人调度场景，深入调研 SLO（Service Level Objective）弹性调度算法的理论基础、行业实践与工程实现。报告覆盖核心算法原理（EDF、弹性调度、utility function）、主流调度框架对比（Borg/Kubernetes/AGV 调度）、推荐算法选型（含伪代码与数据结构）、关键工程挑战与解法、与 robot-logic 现有架构的整合接口，以及参考论文清单与 POC 建议。报告字数约 7500 字，旨在为 robot-logic 项目提供可落地的 SLO 弹性调度技术方案。

---

## 目录

1. [核心概念与数学模型](#1-核心概念与数学模型)
2. [主流算法分类对比表](#2-主流算法分类对比表)
3. [针对本项目的推荐算法选型](#3-针对本项目的推荐算法选型)
4. [关键工程挑战与解法](#4-关键工程挑战与解法)
5. [与 robot-logic 现有架构的整合点](#5-与-robot-logic-现有架构的整合点)
6. [参考论文与项目清单](#6-参考论文与项目清单)
7. [下一步 POC 建议](#7-下一步-poc-建议)

---

## 1. 核心概念与数学模型

### 1.1 SLO 与弹性调度的基本定义

**SLO（Service Level Objective）** 是服务级别目标，通常表示为对某个性能指标的约束。在物流园区调度场景中，SLO 主要体现为：

- **截止时间约束（Deadline）**：订单/任务必须在指定时间前完成
- **优先级（Priority）**：不同任务的重要程度差异
- **资源配额（Quota）**：租户或业务线的资源使用上限
- **软硬截止（Hard/Soft Deadline）**：硬截止必须满足，软截止允许部分违约

**弹性调度（Elastic Scheduling）** 的核心思想是：当系统过载时，通过动态调整任务的资源配额或执行速率来保证核心 SLO 可满足。经典的弹性调度模型由 Buttazzo 等人于 1998 年提出，其基本公式为：

```
U_i^new = min(U_i^max, U_i^old + E_i * (U_total - U_schedulable) / U_schedulable)
```

其中 $U_i$ 为任务 $i$ 的利用率，$E_i$ 为弹性系数，$U_{schedulable}$ 为可调度利用率上界。

### 1.2 Earliest Deadline First（EDF）

EDF 是实时调度领域最经典的动态优先级算法，其核心思想是：**截止时间越近的任务优先级越高**。数学表达为：

```
priority(task_i) = 1 / (deadline_i - current_time)
```

或者使用绝对截止时间作为排序键：

```
sorted_tasks = sorted(tasks, key=lambda t: t.absolute_deadline)
next_task = sorted_tasks[0]
```

**可调度性判定（Uniprocessor EDF）**：

对于隐式截止时间（Implicit Deadline）任务集，EDF 可调度的充分必要条件为：

```
Σ (C_i / T_i) ≤ 1
```

其中 $C_i$ 为最坏情况执行时间，$T_i$ 为任务周期。

**EDF 的优势与局限**：

| 维度 | 优势 | 局限 |
|------|------|------|
| 理论最优性 | 在单处理器隐式截止任务下是最优的 | 多处理器场景下全局 EDF 是 NP-hard |
| 动态适应性 | 自然支持新任务到达 | 需要重新排序，O(n) 开销 |
| 资源竞争 | 公平性好 | 可能导致长任务饥饿 |

### 1.3 Utility Function 与多目标优化

Utility Function（效用函数）将任务的价值量化为执行时间的函数，典型形式包括：

**阶梯型（Step Function）**：
```
U(t) = {
    100%, if completed before deadline
    0%,   if missed
}
```

**线性递减型（Linear）**：
```
U(t) = max(0, 1 - (completion_time - deadline) / grace_period)
```

**Sigmoid 型**：
```
U(t) = 1 / (1 + exp(k * (t - deadline)))
```

在多目标优化场景下，综合效用函数为：

```
Total_Utility = Σ w_i * U_i(completion_time_i)
```

约束条件为：
- 资源约束：Σ resource_requirements ≤ available_resources
- 截止约束：completion_time_i ≤ deadline_i + grace_i

### 1.4 弹性调度（Elastic Scheduling）数学模型

弹性调度的核心是**利用率弹性调整**。设任务 $\tau_i$ 的原始周期为 $T_i$，可调整范围为 $[T_i^{min}, T_i^{max}]$，弹性系数为 $E_i$，则调整后的周期 $T_i'$ 满足：

```
T_i' = min(T_i^{max}, T_i + E_i * (U_total - U_bound))
```

**二次弹性优化问题（Buttazzo 原型）**：

```
Minimize: Σ (T_i - T_i')² / E_i²
Subject to:
    Σ C_i / T_i' ≤ U_bound
    T_i^{min} ≤ T_i' ≤ T_i^{max}
```

2024 年的最新改进（Sudvarg et al.）将线性规划引入此问题，实现了**多项式时间求解**。

### 1.5 关键路径识别与优先级计算

关键路径（Critical Path）在调度中定义为**导致整体完工时间延长的最长路径**。关键路径上的任务具有最高调度优先级。

**关键路径优先调度（Critical Path First, CPF）** 公式：

```
CR_i = Slack_i / Criticality_i
```

其中 $Slack_i = deadline_i - (current_time + remaining_work_i)$，$Criticality_i$ 通过 CPM（关键路径法）计算：

```python
def calculate_criticality(tasks, dependencies):
    forward_pass(tasks)   # 计算最早开始/完成时间
    backward_pass(tasks)  # 计算最晚开始/完成时间
    slack = {t: latest_start[t] - earliest_start[t] for t in tasks}
    return {t: float('inf') if slack[t] == 0 else 1/slack[t] for t in tasks}
```

### 1.6 多 SLO 约束协调机制

在实际系统中，任务通常同时受多个 SLO 约束。本项目涉及的 SLO 包括：

| SLO 类型 | 量化指标 | 调度影响 |
|----------|----------|----------|
| 时效 SLO | 截止时间 (deadline) | EDF 优先级 |
| 吞吐 SLO | 单位时间任务数 | 速率限制 |
| 优先级 SLO | 业务优先级 1-10 | 加权公平调度 |
| 冗余 SLO | 热备设备数量 | 资源预留 |

**多 SLO 综合评分公式**：

```
Score_i = α * EDF_Score_i + β * Priority_Score_i + γ * Urgency_Score_i
```

其中各子分数归一化到 [0, 1]，权重 α+β+γ = 1，由业务策略决定。

---

## 2. 主流算法分类对比表

### 2.1 调度策略分类

| 分类 | 算法名称 | 适用场景 | 时间复杂度 | 优点 | 缺点 |
|------|----------|----------|------------|------|------|
| **经典实时调度** | | | | | |
| | EDF (Earliest Deadline First) | 单机实时任务 | O(log n) | 理论最优 | 多处理器复杂 |
| | RM (Rate Monotonic) | 周期任务 | O(log n) | 简单可预测 | 次优利用率 |
| | LLF (Least Laxity First) | 动态任务 | O(log n) | 适合变长任务 | 高调度开销 |
| **弹性调度** | | | | | |
| | Buttazzo Elastic | 过载保护 | O(n log n) | 自动降级 | 收敛慢 |
| | Orr-Baruah Elastic | 多处理器 | O(n²) | 精确求解 | 实现复杂 |
| | Subtask-level Elastic (RTSS 2024) | 多阶段任务 | O(n log n) | 细粒度控制 | 新兴方法 |
| **行业调度** | | | | | |
| | Kubernetes Default Scheduler | 容器编排 | O(n²) | 成熟生态 | 无 SLO 原生 |
| | Kubernetes PriorityClass + Preemption | 优先级任务 | O(n log n) | 抢占支持 | 资源碎片 |
| | Borg Cell Scheduling | 大规模集群 | O(n) 近似 | 高利用率 | 闭源 |
| **工业调度** | | | | | |
| | GA (Genetic Algorithm) | FJSP | 指数级 | 全局最优 | 慢 |
| | ACO (Ant Colony) | 路径规划 | 指数级 | 并行性好 | 参数敏感 |
| | DRL (Deep Reinforcement Learning) | 动态调度 | 推理 O(1) | 自适应 | 需训练 |
| | Critical Path + VND | FJSP+AGV | 伪多项式 | 确定性强 | 依赖准确性 |
| **微服务/云原生** | | | | | |
| | SLICE | LLM 推理 | O(log n) | SLO 感知 | 新兴 |
| | Morphis | 微服务依赖图 | O(n) | 动态适应 | 需 trace |
| | 2DFQ | 多租户 | O(log n) | 公平性好 | 需 cost 估计 |

### 2.2 算法适用性分析（本项目场景）

| 场景 | 推荐算法 | 理由 |
|------|----------|------|
| 集装箱拆装箱 (A) | EDF + Criticality | 硬截止 + 关键路径依赖 |
| 仓储拣选 (B) | Weighted Fair Queuing + EDF | 多租户 + 时效平衡 |
| 月台装卸 (C) | Elastic + Preemption | 吞吐量优先，允许降级 |
| 跨楼层运输 (D) | DRL (PPO) + RRT* | 动态路径 + 多 AGV 协调 |

### 2.3 Kubernetes 与 Borg 对比

| 特性 | Borg | Kubernetes | 对本项目参考 |
|------|------|------------|--------------|
| 优先级机制 | 10 级优先级 | PriorityClass | 业务优先级映射 |
| 抢占式调度 | 支持 | 支持 | 关键任务优先 |
| 资源配额 | 强调公平性 | ResourceQuota | 租户资源上限 |
| 细胞调度 | Cell scheduling | 调度框架 | 多调度器协同 |
| 状态管理 | 集中式 | etcd | 分布式状态共识 |

---

## 3. 针对本项目的推荐算法选型

### 3.1 整体架构：分层混合调度

综合考虑物流园区的实际需求（多设备、多租户、硬软截止混合、实时遥测融合），推荐采用**分层混合调度架构**：

```
┌─────────────────────────────────────────────────────────────┐
│                    全局调度层 (Global)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ SLO 仲裁器   │  │ 租户公平器  │  │ 关键路径识别 │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│           ↓              ↓              ↓                    │
│  ┌─────────────────────────────────────────┐                │
│  │        优先级队列 (Multi-level Heap)      │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    本地调度层 (Local per Device)             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ EDF 调度器  │  │ SRP 资源协议 │  │ 弹性降级器  │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 核心调度器数据结构

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from heapq import heappush, heappop
import asyncio
import time
from collections import defaultdict

class SLOType(Enum):
    HARD_DEADLINE = auto()    # 硬截止，必须满足
    SOFT_DEADLINE = auto()    # 软截止，可降级
    BEST_EFFORT = auto()     # 尽力而为

class TaskState(Enum):
    PENDING = auto()
    RUNNING = auto()
    DEGRADED = auto()        # 降级执行中
    COMPLETED = auto()
    FAILED = auto()
    ROLLED_BACK = auto()     # 回滚

@dataclass(order=True)
class SLOTask:
    # 排序键：先按 SLO 类型，再按截止时间
    sort_key: tuple = field(compare=True)
    
    # 任务标识
    task_id: str
    task_type: str  # 'A', 'B', 'C', 'D' 对应场景
    
    # SLO 参数
    slo_type: SLOType
    deadline: float                    # 绝对截止时间戳
    created_time: float = field(default_factory=time.time)
    priority: int = 5                 # 业务优先级 1-10
    elasticity: float = 1.0            # 弹性系数，越大越容易降级
    
    # 执行参数
    estimated_duration: float          # 预估执行时间（秒）
    remaining_work: float = field(default=None)  # 剩余工作量
    dependencies: Set[str] = field(default_factory=set)
    
    # 状态
    state: TaskState = TaskState.PENDING
    assigned_device: Optional[str] = None
    backup_device: Optional[str] = None  # 热备设备
    
    # 元数据
    tenant_id: Optional[str] = None     # 租户标识
    tags: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.remaining_work is None:
            self.remaining_work = self.estimated_duration
        # 计算排序键：元组比较按顺序
        # (slo_level, deadline, -priority) 实现优先级
        slo_level = {
            SLOType.HARD_DEADLINE: 0,
            SLOType.SOFT_DEADLINE: 1,
            SLOType.BEST_EFFORT: 2
        }[self.slo_type]
        self.sort_key = (slo_level, self.deadline, -self.priority)
    
    @property
    def slack(self) -> float:
        """计算时间缓冲"""
        return self.deadline - time.time() - self.remaining_work
    
    @property
    def laxity(self) -> float:
        """计算松弛度（相对值）"""
        if self.remaining_work <= 0:
            return float('inf')
        return self.slack / self.remaining_work

class SLOElasticScheduler:
    """
    SLO 弹性调度器
    
    核心算法：
    1. Multi-level deadline-sorted heap
    2. Elastic degradation on overload
    3. Critical path based prioritization
    4. SRP for resource contention
    """
    
    def __init__(
        self,
        max_concurrent: int = 10,
        overload_threshold: float = 0.85,
        grace_period: float = 30.0
    ):
        # 调度队列
        self._pending_heap: List[SLOTask] = []
        self._tasks: Dict[str, SLOTask] = {}
        
        # 运行中的任务
        self._running: Dict[str, SLOTask] = {}
        self._max_concurrent = max_concurrent
        
        # 过载控制
        self._overload_threshold = overload_threshold
        self._grace_period = grace_period
        
        # 设备状态
        self._device_load: Dict[str, float] = defaultdict(float)
        self._device_capabilities: Dict[str, Set[str]] = defaultdict(set)
        
        # 依赖图
        self._dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        # 关键路径缓存
        self._critical_path: Set[str] = set()
        
        # 降级任务追踪
        self._degraded_tasks: Set[str] = set()
        
        # 锁
        self._lock = asyncio.Lock()
    
    def add_task(self, task: SLOTask) -> None:
        """添加新任务到调度队列"""
        with self._lock:
            self._tasks[task.task_id] = task
            self._dependencies[task.task_id] = task.dependencies.copy()
            heappush(self._pending_heap, task)
    
    def _check_dependencies_met(self, task: SLOTask) -> bool:
        """检查任务依赖是否全部满足"""
        return all(
            self._tasks.get(dep_id, SLOTask('', '', SLOType.BEST_EFFORT, 0)).state 
            == TaskState.COMPLETED
            for dep_id in task.dependencies
        )
    
    def _compute_criticality(self) -> Dict[str, float]:
        """
        关键路径计算（CPM - 关键路径法）
        返回每个任务的关键度（0=关键，1=不关键）
        """
        if not self._tasks:
            return {}
        
        # 构建邻接表
        graph: Dict[str, List[str]] = defaultdict(list)
        in_degree: Dict[str, int] = defaultdict(int)
        
        for task_id, task in self._tasks.items():
            for dep in task.dependencies:
                graph[dep].append(task_id)
                in_degree[task_id] += 1
        
        # 前向传递：计算最早完成时间
        earliest: Dict[str, float] = {}
        queue = [tid for tid in self._tasks if in_degree[tid] == 0]
        
        while queue:
            curr = queue.pop(0)
            if curr not in self._tasks:
                continue
            task = self._tasks[curr]
            earliest[curr] = task.created_time + task.remaining_work
            
            for neighbor in graph[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # 反向传递：计算最晚完成时间
        latest: Dict[str, float] = {}
        max_time = max(earliest.values()) if earliest else 0
        
        for task_id in self._tasks:
            latest[task_id] = max_time
        
        # 简化：关键度 = slack / max_slack
        slacks = {tid: max(0, latest[tid] - earliest.get(tid, 0)) 
                  for tid in self._tasks}
        max_slack = max(slacks.values()) if slacks else 1
        
        return {
            tid: slacks[tid] / max_slack if max_slack > 0 else 1.0
            for tid in slacks
        }
    
    def _calculate_elastic_degradation(self) -> Dict[str, float]:
        """
        计算弹性降级因子
        返回：task_id -> 降级后速率比例 (<= 1.0)
        """
        if not self._pending_heap:
            return {}
        
        # 计算当前利用率
        total_load = sum(
            task.remaining_work 
            for task in self._pending_heap 
            if task.state == TaskState.PENDING
        )
        capacity = self._max_concurrent * self._grace_period
        
        if total_load <= capacity * self._overload_threshold:
            return {t.task_id: 1.0 for t in self._pending_heap}
        
        # 过载：计算降级因子
        excess_ratio = total_load / (capacity * self._overload_threshold) - 1
        degradation: Dict[str, float] = {}
        
        # 按弹性系数降级（弹性大的先降）
        sorted_tasks = sorted(
            self._pending_heap,
            key=lambda t: (-t.elasticity, t.deadline)
        )
        
        total_degradation_needed = excess_ratio * capacity
        remaining_degradation = total_degradation_needed
        
        for task in sorted_tasks:
            if remaining_degradation <= 0:
                degradation[task.task_id] = 1.0
            else:
                # 降级量 = 弹性系数 * 剩余工作量
                max_degrade = min(
                    task.remaining_work * 0.5,  # 最多降50%
                    remaining_degradation
                )
                degradation[task.task_id] = 1.0 - max_degrade / task.remaining_work
                remaining_degradation -= max_degrade
        
        return degradation
    
    async def get_next_batch(self, max_count: Optional[int] = None) -> List[SLOTask]:
        """
        获取下一批可调度任务
        
        算法：
        1. 过滤已满足依赖的任务
        2. 更新关键路径
        3. 计算弹性降级
        4. 选择最高优先级任务
        """
        max_count = max_count or self._max_concurrent
        
        async with self._lock:
            eligible = []
            degraded = self._calculate_elastic_degradation()
            criticality = self._compute_criticality()
            
            for task in self._pending_heap:
                if task.state != TaskState.PENDING:
                    continue
                    
                # 检查依赖
                if not self._check_dependencies_met(task):
                    continue
                
                # 检查截止时间可行性
                if task.slack < 0:
                    # 已过期，跳过或标记失败
                    task.state = TaskState.FAILED
                    continue
                
                # 计算综合评分
                deadline_score = 1.0 / (task.deadline - time.time() + 1e-6)
                priority_score = task.priority / 10.0
                criticality_score = 1.0 - criticality.get(task.task_id, 0.5)
                
                combined_score = (
                    0.5 * deadline_score +
                    0.3 * priority_score +
                    0.2 * criticality_score
                )
                
                # 应用降级
                deg_factor = degraded.get(task.task_id, 1.0)
                task.state = TaskState.DEGRADED if deg_factor < 1.0 else TaskState.RUNNING
                
                eligible.append((combined_score, task))
            
            # 选择最高分任务
            eligible.sort(key=lambda x: x[0], reverse=True)
            selected = [task for _, task in eligible[:max_count]]
            
            for task in selected:
                task.state = TaskState.RUNNING
            
            return selected
    
    async def mark_completed(self, task_id: str) -> None:
        """标记任务完成"""
        async with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].state = TaskState.COMPLETED
                self._running.pop(task_id, None)
    
    def get_metrics(self) -> Dict:
        """获取调度器指标"""
        return {
            'pending_count': len([t for t in self._pending_heap if t.state == TaskState.PENDING]),
            'running_count': len(self._running),
            'degraded_count': len(self._degraded_tasks),
            'device_loads': dict(self._device_load),
            'critical_path_tasks': list(self._critical_path)
        }
```

### 3.3 设备适配层接口

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class DeviceSchedulingCapability(Protocol):
    """设备调度能力协议"""
    
    async def get_available_slots(self) -> int:
        """获取可用槽位数"""
        ...
    
    async def get_current_load(self) -> float:
        """获取当前负载率"""
        ...
    
    async def get_supported_task_types(self) -> Set[str]:
        """获取支持的任务类型"""
        ...
    
    async def reserve(self, task_id: str, slot_count: int = 1) -> bool:
        """预留槽位"""
        ...
    
    async def release(self, task_id: str) -> None:
        """释放槽位"""
        ...
```

### 3.4 与 MQTT 遥测融合的事件处理

```python
class TelemetryAwareScheduler:
    """
    融合 MQTT 遥测数据的智能调度器
    
    输入：
    - MQTT topic: robot/{device_id}/telemetry
    - 遥测数据：位置、速度、电池电量、机械臂末端负载
    """
    
    def __init__(self, base_scheduler: SLOElasticScheduler):
        self._scheduler = base_scheduler
        self._telemetry_cache: Dict[str, Dict] = {}
        self._telemetry_handlers: List[Callable] = []
    
    def register_telemetry_handler(self, handler: Callable[[str, Dict], None]) -> None:
        """注册遥测数据处理器"""
        self._telemetry_handlers.append(handler)
    
    async def on_telemetry(self, device_id: str, telemetry: Dict) -> None:
        """
        MQTT 遥测数据回调
        
        遥测数据结构：
        {
            "device_id": "agv-01",
            "timestamp": 1692800000.123,
            "position": {"x": 1.0, "y": 2.0, "z": 0.0},
            "velocity": {"vx": 0.5, "vy": 0.0, "vz": 0.0},
            "battery": 0.85,
            "payload_weight": 12.5,
            "status": "idle" | "moving" | "loading" | "unloading"
        }
        """
        self._telemetry_cache[device_id] = telemetry
        
        # 触发调度重评估
        await self._reassess_scheduling(device_id, telemetry)
        
        # 执行注册的处理器
        for handler in self._telemetry_handlers:
            await handler(device_id, telemetry)
    
    async def _reassess_scheduling(
        self, 
        device_id: str, 
        telemetry: Dict
    ) -> None:
        """
        根据遥测数据重评估调度决策
        
        触发条件：
        1. 设备电量低于阈值 -> 重新分配任务
        2. 设备位置变化 -> 更新路径规划
        3. 设备状态异常 -> 触发热备切换
        """
        battery_threshold = 0.15
        if telemetry.get('battery', 1.0) < battery_threshold:
            # 触发低电量重分配
            await self._trigger_reallocation(device_id)
        
        status = telemetry.get('status', 'idle')
        if status == 'fault' or status == 'e_stop':
            # 触发故障恢复流程
            await self._trigger_failover(device_id)
    
    async def _trigger_reallocation(self, device_id: str) -> None:
        """将设备上的任务重新分配"""
        # 查找该设备正在执行的任务
        tasks_to_move = [
            task for task in self._scheduler._running.values()
            if task.assigned_device == device_id
        ]
        
        for task in tasks_to_move:
            # 取消原分配
            await self._scheduler.mark_completed(task.task_id)  # 或其他取消逻辑
            # 重新加入调度队列
            task.assigned_device = None
            task.state = TaskState.PENDING
            self._scheduler.add_task(task)
    
    async def _trigger_failover(self, device_id: str) -> None:
        """触发热备切换"""
        tasks_to_failover = [
            task for task in self._scheduler._running.values()
            if task.assigned_device == device_id
        ]
        
        for task in tasks_to_failover:
            if task.backup_device:
                # 切换到热备设备
                task.assigned_device = task.backup_device
                # 记录切换事件
                # TODO: 发布 failover 事件到 MQTT
            else:
                # 无热备，标记失败
                task.state = TaskState.FAILED
```

---

## 4. 关键工程挑战与解法

### 4.1 调度抖动（Thrashing）问题

**问题描述**：当系统在高负载边缘频繁波动时，任务可能被反复调度-取消-重新调度，导致吞吐量下降和资源浪费。

**解决方案**：采用**滞后环（Hysteresis）**和**冷却期（Cooldown）**机制：

```python
class ThrashingPrevention:
    def __init__(self, cooldown_seconds: float = 5.0, threshold_ratio: float = 0.1):
        self._cooldown_seconds = cooldown_seconds
        self._threshold_ratio = threshold_ratio
        self._last_reschedule: Dict[str, float] = {}
    
    def can_reschedule(self, task_id: str, current_time: float) -> bool:
        """检查是否允许重新调度"""
        if task_id not in self._last_reschedule:
            return True
        
        elapsed = current_time - self._last_reschedule[task_id]
        return elapsed >= self._cooldown_seconds
    
    def record_reschedule(self, task_id: str, current_time: float) -> None:
        """记录重新调度事件"""
        self._last_reschedule[task_id] = current_time
    
    def get_thrashing_score(self) -> float:
        """
        计算调度抖动分数
        分数越高表示抖动越严重
        """
        if not self._last_reschedule:
            return 0.0
        
        current_time = time.time()
        recent_reschedules = sum(
            1 for t in self._last_reschedule.values()
            if current_time - t < 60  # 过去60秒
        )
        
        return recent_reschedules / len(self._last_reschedule)
```

### 4.2 优先级反转（Priority Inversion）与解决方案

**问题描述**：在多设备协作场景中，低优先级任务持有共享资源（如货架位置），阻塞高优先级任务。

**解决方案**：实现**Deadline Floor 继承协议（DFP）**，改编自实时系统领域的 SRP：

```python
class DeadlineFloorProtocol:
    """
    Deadline Floor 继承协议
    
    原理：
    1. 每个资源关联一个 deadline floor（使用该资源的任务的最小截止时间）
    2. 任务进入临界区时，其截止时间临时降为 floor 值
    3. 这确保了持有资源的任务不会被更早截止的任务抢占
    """
    
    def __init__(self):
        self._resource_floors: Dict[str, float] = {}
        self._resource_holders: Dict[str, Optional[str]] = {}
        self._resource_queues: Dict[str, List[str]] = defaultdict(list)
    
    def set_resource_floor(self, resource_id: str, floor_deadline: float) -> None:
        """设置资源的截止时间下限"""
        self._resource_floors[resource_id] = floor_deadline
    
    async def acquire(self, task_id: str, resource_id: str, current_deadline: float) -> float:
        """
        请求获取资源
        
        返回：任务的新截止时间（可能被降低）
        """
        floor = self._resource_floors.get(resource_id, current_deadline)
        
        holder = self._resource_holders.get(resource_id)
        if holder is None:
            # 资源空闲，直接获取
            self._resource_holders[resource_id] = task_id
            self._resource_floors[resource_id] = current_deadline
            return current_deadline
        elif holder == task_id:
            # 重入
            return current_deadline
        else:
            # 资源被占用，加入等待队列
            self._resource_queues[resource_id].append(task_id)
            
            # 继承 deadline floor
            inherited_deadline = min(current_deadline, floor)
            return inherited_deadline
    
    async def release(self, task_id: str, resource_id: str) -> None:
        """释放资源"""
        if self._resource_holders.get(resource_id) != task_id:
            return
        
        # 唤醒等待队列中的下一个任务
        self._resource_queues[resource_id].pop(0, None)
        
        next_holder = self._resource_queues[resource_id][0] if self._resource_queues[resource_id] else None
        self._resource_holders[resource_id] = next_holder
```

### 4.3 长尾延迟（Long Tail Latency）优化

**问题描述**：在分布式物流系统中，少数慢任务可能拖慢整体吞吐量。

**解决方案**：参考 Shinjuku 的微秒级抢占调度理念，设计**自适应时间片**机制：

```python
class AdaptiveTimeSliceScheduler:
    """
    自适应时间片调度器
    
    核心思想：
    1. 短任务优先：使用短时间片确保快速任务不被阻塞
    2. 动态调整：根据任务预估时长动态调整时间片
    3. 抢占机制：长时间运行的任务定期让出执行权
    """
    
    def __init__(
        self,
        base_slice_ms: float = 100,
        min_slice_ms: float = 10,
        max_slice_ms: float = 500
    ):
        self._base_slice = base_slice_ms / 1000  # 转换为秒
        self._min_slice = min_slice_ms / 1000
        self._max_slice = max_slice_ms / 1000
    
    def calculate_slice(self, task: SLOTask) -> float:
        """
        根据任务特征计算时间片
        
        原则：
        - 截止时间近的任务获得更短的时间片（更快响应）
        - 预估时长长的任务获得更长的时间片（减少切换开销）
        - 松弛度小的任务获得更高优先级
        """
        urgency = 1.0 / (task.slack + 1e-6)
        length_factor = min(task.estimated_duration / 60.0, 1.0)  # 标准化到1分钟
        
        slice_time = self._base_slice * (0.5 + 0.5 * length_factor)
        slice_time *= min(urgency, 10.0) / urgency  # 紧急任务缩短
        
        return max(self._min_slice, min(self._max_slice, slice_time))
    
    async def schedule_round(
        self, 
        tasks: List[SLOTask], 
        executor: Callable[[SLOTask], Awaitable]
    ) -> List[SLOTask]:
        """
        执行一轮调度
        
        返回：未完成任务列表
        """
        remaining = []
        
        for task in tasks:
            slice_time = self.calculate_slice(task)
            try:
                await asyncio.wait_for(
                    executor(task),
                    timeout=slice_time
                )
            except asyncio.TimeoutError:
                # 时间片用完，放回调度队列
                remaining.append(task)
        
        return remaining
```

### 4.4 多租户公平性保障

**问题描述**：多个租户/业务线共享机器人资源时，需要保证公平性和 SLA。

**解决方案**：实现**多维公平队列（Multi-dimensional Fair Queuing）**：

```python
class TenantFairScheduler:
    """
    多租户公平调度器
    
    采用 Deficit Round Robin (DRR) 算法的变体：
    1. 每个租户分配权重
    2. 追踪每个租户的 deficit（赤字）
    3. 超过配额的任务降级处理
    """
    
    def __init__(self, default_weight: float = 1.0):
        self._tenant_weights: Dict[str, float] = {}
        self._tenant_deficits: Dict[str, float] = defaultdict(float)
        self._tenant_quotas: Dict[str, float] = {}  # 每周期配额
        self._default_weight = default_weight
        self._quantum = 10.0  # 时间片大小（秒）
    
    def set_tenant_weight(self, tenant_id: str, weight: float) -> None:
        """设置租户权重"""
        self._tenant_weights[tenant_id] = weight
        # 重新计算配额
        total_weight = sum(self._tenant_weights.values())
        self._tenant_quotas[tenant_id] = self._quantum * weight / total_weight
    
    def get_tenant_allocation(self, tenant_id: str) -> Dict:
        """获取租户当前的资源分配情况"""
        return {
            'weight': self._tenant_weights.get(tenant_id, self._default_weight),
            'deficit': self._tenant_deficits[tenant_id],
            'quota': self._tenant_quotas.get(tenant_id, self._quantum * self._default_weight)
        }
    
    async def schedule_tenant_round(
        self,
        tasks_by_tenant: Dict[str, List[SLOTask]],
        base_scheduler: SLOElasticScheduler
    ) -> List[SLOTask]:
        """
        执行多租户轮询调度
        
        算法：
        1. 按权重轮询租户
        2. 每个租户按 EDF 处理任务
        3. 超过 deficit 的任务推迟
        """
        scheduled = []
        
        for tenant_id, tasks in tasks_by_tenant.items():
            quota = self._tenant_quotas.get(tenant_id, self._quantum * self._default_weight)
            used_time = 0.0
            
            # 按 EDF 排序租户内任务
            sorted_tasks = sorted(tasks, key=lambda t: t.deadline)
            
            for task in sorted_tasks:
                if used_time >= quota + self._tenant_deficits[tenant_id]:
                    # 超过配额，降级处理
                    task.state = TaskState.DEGRADED
                    self._degraded_tasks.add(task.task_id)
                    continue
                
                scheduled.append(task)
                used_time += task.estimated_duration
            
            # 更新 deficit
            self._tenant_deficits[tenant_id] = max(0, used_time - quota)
        
        return scheduled
    
    def refill_deficits(self) -> None:
        """每个调度周期开始时补充 deficit"""
        for tenant_id in self._tenant_deficits:
            self._tenant_deficits[tenant_id] = 0
```

---

## 5. 与 robot-logic 现有架构的整合点

### 5.1 架构整合总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                         WMS / MES / ERP                             │
│              (订单下达、SLO 参数配置、截止时间设置)                      │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓ REST API
                                  ↑
┌─────────────────────────────────────────────────────────────────────┐
│                    simulation/backend/runtime.py                     │
│                         (Runtime 调度入口)                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    新增: SLOElasticScheduler                    │  │
│  │                  (替换现有的 TaskScheduler)                     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                  ↓                                   │
│  ┌──────────────────────┐    ┌──────────────────────┐             │
│  │ services/orchestration/ │    │ services/telemetry/ │             │
│  │    设备命令下发         │    │    MQTT 事件融合     │             │
│  └──────────────────────┘    └──────────────────────┘             │
│                                  ↓                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                         HAL 层                                 │  │
│  │  xarm.py | ur_rtde.py | franka.py | agv.py | stacker.py      │  │
│  │  (新增: SLO 状态上报能力)                                       │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 核心整合接口

#### 5.2.1 调度器接口扩展

**文件**: `simulation/backend/algorithm/scheduler/scheduler.py`

```python
# 新增：SLO 调度器集成入口
from .slo_scheduler import SLOElasticScheduler, SLOTask, SLOType, TaskState

class HybridScheduler:
    """
    混合调度器
    
    支持模式：
    1. Legacy 模式：兼容现有 TaskScheduler 行为
    2. SLO 模式：启用 SLO 弹性调度
    """
    
    def __init__(self, mode: str = "legacy"):
        self._mode = mode
        if mode == "slo":
            self._slo_scheduler = SLOElasticScheduler(
                max_concurrent=10,
                overload_threshold=0.85
            )
        else:
            self._scheduler = TaskScheduler()  # 现有调度器
    
    def add_task(self, task_data: Dict) -> str:
        """添加任务"""
        if self._mode == "slo":
            # 转换为 SLOTask
            slo_type = SLOType.HARD_DEADLINE if task_data.get('hard_deadline') else SLOType.SOFT_DEADLINE
            task = SLOTask(
                task_id=task_data['task_id'],
                task_type=task_data['task_type'],
                slo_type=slo_type,
                deadline=task_data['deadline'],
                priority=task_data.get('priority', 5),
                elasticity=task_data.get('elasticity', 1.0),
                estimated_duration=task_data['estimated_duration'],
                tenant_id=task_data.get('tenant_id')
            )
            self._slo_scheduler.add_task(task)
            return task.task_id
        else:
            # Legacy 模式
            task = Task(**task_data)
            self._scheduler.add_task(task)
            return task.task_id
    
    async def get_next_batch(self, max_concurrent: int = 3) -> List[Dict]:
        """获取下一批任务"""
        if self._mode == "slo":
            tasks = await self._slo_scheduler.get_next_batch(max_concurrent)
            return [self._task_to_dict(t) for t in tasks]
        else:
            return self._scheduler.get_next_batch(max_concurrent)
```

#### 5.2.2 MQTT 遥测融合

**文件**: `rcs/rcs/mqtt/telemetry_fusion.py`（新增）

```python
"""
MQTT 遥测数据与调度器融合模块

监听以下主题：
- robot/{device_id}/telemetry - 实时遥测
- rcs/{device_id}/state - 设备状态
- rcs/{device_id}/alert - 告警事件

发布以下主题：
- scheduler/{device_id}/priority_update - 优先级更新
- scheduler/{device_id}/reallocation - 任务重分配
"""

class TelemetryFusion:
    """
    遥测数据融合器
    
    功能：
    1. 接收并缓存多设备遥测数据
    2. 检测设备状态异常
    3. 触发调度器重评估
    """
    
    def __init__(self, scheduler: SLOElasticScheduler, mqtt_client: MqttClient):
        self._scheduler = scheduler
        self._mqtt = mqtt_client
        self._cache: Dict[str, Dict] = {}
        
        # 注册遥测处理器
        self._scheduler.register_telemetry_handler(self._on_device_update)
        
        # 订阅遥测主题
        self._mqtt.subscribe("robot/+/telemetry", qos=0, handler=self._handle_telemetry)
        self._mqtt.subscribe("rcs/+/alert", qos=1, handler=self._handle_alert)
    
    async def _handle_telemetry(self, topic: str, payload: bytes) -> None:
        """处理遥测消息"""
        # 解析 device_id
        parts = topic.split('/')
        if len(parts) < 3:
            return
        device_id = parts[1]
        
        telemetry = json.loads(payload)
        telemetry['device_id'] = device_id
        
        # 缓存数据
        self._cache[device_id] = telemetry
        
        # 触发调度重评估
        await self._scheduler.on_telemetry(device_id, telemetry)
    
    async def _handle_alert(self, topic: str, payload: bytes) -> None:
        """处理告警消息"""
        alert = json.loads(payload)
        device_id = alert.get('device_id')
        alert_type = alert.get('type')
        
        if alert_type in ('hal_read_timeout', 'controller_halted', 'device_fault'):
            # 触发故障恢复
            await self._scheduler.trigger_failover(device_id)
```

#### 5.2.3 HAL 层 SLO 状态上报

**文件**: `rcs/rcs/hal/protocol.py`

```python
# 新增 SLO 状态协议

@runtime_checkable
class DeviceSLOCapability(Protocol):
    """设备 SLO 能力协议"""
    
    async def report_slo_status(self) -> SLODeviceStatus:
        """
        上报设备 SLO 状态
        
        返回：
        {
            "device_id": str,
            "current_utilization": float,      # 0.0-1.0
            "available_capacity": float,       # 可用容量
            "queue_depth": int,               # 待处理任务数
            "estimated_completion_time": float,
            "slo_violation_risk": float,      # 0.0-1.0
            "battery_level": float | None,    # 电池电量（如适用）
            "fault_status": str | None
        }
        """
        ...
    
    async def get_slo_metrics(self) -> SLOMetrics:
        """获取 SLO 指标"""
        ...

@dataclass
class SLODeviceStatus:
    device_id: str
    current_utilization: float
    available_capacity: float
    queue_depth: int
    estimated_completion_time: float
    slo_violation_risk: float
    battery_level: Optional[float] = None
    fault_status: Optional[str] = None

@dataclass
class SLOMetrics:
    tasks_completed: int
    tasks_failed: int
    tasks_degraded: int
    average_latency: float
    slo_violations: int
    hot_standby_activations: int
```

### 5.3 可观测性指标清单

为可观测平台建设，需要采集以下调度指标：

| 指标名称 | 类型 | 描述 | 采集方式 |
|----------|------|------|----------|
| `scheduler.pending_tasks` | Gauge | 待调度任务数 | Prometheus |
| `scheduler.running_tasks` | Gauge | 运行中任务数 | Prometheus |
| `scheduler.degraded_tasks` | Gauge | 降级执行任务数 | Prometheus |
| `scheduler.utilization` | Gauge | 系统利用率 | Prometheus |
| `scheduler.task.latency` | Histogram | 任务完成延迟 | Prometheus |
| `scheduler.slo.violations` | Counter | SLO 违约次数 | Prometheus |
| `scheduler.failover.activations` | Counter | 热备切换次数 | Prometheus |
| `scheduler.device.load` | Gauge | 各设备负载 | Prometheus |
| `scheduler.queue.depth` | Gauge | 各队列深度 | Prometheus |
| `scheduler.thrashing.score` | Gauge | 调度抖动分数 | Prometheus |

### 5.4 API 扩展

**新增端点**:

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/scheduler/tasks` | 创建 SLO 任务 |
| GET | `/api/scheduler/queue` | 查看调度队列 |
| POST | `/api/scheduler/priorities` | 批量更新优先级 |
| GET | `/api/scheduler/metrics` | 获取调度指标 |
| POST | `/api/scheduler/rebalance` | 触发重平衡 |

---

## 6. 参考论文与项目清单

### 6.1 实时调度与弹性调度

| 序号 | 标题 | 作者 | 来源 | 年份 | 链接 |
|------|------|------|------|------|------|
| 1 | Improved Implicit-Deadline Elastic Scheduling | Sudvarg, Gill, Baruah | IEEE SIES | 2024 | https://doi.org/10.1109/sies62473.2024.10768003 |
| 2 | Schedulability Analysis and Performance Optimization for Constrained-Deadline Elastic Tasks | - | ACM TECS | 2024 | https://doi.org/10.1145/3696355.3696362 |
| 3 | Subtask-Level Elastic Scheduling | Sudvarg et al. | RTSS | 2024 | https://sudvarg.net/publications/RTSS2024_subtask_elastic.pdf |
| 4 | Elastic Scheduling for Harmonic Task Systems | Sudvarg et al. | RTAS | 2024 | https://sudvarg.com/publications/RTAS_2024_Harmonic_Elastic_Scheduling.pdf |
| 5 | A Deadline-Floor Inheritance Protocol for EDF Scheduled Embedded Real-Time Systems | - | IEEE Trans. Computers | 2014 | https://doi.org/10.1109/tc.2014.2322619 |
| 6 | Priority Inheritance Protocols: An Approach to Real-Time Synchronization | Sha, Rajkumar, Lehoczky | IEEE Trans. Computers | 1990 | https://doi.org/10.1109/12.57058 |

### 6.2 集群调度与 Kubernetes

| 序号 | 标题 | 作者 | 来源 | 年份 | 链接 |
|------|------|------|------|------|------|
| 7 | Large-Scale Cluster Management at Google with Borg | Verma et al. | - | 2015 | http://static.googleusercontent.com/media/research.google.com/ru/us/pubs/archive/43438.pdf |
| 8 | Borg, Omega, and Kubernetes | Burns et al. | ACM Queue | 2016 | https://queue.acm.org/detail.cfm?id=2898444 |
| 9 | Omega: Flexible, Scalable Schedulers for Large Compute Clusters | Schwarzkopf et al. | ACM SoSP | 2013 | https://www.researchgate.net/publication/266653848 |

### 6.3 工业调度与 AGV

| 序号 | 标题 | 作者 | 来源 | 年份 | 链接 |
|------|------|------|------|------|------|
| 10 | An Improved Genetic Algorithm for Solving the Multi-AGV Flexible Job Shop Scheduling Problem | - | Sensors | 2023 | https://mdpi-res.com/d_attachment/sensors/sensors-23-03815 |
| 11 | A Heuristic-Assisted Deep Reinforcement Learning Algorithm for Flexible Job Shop Scheduling | - | J. of Intelligent Manufacturing | 2025 | https://doi.org/10.1007/s40747-025-01828-6 |
| 12 | Critical-Path-Based Variable Neighborhood Descent for Joint Scheduling of FJSP and AGVs | - | Mathematics | 2023 | https://doi.org/10.3390/math13233883 |
| 13 | Multi-AGV Scheduling and Path Planning Based on an Improved Ant Colony Algorithm | - | MDPI Algorithms | 2024 | https://www.mdpi.com/2624-8921/7/3/102 |

### 6.4 微服务与云原生调度

| 序号 | 标题 | 作者 | 来源 | 年份 | 链接 |
|------|------|------|------|------|------|
| 14 | Derm: SLA-aware Resource Management for Highly Dynamic Microservices | - | ISCA | 2024 | https://doi.org/10.1109/isca59077.2024.00039 |
| 15 | Morphis: SLO-Aware Resource Scheduling for Microservices with Time-Varying Call Graphs | - | arXiv | 2026 | https://arxiv.org/html/2602.01044v2 |
| 16 | SLA Aware Deep Reinforcement Learning for Adaptive EdgeCloud Task Scheduling | - | Scientific Reports | 2026 | https://www.nature.com/articles/s41598-026-40237-8 |

### 6.5 尾延迟优化

| 序号 | 标题 | 作者 | 来源 | 年份 | 链接 |
|------|------|------|------|------|------|
| 17 | Shinjuku: Preemptive Scheduling for Microsecond-scale Tail Latency | Kaffes et al. | NSDI | 2019 | https://www.usenix.org/system/files/nsdi19-kaffes.pdf |
| 18 | Achieving Microsecond-Scale Tail Latency Efficiently with Approximate Optimal Scheduling | - | - | - | https://dslab.epfl.ch/pubs/concord.pdf |
| 19 | LibPreemptible: Enabling Fast, Adaptive, and Hardware-Assisted User-Space Scheduling | - | HPCA | 2024 | https://arxiv.org/abs/2308.02896 |

### 6.6 多租户公平调度

| 序号 | 标题 | 作者 | 来源 | 年份 | 链接 |
|------|------|------|------|------|------|
| 20 | 2DFQ: Two-Dimensional Fair Queuing for Multi-Tenant Cloud Services | Mace et al. | SIGCOMM | 2016 | https://cs.brown.edu/people/jcmace/papers/mace162dfq.pdf |
| 21 | WF2Q: Worst-Case Fair Weighted Fair Queueing | Zhang & Rossi | INFOCOM | 1996 | https://www.cs.cmu.edu/~hzhang/papers/INFOCOM96.pdf |

---

## 7. 下一步 POC 建议

### 7.1 POC 阶段划分

#### Phase 1: 基础调度框架（2周）

**目标**：实现核心 SLO 调度器并与现有 simulation/backend 集成

**交付物**：
- `simulation/backend/algorithm/scheduler/slo_scheduler.py`（核心调度器）
- `simulation/backend/algorithm/scheduler/hybrid_scheduler.py`（兼容适配层）
- 单元测试覆盖核心路径

**验收标准**：
- [ ] 任务可按 EDF 优先级调度
- [ ] 支持硬截止/软截止任务区分
- [ ] 与现有 API 向后兼容

#### Phase 2: MQTT 遥测融合（2周）

**目标**：实现遥测数据与调度器的闭环反馈

**交付物**：
- `rcs/rcs/mqtt/telemetry_fusion.py`
- MQTT 遥测处理器
- 设备状态异常检测

**验收标准**：
- [ ] 遥测数据实时触发调度重评估
- [ ] 设备故障自动触发任务迁移
- [ ] 端到端延迟 < 100ms

#### Phase 3: 弹性降级与热备（2周）

**目标**：实现完整的弹性调度和热备切换

**交付物**：
- 弹性降级算法实现
- 热备切换机制
- 关键路径识别模块

**验收标准**：
- [ ] 系统过载时自动降级
- [ ] 热备设备可在 < 5s 内接管
- [ ] 降级任务完成率 > 80%

#### Phase 4: 多租户与可观测性（2周）

**目标**：实现多租户公平调度和完整可观测性

**交付物**：
- 多租户调度器
- Prometheus 指标导出
- Dashboard 配置

**验收标准**：
- [ ] 租户公平性偏差 < 10%
- [ ] 调度指标完整采集
- [ ] 可通过 Grafana 查看调度状态

### 7.2 技术风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 调度抖动 | 高 | 实现冷却期机制，监控抖动分数 |
| 状态一致性 | 高 | 使用 asyncio.Lock 保证原子性，事件溯源 |
| 性能瓶颈 | 中 | Profiling 定位热点，批量处理优化 |
| 算法收敛 | 中 | 限流 + 降级策略，预留人工干预接口 |

### 7.3 关键决策点

1. **调度器部署位置**：初期部署在 simulation/backend，复用现有 Runtime 入口；后期可考虑独立微服务
2. **降级策略选择**：建议采用**速率降级**（降低执行频率）而非**丢弃策略**，更适合物流场景
3. **热备切换触发**：建议采用**主动探测**（定期心跳）+**被动告警**双重机制

---

## 附录 A：术语表

| 术语 | 英文 | 定义 |
|------|------|------|
| SLO | Service Level Objective | 服务级别目标，系统承诺的性能指标 |
| EDF | Earliest Deadline First | 最早截止时间优先调度算法 |
| RM | Rate Monotonic | 速率单调调度算法 |
| FJSP | Flexible Job Shop Scheduling Problem | 柔性作业车间调度问题 |
| AGV | Automated Guided Vehicle | 自动导引车 |
| SRP | Stack Resource Policy | 栈资源策略，EDF 系统的资源同步协议 |
| DFP | Deadline Floor Protocol | 截止时间下限继承协议 |
| DRR | Deficit Round Robin | 赤字轮询算法，多租户公平调度 |
| SLO Type | SLO类型 | 硬截止、软截止、尽力而为 |
| Thrashing | 调度抖动 | 任务被反复调度-取消的现象 |

---

## 附录 B：配置文件示例

```yaml
# config/scheduler.yaml
scheduler:
  mode: "slo"  # legacy | slo
  
  slo:
    overload_threshold: 0.85
    grace_period_seconds: 30.0
    hard_deadline_margin_seconds: 60.0
    soft_deadline_margin_seconds: 300.0
  
  device:
    max_concurrent_per_device: 3
    load_balance_strategy: "round_robin"  # round_robin | least_loaded
  
  telemetry:
    fusion_enabled: true
    reassessment_interval_ms: 1000
    battery_threshold: 0.15
  
  failover:
    enabled: true
    switchover_timeout_seconds: 5.0
    heartbeat_interval_seconds: 1.0
  
  metrics:
    enabled: true
    export_interval_seconds: 10.0

tenants:
  - id: "warehouse_a"
    weight: 1.0
    priority_override: 5
  - id: "warehouse_b"  
    weight: 0.8
    priority_override: 4
```

---

*报告生成时间: 2026-08-23*  
*版本: v1.0*  
*状态: 初稿，待评审*
