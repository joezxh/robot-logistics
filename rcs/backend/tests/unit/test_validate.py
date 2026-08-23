"""FloorShell validation — bounds/overlap/zone-types."""
from rcs_backend.topology.validate import validate_shell, ValidationError, ValidationReport
from rcs_backend.models.floor_shell import FloorShell, Bounds, WallSegment, Zone, ZONE_TYPES


def _shell(**kw) -> FloorShell:
    defaults = {"bounds": Bounds(w=100, d=80)}
    defaults.update(kw)
    return FloorShell(**defaults)


def test_valid_shell_passes():
    s = _shell(walls=[WallSegment(id="w1", x0=0, z0=0, x1=10, z1=0)])
    r = validate_shell(s)
    assert r.ok is True
    assert r.errors == []


def test_oversized_bounds_fails():
    s = _shell(bounds=Bounds(w=1000, d=80))
    r = validate_shell(s, max_bounds_m=500.0)
    assert r.ok is False
    assert any("bounds" in e for e in r.errors)


def test_zero_width_zone_fails():
    # Plan patch: Zone model rejects w=0 at construction (Field(gt=0)).
    # Use model_construct to deliberately create a malformed zone so we can
    # exercise validate_shell's catch for it. validate_shell's contract is
    # "defense in depth" — it should report the zero width itself rather
    # than relying on the model to have already rejected it.
    bad = Zone.model_construct(id="z1", ref="A", type="staging", x=0, z=0, w=0, d=5)
    s = _shell(zones=[bad])
    r = validate_shell(s)
    assert r.ok is False
    assert any("width" in e for e in r.errors)


def test_unknown_zone_type_warns():
    s = _shell(zones=[Zone(id="z1", ref="A", type="bogus_type", x=0, z=0, w=5, d=5)])
    r = validate_shell(s)
    assert any("bogus_type" in w for w in r.warnings)


def test_zone_outside_bounds_fails():
    s = _shell(
        bounds=Bounds(w=50, d=50),
        zones=[Zone(id="z1", ref="A", type="staging", x=45, z=0, w=10, d=5)],
    )
    r = validate_shell(s)
    assert r.ok is False
    assert any("outside" in e for e in r.errors)


def test_duplicate_wall_ids_fail():
    s = _shell(walls=[
        WallSegment(id="w1", x0=0, z0=0, x1=5, z1=0),
        WallSegment(id="w1", x0=5, z0=0, x1=10, z1=0),
    ])
    r = validate_shell(s)
    assert any("duplicate" in e.lower() for e in r.errors)
