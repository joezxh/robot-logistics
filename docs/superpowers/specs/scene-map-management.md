# 场景地图管理模块 + 3D（MJCF）查看 设计文档

**状态**：设计评审中（Approach A 已确认）
**日期**：2026-09-02
**作者**：AI Orchestrator（brainstorming → 本设计）

---

## 0. 背景与目标

`rcs` 后端已存在统一地图表 `robot_unified_maps`（`geometry_json` 落库）和
`/api/rcs/maps` 全套 CRUD，但**前端没有地图管理模块**，且场景模板原仅靠 Python
`seed_templates()` 播种（6 个 scenario + 8 个 warehouse）。本次将 `geometry_json` 统一为
从 `warehouse_theatre_3d` 提取的 `wt_floor_shell` 结构，并由 `001_init.sql` 直接播种 13 套场景模板。

本次目标：

1. 在 `001_init.sql` 中直接用 `INSERT` 初始化 **13 套场景地图模板**（`is_template=1`，
   覆盖 7 个场景，每场景 1–2 套布局变体），同时保留 Python `seed_templates()` 幂等刷新
   （**混合并存**：7 个场景的"主变体" `map_id` 与 Python 同键，6 套"备选变体"仅 SQL 播种）。
2. 设计一个**场景地图管理模块**（前端）：模板/实例目录、3D 查看、从模板克隆、Zone 编辑器。
3. 以 `geometry_json` 为**唯一数据源**，由**后端 Python 程序**把 JSON → MJCF，前端用现有
   `MjcfLoader`（three.js）渲染，覆盖装卸场景的月台/货车/火车等元素。

### 已确认的关键决策

| 决策点 | 结论 |
|--------|------|
| 播种来源 | 混合并存：`001_init.sql` 写 13 套变体（7 个场景主变体 `map_id` 与 Python 同键，6 套备选变体加 `-2` 后缀）+ 保留 Python `seed_templates()` 幂等刷新 |
| 3D 渲染 | `geometry_json` 唯一数据源 → 后端 Python `/api/rcs/maps/{id}/mjcf` 生成 MJCF → 前端 `MjcfLoader` 渲染 |
| 管理模块能力 | 完整 CRUD + 从模板克隆 |
| 数据模型 | 方案 A：`geometry_json` 采用 `wt_floor_shell` 结构（源自 `warehouse_theatre_3d`，已含 `h/y/rot/color/label` 及 `walls/docks/facilities/zones/corridors`），后端 zone/dock-type → mujoco body 注册表 |

---

## 1. 13 套场景模板清单（7 场景 × 1–2 变体）

所有模板 `is_template=1`、`kind="scenario"`、`current_version=1`、`topology_json='{}'`（场景模板不带导航图）。
各场景"主变体"的 `map_id` 与 Python `seed_templates()` 的 `SCENARIO_IDS` 完全一致（混合并存 = 同一批行）；
"备选变体"共 6 套，其 `map_id` 在主变体后加 `-2` 后缀，仅由 SQL 播种。

| # | 场景 | 主变体 map_id | 备选变体 map_id | bounds (m) | 关键 zones（装卸链以粗体标注） |
|---|------|--------------|----------------|-----------|-------------------------------|
| 1 | 大型电商仓库 | `tpl-ecommerce` | — | 120×80 | flow_rack / high_rack / mezzanine / ASRS + **truck_dock（月台）** + staging |
| 2 | 火车卸货→月台→大卡车 | `tpl-train_unload` | `tpl-train_unload-2` | 180×80 / 220×90 | `rail_track`（铁轨）+ 多个 `train_car`（车厢）+ `platform`（月台）+ 多个 `truck`（大卡车）+ staging |
| 3 | 工厂仓库(含卸货) | `tpl-manufacturing` | `tpl-manufacturing-2` | 100×80 / 120×90 | production_line×4 + wip_buffer + parts_storage + **truck_dock（卸货月台）** + staging |
| 4 | 港口码头卸货 | `tpl-port` | `tpl-port-2` | 200×150 / 240×160 | container_yard×2 + customs_area + **truck_dock×2** + reefer(cold_zone) + staging |
| 5 | 冷链仓库 | `tpl-scn-cold_chain` | `tpl-scn-cold_chain-2` | 80×60×8 / 100×70×9 | frozen_zone / cold_zone / ambient_zone + **truck_dock×2** + staging |
| 6 | 退货异常仓库 | `tpl-scn-reverse_logistics` | `tpl-scn-reverse_logistics-2` | 60×40 | returns_received + qc_staging×2 + reshelving + disposal + **truck_dock** |
| 7 | 多层仓库 | `tpl-multi_floor` | `tpl-multi_floor-2` | 80×60×12 / 100×70×10 | Floors L1/L2/L3（staging + rack），`elevator_shaft` 垂直连接 |

