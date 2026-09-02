# 7 个场景 · 13 套初始化场景地图模板数据目录

**生成脚本**：`scripts/gen_scene_templates.py`
**数据文件**：`docs/superpowers/specs/scene-map-templates.json`（`schema: wt_floor_shell`，共 13 套）
**结构基准**：大型电商仓库模板提取自 `warehouse_theatre_3d` 仓库 `DEFAULT_SHELL`
**数据来源**：见文末「数据来源」一节（含联网检索的真实参考值）

---

## 1. 统一结构（所有模板字段一致）

```json
{
  "meta": { "scenario", "variant", "name", "name_en", "note", "reference" },
  "bounds": { "w": <m>, "d": <m>, "h": <m 可选,建筑高> },
  "walls":      [ { ref, type, x, z, w, d, h, y, rot, color, label } ],
  "docks":      [ { ref, type, x, z, w, d, h, y, rot, color, label } ],   // type ∈ truck_dock|rail_dock|ship_dock
  "facilities": [ { ref, type, x, z, w, d, h, y, rot, color, label } ],
  "zones":      [ { ref, type, x, z, w, d, h, y, rot, color, label } ],
  "corridors":  [ { ref, type, x, z, w, d, h, y, rot, color, label } ],
  "floors":     [ { "level", "y", "zones": [ref...] } ]   // 仅多层仓库场景
}
```

> 每个元素固定 11 个字段：`ref,type,x,z,w,d,h,y,rot,color,label`（`x,z,w,d` 为底面几何；`h` 高、`y` 离地、`rot` 绕Y旋转、`color` 渲染色、`label` 显示名）。
> `docks` 仅含月台类（`truck_dock/rail_dock/ship_dock`），其余入 `zones`，两数组不重叠。

---

## 2. 模板总览（13 套）

| 场景 | 变体 | 名称 | 月台 | 功能分区(zones) | 楼层 |
|------|------|------|------|----------------|------|
| 大型电商仓库 ecommerce | A1 | 大型电商仓库 | 6 卡车月台 | 收货/发货/流利货架×3/高位货架×3/夹层/立库/退货 | — |
| 火车卸货→月台→大卡车 rail_unload | B1 | 单线转运 | 3 卡车月台 | 铁轨×1/棚车×3/月台/卡车×3/暂存/质检 | — |
| | B2 | 双线多式联运 | 0（堆场式） | 铁轨×2/棚车×6/月台×2/卡车×6/暂存×2 | — |
| 工厂仓库(含卸货) manufacturing | C1 | 离散制造 | 2收+2发 | 收货/双产线/WIP×2/零部件库/成品暂存 | — |
| | C2 | 流水线大产线 | 3收+2发 | 收货/3产线/WIP/零部件库/成品高架/成品暂存 | — |
| 港口码头卸货 port | D1 | 集装箱堆场 | 1岸线+1闸口 | 海关/箱堆场2组(7×6)/冷藏箱/中转暂存 | — |
| | D2 | 多泊位 | 2岸线+1闸口 | 海关/箱堆场2组(8×7)/冷藏/空箱/中转暂存 | — |
| 冷链仓库 cold_chain | E1 | 冷冻+冷藏+穿堂 | 2 冷藏月台 | 穿堂/冷冻(-18℃)/冷藏(2~4℃)/常温 | — |
| | E2 | 深冷+预冷+分拣 | 3 冷藏月台 | 预冷/穿堂/冷冻(-22℃)/冷藏(2~8℃)/常温分拣 | — |
| 退货异常仓库 reverse_logistics | F1 | 标准逆向 | 1 退货口 | 接收/质检/分拣/隔离/翻修/处置/出库 | — |
| | F2 | 高退货量电商 | 2 退货口 | 大接收/双质检/自动分拣/隔离/双翻修/处置/出库 | — |
| 多层仓库 multi_floor | G1 | 3层(收/拣/存) | 1收+1发 | L1收货·发货 / L2拣选 / L3存储 / 货梯 | 3 |
| | G2 | 2层(储发/拣办) | 2收+1发 | L1存储·发货 / L2拣选·办公 / 自动垂直输送 | 2 |

---

## 3. 各场景设计要点与真实数据参考

### 3.1 大型电商仓库（A1，结构基准）
提取自 `warehouse_theatre_3d` 的 `DEFAULT_SHELL`：120×80m，四周 perimeter 墙（高6m），
西/东各 3 个卡车月台（高1.2m），收货/发货暂存、3 组流利货架、3 组高位货架、夹层办公、
自动立库（高8m）、退货区，主/横通道。**所有其它模板的字段结构、配色、高度取值均以此为准。**

### 3.2 火车卸货→月台→大卡车（B1/B2）
- 真实参考：棚车（50ft）内长≈15m、门洞≈2.6×2.6m、地板高≈1.0–1.1m（BNSF 50/60ft Boxcar Diagram）；
  标准装卸月台高≈1.219m（4ft，Rite-Hite）；半挂车货厢≈13.6m×2.59m×2.69m。
- B1：单线铁路侧线 + 3 节棚车 + 转运月台（高1.2m，离地0.3m）+ 3 辆大卡车装车位，构成「火车→月台→卡车」完整装卸链。
- B2：双线铁路 + 6 节棚车 + 双侧月台 + 6 辆卡车，堆场式多式联运场站（ICD）。

