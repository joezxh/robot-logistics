"""Integration tests for topology REST endpoints."""
import pytest
from fastapi.testclient import TestClient
from rcs_backend.main import create_app
from rcs_backend.models.floor_shell import FloorShell, Bounds


@pytest.fixture
def client():
    return TestClient(create_app())


def test_shell_get_missing_returns_404(client):
    r = client.get("/api/rcs/topology/shell/nope-t11")
    assert r.status_code == 404


def test_shell_put_then_get(client):
    shell = FloorShell(bounds=Bounds(w=20, d=10), zones=[])
    r = client.put("/api/rcs/topology/shell/site-A-t11", json=shell.model_dump())
    assert r.status_code == 200
    assert r.json()["ok"] is True

    r2 = client.get("/api/rcs/topology/shell/site-A-t11")
    assert r2.status_code == 200
    assert r2.json()["bounds"]["w"] == 20


def test_shell_put_oversized_returns_422(client):
    shell = FloorShell(bounds=Bounds(w=1000, d=80))
    r = client.put("/api/rcs/topology/shell/site-B-t11", json=shell.model_dump())
    assert r.status_code == 422


def test_shell_list_after_puts(client):
    for sid in ["x-t11", "y-t11", "z-t11"]:
        client.put(
            f"/api/rcs/topology/shell/{sid}",
            json=FloorShell(bounds=Bounds(w=10, d=10)).model_dump(),
        )
    r = client.get("/api/rcs/topology/shell")
    assert r.status_code == 200
    site_ids = {item["site_id"] for item in r.json()}
    assert {"x-t11", "y-t11", "z-t11"}.issubset(site_ids)
