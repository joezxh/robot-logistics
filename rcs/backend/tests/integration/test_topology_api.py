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


# --- Task 12: topology_grid ---
from rcs_backend.models.site_grid import SiteGrid, Cell, CellType


def test_grid_put_then_get(client):
    grid = SiteGrid(
        site_id="site-A-t12",
        bounds={"w": 4.0, "d": 4.0},
        resolution=2.0,
    )
    # Auto-populated 2 cells x 2 cells = 4 cells.
    grid.cells[0][0].type = CellType.BLOCKED
    grid.cells[0][1].type = CellType.AGV_LANE
    r = client.put("/api/rcs/topology/grid/site-A-t12", json=grid.model_dump())
    assert r.status_code == 200

    r2 = client.get("/api/rcs/topology/grid/site-A-t12")
    assert r2.status_code == 200
    body = r2.json()
    assert body["bounds"]["w"] == 4.0
    assert len(body["cells"]) == 2
    assert len(body["cells"][0]) == 2


def test_grid_get_missing_404(client):
    r = client.get("/api/rcs/topology/grid/nope-t12")
    assert r.status_code == 404


def test_grid_capacity_validation(client):
    # bounds 2x2 at resolution 2.0 → capacity = 1
    grid = SiteGrid(
        site_id="site-B-t12",
        bounds={"w": 2.0, "d": 2.0},
        resolution=2.0,
    )
    # Force 4 cells into 2D into a 1-cell capacity; auto-populate makes 2 cells.
    # Here we mutate: 2x2 = 4 entries > capacity 1 → 422.
    grid.cells.append([Cell(x=0, z=2), Cell(x=0, z=3)])  # add rows beyond bounds
    r = client.put("/api/rcs/topology/grid/site-B-t12", json=grid.model_dump())
    assert r.status_code == 422
