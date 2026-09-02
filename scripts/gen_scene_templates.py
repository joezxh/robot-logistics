# -*- coding: utf-8 -*-
"""
生成 7 个场景共 13 套初始化场景地图模板数据。
- 大型电商仓库：1 套（提取自 warehouse_theatre_3d 仓库 DEFAULT_SHELL，结构基准）
- 其余 6 个场景：各 2 套（参考联网真实数据，结构统一）

输出: docs/superpowers/specs/scene-map-templates.json
统一结构 (wt_floor_shell，所有元素字段一致):
  bounds: {w, d, h?}
  walls/docks/facilities/zones/corridors: [{ref,type,x,z,w,d,h,y,rot,color,label}]
"""
import json, os

# ---- 类型 → 默认高度 / 颜色（与 robot-logic ZONE_BODY_TEMPLATES 调色板一致）----
DEFAULT_H = {
    "perimeter": 6, "partition": 4,
    "truck_dock": 1.2, "rail_dock": 1.2, "ship_dock": 2.0,
    "staging": 0.6, "receiving": 0.6, "shipping": 0.6,
    "flow_rack": 3.0, "high_rack": 6.0, "mezzanine": 2.0,
    "automated": 5.0, "asrs": 8.0, "returns": 2.0,
    "platform": 1.2, "train_car": 4.0, "rail_track": 0.3, "truck": 3.5,
    "production_line": 1.5, "wip_buffer": 1.0, "parts_storage": 3.0,
    "frozen_zone": 5.0, "cold_zone": 5.0, "ambient_zone": 5.0,
    "container_yard": 0.3, "customs_area": 3.0,
    "returns_received": 2.0, "qc_staging": 1.5, "reshelving": 3.0, "disposal": 2.0,
    "floor_1": 4.0, "floor_2": 4.0, "floor_3": 4.0, "elevator_shaft": 12.0,
    "corridor": 0.0, "office": 3.0,
}
COLOR = {
    "perimeter": "#6b7280", "partition": "#9ca3af",
    "truck_dock": "#fbbf24", "rail_dock": "#a16207", "ship_dock": "#0ea5e9",
    "staging": "#94a3b8", "receiving": "#cbd5e1", "shipping": "#cbd5e1",
    "flow_rack": "#f59e0b", "high_rack": "#d97706", "mezzanine": "#a16207",
    "automated": "#0ea5e9", "asrs": "#0ea5e9", "returns": "#ef4444",
    "platform": "#eab308", "train_car": "#7c2d12", "rail_track": "#44403c", "truck": "#1f2937",
    "production_line": "#64748b", "wip_buffer": "#475569", "parts_storage": "#334155",
    "frozen_zone": "#3b82f6", "cold_zone": "#60a5fa", "ambient_zone": "#cbd5e1",
    "container_yard": "#10b981", "customs_area": "#8b5cf6",
    "returns_received": "#ef4444", "qc_staging": "#f87171", "reshelving": "#fca5a5", "disposal": "#dc2626",
    "floor_1": "#64748b", "floor_2": "#475569", "floor_3": "#334155", "elevator_shaft": "#22d3ee",
    "corridor": "#e5e7eb", "office": "#a855f7",
}

def E(ref, type, x, z, w, d, h=None, y=0.0, rot=0.0, color=None, label=None):
    """统一字段元素：ref,type,x,z,w,d,h,y,rot,color,label 全部存在。"""
    return {
        "ref": ref, "type": type, "x": x, "z": z, "w": w, "d": d,
        "h": h if h is not None else DEFAULT_H.get(type, 1.0),
        "y": y, "rot": rot,
        "color": color or COLOR.get(type, "#9ca3af"),
        "label": label or ref,
    }

def walls_perimeter(w, d, h=6.0):
    return [
        E("wall-n", "perimeter", 0, 0, w, 2, h=h, label="北墙"),
        E("wall-s", "perimeter", 0, d - 2, w, 2, h=h, label="南墙"),
        E("wall-w", "perimeter", 0, 0, 2, d, h=h, label="西墙"),
        E("wall-e", "perimeter", w - 2, 0, 2, d, h=h, label="东墙"),
    ]

def meta(scenario, variant, name, name_en, note, ref):
    return {"scenario": scenario, "variant": variant, "name": name,
            "name_en": name_en, "note": note, "reference": ref}

