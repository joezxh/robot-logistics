# Architecture — Robot Logic Monorepo

This document describes the four sub-projects, their dependency directions, and
the communication matrix between them. It is the companion to the
[four-subproject split design spec](superpowers/specs/2026-08-07-four-subproject-split-design.md).

## Dependency direction (enforced)

```
        shared/  (zero-dep contracts)
          ▲   ▲
          │   │
   rcs/ ──┘   └── robot-app/
     ▲
     │ (embedded via router, or standalone via HTTP/MQTT)
     │
 simulation/ ──────────────┐
                            │ (colcon underlay overlay)
                     robot-app/robot_arm_hal

 vla-training/  (standalone pipeline, deploys artifacts to robot-app/robot_decision)
```

Rules:

- `shared/` depends on **neither** `rcs/` nor `robot-app/`. It is pure
  data — JSON Schemas + a dependency-free Python package.
- `rcs/` must **not** import the simulation backend. It owns its own
  `config.py` / `security.py`.
- `robot-app/` depends on `shared/` for wire contracts, and on
  `robot_arm_hal` (provided as a colcon underlay by the simulation workspace
  when building the robot workspace, or vice-versa).
- `vla-training/` is decoupled; it only emits inference artifacts consumed by
  `robot-app/robot_decision`.

These directions are checked by `scripts/verify_split.sh`.

## Sub-project responsibilities

### `rcs/` — Robot Control System

- **Core**: device registry, control loop (`loop.py`), controllers
  (arm/agv/stacker), kinematics + planning (`planning/`), simulated HAL
  (`hal/`), state + event types (`state/`, `events.py`).
- **Dual mode**:
  - *Embedded* — the simulation backend mounts `rcs.router()` under
    `/api/rcs` and drives `rcs.lifespan()`.
  - *Standalone* — `rcs.app.create_app()` builds a self-contained FastAPI app
    on its own port (default `8100`).
- **MQTT adapter** (`rcs/mqtt/`): republishes `StateStream` (downsampled, QoS 0)
  and `EventBus` alerts (QoS 1); subscribes command topics (QoS 1) and routes
  them through the **same** `on_command()` path as REST. Never touches the
  1 kHz tick.

### `simulation/` — Logistics simulation

- **backend/**: FastAPI orchestration — devices, tasks, sites, alerts, logs,
  metrics (SSE). Embeds RCS when `RCS_EMBEDDED=true`.
- **frontend/**: Vue 3 + Vite + Three.js dashboard. Calls `/api/*` and `/ws`
  relative paths — unchanged by the split.
- **ros2_ws/**: `robot_bringup` (depends on `robot_arm_hal` via underlay) and
  `robot_moveit_config`.

### `robot-app/` — Robot-side application

- **robot_gateway**: MQTT ↔ ROS 2 bridge. Receives commands (QoS 1) from RCS,
  forwards to local ROS 2 graph; publishes state (QoS 0) and telemetry (QoS 0).
  Buffers while the broker is unreachable.
- **robot_msgs**: local message contracts mirroring `shared/contracts`.
- **robot_decision / robot_perception / robot_arm_hal**: behavior, sensing, and
  the arm hardware-abstraction layer (the shared HAL used by the simulation
  workspace).

### `vla-training/` — VLA pipeline (skeleton)

Data collection → conversion (RLDS/LeRobot-style) → LoRA fine-tune →
evaluation → inference export. Declares `torch`/`transformers`/`peft` but does
**not** download weights or run training. Export target: `robot-app/robot_decision`.

### `shared/` — Communication contracts

- `contracts/*.schema.json`: command / state / alert / telemetry JSON Schemas.
- `python/robot_contracts/`: topic builders + Pydantic payload models, kept in
  lock-step with the schemas. Imported by both `rcs/` and `robot-app/`.

## Communication matrix

| Channel | From → To | Topic | QoS | Notes |
| --- | --- | --- | --- | --- |
| Command | RCS → robot | `rcs/{device_id}/command` | 1 | validated, queued, back-pressured |
| State | robot/RCS → broker | `rcs/{device_id}/state` | 0 | downsampled (default 10 Hz) |
| Alert | RCS → broker | `rcs/{device_id}/alert` | 1 | `EventBus` events |
| Telemetry | robot → broker | `robot/{device_id}/telemetry` | 0 | battery/temp/connectivity |

REST surface (embedded under `/api/rcs`, standalone on `:8100`):

- `GET  /api/rcs/registry`
- `POST /api/rcs/{device_id}/command`
- `GET  /api/rcs/{device_id}/state`
- `POST /api/rcs/{device_id}/estop` / `clear_estop`
- `GET  /api/rcs/_health` and `GET /health` (standalone only)

See [`API.md`](API.md) for full request/response shapes.
