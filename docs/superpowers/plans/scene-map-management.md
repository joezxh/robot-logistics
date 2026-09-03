# 执行计划：场景地图管理模块（Scene Map Management）

> **技能**：`writing-plans` · **依据设计**：`docs/superpowers/specs/scene-map-management.md`
> **数据来源**：`docs/superpowers/specs/scene-map-templates.json`（13 套 `wt_floor_shell`）、`scene-map-templates.md`
> **已落地**：`001_init.sql` 第 8 节已回填 13 套变体（提交 `3785fc2`）

## Context（背景）
后端 `robot_unified_maps` 表与 `/api/rcs/maps` 全套 CRUD 已存在，但**前端没有地图管理模块**，且场景模板仅由 Python `seed_templates()` 播种（6 场景 + 8 仓库）。本次目标：以 `geometry_json`（`wt_floor_shell` 结构）为唯一数据源，提供 **(a) 后端 MJCF 转换接口**（`/mjcf`）+ **(b) 前端完整 CRUD + 3D 查看 + 克隆** 的管理模块，并按既有"仿真中心"模式挂到侧边栏。

## 已锁定决策（来自设计文档）
1. **播种**：混合并存 / `001_init.sql` 已写 13 套变体（7 个场景主变体 `map_id` 与 Python `SCENARIO_IDS` 同键，6 套备选变体 `-2` 后缀）。
2. **数据模型**：`geometry_json` = `wt_floor_shell`（`bounds/walls/docks/facilities/zones/corridors`，元素固定 11 字段 `ref,type,x,z,w,d,h,y,rot,color,label`）。
3. **3D 渲染**：后端 `map_mjcf.py` 读 `geometry_json` → 拼 MJCF → 前端 `MjcfLoader.load(url)` 渲染（复用 `RobotModelViewer.vue` 管线）。
4. **管理模块**：列表 / 详情 3D 查看 / 从模板克隆 / Zone·Dock CRUD 编辑器。
5. **挂载**：仿"仿真中心"——前端 `BUILT_IN_VIEWS` + `AppSidebar` 合成节点（无 DB 菜单改动）。

## 代码库锚点（关键文件）
- 后端路由：`rcs/backend/rcs/api/control/control_unified_maps.py`（`maps_router`，挂载于 `/api/rcs`）
- 后端服务：`rcs/backend/rcs/services/control/control_unified_maps.py`（`UnifiedMapService.get/list/list_templates/seed_templates/SCENARIO_IDS/_scn_*`）
- **新增** 转换器：`rcs/backend/rcs/services/control/map_mjcf.py`
- 前端 API：`rcs/frontend/src/api/map.ts`（`UnifiedMapApi`）
- 前端类型：`rcs/frontend/src/types/scenario.ts`（`UnifiedMapDTO`）
- 3D 模板：`rcs/frontend/src/views/simulation/three/RobotModelViewer.vue`、`MjcfLoader.ts`
- 路由/导航：`rcs/frontend/src/router/dynamic.ts`（`BUILT_IN_VIEWS`）、`rcs/frontend/src/layouts/components/AppSidebar.vue`
- i18n：`rcs/frontend/src/i18n/locales/{zh-CN,zh-TW,en-US,ja-JP}.ts`
- 测试：单测 `tests/unit/control/test_control_unified_maps.py`（需 PG）、`tests/unit/control/test_warehouse_converter.py`（模板）；集成 `tests/integration/test_unified_maps_api.py`（TestClient，需 PG）

## Definition of Done（完成标准）
- [ ] `GET /api/rcs/maps/{id}/mjcf` 对任何 13 套模板返回合法 mujoco XML（可被 `xml.etree` 与 `MjcfLoader` 解析）。
- [ ] 前端 `/maps` 列表展示 13 套模板；点详情在 three.js 中 3D 渲染出月台/货车/火车/货架等元素。
- [ ] "从模板克隆"可新建实例；编辑器可增删改 Zone/Dock 字段并保存，保存后 3D 即时变化。
- [ ] 4 语言侧边栏出现"场景地图"，中英日繁均正常。
- [ ] 单测 + 集成测试全绿。

---

## M1 — 后端转换器 `map_mjcf.py` + 种子对齐（wt_floor_shell）

### T1.1 新建 `rcs/backend/rcs/services/control/map_mjcf.py`
完整代码（含 zone/dock→mujoco body 注册表、FloorShell→wt 兼容转换）：