# =====================================================================
# A. 大型电商仓库 (ecommerce) —— 1 套，提取自 warehouse_theatre_3d DEFAULT_SHELL
# =====================================================================
def tpl_ecommerce():
    w, d = 120, 80
    return {
        "meta": meta("ecommerce", "A1", "大型电商仓库", "Large E-commerce Warehouse",
                     "提取自 warehouse_theatre_3d 仓库 DEFAULT_SHELL，作为统一结构基准",
                     "warehouse_theatre_3d/docs/superpowers/specs/2026-08-18-ecommerce-warehouse-zones-design.md §4 DEFAULT_SHELL"),
        "bounds": {"w": w, "d": d},
        "walls": walls_perimeter(w, d),
        "docks": [
            E("dock-01", "truck_dock", 0, 12, 2, 6, label="卸货口1"),
            E("dock-02", "truck_dock", 0, 26, 2, 6, label="卸货口2"),
            E("dock-03", "truck_dock", 0, 40, 2, 6, label="卸货口3"),
            E("dock-04", "truck_dock", w - 2, 12, 2, 6, label="装货口1"),
            E("dock-05", "truck_dock", w - 2, 26, 2, 6, label="装货口2"),
            E("dock-06", "truck_dock", w - 2, 40, 2, 6, label="装货口3"),
        ],
        "facilities": [E("office", "office", w - 16, 4, 12, 10, label="办公区")],
        "zones": [
            E("stg-rcv", "receiving", 10, 4, 14, 16, label="收货暂存"),
            E("stg-ship", "shipping", 10, 58, 14, 18, label="发货暂存"),
            E("pick-a", "flow_rack", 30, 6, 34, 22, label="流利货架A"),
            E("pick-b", "flow_rack", 30, 34, 34, 22, label="流利货架B"),
            E("pick-c", "flow_rack", 30, 62, 34, 16, label="流利货架C"),
            E("rack-h1", "high_rack", 70, 6, 40, 22, label="高位货架1"),
            E("rack-h2", "high_rack", 70, 34, 40, 22, label="高位货架2"),
            E("rack-h3", "high_rack", 70, 62, 40, 16, label="高位货架3"),
            E("mezz", "mezzanine", 4, 4, 4, 30, label="夹层办公"),
            E("asrs", "asrs", 4, 40, 4, 30, label="自动立库"),
            E("ret", "returns", 26, 4, 4, 8, label="退货区"),
        ],
        "corridors": [
            E("main-aisle", "corridor", 10, 30, 100, 6, label="主通道"),
            E("cross-aisle", "corridor", 64, 4, 6, 72, label="横向通道"),
        ],
    }

# =====================================================================
# B. 火车卸货→月台→大卡车 (rail_unload) —— 2 套
# 真实参考: 棚车 50ft 内长≈15m/门 2.6×2.6m/地板高≈1.0–1.1m; 标准月台高≈1.219m(4ft);
#          半挂车货厢≈13.6m 长×2.59m 宽×2.69m 高
# =====================================================================
def tpl_rail_unload_1():
    w, d = 180, 80
    z = [
        E("rail-track-1", "rail_track", 0, 10, 10, 60, label="铁路侧线"),
        E("train-car-1", "train_car", 12, 12, 15, 12, label="棚车1"),
        E("train-car-2", "train_car", 12, 30, 15, 12, label="棚车2"),
        E("train-car-3", "train_car", 12, 48, 15, 12, label="棚车3"),
        E("platform", "platform", 30, 8, 24, 64, h=1.2, y=0.3, label="转运月台"),
        E("truck-1", "truck", 60, 12, 14, 12, label="大卡车1"),
        E("truck-2", "truck", 60, 30, 14, 12, label="大卡车2"),
        E("truck-3", "truck", 60, 48, 14, 12, label="大卡车3"),
        E("truck-dock-1", "truck_dock", 76, 12, 2, 12, label="卡车月台1"),
        E("truck-dock-2", "truck_dock", 76, 30, 2, 12, label="卡车月台2"),
        E("truck-dock-3", "truck_dock", 76, 48, 2, 12, label="卡车月台3"),
        E("staging", "staging", 90, 8, 88, 64, label="暂存/分拣区"),
        E("qc", "qc_staging", 100, 10, 20, 20, label="质检分拣"),
    ]
    return {
        "meta": meta("rail_unload", "B1", "火车卸货→月台→大卡车(单线)", "Rail Unload → Platform → Truck (single siding)",
                     "单线铁路侧线+月台+3卡车装车位，典型铁路货运站转运",
                     "BNSF 50ft Boxcar Diagram; Rite-Hite 标准月台高 4ft(1.219m)"),
        "bounds": {"w": w, "d": d},
        "walls": walls_perimeter(w, d, h=7),
        "docks": [e for e in z if e["type"] in ("truck_dock", "rail_dock", "ship_dock")],
        "facilities": [],
        "zones": [e for e in z if e["type"] not in ("truck_dock", "rail_dock", "ship_dock")],
        "corridors": [E("aisle", "corridor", 30, 4, 120, 4, label="作业通道")],
    }

