"""Convert unified-map geometry into a mujoco MJCF scene for the 3D viewer.

The authoritative geometry schema is ``wt_floor_shell`` (from warehouse_theatre_3d),
top-level keys: ``bounds / walls / docks / facilities / zones / corridors``. Each
element is a dict with 11 fields: ``ref, type, x, z, w, d, h, y, rot, color, label``.

Two entry points:
* :func:`build_mjcf` — geometry dict (or JSON string) -> MJCF XML string.
* :func:`_floor_shell_to_wt` — legacy ``FloorShell`` dict -> ``wt_floor_shell`` dict
  (used by the seeder so every scenario ships a wt-compatible geometry_json).
"""
from __future__ import annotations

import json
import xml.dom.minidom
from typing import Any, Iterable, Iterator

# ── zone / dock body registry ────────────────────────────────────────────────
# New layout element *type* => box/cylinder template. Add an entry here to make a
# new zone/dock type render with zero logic changes. Missing types fall back to
# "staging" (neutral gray box).
ZONE_BODY_TEMPLATES: dict[str, dict[str, Any]] = {
    "staging":         {"shape": "box", "default_h": 0.6, "color": "#9ca3af", "opacity": 0.5},
    "flow_rack":       {"shape": "box", "default_h": 2.0, "color": "#3b82f6", "opacity": 0.8},
    "high_rack":       {"shape": "box", "default_h": 4.0, "color": "#1d4ed8", "opacity": 0.85},
    "mezzanine":       {"shape": "box", "default_h": 2.5, "color": "#0ea5e9", "opacity": 0.8},
    "asrs":            {"shape": "box", "default_h": 5.0, "color": "#2563eb", "opacity": 0.85},
    "rack":            {"shape": "box", "default_h": 3.0, "color": "#3b82f6", "opacity": 0.8},
    "shelf":           {"shape": "box", "default_h": 2.0, "color": "#60a5fa", "opacity": 0.8},
    # temperature zones (wt_floor_shell names)
    "temp_cold":       {"shape": "box", "default_h": 3.0, "color": "#38bdf8", "opacity": 0.8},
    "temp_frozen":     {"shape": "box", "default_h": 3.0, "color": "#22d3ee", "opacity": 0.8},
    "frozen_zone":     {"shape": "box", "default_h": 3.0, "color": "#22d3ee", "opacity": 0.8},
    "cold_zone":       {"shape": "box", "default_h": 3.0, "color": "#38bdf8", "opacity": 0.8},
    "ambient_zone":    {"shape": "box", "default_h": 3.0, "color": "#a3e635", "opacity": 0.8},
    "reefer":          {"shape": "box", "default_h": 3.0, "color": "#06b6d4", "opacity": 0.8},
    # factories / production
    "production_line": {"shape": "box", "default_h": 1.5, "color": "#f97316", "opacity": 0.85},
    "wip_buffer":      {"shape": "box", "default_h": 1.0, "color": "#fb923c", "opacity": 0.7},
    "parts_storage":   {"shape": "box", "default_h": 2.0, "color": "#fdba74", "opacity": 0.8},
    "office":          {"shape": "box", "default_h": 3.0, "color": "#a78bfa", "opacity": 0.85},
    # freight / port
    "container_yard":  {"shape": "box", "default_h": 2.6, "color": "#0d9488", "opacity": 0.85},
    "customs_area":    {"shape": "box", "default_h": 1.2, "color": "#14b8a6", "opacity": 0.7},
    "rail_track":      {"shape": "box", "default_h": 0.3, "color": "#44403c", "opacity": 0.9},
    "train_car":       {"shape": "box", "default_h": 4.0, "color": "#7c2d12", "opacity": 0.9},
    "truck":           {"shape": "box", "default_h": 3.5, "color": "#1f2937", "opacity": 0.9},
    "ship":            {"shape": "box", "default_h": 6.0, "color": "#334155", "opacity": 0.9},
    # docks (wt_floor_shell `docks` list)
    "truck_dock":      {"shape": "box", "default_h": 0.4, "color": "#fbbf24", "opacity": 0.7},
    "rail_dock":       {"shape": "box", "default_h": 0.4, "color": "#f59e0b", "opacity": 0.7},
    "ship_dock":       {"shape": "box", "default_h": 0.4, "color": "#fcd34d", "opacity": 0.7},
    # returns / reverse logistics
    "returns_received": {"shape": "box", "default_h": 1.0, "color": "#ef4444", "opacity": 0.8},
    "qc_staging":      {"shape": "box", "default_h": 1.0, "color": "#f87171", "opacity": 0.7},
    "reshelving":      {"shape": "box", "default_h": 1.5, "color": "#34d399", "opacity": 0.8},
    "disposal":        {"shape": "box", "default_h": 1.0, "color": "#64748b", "opacity": 0.8},
    # multi-floor
    "elevator_shaft":  {"shape": "cylinder", "default_h": 3.0, "color": "#8b5cf6", "opacity": 0.8},
    "floor_1":         {"shape": "box", "default_h": 0.4, "color": "#9ca3af", "opacity": 0.4},
    "floor_2":         {"shape": "box", "default_h": 0.4, "color": "#9ca3af", "opacity": 0.4},
    "floor_3":         {"shape": "box", "default_h": 0.4, "color": "#9ca3af", "opacity": 0.4},
}


