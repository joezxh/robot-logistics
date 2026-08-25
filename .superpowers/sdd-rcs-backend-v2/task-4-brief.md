## Task 4: DXF ASCII 解析器

**Files:**
- Create: `rcs/backend/rcs_backend/topology/__init__.py`
- Create: `rcs/backend/rcs_backend/topology/dxf_parser.py`
- Create: `rcs/backend/tests/unit/test_dxf_parser.py`

**Interfaces:**
- Produces:
  - `class DxfEntity(BaseModel)`: layer, type ("LWPOLYLINE"|"LINE"|"CIRCLE"|"MTEXT"|"TEXT"|"HATCH"), vertices=[[x,y]...], text="", radius=0.0, layer_name
  - `class DxfDocument(BaseModel)`: entities: list[DxfEntity], header_units="m"
  - `def parse_dxf(text: str) -> DxfDocument`: pure function, 零依赖，解析 DXF ASCII group codes

- [ ] **Step 1: 写失败的测试 `test_dxf_parser.py`**

```python
"""DXF ASCII parser — ported from wx3D parseDXF (zero external deps)."""
from rcs_backend.topology.dxf_parser import parse_dxf, DxfEntity, DxfDocument


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
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && pytest tests/unit/test_dxf_parser.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/topology/__init__.py`**（仅 re-export Task 4 创建的 parse_dxf；其余 5 个是 placeholder 直到各自 Task 替换）

```python
"""Topology utilities — DXF parsing, validation, templates.

Task 4 contributes `parse_dxf` / `DxfEntity` / `DxfDocument` (real).
Tasks 5-8 each edit THIS file to replace their placeholder with the real
re-export (same pattern as Task 4).
"""
from rcs_backend.topology.dxf_parser import parse_dxf, DxfEntity, DxfDocument

# Placeholders — replaced by Tasks 5, 6, 7, 8 respectively
def dxf_to_shell(*args, **kwargs):
    raise NotImplementedError("dxf_to_shell is added by Task 5")

def validate_shell(*args, **kwargs):
    raise NotImplementedError("validate_shell is added by Task 6")

def generate_markings(*args, **kwargs):
    raise NotImplementedError("generate_markings is added by Task 7")

def list_templates(*args, **kwargs):
    raise NotImplementedError("list_templates is added by Task 8")

def get_template(*args, **kwargs):
    raise NotImplementedError("get_template is added by Task 8")

__all__ = [
    "parse_dxf", "DxfEntity", "DxfDocument",
    "dxf_to_shell",
    "validate_shell",
    "generate_markings",
    "list_templates", "get_template",
]
```

> **Plan note:** Tasks 5-8 will each edit THIS file (their Step 3 / Step 1) to replace the NotImplementedError placeholder with the real import.

- [ ] **Step 4: 创建 `rcs/backend/rcs_backend/topology/dxf_parser.py`**

(Paste the verbatim parser code from plan line 957+ — implement a state-machine that:
- iterates group code/value pairs
- on code 0 → start new entity (track type from next line)
- on code 8 → set layer
- on code 10/20/30 → push x/y/z to current entity
- on code 40 → CIRCLE radius
- on code 1 → TEXT/MTEXT text
- on code 90 → LWPOLYLINE vertex count
- on code 70 → polyline flag
- on SECTION/ENDSEC/EOF → control flow
- INSBUNITS header code 70 → "m"/"mm" mapping
- raise ValueError("invalid DXF: ...") if neither SECTION nor EOF found

The full reference parser is in the plan document at line 957+ — copy it verbatim.)

- [ ] **Step 5: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/unit/test_dxf_parser.py -v`
Expected: PASS (6 tests)

- [ ] **Step 6: 跑全 suite 确认无回归**

Run: `cd rcs/backend && pytest -v`
Expected: 11 (Tasks 2-3) + 6 (Task 4) = 17 passed

- [ ] **Step 7: Commit**

```bash
git add rcs/backend/rcs_backend/topology/__init__.py \
        rcs/backend/rcs_backend/topology/dxf_parser.py \
        rcs/backend/tests/unit/test_dxf_parser.py
git commit -m "feat(rcs-backend): DXF ASCII parser (zero-deps, 6 entity types)"
```