def tpl_rail_unload_2():
    w, d = 220, 90
    z = [
        E("rail-track-1", "rail_track", 0, 10, 10, 70, label="铁路一线"),
        E("rail-track-2", "rail_track", 14, 10, 10, 70, label="铁路二线"),
        E("train-car-1", "train_car", 0, 14, 15, 12, label="棚车1-1"),
        E("train-car-2", "train_car", 0, 32, 15, 12, label="棚车1-2"),
        E("train-car-3", "train_car", 0, 50, 15, 12, label="棚车1-3"),
        E("train-car-4", "train_car", 14, 14, 15, 12, label="棚车2-1"),
        E("train-car-5", "train_car", 14, 32, 15, 12, label="棚车2-2"),
        E("train-car-6", "train_car", 14, 50, 15, 12, label="棚车2-3"),
        E("platform-1", "platform", 30, 8, 22, 74, h=1.2, y=0.3, label="北侧月台"),
        E("platform-2", "platform", 110, 8, 22, 74, h=1.2, y=0.3, label="南侧月台"),
        E("truck-1", "truck", 56, 14, 14, 12, label="卡车1"),
        E("truck-2", "truck", 56, 32, 14, 12, label="卡车2"),
        E("truck-3", "truck", 56, 50, 14, 12, label="卡车3"),
        E("truck-4", "truck", 136, 14, 14, 12, label="卡车4"),
        E("truck-5", "truck", 136, 32, 14, 12, label="卡车5"),
        E("truck-6", "truck", 136, 50, 14, 12, label="卡车6"),
        E("staging-1", "staging", 78, 8, 28, 74, label="中区暂存"),
        E("staging-2", "staging", 158, 8, 60, 74, label="出库暂存"),
    ]
    return {
        "meta": meta("rail_unload", "B2", "火车卸货→月台→大卡车(双线多式联运)", "Rail Unload → Platform → Truck (twin siding ICD)",
                     "双线铁路+双侧月台+6卡车装车位，大型多式联运场站",
                     "BNSF 50/60ft Boxcar; Rite-Hite 月台 1.219m; 集装箱多式联运场站惯例"),
        "bounds": {"w": w, "d": d},
        "walls": walls_perimeter(w, d, h=8),
        "docks": [e for e in z if e["type"] in ("truck_dock", "rail_dock", "ship_dock")],
        "facilities": [],
        "zones": [e for e in z if e["type"] not in ("truck_dock", "rail_dock", "ship_dock")],
        "corridors": [E("aisle", "corridor", 30, 4, 160, 4, label="作业通道")],
    }

