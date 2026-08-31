# RCS 统一地图模型（Unified Map Model）设计文档

**日期**：2026-08-31
**范围**：`rcs/backend`（FastAPI + 异步 SQLAlchemy）、`rcs/frontend`（Vue 3 + TS + Ant Design Vue）
**数据库**：PostgreSQL
**状态**：设计已确认，待拆实施计划

---

## 1. 背景与目标

当前 RCS 中存在三类"地图"概念，彼此命名重叠但数据来源分散，且前端有三个独立入口页面（`SiteMapView` 站点地图 / `AdminMapsView` 场景地图 / `WarehouseView` 仓库视图）。本次重构目标：**后端数据统一为单一 `UnifiedMap`，前端三个入口合并为唯一「场景地图」页面**，页面内部通过子视图（几何 / 拓扑 / 布局）对统一数据进行不同投影，原「站点地图」「仓库视图」菜单项不再保留。

| 原名称 | 原入口/页面 | 合并后 |
|---|---|---|
| 仓库地图 | `WarehouseView.vue`（`/warehouse`） | 统一入口「场景地图」的「仓库布局」子视图（消费 `geometry_json` + `grid_json`）|
| 场景地图（拓扑） | `AdminMapsView.vue`（`/admin/maps`） | 统一入口「场景地图」本身（消费 `topology_json` + `robot_site_map_versions`）|
| 站点地图 | `SiteMapView.vue`（`/sitemap`） | 统一入口「场景地图」的「站点/几何」子视图（消费 `geometry_json` + 模板下拉）|

此外还分散存在：
- `SiteGrid`（AGV 导航栅格，内存 pydantic 模型，独立 `/grid/*` 接口）
- `rcs/models/topology_templates.py`（6 个硬编码 scenario：ecommerce/manufacturing/cold_chain/port/reverse_logistics/multi_floor）
- `rcs/models/site_map_templates.py`（8 个 DB 仓库模板）

**目标**：把三类地图收敛为**单一 `UnifiedMap` 数据模型的三种视图投影**，底层数据统一、上层按需投影，消除重复维护成本，同时保留各自场景的差异化能力。

**统一模型分层**（概念）：
```
统一地图模型
├── 几何层 Geometry   — 静态元素（墙体/货架/月台/柱/AGV 栅格），含唯一 ID + 类型 + 几何描述 + 拓扑连通性
├── 语义层 Semantic   — 区域类型标注、站点属性、元素状态、业务规则（速度/优先级/方向）
├── 拓扑层 Topology   — 节点/边图结构（原 SiteMap）
└── 动态层 Dynamic    — 实时占用/拥堵/临时障碍/动态代价（本次新增数据模型）
```

---

## 2. 核心数据模型（ORM：`rcs/db/models.py`）

### 2.1 统一主表 `robot_unified_maps`

```python
class UnifiedMap(Base):
    __tablename__ = "robot_unified_maps"

    map_id         = Column(String, primary_key=True)   # 取代 site_id 与 map_id 双主键
    name          = Column(String, nullable=False)
    name_en       = Column(String, nullable=True)
    is_template   = Column(Boolean, default=False)
    kind          = Column(String, default="warehouse") # warehouse | scenario | site（视图提示，非强约束）
    current_version = Column(Integer, default=1)
    bounds_json   = Column(JSONB, nullable=False, default=dict)   # {w, d, h}
    geometry_json = Column(JSONB, nullable=False, default=dict)   # FloorShell: walls/zones/facilities/docks/corridors/markings/floors
    grid_json     = Column(JSONB, nullable=True, default=dict)    # SiteGrid: {bounds, resolution, cells}（AGV 导航栅格，并入几何层）
    topology_json = Column(JSONB, nullable=False, default=dict)   # {nodes:[...], edges:[...]}（原 SiteMap.nodes_json/edges_json）
    semantic_json = Column(JSONB, nullable=True, default=dict)    # 区域类型/业务规则（可由 geometry 推导，独立存储以便覆盖）
    dynamic_json  = Column(JSONB, nullable=True, default=dict)    # 预留动态扩展（实时态主要由子表 robot_map_dynamic_state 承载）
    data          = Column(JSONB, nullable=True)
    created_at    = Column(DateTime, default=utcnow)
    updated_at    = Column(DateTime, default=utcnow, onupdate=utcnow)

    zones     = relationship("TopologyGrid", back_populates="map", cascade="all, delete-orphan")
    versions  = relationship("SiteMapVersion", back_populates="map", cascade="all, delete-orphan")
```

**字段划分原则**（已确认）：`geometry_json` / `grid_json` / `topology_json` / `semantic_json` 分列存储，便于按需投影查询与局部更新（动态层独立更新，不触碰静态几何）。

### 2.2 保留子表（外键改挂 `map_id`）