```python
"""Convert a unified-map `geometry_json` (wt_floor_shell) to a mujoco MJCF string.

Pure stdlib (xml.etree) — no third-party XML deps. Reads `zones` + `docks`
(both map to bodies); `walls`/`facilities`/`corridors` are kept in the schema
but rendered as plain bodies when present. Floors are flattened by the
`_floor_shell_to_wt` adapter so legacy FloorShell seeds produce the same schema.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from typing import Any, Iterable, Iterator

# zone/dock type -> mujoco body template. Add a key = support a new type.
ZONE_BODY_TEMPLATES: dict[str, dict[str, Any]] = {
    "flow_rack": {"shape": "box", "default_h": 2.2, "color": "#60a5fa", "opacity": 0.85},
    "high_rack": {"shape": "box", "default_h": 6.0, "color": "#3b82f6", "opacity": 0.9},
    "mezzanine": {"shape": "box", "default_h": 1.0, "color": "#93c5fd", "opacity": 0.6},
    "automated": {"shape": "box", "default_h": 3.5, "color": "#6366f1", "opacity": 0.9},
    "asrs": {"shape": "box", "default_h": 8.0, "color": "#4338ca", "opacity": 0.9},
    "staging": {"shape": "box", "default_h": 0.3, "color": "#cbd5e1", "opacity": 0.6},
    "temp_cold": {"shape": "box", "default_h": 4.0, "color": "#67e8f9", "opacity": 0.85},
    "temp_frozen": {"shape": "box", "default_h": 4.0, "color": "#22d3ee", "opacity": 0.85},
    "returns": {"shape": "box", "default_h": 1.5, "color": "#fca5a5", "opacity": 0.85},
    "production_line": {"shape": "box", "default_h": 1.2, "color": "#facc15", "opacity": 0.8},
    "wip_buffer": {"shape": "box", "default_h": 1.0, "color": "#fde047", "opacity": 0.7},
    "parts_storage": {"shape": "box", "default_h": 3.0, "color": "#a3e635", "opacity": 0.85},
    "container_yard": {"shape": "box", "default_h": 2.6, "color": "#34d399", "opacity": 0.85},
    "customs_area": {"shape": "box", "default_h": 2.0, "color": "#10b981", "opacity": 0.8},
    "reefer": {"shape": "box", "default_h": 2.9, "color": "#14b8a6", "opacity": 0.85},
    "frozen_zone": {"shape": "box", "default_h": 4.0, "color": "#22d3ee", "opacity": 0.85},
    "cold_zone": {"shape": "box", "default_h": 4.0, "color": "#67e8f9", "opacity": 0.85},
    "ambient_zone": {"shape": "box", "default_h": 4.0, "color": "#94a3b8", "opacity": 0.8},
    "returns_received": {"shape": "box", "default_h": 1.5, "color": "#fca5a5", "opacity": 0.85},
    "qc_staging": {"shape": "box", "default_h": 1.2, "color": "#fdba74", "opacity": 0.8},
    "reshelving": {"shape": "box", "default_h": 2.0, "color": "#86efac", "opacity": 0.8},
    "disposal": {"shape": "box", "default_h": 1.5, "color": "#f87171", "opacity": 0.8},
    "rail_track": {"shape": "box", "default_h": 0.3, "color": "#44403c", "opacity": 0.9},
    "train_car": {"shape": "box", "default_h": 4.0, "color": "#7c2d12", "opacity": 0.9},
    "truck": {"shape": "box", "default_h": 3.5, "color": "#1f2937", "opacity": 0.9},
    "truck_dock": {"shape": "box", "default_h": 0.4, "color": "#fbbf24", "opacity": 0.7},
    "rail_dock": {"shape": "box", "default_h": 0.4, "color": "#f59e0b", "opacity": 0.7},
    "ship_dock": {"shape": "box", "default_h": 0.4, "color": "#fcd34d", "opacity": 0.7},
    "office": {"shape": "box", "default_h": 3.0, "color": "#a78bfa", "opacity": 0.85},
    "elevator_shaft": {"shape": "box", "default_h": 12.0, "color": "#64748b", "opacity": 0.5},
    "default": {"shape": "box", "default_h": 1.5, "color": "#94a3b8", "opacity": 0.8},
}

_ELEM_KEYS = ("ref", "type", "x", "z", "w", "d", "h", "y", "rot", "color", "label")


def _hex_to_rgba(hex_color: str, opacity: float = 1.0) -> str:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return f"{r:.3f} {g:.3f} {b:.3f} {opacity:.3f}"


def _normalize(el: dict) -> dict:
    """Coerce an element dict to the 11-field shape with registry-backed defaults."""
    etype = el.get("type", "default")
    tpl = ZONE_BODY_TEMPLATES.get(etype, ZONE_BODY_TEMPLATES["default"])
    return {
        "id": el.get("id") or el.get("ref") or etype,
        "type": etype,
        "x": float(el.get("x", 0)),
        "z": float(el.get("z", 0)),
        "w": float(el.get("w", 1)),
        "d": float(el.get("d", 1)),
        "h": float(el.get("h") or tpl["default_h"]),
        "y": float(el.get("y", 0) or 0),
        "rot": float(el.get("rot", 0) or 0),
        "color": el.get("color") or tpl["color"],
        "label": el.get("label"),
    }


def _iter_elements(geo: dict) -> Iterator[dict]:
    for key in ("zones", "docks", "walls", "facilities", "corridors"):
        for el in geo.get(key, []) or []:
            yield _normalize(el)


def _ensure_material(asset: ET.Element, seen: set[str], color: str, opacity: float) -> str:
    mat = "mat_" + color.lstrip("#")
    if mat not in seen:
        seen.add(mat)
        ET.SubElement(asset, "material", {"name": mat, "rgba": _hex_to_rgba(color, opacity)})
    return mat


def _add_body(world: ET.Element, z: dict, tpl: dict, mat: str) -> None:
    cx = z["x"] + z["w"] / 2
    cz = z["z"] + z["d"] / 2
    cy = z["y"] + z["h"] / 2
    attrs = {"name": str(z["id"]), "pos": f"{cx:.3f} {cy:.3f} {cz:.3f}"}
    if z["rot"]:
        attrs["euler"] = f"0 {z['rot']:.3f} 0"
    body = ET.SubElement(world, "body", attrs)
    geom = ET.SubElement(
        body, "geom",
        {"type": tpl["shape"], "material": mat, "mass": "0",
         "contype": "0", "conaffinity": "0"},
    )
    if tpl["shape"] == "box":
        geom.set("size", f"{z['w'] / 2:.3f} {z['h'] / 2:.3f} {z['d'] / 2:.3f}")
    else:
        r = min(z["w"], z["d"]) / 2
        geom.set("size", f"{r:.3f} {z['h'] / 2:.3f}")
    if z["label"]:
        ET.SubElement(body, "site", {"type": "box", "size": "0.1 0.1 0.1", "rgba": "0 0 0 0"})


def build_mjcf(map_dict: dict) -> str:
    """Build a mujoco MJCF string for a unified map row (dict from service.get)."""
    geo = map_dict.get("geometry") or map_dict.get("geometry_json") or {}
    if isinstance(geo, str):
        geo = json.loads(geo)
    geo = geo or {}

    m = ET.Element("mujoco", {"model": str(map_dict.get("map_id", "scene"))})
    asset = ET.SubElement(m, "asset")
    world = ET.SubElement(m, "worldbody")

    # ground + lights
    ET.SubElement(world, "geom", {"name": "ground", "type": "plane",
                                  "pos": "0 0 0", "size": "300 300 0.1",
                                  "rgba": "0.82 0.84 0.86 1"})
    ET.SubElement(world, "light", {"pos": "-6 10 6", "dir": "0 -1 -0.3",
                                   "diffuse": "0.9 0.9 0.9", "specular": "0.2 0.2 0.2"})
    ET.SubElement(world, "light", {"pos": "6 10 -6", "dir": "0 -1 0.3",
                                   "diffuse": "0.7 0.7 0.7"})
    ET.SubElement(world, "light", {"pos": "0 14 0", "dir": "0 -1 0",
                                   "diffuse": "0.5 0.5 0.5"})

    seen: set[str] = set()
    for z in _iter_elements(geo):
        tpl = ZONE_BODY_TEMPLATES.get(z["type"], ZONE_BODY_TEMPLATES["default"])
        mat = _ensure_material(asset, seen, z["color"], tpl.get("opacity", 0.85))
        _add_body(world, z, tpl, mat)

    ET.register_namespace("", "http://www.mujoco.org")
    raw = ET.tostring(m, encoding="unicode")
    # pretty print
    from xml.dom import minidom
    return minidom.parseString(raw).toprettyxml(indent="  ")


def _floor_shell_to_wt(shell: dict, semantic: dict | None = None) -> dict:
    """Convert a legacy FloorShell dict (bounds/zones/floors) to wt_floor_shell.

    Used so the 6 existing Python scenario builders seed the SAME schema as the
    SQL-templated rows. `loading_bay` zones become `docks` (truck_dock);
    multi-floor zones get a `y` offset per floor index.
    """
    out: dict = {
        "bounds": {"w": shell.get("bounds", {}).get("w"),
                   "d": shell.get("bounds", {}).get("d")},
        "walls": [], "docks": [], "facilities": [], "zones": [], "corridors": [],
    }
    floors = shell.get("floors") or []
    if floors:
        for fi, fz in enumerate(floors):
            y0 = fi * 4.0  # 4m per floor
            for z in fz.get("zones", []) or []:
                out["zones"].append(_convert_one_zone(z, y0))
    else:
        for z in shell.get("zones", []) or []:
            out["zones"].append(_convert_one_zone(z, 0.0))
    if semantic:
        out["semantic"] = semantic
    return out


def _convert_one_zone(z: dict, y0: float) -> dict:
    zt = z.get("type")
    base = {
        "ref": z.get("id") or z.get("ref"),
        "type": zt,
        "x": z.get("x", 0), "z": z.get("z", 0),
        "w": z.get("w", 1), "d": z.get("d", 1),
        "h": None, "y": y0, "rot": 0, "color": None, "label": zt,
    }
    if zt in ("loading_bay", "dock", "truck_dock"):
        base["type"] = "truck_dock"
        base["y"] = y0 + 0.3
        base["h"] = 0.4
        return base  # goes to docks below
    return base
```