# =====================================================================
# C. 工厂仓库(含卸货) (manufacturing) —— 2 套
# 真实参考: 制造仓含收货卸货月台+生产线+WIP+零部件库+成品发运
# =====================================================================
def tpl_manufacturing_1():
    w, d = 100, 80
    z = [
        E("rcv-dock-1", "truck_dock", 0, 10, 2, 8, label="收货月台1"),
        E("rcv-dock-2", "truck_dock", 0, 26, 2, 8, label="收货月台2"),
        E("stg-rcv", "receiving", 8, 8, 16, 30, label="收货暂存"),
        E("line-1", "production_line", 30, 8, 30, 14, label="生产线1"),
        E("line-2", "production_line", 30, 26, 30, 14, label="生产线2"),
        E("wip-1", "wip_buffer", 30, 44, 18, 12, label="WIP缓冲1"),
        E("wip-2", "wip_buffer", 30, 60, 18, 12, label="WIP缓冲2"),
        E("parts", "parts_storage", 54, 8, 24, 34, label="零部件库"),
        E("ship-dock-1", "truck_dock", w - 2, 10, 2, 8, label="发运月台1"),
        E("ship-dock-2", "truck_dock", w - 2, 26, 2, 8, label="发运月台2"),
        E("stg-ship", "shipping", 64, 8, 32, 30, label="成品暂存"),
    ]
    return {
        "meta": meta("manufacturing", "C1", "工厂仓库(含卸货)-离散制造", "Factory Warehouse w/ Unloading (discrete mfg)",
                     "收货卸货月台+双生产线+WIP+零部件库+成品发运",
                     "离散制造仓通用布局; 收货/发运月台高≈1.2m(Rite-Hite)"),
        "bounds": {"w": w, "d": d},
        "walls": walls_perimeter(w, d),
        "docks": [e for e in z if e["type"] in ("truck_dock", "rail_dock", "ship_dock")],
        "facilities": [E("office", "office", w - 14, 50, 10, 12, label="厂务办公")],
        "zones": [e for e in z if e["type"] not in ("truck_dock", "rail_dock", "ship_dock")],
        "corridors": [E("aisle", "corridor", 8, 44, 84, 4, label="物流通道")],
    }

def tpl_manufacturing_2():
    w, d = 120, 90
    z = [
        E("rcv-dock-1", "truck_dock", 0, 12, 2, 8, label="收货月台1"),
        E("rcv-dock-2", "truck_dock", 0, 28, 2, 8, label="收货月台2"),
        E("rcv-dock-3", "truck_dock", 0, 44, 2, 8, label="收货月台3"),
        E("stg-rcv", "receiving", 8, 8, 18, 40, label="收货暂存"),
        E("line-1", "production_line", 32, 8, 40, 16, label="主线1"),
        E("line-2", "production_line", 32, 28, 40, 16, label="主线2"),
        E("line-3", "production_line", 32, 48, 40, 16, label="主线3"),
        E("wip-1", "wip_buffer", 32, 68, 24, 14, label="WIP缓冲"),
        E("parts", "parts_storage", 76, 8, 26, 40, label="零部件库"),
        E("fin-rack", "high_rack", 76, 52, 26, 30, label="成品高架"),
        E("ship-dock-1", "truck_dock", w - 2, 12, 2, 8, label="发运月台1"),
        E("ship-dock-2", "truck_dock", w - 2, 28, 2, 8, label="发运月台2"),
        E("stg-ship", "shipping", 78, 8, 30, 30, label="成品暂存"),
    ]
    return {
        "meta": meta("manufacturing", "C2", "工厂仓库(含卸货)-流水线大产线", "Factory Warehouse w/ Unloading (flow line)",
                     "3 条主生产线+更大零部件/成品库+3收货2发运月台",
                     "汽车/家电总装厂物流布局惯例; 月台 1.2m"),
        "bounds": {"w": w, "d": d},
        "walls": walls_perimeter(w, d),
        "docks": [e for e in z if e["type"] in ("truck_dock", "rail_dock", "ship_dock")],
        "facilities": [E("office", "office", w - 14, 60, 10, 14, label="厂务办公")],
        "zones": [e for e in z if e["type"] not in ("truck_dock", "rail_dock", "ship_dock")],
        "corridors": [E("aisle", "corridor", 8, 52, 100, 4, label="物流通道")],
    }

# =====================================================================
# D. 港口码头卸货 (port) —— 2 套
# 真实参考: 20ft 箱 6.06×2.44×2.59m; 40ft 12.19×2.44×2.59m; 40HC 高2.90m;
#          堆场按 6–7 列×5–6 箱长, RTG 作业; 岸桥/闸口
# =====================================================================
def _containers(prefix, x0, z0, ncols, nrows, cw=2.44, cd=6.06, gap=0.3):
    out = []
    for r in range(nrows):
        for c in range(ncols):
            out.append(E(f"{prefix}-{r}-{c}", "container_yard", x0 + c * (cw + gap),
                         z0 + r * (cd + gap), cw, cd, h=2.59, label=f"箱{r}-{c}"))
    return out