`TopologyGrid`（zone 行）与 `SiteMapVersion`（版本）**保留为子表**，仅将父键由 `site_id` / `map_id` 统一为 `map_id`：

```python
class TopologyGrid(Base):
    __tablename__ = "robot_topology_grid"
    id     = Column(Integer, primary_key=True)
    map_id = Column(String, ForeignKey("robot_unified_maps.map_id", ondelete="CASCADE"))
    zone_id = Column(String)
    zone_type = Column(String)
    # ... 其余列不变
    map = relationship("UnifiedMap", back_populates="zones")

class SiteMapVersion(Base):
    __tablename__ = "robot_site_map_versions"
    id     = Column(Integer, primary_key=True)
    map_id = Column(String, ForeignKey("robot_unified_maps.map_id", ondelete="CASCADE"))
    # ... 其余列不变
    map = relationship("UnifiedMap", back_populates="versions")
```

### 2.3 动态层 `robot_map_dynamic_state`（新增）

```python
class MapDynamicState(Base):
    __tablename__ = "robot_map_dynamic_state"
    id         = Column(Integer, primary_key=True)
    map_id     = Column(String, ForeignKey("robot_unified_maps.map_id", ondelete="CASCADE"), index=True)
    element_id = Column(String, index=True)   # 元素唯一 ID（来自 geometry/grid 层）
    state      = Column(String)               # occupied | free | blocked | congested | ...
    payload    = Column(JSONB, nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
```

### 2.4 `SiteGrid` 模型处理

`rcs/models/site_grid.py` 的 `SiteGrid` 是 pydantic 模型（非 ORM）。并入后：
- `UnifiedMap.grid_json` 存储其序列化（bounds + resolution + cells）。
- 删除独立 `/grid/*` 接口，改为从 `UnifiedMap.grid_json` 读写（或作为 `GET /maps/{id}` 响应中的 `grid` 字段）。
- 所有历史 `site_id` 参数语义对齐为 `map_id`；`SiteGrid.site_id` 字段在序列化时存为所属 `map_id`。

### 2.5 内存导航图类 `control/topology/site_map.py::SiteMap`

保留原名（它是导航图内存模型，与 ORM 表解耦）。`pathfinder` 改为从 `UnifiedMap.topology_json` 构造内存 `SiteMap`，不再引用 ORM `SiteMap` 表（该表已消失）。

---

## 3. 迁移策略（旧表直接删除，不保留）

新增迁移 `migrations/007_unified_map.sql`（幂等，可重复执行；**迁移完成后直接 DROP 旧表**）：

1. `CREATE TABLE robot_unified_maps (...)`（`IF NOT EXISTS`）
2. `CREATE TABLE robot_map_dynamic_state (...)`（`IF NOT EXISTS`）
3. `ALTER TABLE robot_topology_grid RENAME COLUMN site_id TO map_id;`（若列名为 site_id）并更新外键定义指向 `robot_unified_maps.map_id`
4. 迁移数据（INSERT...SELECT）：
   - 以 `robot_topology_shell.site_id` 为主键建立 `map_id`。
   - `data`（FloorShell）拆分为 `bounds_json`（bounds）+ `geometry_json`（zones/walls/.../floors）。
   - `LEFT JOIN robot_site_maps ON site_id = map_id`，填充 `topology_json`（nodes_json/edges_json）；若无匹配则 `topology_json = {}`。
   - `is_template`、`name`、`name_en` 直接映射。
5. `SiteMapVersion` 父键无需改列名（已是 `map_id`），仅外键目标表名变（若 DB 级外键存在）。
6. **迁移完成后直接 DROP 旧表**（不保留、不另出 008）：
   ```sql
   DROP TABLE IF EXISTS robot_topology_shell;
   DROP TABLE IF EXISTS robot_site_maps;
   ```
   > 注：因 dev 环境且模板可经 `seed_templates` 重建，删除旧表可接受；生产部署前需对旧库先行备份。

**site_id 与 map_id 一致性保证**：模板场景下两表 `map_id`/`site_id` 已相等（`tpl-<key>`）；live map 由 `create_from_template` 保证 `map_id == site_id`。迁移 JOIN 用 `site_id = map_id`，缺失侧补空。

---

## 4. 统一 API（`rcs/api/maps.py`，取代 topology_shell + control_maps 拓扑部分）

废弃 `/topology/shell/*` 与 `/maps/*` 双套，统一为：

