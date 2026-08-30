"""Unit tests for the built-in warehouse site-map templates.

These run without a database — the templates are pure Python data, so the
graph invariants are checked directly.
"""
from __future__ import annotations

import math

import pytest

from rcs.models.site_map_templates import (
    TEMPLATE_KEYS,
    get_template,
    list_templates,
    template_map_id,
    template_summary,
)

# The eight warehouse types the product asked to ship with. The second
# e-commerce entry is the warehouse_theatre_3d reference layout.
EXPECTED = {
    "ecommerce_large": "大型电商仓",
    "theatre_ecommerce": "大型电商仓（warehouse_theatre_3d）",
    "port_terminal": "港口集装箱码头",
    "factory_warehouse": "工厂仓库",
    "highway_freight_hub": "货运公路港",
    "third_party_logistics": "第三方物流仓库",
    "cold_chain": "冷链仓",
    "reverse_logistics": "逆向退货仓",
}

# Categories a consumer can filter on.
CATEGORIES = {
    "ecommerce_large": "ecommerce",
    "theatre_ecommerce": "ecommerce",
    "port_terminal": "port",
    "factory_warehouse": "manufacturing",
    "highway_freight_hub": "freight",
    "third_party_logistics": "third_party",
    "cold_chain": "cold_chain",
    "reverse_logistics": "reverse_logistics",
}


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _connected_components(node_ids: set[str], edges: list[dict]) -> list[set[str]]:
    """Independent union-find so the test does not reuse production helpers."""
    parent = {i: i for i in node_ids}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for e in edges:
        ra, rb = find(e["from"]), find(e["to"])
        if ra != rb:
            parent[ra] = rb

    groups: dict[str, set[str]] = {}
    for i in node_ids:
        groups.setdefault(find(i), set()).add(i)
    return list(groups.values())


@pytest.fixture(params=TEMPLATE_KEYS)
def template(request):
    return get_template(request.param)


def test_registry_contains_the_eight_warehouse_types():
    assert set(TEMPLATE_KEYS) == set(EXPECTED)
    assert {t.key: t.name for t in list_templates()} == EXPECTED


def test_every_template_declares_a_category():
    assert {t.key: t.category for t in list_templates()} == CATEGORIES
    assert all(t.description for t in list_templates())


def test_get_template_unknown_key_raises():
    with pytest.raises(KeyError):
        get_template("no_such_template")


def test_map_id_is_deterministic_and_prefixed():
    assert template_map_id("port_terminal") == "tpl-port_terminal"
    assert get_template("port_terminal").map_id == "tpl-port_terminal"


def test_node_ids_are_unique(template):
    ids = [n["id"] for n in template.nodes]
    assert len(ids) == len(set(ids)), f"duplicate node ids in {template.key}"


def test_edges_reference_existing_nodes(template):
    ids = {n["id"] for n in template.nodes}
    for e in template.edges:
        assert e["from"] in ids, f"{template.key}: edge {e} has unknown 'from'"
        assert e["to"] in ids, f"{template.key}: edge {e} has unknown 'to'"


def test_no_self_loops(template):
    for e in template.edges:
        assert e["from"] != e["to"], f"{template.key}: self-loop at {e['from']}"


def test_graph_is_fully_connected(template):
    """Every node must be reachable — isolated corridors are unroutable."""
    ids = {n["id"] for n in template.nodes}
    comps = _connected_components(ids, template.edges)
    assert len(comps) == 1, (
        f"{template.key}: graph split into {len(comps)} components; "
        f"smallest has {min(len(c) for c in comps)} nodes"
    )


def test_node_positions_within_bounds(template):
    w, d = template.bounds["w"], template.bounds["d"]
    for n in template.nodes:
        x, z = n["pos"][0], n["pos"][2]
        assert 0 <= x <= w, f"{template.key}: {n['id']} x={x} outside [0, {w}]"
        assert 0 <= z <= d, f"{template.key}: {n['id']} z={z} outside [0, {d}]"


