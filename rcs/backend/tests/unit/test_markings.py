"""Auto-generate floor markings from FloorShell."""
from rcs.models.topology_markings import generate_markings
from rcs.models.floor_shell import (
    FloorShell, Bounds, WallSegment, Corridor, Zone, Marking, Dock,
)


def test_corridor_generates_lane_marking():
    shell = FloorShell(
        bounds=Bounds(w=50, d=30),
        zones=[
            Zone(id="z1", ref="A", type="staging", x=0, z=0, w=10, d=10),
            Zone(id="z2", ref="B", type="staging", x=20, z=0, w=10, d=10),
        ],
        corridors=[Corridor(id="c1", from_zone="z1", to_zone="z2", w=3.0, bidirectional=False)],
    )
    markings = generate_markings(shell)
    lanes = [m for m in markings if m.kind == "lane"]
    assert len(lanes) == 1
    assert lanes[0].points


def test_dock_zones_get_stop_markings():
    shell = FloorShell(
        bounds=Bounds(w=50, d=30),
        docks=[Dock(id="d1", ref="D1", x=10, z=10)],
    )
    markings = generate_markings(shell)
    stops = [m for m in markings if m.kind == "stop"]
    assert len(stops) == 1


def test_no_zones_no_corridors_no_docks_empty():
    shell = FloorShell(bounds=Bounds(w=10, d=10))
    assert generate_markings(shell) == []


def test_markings_have_color():
    shell = FloorShell(
        bounds=Bounds(w=50, d=30),
        corridors=[Corridor(id="c1", from_zone="z1", to_zone="z2")],
        zones=[
            Zone(id="z1", ref="A", type="staging", x=0, z=0, w=5, d=5),
            Zone(id="z2", ref="B", type="staging", x=10, z=0, w=5, d=5),
        ],
    )
    markings = generate_markings(shell)
    for m in markings:
        assert isinstance(m, Marking)
        assert m.color.startswith("#")


def test_lane_marks_both_directions_when_bidirectional():
    shell = FloorShell(
        bounds=Bounds(w=50, d=30),
        zones=[
            Zone(id="z1", ref="A", type="staging", x=0, z=0, w=5, d=5),
            Zone(id="z2", ref="B", type="staging", x=10, z=0, w=5, d=5),
        ],
        corridors=[Corridor(id="c1", from_zone="z1", to_zone="z2", bidirectional=True)],
    )
    markings = generate_markings(shell)
    # bidirectional corridor (default) generates 2 lane markings (forward + reverse)
    lanes = [m for m in markings if m.kind == "lane"]
    assert len(lanes) == 2