| # | 场景 | map_id | bounds (m) | 关键 zones（装卸链以粗体标注） |
|---|------|--------|-----------|-------------------------------|
| 1 | 大型电商仓库 | `tpl-ecommerce` | 160×100 | flow_rack / high_rack / mezzanine / ASRS + **loading_bay（月台）** + staging |
| 2 | 火车卸货→月台→大卡车 | `tpl-train_unload` | 180×80 | `rail_track`（铁轨）+ 多个 `train_car`（车厢）+ `platform`（月台）+ 多个 `truck`（大卡车）+ staging |
| 3 | 工厂仓库(含卸货) | `tpl-manufacturing` | 100×80 | production_line×4 + wip_buffer + parts_storage + **loading_bay（卸货月台）** + staging |
| 4 | 港口码头卸货 | `tpl-port` | 200×150 | container_yard×2 + customs_area + **loading_bay×2** + reefer(cold_zone) + staging |
| 5 | 冷链仓库 | `tpl-scn-cold_chain` | 80×60 | frozen_zone / cold_zone / ambient_zone + **loading_bay×2** + staging |
| 6 | 退货异常仓库 | `tpl-scn-reverse_logistics` | 60×40 | returns_received + qc_staging×2 + reshelving + disposal + **loading_bay** |
| 7 | 多层仓库 | `tpl-multi_floor` | 80×60×12 | Floors L1/L2/L3（staging + rack），`elevator_shaft` 垂直连接 |

> 每个场景都含 `loading_bay`（月台/卸货口），满足"必须包含装卸场景"要求。
> `train_unload` 用 `rail_track → train_car → platform → truck` 表达完整装卸链。
> `cold_chain`/`reverse_logistics` 因与 warehouse 模板 key 冲突，沿用 `tpl-scn-<id>` 命名空间（与 Python 一致）。

### `train_unload` 场景布局建议（坐标示意，单位 m）

- `rail_track`：贴左侧长条，`x=0,z=0,w=8,d=80`（铁轨基座）。
- `train_car`（车厢）×3：`x=10,z=10/35/60,w=30,d=20,h=4`，代表停靠的货运车厢。
- `platform`（月台）：`x=45,z=0,w=20,d=80,h=1.2`，站台面略高于地面（`y=0.3`）。
- `truck`（大卡车）×3：右侧，`x=70,z=10/35/60,w=25,d=18,h=3.5`，货厢。
- `staging`：最右 `x=100,z=0,w=80,d=80` 暂存区。
- 流向：火车(左) → 月台(中) → 卡车(右)，在 `semantic_json` 标注 `flow: ["rail_track","train_car","platform","truck"]`。

---

## 2. `geometry_json` 扩展字段与 zone-type 注册表

### 2.1 `geometry_json` 采用 `wt_floor_shell` 结构（统一数据源）

`geometry_json` 直接采用从 `warehouse_theatre_3d` 提取的 `wt_floor_shell` 结构（已是 13 套模板的统一 schema），
**不再需要扩展旧 `FloorShell`**。其顶层为 `bounds / walls / docks / facilities / zones / corridors`，
每个布局元素固定 11 字段：

