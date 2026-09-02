"""Unit tests for the wt_floor_shell -> MJCF converter (no DB needed)."""
import xml.dom.minidom

from rcs.services.control.map_mjcf import build_mjcf, _floor_shell_to_wt

WT = {
    "bounds": {"w": 100, "d": 60},
    "walls": [],
    "docks": [
        {"ref": "dk", "type": "truck_dock", "x": 1, "z": 1, "w": 4, "d": 4,
         "h": 0.4, "y": 0.3, "rot": 0, "color": "#fbbf24", "label": "dock"},
    ],
    "facilities": [],
    "zones": [
        {"ref": "r", "type": "high_rack", "x": 10, "z": 10, "w": 20, "d": 10,
         "h": 4, "y": 0, "rot": 0, "color": None, "label": "rack"},
        {"ref": "s", "type": "staging", "x": 40, "z": 10, "w": 20, "d": 10,
         "h": None, "y": 0, "rot": 0, "color": None, "label": "stg"},
    ],
    "corridors": [],
}


def test_build_mjcf_valid_and_contains_bodies():
    xml_str = build_mjcf(WT)
    doc = xml.dom.minidom.parseString(xml_str)
    assert doc.getElementsByTagName("mujoco")
    assert doc.getElementsByTagName("worldbody")
    assert doc.getElementsByTagName("asset")

    # floor plane present
    planes = [g for g in doc.getElementsByTagName("geom") if g.getAttribute("type") == "plane"]
    assert planes

    # 1 floor + 2 zones + 1 dock = 4 bodies
    bodies = doc.getElementsByTagName("body")
    assert len(bodies) == 4

    # materials live under <asset>, never directly under <mujoco>
    mj = doc.documentElement
    direct_materials = [c for c in mj.childNodes
                        if getattr(c, "tagName", "") == "material"]
    assert direct_materials == []

    # every material reference resolves to a declared material
    mats = {m.getAttribute("name") for m in doc.getElementsByTagName("material")}
    for g in doc.getElementsByTagName("geom"):
        ref = g.getAttribute("material")
        if ref:
            assert ref in mats


def test_build_mjcf_accepts_map_dict_with_geometry_key():
    xml_str = build_mjcf({"geometry": WT})
    doc = xml.dom.minidom.parseString(xml_str)
    assert doc.getElementsByTagName("worldbody")


def test_build_mjcf_normalizes_missing_height():
    xml_str = build_mjcf(WT)
    doc = xml.dom.minidom.parseString(xml_str)
    named = {b.getAttribute("name"): b for b in doc.getElementsByTagName("body")}
    # staging 's' has h=None -> registry default 0.6 -> half 0.3
    s_geom = named["s"].getElementsByTagName("geom")[0]
    assert s_geom.getAttribute("size")  # non-empty half-extents


def test_floor_shell_to_wt_routes_loading_bay_to_docks():
    fs = {
        "bounds": {"w": 80, "d": 60},
        "zones": [
            {"id": "lb", "ref": "LB", "type": "loading_bay", "x": 0, "z": 30, "w": 40, "d": 20},
            {"id": "st", "ref": "ST", "type": "staging", "x": 0, "z": 50, "w": 80, "d": 10},
        ],
        "floors": [],
    }
    wt = _floor_shell_to_wt(fs, {"scenario": "x"})
    dock_types = {d["type"] for d in wt["docks"]}
    zone_types = {z["type"] for z in wt["zones"]}
    assert "truck_dock" in dock_types
    assert "loading_bay" not in zone_types
    assert "staging" in zone_types
    assert wt["semantic"]["scenario"] == "x"


def test_floor_shell_to_wt_multi_floor_y_offset():
    fs = {
        "bounds": {"w": 80, "d": 60, "h": 12},
        "zones": [],
        "floors": [
            {"z": 0.0, "zones": [{"id": "a", "ref": "A", "type": "staging", "x": 0, "z": 0, "w": 10, "d": 10}]},
            {"z": 4.0, "zones": [{"id": "b", "ref": "B", "type": "staging", "x": 0, "z": 0, "w": 10, "d": 10}]},
        ],
    }
    wt = _floor_shell_to_wt(fs)
    ys = [z["y"] for z in wt["zones"]]
    assert ys == [0.0, 4.0]
    assert wt["bounds"]["h"] == 12
