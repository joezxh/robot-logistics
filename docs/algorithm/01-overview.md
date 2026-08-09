# 系统架构总览

> 本章介绍物流装卸机器人算法系统的整体架构、模块职责和参数化配置体系。

---

## 1.1 设计理念

本算法系统采用**通用化设计**，不区分集装箱机器人与散货机器人类型，通过统一的算法框架和可配置参数适配不同负载、不同精度要求的作业场景。

**核心设计原则：**

- 统一的数据结构和接口定义
- 基于参数的差异化配置（不写分支代码）
- 模块化架构，支持灵活组合
- 支持从轻载协作机器人到重载工业机器人的全谱系覆盖

---

## 1.2 系统架构图

```mermaid
graph TB
    subgraph "任务层"
        T1[任务调度器<br/>WMS/MES接口]
        T2[监控运维层<br/>数据采集/日志]
    end
    
    subgraph "决策层"
        D1[任务分解器]
        D2[任务序列优化器]
        D3[参数化策略引擎]
    end
    
    subgraph "执行层"
        P1[运动规划器]
        P2[环境感知器]
        P3[末端控制器]
    end
    
    subgraph "硬件层"
        H1[工业机器人控制器<br/>EtherCAT]
        H2[视觉传感器<br/>USB3/Gige]
        H3[末端执行器<br/>CAN/Modbus]
    end
    
    T1 --> D1
    T2 --> D2
    D1 --> D2
    D2 --> D3
    D3 --> P1
    D3 --> P2
    D3 --> P3
    
    P1 --> H1
    P2 --> H2
    P3 --> H3
```

**架构说明：**

| 层级 | 组件 | 功能 | 部署位置 |
|------|------|------|---------|
| 任务层 | 任务调度器 | WMS/MES接口、批次任务管理 | 云端 |
| 任务层 | 监控运维 | 数据采集、日志记录 | 边缘 |
| 决策层 | 任务分解器 | 高层任务分解为动作序列 | 云端 |
| 决策层 | 序列优化器 | 任务执行顺序优化 | 云端 |
| 决策层 | 策略引擎 | 参数化算法配置适配 | 云端+边缘 |
| 执行层 | 运动规划器 | 路径规划、轨迹优化 | 边缘 |
| 执行层 | 环境感知器 | 目标检测、姿态估计 | 边缘+云端 |
| 执行层 | 末端控制器 | 力位混合控制 | 边缘 |

---

## 1.3 模块职责总览

| 模块名称 | 位置 | 功能职责 | 实时性要求 |
|---------|------|---------|-----------|
| **运动规划器** | 边缘 | 全局路径+局部优化+轨迹插补 | <2s规划 |
| **目标检测** | 边缘 | 通用物体检测（闭集+开集） | <50ms |
| **6-DoF姿态估计** | 云端 | 物体精确位姿 | <80ms |
| **抓取姿态规划** | 云端 | 最优抓取计算 | <100ms |
| **任务调度器** | 云端 | 批次优化 | 秒级 |

---

## 1.4 参数化配置体系

### RobotConfig 数据结构

```python
@dataclass
class RobotConfig:
    """机器人通用配置"""
    num_joints: int = 6                    # 关节数量（6或7）
    payload_kg: float = 25.0               # 负载(kg)
    
    # 精度参数
    position_accuracy_mm: float = 0.5      # 定位精度(mm)
    repeatability_mm: float = 0.1          # 重复精度(mm)
    
    # 速度参数
    max_velocity_mps: float = 3.0          # 最大线速度(m/s)
    max_acceleration_mps2: float = 15.0    # 最大加速度(m/s²)
    
    # 控制频率
    control_frequency_hz: int = 250         # 控制频率
    
    # 工作空间
    workspace_radius_m: float = 2.0         # 工作半径(m)
```

### 参数派生机制

```python
class PlanningConfig:
    """规划算法配置"""
    max_iterations: int = 7000
    step_size: float = 0.08
    rewire_radius: float = 0.4
    smoothness_weight: float = 0.5
    collision_weight: float = 1.5
    interpolation_mode: str = "s_curve"
    
    @classmethod
    def from_robot_config(cls, robot_config: RobotConfig) -> PlanningConfig:
        # 高精度场景
        if robot_config.position_accuracy_mm < 1.0:
            return cls(
                max_iterations=10000,
                step_size=0.05,
                rewire_radius=0.3,
                smoothness_weight=0.6,
                collision_weight=2.0,
                interpolation_mode="s_curve"
            )
        # 高速场景
        elif robot_config.max_velocity_mps > 2.0:
            return cls(
                max_iterations=5000,
                step_size=0.1,
                rewire_radius=0.5,
                smoothness_weight=0.3,
                collision_weight=1.0,
                interpolation_mode="linear"
            )
        # 默认场景
        else:
            return cls(
                max_iterations=7000,
                step_size=0.08,
                rewire_radius=0.4,
                smoothness_weight=0.5,
                collision_weight=1.5,
                interpolation_mode="s_curve"
            )
```

### 场景配置对照表

| 场景 | 定位精度 | 最大速度 | 规划迭代 | 插补模式 |
|------|---------|---------|---------|---------|
| 高精度分拣 | <1mm | <2m/s | 10000次 | S曲线 |
| 高速搬运 | 1-2mm | >2m/s | 5000次 | 线性 |
| 通用场景 | 0.5mm | 3m/s | 7000次 | S曲线 |

---

## 1.5 云边协同架构

```mermaid
flowchart TB
    subgraph "边缘服务器"
        E1[RGB-D相机] --> E2[视觉预处理]
        E2 --> E3[目标检测]
        E3 --> E4[检测融合]
        
        subgraph "检测模块"
            E3a[YOLOv8闭集检测<br/>高准确率]
            E3b[YOLO-World开集检测<br/>零样本能力]
            E3a --> E4
            E3b --> E4
        end
    end
    
    E4 -->|检测结果| C1[云端服务]
    
    subgraph "云端服务器"
        C1 --> C2[6-DoF姿态估计]
        C2 --> C3[抓取姿态规划]
        C3 --> C4[返回抓取姿态]
    end
    
    C4 -->|执行指令| Robot[机器人执行]
    
    E4 -->|本地备选| LocalGrasp[本地抓取规划]
    LocalGrasp --> Robot
```

---

## 1.6 完整规划流程

```mermaid
flowchart LR
    A[MotionPlanRequest] --> B[全局规划]
    B --> C{规划成功?}
    C -->|否| D[返回失败]
    C -->|是| E[局部优化]
    E --> F[轨迹插补]
    F --> G[JointState序列]
    G --> H[MotionPlanResponse]
    
    subgraph "全局规划"
        B1[输入start, goal]
        B2[碰撞检测]
        B3[RRT*采样]
        B4[重连线/重布线]
        B5[返回Trajectory]
        B1 --> B2 --> B3 --> B4 --> B5
    end
    
    subgraph "局部优化"
        E1[输入Trajectory]
        E2[计算代价梯度]
        E3[迭代优化]
        E4[限位约束]
        E5[返回优化轨迹]
        E1 --> E2 --> E3 --> E4 --> E5
    end
    
    subgraph "轨迹插补"
        F1[输入Trajectory]
        F2[选择插补模式]
        F3[时间参数化]
        F4[位置插值]
        F5[速度限制]
        F6[输出JointState]
        F1 --> F2 --> F3 --> F4 --> F5 --> F6
    end
```

---

**下一章**：[运动规划算法系统](02-motion-planning.md)