```yaml
element: { ref, type, x, z, w, d, h, y, rot, color, label }
top:     { bounds:{w,d}, walls:[...], docks:[...], facilities:[...], zones:[...], corridors:[...] }
```

- `x/z/w/d`：地面投影（中心 `cx=x+w/2, cz=z+d/2`）。
- `h`：高度(m)；缺省时由注册表 `default_h` 兜底。
- `y`：离地高度(m)，如月台 `y=0.3`、集装箱堆垛 `y=0`（落地）。
- `rot`：绕 Y 轴旋转(度)。
- `color`：覆盖色 `#rrggbb`；缺省由注册表取。
- `label`：可选显示标签（中文/英文）。
- `docks` 仅放月台类（`truck_dock / rail_dock / ship_dock`），其余布局元素入 `zones`，二者不重叠。

转换器在 M2 读取此结构；`docks` 与 `zones` 都映射为 mujoco body（见 §3.1）。

> 原旧 `FloorShell`（`bounds/zones/floors`）仍为后端 ORM 读取格式；本设计以 `wt_floor_shell` 作为
> `geometry_json` 落库与渲染的**唯一权威 schema**，M1 的 Python 构建器应同步产出 `wt_floor_shell`
> 兼容的 geometry（或以后以 SQL 播种的 JSON 为准，Python 仅作幂等刷新）。

### 2.2 zone-type → mujoco body 注册表

新文件 `rcs/services/control/map_mjcf.py` 内定义 `ZONE_BODY_TEMPLATES`：

```python
ZONE_BODY_TEMPLATES: dict[str, dict] = {
    # type: {shape, default_h, color, opacity, label_zh}
    "flow_rack":      {"shape": "box", "default_h": 3.0, "color": "#f59e0b", "opacity": 0.85},
    "high_rack":      {"shape": "box", "default_h": 6.0, "color": "#d97706", "opacity": 0.9},
    "mezzanine":      {"shape": "box", "default_h": 2.0, "color": "#a16207", "opacity": 0.8},
    "automated":      {"shape": "box", "default_h": 5.0, "color": "#0ea5e9", "opacity": 0.8},
    "temp":           {"shape": "box", "default_h": 2.5, "color": "#84cc16", "opacity": 0.8},
    "temp_bagged":    {"shape": "box", "default_h": 2.5, "color": "#65a30d", "opacity": 0.8},
    "returns":        {"shape": "box", "default_h": 2.0, "color": "#ef4444", "opacity": 0.8},
    "staging":        {"shape": "box", "default_h": 0.6, "color": "#94a3b8", "opacity": 0.6},
    "production_line": {"shape": "box", "default_h": 1.5, "color": "#64748b", "opacity": 0.85},
    "wip_buffer":     {"shape": "box", "default_h": 1.0, "color": "#475569", "opacity": 0.8},
    "parts_storage":  {"shape": "box", "default_h": 3.0, "color": "#334155", "opacity": 0.8},
    "frozen_zone":    {"shape": "box", "default_h": 3.0, "color": "#3b82f6", "opacity": 0.85},
    "cold_zone":      {"shape": "box", "default_h": 3.0, "color": "#60a5fa", "opacity": 0.85},
    "ambient_zone":   {"shape": "box", "default_h": 3.0, "color": "#cbd5e1", "opacity": 0.7},
    "loading_bay":    {"shape": "box", "default_h": 0.4, "color": "#fbbf24", "opacity": 0.7},
    "platform":       {"shape": "box", "default_h": 1.2, "color": "#eab308", "opacity": 0.9},
    "container_yard": {"shape": "box", "default_h": 0.3, "color": "#10b981", "opacity": 0.6},
    "customs_area":   {"shape": "box", "default_h": 2.5, "color": "#8b5cf6", "opacity": 0.8},
    "returns_received":{"shape": "box", "default_h": 2.0, "color": "#ef4444", "opacity": 0.8},
    "qc_staging":     {"shape": "box", "default_h": 1.5, "color": "#f87171", "opacity": 0.8},
    "reshelving":     {"shape": "box", "default_h": 3.0, "color": "#fca5a5", "opacity": 0.8},
    "disposal":       {"shape": "box", "default_h": 2.0, "color": "#dc2626", "opacity": 0.8},
    "floor_1":        {"shape": "box", "default_h": 4.0, "color": "#64748b", "opacity": 0.8},
    "floor_2":        {"shape": "box", "default_h": 4.0, "color": "#475569", "opacity": 0.8},
    "floor_3":        {"shape": "box", "default_h": 4.0, "color": "#334155", "opacity": 0.8},
    "elevator_shaft": {"shape": "cylinder", "default_h": 12.0, "color": "#22d3ee", "opacity": 0.5},
    # —— 新增装卸类型 ——
    "rail_track":     {"shape": "box", "default_h": 0.3, "color": "#44403c", "opacity": 0.9},
    "train_car":      {"shape": "box", "default_h": 4.0, "color": "#7c2d12", "opacity": 0.9},
    "truck":          {"shape": "box", "default_h": 3.5, "color": "#1f2937", "opacity": 0.9},
    # —— 月台 / 设施（来自 wt_floor_shell 的 docks / facilities）——
    "truck_dock":     {"shape": "box", "default_h": 0.4, "color": "#fbbf24", "opacity": 0.7},
    "rail_dock":      {"shape": "box", "default_h": 0.4, "color": "#f59e0b", "opacity": 0.7},
    "ship_dock":      {"shape": "box", "default_h": 0.4, "color": "#fcd34d", "opacity": 0.7},
    "office":         {"shape": "box", "default_h": 3.0, "color": "#a78bfa", "opacity": 0.85},
}
```

