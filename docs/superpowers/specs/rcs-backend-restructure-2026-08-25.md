# RCS Backend 重命名 + 控制层分层重构与持久化设计

**状态**：草稿（待 review）
**日期**：2026-08-25
**范围**：rcs/backend/rcs_backend 重命名为 rcs/backend/rcs；control 层 7 模块分层（API/Models/Services）+ 持久化到 PostgreSQL；前端 5 个管理页面完整实现。

---

## 1. 决策基线（已与用户确认）

| 项 | 决策 |
|----|------|
| 执行范围 | 全量一次性完成（重命名 + 7 模块持久化 + 前端） |
| 重命名 | `rcs/backend/rcs_backend` → `rcs/backend/rcs`，导入 `rcs_backend.*` → `rcs.*` |
| 存储后端 | **统一 PostgreSQL（asyncpg）**，废弃 `services/shell_store.py`；移除 memory/sqlite 分支 |
| API 风格 | RESTful，统一前缀 `/api/rcs` |
| 前端交付 | 完整 5 个页面（Vue 3 + Pinia + vue-router + vue-i18n） |
| 场景地图编辑 | 查看器 + JSON 导入/导出（不做拖拽编辑器，留后续） |

---

## 2. 目录重命名

机械替换全仓 `rcs_backend.` → `rcs.`，涉及：
- `rcs/backend/rcs_backend/` → `rcs/backend/rcs/`（目录移动）
- `main.py` / `config.py` / `db/session.py` / `db/models.py` / `control/__init__.py` / `api/*` / `tests/*` 内所有 `rcs_backend.` 导入
- `rcs/backend/pyproject.toml`：`packages` / `tool.setuptools` 包名 `rcs_backend` → `rcs`
- `rcs/backend/Dockerfile`：`PYTHONPATH` 中 `rcs_backend` → `rcs`
- 纯重命名，无逻辑改动。

---

## 3. 存储层统一（PostgreSQL only）

### 3.1 废弃
- 删除 `rcs/backend/rcs/services/shell_store.py`（raw aiosqlite）。
- `topology_*` 路由改走 SQLAlchemy `db/` 层。

### 3.2 `config.py`
- 移除 `storage: Literal["memory","sqlite","postgres"]`、`db_path`、`service_*` 残留。
- 保留唯一：`database_url: str = "postgresql+asyncpg://rcs:rcs@localhost:5432/rcs"`（可被 `RCS_DATABASE_URL` 覆盖）。
- 移除已删的 `embedded/service_url/service_timeout_s`（上一轮已删，确认无残留）。

### 3.3 `db/session.py`
- 仅保留 PostgreSQL async engine 工厂（`create_async_engine(database_url, ...)`）。
- `init_db()`：`Base.metadata.create_all`（开发期）或在 Postgres 已建表时跳过；迁移以 `migrations/001_init.sql` 为准（生产用 `alembic` 留后续，本轮用 `create_all` 保证可跑）。
- 提供 `async_session()` 依赖（FastAPI `Depends`）。

---

## 4. 分层架构（高内聚低耦合）

每个控制子模块统一为三层；**算法/领域层保留不动，services 叠加持久化外壳**：

```
rcs/control/<module>/
  models.py     # 领域模型（pydantic / dataclass）—— 运行时逻辑，保留
  orm.py        # SQLAlchemy ORM 表（持久化实体）—— 新增
  service.py    # 业务服务：读写 DB + 调用领域逻辑 —— 新增/改造
  api.py        # FastAPI 路由（REST 资源）—— 新增/改造，导出 router()
```

保留的纯算法文件（不动）：
- `control/dag/graph.py`（TaskDAG / TaskNode）
- `control/planning/trajectory.py`（plan_trapezoidal / plan_quintic）
- `control/scheduler/policy.py`（compute_utility）
- `control/orders/decomposer.py`（decompose_order）
- `control/registry.py`（运行期注册表，改为从 DB 加载 + 种子化）

services 通过 `db/session.async_session()` 读写；领域逻辑保持无 DB 依赖。

---

## 5. 数据库模型（`db/models.py` 扩展）

PostgreSQL 表（沿用 SQLAlchemy 2.0 `Mapped` 声明式）。