> 注意：上面 `_convert_one_zone` 对 `loading_bay` 返回 `truck_dock` 元素；在 `_floor_shell_to_wt` 中需把这类元素分流到 `docks`。**请在该函数内**补一段：遍历 `out["zones"]` 把 `type=="truck_dock"` 的项移到 `out["docks"]`。为简洁此处省略该 3 行循环，实现时直接加：
> ```python
> out["docks"] = [z for z in out["zones"] if z["type"] == "truck_dock"]
> out["zones"] = [z for z in out["zones"] if z["type"] != "truck_dock"]
> ```

### T1.2 在 `control_unified_maps.py` 接入转换器 + `train_unload` 场景
1. 文件顶部新增：`from .map_mjcf import build_mjcf, _floor_shell_to_wt`。
2. `SCENARIO_IDS` 增加 `'train_unload'`（位置随意；不与仓库 key 冲突）。
3. 新增构建器（返回 **wt_floor_shell 字典**，直接进 `geometry_json`）：

```python
def _scn_train_unload() -> ScenarioBundle:
    """火车卸货 → 月台 → 大卡车 的 wt_floor_shell 布局（单线版）。"""
    W, D = 180, 80
    zones = [
        # 铁轨（沿 x 方向的长条）
        {"ref": "rail_1", "type": "rail_track", "x": 10, "z": 8, "w": 150, "d": 8,
         "h": 0.3, "y": 0, "rot": 0, "color": "#44403c", "label": "铁轨"},
    ]
    # 3 节车厢停靠铁轨
    for i in range(3):
        zones.append({"ref": f"car_{i+1}", "type": "train_car", "x": 20 + i * 52, "z": 8,
                      "w": 15, "d": 6, "h": 4.0, "y": 1.0, "rot": 0,
                      "color": "#7c2d12", "label": f"车厢{i+1}"})
    # 月台（平行车厢）
    zones.append({"ref": "platform_1", "type": "platform", "x": 10, "z": 20, "w": 150, "d": 10,
                  "h": 1.0, "y": 0.3, "rot": 0, "color": "#a8a29e", "label": "卸货月台"})
    # 3 辆大卡车在月台外侧
    for i in range(3):
        zones.append({"ref": f"truck_{i+1}", "type": "truck", "x": 20 + i * 52, "z": 40,
                      "w": 13.6, "d": 2.6, "h": 3.5, "y": 0, "rot": 0,
                      "color": "#1f2937", "label": f"大卡车{i+1}"})
    # 暂存区
    zones.append({"ref": "staging_1", "type": "staging", "x": 10, "z": 55, "w": 150, "d": 18,
                  "h": 0.3, "y": 0, "rot": 0, "color": "#cbd5e1", "label": "暂存区"})
    shell = {"bounds": {"w": W, "d": D}, "walls": [], "docks": [],
             "facilities": [], "zones": zones, "corridors": []}
    return ScenarioBundle(
        shell=ShellAdapter(shell),  # 见下方说明
        metadata={"kind": "scenario", "scenario": "train_unload",
                  "flow": ["rail_track", "train_car", "platform", "truck"]},
    )
```

