# Task 8 Report: 6 场景预置模板（templates）

## Status: DONE_WITH_CONCERNS

## Commit(s)
| Hash | Message |
|------|---------|
| `d28c44b` | `feat(rcs-backend): 6 scenario templates (ecommerce/manufacturing/cold_chain/port/reverse/multi_floor)` |

## TDD Evidence

### RED
Run: `cd rcs/backend && python -m pytest tests/unit/test_templates.py -v`
```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.0.1, pluggy-1.6.0
rootdir: D:\projects\robot-logic\rcs\backend
configfile: pyproject.toml
collecting ... collected 0 items / 1 error

=================================== ERRORS ====================================
________________ ERROR collecting tests/unit/test_templates.py ________________
ImportError while importing test module
'D:\projects\robot-logic\rcs\backend\tests\unit\test_templates.py'.
Traceback:
... rc\backend\tests\unit\test_templates.py:3: in <module>
    from rcs_backend.topology.templates import (
... rc\backend\rcs_backend\topology\__init__.py:14: in <module>
    from rcs_backend.topology.templates import (
E   ModuleNotFoundError: No module named 'rcs_backend.topology.templates'
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 1.89s ===============================
```
Matches brief Step 2 expectation exactly (`ModuleNotFoundError` from
`rcs_backend.topology.templates`).

### GREEN
Run: `cd rcs/backend && python -m pytest tests/unit/test_templates.py -v`
```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.0.1, pluggy-1.6.0
rootdir: D:\projects\robot-logic\rcs\backend
configfile: pyproject.toml
collected 8 items

tests/unit/test_templates.py::test_scenario_ids_count PASSED             [ 12%]
tests/unit/test_templates.py::test_list_templates_returns_six PASSED     [ 25%]
tests/unit/test_templates.py::test_get_ecommerce_template PASSED         [ 37%]
tests/unit/test_templates.py::test_get_cold_chain_template PASSED        [ 50%]
tests/unit/test_templates.py::test_get_port_template PASSED              [ 62%]
tests/unit/test_templates.py::test_get_multi_floor_has_floors PASSED     [ 75%]
tests/unit/test_templates.py::test_get_unknown_template_raises PASSED    [ 87%]
tests/unit/test_templates.py::test_templates_have_scenario_metadata PASSED [100%]

============================== 8 passed in 0.33s ==============================
```
All 8 brief tests pass on first GREEN run.