def tpl_port_1():
    w, d = 200, 150
    z = [
        E("quay", "ship_dock", 0, 0, 12, 30, h=2.0, label="码头岸线"),
        E("crane-apron", "corridor", 12, 0, 30, 30, label="岸桥作业带"),
        E("customs", "customs_area", 12, 34, 40, 24, label="海关查验区"),
    ]
    z += _containers("yard-a", 60, 10, 7, 6)
    z += _containers("yard-b", 130, 10, 7, 6)
    z += [
        E("reefer", "cold_zone", 60, 60, 60, 20, h=2.9, label="冷藏箱区"),
        E("gate", "truck_dock", w - 2, 40, 2, 20, label="闸口发运"),
        E("staging", "staging", 60, 90, 120, 50, label="中转暂存"),
    ]
    return {
        "meta": meta("port", "D1", "港口码头卸货-集装箱堆场", "Port Terminal Unloading (container yard)",
                     "岸线+海关区+双集装箱堆场(20/40ft)+冷藏箱+闸口",
                     "Container 20ft 6.06×2.44×2.59m / 40ft 12.19×2.44×2.59m (kscranegroup,hansatic); 堆场 6–7 列(porteconomicsmanagement Ch6.5)"),
        "bounds": {"w": w, "d": d},
        "walls": walls_perimeter(w, d, h=4),
        "docks": [e for e in z if e["type"] in ("truck_dock", "rail_dock", "ship_dock")],
        "facilities": [],
        "zones": [e for e in z if e["type"] not in ("truck_dock", "rail_dock", "ship_dock")],
        "corridors": [E("apron", "corridor", 12, 30, 180, 6, label="水平运输通道")],
    }

def tpl_port_2():
    w, d = 240, 160
    z = [
        E("quay-1", "ship_dock", 0, 0, 12, 40, h=2.0, label="泊位1岸线"),
        E("quay-2", "ship_dock", 0, 50, 12, 40, h=2.0, label="泊位2岸线"),
        E("crane-apron", "corridor", 12, 0, 34, 100, label="岸桥作业带"),
        E("customs", "customs_area", 12, 110, 50, 30, label="海关查验区"),
    ]
    z += _containers("yard-a", 70, 10, 8, 7)
    z += _containers("yard-b", 150, 10, 8, 7)
    z += [
        E("reefer", "cold_zone", 70, 70, 70, 24, h=2.9, label="冷藏箱区"),
        E("empty-yard", "container_yard", 150, 70, 70, 24, label="空箱堆场"),
        E("gate", "truck_dock", w - 2, 60, 2, 30, label="闸口"),
        E("staging", "staging", 70, 100, 150, 50, label="中转暂存"),
    ]
    return {
        "meta": meta("port", "D2", "港口码头卸货-多泊位", "Port Terminal Unloading (multi-berth)",
                     "双泊位+海关+双堆场+冷藏/空箱区+闸口",
                     "ISO 集装箱尺寸; 多泊位集装箱码头布局(porteconomicsmanagement Ch6.5)"),
        "bounds": {"w": w, "d": d},
        "walls": walls_perimeter(w, d, h=4),
        "docks": [e for e in z if e["type"] in ("truck_dock", "rail_dock", "ship_dock")],
        "facilities": [],
        "zones": [e for e in z if e["type"] not in ("truck_dock", "rail_dock", "ship_dock")],
        "corridors": [E("apron", "corridor", 12, 100, 220, 6, label="水平运输通道")],
    }

# =====================================================================
# E. 冷链仓库 (cold_chain) —— 2 套
# 真实参考: 冷冻 -18~-25°C; 冷藏 0~8°C(生鲜≈1~4°C); 穿堂/月台需密封
# =====================================================================
def tpl_cold_chain_1():
    w, d = 80, 60
    z = [
        E("dock-1", "truck_dock", 0, 10, 2, 8, label="冷藏月台1"),
        E("dock-2", "truck_dock", 0, 26, 2, 8, label="冷藏月台2"),
        E("airlock", "ambient_zone", 8, 10, 10, 24, label="穿堂/缓冲"),
        E("frozen", "frozen_zone", 22, 8, 30, 30, h=6, label="冷冻区(-18℃)"),
        E("chilled", "cold_zone", 22, 40, 30, 18, h=6, label="冷藏区(2~4℃)"),
        E("ambient", "ambient_zone", 56, 8, 20, 40, h=5, label="常温暂存"),
    ]
    return {
        "meta": meta("cold_chain", "E1", "冷链仓库-冷冻+冷藏+穿堂", "Cold Chain (frozen+chilled+airlock)",
                     "冷冻(-18℃)+冷藏(2~4℃)+穿堂缓冲+2 冷藏月台",
                     "GCCA/IE Cold Storage: Frozen -10°F(-23℃)/Chilled 34°F(1℃); 冷链月台需密封门封"),
        "bounds": {"w": w, "d": d, "h": 8},
        "walls": walls_perimeter(w, d, h=8),
        "docks": [e for e in z if e["type"] in ("truck_dock", "rail_dock", "ship_dock")],
        "facilities": [],
        "zones": [e for e in z if e["type"] not in ("truck_dock", "rail_dock", "ship_dock")],
        "corridors": [E("aisle", "corridor", 8, 36, 64, 4, label="内通道")],
    }