新增 zone / dock 类型只需加一条字典项，**零逻辑改动**即可被转换器与编辑器识别。
`docks` 里的 `truck_dock/rail_dock/ship_dock` 与 `zones` 共用同一注册表（按 `type` 查 `default_h/color`）。

---

## 3. 后端 `/mjcf` 接口 + 转换器

### 3.1 转换器 `rcs/services/control/map_mjcf.py`

```python
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

def build_mjcf(map_dict: dict) -> str:
    """将 UnifiedMap 行(dict)的 geometry_json 转为 MUJOCO .xml 字符串。"""
    geo = map_dict.get("geometry") or map_dict.get("geometry_json") or {}
    root = ET.Element("mujoco", model=map_dict.get("map_id", "scene"))
    # asset: 为每个用到的 color 注册一个 material
    assets = ET.SubElement(root, "asset")
    world = ET.SubElement(root, "worldbody")
    # 地面
    ET.SubElement(world, "geom", type="plane", name="floor",
                  pos="0 0 0", size="500 500 0.1", rgba="0.8 0.8 0.8 1")
    # 光照 + 相机
    ET.SubElement(world, "light", pos="0 50 50", directional="true")
    ET.SubElement(world, "camera", name="scene_cam", pos="40 40 40",
                  xyaxes="0 -1 0 0.3 0 0.95")
    # 遍历 zones + docks（wt_floor_shell：二者都映射为 body）
    color_seen: set[str] = set()
    for z in _iter_elements(geo):
        tpl = ZONE_BODY_TEMPLATES.get(z["type"], ZONE_BODY_TEMPLATES["staging"])
        h = z.get("h") or tpl["default_h"]
        y = z.get("y", 0.0)
        rot = z.get("rot", 0.0)
        color = z.get("color") or tpl["color"]
        mat = _ensure_material(assets, color_seen, color)
        cx = z["x"] + z["w"] / 2
        cz = z["z"] + z["d"] / 2
        cy = y + h / 2
        body = ET.SubElement(world, "body", name=z["id"], pos=f"{cx} {cy} {cz}")
        if rot:
            body.set("euler", f"0 {rot} 0")
        ET.SubElement(body, "geom", type=tpl["shape"],
                      size=_geo_size(tpl["shape"], z["w"], h, z["d"]),
                      material=mat,
                      rgba=f"{_hex_to_rgb(color)} {tpl['opacity']}")
        if z.get("label"):
            ET.SubElement(body, "site", type="box", size="0.5 0.5 0.5",
                          name=f"label_{z['id']}")
    return ET.tostring(root, encoding="unicode")
```

