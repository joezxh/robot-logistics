"""Integration tests for warehouse_theatre_3d import REST endpoints."""
import pytest
from fastapi.testclient import TestClient
from rcs.main import create_app


@pytest.fixture
def client():
    with TestClient(create_app()) as c:
        yield c


class TestPreviewEndpoint:
    """GET /api/rcs/import/warehouse-theatre/preview — no DB writes."""

    def test_preview_returns_200(self, client):
        r = client.get("/api/rcs/import/warehouse-theatre/preview")
        assert r.status_code == 200

    def test_preview_has_shell(self, client):
        body = r = client.get("/api/rcs/import/warehouse-theatre/preview").json()
        assert "shell" in body
        assert body["shell"]["bounds"]["w"] == 160
        assert body["shell"]["bounds"]["d"] == 100

    def test_preview_has_nodes_and_edges(self, client):
        body = client.get("/api/rcs/import/warehouse-theatre/preview").json()
        assert len(body["nodes"]) > 0
        assert len(body["edges"]) > 0

    def test_preview_summary(self, client):
        body = client.get("/api/rcs/import/warehouse-theatre/preview").json()
        s = body["summary"]
        assert s["zone_count"] == 8
        assert s["dock_count"] == 4
        assert s["facility_count"] == 12
        assert s["node_count"] == len(body["nodes"])
        assert s["edge_count"] == len(body["edges"])


class TestImportEndpoint:
    """POST /api/rcs/import/warehouse-theatre — persists to DB."""

    def test_import_returns_ok(self, client):
        r = client.post("/api/rcs/import/warehouse-theatre")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert body["site_id"] == "warehouse-theatre-3d"
        assert body["zone_count"] == 8
        assert body["node_count"] > 0
        assert body["edge_count"] > 0

    def test_import_creates_shell(self, client):
        client.post("/api/rcs/import/warehouse-theatre")
        r = client.get("/api/rcs/maps/warehouse-theatre-3d")
        assert r.status_code == 200
        geometry = r.json()["geometry"]
        assert geometry["bounds"]["w"] == 160
        assert len(geometry.get("zones", [])) == 8

    def test_import_creates_site_map(self, client):
        result = client.post("/api/rcs/import/warehouse-theatre").json()
        map_id = result["map_id"]
        r = client.get(f"/api/rcs/maps/{map_id}")
        assert r.status_code == 200
        map_data = r.json()
        assert len(map_data["topology"]["nodes"]) > 0
        assert len(map_data["topology"]["edges"]) > 0

    def test_import_idempotent(self, client):
        r1 = client.post("/api/rcs/import/warehouse-theatre").json()
        r2 = client.post("/api/rcs/import/warehouse-theatre").json()
        # Same site_id, incremented version
        assert r1["site_id"] == r2["site_id"]
        assert r2["map_version"] == r1["map_version"] + 1

    def test_import_persists_zones_in_unified_map(self, client):
        """Zone data is persisted inside the UnifiedMap geometry (no separate
        TopologyGrid table anymore)."""
        client.post("/api/rcs/import/warehouse-theatre")
        r = client.get("/api/rcs/maps/warehouse-theatre-3d")
        assert r.status_code == 200
        zones = r.json().get("geometry", {}).get("zones", [])
        assert len(zones) == 8