### Full suite
Run: `cd rcs/backend && python -m pytest -v`
```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.0.1, pluggy-1.6.0
rootdir: D:\projects\robot-logic\rcs\backend
configfile: pyproject.toml
testpaths: tests
collected 51 items

tests/unit/test_dxf_parser.py::test_parse_minimal_line_entity PASSED     [  1%]
tests/unit/test_dxf_parser.py::test_parse_lwpolyline_with_bulge PASSED   [  3%]
tests/unit/test_dxf_parser.py::test_parse_text_entity PASSED             [  5%]
tests/unit/test_dxf_parser.py::test_parse_circle_entity PASSED           [  7%]
tests/unit/test_dxf_parser.py::test_parse_empty_document PASSED          [  9%]
tests/unit/test_dxf_parser.py::test_parse_invalid_raises PASSED         [ 11%]
tests/unit/test_dxf_to_shell.py::test_walls_layer_becomes_wall_segments PASSED [ 13%]
tests/unit/test_dxf_to_shell.py::test_zones_layer_becomes_zones_with_ref PASSED [ 15%]
tests/unit/test_dxf_to_shell.py::test_facilities_layer_becomes_facilities PASSED [ 17%]
tests/unit/test_dxf_to_shell.py::test_floor_layer_sets_bounds PASSED     [ 19%]
tests/unit/test_dxf_to_shell.py::test_empty_doc_yields_empty_shell PASSED [ 21%]
tests/unit/test_floor_shell_model.py::test_wall_segment_full PASSED      [ 23%]
tests/unit/test_floor_shell_model.py::test_zone_with_cold_chain_metadata PASSED [ 25%]
tests/unit/test_floor_shell_model.py::test_floor_shell_minimal PASSED    [ 27%]
tests/unit/test_floor_shell_model.py::test_floor_shell_with_multi_floor PASSED [ 29%]
tests/unit/test_floor_shell_model.py::test_zone_type_v2_2_covers_scenarios PASSED [ 31%]
tests/unit/test_markings.py::test_corridor_generates_lane_marking PASSED [ 33%]
tests/unit/test_markings.py::test_dock_zones_get_stop_markings PASSED    [ 35%]
tests/unit/test_markings.py::test_no_zones_no_corridors_no_docks_empty PASSED [ 37%]
tests/unit/test_markings.py::test_markings_have_color PASSED             [ 39%]
tests/unit/test_markings.py::test_lane_marks_both_directions_when_bidirectional PASSED [ 41%]
tests/unit/test_rcs_client.py::test_get_registry_calls_correct_endpoint FAILED [ 43%]
tests/unit/test_rcs_client.py::test_send_command_posts_to_device_id FAILED [ 45%]
tests/unit/test_rcs_client.py::test_get_state_calls_device_state_endpoint FAILED [ 47%]
tests/unit/test_rcs_client.py::test_client_default_url PASSED            [ 49%]
tests/unit/test_rcs_client.py::test_client_passes_timeout PASSED         [ 50%]
tests/unit/test_rcs_client.py::test_estop_all_devices FAILED             [ 52%]
tests/unit/test_shell_store.py::test_memory_store_save_and_get PASSED    [ 54%]
tests/unit/test_shell_store.py::test_memory_store_get_missing_returns_none PASSED [ 56%]
tests/unit/test_shell_store.py::test_memory_store_list_sites PASSED      [ 58%]
tests/unit/test_shell_store.py::test_sqlite_store_persists PASSED        [ 60%]
tests/unit/test_site_grid_model.py::test_cell_type_enum_all_members PASSED [ 62%]
tests/unit/test_site_grid_model.py::test_cell_default_empty PASSED       [ 64%]
tests/unit/test_site_grid_model.py::test_site_grid_minimal_default_resolution PASSED [ 66%]
tests/unit/test_site_grid_model.py::test_site_grid_custom_resolution PASSED [ 68%]
tests/unit/test_site_grid_model.py::test_site_grid_2d_indexing PASSED    [ 70%]
tests/unit/test_site_grid_model.py::test_site_grid_serializes_to_dict PASSED [ 72%]
tests/unit/test_templates.py::test_scenario_ids_count PASSED             [ 74%]
tests/unit/test_templates.py::test_list_templates_returns_six PASSED     [ 76%]
tests/unit/test_templates.py::test_get_ecommerce_template PASSED         [ 78%]
tests/unit/test_templates.py::test_get_cold_chain_template PASSED        [ 80%]
tests/unit/test_templates.py::test_get_port_template PASSED              [ 82%]
tests/unit/test_templates.py::test_get_multi_floor_has_floors PASSED     [ 84%]
tests/unit/test_templates.py::test_get_unknown_template_raises PASSED    [ 87%]
tests/unit/test_templates.py::test_templates_have_scenario_metadata PASSED [ 88%]
tests/unit/test_validate.py::test_valid_shell_passes PASSED              [ 90%]
tests/unit/test_validate.py::test_oversized_bounds_fails PASSED          [ 92%]
tests/unit/test_validate.py::test_zero_width_zone_fails PASSED           [ 94%]
tests/unit/test_validate.py::test_unknown_zone_type_warns PASSED         [ 96%]
tests/unit/test_validate.py::test_zone_outside_bounds_fails PASSED       [ 98%]
tests/unit/test_validate.py::test_duplicate_wall_ids_fail PASSED         [100%]

======================== 4 failed, 47 passed in 3.57s =========================
```