def _hex_to_rgb(hx: str) -> tuple[float, float, float]:
    hx = hx.lstrip("#")
    if len(hx) == 3:
        hx = "".join(c * 2 for c in hx)
    r = int(hx[0:2], 16) / 255.0
    g = int(hx[2:4], 16) / 255.0
    b = int(hx[4:6], 16) / 255.0
    return (r, g, b)


def _geo_size(shape: str, w: float, d: float, h: float):
    """Return (size_str, half_y) for a mujoco geom."""
    if shape == "cylinder":
        radius = max(w, d) / 2.0
        half = h / 2.0
        return f"{radius:.3f} {half:.3f}", half
    # box: half extents
    hx_ = w / 2.0
    hz_ = d / 2.0
    hy_ = h / 2.0
    return f"{hx_:.3f} {hy_:.3f} {hz_:.3f}", hy_


def _normalize(el: dict) -> dict:
    out = dict(el)
    out["type"] = out.get("type") or "staging"
    out["h"] = out.get("h")
    if out["h"] is None:
        out["h"] = ZONE_BODY_TEMPLATES.get(out["type"], ZONE_BODY_TEMPLATES["staging"])["default_h"]
    out["y"] = float(out.get("y", 0) or 0)
    out["rot"] = float(out.get("rot", 0) or 0)
    out["color"] = out.get("color") or ZONE_BODY_TEMPLATES.get(out["type"], ZONE_BODY_TEMPLATES["staging"])["color"]
    out["opacity"] = out.get("opacity") or ZONE_BODY_TEMPLATES.get(out["type"], ZONE_BODY_TEMPLATES["staging"])["opacity"]
    out["shape"] = ZONE_BODY_TEMPLATES.get(out["type"], ZONE_BODY_TEMPLATES["staging"])["shape"]
    return out


def _iter_elements(geo: dict) -> Iterator[dict]:
    for z in geo.get("zones", []) or []:
        yield z
    for d in geo.get("docks", []) or []:
        yield d


def _ensure_material(mj_root, name: str, color: str, opacity: float, seen: set[str]) -> None:
    """Append a <material> under the first <asset> child of mj_root (create one if needed)."""
    assets = mj_root.getElementsByTagName("asset")
    asset = assets[0] if assets else mj_root.appendChild(
        xml.dom.minidom.Document().createElement("asset")
    )
    if name in seen:
        return
    seen.add(name)
    mat = xml.dom.minidom.Document().createElement("material")
    mat.setAttribute("name", name)
    mat.setAttribute("rgba", f"{color[0]:.3f} {color[1]:.3f} {color[2]:.3f} {opacity:.2f}")
    asset.appendChild(mat)


def _add_body(parent, el: dict) -> None:
    el = _normalize(el)
    eid = el.get("id") or el.get("ref") or el["type"]
    cx = float(el.get("x", 0)) + float(el.get("w", 0)) / 2.0
    cz = float(el.get("z", 0)) + float(el.get("d", 0)) / 2.0
    cy = el["y"] + el["h"] / 2.0

    body = xml.dom.minidom.Document().createElement("body")
    body.setAttribute("name", str(eid))
    body.setAttribute("pos", f"{cx:.3f} {cy:.3f} {cz:.3f}")
    if el["rot"]:
        body.setAttribute("euler", f"0 {el['rot']:.3f} 0")

    mat_name = f"mat_{el['color'].lstrip('#')}"
    rgb = _hex_to_rgb(el["color"])
    _ensure_material(parent.parentNode, mat_name, rgb, el["opacity"], _seen(parent))

    geom = xml.dom.minidom.Document().createElement("geom")
    geom.setAttribute("type", el["shape"])
    size_str, _ = _geo_size(el["shape"], float(el.get("w", 1)), float(el.get("d", 1)), float(el["h"]))
    geom.setAttribute("size", size_str)
    geom.setAttribute("material", mat_name)
    geom.setAttribute("pos", "0 0 0")
    body.appendChild(geom)
    parent.appendChild(body)