> **说明**：现有 `_scn_*` 返回 `ScenarioBundle(..., shell=FloorShell(...))`。为不改动 `ScenarioBundle`/`FloorShell` 类型，给 `train_unload` 一个轻量 `ShellAdapter`：`class ShellAdapter: def __init__(self,d): self.shell=d; self.zones=d.get("zones",[]); self.floors=[]`。`seed_templates` 读取 `b.shell.bounds`/`b.shell.zones`/`b.shell.floors`——`ShellAdapter` 暴露这些属性即可。
4. 修改 `seed_templates` 的循环，使 `geometry_json` 统一为 wt：
```python
for sid in SCENARIO_IDS:
    b = _SCENARIO_BUILDERS[sid]()
    shell = b.shell
    wt = _floor_shell_to_wt(
        {"bounds": getattr(shell, "bounds", {}),
         "zones": getattr(shell, "zones", []),
         "floors": getattr(shell, "floors", [])},
        b.metadata,
    )
    m.geometry_json = wt
    m.bounds_json = wt["bounds"]
    m.semantic_json = b.metadata
```
（`train_unload` 的 `ShellAdapter.shell` 已是 wt dict，`_floor_shell_to_wt` 会再包一层——可接受；或在 `seed_templates` 中特判 `isinstance(shell, ShellAdapter)` 直接 `m.geometry_json = shell.shell`。**实现时**对 `train_unload` 直接赋 `shell.shell`。）
5. `_list_scenario_infos` 已读 `b.shell.bounds`/`b.shell.zones`/`b.shell.floors`；`ShellAdapter` 提供这些属性后无需改。