**Targeted scope count (Task 8 brief's "33 prior + 8 new = 41"):** When the
test command is restricted to the 7 in-scope test modules
(`test_templates.py test_dxf_parser.py test_dxf_to_shell.py test_floor_shell_model.py test_markings.py test_site_grid_model.py test_validate.py`)
the result is exactly **41 passed in 0.57s**, matching the brief's expected
"33 prior + 8 new".

The on-disk `python -m pytest -v` (no filter) collects **51 items** because
the working tree also contains untracked-but-on-disk files from later tasks
(`test_rcs_client.py` for Task 10 and `test_shell_store.py` for Task 9) that
are not part of Task 8's commit. Those files are present on disk but outside
the brief's file list. The 4 failures are all in `test_rcs_client.py` and
reflect pre-existing Task 10 implementation defects in `rcs_backend/api/rcs_client.py`
(httpx transport is constructed without `base_url`, so relative URLs like
`/registry` raise `ValueError: unknown url type`). These failures are unrelated
to Task 8 and to my commit.

## Files Created/Modified

**Created** (2):
- `rcs/backend/rcs_backend/topology/templates.py` — 6 scenario builders
  (`_ecommerce`, `_manufacturing`, `_cold_chain`, `_port`,
  `_reverse_logistics`, `_multi_floor`), public dataclasses `TemplateInfo`
  (pydantic `BaseModel`) and `TemplateBundle` (`@dataclass`), public functions
  `list_templates()` and `get_template(scenario_id)`, and the patched
  `_default_grid(w, d, resolution=2.0)` that uses `SiteGrid(site_id="default",
  bounds={"w": w, "d": d}, resolution=resolution)` and lets `SiteGrid.__init__`'s
  empty-cell branch auto-populate the grid with EMPTY cells.
- `rcs/backend/tests/unit/test_templates.py` — 8 tests per brief (with all 3
  orchestrator-applied test-side patches: added `pytest` import, added
  `TemplateInfo`/`TemplateBundle` to import list, and
  `test_list_templates_returns_six` now does `isinstance(t, TemplateInfo)`).

**Modified** (1):
- `rcs/backend/rcs_backend/topology/__init__.py` — replaced the two
  `NotImplementedError` placeholders for `list_templates` and `get_template`
  with a real `from rcs_backend.topology.templates import (...)` re-export,
  updated `__all__` to include `SCENARIO_IDS`, `TemplateInfo`, `TemplateBundle`.
  Tasks 4-7 imports (`parse_dxf`, `DxfEntity`, `DxfDocument`, `dxf_to_shell`,
  `validate_shell`, `ValidationError`, `ValidationReport`,
  `generate_markings`) are preserved.

**Commit stat:**
```
rcs/backend/rcs_backend/topology/__init__.py  |  14 +-
rcs/backend/rcs_backend/topology/templates.py | 208 ++++++++++++++++++++++++++
rcs/backend/tests/unit/test_templates.py      |  61 ++++++++
3 files changed, 274 insertions(+), 9 deletions(-)
```

## Concerns

1. **Pre-existing Task 10 failures in `test_rcs_client.py` (out-of-scope for
   Task 8).** The on-disk full suite shows 4 failures, all in
   `tests/unit/test_rcs_client.py::test_get_registry_calls_correct_endpoint`,
   `test_send_command_posts_to_device_id`,
   `test_get_state_calls_device_state_endpoint`, and `test_estop_all_devices`.
   Root cause is in `rcs_backend/api/rcs_client.py` (lines 17-20): the
   constructor builds `httpx.AsyncClient(base_url=self.base_url, ...)` but
   the test injects `client._client = httpx.AsyncClient(transport=mock_transport)`
   with no `base_url`, so the subsequent relative-URL calls (`/registry`,
   `/agv-01/command`, `/agv-01/state`, `/estop`) hit `urllib.request`'s
   `ValueError: unknown url type: '/registry'`. This is a Task 10 file
   (`rcs_backend/api/rcs_client.py`) and test, neither of which appears in
   Task 8's file list. **Per discipline I did not touch either file.** The
   brief's expected "41 passed" is achieved when the run is restricted to
   the 7 in-scope test modules; the 4 failures are a Task 10 regression,
   not introduced by Task 8.

2. **Orchestrator-applied patches in Task 7's `test_markings.py`**
   (out-of-scope for Task 8). Between the time the brief was generated and
   my run, the on-disk `test_markings.py::test_corridor_generates_lane_marking`
   was patched to add `bidirectional=False` to the `Corridor` constructor
   call (line 15). This is what allows that test to pass on the current
   disk state (and is consistent with the Task 7 FAILED report's suggested
   fix). Task 7's commit has not landed on `main` (`markings.py` and
   `test_markings.py` are still untracked as of my commit), so this patch
   lives only in the working tree. **Per discipline I did not touch
   `test_markings.py` or `markings.py`.**

