"""Integration tests for the warehouse inventory domain (WMS layer) REST endpoints."""
import pytest
from fastapi.testclient import TestClient

from rcs.main import create_app


@pytest.fixture
def client():
    with TestClient(create_app()) as c:
        yield c


class TestInventorySeedAndRead:
    """Seed demo inventory, then read it back through the read endpoints."""

    def test_seed_returns_counts(self, client):
        r = client.post("/api/rcs/warehouse/inventory/seed")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert body["slots"] > 0
        assert body["items"] > 0
        assert body["agvs"] == 4
        assert body["tasks"] == 12

    def test_groups_after_seed(self, client):
        client.post("/api/rcs/warehouse/inventory/seed")
        r = client.get("/api/rcs/warehouse/inventory/groups")
        assert r.status_code == 200
        groups = r.json()["groups"]
        assert len(groups) >= 1
        assert all("slot_count" in g for g in groups)

    def test_slots_contract(self, client):
        client.post("/api/rcs/warehouse/inventory/seed")
        r = client.get("/api/rcs/warehouse/inventory/slots")
        assert r.status_code == 200
        slots = r.json()["slots"]
        assert len(slots) > 0
        sl = slots[0]
        # Frontend Slot contract fields
        assert {"wh", "label", "row", "col", "row_gap", "levels"} <= set(sl.keys())
        assert len(sl["levels"]) == 3

    def test_tasks_contract(self, client):
        client.post("/api/rcs/warehouse/inventory/seed")
        r = client.get("/api/rcs/warehouse/inventory/tasks")
        assert r.status_code == 200
        tasks = r.json()["tasks"]
        assert len(tasks) == 12
        t = tasks[0]
        assert {"ref", "type", "status", "priority", "items"} <= set(t.keys())

    def test_agv_contract(self, client):
        client.post("/api/rcs/warehouse/inventory/seed")
        r = client.get("/api/rcs/warehouse/inventory/agv")
        assert r.status_code == 200
        agvs = r.json()["agvs"]
        assert len(agvs) == 4
        assert {"ref", "x", "z", "yaw", "battery", "status"} <= set(agvs[0].keys())

    def test_stats(self, client):
        client.post("/api/rcs/warehouse/inventory/seed")
        r = client.get("/api/rcs/warehouse/inventory/stats")
        assert r.status_code == 200
        stats = r.json()["stats"]
        assert "total_inbound" in stats
        assert "total_outbound" in stats

    def test_seed_is_idempotent(self, client):
        r1 = client.post("/api/rcs/warehouse/inventory/seed").json()
        r2 = client.post("/api/rcs/warehouse/inventory/seed").json()
        # Re-seeding must not duplicate rows for the same site.
        assert r1["slots"] == r2["slots"]
        assert r1["items"] == r2["items"]
        assert r1["tasks"] == r2["tasks"]
