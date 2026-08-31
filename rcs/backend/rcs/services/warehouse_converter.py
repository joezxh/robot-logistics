"""Convert warehouse_theatre_3d DEFAULT_SHELL blueprint to RCS data models.

Coordinate convention:
- warehouse_theatre_3d blueprint uses **center-based** coords with origin at
  warehouse center (x ∈ [-W/2, W/2], z ∈ [-D/2, D/2]).
- RCS FloorShell uses **bottom-left corner** coords (x ∈ [0, W], z ∈ [0, D]).
- Shift: ``new_x = old_x + W/2``, ``new_z = old_z + D/2`` for points.
- For zone/facility rects: ``corner_x = center_x + W/2 - w/2``.

The site-map graph (nodes + edges) is derived from the spatial topology:
corridors, zones, docks, and facilities become navigable nodes; edges connect
adjacent corridor segments, zones to their nearest corridor, and docks /
facilities to the nearest corridor node.
"""
from __future__ import annotations

import math
import uuid
from typing import Any

# ── Embedded blueprint (mirror of warehouse_theatre_3d layout_blueprint.py) ────

BLUEPRINT: dict[str, Any] = {
    "bounds": {"w": 160, "d": 100},
    "walls": [
        {"x0": -80, "z0": -50, "x1": -42, "z1": -50, "h": 3.5},
        {"x0": -38, "z0": -50, "x1": 38, "z1": -50, "h": 3.5},
        {"x0": 42, "z0": -50, "x1": 80, "z1": -50, "h": 3.5},
        {"x0": -80, "z0": 50, "x1": 80, "z1": 50, "h": 3.5},
        {"x0": -80, "z0": -50, "x1": -80, "z1": 50, "h": 3.5},
        {"x0": 80, "z0": -50, "x1": 80, "z1": 50, "h": 3.5},
        {"x0": -16, "z0": -55, "x1": 16, "z1": -55, "h": 1.2},
    ],
    "docks": [
        {"ref": "DOCK-1", "x": -12, "z": -53, "rot": 0, "flow": "inbound"},
        {"ref": "DOCK-2", "x": -4, "z": -53, "rot": 0, "flow": "outbound"},
        {"ref": "DOCK-3", "x": 4, "z": -53, "rot": 0, "flow": "inbound"},
        {"ref": "DOCK-4", "x": 12, "z": -53, "rot": 0, "flow": "outbound"},
    ],
    "facilities": [
        {"ref": "ENT-A", "kind": "entrance", "x": -40, "z": -50, "w": 4},
        {"ref": "ENT-B", "kind": "entrance", "x": 40, "z": -50, "w": 4},
        {"ref": "QC-1", "kind": "qc", "x": -66, "z": -38, "w": 14, "d": 6},
        {"ref": "SORT-1", "kind": "sorting", "x": -28, "z": -38, "w": 16, "d": 6},
        {"ref": "PACK-1", "kind": "packing", "x": -28, "z": -30, "w": 16, "d": 6},
        {"ref": "QC-2", "kind": "qc", "x": 66, "z": -38, "w": 14, "d": 6},
        {"ref": "SORT-2", "kind": "sorting", "x": 28, "z": -38, "w": 16, "d": 6},
        {"ref": "PACK-2", "kind": "packing", "x": 28, "z": -30, "w": 16, "d": 6},
        {"ref": "CHG-1", "kind": "charger", "x": -78, "z": -38, "w": 2, "d": 2},
        {"ref": "CHG-2", "kind": "charger", "x": -78, "z": -44, "w": 2, "d": 2},
        {"ref": "CHG-3", "kind": "charger", "x": 78, "z": -38, "w": 2, "d": 2},
        {"ref": "CHG-4", "kind": "charger", "x": 78, "z": -44, "w": 2, "d": 2},
    ],
    "zones": [
        {"ref": "TEMP-1", "type": "temp", "x": -30, "z": -22, "w": 28, "d": 8},
        {"ref": "TEMP-2", "type": "temp_bagged", "x": 30, "z": -22, "w": 28, "d": 8},
        {"ref": "RET-1", "type": "returns", "x": -47, "z": -38, "w": 16, "d": 6},
        {"ref": "ZONE-A", "type": "flow_rack", "x": -40, "z": -6, "w": 36, "d": 24},
        {"ref": "ZONE-B", "type": "high_rack", "x": -40, "z": 20, "w": 36, "d": 24},
        {"ref": "ZONE-C", "type": "high_rack", "x": 40, "z": 20, "w": 36, "d": 24},
        {"ref": "ZONE-D", "type": "mezzanine", "x": 40, "z": -6, "w": 36, "d": 24},
        {"ref": "ASRS-1", "type": "automated", "x": 0, "z": 42, "w": 80, "d": 16},
    ],
    "corridors": [
        {"x0": -2, "z0": -46, "x1": 2, "z1": 34, "main": True},
        {"x0": -22, "z0": -16, "x1": 22, "z1": -14, "main": False},
        {"x0": -22, "z0": 8, "x1": 22, "z1": 10, "main": False},
        {"x0": -58, "z0": -16, "x1": -56, "z1": 32, "main": False},
        {"x0": -22, "z0": 32, "x1": 22, "z1": 34, "main": False},
        {"x0": 56, "z0": -16, "x1": 58, "z1": 32, "main": False},
        {"x0": -78, "z0": -34, "x1": -76, "z1": -18, "main": False},
        {"x0": 76, "z0": -34, "x1": 78, "z1": -18, "main": False},
        {"x0": -78, "z0": -16, "x1": -60, "z1": -14, "main": False},
        {"x0": 60, "z0": -16, "x1": 78, "z1": -14, "main": False},
        {"x0": -56, "z0": -46, "x1": 56, "z1": -44, "main": True},
    ],
}