def test_distance_matches_geometry(template):
    """`distance` must agree with the node coordinates, not be fabricated."""
    pos = {n["id"]: (n["pos"][0], n["pos"][2]) for n in template.nodes}
    for e in template.edges:
        expected = round(_dist(pos[e["from"]], pos[e["to"]]), 2)
        assert e["distance"] == pytest.approx(expected, abs=0.02), (
            f"{template.key}: edge {e['from']}->{e['to']} distance mismatch"
        )


def test_required_fields_per_node_type(template):
    required = {
        "corridor_waypoint": {"corridor_idx"},
        "zone": {"zone_type", "capacity", "w", "d"},
        "dock": {"flow"},
        "facility": {"facility_kind"},
    }
    for n in template.nodes:
        assert "id" in n
        assert "type" in n
        assert len(n["pos"]) == 3
        for field in required.get(n["type"], set()):
            assert field in n, f"{template.key}: {n['id']} missing '{field}'"


def test_edges_carry_routing_attributes(template):
    for e in template.edges:
        assert set(("from", "to", "distance", "bidirectional", "speed_limit")) <= set(e)
        assert e["speed_limit"] > 0
        assert e["distance"] >= 0


def test_each_template_has_zones_docks_and_facilities(template):
    kinds = {n["type"] for n in template.nodes}
    assert {"zone", "dock", "facility", "corridor_waypoint"} <= kinds


def test_get_template_returns_fresh_objects():
    """Mutating one result must not corrupt later calls."""
    a = get_template("factory_warehouse")
    a.nodes.append({"id": "POLLUTED"})
    b = get_template("factory_warehouse")
    assert all(n["id"] != "POLLUTED" for n in b.nodes)


def test_template_summary_is_compact():
    s = template_summary(get_template("ecommerce_large"))
    assert s["key"] == "ecommerce_large"
    assert s["map_id"] == "tpl-ecommerce_large"
    # Summary must not leak the heavy payloads.
    assert "nodes" not in s and "edges" not in s
    assert s["node_count"] > 0 and s["edge_count"] > 0
    assert sum(s["node_types"].values()) == s["node_count"]
    # Geometry counts come from the FloorShell, not the graph.
    assert s["zone_count"] == len(get_template("ecommerce_large").shell.zones)
    assert s["grid_row_count"] == s["zone_count"]


# ── FloorShell geometry (the part that actually renders) ─────────────────────

def test_shell_passes_rcs_validation(template):
    """Every template shell must satisfy the real FloorShell validator."""
    from rcs.services.topology.validate import validate_shell

    report = validate_shell(template.shell)
    assert report.errors == [], f"{template.key}: {report.errors}"


def test_shell_zones_are_inside_bounds(template):
    """FloorShell zones are corner-based and must fit inside bounds."""
    w, d = template.bounds["w"], template.bounds["d"]
    for z in template.shell.zones:
        assert z.x >= -0.01 and z.z >= -0.01, f"{template.key}: {z.id} negative corner"
        assert z.x + z.w <= w + 0.01, f"{template.key}: {z.id} exceeds width"
        assert z.z + z.d <= d + 0.01, f"{template.key}: {z.id} exceeds depth"


def test_shell_has_walls_docks_and_facilities(template):
    assert template.shell.walls, f"{template.key}: no walls"
    assert template.shell.docks, f"{template.key}: no docks"
    assert template.shell.facilities, f"{template.key}: no facilities"
    # Wall ids must be unique (a hard error in the validator).
    ids = [w.id for w in template.shell.walls]
    assert len(ids) == len(set(ids))


def test_shell_markings_are_deterministic(template):
    """Marking ids must be stable — uuid-based ids would churn seeded rows."""
    a = [m.id for m in template.shell.markings]
    b = [m.id for m in get_template(template.key).shell.markings]
    assert a == b
    assert len(a) == len(set(a)), f"{template.key}: duplicate marking ids"


def test_shell_corridors_reference_real_zones(template):
    """Corridors are semantic zone-to-zone links; dangling refs render nothing."""
    zone_ids = {z.id for z in template.shell.zones}
    for c in template.shell.corridors:
        assert c.from_zone in zone_ids, f"{template.key}: {c.id} bad from_zone"
        assert c.to_zone in zone_ids, f"{template.key}: {c.id} bad to_zone"