### 5.1 设备 `devices`（扩展现有）
- `device_id` PK, `name`, `morphology`(agv/arm/...), `kind`
- `spec_json` JSONB（ArmSpec: dh_params, tcp_offset, joint_limits；叉车/AGV 参数）
- `limits_json` JSONB（pos_lower/upper, vel_max, acc_max, control_hz）
- `home_joints_json` JSONB
- `status`(registered/online/offline/error), `created_at`, `updated_at`

### 5.2 场景地图 `site_maps` + `site_map_versions`（新）
> 取代现有 `TopologyShell` / `TopologyGrid` 两表（后者随 `shell_store.py` 一并废弃），统一为节点/边 JSONB 模型。迁移时 `001_init.sql` 中的这两个表删除或保留为历史（本轮不再写入）。
- `site_maps`: `map_id` PK, `name`, `current_version`, `nodes_json` JSONB, `edges_json` JSONB, `created_at`, `updated_at`
- `site_map_versions`: `version_id` PK, `map_id` FK, `version` int, `nodes_json`, `edges_json`, `note`, `created_at`
- 导入=解析 JSON 写 nodes/edges；导出=读取 nodes/edges 序列化为 JSON；保存版本=插 `site_map_versions`。

### 5.3 订单 `orders` / `order_items` / `order_tasks`（扩展现有）
- `orders` 增：`status`(PENDING/RUNNING/DONE/FAILED/CANCELLED), `dag_json` JSONB（分解后的 DAG 快照）, `created_at`, `updated_at`
- `order_tasks` 增：`status`(PENDING/READY/RUNNING/DONE/FAILED), `started_at`, `finished_at`（状态机推进）

### 5.4 规划库 `planning_profiles`（新）
- `profile_id` PK, `name`, `algo`(trapezoidal/quintic), `axes` int, `vel_max_json` JSONB, `acc_max_json` JSONB, `created_by`, `created_at`
- 运行时按 `profile_id` 取参调用 `plan_trapezoidal/quintic`。

### 5.5 调度配置 `scheduler_configs`（新）
- `config_id` PK, `name`, `strategy`(nearest/util-weighted/...), `weights_json` JSONB({w1..w4}), `active` bool, `created_at`
- 仅一个 `active=true`；运行时 `scheduler.policy.compute_utility` 读 active 配置。

### 5.6 日志 `command_logs` + `event_logs`（新）
- `command_logs`: `cmd_id` PK, `device_id`, `cmd_type`, `payload_json` JSONB, `issued_by`, `result`(ok/fail), `created_at`
- `event_logs`: `event_id` PK, `level`(info/warn/error), `source`, `message`, `meta_json` JSONB, `created_at`
- 统一入口：`logs.service.issue_command(device_id, cmd, payload)` 落 `command_logs` + `event_logs`；控制层所有指令下发经此。

---

## 6. 各模块服务职责

| 模块 | service 职责 | 运行时衔接 |
|------|-------------|-----------|
| devices | 注册/查询/参数更新；首次启动若空则从 `registry._DEFAULT_PROFILES` 种子化 | `registry` 改为从 DB 加载设备 |
| sitemap | 地图 CRUD + 导入(JSON 文本)/导出 + 版本保存/回滚 | 拓扑图供调度/规划读取 |
| orders | 创建→`decompose_order`→存 DAG(`dag_json`+`order_tasks`)→状态机推进 | 与 control 调度闭环 |
| planning | 规划配置库增删查；按 profile_id 取参调 `trajectory` | 运行时轨迹生成 |
| scheduler | 读写 `weights_json`/strategy；`active` 切换 | 注入 `compute_utility` |
| dag | 任务依赖图结构化存储 + ready/completed 监控 | 基于 `graph.TaskDAG` |
| logs | `issue_command()` 统一落库；事件记录 | 审计/排障 |

---

## 7. REST API（统一前缀 `/api/rcs`）