### T1.3 单测 `tests/unit/control/test_map_mjcf.py`（TDD，先写后实现）
```python
import xml.etree.ElementTree as ET
from rcs.services.control.map_mjcf import build_mjcf, _floor_shell_to_wt

def _wt():
    return {"bounds": {"w": 120, "d": 80}, "walls": [], "docks": [],
            "facilities": [], "corridors": [],
            "zones": [
                {"ref": "r1", "type": "high_rack", "x": 10, "z": 10, "w": 20, "d": 5},
                {"ref": "d1", "type": "truck_dock", "x": 0, "z": 70, "w": 12, "d": 4, "y": 0.3},
            ]}

def test_build_mjcf_parses_and_has_bodies():
    xml = build_mjcf({"map_id": "tpl-x", "geometry": _wt()})
    root = ET.fromstring(xml)
    assert root.tag == "mujoco"
    world = root.find("worldbody")
    bodies = world.findall("body")
    # 2 zones + ground geom (geom not body) -> 2 bodies
    assert len(bodies) == 2
    mats = root.find("asset").findall("material")
    assert mats  # at least one material
    # rotation field optional; ensure turtle dock has y offset applied
    pos = bodies[1].get("pos")
    assert pos.startswith("6.0")  # dock center x = 0 + 12/2

def test_floor_shell_to_wt_splits_docks():
    fs = {"bounds": {"w": 100, "d": 80},
          "zones": [{"id": "z1", "type": "high_rack", "x": 0, "z": 0, "w": 10, "d": 10},
                    {"id": "b1", "type": "loading_bay", "x": 0, "z": 70, "w": 12, "d": 4}],
          "floors": []}
    wt = _floor_shell_to_wt(fs)
    assert any(z["type"] == "truck_dock" for z in wt["docks"])
    assert not any(z["type"] == "truck_dock" for z in wt["zones"])
```

### T1.4 更新既有 `test_control_unified_maps.py`
将 `test_seed_templates_creates_fourteen_rows` 改为断言 `len(rows) >= 15` 且 `'tpl-train_unload' in ids`（8 仓库 + 7 场景）。

### T1.5 验证 + 提交
```bash
cd rcs/backend
python -m pytest tests/unit/control/test_map_mjcf.py tests/unit/control/test_control_unified_maps.py -q
```
- 提交：`feat(maps): add map_mjcf converter + train_unload scenario (wt_floor_shell)`

---

## M2 — `/mjcf` API 路由 + 集成测试

### T2.1 在 `control_unified_maps.py`（API 路由文件）新增路由
```python
from fastapi import Response
from fastapi.responses import Response as FastResponse
from ..services.control.map_mjcf import build_mjcf

@maps_router.get("/maps/{map_id}/mjcf", summary="导出场景地图 MJCF (mujoco)")
async def get_map_mjcf(map_id: str, download: bool = False,
                       db: AsyncSession = Depends(get_db)):
    m = await map_svc.get(map_id)
    if m is None:
        raise HTTPException(status_code=404, detail="map not found")
    xml = build_mjcf(m)
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{map_id}.mjcf"'
    return Response(content=xml, media_type="application/xml", headers=headers)
```
> 路由与既有 `GET /maps/{map_id}` 不冲突（路径多一段 `/mjcf`）。`map_svc.get` 返回 dict，`build_mjcf` 读 `geometry`。

### T2.2 集成测试（追加到 `tests/integration/test_unified_maps_api.py`）
```python
def test_get_map_mjcf_returns_xml(client):
    r = client.get("/api/rcs/maps/tpl-ecommerce/mjcf")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/xml")
    root = ET.fromstring(r.text)
    assert root.tag == "mujoco"
    assert root.find("worldbody").findall("body")

def test_get_map_mjcf_download_header(client):
    r = client.get("/api/rcs/maps/tpl-ecommerce/mjcf?download=1")
    assert r.status_code == 200
    assert "attachment" in r.headers.get("content-disposition", "")

def test_get_map_mjcf_404(client):
    assert client.get("/api/rcs/maps/nope/mjcf").status_code == 404
```

### T2.3 验证 + 提交
```bash
cd rcs/backend
python -m pytest tests/integration/test_unified_maps_api.py::test_get_map_mjcf_returns_xml -q
```
- 提交：`feat(maps): add GET /maps/{id}/mjcf endpoint + integration tests`

---

## M3 — 前端：列表 / 详情 3D 查看 / 克隆 + ThreeMapViewer