```
GET  /maps                              # 列表（?include_templates=）
GET  /maps/templates                    # 全部模板元信息（返回 map_id，不再有 site_id 字段）
GET  /maps/templates/{key}
POST /maps/templates/seed              # 重新 seed 全部模板（含原 8 仓库模板 + 原 6 硬编码 scenario）
POST /maps/from-template               # 克隆 map_id 维度全部数据（几何+栅格+拓扑+zone+version）
GET  /maps/{id}                        # ★ 统一入口：{geometry, grid, topology, semantic, dynamic_summary}
PUT  /maps/{id}                        # 写回（geometry/grid/topology/semantic 分别落对应 JSON 列）
GET  /maps/{id}/versions               # 版本列表
POST /maps/{id}/versions               # 新建版本
GET  /maps/{id}/zones                  # zone 行（或含于 geometry）
GET  /maps/{id}/dynamic?element_id=&state=   # 动态层查询（/map/stations?status=available 基础版）
POST /maps/{id}/dynamic                # 写入动态态
```

- 前端统一「场景地图」页面（合并原 `SiteMapView` / `AdminMapsView` / `WarehouseView`）调 `GET /maps/{id}`，按子视图分别消费 `geometry` / `grid` / `topology` 字段。
- `warehouse_converter.py` / `warehouse_inventory.py`：语义 `SITE_ID` → `MAP_ID`，调 `get(map_id)` 取 geometry/grid。
- `sys_dashboard.py`：`from ... import UnifiedMap`，`is_template` 过滤逻辑不变（字段仍存在）。
- 删除 `rcs/api/topology/topology_shell.py`、`topology_grid.py` 中独立路由（或改为转发到 `/maps`）。
- 删除 `rcs/api/topology/topology_templates.py` 及 `main.py` 中 `app.include_router(topology_templates, prefix="/api/rcs/topology")`；其前端消费方改为读 `/maps/templates`。

---

## 5. 后端服务层（`rcs/services/control/control_maps.py`）

- `UnifiedMapCRUD.get(map_id)`：返回合并 dict（聚合 zones/versions/grid）。
- `create_from_template(key)`：克隆统一 `map_id` 下全部数据（原跨 3 表逻辑改为跨 `unified_maps` + `topology_grid` + `site_map_versions`）。
- `seed_templates()`：`_build_*_template` 原返回 `(shell, grid_rows, nodes, edges)`，现改为返回单一 `UnifiedMap` 构造参数（geometry_json + grid_json + topology_json + semantic_json）。
- **并入原 6 硬编码 scenario**：`rcs/models/topology_templates.py` 的 `SCENARIO_IDS` 6 个 builder 改写为生成 `UnifiedMap` 模板数据（含 grid），统一进 `seed_templates`；删除 `topology_templates.py` 模块及 `services/topology/__init__.py` 对其的导入。
- `control/topology/site_map.py` 内存 `SiteMap` 类保留；`pathfinder` 由 `topology_json` 构造。

---

## 6. 前端改动

### 6.1 API 客户端
- 新增/合并 `api/map.ts`：`getMap(id)` 返回 `{geometry, grid, topology, semantic, ...}`；取代 `api/topologyShell.ts`（删除 `getShell`/`listShells`）。
- `api/warehouseTemplates.ts`：模板信息去掉 `site_id`，仅留 `map_id`。
- `api/templates.ts`、`views/simulation/warehouse/api/warehouse.ts`：grid 相关调用改为 `getMap(id).grid`。

### 6.2 状态管理
- `stores/floorShell.ts`：`loadBySite(siteId)` → `loadByMap(mapId)`，内部调 `getMap`。
- `stores/warehouse.ts`：`SITE_ID` → `MAP_ID`，调 `getMap`。
- `stores/scenario.ts`：`selectTemplate` 调 `floorStore.loadByMap(tpl.map_id)`。
- `stores/adminMaps.ts`：`current` 改为从 `getMap(id).topology` 读取；保存调 `PUT /maps/{id}`。
- `stores/siteGrid.ts`：改为从 `getMap(id).grid` 派生，或删除独立 store。

### 6.3 视图（三页面合并为唯一「场景地图」）

原 `SiteMapView`（站点地图）、`AdminMapsView`（场景地图/拓扑）、`WarehouseView`（仓库视图）**合并为单一「场景地图」页面** `ScenarioMapView.vue`（路由 `/scenario-map` 或保留 `/admin/maps`）：

- 页面顶部：模板下拉（8 + 6 = 14 个 DB 模板，选 `map_id`），统一调 `getMap(map_id)` 取完整 `UnifiedMap`。
- 页面内部三个子视图（tab / 切换），均为同一 `map_id` 数据的不同投影：
  - **几何视图**：原 `SiteMapView` 的 2D/3D 渲染（`DeviceMap2D` / `DeviceMap3D`），消费 `geometry_json` + `grid_json` + `bounds_json`。
  - **拓扑编辑**：原 `AdminMapsView` 的节点/边编辑，消费 `topology_json` + `robot_site_map_versions`。
  - **仓库布局**：原 `WarehouseView` 的布局预览，消费 `geometry_json`（墙体/区域/设施/月台）。