```
GET    /api/rcs/devices
POST   /api/rcs/devices                 # 注册
GET    /api/rcs/devices/:id
PUT    /api/rcs/devices/:id             # 参数更新
DELETE /api/rcs/devices/:id

GET    /api/rcs/maps
POST   /api/rcs/maps                    # 创建
GET    /api/rcs/maps/:id
PUT    /api/rcs/maps/:id
DELETE /api/rcs/maps/:id
POST   /api/rcs/maps/:id/import         # JSON 文本导入
GET    /api/rcs/maps/:id/export         # 导出 JSON
GET    /api/rcs/maps/:id/versions
POST   /api/rcs/maps/:id/versions/:vid/restore

POST   /api/rcs/orders                  # 创建并分解 DAG
GET    /api/rcs/orders
GET    /api/rcs/orders/:id
PUT    /api/rcs/orders/:id/status       # 状态机推进
GET    /api/rcs/orders/:id/tasks        # DAG 任务监控

GET    /api/rcs/planning-profiles
POST   /api/rcs/planning-profiles
GET    /api/rcs/planning-profiles/:id
DELETE /api/rcs/planning-profiles/:id

GET    /api/rcs/scheduler-configs
POST   /api/rcs/scheduler-configs
PUT    /api/rcs/scheduler-configs/:id
POST   /api/rcs/scheduler-configs/:id/activate

GET    /api/rcs/logs/commands[?device_id=&limit=]
GET    /api/rcs/logs/events[?level=&limit=]
```
（原有 `topology_*`、`control` 运行期路由保留；新分层路由逐步并入，禁止破坏现有 `/registry`、`/command`、`/_health` 等运行接口。）

---

## 8. 前端（rcs/frontend，完整实现）

新增 5 个页面 + 配套 `types/`、`api/`、`stores/`、`router/`、`i18n/`、`App.vue` 导航：

| 页面 | 路由 | 后端接口 | 说明 |
|------|------|---------|------|
| 设备列表与参数配置 | `/devices` | `/devices` | 列表 + 选中设备参数抽屉（编辑 limits/spec） |
| 场景地图查看器 | `/sitemap`(改) | `/maps` | SVG/Canvas 只读渲染节点/边 + 导入/导出 JSON 按钮 |
| 订单管理与监控看板 | `/orders` | `/orders`, `/orders/:id/tasks` | 列表 + 状态 + DAG 任务依赖图 |
| 调度策略配置面板 | `/scheduler` | `/scheduler-configs` | 权重/策略表单 + 激活切换 |
| 系统日志查询 | `/logs` | `/logs/commands`, `/logs/events` | 分页表格 + 级别/设备过滤 |

约定（对齐现有）：
- `api/*.ts` 用 `http` 客户端；`types/*.ts` 集中类型；`stores/*.ts` 用 Pinia。
- `App.vue` 导航增加 `设备`/`调度`/`日志` 链接。
- `i18n/messages.ts` 增加对应中英文段。
- 地图编辑仅查看 + JSON 导入导出（无拖拽）。

---

## 9. 迁移与回退
- `001_init.sql` 修订：移除 `TopologyShell`/`TopologyGrid`（由 `site_maps` 取代），保留/扩展 `devices`/`orders`/`order_items`/`order_tasks`；新增 `site_maps`/`site_map_versions`/`planning_profiles`/`scheduler_configs`/`command_logs`/`event_logs`。
- `db/session.init_db()` 用 `Base.metadata.create_all` 保证开发环境可跑（生产用修订后的 `001_init.sql` + alembic 留后续）。
- `docker-compose.yml` 已含 Postgres 16；移除已删的 sqlite 相关卷/环境变量残留。

## 10. 验证
- 后端：`python -c "import rcs"` 通过；原有 64 测试 + 新增 services/repo 测试通过；pytest 覆盖 devices/sitemap/orders/planning/scheduler/logs 服务。
- 前端：`vue-tsc --noEmit` 通过；`vitest` 通过；`npm run build` 通过。
- 端到端（需本地 Postgres）：`docker compose up -d` → 启动 uvicorn → 设备种子化、地图导入导出、下单分解 DAG、调度配置激活、日志查询均可用。
- 不破坏现有 `control` 运行期算法。

## 11. 风险
- 重命名漏改导致导入失败 → 全仓 grep `rcs_backend` 清零后验证。
- PostgreSQL 未起时无法运行 → 文档明确需先起 Postgres；CI 用服务容器。
- 大 spec 多文件改动 → 按模块分步提交，每模块独立可测。
