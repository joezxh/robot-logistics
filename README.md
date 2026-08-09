# 机器人智能仓储物流系统 / Robot Logic System (monorepo)

> Monorepo for a mixed-fleet warehouse control plane: container robots, AGVs,
> and stacker cranes — coordinated by a Robot Control System (RCS), simulated
> end-to-end, with a robot-side application and a VLA training pipeline.

![status](https://img.shields.io/badge/status-prototype-yellow)
![python](https://img.shields.io/badge/python-3.11%2B-blue)
![vue](https://img.shields.io/badge/vue-3.x-green)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

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
