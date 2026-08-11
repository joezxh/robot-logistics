# robot-logic 智能仓储物流机器人逻辑系统

[![monorepo](https://img.shields.io/badge/structure-monorepo-blue)](https://en.wikipedia.org/wiki/Monorepo)
[![rcs](https://img.shields.io/badge/rcs-FastAPI-009688)](rcs/)
[![sim](https://img.shields.io/badge/sim-FastAPI%2BVue-42A5F5)](simulation/)
[![ros2](https://img.shields.io/badge/ros2-Humble-222)](robot-app/)
[![vla](https://img.shields.io/badge/vla-training-skeleton-orange)](vla-training/)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

> 🌐 **Language / 语言**：[English](README.md) · [中文](README_CN.md)

---

## 项目简介

`robot-logic` 是一个智能仓储物流机器人逻辑系统，将仿真、机器人控制与 VLA（视觉-语言-动作）训练整合在一个仓库中。从高层次看：

- **仿真侧（simulation）** 运行一个 FastAPI 后端（业务编排/调度）与 Vue 前端。
- **机器人侧（robot-app）** 运行 ROS2，包含网关、决策、感知与硬件抽象层（HAL）包。
- **RCS（机器人控制系统）** 是协调仿真与机器人之间的运动控制与状态同步的独立（或内嵌）服务。
- **VLA 训练（vla-training）** 是一个微调流水线骨架，用于训练/适配机器人策略模型。
- **共享层（shared）** 通过 JSON Schema + Python 包定义 MQTT 主题与负载契约，确保各端契约一致。

机器人侧始终通过 **MQTT** 与仿真/RCS 桥接。

---

## 文档目录

所有设计文档、规格书、算法笔记与论文研读均位于 [`docs/`](docs/) 目录下，完整目录如下。

### 顶层文档

| 文档 | 说明 |
| --- | --- |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | 系统架构：依赖关系图与通信矩阵。 |
| [`docs/API.md`](docs/API.md) | HTTP（REST/WebSocket）+ MQTT 接口参考。 |
| [`docs/OPERATIONS.md`](docs/OPERATIONS.md) | 部署与运维指南（Docker、k8s、CI）。 |
| [`docs/OPERATIONS-ZH.md`](docs/OPERATIONS-ZH.md) | 运维部署指南（中文版）。 |
| [`docs/robot-algorithm-design.md`](docs/robot-algorithm-design.md) | 机器人算法设计总览。 |
| [`docs/机器人智能仓储物流系统_完整设计文档.md`](docs/机器人智能仓储物流系统_完整设计文档.md) | 完整系统设计文档。 |
| [`docs/物流装卸机器人算法系统设计.md`](docs/物流装卸机器人算法系统设计.md) | 物流装卸机器人算法系统设计。 |
| [`docs/集装箱机器人与散货机器人_技术规格书.md`](docs/集装箱机器人与散货机器人_技术规格书.md) | 集装箱/散货/双臂AGV/实验室装卸机器人技术规格书（含采购附录）。 |

### 算法设计（`docs/algorithm/`）

| 文档 | 说明 |
| --- | --- |
| [`docs/algorithm/README.md`](docs/algorithm/README.md) | 算法模块索引。 |
| [`docs/algorithm/01-overview.md`](docs/algorithm/01-overview.md) | 总览。 |
| [`docs/algorithm/02-motion-planning.md`](docs/algorithm/02-motion-planning.md) | 运动规划。 |
| [`docs/algorithm/03-perception.md`](docs/algorithm/03-perception.md) | 感知。 |
| [`docs/algorithm/04-task-scheduling.md`](docs/algorithm/04-task-scheduling.md) | 任务调度。 |
| [`docs/algorithm/05-deployment.md`](docs/algorithm/05-deployment.md) | 部署。 |

### 技术设计（`docs/technical/`）

| 文档 | 说明 |
| --- | --- |
| [`docs/technical/container-robot/集装箱机器人技术设计方案_V1.0.md`](docs/technical/container-robot/集装箱机器人技术设计方案_V1.0.md) | 集装箱机器人技术设计方案 V1.0。 |
| [`docs/technical/bulk-cargo-robot/散货机器人技术设计方案_V1.0.md`](docs/technical/bulk-cargo-robot/散货机器人技术设计方案_V1.0.md) | 散货机器人技术设计方案 V1.0。 |

### VLA 论文研读（`docs/paper/`）

每篇论文均有英文版与中文版（`-CN`）。

| 论文 | 英文 | 中文 |
| --- | --- | --- |
| AdaJEPA | [`adajepa.md`](docs/paper/adajepa.md) | [`adajepa-CN.md`](docs/paper/adajepa-CN.md) |
| CogACT | [`cogact.md`](docs/paper/cogact.md) | [`cogact-CN.md`](docs/paper/cogact-CN.md) |
| Diffusion Policy | [`diffusion-policy.md`](docs/paper/diffusion-policy.md) | [`diffusion-policy-CN.md`](docs/paper/diffusion-policy-CN.md) |
| Embodied-R1 | [`embodied-r1.md`](docs/paper/embodied-r1.md) | [`embodied-r1-CN.md`](docs/paper/embodied-r1-CN.md) |
| Octo | [`octo.md`](docs/paper/octo.md) | [`octo-CN.md`](docs/paper/octo-CN.md) |
| OpenVLA | [`openvla.md`](docs/paper/openvla.md) | [`openvla-CN.md`](docs/paper/openvla-CN.md) |
| Patch Policy | [`patch-policy.md`](docs/paper/patch-policy.md) | [`patch-policy-CN.md`](docs/paper/patch-policy-CN.md) |
| R3M | [`r3m.md`](docs/paper/r3m.md) | [`r3m-CN.md`](docs/paper/r3m-CN.md) |
| ReConVLA | [`reconvla.md`](docs/paper/reconvla.md) | [`reconvla-CN.md`](docs/paper/reconvla-CN.md) |
| RoboVista | [`robovista.md`](docs/paper/robovista.md) | [`robovista-CN.md`](docs/paper/robovista-CN.md) |
| RT-2 | [`rt2.md`](docs/paper/rt2.md) | [`rt2-CN.md`](docs/paper/rt2-CN.md) |
| Scaling Diffusion Policy | [`scaling-diffusion-policy.md`](docs/paper/scaling-diffusion-policy.md) | [`scaling-diffusion-policy-CN.md`](docs/paper/scaling-diffusion-policy-CN.md) |
| TinyVLA | [`tinyvla.md`](docs/paper/tinyvla.md) | [`tinyvla-CN.md`](docs/paper/tinyvla-CN.md) |
| V-JEPA2 | [`v-jepa2.md`](docs/paper/v-jepa2.md) | [`v-jepa2-CN.md`](docs/paper/v-jepa2-CN.md) |
| VLA Survey | [`vla-survey.md`](docs/paper/vla-survey.md) | [`vla-survey-CN.md`](docs/paper/vla-survey-CN.md) |
| W2VLA | [`w2vla.md`](docs/paper/w2vla.md) | [`w2vla-CN.md`](docs/paper/w2vla-CN.md) |
| WSA1 | [`wsa1.md`](docs/paper/wsa1.md) | [`wsa1-CN.md`](docs/paper/wsa1-CN.md) |

### 工程记录（`docs/superpowers/`）

| 路径 | 说明 |
| --- | --- |
| [`docs/superpowers/specs/`](docs/superpowers/specs/) | 设计规格（原型、RCS 运动控制、双臂 AGV、端到端链路等）。 |
| [`docs/superpowers/instructions/`](docs/superpowers/instructions/) | 交接说明（如 `rcs-1-handoff.md`）。 |
| [`docs/superpowers/plans/`](docs/superpowers/plans/) | 阶段/实施计划与报告。 |

---

## 快速开始（仿真后端 + 内嵌 RCS）

```bash
# 安装
pip install -e simulation/backend -e rcs -e shared/python -e vla-training/src

# 内嵌模式（推荐先跑通）：仿真后端自带 RCS
cd simulation/backend
RCS_EMBEDDED=true uvicorn backend.main:app --port 8000

# 前端
cd simulation/frontend
npm install && npm run dev
```

### 快速开始（独立 RCS + MQTT）

```bash
# 消息代理
docker compose -f deploy/docker-compose.yml up -d mosquitto

# 将 RCS 作为独立服务运行在 :8100
cd rcs
pip install -r requirements.txt
RCS_MQTT_ENABLED=true uvicorn rcs.app:create_app --factory --host 127.0.0.1 --port 8100

# 让仿真后端指向它（可选）
cd simulation/backend
RCS_EMBEDDED=false RCS_SERVICE_URL=http://127.0.0.1:8100 uvicorn backend.main:app --port 8000
```

---

## 验证拆分结果

```bash
bash scripts/verify_split.sh            # 运行各子项目测试套件 + 契约检查
bash scripts/verify_split.sh --no-mqtt  # 同上，但跳过实时代理回环测试
```

---

## 仓库结构

```
rcs/                     RCS 机器人控制系统（独立 + 内嵌）
simulation/              仿真后端 + Vue 前端 + ROS2 工作空间
robot-app/               机器人侧 ROS2 包（网关、决策、感知、HAL）
vla-training/            VLA 微调流水线（骨架）
shared/                  MQTT 主题 + 负载契约（JSON Schema + Python 包）
deploy/                  docker-compose + k8s 清单
scripts/                 构建 / 验证辅助脚本
docs/                    API、运维、设计规格
```

详见 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) 了解系统结构，[`docs/API.md`](docs/API.md) 了解接口契约。