def test_grid_rows_cover_every_zone(template):
    rows = template.grid_rows()
    assert [r["zone_id"] for r in rows] == [z.id for z in template.shell.zones]
    for r, z in zip(rows, template.shell.zones):
        # centre must match the zone rectangle
        assert r["center_m"] == pytest.approx(
            [z.x + z.w / 2, z.z + z.d / 2], abs=0.01)
        assert r["size_m"] == [z.w, z.d]
        assert r["data"]["type"] == z.type


def test_shell_and_site_map_share_one_id(template):
    """All three tables are keyed by the same deterministic id."""
    assert template.shell is not None
    assert template.map_id == template.site_id == f"tpl-{template.key}"


def test_theatre_template_matches_the_reference_layout():
    """The theatre template must keep the warehouse_theatre_3d proportions."""
    t = get_template("theatre_ecommerce")
    assert t.bounds == {"w": 160, "d": 100}
    refs = {z.ref for z in t.shell.zones}
    assert {"ZONE-A", "ZONE-B", "ZONE-C", "ZONE-D", "ASRS-1"} <= refs
    assert {d.ref for d in t.shell.docks} == {"DOCK-1", "DOCK-2", "DOCK-3", "DOCK-4"}
    # Docks face south in the reference layout.
    assert all(d.direction == "S" for d in t.shell.docks)


def test_templates_are_deterministic():
    """Two builds must serialise identically, or seeding would always write."""
    for key in TEMPLATE_KEYS:
        a = get_template(key).shell.model_dump(mode="json")
        b = get_template(key).shell.model_dump(mode="json")
        assert a == b, f"{key}: shell is not deterministic"


# ── Cold chain specifics ─────────────────────────────────────────────────────

def test_cold_chain_multi_temperature_zones():
    t = get_template("cold_chain")
    by_type = {z.type for z in t.shell.zones}
    assert {"frozen_zone", "cold_zone", "ambient_zone", "loading_bay"} <= by_type


def test_cold_chain_temperature_ranges_are_set():
    """Temperature-controlled zones must carry their band, not just a type."""
    t = get_template("cold_chain")
    frozen = [z for z in t.shell.zones if z.type == "frozen_zone"]
    chilled = [z for z in t.shell.zones if z.type == "cold_zone"]
    assert frozen and chilled
    for z in frozen:
        assert z.temperature_range is not None
        assert z.temperature_range.max <= -18, f"{z.id} not cold enough"
        assert z.batch_tracking, f"{z.id} must track batches"
    for z in chilled:
        assert z.temperature_range is not None
        assert 0 <= z.temperature_range.min and z.temperature_range.max <= 10
        assert z.batch_tracking


def test_cold_chain_has_freeze_and_thaw_equipment():
    t = get_template("cold_chain")
    kinds = {f.type for f in t.shell.facilities}
    assert {"blast_freezer", "defrost", "monitoring"} <= kinds


# ── Reverse logistics specifics ──────────────────────────────────────────────

def test_reverse_logistics_covers_the_full_disposition_flow():
    t = get_template("reverse_logistics")
    by_type = {z.type for z in t.shell.zones}
    assert "returns_received" in by_type, "no returns receiving zone"
    assert "qc_staging" in by_type, "no triage/grading zone"
    # Every return must end up restocked, refurbished or disposed of.
    assert "reshelving" in by_type
    assert "disposal" in by_type


def test_reverse_logistics_mostly_inbound_docks():
    """Returns flow inward, so inbound capacity should dominate."""
    t = get_template("reverse_logistics")
    flows = [n["flow"] for n in t.nodes if n["type"] == "dock"]
    assert flows.count("inbound") > flows.count("outbound")


def test_disposal_zone_flags_hazard():
    t = get_template("reverse_logistics")
    disposal = [z for z in t.shell.zones if z.type == "disposal"]
    assert len(disposal) == 1
    assert disposal[0].hazard_level is not None


# ── Optional attribute pass-through ──────────────────────────────────────────

def test_port_customs_zone_flags_customs_regulated():
    """Regression: the customs flag used to be silently dropped."""
    t = get_template("port_terminal")
    customs = [z for z in t.shell.zones if z.type == "customs_area"]
    assert customs, "no customs zone in the port template"
    assert all(z.customs_regulated for z in customs)