- 删除 `SiteMapView.vue`、`WarehouseView.vue`（或其内容并入 `ScenarioMapView`）；`AdminMapsView.vue` 重命名为 `ScenarioMapView.vue` 并扩充几何/布局子视图。
- `scenarioConfig.ts`：keyed by category，消费 `map_id`。

### 6.4 类型与命名
- `types/siteGrid.ts`：`SiteGrid` 序列化结构与 `UnifiedMap.grid_json` 对齐（`site_id` → `map_id`）。
- `types/types.ts` / `types/scenario.ts`：`SiteMapInfo.site_id` 移除。
- **菜单/侧边栏（`sys_seed.py`）—— 仅保留「场景地图」一项**：
  - 删除「站点地图」菜单项（原 `/sitemap`）。
  - 删除「仓库视图」菜单项（原 `/warehouse`）。
  - 「场景地图」（原 `/admin/maps`）保留并作为唯一地图入口；可更名为「场景地图」或「地图」均可，本设计保留「场景地图」名称。
- **产品标题** `RCS 站点地图` → `RCS 控制台`（i18n `app.title`），消除与菜单项撞名。

---

## 7. 测试

### 7.1 后端
- 新增 `test_unified_map.py`：CRUD、合并视图投影、克隆、seed（14 模板）、动态层读写、grid 并入。
- 改写 `test_site_map_templates.py`（143 测试）：断言 8 仓库模板 + 6 硬编码 scenario 共 14 模板落在 `robot_unified_maps`，含 geometry/grid/topology。
- 改写 `test_topology_*.py`：改调 `/maps/{id}`。
- `seed` 幂等性：重复 seed 不重复插入（按 `map_id` upsert）。

### 7.2 前端
- `stores/floorShell.spec.ts`、`scenario.spec.ts`、`adminMaps.spec.ts`：改 `map_id` 语义。
- 新增 `api/map.spec.ts` 取代 `topologyShell.spec.ts`。
- `ScenarioMapView.spec.ts`（原 `AdminMapsView.spec.ts` + `SiteMapView.spec.ts` 合并）：改调统一接口，覆盖几何/拓扑/布局三子视图。
- `types/siteGrid.spec.ts`：grid 序列化对齐。

### 7.3 验证
- `pnpm run test`（前端单测）、`pytest`（后端单测）全绿。
- `tsc --noEmit` + `vite build` 通过。
- Playwright 真实浏览器走查：进「场景地图」→ 选模板 → 几何视图渲染 → 切「拓扑编辑」改节点 → 切「仓库布局」；确认无 Vue 报错、接口无 500、旧「站点地图/仓库视图」菜单已不存在。

---

## 8. 风险与缓解

| 风险 | 缓解 |
|---|---|
| 双 id 不一致（site_id vs map_id） | 模板两表 map_id 已相等；live map 由 create_from_template 保证相等；迁移 JOIN 用 `site_id=map_id`，缺失侧补空 |
| 动态层无实时数据源 | 本阶段仅建表 + 基础查询接口；`/map/stations?status=available` 无数据时回退静态语义（默认 available） |
| 旧表删除风险 | 迁移在 `007` 内 DROP 旧表；dev 环境可经 `seed_templates` 重建；生产部署前需对旧库备份 |
| SiteGrid 边界并入 | grid 作为 `grid_json` 列并入，独立 `/grid/*` 接口删除，前端统一从 `getMap` 取 |
| 6 硬编码模板与 8 DB 模板重叠 | 统一 seed 进 `robot_unified_maps`，去重后共 14 模板；删除 `topology_templates.py` 模块 |
| 三页面合并复杂度 | 原三个视图组件合并为 `ScenarioMapView` 单页三子视图；需保证 2D/3D/拓扑编辑/布局渲染不互相污染状态 |

---

## 9. 实施顺序建议（供 writing-plans 拆解）

1. 后端 ORM：新增 `UnifiedMap` / `MapDynamicState`，改 `TopologyGrid` / `SiteMapVersion` 父键；迁移 `007`。
2. 后端服务：`control_maps` 改 `UnifiedMapCRUD` + `seed_templates`（含 6 scenario 并入）。
3. 后端 API：`maps.py` 统一接口；删除旧 `topology_shell` / `topology_templates` 路由；改 `main.py`、`sys_dashboard`、`warehouse_*`。
4. 前端 API/store/types：新增 `api/map.ts`，改 4 个 store，改类型。
5. 前端视图合并：删除 `SiteMapView` / `WarehouseView`，`AdminMapsView` → `ScenarioMapView`（含几何/拓扑/布局三子视图）+ 菜单仅留「场景地图」+ 产品标题「RCS 控制台」。
6. 测试 + tsc/build + Playwright 验证。
7. spec 自审 + 用户审阅 gate。