3. **Plan patch `#1` (brief) applied verbatim**: `_default_grid` uses
   `SiteGrid(site_id="default", bounds={"w": w, "d": d}, resolution=2.0)`
   and lets `SiteGrid.__init__`'s empty-cell branch auto-populate. No
   `cells=` or `cell_size=` argument is passed. The docstring in the file
   explains why the brief's original 3-argument form
   (`SiteGrid(bounds=..., cell_size=2.0, cells=cells)`) is incompatible
   with the actual `SiteGrid` model.

4. **Plan patch `#2`/`#3`/`#4` (brief) applied verbatim to test**: pytest
   import added, `TemplateInfo`/`TemplateBundle` added to the import list,
   and `test_list_templates_returns_six` does
   `isinstance(t, TemplateInfo)` per the brief.

## Self-Review

- **Completeness**: All 6 brief steps executed in order. Step 0 placeholder
  replaced → Step 1 tests written → Step 2 RED captured
  (`ModuleNotFoundError: No module named 'rcs_backend.topology.templates'`)
  → Step 3 `templates.py` created → Step 4 GREEN captured (8/8 passed)
  → Step 5 full-suite evidence captured (47/51 pass; 41/41 pass when
  restricted to in-scope modules) → Step 6 single commit on `main` with
  the brief's verbatim message. No steps skipped.

- **Quality**: `templates.py` uses `from __future__ import annotations`,
  full type hints (`list[TemplateInfo]`, `TemplateBundle`, etc.),
  pydantic `BaseModel` for `TemplateInfo` (matches the FloorShell/SiteGrid
  pydantic idiom), `@dataclass` for `TemplateBundle` (the brief's chosen
  shape). Each scenario builder is independent and pure (no shared mutable
  state). `_default_grid` deliberately uses `SiteGrid`'s built-in
  auto-populate, exactly as the orchestrator patch specifies, and the
  docstring records the brief-defect correction. `__init__.py` preserves
  all 9 names from Tasks 4-7 (`parse_dxf`, `DxfEntity`, `DxfDocument`,
  `dxf_to_shell`, `validate_shell`, `ValidationError`, `ValidationReport`,
  `generate_markings`) and adds the 5 new names
  (`list_templates`, `get_template`, `SCENARIO_IDS`, `TemplateInfo`,
  `TemplateBundle`); all 14 names are exported via `__all__`.

- **Discipline**: Only the 3 files listed in the brief were touched.
  Verified with `git show --stat HEAD` — `3 files changed`. No edits to
  `tests/conftest.py`, `rcs_backend/__init__.py`, `main.py`, `models/*`,
  `config.py`, `dxf_parser.py`, `dxf_to_shell.py`, `validate.py`,
  `markings.py`, `api/`, `services/`, `test_rcs_client.py`,
  `test_shell_store.py`, or any other file. **Specifically did NOT touch
  `floor_shell.py` or `site_grid.py`** — `SiteGrid` is imported and
  instantiated but the model file is byte-for-byte identical to the
  Task 3 commit. The pre-existing modifications to
  `docs/superpowers/plans/2026-08-23-rcs-backend-v2-implementation.md`
  (visible in `git status` prior to my work) were left untouched.

- **Testing**: RED was a real `ModuleNotFoundError` from the new module
  import (not a stub mismatch). GREEN all 8 tests passed on first run.
  Full suite in-scope count: 41/41 passed. Full suite including
  on-disk untracked tasks: 47/51 passed — the 4 failures are all in
  Task 10 files (`test_rcs_client.py`, `rcs_backend/api/rcs_client.py`),
  not introduced by my commit. CRLF→LF normalization warnings on the two
  new files are expected Windows behavior.