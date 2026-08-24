"""DXF ASCII parser — ported from wx3D parseDXF (zero external deps)."""
from rcs.topology.dxf_parser import parse_dxf, DxfEntity, DxfDocument


def test_parse_minimal_line_entity():
    dxf = """0
SECTION
2
HEADER
9
$INSUNITS
70
6
0
ENDSEC
0
SECTION
2
ENTITIES
0
LINE
8
WALLS
10
0.0
20
0.0
30
0.0
11
10.0
21
0.0
31
0.0
0
ENDSEC
0
EOF
"""
    doc = parse_dxf(dxf)
    assert isinstance(doc, DxfDocument)
    assert doc.header_units == "m"
    assert len(doc.entities) == 1
    assert doc.entities[0].type == "LINE"
    assert doc.entities[0].layer == "WALLS"
    assert doc.entities[0].vertices == [[0.0, 0.0], [10.0, 0.0]]


def test_parse_lwpolyline_with_bulge():
    dxf = """0
SECTION
2
ENTITIES
0
LWPOLYLINE
8
FLOOR
90
4
70
1
10
0.0
20
0.0
10
10.0
20
0.0
10
10.0
20
5.0
10
0.0
20
5.0
0
ENDSEC
0
EOF
"""
    doc = parse_dxf(dxf)
    poly = doc.entities[0]
    assert poly.type == "LWPOLYLINE"
    assert poly.layer == "FLOOR"
    assert len(poly.vertices) == 4


def test_parse_text_entity():
    dxf = """0
SECTION
2
ENTITIES
0
TEXT
8
TEXT
10
5.0
20
3.0
30
0.0
40
0.5
1
Zone A1
0
ENDSEC
0
EOF
"""
    doc = parse_dxf(dxf)
    txt = doc.entities[0]
    assert txt.type == "TEXT"
    assert txt.text == "Zone A1"


def test_parse_circle_entity():
    dxf = """0
SECTION
2
ENTITIES
0
CIRCLE
8
FACILITIES
10
5.0
20
5.0
30
0.0
40
2.5
0
ENDSEC
0
EOF
"""
    doc = parse_dxf(dxf)
    c = doc.entities[0]
    assert c.type == "CIRCLE"
    assert c.radius == 2.5


def test_parse_empty_document():
    dxf = """0
EOF
"""
    doc = parse_dxf(dxf)
    assert doc.entities == []


def test_parse_invalid_raises():
    import pytest
    with pytest.raises(ValueError, match="invalid DXF"):
        parse_dxf("not a dxf file at all")
