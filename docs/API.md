# API Reference

> Reference for the robot-logic prototype HTTP API. The default base URL is
> `http://localhost:8000`. All endpoints are JSON unless noted; SSE endpoints
> return `text/event-stream`.

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
  "device_count": 4,
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
| `type` | string | yes | one of `dock_loading`, `agv_transport`, `warehouse_storage` |
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
  "type": "move_j | move_l | stop | home | estop | recover",
  "target_joints": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  "speed_scale": 1.0
}
```

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

