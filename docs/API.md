# API Reference

> Reference for the robot-logic prototype HTTP API. The default base URL is
> `http://localhost:8000`. All endpoints are JSON unless noted; SSE endpoints
> return `text/event-stream`.
>
> **Last updated**: 2026-08-09 — Phase 1 (dual-arm AGV loading robot) complete.

## Conventions

| Header | Required | Notes |
| --- | --- | --- |
| `Content-Type: application/json` | for `POST` bodies | accepted everywhere |
| `X-API-Key` | only when auth enabled | see [Security](#security) |
| `Accept: text/event-stream` | SSE | optional |

Rate limits (per IP, sliding 60s window) apply to mutating endpoints when
`api_auth_enabled=true` and `rate_limit_max` is exceeded.

Common error shapes:

```json
{ "detail": "human-readable reason" }
```

---

## Health & metadata

### `GET /`

Liveness + version banner.

```bash
curl http://localhost:8000/
```

```json
{ "message": "Robot Logic System API", "version": "1.0.0" }
```

### `GET /api/status`

Runtime summary (uptime, device count, queued tasks).

```bash
curl http://localhost:8000/api/status
```

```json
{
  "running": true,
  "uptime_seconds": 42.0,
  "device_count": 5,
  "task_count": 3,
  "queue_size": 3
}
```

### `GET /api/metrics`

Business KPIs derived from in-memory state. Cheap, no auth.

```json
{
  "throughput_per_hour": 51,
  "success_rate": 75.0,
  "active_tasks": 0,
  "energy_kwh": 0.03
}
```

### `GET /metrics`

Prometheus text exposition (no Prometheus client required). Counter
`robot_logic_api_hits`, gauges for tasks per status and alerts per
severity, and a tick-latency summary.

```
# TYPE robot_logic_api_hits counter
robot_logic_api_hits 42.0
# TYPE robot_logic_tasks_pending gauge
robot_logic_tasks_pending 7
# TYPE robot_logic_alerts_warning gauge
robot_logic_alerts_warning 1
```

---

## Devices

### `GET /api/devices`

Snapshot list of every simulated device, including live position, battery,
and current task.

```bash
curl http://localhost:8000/api/devices
```

```json
[
  {
    "device_id": "agv-01",
    "device_type": "agv",
    "name": "AGV 转运车",
    "position": [0.04, 0.0, 0.02],
    "route": [[-5.0, 0.0, -1.0], [0.0, 0.0, 0.0], [5.0, 0.0, 2.0]],
    "speed": 1.2,
    "status": "running",
    "progress": 0.5,
    "battery": 99.56,
    "current_task": "task-1215cd23"
  }
]
```

`status` is one of `idle | running | charging | fault`.

**Default devices**:

| device_id | device_type | name | position |
|-----------|-------------|------|----------|
| robot-01 | container_robot | 集装箱装卸机器人 | [-8, 0, 2] |
| loader-01 | loading_robot | 双臂AGV装卸机器人 | [-3, 0, 0] |
| agv-01 | agv | AGV 转运车 | [-5, 0, -1] |
| agv-02 | agv | AGV 转运车 2 | [1, 0, 2] |
| stacker-01 | stacker | 立库堆垛机 | [7, 0, 0] |

### `GET /api/stats`

Detailed per-status / per-type task counts plus uptime.

```json
{
  "by_status": {"pending": 1, "running": 2, "completed": 0},
  "by_type": {"dock_loading": 1, "agv_transport": 1, "warehouse_storage": 1},
  "per_device_battery": {"robot-01": 99.5, "loader-01": 100.0, "agv-01": 98.2},
  "uptime_seconds": 42.0,
  "running": true,
  "reverted_count": 0
}
```

---

## Tasks

### `GET /api/tasks`

List every task known to the runtime, including `completed` and `reverted`
historical records.

### `POST /api/tasks`

Create a task.

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H 'Content-Type: application/json' \
  -d '{"type":"agv_transport","description":"smoke","priority":3,"device_id":"agv-02"}'
```

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `type` | string | yes | one of `dock_loading`, `agv_transport`, `warehouse_storage`, `container_unload`, or any custom string |
| `description` | string | no | human label |
| `priority` | int | no | `1` critical → `4` low (default 3) |
| `device_id` | string | yes | must match `GET /api/devices` |

Response `200`:

```json
{
  "task_id": "task-b769db3e",
  "type": "agv_transport",
  "description": "smoke",
  "priority": 3,
  "status": "pending",
  "device_id": "agv-02",
  "created_at": "2026-07-23T14:01:01.507212+00:00",
  "trace_id": "20260723-2201-f9d22b58"
}
```

`400` is returned for unknown device_id or invalid priority.

### `POST /api/tasks/{task_id}/rollback`

Revert a single task that is already `completed` or `failed`. Restores
device position, battery, route and status from a snapshot taken when the
task was scheduled.

```bash
curl -X POST http://localhost:8000/api/tasks/task-1215cd23/rollback
```

`404` if unknown id; `409` if the task is still pending or running.

### `POST /api/tasks/rollback`

Roll back the N most recent terminal tasks in creation order (newest first).

```bash
curl -X POST http://localhost:8000/api/tasks/rollback \
  -H 'Content-Type: application/json' \
  -d '{"limit": 3}'
```

`limit` defaults to 1, range 1-20.

## Sites

### `GET /api/sites`

List all sites (dock/warehouse zones).

### `POST /api/sites`

Create a site.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | 1-64 chars |
| `kind` | string | yes | `dock` or `warehouse` |
| `name` | string | yes | 1-128 chars |
| `x`, `y`, `z` | float | no | position (default 0) |
| `width`, `height`, `depth` | float | no | dimensions (default 2.5/1.5/2.5) |
| `rotation` | float | no | radians (default 0) |
| `color` | string | no | hex color (default `#5eb0ff`) |

### `PATCH /api/sites/{site_id}`

Partial update of a site. All fields optional.

### `DELETE /api/sites/{site_id}`

Remove a site. `404` if unknown.

---

## Device joints SSE

### `GET /api/devices/{device_id}/joints` (SSE)

Real-time joint positions for a device, updated at 30Hz. Used by the frontend
for robot visualization.

```bash
curl -N http://localhost:8000/api/devices/loader-01/joints
```

```json
{
  "device_id": "loader-01",
  "joints": {
    "left_joint_1": 0.0,
    "left_joint_2": 0.0,
    "left_joint_3": 0.0,
    "left_joint_4": 0.0,
    "left_joint_5": 0.0,
    "left_joint_6": 0.0,
    "right_joint_1": 0.0,
    "right_joint_2": 0.0,
    "right_joint_3": 0.0,
    "right_joint_4": 0.0,
    "right_joint_5": 0.0,
    "right_joint_6": 0.0,
    "left_paddle": 0.0,
    "right_paddle": 0.0
  },
  "timestamp": 1723190400.0
}
```

For `loader-01`, 14 joints: 6 left arm + 6 right arm + 2 hug paddles.

---

## Lifecycle

### `POST /api/control`

```bash
curl -X POST http://localhost:8000/api/control \
  -H 'Content-Type: application/json' \
  -d '{"action":"reset"}'
```

`action ∈ {start, stop, reset}`. `reset` clears tasks and logs.

---

## Logs

### `GET /api/logs`

Last 200 log entries (newest last). Each entry:

```json
{
  "trace_id": "20260723-2201-768a9b67",
  "task_id": "task-75dfc088",
  "module": "scheduler",
  "message": "assigned to agv-02",
  "level": "INFO",
  "timestamp": "2026-07-23T14:01:47.571357+00:00"
}
```

### `GET /api/logs/stream` (SSE)

Live log stream. The server pushes `data:` frames and heartbeats every 2s.

```bash
curl -N http://localhost:8000/api/logs/stream
```

```
retry: 5000
: ping
data: {"trace_id":"…","module":"task","message":"created: agv_transport",...}
```

The client should auto-reconnect on disconnect.

---

## Alerts

### `GET /api/alerts`

Active alerts + counts per severity.

```json
{
  "firing": [
    {
      "id": "f8…",
      "alert_key": "queue_backlog:global",
      "severity": "warning",
      "title": "任务队列堆积",
      "message": "当前有 5 条 pending 任务",
      "rule": "queue_backlog",
      "state": "firing",
      "created_at": "2026-07-23T14:01:50Z"
    }
  ],
  "count_by_severity": { "info": 0, "warning": 1, "critical": 0 }
}
```

Rules currently evaluated every tick:

| Rule | Severity | Trigger |
| --- | --- | --- |
| `device_battery_low` | warning, critical <5% | device.battery < 20 |
| `device_fault` | critical | device.status == fault |
| `queue_backlog` | warning | pending tasks ≥ 5 |
| `task_timeout` | warning | running > 30s with progress lagging |

### `POST /api/alerts/{alert_id}/ack`

```bash
curl -X POST http://localhost:8000/api/alerts/<id>/ack \
  -H 'Content-Type: application/json' \
  -d '{"by":"alice"}'
```

`404` if the alert has already been resolved.

### `GET /api/alerts/stream` (SSE)

Live alert state transitions (firing → acknowledged → resolved).

```bash
curl -N http://localhost:8000/api/alerts/stream
```

---

## Security

When `API_AUTH_ENABLED=1` is set in the environment, every request must
include a valid API key.

```http
X-API-Key: dev-key-1
Authorization: Bearer dev-key-1    # also accepted
```

Keys are configured via `API_API_KEYS` (comma separated). When auth is
enabled but no keys are configured, requests are allowed through (fail
open is intentional for local dev).

When `API_AUTH_ENABLED=0` (the default), no header is required.

The rate limit defaults to `120` requests per IP per `60s`, applied to
mutating endpoints (`POST /api/tasks`, `POST /api/control`,
`POST /api/tasks/{id}/rollback`, `POST /api/tasks/rollback`,
`POST /api/alerts/{id}/ack`). Reads and SSE streams are uncapped.

A `429 Too Many Requests` response indicates the cap was hit.

---

## Error codes

| Code | When |
| --- | --- |
| 400 | bad payload (invalid priority, unknown device_id) |
| 401 | API key missing/invalid (auth enabled) |
| 404 | unknown task_id / alert_id |
| 409 | task not in terminal state for rollback |
| 429 | rate limit exceeded |

---

## RCS service (standalone)

When RCS runs as its own service (`uvicorn rcs.app:create_app --factory`,
default port `8100`), the same routes live under `/api/rcs`. In embedded mode
the simulation backend mounts them on the same prefix. Auth (`RCS_API_AUTH_ENABLED`)
and MQTT (`RCS_MQTT_ENABLED`) are configured independently of the simulation
backend.

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/rcs/registry` | — | List registered devices + profiles |
| POST | `/api/rcs/{device_id}/command` | key | Enqueue a control command (same payload as MQTT) |
| GET | `/api/rcs/{device_id}/state` | key | Latest controller state |
| POST | `/api/rcs/{device_id}/estop` | key | Emergency stop (mode → `E_STOP`) |
| POST | `/api/rcs/{device_id}/clear_estop` | key | Clear estop (mode → `IDLE`) |
| GET | `/api/rcs/_health` | — | RCS liveness |
| GET | `/health` | — | standalone-app liveness (factory only) |

Command body (validated by `shared/python/robot_contracts`):

```json
{
  "command_id": "c-abc",
  "type": "move_j | move_l | execute_task | stop | home | estop | recover",
  "target_joints": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  "speed_scale": 1.0,
  "task_type": "pick_box",
  "parameters": {"target_pose": {"x": 0, "y": 0, "z": 0.5}},
  "group": "both"
}
```

When `type` is `execute_task`, the `task_type` and `parameters` fields are used
by `TaskCoordinator` to drive the 9-phase FSM. `group` selects the execution
group: `"left"`, `"right"`, `"base"`, or `"both"`.

## MQTT interface

RCS and the robot side (`robot_gateway`) exchange messages over an MQTT broker
(Mosquitto in `deploy/docker-compose.yml`). Topic layout and QoS are defined in
[`shared/contracts/mqtt_topics.md`](shared/contracts/mqtt_topics.md) and
enforced by the Pydantic models in
[`shared/python/robot_contracts`](shared/python/robot_contracts).

| Direction | Topic | QoS | Payload |
| --- | --- | --- | --- |
| down | `rcs/{device_id}/command` | 1 | `command.schema.json` |
| up | `rcs/{device_id}/state` | 0 | `state.schema.json` (downsampled, default 10 Hz) |
| up | `rcs/{device_id}/alert` | 1 | `alert.schema.json` |
| up | `robot/{device_id}/telemetry` | 0 | `telemetry.schema.json` |

MQTT is **off by default** (`RCS_MQTT_ENABLED=false`). Enable it with
`RCS_MQTT_ENABLED=true` plus `RCS_MQTT_HOST` / `RCS_MQTT_PORT` /
`RCS_MQTT_TOPIC_PREFIX`. The robot side mirrors the same topic prefix.

