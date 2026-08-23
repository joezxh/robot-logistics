"""Integration tests for orders API."""
import pytest
from fastapi.testclient import TestClient
from rcs_backend.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_create_order(client):
    r = client.post("/api/rcs/orders", json={
        "scenario_id": "ecommerce",
        "items": [{"ref": "A1", "quantity": 2}],
        "priority": 7,
    })
    assert r.status_code == 202
    body = r.json()
    assert body["order_id"].startswith("ORD-")
    assert len(body["dag"]) == 4


def test_get_order_after_create(client):
    r = client.post("/api/rcs/orders", json={
        "scenario_id": "cold_chain",
        "items": [{"ref": "F1", "quantity": 1}],
    })
    oid = r.json()["order_id"]
    r2 = client.get(f"/api/rcs/orders/{oid}")
    assert r2.status_code == 200
    assert r2.json()["order_id"] == oid


def test_get_missing_order_404(client):
    r = client.get("/api/rcs/orders/ORD-doesnotexist")
    assert r.status_code == 404


def test_order_validation_invalid_quantity(client):
    r = client.post("/api/rcs/orders", json={
        "scenario_id": "ecommerce",
        "items": [{"ref": "A1", "quantity": 0}],
    })
    assert r.status_code == 422