# ── Coordinate helpers ────────────────────────────────────────────────────────

_W2 = 80.0   # W / 2
_D2 = 50.0   # D / 2


def _shift_point(x: float, z: float) -> tuple[float, float]:
    """Shift a point from blueprint center-origin to FloorShell bottom-left."""
    return x + _W2, z + _D2


def _center_to_corner(cx: float, cz: float, w: float, d: float) -> tuple[float, float]:
    """Convert a center-based rect to bottom-left corner in FloorShell space."""
    return cx - w / 2 + _W2, cz - d / 2 + _D2


def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _uuid() -> str:
    return uuid.uuid4().hex[:12]


# ── Blueprint → FloorShell ────────────────────────────────────────────────────

def convert_to_floor_shell() -> dict[str, Any]:
    """Convert the embedded blueprint to an RCS FloorShell dict.

    The returned dict is compatible with ``rcs.models.floor_shell.FloorShell``
    and is stored as the UnifiedMap ``geometry_json``.
    """
    bp = BLUEPRINT

    # Walls
    walls = []
    for i, w in enumerate(bp["walls"]):
        sx, sz = _shift_point(w["x0"], w["z0"])
        ex, ez = _shift_point(w["x1"], w["z1"])
        walls.append({
            "id": f"W-{i}",
            "x0": sx, "z0": sz,
            "x1": ex, "z1": ez,
            "h": w.get("h", 3.5),
            "kind": "wall",
        })

    # Zones (center → bottom-left corner)
    zones = []
    for z in bp["zones"]:
        cx, cz = _center_to_corner(z["x"], z["z"], z["w"], z["d"])
        zones.append({
            "id": z["ref"],
            "ref": z["ref"],
            "type": z["type"],
            "x": cx, "z": cz,
            "w": z["w"], "d": z["d"],
            "name": z["ref"],
        })

    # Facilities
    facilities = []
    for f in bp["facilities"]:
        fw = f["w"]
        fd = f.get("d", fw)
        cx, cz = _center_to_corner(f["x"], f["z"], fw, fd)
        facilities.append({
            "id": f["ref"],
            "ref": f["ref"],
            "type": f["kind"],
            "x": cx, "z": cz,
            "w": fw, "d": fd,
        })

    # Docks — all face south (z = 0 side)
    docks = []
    for d in bp["docks"]:
        sx, sz = _shift_point(d["x"], d["z"])
        docks.append({
            "id": d["ref"],
            "ref": d["ref"],
            "x": sx, "z": sz,
            "direction": "S",
            "door_w": 4.0,
        })

    # Corridors — convert to zone-like rects for the floor shell
    corridors = []
    for i, c in enumerate(bp["corridors"]):
        cx0 = min(c["x0"], c["x1"]) + _W2
        cz0 = min(c["z0"], c["z1"]) + _D2
        cw = abs(c["x1"] - c["x0"])
        cd = abs(c["z1"] - c["z0"])
        corridors.append({
            "id": f"CORR-{i}",
            "from_zone": f"CORR-{i}-A",
            "to_zone": f"CORR-{i}-B",
            "w": max(cw, cd),
            "bidirectional": True,
        })

    return {
        "bounds": {"w": bp["bounds"]["w"], "d": bp["bounds"]["d"], "h": 0},
        "walls": walls,
        "zones": zones,
        "facilities": facilities,
        "docks": docks,
        "corridors": corridors,
        "markings": [],
        "metadata": {
            "name": "E-Commerce Warehouse (warehouse_theatre_3d)",
            "source": "warehouse_theatre_3d",
        },
    }


