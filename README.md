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
| [`vla-training/`](vla-training/) | **VLA model training** — data collection/conversion, LoRA fine-tuning, evaluation, inference export (skeleton; does not download weights). |
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
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System architecture: dependency map & communication matrix. |
| [`docs/API.md`](docs/API.md) | HTTP (REST/WebSocket) + MQTT interface reference. |
| [`docs/OPERATIONS.md`](docs/OPERATIONS.md) | Deployment & operations guide (Docker, k8s, CI). |
| [`docs/OPERATIONS-ZH.md`](docs/OPERATIONS-ZH.md) | 运维部署指南（中文版）。 |
| [`docs/robot-algorithm-design.md`](docs/robot-algorithm-design.md) | Robot algorithm design overview. |
| [`docs/机器人智能仓储物流系统_完整设计文档.md`](docs/机器人智能仓储物流系统_完整设计文档.md) | 完整系统设计文档（中文）。 |
| [`docs/物流装卸机器人算法系统设计.md`](docs/物流装卸机器人算法系统设计.md) | 物流装卸机器人算法系统设计（中文）。 |
| [`docs/集装箱机器人与散货机器人_技术规格书.md`](docs/集装箱机器人与散货机器人_技术规格书.md) | 集装箱/散货/双臂AGV/实验室装卸机器人技术规格书（含采购附录）。 |

### Algorithm design (`docs/algorithm/`)

| Document | Description |
| --- | --- |
| [`docs/algorithm/README.md`](docs/algorithm/README.md) | Algorithm module index. |
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

| Path | Description |
| --- | --- |
| [`docs/superpowers/specs/`](docs/superpowers/specs/) | Design specs (prototype, RCS motion control, dual-arm AGV, e2e chain, etc.). |
| [`docs/superpowers/instructions/`](docs/superpowers/instructions/) | Hand-off instructions (e.g. `rcs-1-handoff.md`). |
| [`docs/superpowers/plans/`](docs/superpowers/plans/) | Phase/implementation plans & reports. |

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
vla-training/            VLA fine-tuning pipeline (skeleton)
shared/                  MQTT topic + payload contracts (JSON Schema + Python pkg)
deploy/                  docker-compose + k8s manifests
scripts/                 build / verify helper scripts
docs/                    API, operations, design specs
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the dependency map and
communication matrix, and [`docs/API.md`](docs/API.md) for the HTTP/MQTT
interface reference.

---

## License

MIT (see `LICENSE` once published).