def tpl_cold_chain_2():
    w, d = 100, 70
    z = [
        E("dock-1", "truck_dock", 0, 10, 2, 8, label="冷藏月台1"),
        E("dock-2", "truck_dock", 0, 24, 2, 8, label="冷藏月台2"),
        E("dock-3", "truck_dock", 0, 38, 2, 8, label="冷藏月台3"),
        E("precool", "cold_zone", 8, 10, 12, 24, h=5, label="快速预冷(0~4℃)"),
        E("airlock", "ambient_zone", 8, 36, 12, 24, label="穿堂"),
        E("frozen", "frozen_zone", 24, 8, 36, 28, h=7, label="冷冻区(-22℃)"),
        E("chilled", "cold_zone", 24, 40, 36, 24, h=7, label="冷藏区(2~8℃)"),
        E("ambient", "ambient_zone", 64, 8, 32, 50, h=5, label="常温/分拣"),
    ]
    return {
        "meta": meta("cold_chain", "E2", "冷链仓库-深冷+预冷+分拣", "Cold Chain (deep-freeze+precool+sort)",
                     "深冷(-22℃)+冷藏(2~8℃)+快速预冷+穿堂+3 冷藏月台+常温分拣",
                     "GCCA 冷藏设计; 冷冻 -18~-25℃ 区间; 生鲜冷藏 1~8℃"),
        "bounds": {"w": w, "d": d, "h": 9},
        "walls": walls_perimeter(w, d, h=9),
        "docks": [e for e in z if e["type"] in ("truck_dock", "rail_dock", "ship_dock")],
        "facilities": [],
        "zones": [e for e in z if e["type"] not in ("truck_dock", "rail_dock", "ship_dock")],
        "corridors": [E("aisle", "corridor", 8, 62, 84, 4, label="内通道")],
    }

# =====================================================================
# F. 退货异常仓库 (reverse_logistics) —— 2 套
# 真实参考: 收货卸货→质检分级→分拣→隔离→翻修→处置→出库
# =====================================================================
def tpl_reverse_1():
    w, d = 60, 40
    z = [
        E("rcv-dock", "truck_dock", 0, 12, 2, 10, label="退货卸货口"),
        E("rcv", "returns_received", 6, 8, 14, 24, label="退货接收"),
        E("inspect", "qc_staging", 24, 8, 14, 12, label="质检分级"),
        E("sort", "qc_staging", 24, 24, 14, 12, label="分拣归类"),
        E("quarantine", "returns", 42, 8, 14, 12, label="隔离待决"),
        E("refurb", "reshelving", 42, 24, 14, 12, label="翻修/再上架"),
        E("dispose", "disposal", 6, 34, 20, 6, label="残损处置"),
        E("ship", "shipping", 40, 34, 18, 6, label="正向出库"),
    ]
    return {
        "meta": meta("reverse_logistics", "F1", "退货异常仓库-标准逆向", "Reverse Logistics (standard returns)",
                     "退货接收→质检分级→分拣→隔离→翻修→处置→出库 完整逆向链",
                     "ReturnPro 逆向中心分区; ShelvingIndia 退货仓布局(接收/质检/分拣/隔离/翻修/处置)"),
        "bounds": {"w": w, "d": d},
        "walls": walls_perimeter(w, d),
        "docks": [e for e in z if e["type"] in ("truck_dock", "rail_dock", "ship_dock")],
        "facilities": [],
        "zones": [e for e in z if e["type"] not in ("truck_dock", "rail_dock", "ship_dock")],
        "corridors": [E("aisle", "corridor", 6, 36, 50, 2, label="作业通道")],
    }

