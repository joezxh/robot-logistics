"""Pydantic models for site grid (resolution-N raster of CellType)."""
import pytest
from rcs.models.site_grid import SiteGrid, Cell, CellType


def test_cell_type_enum_all_members():
    """All 10 v2.2 cell types must exist (spec §13.3.3)."""
    assert CellType.EMPTY == "empty"
    assert CellType.BLOCKED == "blocked"
    assert CellType.AGV_LANE == "agv_lane"
    assert CellType.AGV_NODE == "agv_node"
    assert CellType.ROBOT_LANE == "robot_lane"
    assert CellType.ROBOT_NODE == "robot_node"
    assert CellType.CHARGER == "charger"
    assert CellType.DOCK == "dock"
    assert CellType.SHELF == "shelf"
    assert CellType.WORK_ZONE == "work_zone"


def test_cell_default_empty():
    c = Cell(x=0, z=0)
    assert c.type == CellType.EMPTY
    assert c.height == 0.0
    assert c.metadata == {}


def test_site_grid_minimal_default_resolution():
    grid = SiteGrid(site_id="site-A", bounds={"w": 10.0, "d": 8.0})
    assert grid.resolution == 0.5
    # 10 / 0.5 = 20 cells x, 8 / 0.5 = 16 cells z
    assert len(grid.cells) == 16
    assert len(grid.cells[0]) == 20


def test_site_grid_custom_resolution():
    grid = SiteGrid(site_id="site-A", bounds={"w": 10.0, "d": 10.0}, resolution=1.0)
    assert len(grid.cells) == 10
    assert len(grid.cells[0]) == 10


def test_site_grid_2d_indexing():
    """cells[z][x] returns the cell at (x, z)."""
    grid = SiteGrid(site_id="site-A", bounds={"w": 2.0, "d": 2.0}, resolution=1.0)
    grid.cells[0][0].type = CellType.AGV_LANE
    assert grid.cells[0][0].type == CellType.AGV_LANE
    # bounds-check
    with pytest.raises(IndexError):
        _ = grid.cells[10][10]


def test_site_grid_serializes_to_dict():
    grid = SiteGrid(site_id="site-A", bounds={"w": 4.0, "d": 4.0}, resolution=1.0)
    d = grid.model_dump()
    assert d["site_id"] == "site-A"
    assert d["resolution"] == 1.0
    assert d["bounds"]["w"] == 4.0
    assert len(d["cells"]) == 4
