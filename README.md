# 机器人智能仓储物流系统 / Robot Logic System (monorepo)

> Monorepo for a mixed-fleet warehouse control plane: container robots, AGVs,
> and stacker cranes — coordinated by a Robot Control System (RCS), simulated
> end-to-end, with a robot-side application and a VLA training pipeline.

![status](https://img.shields.io/badge/status-prototype-yellow)
![python](https://img.shields.io/badge/python-3.11%2B-blue)
![vue](https://img.shields.io/badge/vue-3.x-green)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

> 🌐 **Language / 语言**：[English](README.md) · [中文](README_CN.md)

---

## What this is

A working end-to-end slice of a warehouse orchestration system, split into four
independent sub-projects plus a shared contract layer:

| Sub-project | Role |
| --- | --- |
| [`rcs/`](rcs/) | **Robot Control System** — device registry, control loop (up to 1 kHz), kinematics, trajectory planning, simulated HAL, REST + WebSocket, and an MQTT adapter. Runs standalone *or* embedded in the simulation backend. |
| [`simulation/`](simulation/) | **Logistics loading/unloading simulation** — FastAPI orchestration backend, Vue 3 + Three.js dashboard, Gazebo/MoveIt ROS 2 packages. |
| [`robot-app/`](robot-app/) | **Robot-side application** — ROS 2 packages (gateway, decision, perception, arm HAL, message contracts) that talk to RCS over MQTT. |
| [`vla-training/`](vla-training/) | **VLA model training** — model adapter registry (Hy-Embodied-0.5-VLA), LoRA fine-tuning, knowledge distillation, evaluation, inference export. |
| [`shared/`](shared/) | **Communication contracts** — MQTT topic + payload definitions shared by `rcs` and `robot-app`. |

The simulation backend and RCS communicate over HTTP (embedded mode) or over an
MQTT broker (standalone mode). The robot side always bridges via MQTT.

---

## Documentation

All design docs, specs, algorithm notes, and paper write-ups live under
[`docs/`](docs/). A full catalog follows.

### Top-level docs

| Document | Description |
| --- | --- |
| [`docs/technical/ARCHITECTURE.md`](docs/technical/ARCHITECTURE.md) | System architecture: dependency map & communication matrix. |
| [`docs/technical/API.md`](docs/technical/API.md) | HTTP (REST/WebSocket) + MQTT interface reference. |
| [`docs/technical/OPERATIONS.md`](docs/technical/OPERATIONS.md) | Deployment & operations guide (Docker, k8s, CI). |
| [`docs/technical/OPERATIONS-ZH.md`](docs/technical/OPERATIONS-ZH.md) | 运维部署指南（中文版）。 |
| [`docs/algorithm/robot-algorithm-design.md`](docs/algorithm/robot-algorithm-design.md) | Robot algorithm design overview. |
| [`docs/机器人智能仓储物流系统_完整设计文档.md`](docs/机器人智能仓储物流系统_完整设计文档.md) | 完整系统设计文档（中文）。 |
| [`docs/物流装卸机器人算法系统设计.md`](docs/物流装卸机器人算法系统设计.md) | 物流装卸机器人算法系统设计（中文）。 |
| [`docs/集装箱机器人与散货机器人_技术规格书.md`](docs/集装箱机器人与散货机器人_技术规格书.md) | 集装箱/散货/双臂AGV/实验室装卸机器人技术规格书（含采购附录）。 |
| [`docs/装卸场景与机器人适配选型.md`](docs/装卸场景与机器人适配选型.md) | 装卸场景分析与机器人适配选型（中文）。 |

### Algorithm design (`docs/algorithm/`)

| Document | Description |
| --- | --- |
| [`docs/algorithm/README.md`](docs/algorithm/README.md) | Algorithm module index. |
| [`docs/algorithm/robot-algorithm-design.md`](docs/algorithm/robot-algorithm-design.md) | Robot algorithm design (consolidated). |
| [`docs/algorithm/01-overview.md`](docs/algorithm/01-overview.md) | Overview. |
| [`docs/algorithm/02-motion-planning.md`](docs/algorithm/02-motion-planning.md) | Motion planning. |
| [`docs/algorithm/03-perception.md`](docs/algorithm/03-perception.md) | Perception. |
| [`docs/algorithm/04-task-scheduling.md`](docs/algorithm/04-task-scheduling.md) | Task scheduling. |
| [`docs/algorithm/05-deployment.md`](docs/algorithm/05-deployment.md) | Deployment. |

### Technical design (`docs/technical/`)

| Document | Description |
| --- | --- |
| [`docs/technical/container-robot/集装箱机器人技术设计方案_V1.0.md`](docs/technical/container-robot/集装箱机器人技术设计方案_V1.0.md) | 集装箱机器人技术设计方案 V1.0. |
| [`docs/technical/bulk-cargo-robot/散货机器人技术设计方案_V1.0.md`](docs/technical/bulk-cargo-robot/散货机器人技术设计方案_V1.0.md) | 散货机器人技术设计方案 V1.0. |

### VLA paper studies (`docs/paper/`)

Each paper has an English version and a Chinese version (`-CN`).

| Paper | English | 中文 |
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

### Engineering records (`docs/superpowers/`)

#### Design specs (`specs/`)

| Document | Description |
| --- | --- |
| [`2026-07-23-robot-logic-prototype-design.md`](docs/superpowers/specs/2026-07-23-robot-logic-prototype-design.md) | Prototype design spec. |
| [`2026-07-23-robot-logic-phase5-design.md`](docs/superpowers/specs/2026-07-23-robot-logic-phase5-design.md) | Phase 5 design spec. |
| [`2026-07-24-rcs-1-motion-control-design.md`](docs/superpowers/specs/2026-07-24-rcs-1-motion-control-design.md) | RCS-1 motion control design. |
| [`2026-08-07-four-subproject-split-design.md`](docs/superpowers/specs/2026-08-07-four-subproject-split-design.md) | Four sub-project split design. |
| [`2026-08-09-e2e-motion-chain-design.md`](docs/superpowers/specs/2026-08-09-e2e-motion-chain-design.md) | End-to-end motion chain design. |
| [`2026-08-09-loading-robot-dual-arm-agv-design.md`](docs/superpowers/specs/2026-08-09-loading-robot-dual-arm-agv-design.md) | Loading robot dual-arm AGV design. |
| [`2026-08-09-phase2-perception-navigation-design.md`](docs/superpowers/specs/2026-08-09-phase2-perception-navigation-design.md) | Phase 2 perception & navigation design. |
| [`2026-08-09-technology-roadmap-phase1-design.md`](docs/superpowers/specs/2026-08-09-technology-roadmap-phase1-design.md) | Technology roadmap Phase 1 design. |
| [`2026-08-14-top3-rcs-robotapp-design.md`](docs/superpowers/specs/2026-08-14-top3-rcs-robotapp-design.md) | Top-3 RCS & robot-app design. |
| [`2026-08-14-top3-simulation-design.md`](docs/superpowers/specs/2026-08-14-top3-simulation-design.md) | Top-3 simulation design. |

#### Plans & reports (`plans/`)

| Document | Description |
| --- | --- |
| [`2026-07-23-robot-logic-prototype.md`](docs/superpowers/plans/2026-07-23-robot-logic-prototype.md) | Prototype implementation plan. |
| [`2026-07-24-phase5-m3-gazebo-moveit-report.md`](docs/superpowers/plans/2026-07-24-phase5-m3-gazebo-moveit-report.md) | Phase 5 Gazebo/MoveIt report. |
| [`2026-07-24-rcs-1-motion-control.md`](docs/superpowers/plans/2026-07-24-rcs-1-motion-control.md) | RCS-1 motion control plan. |
| [`2026-08-09-e2e-motion-chain.md`](docs/superpowers/plans/2026-08-09-e2e-motion-chain.md) | E2E motion chain implementation plan. |
| [`2026-08-09-loading-robot-dual-arm-agv.md`](docs/superpowers/plans/2026-08-09-loading-robot-dual-arm-agv.md) | Dual-arm AGV implementation plan. |
| [`2026-08-09-phase1-dual-arm-implementation.md`](docs/superpowers/plans/2026-08-09-phase1-dual-arm-implementation.md) | Phase 1 dual-arm implementation plan. |
| [`2026-08-09-phase2-perception-navigation.md`](docs/superpowers/plans/2026-08-09-phase2-perception-navigation.md) | Phase 2 perception & navigation plan. |
| [`2026-08-14-top3-rcs-robotapp-plan.md`](docs/superpowers/plans/2026-08-14-top3-rcs-robotapp-plan.md) | Top-3 RCS & robot-app plan. |
| [`2026-08-14-top3-simulation-plan.md`](docs/superpowers/plans/2026-08-14-top3-simulation-plan.md) | Top-3 simulation plan. |

#### Hand-off instructions

| Path | Description |
| --- | --- |
| [`docs/superpowers/instructions/rcs-1-handoff.md`](docs/superpowers/instructions/rcs-1-handoff.md) | RCS-1 hand-off instructions. |

---

## Quick start (simulation backend, embedded RCS)

```bash
# Backend (terminal 1) — RCS is embedded by default (RCS_EMBEDDED=true)
cd simulation/backend
python -m venv .venv && . .venv/Scripts/activate
pip install -r requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Frontend (terminal 2)
cd simulation/frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Open <http://localhost:5173>.

### Quick start (standalone RCS + MQTT)

```bash
# Broker
docker compose -f deploy/docker-compose.yml up -d mosquitto

# RCS as its own service on :8100
cd rcs
pip install -r requirements.txt
RCS_MQTT_ENABLED=true uvicorn rcs.app:create_app --factory --host 127.0.0.1 --port 8100

# Point the simulation backend at it (optional)
cd simulation/backend
RCS_EMBEDDED=false RCS_SERVICE_URL=http://127.0.0.1:8100 uvicorn backend.main:app --port 8000
```

---

## Verifying the split

```bash
bash scripts/verify_split.sh            # runs all sub-project test suites + contract checks
bash scripts/verify_split.sh --no-mqtt  # same, skipping the live-broker round trip
```

---

## Repository layout

```
rcs/                     RCS robot control system (standalone + embedded)
simulation/              simulation backend + Vue frontend + ROS2 workspace
robot-app/               robot-side ROS2 packages (gateway, decision, perception, HAL)
vla-training/            VLA fine-tuning pipeline (model adapters + distillation)
shared/                  MQTT topic + payload contracts (JSON Schema + Python pkg)
deploy/                  docker-compose + k8s manifests
docs/                    architecture, API, operations, algorithm, paper studies, design specs
```

See [`docs/technical/ARCHITECTURE.md`](docs/technical/ARCHITECTURE.md) for the dependency map and
communication matrix, and [`docs/technical/API.md`](docs/technical/API.md) for the HTTP/MQTT
interface reference.

---

## License

MIT (see `LICENSE` once published).