辅助函数：`_iter_elements`（展开 `zones` + `docks`）、
`_ensure_material`、`_geo_size`（box→半边长 / cylinder→半径,半高）、`_hex_to_rgb`。
用标准库 `xml.etree` 拼装，输出可被 mujoco / MjcfLoader 解析。
`wt_floor_shell` 已把楼层纵向位置写进各元素的 `y` 字段（如 `floor_2` 的 `y=4.0`），
故无需再展开 `floors[]` 叠加偏移。

### 3.2 接口

在 `rcs/api/control/control_unified_maps.py` 增加：

```python
@router.get("/maps/{map_id}/mjcf")
async def get_map_mjcf(map_id: str, download: bool = False):
    m = await svc.get(map_id)
    if not m:
        raise HTTPException(404, "map not found")
    xml = build_mjcf(m)
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{map_id}.mjcf.xml"'
    return Response(content=xml, media_type="application/xml", headers=headers)
```

模板与实例均可调用；`?download=1` 用于 mujoco 离线仿真。

---

## 4. 前端地图管理模块

### 4.1 路由（`src/router/index.ts`）

| path | 视图 | 说明 |
|------|------|------|
| `/maps` | `MapsListView.vue` | 模板+实例目录（卡片） |
| `/maps/:id` | `MapDetailView.vue` | 详情 + 3D 查看 |
| `/maps/:id/edit` | `MapEditorView.vue` | Zone 编辑器 |
| `/maps/new` | 复用 `MapEditorView.vue`（空白）或 `/maps?clone=<key>` | 从模板克隆新建 |

### 4.2 视图组件

- **`MapsListView.vue`**：卡片列表，区分"模板/实例"徽标；每张卡操作：`查看 / 克隆 / 编辑 / 删除`。
  - 克隆：弹窗输入新名称 → `POST /api/rcs/maps/from-template?key=<map_id 去前缀>`。
- **`MapDetailView.vue`**：左栏元信息（name / bounds / zones 表 + 业务属性）；右栏
  `ThreeMapViewer.vue`——`fetch(/api/rcs/maps/{id}/mjcf)` 拿到 MJCF 字符串，传给现有
  `MjcfLoader`（three.js）在 `WarehouseScene` 容器中渲染。
- **`MapEditorView.vue`**：zones 表格编辑器（增/删/改 Zone 字段：type/x/z/w/d/h/y/rot/color/label），
  保存调 `PUT /api/rcs/maps/{id}`（复用现有 `update`）。保存后详情 3D 视图即时变化（单一数据源）。

### 4.3 复用现有管线

`WarehouseScene.vue` / `MjcfLoader.ts` 已能把 MJCF XML → three.js meshes，本模块不重复造轮子，
仅新增一个"取 `/mjcf` 字符串再喂给 loader"的 `ThreeMapViewer` 包装组件。

### 4.4 菜单与 i18n

- `stores/auth.ts` 菜单加 `场景地图 / Scene Maps`（权限位 `sys:map:list`）。
- 4 个 locale（`zh-CN/en-US/ja-JP/zh-TW`）加模块文案：场景地图、模板、实例、克隆、月台、货车、火车、多层仓库等。

---

## 5. SQL `001_init.sql` 播种（已回填 13 套变体）

