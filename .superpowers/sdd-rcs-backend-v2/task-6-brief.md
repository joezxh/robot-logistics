## Task 6: 蓝图校验（validate_shell）

**Files:**
- Create: `rcs/backend/rcs_backend/topology/validate.py`
- Create: `rcs/backend/tests/unit/test_validate.py`
- **Modify** `rcs/backend/rcs_backend/topology/__init__.py` (replace `validate_shell` placeholder)

**Interfaces:**
- Produces:
  - `class ValidationError(ValueError)`
  - `class ValidationReport(BaseModel)`: errors: list[str], warnings: list[str], ok: bool
  - `def validate_shell(shell: FloorShell, max_bounds_m=500.0) -> ValidationReport`

- [ ] **Step 0: Replace placeholder in `topology/__init__.py`**

Edit `rcs/backend/rcs_backend/topology/__init__.py`: replace the placeholder `def validate_shell(*args, **kwargs): raise NotImplementedError(...)` with the real import:

```python
from rcs_backend.topology.validate import validate_shell, ValidationError, ValidationReport
```

(`validate_shell` is already in `__all__` — no change needed there.)

- [ ] **Step 1: 写失败的测试 `test_validate.py`**

```python
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
```

> **Plan patch note**: Brief's `test_zero_width_zone_fails` constructed
> `Zone(w=0, d=5)` literally, which fails at pydantic validation
> (`Field(gt=0)`) before `validate_shell` ever sees it. The patched test uses
> `Zone.model_construct(...)` to deliberately create the malformed zone so
> `validate_shell`'s own zero-width check is exercised. This preserves both
> the model strictness and validate_shell's defense-in-depth contract.

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && pytest tests/unit/test_validate.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/topology/validate.py`**

```python
"""Validate FloorShell blueprints."""
from __future__ import annotations
from pydantic import BaseModel
from rcs_backend.models.floor_shell import FloorShell, ZONE_TYPES


class ValidationError(ValueError):
    """Raised when a shell fails hard validation (e.g. duplicate IDs)."""


class ValidationReport(BaseModel):
    errors: list[str] = []
    warnings: list[str] = []
    ok: bool = True


def validate_shell(shell: FloorShell, max_bounds_m: float = 500.0) -> ValidationReport:
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Bounds check
    if shell.bounds.w > max_bounds_m or shell.bounds.d > max_bounds_m:
        errors.append(
            f"bounds {shell.bounds.w}x{shell.bounds.d} exceed max {max_bounds_m}m"
        )

    # 2. Duplicate wall IDs
    wall_ids = [w.id for w in shell.walls]
    if len(wall_ids) != len(set(wall_ids)):
        errors.append("duplicate wall IDs detected")

    # 3. Zone geometry
    for z in shell.zones:
        if z.w <= 0 or z.d <= 0:
            errors.append(f"zone {z.id} has zero width/depth")
        if z.x < -0.01 or z.z < -0.01:
            errors.append(f"zone {z.id} has negative origin")
        if z.x + z.w > shell.bounds.w + 0.01 or z.z + z.d > shell.bounds.d + 0.01:
            errors.append(f"zone {z.id} extends outside bounds")

    # 4. Unknown zone type
    for z in shell.zones:
        if z.type not in ZONE_TYPES:
            warnings.append(f"zone {z.id} has unknown type '{z.type}'")

    return ValidationReport(errors=errors, warnings=warnings, ok=len(errors) == 0)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/unit/test_validate.py -v`
Expected: PASS（6 tests）

- [ ] **Step 5: 跑全 suite 确认无回归**

Run: `cd rcs/backend && pytest -v`
Expected: 22 (prior) + 6 (new) = 28 passed

- [ ] **Step 6: Commit**

```bash
git add rcs/backend/rcs_backend/topology/validate.py \
        rcs/backend/rcs_backend/topology/__init__.py \
        rcs/backend/tests/unit/test_validate.py
git commit -m "feat(rcs-backend): FloorShell validation (bounds/overlap/zone types)"
```