### 3.3 工厂仓库(含卸货)（C1/C2）
- 真实参考：制造仓通用布局含收货卸货月台 + 生产线 + WIP 缓冲 + 零部件库 + 成品发运；月台高≈1.2m。
- C1：2 收货月台 + 双生产线 + WIP×2 + 零部件库 + 2 发运月台。
- C2：3 收货 + 3 条主生产线 + 更大零部件/成品高架 + 2 发运，对应汽车/家电总装厂物流。

### 3.4 港口码头卸货（D1/D2）
- 真实参考：ISO 箱 20ft 6.06×2.44×2.59m、40ft 12.19×2.44×2.59m、40HC 高2.90m；
  堆场按 6–7 列 × 5–6 箱长、RTG 作业（PortEconomics Ch.6.5）。
- D1：岸线 + 海关查验 + 双集装箱堆场（7×6）+ 冷藏箱区 + 闸口。
- D2：双泊位 + 海关 + 双堆场（8×7）+ 冷藏/空箱区 + 闸口。

### 3.5 冷链仓库（E1/E2）
- 真实参考：冷冻 -18～-25℃（常见 -18～-22），冷藏 0～8℃（生鲜≈1～4℃）；
  冷链月台需密封门封（GCCA / IE Cold Storage）。
- E1：冷冻(-18℃) + 冷藏(2~4℃) + 穿堂缓冲 + 2 冷藏月台。
- E2：深冷(-22℃) + 冷藏(2~8℃) + 快速预冷 + 穿堂 + 3 冷藏月台 + 常温分拣。

### 3.6 退货异常仓库（F1/F2）
- 真实参考：逆向中心分区为 接收/质检分级 → 分拣归类 → 隔离待决 → 翻修再上架 → 残损处置 → 正向出库
  （ReturnPro / ShelvingIndia / Pallite）；NRF 退货率逐年攀升。
- F1：标准 7 段逆向链（单卸货口）。F2：双卸货 + 双质检 + 自动分拣 + 双翻修，电商高退货量中心。

### 3.7 多层仓库（G1/G2）
- 真实参考：多层物流建筑每层专用；货梯/垂直输送机（托盘/料箱）连接楼层（GSE Group / X-YES / GSsort）。
- G1：3 层（L1 收货·发货 / L2 拣选 / L3 存储）+ 货梯（垂直输送机，高12m）。
- G2：2 层（L1 存储·发货 / L2 拣选·办公）+ 自动垂直输送。

---

## 4. 数据来源

1. **warehouse_theatre_3d 仓库 `DEFAULT_SHELL`**（大型电商仓库结构基准）
   `warehouse_theatre_3d/docs/superpowers/specs/2026-08-18-ecommerce-warehouse-zones-design.md` §4
2. **Rite-Hite** — 标准装卸月台高 4 ft (1.219 m)
   https://www.ritehite.com/en/ap/solutions/.../loading-dock-safety-and-security/
3. **BNSF Railway** — 50 ft / 60 ft Boxcar Diagram（棚车内长≈15/18.3m，门 2.6×2.6m，地板高≈1.0–1.1m）
   https://www.bnsf.com/ship-with-bnsf/ways-of-shipping/equipment/pdf/50ftF_BoxcarDiagram.pdf
4. **American-Rails** — Boxcar dimensions & capacity
   https://www.american-rails.com/box.html
5. **PortEconomics (PEMP)** — Ch.6.5 Container Terminal Design and Equipment（堆场 6–7 列 × 5–6 箱长，RTG）
   https://porteconomicsmanagement.org/pemp/contents/part6/container-terminal-design-equipment/
6. **KSCraneGroup / Hansatic** — 集装箱尺寸 20ft 6.06×2.44×2.59m / 40ft 12.19×2.44×2.59m / 40HC 2.90m
7. **GCCA / IE Cold Storage** — Frozen -10°F(-23℃) / Chilled 34°F(1℃)；冷链月台门封
8. **ReturnPro / ShelvingIndia / Pallite** — 逆向物流分区（接收/质检/分拣/隔离/翻修/处置/出库）
9. **GSE Group / X-YES / GSsort** — 多层物流建筑（每层专用）、货梯/垂直输送机连接楼层

---

## 5. 与场景地图模块的对应关系

- 该 JSON 是 `geometry_json` 的「场景模板」数据源；可经后端 `map_mjcf.py` 的 zone-type→MJCF 注册表转为 MJCF，
  由前端 `MjcfLoader`（three.js）渲染（详见 `scene-map-management.md`）。
- 7 个场景对应 `seed_templates()` 的 `SCENARIO_IDS`（ecommerce / train_unload / manufacturing / port / cold_chain / reverse_logistics / multi_floor），
  其中 `ecommerce` 与 `multi_floor` 已有 Python 构建器，其余 5 个场景的 2 套变体可作为「同类场景的不同布局预设」入库。

---

> 免责声明：本数据为基于公开行业资料的场景地图初始化模板，尺寸为典型参考值，落地前请结合实际场地与规范复核。