def tpl_reverse_2():
    w, d = 80, 50
    z = [
        E("rcv-dock-1", "truck_dock", 0, 10, 2, 10, label="退货卸货1"),
        E("rcv-dock-2", "truck_dock", 0, 26, 2, 10, label="退货卸货2"),
        E("rcv", "returns_received", 6, 8, 18, 30, label="大批量退货接收"),
        E("inspect-1", "qc_staging", 28, 8, 16, 14, label="质检分级1"),
        E("inspect-2", "qc_staging", 28, 26, 16, 14, label="质检分级2"),
        E("sort", "qc_staging", 48, 8, 14, 14, label="自动分拣"),
        E("quarantine", "returns", 48, 26, 14, 14, label="隔离待决"),
        E("refurb-1", "reshelving", 66, 8, 12, 14, label="翻修工位1"),
        E("refurb-2", "reshelving", 66, 26, 12, 14, label="翻修工位2"),
        E("dispose", "disposal", 6, 40, 24, 8, label="残损处置"),
        E("ship", "shipping", 36, 40, 42, 8, label="正向/转售出库"),
    ]
    return {
        "meta": meta("reverse_logistics", "F2", "退货异常仓库-高退货量电商", "Reverse Logistics (high-volume e-com)",
                     "双卸货+双质检+自动分拣+双翻修+处置+出库，电商高退货量逆向中心",
                     "NRF 退货率逐年攀升; Pallite 电商退货处理区设计; ReturnPro 分区"),
        "bounds": {"w": w, "d": d},
        "walls": walls_perimeter(w, d),
        "docks": [e for e in z if e["type"] in ("truck_dock", "rail_dock", "ship_dock")],
        "facilities": [],
        "zones": [e for e in z if e["type"] not in ("truck_dock", "rail_dock", "ship_dock")],
        "corridors": [E("aisle", "corridor", 6, 42, 70, 2, label="作业通道")],
    }

# =====================================================================
# G. 多层仓库 (multi_floor) —— 2 套
# 真实参考: 多层物流建筑每层专用; 货梯/垂直输送连接; 垂直输送机运托盘/料箱
# =====================================================================
def tpl_multi_floor_1():
    w, d = 80, 60
    z = [
        E("floor-1-rcv", "floor_1", 6, 6, 30, 20, h=4, y=0, label="L1收货暂存"),
        E("floor-1-stage", "floor_1", 6, 30, 30, 20, h=4, y=0, label="L1发货暂存"),
        E("floor-2-pick", "floor_2", 6, 6, 30, 40, h=4, y=4, label="L2拣选区"),
        E("floor-3-store", "floor_3", 6, 6, 30, 40, h=4, y=8, label="L3存储区"),
        E("elevator", "elevator_shaft", 40, 6, 6, 6, h=12, y=0, label="货梯/垂直输送"),
        E("dock-1", "truck_dock", 0, 10, 2, 8, label="L1卸货口"),
        E("dock-2", "truck_dock", w - 2, 10, 2, 8, label="L1装货口"),
    ]
    # 用 floors 表达楼层（沿用 robot-logic FloorShell 概念，与场景模块几何一致）
    return {
        "meta": meta("multi_floor", "G1", "多层仓库-3层(收/拣/存)", "Multi-floor Warehouse (3 levels)",
                     "L1收货/发货, L2拣选, L3存储, 货梯垂直连接",
                     "GSE Group 多层物流建筑(每层专用); X-YES/GS 垂直输送机/货梯连接楼层"),
        "bounds": {"w": w, "d": d, "h": 12},
        "walls": walls_perimeter(w, d, h=12),
        "docks": [e for e in z if e["type"] in ("truck_dock", "rail_dock", "ship_dock")],
        "facilities": [],
        "zones": [e for e in z if e["type"] not in ("truck_dock", "rail_dock", "ship_dock")],
        "floors": [
            {"level": 1, "y": 0, "zones": ["floor-1-rcv", "floor-1-stage"]},
            {"level": 2, "y": 4, "zones": ["floor-2-pick"]},
            {"level": 3, "y": 8, "zones": ["floor-3-store"]},
        ],
        "corridors": [E("core", "corridor", 40, 12, 6, 40, label="核心筒通道")],
    }

