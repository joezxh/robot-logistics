"""Convert DXF document into FloorShell."""
from rcs.services.topology.dxf_parser import DxfDocument, DxfEntity
from rcs.services.topology.dxf_to_shell import dxf_to_shell
from rcs.models.floor_shell import WallSegment, Zone, Facility


def _doc(entities: list[DxfEntity]) -> DxfDocument:
    return DxfDocument(entities=entities, header_units="m")


def test_walls_layer_becomes_wall_segments():
    doc = _doc([
        DxfEntity(type="LINE", layer="WALLS", vertices=[[0, 0], [10, 0]]),
        DxfEntity(type="LINE", layer="WALLS", vertices=[[10, 0], [10, 8]]),
    ])
    shell = dxf_to_shell(doc)
    assert len(shell.walls) == 2
    assert all(isinstance(w, WallSegment) for w in shell.walls)
    assert shell.walls[0].kind == "wall"


def test_zones_layer_becomes_zones_with_ref():
    # Zone spans [0,0]-[10,5] → center (5, 2.5). Place TEXT at zone center
    # so the lookup heuristic (exact / round-1-decimal) finds it.
    doc = _doc([
        DxfEntity(type="LWPOLYLINE", layer="ZONES", vertices=[[0, 0], [10, 0], [10, 5], [0, 5]]),
        DxfEntity(type="TEXT", layer="TEXT", vertices=[[5, 2.5]], text="A1"),
    ])
    shell = dxf_to_shell(doc)
    assert len(shell.zones) == 1
    zone = shell.zones[0]
    assert zone.ref == "A1"
    assert zone.type == "staging"
    assert zone.w > 0 and zone.d > 0


def test_facilities_layer_becomes_facilities():
    doc = _doc([
        DxfEntity(type="CIRCLE", layer="FACILITIES", vertices=[[5, 5]], radius=2.0),
    ])
    shell = dxf_to_shell(doc)
    assert len(shell.facilities) == 1
    assert isinstance(shell.facilities[0], Facility)


def test_floor_layer_sets_bounds():
    doc = _doc([
        DxfEntity(type="LWPOLYLINE", layer="FLOOR", vertices=[[0, 0], [100, 0], [100, 80], [0, 80]]),
    ])
    shell = dxf_to_shell(doc)
    assert shell.bounds.w == pytest.approx(100.0)
    assert shell.bounds.d == pytest.approx(80.0)


def test_empty_doc_yields_empty_shell():
    shell = dxf_to_shell(_doc([]))
    assert shell.walls == []
    assert shell.zones == []
    assert shell.facilities == []


import pytest  # noqa: E402