### T3.1 `src/api/map.ts` 增加方法
```ts
import type { UnifiedMapDTO } from '@/types/scenario'

export function getMapMjcfUrl(id: string): string {
  return `/api/rcs/maps/${id}/mjcf`
}
export function getTemplates(): Promise<UnifiedMapDTO[]> {
  return request.get('/api/rcs/maps/templates')
}
export function cloneMap(templateId: string, payload: { name?: string; name_en?: string }): Promise<UnifiedMapDTO> {
  return request.post(`/api/rcs/maps/from-template?template_id=${templateId}`, payload)
}
// 假设已存在：getMap(id) / updateMap(id, payload) / deleteMap(id)
```

### T3.2 新建 `src/views/maps/ThreeMapViewer.vue`（克隆自 RobotModelViewer.vue）
```vue
<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { MjcfLoader } from '@/views/simulation/three/MjcfLoader'
import { getMapMjcfUrl, getMap } from '@/api/map'

const props = defineProps<{ mapId: string }>()
const container = ref<HTMLDivElement | null>(null)
let renderer: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.PerspectiveCamera
let controls: OrbitControls, raf = 0, current: THREE.Group | null = null

async function load() {
  const url = getMapMjcfUrl(props.mapId)
  const r = await MjcfLoader.load(url, { baseUrl: url, fixBaseLink: true })
  if (current) scene.remove(current)
  current = r.root
  scene.add(current)
  // center camera on map bounds
  const m = await getMap(props.mapId).catch(() => null)
  const w = m?.bounds?.w ?? 100, d = m?.bounds?.d ?? 80
  controls.target.set(w / 2, 0, d / 2)
  camera.position.set(w / 2, Math.max(w, d) * 0.7, d / 2 + Math.max(w, d) * 0.7)
  controls.update()
}
function animate() { raf = requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera) }
function resize() {
  if (!container.value) return
  const w = container.value.clientWidth, h = container.value.clientHeight
  renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix()
}
onMounted(async () => {
  scene = new THREE.Scene(); scene.background = new THREE.Color('#0b1020')
  camera = new THREE.PerspectiveCamera(50, 1, 0.1, 2000)
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setPixelRatio(window.devicePixelRatio)
  container.value!.appendChild(renderer.domElement)
  controls = new OrbitControls(camera, renderer.domElement)
  scene.add(new THREE.GridHelper(300, 60, 0x334155, 0x1e293b))
  animate(); resize(); window.addEventListener('resize', resize)
  await load()
})
watch(() => props.mapId, load)
onBeforeUnmount(() => {
  cancelAnimationFrame(raf); window.removeEventListener('resize', resize)
  controls?.dispose(); renderer?.dispose()
})
</script>
<template><div ref="container" class="map-viewer" /></template>
<style scoped>.map-viewer { width: 100%; height: 100%; min-height: 480px; }</style>
```

### T3.3 新建 `src/views/maps/MapsListView.vue`
```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getTemplates, cloneMap, deleteMap } from '@/api/map'
import type { UnifiedMapDTO } from '@/types/scenario'

const router = useRouter()
const list = ref<UnifiedMapDTO[]>([])
onMounted(async () => { list.value = await getTemplates() })

async function onClone(t: UnifiedMapDTO) {
  const inst = await cloneMap(t.map_id, { name: `${t.name}(副本)` })
  router.push(`/maps/${inst.map_id}/edit`)
}
async function onDelete(t: UnifiedMapDTO) {
  if (!confirm(`删除 ${t.name}?`)) return
  await deleteMap(t.map_id); list.value = list.value.filter(x => x.map_id !== t.map_id)
}
</script>
<template>
  <div class="maps-page">
    <h2>{{ $t('maps.list') }}</h2>
    <div class="grid">
      <div v-for="t in list" :key="t.map_id" class="card">
        <div class="card-title">{{ t.name }} <small>{{ t.name_en }}</small></div>
        <div class="card-meta">map_id: {{ t.map_id }}</div>
        <div class="card-actions">
          <button @click="router.push(`/maps/${t.map_id}`)">{{ $t('maps.view3d') }}</button>
          <button @click="onClone(t)">{{ $t('maps.clone') }}</button>
          <button @click="router.push(`/maps/${t.map_id}/edit`)">{{ $t('maps.edit') }}</button>
          <button class="danger" @click="onDelete(t)">{{ $t('maps.delete') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.card { border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; background: var(--bg-surface); }
.card-title { font-weight: 600; font-size: 15px; }
.card-meta { color: var(--fg-muted); font-size: 12px; margin: 6px 0 12px; }
.card-actions { display: flex; flex-wrap: wrap; gap: 8px; }
button { border: 1px solid var(--border); background: var(--bg-input); color: var(--fg); border-radius: var(--radius-sm); padding: 6px 10px; cursor: pointer; }
button.danger { color: #f87171; }
</style>
```

