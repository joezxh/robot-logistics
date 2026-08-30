"""Pre-built warehouse templates spanning all three topology tables.

A warehouse template is not just a navigation graph. To render on the 2D/3D map
and to be instantiable as a working site it needs three artefacts, each of
which lands in its own table:

    robot_topology_shell  →  FloorShell geometry (bounds / walls / zones /
                             facilities / docks / corridors / markings)
    robot_topology_grid   →  one placement row per zone
    robot_site_maps       →  navigation graph (nodes_json / edges_json)

All three are keyed by the same deterministic ``tpl-<key>`` id, which makes
``control_maps.seed_templates()`` idempotent and lets
``create_from_template()`` clone a template into a coherent new site.

Authoring convention
--------------------
Specs below are written in **bottom-left origin** coordinates
(``x ∈ [0, W]``, ``z ∈ [0, D]``). Zones / facilities are authored by *centre*
(for readability) and converted to FloorShell's *corner* form by
``_shell_zone`` / ``_shell_facility``. Corridors are authored as geometric
segments (they drive the navigation graph) and reduced to FloorShell's
zone-to-zone form by :func:`_shell_corridors`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from rcs.models.floor_shell import (
    Bounds,
    Corridor,
    Dock,
    Facility,
    FloorShell,
    Marking,
    WallSegment,
    Zone,
)

WAYPOINT = "corridor_waypoint"
ZONE = "zone"
DOCK = "dock"
FACILITY = "facility"

# Zone type → integer code, matching TopologyGrid.zone_type
# (same mapping as the warehouse import pipeline).
_ZONE_TYPE_INT = {
    "flow_rack": 1, "high_rack": 2, "mezzanine": 3, "automated": 4,
    "temp": 5, "temp_bagged": 6, "returns": 7, "rack": 8,
}


@dataclass(frozen=True)
class SiteMapTemplate:
    """An immutable warehouse-type template."""

    key: str
    name: str
    name_en: str
    category: str
    description: str
    shell: FloorShell
    nodes: list
    edges: list

    @property
    def bounds(self) -> dict:
        return {"w": self.shell.bounds.w, "d": self.shell.bounds.d}

    @property
    def map_id(self) -> str:
        """Primary key in ``robot_site_maps``."""
        return f"tpl-{self.key}"

    @property
    def site_id(self) -> str:
        """Primary key in ``robot_topology_shell`` / FK in ``robot_topology_grid``."""
        return f"tpl-{self.key}"

    def grid_rows(self) -> list[dict]:
        """One ``robot_topology_grid`` row per zone, derived from the shell."""
        rows = []
        for i, z in enumerate(self.shell.zones, start=1):
            rows.append({
                "zone_id": z.id,
                "zone_type": _ZONE_TYPE_INT.get(z.type, 0),
                "center_m": [round(z.x + z.w / 2, 3), round(z.z + z.d / 2, 3)],
                "size_m": [z.w, z.d],
                "rotation_deg": 0.0,
                "data": {"ref": z.ref, "type": z.type, "order": i},
            })
        return rows


# ── Geometry helpers ─────────────────────────────────────────────────────────

def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


# Optional Zone attributes a spec may set; anything else is intentionally
# ignored so typos cannot silently become model fields.
_ZONE_OPTIONAL = ("temperature_range", "batch_tracking", "hazard_level",
                  "customs_regulated")


def _shell_zone(z: dict) -> Zone:
    """Centre-based spec → FloorShell :class:`Zone` (bottom-left corner).

    Temperature range / batch tracking matter for cold chain, customs and
    hazard flags for port and 3PL, so they are passed through when present.
    """
    extra = {k: z[k] for k in _ZONE_OPTIONAL if k in z}
    return Zone(
        id=z["ref"],
        ref=z["ref"],
        type=z["type"],
        x=round(z["x"] - z["w"] / 2, 3),
        z=round(z["z"] - z["d"] / 2, 3),
        w=z["w"],
        d=z["d"],
        name=z.get("name", z["ref"]),
        **extra,
    )


def _shell_facility(f: dict) -> Facility:
    fw = float(f.get("w", 2.0))
    fd = float(f.get("d", fw))
    return Facility(
        id=f["ref"],
        ref=f["ref"],
        type=f["kind"],
        x=round(f["x"] - fw / 2, 3),
        z=round(f["z"] - fd / 2, 3),
        w=fw,
        d=fd,
        h=float(f.get("h", 2.5)),
    )


def _shell_dock(d: dict, bounds: dict, margin: float = 8.0) -> Dock:
    """Infer the door direction from which wall the dock sits against."""
    x, z = d["x"], d["z"]
    if z <= margin:
        direction = "S"
    elif z >= bounds["d"] - margin:
        direction = "N"
    elif x <= margin:
        direction = "W"
    elif x >= bounds["w"] - margin:
        direction = "E"
    else:
        direction = "S"
    return Dock(
        id=d["ref"], ref=d["ref"], x=x, z=z,
        direction=direction, door_w=float(d.get("door_w", 4.0)),
    )


def _perimeter_walls(bounds: dict, h: float = 3.5) -> list[WallSegment]:
    """Four walls tracing the building envelope."""
    w, d = bounds["w"], bounds["d"]
    segs = [
        ("WALL-S", 0.0, 0.0, w, 0.0),
        ("WALL-N", 0.0, d, w, d),
        ("WALL-W", 0.0, 0.0, 0.0, d),
        ("WALL-E", w, 0.0, w, d),
    ]
    return [
        WallSegment(id=i, x0=x0, z0=z0, x1=x1, z1=z1, h=h)
        for i, x0, z0, x1, z1 in segs
    ]


def _shell_corridors(zones: list[Zone]) -> list[Corridor]:
    """Reduce the zone layout to FloorShell's zone-to-zone corridors.

    RCS corridors are semantic links, not geometry: each zone is joined to its
    nearest neighbour, giving an aisle network that ``generate_markings`` can
    turn into lane markings. Pairs are de-duplicated.
    """
    out: list[Corridor] = []
    seen: set[tuple[str, str]] = set()
    for a in zones:
        best, best_d = None, None
        for b in zones:
            if b.id == a.id:
                continue
            d = _dist((a.x + a.w / 2, a.z + a.d / 2), (b.x + b.w / 2, b.z + b.d / 2))
            if best_d is None or d < best_d:
                best_d, best = d, b
        if best is None:
            continue
        pair = tuple(sorted((a.id, best.id)))
        if pair in seen:
            continue
        seen.add(pair)
        out.append(Corridor(
            id=f"CORR-{len(out) + 1:02d}",
            from_zone=pair[0], to_zone=pair[1],
            w=3.0, bidirectional=True,
        ))
    return out


def _markings(shell: FloorShell) -> list[Marking]:
    """Deterministic equivalent of ``topology_markings.generate_markings``.

    The shared helper uses ``uuid4`` for marking ids, which would make every
    template build produce different ids and churn the seeded rows. Here the
    ids are sequential so a template is byte-stable across builds.
    """
    out: list[Marking] = []
    zone_map = {z.id: z for z in shell.zones}
    n = 0
    for c in shell.corridors:
        a, b = zone_map.get(c.from_zone), zone_map.get(c.to_zone)
        if a is None or b is None:
            continue
        ax, az = round(a.x + a.w / 2, 2), round(a.z + a.d / 2, 2)
        bx, bz = round(b.x + b.w / 2, 2), round(b.z + b.d / 2, 2)
        n += 1
        out.append(Marking(id=f"MK-LANE-{n:03d}", kind="lane",
                           points=[[ax, az], [bx, bz]], color="#fbbf24"))
        if c.bidirectional:
            n += 1
            out.append(Marking(id=f"MK-LANE-{n:03d}", kind="lane",
                               points=[[bx, bz], [ax, az]], color="#fbbf24"))
    for i, d in enumerate(shell.docks, start=1):
        out.append(Marking(
            id=f"MK-STOP-{i:03d}", kind="stop",
            points=[[round(d.x - 1.5, 2), d.z], [round(d.x + 1.5, 2), d.z]],
            color="#ef4444",
        ))
    return out


# ── Navigation graph ─────────────────────────────────────────────────────────

def _components(nodes: list[dict], edges: list[dict]) -> list[list[dict]]:
    """Group ``nodes`` into connected components using ``edges`` (union-find)."""
    parent = {n["id"]: n["id"] for n in nodes}

    def find(a: str) -> str:
        while parent[a] != a:
            parent[a] = parent[parent[a]]  # path halving
            a = parent[a]
        return a

    for e in edges:
        if e["from"] not in parent or e["to"] not in parent:
            continue
        ra, rb = find(e["from"]), find(e["to"])
        if ra != rb:
            parent[ra] = rb

    groups: dict[str, list[dict]] = {}
    for n in nodes:
        groups.setdefault(find(n["id"]), []).append(n)
    return list(groups.values())


def _connect_components(waypoints: list[dict], edges: list[dict],
                        max_links: int, speed: float) -> None:
    """Mutate ``edges`` until the waypoint network is a single component.

    Corridors that never come within the junction radius would otherwise form
    isolated islands no vehicle can route between. Repeatedly link the two
    closest components (Prim-style).
    """
    for _ in range(max_links):
        comps = _components(waypoints, edges)
        if len(comps) <= 1:
            return
        best: tuple[float, dict, dict] | None = None
        for i in range(len(comps)):
            for j in range(i + 1, len(comps)):
                for a in comps[i]:
                    for b in comps[j]:
                        d = _dist((a["pos"][0], a["pos"][2]),
                                  (b["pos"][0], b["pos"][2]))
                        if best is None or d < best[0]:
                            best = (d, a, b)
        if best is None:
            return
        d, a, b = best
        edges.append({
            "from": a["id"], "to": b["id"], "distance": round(d, 2),
            "bidirectional": True, "speed_limit": speed,
        })


def _corridor_waypoints(corridor: dict, idx: int, spacing: float) -> list[dict]:
    x0, z0 = float(corridor["x0"]), float(corridor["z0"])
    x1, z1 = float(corridor["x1"]), float(corridor["z1"])
    length = _dist((x0, z0), (x1, z1))
    steps = max(2, int(round(length / spacing))) if corridor.get("main") else 1

    out: list[dict] = []
    for s in range(steps + 1):
        t = s / steps
        node = {
            "id": f"CORR-{idx}-{s}",
            "pos": [round(x0 + t * (x1 - x0), 2), 0.0, round(z0 + t * (z1 - z0), 2)],
            "type": WAYPOINT,
            "corridor_idx": idx,
        }
        if corridor.get("main"):
            node["main"] = True
        out.append(node)
    return out


def _nearest_waypoint(pos: tuple[float, float], waypoints: list[dict],
                      max_dist: float) -> dict | None:
    best: dict | None = None
    best_d = max_dist
    for n in waypoints:
        d = _dist(pos, (n["pos"][0], n["pos"][2]))
        if d < best_d:
            best_d, best = d, n
    return best


def _build_graph(*, zones: list[dict], docks: list[dict], facilities: list[dict],
                 corridors: list[dict], spacing: float = 25.0,
                 junction_radius: float = 15.0,
                 speed_main: float = 2.0, speed_branch: float = 1.5,
                 speed_spur: float = 1.0) -> tuple[list[dict], list[dict]]:
    """Turn a declarative layout spec into ``(nodes, edges)``."""
    nodes: list[dict] = []
    for i, c in enumerate(corridors):
        nodes.extend(_corridor_waypoints(c, i, spacing))

    for z in zones:
        nodes.append({
            "id": z["ref"],
            "pos": [round(z["x"], 2), 0.0, round(z["z"], 2)],
            "type": ZONE,
            "zone_type": z["type"],
            "w": z["w"], "d": z["d"],
            "capacity": int(z["w"] * z["d"] * 0.5),
        })
    for d in docks:
        nodes.append({
            "id": d["ref"],
            "pos": [round(d["x"], 2), 0.0, round(d["z"], 2)],
            "type": DOCK, "flow": d["flow"],
        })
    for f in facilities:
        nodes.append({
            "id": f["ref"],
            "pos": [round(f["x"], 2), 0.0, round(f["z"], 2)],
            "type": FACILITY, "facility_kind": f["kind"],
        })

    waypoints = [n for n in nodes if n["type"] == WAYPOINT]
    leaves = [n for n in nodes if n["type"] != WAYPOINT]
    edges: list[dict] = []

    # 1. Chain consecutive waypoints of the same corridor.
    for i, c in enumerate(corridors):
        chain = [n for n in waypoints if n.get("corridor_idx") == i]
        limit = speed_main if c.get("main") else speed_branch
        for a, b in zip(chain, chain[1:]):
            edges.append({
                "from": a["id"], "to": b["id"],
                "distance": round(_dist((a["pos"][0], a["pos"][2]),
                                        (b["pos"][0], b["pos"][2])), 2),
                "bidirectional": True, "speed_limit": limit,
            })

    # 2. Junction links between distinct corridors that physically meet.
    for i, a in enumerate(waypoints):
        for b in waypoints[i + 1:]:
            if a.get("corridor_idx") == b.get("corridor_idx"):
                continue
            d = _dist((a["pos"][0], a["pos"][2]), (b["pos"][0], b["pos"][2]))
            if d < junction_radius:
                edges.append({
                    "from": a["id"], "to": b["id"], "distance": round(d, 2),
                    "bidirectional": True, "speed_limit": speed_spur,
                })

    # 3. Guarantee one connected waypoint network.
    _connect_components(waypoints, edges,
                        max_links=len(corridors) + 1, speed=speed_spur)

    # 4. Spur every zone / dock / facility onto its nearest waypoint.
    for n in leaves:
        pos = (n["pos"][0], n["pos"][2])
        near = _nearest_waypoint(pos, waypoints, max_dist=10_000.0)
        if near is None:
            continue
        edges.append({
            "from": n["id"], "to": near["id"],
            "distance": round(_dist(pos, (near["pos"][0], near["pos"][2])), 2),
            "bidirectional": True, "speed_limit": speed_spur,
        })

    return nodes, edges


# ── Repetitive-layout generators ─────────────────────────────────────────────

def _dock_row(start_x: float, end_x: float, z: float, count: int,
              prefix: str = "DOCK") -> list[dict]:
    if count < 1:
        return []
    step = (end_x - start_x) / (count - 1) if count > 1 else 0.0
    return [
        {"ref": f"{prefix}-{i + 1}", "x": round(start_x + step * i, 2), "z": z,
         "flow": "inbound" if i % 2 == 0 else "outbound"}
        for i in range(count)
    ]


def _chargers(x: float, z0: float, count: int, step: float = 6.0,
              start: int = 1) -> list[dict]:
    return [
        {"ref": f"CHG-{start + i}", "kind": "charger",
         "x": x, "z": round(z0 + step * i, 2)}
        for i in range(count)
    ]


def _assemble(*, key: str, name: str, name_en: str, category: str,
              description: str, bounds: dict, zones: list[dict],
              docks: list[dict], facilities: list[dict], corridors: list[dict],
              spacing: float = 25.0, junction_radius: float = 15.0,
              speed_main: float = 2.0, speed_branch: float = 1.5,
              speed_spur: float = 1.0) -> SiteMapTemplate:
    """Build a template from one declarative spec (shell + graph)."""
    shell_zones = [_shell_zone(z) for z in zones]
    shell = FloorShell(
        bounds=Bounds(w=bounds["w"], d=bounds["d"], h=bounds.get("h", 0)),
        walls=_perimeter_walls(bounds),
        zones=shell_zones,
        facilities=[_shell_facility(f) for f in facilities],
        docks=[_shell_dock(d, bounds) for d in docks],
        metadata={"template_key": key, "name": name, "category": category},
    )
    # Assigned after construction: both derive from the populated zone list.
    shell.corridors = _shell_corridors(shell_zones)
    shell.markings = _markings(shell)

    nodes, edges = _build_graph(
        zones=zones, docks=docks, facilities=facilities, corridors=corridors,
        spacing=spacing, junction_radius=junction_radius,
        speed_main=speed_main, speed_branch=speed_branch, speed_spur=speed_spur,
    )
    return SiteMapTemplate(
        key=key, name=name, name_en=name_en, category=category,
        description=description, shell=shell, nodes=nodes, edges=edges,
    )


# ── Template 1: 大型电商仓 ────────────────────────────────────────────────────

def _ecommerce_large() -> SiteMapTemplate:
    return _assemble(
        key="ecommerce_large", name="大型电商仓",
        name_en="Large E-Commerce Warehouse", category="ecommerce",
        description="高吞吐 B2C 履约仓：月台收货 → 质检 → 分拣 → 打包 → 出库，"
                    "含流利架区、高位货架、夹层与 ASRS 自动化立体库。",
        bounds={"w": 160, "d": 100},
        zones=[
            {"ref": "FLOW-1", "type": "flow_rack", "x": 30, "z": 52, "w": 44, "d": 22},
            {"ref": "FLOW-2", "type": "flow_rack", "x": 80, "z": 52, "w": 44, "d": 22},
            {"ref": "MEZZ-1", "type": "mezzanine", "x": 130, "z": 52, "w": 44, "d": 22},
            {"ref": "RACK-1", "type": "high_rack", "x": 30, "z": 82, "w": 44, "d": 22},
            {"ref": "ASRS-1", "type": "automated", "x": 80, "z": 82, "w": 44, "d": 22},
            {"ref": "RACK-2", "type": "high_rack", "x": 130, "z": 82, "w": 44, "d": 22},
            {"ref": "TEMP-1", "type": "temp", "x": 10, "z": 64, "w": 12, "d": 14},
            {"ref": "RET-1", "type": "returns", "x": 150, "z": 64, "w": 12, "d": 14},
            {"ref": "STG-1", "type": "staging", "x": 150, "z": 30, "w": 16, "d": 20},
        ],
        docks=_dock_row(15, 145, 3, 9),
        facilities=[
            {"ref": "QC-1", "kind": "qc", "x": 20, "z": 14, "w": 14, "d": 6},
            {"ref": "QC-2", "kind": "qc", "x": 140, "z": 14, "w": 14, "d": 6},
            {"ref": "SORT-1", "kind": "sorting", "x": 50, "z": 16, "w": 16, "d": 6},
            {"ref": "SORT-2", "kind": "sorting", "x": 80, "z": 16, "w": 16, "d": 6},
            {"ref": "SORT-3", "kind": "sorting", "x": 110, "z": 16, "w": 16, "d": 6},
            {"ref": "PACK-1", "kind": "packing", "x": 50, "z": 27, "w": 16, "d": 6},
            {"ref": "PACK-2", "kind": "packing", "x": 80, "z": 27, "w": 16, "d": 6},
            {"ref": "PACK-3", "kind": "packing", "x": 110, "z": 27, "w": 16, "d": 6},
            *_chargers(6, 20, 3),
            *_chargers(154, 20, 3, start=4),
        ],
        corridors=[
            {"x0": 8, "z0": 8, "x1": 152, "z1": 8, "main": True},
            {"x0": 8, "z0": 38, "x1": 152, "z1": 38, "main": True},
            {"x0": 8, "z0": 68, "x1": 152, "z1": 68, "main": True},
            {"x0": 80, "z0": 8, "x1": 80, "z1": 94, "main": True},
            {"x0": 52, "z0": 8, "x1": 52, "z1": 38},
            {"x0": 108, "z0": 8, "x1": 108, "z1": 38},
            {"x0": 30, "z0": 38, "x1": 30, "z1": 94},
            {"x0": 130, "z0": 38, "x1": 130, "z1": 94},
        ],
    )


# ── Template 2: 港口集装箱码头 ────────────────────────────────────────────────

def _port_terminal() -> SiteMapTemplate:
    return _assemble(
        key="port_terminal", name="港口集装箱码头",
        name_en="Port Container Terminal", category="port",
        description="集装箱码头：泊位 ↔ 堆场（6 个箱区）↔ 闸口，含冷藏箱区、"
                    "危险品区、空箱堆场与 CFS 拆装箱库。",
        bounds={"w": 300, "d": 180},
        zones=[
            {"ref": "YARD-A", "type": "container_yard", "x": 50, "z": 130, "w": 80, "d": 40},
            {"ref": "YARD-B", "type": "container_yard", "x": 150, "z": 130, "w": 80, "d": 40},
            {"ref": "YARD-C", "type": "container_yard", "x": 250, "z": 130, "w": 80, "d": 40},
            {"ref": "YARD-D", "type": "container_yard", "x": 50, "z": 75, "w": 80, "d": 40},
            {"ref": "YARD-E", "type": "container_yard", "x": 150, "z": 75, "w": 80, "d": 40},
            {"ref": "YARD-F", "type": "container_yard", "x": 250, "z": 75, "w": 80, "d": 40},
            {"ref": "REEFER-1", "type": "cold_zone", "x": 45, "z": 25, "w": 50, "d": 30},
            {"ref": "CUSTOMS-1", "type": "customs_area", "x": 108, "z": 25, "w": 30, "d": 30,
             "customs_regulated": True},
            {"ref": "STG-EMPTY", "type": "staging", "x": 240, "z": 25, "w": 100, "d": 30},
        ],
        docks=_dock_row(50, 248, 174, 4, prefix="BERTH"),
        facilities=[
            {"ref": "GATE-IN", "kind": "gate", "x": 20, "z": 10, "w": 6, "d": 4},
            {"ref": "GATE-OUT", "kind": "gate", "x": 280, "z": 10, "w": 6, "d": 4},
            {"ref": "CFS-1", "kind": "cfs", "x": 180, "z": 25, "w": 24, "d": 16},
            {"ref": "INSP-1", "kind": "inspection", "x": 140, "z": 25, "w": 20, "d": 16},
            *_chargers(12, 60, 3),
            *_chargers(288, 60, 3, start=4),
        ],
        corridors=[
            {"x0": 10, "z0": 160, "x1": 290, "z1": 160, "main": True},
            {"x0": 10, "z0": 105, "x1": 290, "z1": 105, "main": True},
            {"x0": 10, "z0": 52, "x1": 290, "z1": 52, "main": True},
            {"x0": 100, "z0": 52, "x1": 100, "z1": 160, "main": True},
            {"x0": 200, "z0": 52, "x1": 200, "z1": 160, "main": True},
            {"x0": 50, "z0": 52, "x1": 50, "z1": 160},
            {"x0": 150, "z0": 52, "x1": 150, "z1": 160},
            {"x0": 250, "z0": 52, "x1": 250, "z1": 160},
        ],
        spacing=40.0, junction_radius=25.0,
        speed_main=3.0, speed_branch=2.0,
    )


# ── Template 3: 工厂仓库 ──────────────────────────────────────────────────────

def _factory_warehouse() -> SiteMapTemplate:
    return _assemble(
        key="factory_warehouse", name="工厂仓库",
        name_en="Factory Warehouse", category="manufacturing",
        description="生产配套仓：原料库 → 线边库（3 条产线）→ 在制品缓冲 → 成品库，"
                    "配套质检室与工具间，强调 JIT 配送节拍。",
        bounds={"w": 120, "d": 80},
        zones=[
            {"ref": "RAW-1", "type": "parts_storage", "x": 25, "z": 52, "w": 30, "d": 20},
            {"ref": "RAW-2", "type": "parts_storage", "x": 60, "z": 52, "w": 30, "d": 20},
            {"ref": "WIP-1", "type": "wip_buffer", "x": 95, "z": 52, "w": 20, "d": 20},
            {"ref": "FG-1", "type": "staging", "x": 30, "z": 25, "w": 30, "d": 18},
            {"ref": "FG-2", "type": "staging", "x": 70, "z": 25, "w": 30, "d": 18},
            {"ref": "LINE-A", "type": "production_line", "x": 25, "z": 75, "w": 25, "d": 6},
            {"ref": "LINE-B", "type": "production_line", "x": 60, "z": 75, "w": 25, "d": 6},
            {"ref": "LINE-C", "type": "production_line", "x": 95, "z": 75, "w": 20, "d": 6},
        ],
        docks=[
            {"ref": "DOCK-IN-1", "x": 25, "z": 3, "flow": "inbound"},
            {"ref": "DOCK-IN-2", "x": 45, "z": 3, "flow": "inbound"},
            {"ref": "DOCK-OUT-1", "x": 75, "z": 3, "flow": "outbound"},
            {"ref": "DOCK-OUT-2", "x": 95, "z": 3, "flow": "outbound"},
        ],
        facilities=[
            {"ref": "QC-LAB", "kind": "qc", "x": 12, "z": 20, "w": 10, "d": 8},
            {"ref": "TOOL-1", "kind": "tool_room", "x": 110, "z": 40, "w": 8, "d": 10},
            *_chargers(6, 20, 3),
        ],
        corridors=[
            {"x0": 8, "z0": 12, "x1": 112, "z1": 12, "main": True},
            {"x0": 8, "z0": 40, "x1": 112, "z1": 40, "main": True},
            {"x0": 8, "z0": 66, "x1": 112, "z1": 66, "main": True},
            {"x0": 45, "z0": 12, "x1": 45, "z1": 66},
            {"x0": 85, "z0": 12, "x1": 85, "z1": 66},
        ],
        spacing=20.0,
    )


# ── Template 4: 货运公路港 ────────────────────────────────────────────────────

def _highway_freight_hub() -> SiteMapTemplate:
    return _assemble(
        key="highway_freight_hub", name="货运公路港",
        name_en="Highway Freight Hub", category="freight",
        description="干线运输枢纽：12 个货车泊位 + 越库月台 + 零担分拨 + 集拼区，"
                    "配套地磅、加油、司机之家与大件/停车区。",
        bounds={"w": 240, "d": 160},
        zones=[
            {"ref": "XDOCK-1", "type": "staging", "x": 60, "z": 45, "w": 90, "d": 30},
            {"ref": "CONSOL-1", "type": "staging", "x": 170, "z": 45, "w": 50, "d": 30},
            {"ref": "LTL-A", "type": "staging", "x": 60, "z": 95, "w": 70, "d": 30},
            {"ref": "LTL-B", "type": "staging", "x": 160, "z": 95, "w": 70, "d": 30},
            {"ref": "PARK-A", "type": "staging", "x": 25, "z": 130, "w": 40, "d": 30},
            {"ref": "PARK-B", "type": "staging", "x": 215, "z": 130, "w": 40, "d": 30},
            {"ref": "BULK-1", "type": "staging", "x": 120, "z": 130, "w": 60, "d": 30},
        ],
        docks=_dock_row(20, 220, 6, 12, prefix="BAY"),
        facilities=[
            {"ref": "WEIGH-1", "kind": "weighbridge", "x": 20, "z": 20, "w": 12, "d": 8},
            {"ref": "INSP-1", "kind": "inspection", "x": 60, "z": 20, "w": 14, "d": 8},
            {"ref": "FUEL-1", "kind": "fuel", "x": 120, "z": 20, "w": 16, "d": 10},
            {"ref": "DRIVER-1", "kind": "driver_service", "x": 220, "z": 20, "w": 18, "d": 12},
            *_chargers(10, 60, 3),
            *_chargers(230, 60, 3, start=4),
        ],
        corridors=[
            {"x0": 10, "z0": 30, "x1": 230, "z1": 30, "main": True},
            {"x0": 10, "z0": 80, "x1": 230, "z1": 80, "main": True},
            {"x0": 10, "z0": 118, "x1": 230, "z1": 118, "main": True},
            {"x0": 120, "z0": 6, "x1": 120, "z1": 30, "main": True},
            {"x0": 60, "z0": 30, "x1": 60, "z1": 118},
            {"x0": 160, "z0": 30, "x1": 160, "z1": 118},
        ],
        spacing=30.0, junction_radius=20.0,
        speed_main=2.5, speed_branch=1.8,
    )


# ── Template 5: 第三方物流仓库 ────────────────────────────────────────────────

def _third_party_logistics() -> SiteMapTemplate:
    return _assemble(
        key="third_party_logistics", name="第三方物流仓库",
        name_en="3PL Warehouse", category="third_party",
        description="多货主共享仓：按客户分区（A/B/C）+ 保税区 + 增值服务（VAS）区 + "
                    "退货区，共享月台与暂存区，适合 3PL 运营。",
        bounds={"w": 200, "d": 120},
        zones=[
            {"ref": "CLI-A", "type": "high_rack", "x": 35, "z": 50, "w": 50, "d": 30},
            {"ref": "CLI-B", "type": "high_rack", "x": 100, "z": 50, "w": 50, "d": 30},
            {"ref": "CLI-C", "type": "high_rack", "x": 165, "z": 50, "w": 50, "d": 30},
            {"ref": "BONDED-1", "type": "customs_area", "x": 35, "z": 95, "w": 50, "d": 30,
             "customs_regulated": True},
            {"ref": "VAS-1", "type": "staging", "x": 100, "z": 95, "w": 50, "d": 30},
            {"ref": "RET-1", "type": "returns", "x": 165, "z": 95, "w": 50, "d": 30},
            {"ref": "STG-1", "type": "staging", "x": 188, "z": 20, "w": 16, "d": 24},
        ],
        docks=_dock_row(20, 180, 3, 8),
        facilities=[
            {"ref": "QC-1", "kind": "qc", "x": 30, "z": 16, "w": 14, "d": 8},
            {"ref": "VAS-WORK", "kind": "value_added", "x": 100, "z": 16, "w": 20, "d": 8},
            {"ref": "OFFICE", "kind": "office", "x": 170, "z": 16, "w": 18, "d": 8},
            *_chargers(8, 30, 3),
            *_chargers(192, 45, 3, start=4),
        ],
        corridors=[
            {"x0": 10, "z0": 12, "x1": 190, "z1": 12, "main": True},
            {"x0": 10, "z0": 35, "x1": 190, "z1": 35, "main": True},
            {"x0": 10, "z0": 80, "x1": 190, "z1": 80, "main": True},
            {"x0": 65, "z0": 35, "x1": 65, "z1": 112},
            {"x0": 130, "z0": 35, "x1": 130, "z1": 112},
        ],
        spacing=28.0, junction_radius=18.0,
    )


# ── Template 6: warehouse_theatre_3d 大型电商仓 ───────────────────────────────

def _theatre_ecommerce() -> SiteMapTemplate:
    """The warehouse_theatre_3d reference warehouse, as an RCS template.

    Reuses the existing converter so there is a single source of truth for that
    layout: it already performs the centre-origin → bottom-left conversion and
    produces both artefacts. Two fix-ups are applied on top:

    * the converter's graph has no connectivity guarantee, so the waypoint
      network is repaired with :func:`_connect_components`;
    * zone nodes are enriched with their footprint, matching the other
      templates' node shape.
    """
    from rcs.services.warehouse_converter import (
        BLUEPRINT, convert_to_floor_shell, convert_to_site_map,
    )

    shell = FloorShell(**convert_to_floor_shell())
    nodes, edges = convert_to_site_map()

    # Restore a stable FloorShell.corridors set: the converter writes
    # placeholder from_zone/to_zone ids that do not exist in `zones`, which
    # makes generate_markings (and any corridor-aware consumer) skip them all.
    shell.corridors = _shell_corridors(shell.zones)
    shell.markings = _markings(shell)

    # Enrich zone nodes with w/d so all templates share one node shape.
    by_ref = {z["ref"]: z for z in BLUEPRINT["zones"]}
    for n in nodes:
        if n["type"] == ZONE and n["id"] in by_ref:
            src = by_ref[n["id"]]
            n["w"] = src["w"]
            n["d"] = src["d"]

    # wt3d parks its loading docks on the apron *outside* the south wall
    # (z = -3 once shifted). RCS treats the building envelope as [0, W]×[0, D],
    # so pull any out-of-range geometry onto the wall line — in the shell and in
    # the graph alike — then recompute edge distances against the new positions.
    def _clamp(v: float, hi: float) -> float:
        return min(max(v, 0.0), hi)

    for d in shell.docks:
        d.x = _clamp(d.x, shell.bounds.w)
        d.z = _clamp(d.z, shell.bounds.d)
    for n in nodes:
        n["pos"][0] = round(_clamp(n["pos"][0], shell.bounds.w), 2)
        n["pos"][2] = round(_clamp(n["pos"][2], shell.bounds.d), 2)

    # The converter links zones/docks/facilities to the nearest waypoint but
    # never repairs a fragmented corridor network.
    waypoints = [n for n in nodes if n["type"] == WAYPOINT]
    _connect_components(waypoints, edges,
                        max_links=len(BLUEPRINT["corridors"]) + 1, speed=1.0)

    # Clamping moved some nodes, so every stored distance is now stale.
    pos = {n["id"]: (n["pos"][0], n["pos"][2]) for n in nodes}
    for e in edges:
        e["distance"] = round(_dist(pos[e["from"]], pos[e["to"]]), 2)

    return SiteMapTemplate(
        key="theatre_ecommerce", name="大型电商仓（warehouse_theatre_3d）",
        name_en="Large E-Commerce Warehouse (warehouse_theatre_3d)",
        category="ecommerce",
        description="来自 warehouse_theatre_3d 参考 3D 仓库：4 个月台、双向分拣打包线、"
                    "流利架/高位货架/夹层四大存储区与 80×16m 的 ASRS 立体库，"
                    "含温控区与退货区。",
        shell=shell, nodes=nodes, edges=edges,
    )


# ── Template 7: 冷链仓 ────────────────────────────────────────────────────────

def _cold_chain() -> SiteMapTemplate:
    return _assemble(
        key="cold_chain", name="冷链仓",
        name_en="Cold Chain Warehouse", category="cold_chain",
        description="多温层冷链仓：冷冻区（-25~-18℃）+ 冷藏区（2~8℃）+ 常温区，"
                    "配速冻机与解冻间，穿堂式温控月台，全批次追溯。",
        bounds={"w": 120, "d": 80},
        zones=[
            # Frozen deck — north, furthest from the dock doors.
            {"ref": "FZ-1", "type": "frozen_zone", "x": 28, "z": 70, "w": 48, "d": 18,
             "temperature_range": {"min": -25, "max": -18}, "batch_tracking": True},
            {"ref": "FZ-2", "type": "frozen_zone", "x": 76, "z": 70, "w": 48, "d": 18,
             "temperature_range": {"min": -25, "max": -18}, "batch_tracking": True},
            # Chilled deck — middle.
            {"ref": "CZ-1", "type": "cold_zone", "x": 28, "z": 44, "w": 48, "d": 28,
             "temperature_range": {"min": 2, "max": 8}, "batch_tracking": True},
            {"ref": "CZ-2", "type": "cold_zone", "x": 76, "z": 44, "w": 48, "d": 28,
             "temperature_range": {"min": 2, "max": 8}, "batch_tracking": True},
            # Temperature-controlled loading bays directly behind the doors.
            {"ref": "LB-IN", "type": "loading_bay", "x": 28, "z": 16, "w": 48, "d": 20,
             "temperature_range": {"min": 2, "max": 8}},
            {"ref": "LB-OUT", "type": "loading_bay", "x": 76, "z": 16, "w": 48, "d": 20,
             "temperature_range": {"min": 2, "max": 8}},
            # Ambient handling + quarantine on the warm east column.
            {"ref": "AZ-1", "type": "ambient_zone", "x": 108, "z": 30, "w": 20, "d": 26},
            {"ref": "QUAR-1", "type": "staging", "x": 108, "z": 62, "w": 20, "d": 26,
             "name": "待处理/隔离区"},
        ],
        docks=[
            {"ref": "DOCK-IN-1", "x": 24, "z": 2, "flow": "inbound", "door_w": 3.0},
            {"ref": "DOCK-IN-2", "x": 36, "z": 2, "flow": "inbound", "door_w": 3.0},
            {"ref": "DOCK-OUT-1", "x": 72, "z": 2, "flow": "outbound", "door_w": 3.0},
            {"ref": "DOCK-OUT-2", "x": 84, "z": 2, "flow": "outbound", "door_w": 3.0},
        ],
        facilities=[
            {"ref": "BLAST-1", "kind": "blast_freezer", "x": 20, "z": 30, "w": 12, "d": 8},
            {"ref": "QC-1", "kind": "qc", "x": 60, "z": 30, "w": 12, "d": 8},
            {"ref": "DEFROST-1", "kind": "defrost", "x": 100, "z": 30, "w": 12, "d": 8},
            {"ref": "MON-1", "kind": "monitoring", "x": 110, "z": 76, "w": 10, "d": 6},
            *_chargers(2, 32, 3),
        ],
        corridors=[
            {"x0": 4, "z0": 2, "x1": 116, "z1": 4, "main": True},    # dock apron
            {"x0": 4, "z0": 28, "x1": 116, "z1": 30, "main": True},  # bay → chilled
            {"x0": 4, "z0": 59, "x1": 100, "z1": 61, "main": True},  # chilled → frozen
            {"x0": 59, "z0": 2, "x1": 61, "z1": 78, "main": True},   # central spine
            {"x0": 27, "z0": 28, "x1": 29, "z1": 78},
            {"x0": 75, "z0": 28, "x1": 77, "z1": 78},
            {"x0": 103, "z0": 2, "x1": 105, "z1": 78},
        ],
    )


# ── Template 8: 逆向退货仓 ────────────────────────────────────────────────────

def _reverse_logistics() -> SiteMapTemplate:
    return _assemble(
        key="reverse_logistics", name="逆向退货仓",
        name_en="Reverse Logistics Warehouse", category="reverse_logistics",
        description="退货逆向处理中心：退货接收 → 质检分级 → 重新上架 / 翻新维修 / "
                    "报废销毁，双流向分拣，支持二次销售与残值回收。",
        bounds={"w": 100, "d": 70},
        zones=[
            # Inbound returns land here first.
            {"ref": "RR-1", "type": "returns_received", "x": 30, "z": 14, "w": 52, "d": 16},
            # Two triage / grading cells.
            {"ref": "QC-A", "type": "qc_staging", "x": 20, "z": 38, "w": 30, "d": 20},
            {"ref": "QC-B", "type": "qc_staging", "x": 55, "z": 38, "w": 30, "d": 20},
            # Disposition outcomes: restock, refurbish, dispose.
            {"ref": "RS-1", "type": "reshelving", "x": 28, "z": 60, "w": 46, "d": 16},
            {"ref": "RF-1", "type": "staging", "x": 76, "z": 60, "w": 36, "d": 16,
             "name": "翻新维修区"},
            {"ref": "DP-1", "type": "disposal", "x": 85, "z": 14, "w": 22, "d": 16,
             "hazard_level": "low"},
            {"ref": "STG-1", "type": "staging", "x": 85, "z": 38, "w": 22, "d": 20,
             "name": "待判定暂存"},
        ],
        docks=[
            {"ref": "DOCK-IN-1", "x": 15, "z": 2, "flow": "inbound"},
            {"ref": "DOCK-IN-2", "x": 30, "z": 2, "flow": "inbound"},
            {"ref": "DOCK-IN-3", "x": 45, "z": 2, "flow": "inbound"},
            {"ref": "DOCK-OUT-1", "x": 80, "z": 2, "flow": "outbound"},
            {"ref": "DOCK-OUT-2", "x": 92, "z": 2, "flow": "outbound"},
        ],
        facilities=[
            {"ref": "INSP-1", "kind": "inspection", "x": 37, "z": 38, "w": 5, "d": 14},
            {"ref": "REPACK-1", "kind": "repack", "x": 37, "z": 52, "w": 14, "d": 6},
            {"ref": "SHRED-1", "kind": "destruction", "x": 85, "z": 24, "w": 10, "d": 4},
            *_chargers(2, 20, 3),
        ],
        corridors=[
            {"x0": 4, "z0": 2, "x1": 96, "z1": 4, "main": True},    # dock apron
            {"x0": 4, "z0": 24, "x1": 96, "z1": 26, "main": True},  # receiving → QC
            {"x0": 4, "z0": 50, "x1": 96, "z1": 52, "main": True},  # QC → disposition
            {"x0": 37, "z0": 2, "x1": 39, "z1": 68, "main": True},  # central spine
            {"x0": 67, "z0": 2, "x1": 69, "z1": 68},                # east spine
            {"x0": 19, "z0": 26, "x1": 21, "z1": 52},               # QC-A branch
            {"x0": 54, "z0": 26, "x1": 56, "z1": 52},               # QC-B branch
        ],
    )


# ── Registry ─────────────────────────────────────────────────────────────────

_BUILDERS = {
    "ecommerce_large": _ecommerce_large,
    "theatre_ecommerce": _theatre_ecommerce,
    "port_terminal": _port_terminal,
    "factory_warehouse": _factory_warehouse,
    "highway_freight_hub": _highway_freight_hub,
    "third_party_logistics": _third_party_logistics,
    "cold_chain": _cold_chain,
    "reverse_logistics": _reverse_logistics,
}

TEMPLATE_KEYS: list[str] = list(_BUILDERS)


def list_templates() -> list[SiteMapTemplate]:
    """Return every warehouse template, in registry order."""
    return [builder() for builder in _BUILDERS.values()]


def get_template(key: str) -> SiteMapTemplate:
    """Return one template by ``key``.

    Raises:
        KeyError: if ``key`` is not a known template.
    """
    try:
        return _BUILDERS[key]()
    except KeyError:
        raise KeyError(f"unknown site-map template: {key}") from None


def template_map_id(key: str) -> str:
    """Deterministic ``robot_site_maps.map_id`` for a template key."""
    return f"tpl-{key}"


def template_summary(t: SiteMapTemplate) -> dict[str, Any]:
    """Compact, API-friendly summary (no node/edge payloads)."""
    kinds: dict[str, int] = {}
    for n in t.nodes:
        kinds[n["type"]] = kinds.get(n["type"], 0) + 1
    return {
        "key": t.key,
        "map_id": t.map_id,
        "site_id": t.site_id,
        "name": t.name,
        "name_en": t.name_en,
        "category": t.category,
        "description": t.description,
        "bounds": t.bounds,
        "node_count": len(t.nodes),
        "edge_count": len(t.edges),
        "node_types": kinds,
        "zone_count": len(t.shell.zones),
        "facility_count": len(t.shell.facilities),
        "dock_count": len(t.shell.docks),
        "wall_count": len(t.shell.walls),
        "grid_row_count": len(t.grid_rows()),
    }