# ── Blueprint → Site Map (nodes + edges) ──────────────────────────────────────

def _corridor_nodes(corridor: dict, idx: int) -> list[dict]:
    """Generate navigation nodes along a corridor segment."""
    x0, z0 = _shift_point(min(corridor["x0"], corridor["x1"]),
                          min(corridor["z0"], corridor["z1"]))
    x1, z1 = _shift_point(max(corridor["x0"], corridor["x1"]),
                          max(corridor["z0"], corridor["z1"]))
    is_main = corridor.get("main", False)
    nodes: list[dict] = []

    if is_main:
        # Place nodes every ~20 m along the corridor
        length = math.hypot(x1 - x0, z1 - z0)
        steps = max(2, int(length / 20))
        for s in range(steps + 1):
            t = s / steps
            nx = x0 + t * (x1 - x0)
            nz = z0 + t * (z1 - z0)
            nodes.append({
                "id": f"CORR-{idx}-{s}",
                "pos": [round(nx, 2), 0.0, round(nz, 2)],
                "type": "corridor_waypoint",
                "corridor_idx": idx,
                "main": True,
            })
    else:
        # Just two endpoints
        nodes.append({
            "id": f"CORR-{idx}-0",
            "pos": [round(x0, 2), 0.0, round(z0, 2)],
            "type": "corridor_waypoint",
            "corridor_idx": idx,
        })
        nodes.append({
            "id": f"CORR-{idx}-1",
            "pos": [round(x1, 2), 0.0, round(z1, 2)],
            "type": "corridor_waypoint",
            "corridor_idx": idx,
        })
    return nodes


def _nearest_node(pos: tuple[float, float],
                  nodes: list[dict], max_dist: float = 60.0) -> dict | None:
    """Find the nearest corridor-waypoint node within *max_dist*."""
    best: dict | None = None
    best_d = max_dist
    for n in nodes:
        if n["type"] != "corridor_waypoint":
            continue
        d = _dist(pos, (n["pos"][0], n["pos"][2]))
        if d < best_d:
            best_d = d
            best = n
    return best