### T3.4 新建 `src/views/maps/MapDetailView.vue`
```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getMap } from '@/api/map'
import type { UnifiedMapDTO } from '@/types/scenario'
import ThreeMapViewer from './ThreeMapViewer.vue'

const route = useRoute()
const map = ref<UnifiedMapDTO | null>(null)
onMounted(async () => { map.value = await getMap(route.params.id as string) })
const zones = () => {
  const g: any = (map.value as any)?.geometry ?? {}
  return [...(g.zones ?? []), ...(g.docks ?? [])]
}
</script>
<template>
  <div v-if="map" class="detail">
    <div class="info">
      <h2>{{ map.name }} <small>{{ map.name_en }}</small></h2>
      <p>map_id: {{ map.map_id }}</p>
      <p>尺寸: {{ map.bounds?.w }} × {{ map.bounds?.d }} m</p>
      <table>
        <thead><tr><th>ref</th><th>type</th><th>x</th><th>z</th><th>w</th><th>d</th><th>h</th></tr></thead>
        <tbody>
          <tr v-for="z in zones()" :key="z.ref">
            <td>{{ z.ref }}</td><td>{{ z.type }}</td><td>{{ z.x }}</td><td>{{ z.z }}</td>
            <td>{{ z.w }}</td><td>{{ z.d }}</td><td>{{ z.h }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="viewer"><ThreeMapViewer :map-id="map.map_id" /></div>
  </div>
</template>
<style scoped>
.detail { display: grid; grid-template-columns: 360px 1fr; gap: 16px; height: calc(100vh - 120px); }
.viewer { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th, td { border-bottom: 1px solid var(--divider); padding: 4px 6px; text-align: left; }
</style>
```

### T3.5 路由 + 侧边栏
`src/router/dynamic.ts` 的 `BUILT_IN_VIEWS` 增加：
```ts
'/maps': { component: 'views/maps/MapsListView.vue', name: 'MapsList', title: '场景地图' },
'/maps/new': { component: 'views/maps/MapEditorView.vue', name: 'MapNew', title: '新建地图' },
'/maps/:id': { component: 'views/maps/MapDetailView.vue', name: 'MapDetail', title: '地图详情' },
'/maps/:id/edit': { component: 'views/maps/MapEditorView.vue', name: 'MapEdit', title: '编辑地图' },
```

`src/layouts/components/AppSidebar.vue`：在 `SIMULATION_MENU` 后新增（仿照）：
```ts
const MAPS_MENU: MenuNode = {
  id: -2000, name: '场景地图',
  i18n: { 'zh-CN': '场景地图', 'zh-TW': '場景地圖', 'en-US': 'Scene Maps', 'ja-JP': 'シーンマップ' },
  path: '/maps', icon: 'GlobalOutlined', type: 1, sort: 998, status: 1, visible: 1,
  keepAlive: 0, alwaysShow: 1,
  children: [leaf(-2001, '场景模板', '/maps', 'GlobalOutlined')],
}
const menus = computed(() => [...auth.menus, SIMULATION_MENU, MAPS_MENU])
```

### T3.6 验证 + 提交
```bash
cd rcs/frontend
npx vue-tsc --noEmit && npm run build
```
- 提交：`feat(maps): add list/detail/clone views + ThreeMapViewer + nav`

---

## M4 — 前端 `MapEditorView.vue`（Zone/Dock CRUD）

