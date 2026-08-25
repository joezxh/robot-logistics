# rcs/backend

RCS 统一后端（已合并 control 子项目）。所有控制运行期 + 持久化 + REST API
在一个 FastAPI 进程内。

提供：

- 嵌入式控制运行期（registry / 命令调度 / 状态机 / 拓扑解析 / 任务 DAG）
- 站点拓扑 CRUD（floor_shell / site_grid）— 与 DXF 导入导出
- 6 场景物流模板（电商 / 制造 / 冷链 / 港口 / 退货 / 多层）
- 订单 CRUD + DAG 生命周期
- **Phase B/C** 持久化（统一 PostgreSQL）：
  - 设备（含 spec / limits / home_joints / status）
  - 场景地图（含版本回滚 + JSON 导入导出）
  - 订单状态机 + DAG 任务监控
  - 规划配置库（trapezoidal / quintic profiles）
  - 调度配置（单激活，含权重）
  - 命令 + 事件日志（审计）

## 运行

```bash
cd rcs/backend
pip install -e ".[dev]"
# 起 Postgres（必需；init_db 会建表）
docker compose -f rcs/backend/docker-compose.yml up -d db
pytest -v

# 开发启动
uvicorn rcs.main:app --reload --port 8100

# Docker（带 db）
docker compose -f rcs/backend/docker-compose.yml up --build
```

## 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `RCS_API_KEY` | `` | API 密钥（留空则禁用） |
| `RCS_DATABASE_URL` | `postgresql+asyncpg://rcs:rcs@localhost:5432/rcs` | PostgreSQL 连接（必需） |

> 旧版 `RCS_STORAGE`/`RCS_DB_PATH`/`RCS_SERVICE_URL`/`RCS_EMBEDDED` 已移除 —
> 仅 PostgreSQL，且控制运行期与 API 进程内嵌，无外部服务。

## REST API（全部 `/api/rcs/...` 前缀）

### 健康与运行期
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/rcs/_health` | 嵌入式控制运行期健康 |

### 拓扑 / DXF
| 方法 | 路径 | 描述 |
|------|------|------|
| GET/POST | `/api/rcs/topology/shell[/{site_id}]` | shell CRUD |
| GET/PUT | `/api/rcs/topology/grid/{site_id}` | grid CRUD |
| POST | `/api/rcs/topology/import/dxf[/{site_id}]` | DXF 解析+保存 |
| POST | `/api/rcs/topology/export/dxf[/{site_id}]` | DXF 导出 |
| GET | `/api/rcs/topology/templates[/{scenario_id}]` | 6 场景模板 |

### 设备（Phase C1）
| 方法 | 路径 | 描述 |
|------|------|------|
| GET/POST/PUT/DELETE | `/api/rcs/devices[/{device_id}]` | 设备 CRUD + 参数编辑 |
| GET | `/api/rcs/registry` | 当前 in-memory 注册表（运行期） |

### 场景地图（Phase C2）
| 方法 | 路径 | 描述 |
|------|------|------|
| GET/POST/PUT/DELETE | `/api/rcs/maps[/{map_id}]` | 地图 CRUD |
| POST | `/api/rcs/maps/{map_id}/import` | JSON 导入 |
| GET | `/api/rcs/maps/{map_id}/export` | JSON 导出 |
| GET | `/api/rcs/maps/{map_id}/versions` | 版本列表 |
| POST | `/api/rcs/maps/{map_id}/versions/{vid}/restore` | 恢复版本 |

### 订单 + DAG（Phase C3）
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/rcs/orders` | 创建并分解为 DAG（202） |
| GET | `/api/rcs/orders[?status=…]` | 列出 |
| GET | `/api/rcs/orders/{order_id}` | 获取 |
| PUT | `/api/rcs/orders/{order_id}/status` | 推进状态机 |
| GET | `/api/rcs/orders/{order_id}/tasks` | DAG 任务监控 |
| PUT | `/api/rcs/orders/{order_id}/tasks/{node_id}/status` | 任务状态 |

### 规划 /调度（Phase C4/C5）
| 方法 | 路径 | 描述 |
|------|------|------|
| GET/POST/DELETE | `/api/rcs/planning-profiles[/{id}]` | 轨迹规划配置库 |
| GET/POST/PUT | `/api/rcs/scheduler-configs[/{id}]` | 调度配置 CRUD |
| GET | `/api/rcs/scheduler-configs/active` | 当前激活 |
| POST | `/api/rcs/scheduler-configs/{id}/activate` | 切换激活 |

### 日志（Phase C6）
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/rcs/logs/commands[?device_id=&limit=]` | 指令日志 |
| GET | `/api/rcs/logs/events[?level=&limit=]` | 事件日志 |

### 控制运行期（命令 / 状态 / WS）
| GET | `/api/rcs/registry` |
| POST / | `/api/rcs/{device_id}/command` |
| POST / | `/api/rcs/{device_id}/estop` |
| POST / | `/api/rcs/{device_id}/clear_estop` |
| GET | `/api/rcs/{device_id}/state` |
| WS | `/api/rcs/ws` |

## 6 场景 ID

`ecommerce`, `manufacturing`, `cold_chain`, `port`, `reverse_logistics`, `multi_floor`

## 验证

```bash
pytest -v          # 51 unit pass + 6 skipped (Postgres 不在线时)
```