def convert_to_site_map() -> tuple[list[dict], list[dict]]:
    """Convert the embedded blueprint to a site-map graph.

    Returns ``(nodes, edges)`` stored as the UnifiedMap ``topology_json``.

    Node types:
      - ``zone`` — center of each storage zone
      - ``dock`` — each loading dock
      - ``facility`` — each functional facility (QC, sorting, packing, charger)
      - ``corridor_waypoint`` — navigation points along corridors

    Edge strategy:
      1. Consecutive corridor waypoints are linked (path segments).
      2. Each zone / dock / facility connects to its nearest corridor waypoint.
      3. Nearby corridor waypoints from different corridors are linked if
         within 15 m (models intersections / junctions).
    """
    bp = BLUEPRINT
    all_nodes: list[dict] = []
    all_edges: list[dict] = []

    # 1. Corridor waypoint nodes
    for i, c in enumerate(bp["corridors"]):
        all_nodes.extend(_corridor_nodes(c, i))

    # 2. Zone center nodes
    for z in bp["zones"]:
        sx, sz = _shift_point(z["x"], z["z"])
        all_nodes.append({
            "id": z["ref"],
            "pos": [round(sx, 2), 0.0, round(sz, 2)],
            "type": "zone",
            "zone_type": z["type"],
            "capacity": int(z["w"] * z["d"] * 0.5),  # rough capacity proxy
        })

    # 3. Dock nodes
    for d in bp["docks"]:
        sx, sz = _shift_point(d["x"], d["z"])
        all_nodes.append({
            "id": d["ref"],
            "pos": [round(sx, 2), 0.0, round(sz, 2)],
            "type": "dock",
            "flow": d["flow"],
        })

    # 4. Facility nodes
    for f in bp["facilities"]:
        sx, sz = _shift_point(f["x"], f["z"])
        all_nodes.append({
            "id": f["ref"],
            "pos": [round(sx, 2), 0.0, round(sz, 2)],
            "type": "facility",
            "facility_kind": f["kind"],
        })

    # ── Edge generation ───────────────────────────────────────────────────

    corridor_nodes = [n for n in all_nodes if n["type"] == "corridor_waypoint"]
    non_corridor = [n for n in all_nodes if n["type"] != "corridor_waypoint"]

    # 5. Connect consecutive corridor waypoints (same corridor)
    for i, c in enumerate(bp["corridors"]):
        c_nodes = [n for n in corridor_nodes if n.get("corridor_idx") == i]
        for j in range(len(c_nodes) - 1):
            a, b = c_nodes[j], c_nodes[j + 1]
            dist = _dist((a["pos"][0], a["pos"][2]), (b["pos"][0], b["pos"][2]))
            all_edges.append({
                "from": a["id"], "to": b["id"],
                "distance": round(dist, 2),
                "bidirectional": True,
                "speed_limit": 2.0 if c.get("main") else 1.5,
            })

    # 6. Connect nearby corridor waypoints from different corridors (junctions)
    for i, a in enumerate(corridor_nodes):
        for j, b in enumerate(corridor_nodes):
            if j <= i:
                continue
            if a.get("corridor_idx") == b.get("corridor_idx"):
                continue
            dist = _dist((a["pos"][0], a["pos"][2]), (b["pos"][0], b["pos"][2]))
            if dist < 15.0:
                all_edges.append({
                    "from": a["id"], "to": b["id"],
                    "distance": round(dist, 2),
                    "bidirectional": True,
                    "speed_limit": 1.0,
                })

    # 7. Connect each non-corridor node to its nearest corridor waypoint
    for n in non_corridor:
        pos = (n["pos"][0], n["pos"][2])
        nearest = _nearest_node(pos, corridor_nodes, max_dist=60.0)
        if nearest:
            dist = _dist(pos, (nearest["pos"][0], nearest["pos"][2]))
            all_edges.append({
                "from": n["id"], "to": nearest["id"],
                "distance": round(dist, 2),
                "bidirectional": True,
                "speed_limit": 1.0,
            })

    return all_nodes, all_edges