### T4.1 新建 `src/views/maps/MapEditorView.vue`
```vue
<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getMap, updateMap, cloneMap } from '@/api/map'

const route = useRoute(); const router = useRouter()
const isNew = !!route.query.template_id
const mapId = ref<string>('')
const geo = reactive<{ bounds: any; walls: any[]; docks: any[]; facilities: any[]; zones: any[]; corridors: any[] }>(
  { bounds: { w: 100, d: 80 }, walls: [], docks: [], facilities: [], zones: [], corridors: [] }
)

async function load() {
  if (isNew) {
    const inst = await cloneMap(route.query.template_id as string, { name: '新建地图' })
    mapId.value = inst.map_id
  } else {
    mapId.value = route.params.id as string
  }
  const m = await getMap(mapId.value)
  Object.assign(geo, m.geometry ?? {})
}
function addZone() { geo.zones.push({ ref: `z${geo.zones.length + 1}`, type: 'staging', x: 0, z: 0, w: 5, d: 5, h: 0.3, y: 0, rot: 0, color: '#cbd5e1', label: '' }) }
function delZone(i: number) { geo.zones.splice(i, 1) }
async function save() {
  await updateMap(mapId.value, { geometry: JSON.parse(JSON.stringify(geo)) })
  router.push(`/maps/${mapId.value}`)
}
onMounted(load)
</script>
<template>
  <div class="editor">
    <h2>{{ isNew ? $t('maps.new') : $t('maps.edit') }}</h2>
    <button @click="addZone">+ Zone</button>
    <table>
      <thead><tr><th>ref</th><th>type</th><th>x</th><th>z</th><th>w</th><th>d</th><th>h</th><th>y</th><th>rot</th><th>color</th><th></th></tr></thead>
      <tbody>
        <tr v-for="(z, i) in geo.zones" :key="i">
          <td><input v-model="z.ref" /></td>
          <td><input v-model="z.type" /></td>
          <td><input type="number" v-model.number="z.x" /></td>
          <td><input type="number" v-model.number="z.z" /></td>
          <td><input type="number" v-model.number="z.w" /></td>
          <td><input type="number" v-model.number="z.d" /></td>
          <td><input type="number" v-model.number="z.h" /></td>
          <td><input type="number" v-model.number="z.y" /></td>
          <td><input type="number" v-model.number="z.rot" /></td>
          <td><input v-model="z.color" /></td>
          <td><button class="danger" @click="delZone(i)">×</button></td>
        </tr>
      </tbody>
    </table>
    <button class="primary" @click="save">{{ $t('maps.save') }}</button>
  </div>
</template>
<style scoped>
input { width: 76px; background: var(--bg-input); color: var(--fg); border: 1px solid var(--border); border-radius: 4px; }
.primary { background: var(--accent); color: var(--fg-inverse); border: none; padding: 8px 16px; border-radius: var(--radius-sm); cursor: pointer; }
.danger { color: #f87171; }
</style>
```
> `updateMap` 的 payload 沿用 `UnifiedMapUpdate.geometry`（后端 `update_map` 直接 `m.geometry_json = payload.geometry`，不校验类型），故发送 wt dict 安全。

### T4.2 验证 + 提交
```bash
cd rcs/frontend && npx vue-tsc --noEmit
```
- 提交：`feat(maps): add MapEditorView with zone/dock CRUD`

---

## M5 — SQL 播种校验（已回填，仅验证）
- T5.1 在全新库执行迁移后断言：`list_templates` 返回 13 行且包含 7 个主变体 `map_id`。
  ```bash
  cd rcs/backend
  python -c "import json,re,pathlib; s=pathlib.Path('migrations/001_init.sql').read_text(); sec=s.split('-- 8. Scene-map scenario templates',1)[1]; print('rows:', sec.count('(\'tpl-')); print('json ok:', all(__import__('json').loads(m.replace(\"''\",\"'\").replace('\\\\\\\\','\\\\')) for m in re.findall(r\"'([^']*)'::json\", sec, re.S))) )"
  ```
- 提交：无（仅验证，SQL 已在 `3785fc2` 落地）。

---

## M6 — i18n 四语言 + 收尾

### T6.1 四个 locale 文件增加 `maps` 命名空间
`zh-CN.ts` / `zh-TW.ts` / `en-US.ts` / `ja-JP.ts` 在根对象加：
```ts
maps: {
  title: '场景地图',          // zh-TW: '場景地圖'  en-US: 'Scene Maps'  ja-JP: 'シーンマップ'
  list: '场景模板',           // zh-TW: '場景模板'  en-US: 'Scene Templates'  ja-JP: 'シーンテンプレート'
  detail: '地图详情',         // zh-TW: '地圖詳情'  en-US: 'Map Detail'  ja-JP: 'マップ詳細'
  edit: '编辑地图',           // zh-TW: '編輯地圖'  en-US: 'Edit Map'  ja-JP: 'マップ編集'
  new: '新建地图',            // zh-TW: '新建地圖'  en-US: 'New Map'  ja-JP: '新規マップ'
  clone: '克隆',              // zh-TW: '複製'      en-US: 'Clone'   ja-JP: '複製'
  delete: '删除',             // zh-TW: '刪除'      en-US: 'Delete'  ja-JP: '削除'
  view3d: '3D 预览',          // zh-TW: '3D 預覽'  en-US: '3D Preview'  ja-JP: '3D プレビュー'
  save: '保存',               // zh-TW: '儲存'      en-US: 'Save'    ja-JP: '保存'
}
```

### T6.2 验证 + 提交
```bash
cd rcs/frontend && npm run build
```
- 提交：`feat(maps): add i18n (zh/en/ja/tw) for scene maps`

---

## 提交顺序（建议）
1. M1 转换器 + 种子对齐
2. M2 `/mjcf` 路由 + 测试
3. M3 前端列表/详情/克隆 + 3D
4. M4 编辑器
5. M6 i18n（M5 无提交）

每个任务提交前跑对应测试 / `vue-tsc --noEmit`。合并前在 dev server 手动验收：打开 `/maps` → 任一点"3D 预览"应渲染出对应元素；"克隆"后编辑保存，返回详情 3D 即时变化。