`001_init.sql` 末尾已追加 **第 8 节 · Scene-map scenario templates**：13 条幂等 `INSERT`
（单一 `VALUES` 批量 + `ON CONFLICT (map_id) DO UPDATE`）。数据由生成器
`scripts/gen_scene_maps_sql.py` 从 `docs/superpowers/specs/scene-map-templates.json` 导出，
**请勿手工编辑该节 JSON 字面量**，改数据请改 JSON 后重跑生成器。

- 字段顺序：`(map_id, name, name_en, is_template, kind, current_version, bounds_json,
  geometry_json, topology_json, semantic_json, dynamic_json, data)`。
- `geometry_json` = 对应场景的 `wt_floor_shell` 完整对象（`bounds/walls/docks/facilities/zones/corridors`），
  已校验 13 行 × 6 个 JSON 列共 78 个 `::json` 字面量均可解析。
- `bounds_json` = `{"w":..,"d":..}`（多层仓库附 `"h"`）。
- `semantic_json` 含 `scenario/variant/reference`，`train_unload` 额外带
  `flow:["rail_track","train_car","platform","truck"]`。
- 主变体 `map_id`（`tpl-ecommerce` / `tpl-train_unload` / `tpl-manufacturing` / `tpl-port` /
  `tpl-scn-cold_chain` / `tpl-scn-reverse_logistics` / `tpl-multi_floor`）与 Python `SCENARIO_IDS`
  同键；6 套备选变体加 `-2` 后缀，仅 SQL 播种。
- `map_id` 是主键，`ON CONFLICT (map_id)` 合法（此前已确认主键存在）。

> 13 套模板的字段结构、场景要点与数据来源详见同级 `scene-map-templates.md`（目录）与
> `scene-map-templates.json`（数据）。

---

## 6. 里程碑与验证

| 里程碑 | 内容 | 验证 |
|--------|------|------|
| M1 | 对齐 `geometry_json` 为 `wt_floor_shell` 结构；新增 `train_unload` 构建器；`SCENARIO_IDS` 加 `'train_unload'`；保留 `multi_floor` | `seed_templates()` 跑通，7 个主变体行入库（与 SQL 同键） |
| M2 | `map_mjcf.py` 注册表 + `build_mjcf`（遍历 zones+docks）+ `/mjcf` 接口 | 单测：输出能被 `xml.etree` 解析且含 floor 与各 body；`GET /mjcf` 返回合法 XML |
| M3 | 前端列表/详情/克隆 + `ThreeMapViewer` | 浏览器打开 13 套模板均能 3D 渲染 |
| M4 | 前端 `MapEditorView` Zone/Dock CRUD | 改一个 zone 保存后 3D 视图即时变化 |
| M5 | `001_init.sql` 已回填 13 套变体（§5）；`train_unload` 为主变体、保留 `multi_floor` | 全新库执行迁移后 `list_templates` 见 13 行 |
| M6 | 菜单 + 4 语言 i18n + router/main 接线 | 导航出现"场景地图"，中/英/日/繁均正常 |

---

## 7. 风险与注意

- **数据源一致性**：SQL 播种以 `wt_floor_shell` 为权威 schema；Python `seed_templates()` 的 7 个主变体 `map_id` 与 SQL 同键，刷新互不覆盖。改布局数据请改 `scene-map-templates.json` 后重跑 `scripts/gen_scene_maps_sql.py`，保持 SQL 与 JSON 同源（不再手工维护 SQL 字面量）。
- **MJCF 复杂度**：仅用 box/cylinder + 材质，不做关节/动力学，纯几何可视化，足够"查看地图"。
- **多楼层渲染**：`wt_floor_shell` 已把楼层纵向位置写进各元素 `y` 字段，转换器直接读 `y` 即可，无需再展开 `floors[]`。
- **依赖**：复用现有 `MjcfLoader`/three.js；后端仅用标准库 `xml.etree`，无新依赖。

---

## 8. 免责声明

本设计为功能实现规划文档，描述系统如何管理场景地图模板并以 MJCF 三维可视化，不构成任何投资或业务建议。
