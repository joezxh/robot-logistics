"""Unit tests for warehouse_theatre_3d → RCS data converter."""
import pytest
from rcs.services.warehouse_converter import (
    convert_to_floor_shell,
    convert_to_site_map,
    BLUEPRINT,
    _shift_point,
    _center_to_corner,
)


class TestCoordinateTransform:
    """Verify the center-origin → bottom-left coordinate mapping."""

    def test_shift_origin(self):
        assert _shift_point(0, 0) == (80.0, 50.0)

    def test_shift_negative_corner(self):
        assert _shift_point(-80, -50) == (0.0, 0.0)

    def test_shift_positive_corner(self):
        assert _shift_point(80, 50) == (160.0, 100.0)

    def test_center_to_corner_zone_a(self):
        # ZONE-A: center=(-40, -6), w=36, d=24
        cx, cz = _center_to_corner(-40, -6, 36, 24)
        assert cx == pytest.approx(22.0)   # -40 - 18 + 80
        assert cz == pytest.approx(32.0)   # -6  - 12 + 50


class TestFloorShellConversion:
    """Validate the FloorShell dict structure and content."""

    @pytest.fixture
    def shell(self):
        return convert_to_floor_shell()

    def test_bounds(self, shell):
        assert shell["bounds"]["w"] == 160
        assert shell["bounds"]["d"] == 100

    def test_zone_count(self, shell):
        assert len(shell["zones"]) == len(BLUEPRINT["zones"])

    def test_zone_coords_positive(self, shell):
        """All zone corners must be in [0, W] × [0, D]."""
        for z in shell["zones"]:
            assert z["x"] >= 0, f"{z['ref']} x < 0"
            assert z["z"] >= 0, f"{z['ref']} z < 0"
            assert z["x"] + z["w"] <= 160, f"{z['ref']} exceeds width"
            assert z["z"] + z["d"] <= 100, f"{z['ref']} exceeds depth"

    def test_zone_types_preserved(self, shell):
        types = {z["type"] for z in shell["zones"]}
        assert "flow_rack" in types
        assert "high_rack" in types
        assert "automated" in types

    def test_wall_count(self, shell):
        assert len(shell["walls"]) == len(BLUEPRINT["walls"])

    def test_facility_count(self, shell):
        assert len(shell["facilities"]) == len(BLUEPRINT["facilities"])

    def test_dock_count(self, shell):
        assert len(shell["docks"]) == len(BLUEPRINT["docks"])

    def test_docks_all_face_south(self, shell):
        for d in shell["docks"]:
            assert d["direction"] == "S"

    def test_metadata_source(self, shell):
        assert shell["metadata"]["source"] == "warehouse_theatre_3d"


class TestSiteMapConversion:
    """Validate the node/edge graph generation."""

    @pytest.fixture
    def graph(self):
        nodes, edges = convert_to_site_map()
        return {"nodes": nodes, "edges": edges}

    def test_node_count_positive(self, graph):
        assert len(graph["nodes"]) > 0

    def test_edge_count_positive(self, graph):
        assert len(graph["edges"]) > 0

    def test_zone_nodes_present(self, graph):
        zone_ids = {n["id"] for n in graph["nodes"] if n["type"] == "zone"}
        expected = {z["ref"] for z in BLUEPRINT["zones"]}
        assert expected == zone_ids

    def test_dock_nodes_present(self, graph):
        dock_ids = {n["id"] for n in graph["nodes"] if n["type"] == "dock"}
        expected = {d["ref"] for d in BLUEPRINT["docks"]}
        assert expected == dock_ids

    def test_facility_nodes_present(self, graph):
        fac_ids = {n["id"] for n in graph["nodes"] if n["type"] == "facility"}
        expected = {f["ref"] for f in BLUEPRINT["facilities"]}
        assert expected == fac_ids

    def test_corridor_nodes_present(self, graph):
        corr = [n for n in graph["nodes"] if n["type"] == "corridor_waypoint"]
        assert len(corr) >= 2 * len(BLUEPRINT["corridors"])  # at least 2 per corridor

    def test_all_edges_reference_valid_nodes(self, graph):
        node_ids = {n["id"] for n in graph["nodes"]}
        for e in graph["edges"]:
            assert e["from"] in node_ids, f"edge from unknown node {e['from']}"
            assert e["to"] in node_ids, f"edge to unknown node {e['to']}"

    def test_no_self_loops(self, graph):
        for e in graph["edges"]:
            assert e["from"] != e["to"], f"self-loop on {e['from']}"

    def test_all_non_corridor_nodes_connected(self, graph):
        """Every zone / dock / facility must have at least one edge."""
        connected = set()
        for e in graph["edges"]:
            connected.add(e["from"])
            connected.add(e["to"])
        for n in graph["nodes"]:
            if n["type"] != "corridor_waypoint":
                assert n["id"] in connected, f"{n['id']} ({n['type']}) has no edges"

    def test_edge_distances_positive(self, graph):
        for e in graph["edges"]:
            assert e["distance"] > 0, f"edge {e['from']}→{e['to']} has zero distance"
