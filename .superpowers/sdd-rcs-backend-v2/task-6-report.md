# Task 6 Report: 蓝图校验（validate_shell）

## Status: DONE

## Commit(s)
| Hash | Message |
|------|---------|
| `fb64727` | `feat(rcs-backend): FloorShell validation (bounds/overlap/zone types)` |

## TDD Evidence

### RED
Run: `cd rcs/backend && python -m pytest tests/unit/test_validate.py -v`
```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.0.1, pluggy-1.6.0
rootdir: D:\projects\robot-logic\rcs\backend
configfile: pyproject.toml
collecting ... collected 0 items / 1 error

=================================== ERRORS ====================================
________________ ERROR collecting tests/unit/test_validate.py _________________
ImportError while importing test module
'...\tests\unit\test_validate.py'.
Traceback:
... rc\backend\tests\unit\test_validate.py:2: in <module>
    from rcs_backend.topology.validate import validate_shell, ValidationError, ValidationReport
... rc\backend\rcs_backend\topology\__init__.py:10: in <module>
    from rcs_backend.topology.validate import validate_shell, ValidationError, ValidationReport
E   ModuleNotFoundError: No module named 'rcs_backend.topology.validate'
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 1.38s ===============================
```

### GREEN
Run: `cd rcs/backend && python -m pytest tests/unit/test_validate.py -v`
```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.0.1, pluggy-1.6.0
rootdir: D:\projects\robot-logic\rcs\backend
configfile: pyproject.toml
collected 6 items

tests/unit/test_validate.py::test_valid_shell_passes        PASSED [ 16%]
tests/unit/test_validate.py::test_oversized_bounds_fails    PASSED [ 33%]
tests/unit/test_validate.py::test_zero_width_zone_fails     PASSED [ 50%]
tests/unit/test_validate.py::test_unknown_zone_type_warns   PASSED [ 66%]
tests/unit/test_validate.py::test_zone_outside_bounds_fails PASSED [ 83%]
tests/unit/test_validate.py::test_duplicate_wall_ids_fail   PASSED [100%]

============================== 6 passed in 0.11s ===============================
```

### Full suite
Run: `cd rcs/backend && python -m pytest -v`
```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.0.1, pluggy-1.6.0
rootdir: D:\projects\robot-logic\rcs\backend
configfile: pyproject.toml
testpaths: tests
collected 28 items

tests/unit/test_dxf_parser.py::test_parse_minimal_line_entity             PASSED [  3%]
tests/unit/test_dxf_parser.py::test_parse_lwpolyline_with_bulge           PASSED [  7%]
tests/unit/test_dxf_parser.py::test_parse_text_entity                     PASSED [ 10%]
tests/unit/test_dxf_parser.py::test_parse_circle_entity                   PASSED [ 14%]
tests/unit/test_dxf_parser.py::test_parse_empty_document                  PASSED [ 17%]
tests/unit/test_dxf_parser.py::test_parse_invalid_raises                  PASSED [ 21%]
tests/unit/test_dxf_to_shell.py::test_walls_layer_becomes_wall_segments   PASSED [ 25%]
tests/unit/test_dxf_to_shell.py::test_zones_layer_becomes_zones_with_ref  PASSED [ 28%]
tests/unit/test_dxf_to_shell.py::test_facilities_layer_becomes_facilities PASSED [ 32%]
tests/unit/test_dxf_to_shell.py::test_floor_layer_sets_bounds             PASSED [ 35%]
tests/unit/test_dxf_to_shell.py::test_empty_doc_yields_empty_shell        PASSED [ 39%]
tests/unit/test_floor_shell_model.py::test_wall_segment_full              PASSED [ 42%]
tests/unit/test_floor_shell_model.py::test_zone_with_cold_chain_metadata  PASSED [ 46%]
tests/unit/test_floor_shell_model.py::test_floor_shell_minimal            PASSED [ 50%]
tests/unit/test_floor_shell_model.py::test_floor_shell_with_multi_floor   PASSED [ 53%]
tests/unit/test_floor_shell_model.py::test_zone_type_v2_2_covers_scenarios PASSED [ 57%]
tests/unit/test_site_grid_model.py::test_cell_type_enum_all_members       PASSED [ 60%]
tests/unit/test_site_grid_model.py::test_cell_default_empty               PASSED [ 64%]
tests/unit/test_site_grid_model.py::test_site_grid_minimal_default_resolution PASSED [ 67%]
tests/unit/test_site_grid_model.py::test_site_grid_custom_resolution      PASSED [ 71%]
tests/unit/test_site_grid_model.py::test_site_grid_2d_indexing            PASSED [ 75%]
tests/unit/test_site_grid_model.py::test_site_grid_serializes_to_dict     PASSED [ 78%]
tests/unit/test_validate.py::test_valid_shell_passes                      PASSED [ 82%]
tests/unit/test_validate.py::test_oversized_bounds_fails                  PASSED [ 85%]
tests/unit/test_validate.py::test_zero_width_zone_fails                   PASSED [ 89%]
tests/unit/test_validate.py::test_unknown_zone_type_warns                 PASSED [ 92%]
tests/unit/test_validate.py::test_zone_outside_bounds_fails               PASSED [ 96%]
tests/unit/test_validate.py::test_duplicate_wall_ids_fail                 PASSED [100%]

============================= 28 passed in 0.21s ===============================
```

## Files Created/Modified

**Modified** (1):
- `rcs/backend/rcs_backend/topology/__init__.py` — replaced `validate_shell` placeholder with real import; updated `__all__` to expose `ValidationError`, `ValidationReport`; left `generate_markings`, `list_templates`, `get_template` placeholders intact for Tasks 7, 8.

**Created** (2):
- `rcs/backend/rcs_backend/topology/validate.py` — `ValidationError`, `ValidationReport`, `validate_shell(shell, max_bounds_m=500.0)`.
- `rcs/backend/tests/unit/test_validate.py` — 6 tests per brief (including `Zone.model_construct` patch for `test_zero_width_zone_fails`).

## Concerns (if any)

None. Brief was implementable verbatim. The plan patch for `test_zero_width_zone_fails` (`Zone.model_construct(...)`) was applied as provided and exercised `validate_shell`'s defense-in-depth zero-width check correctly (test asserts `"width" in e` — error message says `zone z1 has zero width/depth`).

Git emitted CRLF→LF normalization warnings for the two new files (Windows checkout), which is expected behavior and not a concern.

## Self-Review

- **Completeness:** All 6 brief steps executed in order: placeholder replaced → tests written → RED captured → module created → GREEN captured → full suite 28/28 → single commit on `main`. Commit message verbatim from brief.
- **Quality:** Module uses `from __future__ import annotations`, full type hints, pydantic `BaseModel` for `ValidationReport`, default tolerance of 0.01 m for negative-origin and out-of-bounds checks. No code comments narrating mechanics. Tests use a `_shell(**kw)` helper to keep cases readable.
- **Discipline:** Only the three files listed in the brief were touched. Verified with `git show --stat HEAD` — `3 files changed`. No edits to `tests/conftest.py`, `rcs_backend/__init__.py`, `main.py`, `models/*`, `config.py`, `dxf_parser.py`, `dxf_to_shell.py`, or `api/`. The uncommitted plan-doc edit on `main` (from prior orchestration) was left untouched.
- **Testing:** RED was a real `ModuleNotFoundError` from the new module import (not a stub mismatch). GREEN all 6 passed. Full suite shows 22 prior + 6 new = 28 passed, no regressions.