def tpl_multi_floor_2():
    w, d = 90, 70
    z = [
        E("floor-1-store", "floor_1", 6, 6, 36, 30, h=4, y=0, label="L1存储/发货"),
        E("floor-1-ship", "floor_1", 6, 40, 36, 20, h=4, y=0, label="L1发货暂存"),
        E("floor-2-pick", "floor_2", 6, 6, 36, 30, h=4, y=4, label="L2拣选"),
        E("floor-2-office", "floor_2", 6, 40, 36, 20, h=4, y=4, label="L2办公/质控"),
        E("elevator", "elevator_shaft", 46, 6, 8, 8, h=12, y=0, label="自动垂直输送"),
        E("dock-1", "truck_dock", 0, 12, 2, 8, label="L1卸货口"),
        E("dock-2", "truck_dock", 0, 28, 2, 8, label="L1卸货口2"),
        E("dock-3", "truck_dock", w - 2, 12, 2, 8, label="L1装货口"),
    ]
    return {
        "meta": meta("multi_floor", "G2", "多层仓库-2层(储发/拣办)", "Multi-floor Warehouse (2 levels)",
                     "L1存储/发货, L2拣选/办公, 自动垂直输送",
                     "多层配送中心惯例; 垂直输送机(gssort)/货梯连接楼层"),
        "bounds": {"w": w, "d": d, "h": 8},
        "walls": walls_perimeter(w, d, h=8),
        "docks": [e for e in z if e["type"] in ("truck_dock", "rail_dock", "ship_dock")],
        "facilities": [],
        "zones": [e for e in z if e["type"] not in ("truck_dock", "rail_dock", "ship_dock")],
        "floors": [
            {"level": 1, "y": 0, "zones": ["floor-1-store", "floor-1-ship"]},
            {"level": 2, "y": 4, "zones": ["floor-2-pick", "floor-2-office"]},
        ],
        "corridors": [E("core", "corridor", 46, 16, 8, 40, label="核心筒通道")],
    }

# ---- 汇总 ----
TEMPLATES = [
    tpl_ecommerce(),
    tpl_rail_unload_1(), tpl_rail_unload_2(),
    tpl_manufacturing_1(), tpl_manufacturing_2(),
    tpl_port_1(), tpl_port_2(),
    tpl_cold_chain_1(), tpl_cold_chain_2(),
    tpl_reverse_1(), tpl_reverse_2(),
    tpl_multi_floor_1(), tpl_multi_floor_2(),
]

SOURCES = [
    "warehouse_theatre_3d 仓库 DEFAULT_SHELL — docs/superpowers/specs/2026-08-18-ecommerce-warehouse-zones-design.md §4（大型电商仓库结构基准）",
    "Rite-Hite — Standard loading dock height 4 ft (1.219 m): https://www.ritehite.com/...",
    "BNSF Railway — 50 ft / 60 ft Boxcar Diagram（棚车内长≈15/18.3m, 门 2.6×2.6m, 地板高≈1.0–1.1m）: https://www.bnsf.com/",
    "American-Rails — Boxcar dimensions: https://www.american-rails.com/box.html",
    "PortEconomics — Ch.6.5 Container Terminal Design and Equipment（堆场 6–7 列×5–6 箱长, RTG）: https://porteconomicsmanagement.org/",
    "KSCraneGroup / Hansatic — Shipping container dimensions 20ft 6.06×2.44×2.59m, 40ft 12.19×2.44×2.59m, 40HC 2.90m",
    "GCCA / IE Cold Storage — Frozen -10°F(-23℃) / Chilled 34°F(1℃); 冷链月台门封",
    "ReturnPro / ShelvingIndia / Pallite — Reverse logistics 分区: 接收/质检分级/分拣/隔离/翻修/处置/出库",
    "GSE Group / X-YES / GSsort — Multi-storey logistics（每层专用）, 货梯/垂直输送机连接楼层",
]

OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "superpowers", "specs", "scene-map-templates.json")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc = {"schema": "wt_floor_shell", "version": 1, "sources": SOURCES, "templates": TEMPLATES}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
print("wrote", OUT, "templates:", len(TEMPLATES))
