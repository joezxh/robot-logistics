# 物流装卸机器人算法系统设计

> **文档版本**：V2.1  
> **编制日期**：2026年7月21日  
> **最后更新**：2026年8月9日（Phase 2 感知与导航 Task 1-6 完成）  
> **文档类型**：算法技术设计  
> **适用范围**：物流装卸机器人通用算法系统

---

## 文档结构

本文档采用模块化结构，按功能拆分为多个文件：

| 文件 | 内容 | 实现状态 |
|------|------|----------|
| [01-overview.md](01-overview.md) | 系统架构、模块职责、参数配置 | ✅ 目标架构 |
| [02-motion-planning.md](02-motion-planning.md) | 运动规划算法系统（共用基础、全局规划、局部优化、轨迹插补） | ✅ 设计完成；BaseExecutor 已集成 Nav2 |
| [03-perception.md](03-perception.md) | 环境感知系统（视觉预处理、目标检测、云端感知） | 🔧 Phase 2 合成传感器 + 7 步管线已实现 |
| [04-task-scheduling.md](04-task-scheduling.md) | 任务调度与决策 | ✅ TaskCoordinator 9 阶段 FSM 已实现 |
| [05-deployment.md](05-deployment.md) | 部署配置与性能指标 | 🔧 Docker + FastAPI 部署已实现 |

---

## 快速导航

### 运动规划算法

| 章节 | 算法 | 核心原理 |
|------|------|---------|
| 2.1 共用基础层 | 数据结构 | JointState, Pose6D, Trajectory, PlanningConfig |
| 2.2 全局规划 | RRT* | 基于随机采样的最优路径规划 |
| 2.3 局部优化 | 梯度下降/随机优化 | 轨迹平滑、无碰撞优化 |
| 2.4 轨迹插补 | S曲线/线性插补 | 时间参数化、位置插值 |

### 环境感知算法

| 章节 | 算法 | 核心原理 |
|------|------|---------|
| 3.1 云边协同 | 边缘+云端 | 感知能力分层 |
| 3.2 视觉预处理 | 双边滤波、体素降采样 | 深度图处理、点云滤波 |
| 3.3 目标检测 | YOLOv8 + YOLO-World | 闭集+开集混合检测 |
| 3.4 云端感知 | CosyPose + GraspNet | 6-DoF姿态估计、抓取规划 |

### 任务调度算法

| 章节 | 算法 | 核心原理 |
|------|------|---------|
| 3.5 任务调度 | Kahn拓扑排序 + 优先级队列 | 依赖解析、批次优化 |

---

## 核心设计原则

1. **通用化设计**：不区分集装箱机器人与散货机器人类型
2. **参数化配置**：通过统一参数适配不同场景
3. **模块化架构**：支持灵活组合
4. **云边协同**：边缘实时、云端精准

---

## 当前实现状态（截至 2026-08-09）

本算法系统的软件实现采用 **四子项目 Monorepo** 架构：

| 子项目 | 职责 | 测试数 |
|--------|------|--------|
| `shared/` | 零依赖数据契约（JSON Schema + Python 包） | — |
| `rcs/` | 机器人控制系统（设备注册、控制循环、运动学、MQTT） | 85 |
| `simulation/` | 物流仿真（FastAPI 后端 + Vue 3 前端 + 合成传感器） | 89 |
| `robot-app/` | 机器人端应用（ROS 2 节点：网关、决策、感知、HAL） | 43 + 44 + 7 |
| `vla-training/` | VLA 模型训练管线 | 40 |

**Phase 1 已完成**：双臂 AGV 装卸机器人 — TaskCoordinator 9 阶段 FSM、BaseExecutor（Nav2）、ArmExecutor（MoveIt）、HugController（双臂同步抱夹）、SafetyMonitor。

**Phase 2 已实现（Task 1-6）**：
- 合成传感器：PointCloudGenerator（深度相机模拟）、LaserScanGenerator（2D LIDAR）
- 感知管线：PointCloudProcessor 7 步管线（PassThrough → VoxelGrid → StatisticalOutlier → RANSAC → EuclideanCluster(Union-Find) → BBox → Pose）
- 导航集成：BaseExecutor 重构为 Nav2 NavigateToPose action client
- SSE 端点：`/api/devices/{id}/detections`（10Hz）、`/nav_path`（1Hz）

**测试总计**：308 tests，0 failures。

---

**相关文档**：[机器人技术规格书](../集装箱机器人与散货机器人_技术规格书.md) | [系统架构](../ARCHITECTURE.md)