def _seen(parent) -> set[str]:
    # share a seen-set via the worldbody via document user data
    doc = parent.ownerDocument if hasattr(parent, "ownerDocument") else parent
    if not hasattr(doc, "_wt_seen"):
        doc._wt_seen = set()
    return doc._wt_seen


def _build_floor(root, bw: float, bd: float):
    floor = xml.dom.minidom.Document().createElement("body")
    floor.setAttribute("name", "floor")
    floor.setAttribute("pos", "0 0 0")
    geom = xml.dom.minidom.Document().createElement("geom")
    geom.setAttribute("type", "plane")
    geom.setAttribute("size", f"{bw:.3f} {bd:.3f} 0.1")
    geom.setAttribute("material", "mat_floor")
    floor.appendChild(geom)
    root.appendChild(floor)


def build_mjcf(map_or_geo: dict | str) -> str:
    """Build an MJCF XML string for a unified map (dict from service, or raw geo)."""
    if isinstance(map_or_geo, str):
        geo = json.loads(map_or_geo)
    else:
        # A raw wt_floor_shell dict carries "zones"/"docks"/"bounds" at the top
        # level; a map dict from the service carries it under "geometry_json"
        # (or legacy "geometry"). Detect which shape we got.
        if "zones" in map_or_geo or "docks" in map_or_geo or "bounds" in map_or_geo:
            geo = map_or_geo
        else:
            geo = map_or_geo.get("geometry") or map_or_geo.get("geometry_json")
            if isinstance(geo, str):
                geo = json.loads(geo)
    geo = geo or {}
    bounds = geo.get("bounds", {}) or {}
    bw = float(bounds.get("w", 100))
    bd = float(bounds.get("d", 100))

    impl = xml.dom.minidom.getDOMImplementation()
    doc = impl.createDocument(None, "mujoco", None)
    mj = doc.documentElement
    mj.setAttribute("model", "scene_map")

    # floor material (shared)
    asset = doc.createElement("asset")
    floor_mat = doc.createElement("material")
    floor_mat.setAttribute("name", "mat_floor")
    floor_mat.setAttribute("rgba", "0.85 0.85 0.85 1")
    asset.appendChild(floor_mat)
    mj.appendChild(asset)

    world = doc.createElement("worldbody")
    mj.appendChild(world)
    _build_floor(world, bw, bd)

    for el in _iter_elements(geo):
        _add_body(world, el)

    return doc.toprettyxml(indent="  ")


def _convert_one_zone(z: dict, y0: float = 0.0) -> dict:
    zt = z.get("type") or "staging"
    base = {
        "ref": z.get("id") or z.get("ref") or zt,
        "type": zt,
        "x": float(z.get("x", 0)),
        "z": float(z.get("z", 0)),
        "w": float(z.get("w", 1)),
        "d": float(z.get("d", 1)),
        "h": None,
        "y": y0,
        "rot": float(z.get("rot", 0) or 0),
        "color": z.get("color"),
        "label": z.get("label") or zt,
    }
    if zt == "loading_bay":  # route to docks, not zones
        base["type"] = "truck_dock"
    return base


def _floor_shell_to_wt(shell: dict, semantic: dict | None = None) -> dict:
    """Legacy FloorShell dict (bounds/zones/floors) -> wt_floor_shell dict."""
    out: dict[str, Any] = {"bounds": {"w": shell["bounds"].get("w", 0), "d": shell["bounds"].get("d", 0)}}
    if "h" in shell["bounds"]:
        out["bounds"]["h"] = shell["bounds"]["h"]
    out["walls"] = shell.get("walls", []) or []
    out["docks"] = []
    out["facilities"] = shell.get("facilities", []) or []
    out["zones"] = []
    out["corridors"] = shell.get("corridors", []) or []

    floors = shell.get("floors") or []
    if floors:
        for fi, fz in enumerate(floors):
            y0 = fi * 4.0
            for z in fz.get("zones", []) or []:
                out["zones"].append(_convert_one_zone(z, y0))
    else:
        for z in shell.get("zones", []) or []:
            out["zones"].append(_convert_one_zone(z))

    # docks holds only月台类; split out from zones (loading_bay -> truck_dock)
    kept = []
    for z in out["zones"]:
        if z["type"] in ("truck_dock", "rail_dock", "ship_dock"):
            out["docks"].append(z)
        else:
            kept.append(z)
    out["zones"] = kept

    if semantic:
        out["semantic"] = semantic
    return out
