# RCS Backend v2.2 Progress Ledger

Tracks per-task review state for plan `docs/superpowers/plans/2026-08-23-rcs-backend-v2-implementation.md`.

Spec reference: `docs/superpowers/specs/2026-08-23-rcs-frontend-design.md` §13

## Workflow

For each task N:
1. Create `task-N-brief.md` from plan (verbatim copy of Task N section)
2. Dispatch implementer subagent (Task tool, subagent_type=generalPurpose) — implements Task N, runs tests, commits, writes `task-N-report.md`
3. Dispatch reviewer subagent — independently re-runs tests + verifies report claims, returns verdict
4. Update this ledger with status (✅ DONE / ⚠️ DONE_WITH_CONCERNS / ❌ FAILED)
5. Move to Task N+1

## Standard subagent prompt template

All Tasks 11-16 (and any later task that adds an API router) MUST include this preamble in the implementer subagent prompt:

> **Pre-step: replace your stub in `rcs_backend/api/__init__.py`**
> This task introduces one new router. Before creating the router module file, edit `rcs_backend/api/__init__.py` and replace the line:
> ```python
> <your_router_name> = APIRouter()
> ```
> with:
> ```python
> from rcs_backend.api.<your_module> import router as <your_router_name>
> ```
> Do this BEFORE running any pytest. The test collection depends on it.

(The Task 1 brief is already fixed at plan level — Task 1's stub ensures Tasks 2-10 collection works. Tasks 11-16 must each replace their own stub at the start.)

## Completed Tasks

- Task 1: rcs/backend 工程骨架 + pyproject + Docker — `a8c1a66` ✅ APPROVED_WITH_CONCERNS (plan defect: Step 7 imported 6 api submodules that didn't exist until Tasks 11-16. Plan patched: Task 1 stub + Tasks 11-16 each replace their stub at start). 11 files, +191 lines. Files match brief verbatim.
- Task 1 fix-up: `72c44e5` — `fix(rcs-backend): include_router passes router instance, stub is APIRouter()`. Plan defect extension: main.py used `.router` form but stub is bare APIRouter. Fixed to `include_router(topology_shell, ...)`; Task 11-16 re-exports already match this form.
- Task 2: Pydantic FloorShell model — `81af9f3` ✅ DONE. 3 files +193 lines. 5/5 tests pass. (Subagent made out-of-scope uncommitted changes to conftest/__init__/api/__init__.py; conftest/__init__ reverted, api/__init__ kept as plan-fix, main.py fixed in `72c44e5`.)
- Task 3: Pydantic SiteGrid model — `2d184a7` ✅ DONE. 3 files +117 lines. 6/6 tests pass. Full suite 11/11. Subagent respected file scope.
- Task 4: DXF ASCII parser — `2c63902` ✅ DONE. 3 files +331 lines. 6/6 tests pass. Full suite 17/17. Subagent respected scope; acknowledged pre-existing plan doc mods.
- Task 5: dxf_to_shell converter — `aecbfa4` ✅ DONE (after plan patch). Subagent correctly stopped with FAILED (Bounds(0,0) vs Field(gt=0), TEXT mismatch at y=2 vs zone center y=2.5, empty-shell assertion on bounds). Orchestrator applied 3 patches: model_construct for empty bounds, TEXT keyed by exact + round-1, test data TEXT at zone center. 5/5 tests pass. Full suite 22/22.
- Task 6: validate_shell — `fb64727` ✅ DONE (with 1 orchestrator patch). Subagent [c4ce6b55](c4ce6b55-5e2b-4ab5-8f9a-e8915a62dcf6) succeeded on first run. Pre-applied patch: `test_zero_width_zone_fails` uses `Zone.model_construct` (not literal `Zone(w=0)`) so validate_shell's own check is exercised. 6/6 tests pass. Full suite 28/28 (22 prior + 6 new). Zero regressions.
- Task 7: floor markings — `c9c54be` ✅ DONE.
- Task 8: 6 scenario templates — `d28c44b` ✅ DONE.
- Task 9: Shell 存储服务 — `582ac98` ✅ DONE_WITH_CONCERNS. 4/4 unit tests green; full suite 52/55 (3 failures from untracked Task 11 integration tests, OOS). Both orchestrator patches applied verbatim.
- Task 10: HTTP 客户端 → rcs/rcs — `d2ff2b5` ✅ DONE_WITH_CONCERNS. Brief had defect #4 (mock AsyncClient missing base_url — httpx 0.28.x requires absolute URLs to extract cookies). Orchestrator fix: 4 mock clients now threaded `base_url=client.base_url`. 6/6 unit tests green; full backend unit suite 47/47.
- Task 11: API router — topology_shell — `d2ddc08` ✅ DONE. 5 files, 111 ins / 8 del. 4/4 integration tests green; full suite 55/55.
- Task 12: API router — topology_grid — `5ed6972` ✅ DONE (with 3 brief bug fixes). 3 files, 81 ins / 2 del. Brief bugs fixed: (a) `cell_size` renamed to `resolution`, (b) flat `cells=[Cell,Cell]` simplified to auto-populated 2D `list[list[Cell]]`, (c) `grid.dimensions()` removed in favor of in-router capacity calc from bounds/resolution. 3/3 new integration tests green; full suite 58/58.
- Task 13: API router — topology_import — `9e95184` ✅ DONE (with 1 architectural fix + 1 minor). 5 files, 145 ins / 6 del. Architectural fix: `services/shell_store.py` now exposes `default_memory_store()` so the import router writes to the same backing store the topology_shell router reads from (previously each owned a private singleton, breaking test_dxf_import_save). 3/3 new integration tests green; full suite 61/61.
- Task 14: API router — topology_export — `0946603` ✅ DONE (with 1 brief bug fix). 3 files, 89 ins / 2 del. Brief bug fix: `WallSegment.{x0,y0,x1,y1}` is actually `{x0,z0,x1,z1}` in the real model. Used correct fields. 2/2 new integration tests green; full suite 63/63.
- Task 15: API router — topology_templates — `64fe1a6` ✅ DONE (with 1 brief bug fix). 3 files, 52 ins / 2 del. Brief bug fix: brief asserted `body["metadata"]["scenario"]` but real `cold_chain` template ships `{alert_types, highlight_color}` (no `scenario` key). Test adapted to assert against actual keys without weakening coverage. 3/3 new integration tests green; full suite 66/66.
- Task 16: API router — orders — `a3cfecf` ✅ DONE. 3 files, 104 ins / 3 del. 4/4 new integration tests green; full suite 70/70. File scope respected (test in dedicated `test_orders_api.py` per brief).
- Task 17: deploy/docker-compose.yml — `15f6e49` ✅ DONE (with 2 brief bug fixes). 1 file, +27 lines. Brief bugs fixed: (a) port 8100 collides with the existing standalone `rcs` service → moved to 8102 (free); (b) `RCS_SERVICE_URL: http://rcs:8101` would point to a nonexistent service → corrected to `http://rcs:8100` (matches the existing `rcs` service in the same compose). Added `volumes: rcs-data:` and matched healthcheck port. YAML validated.
- Task 18: full suite smoke + README — `a0ff60f` ✅ DONE. 1 file, +23 lines. Smoke test: `/health` → `{"status":"ok","version":"0.1.0"}`; `/api/rcs/topology/templates` → 6 scenarios (`cold_chain`, `ecommerce`, `manufacturing`, `multi_floor`, `port`, `reverse_logistics`). Full suite 70 passed / 0 failed. README gained REST API endpoint table + scenario ID list.

## Pending Tasks (0/18)

(none — all 18 tasks complete)

## Plan Defects Documented

- **Task 5** (already in ledger): Bounds(0,0) vs Field(gt=0), TEXT key mismatch, empty-shell bounds assertion — 3 orchestrator patches applied.
- **Task 6** (already in ledger): test_zero_width_zone_fails pre-applied patch (model_construct).
- **Task 10** (already in ledger): brief's test code creates `httpx.AsyncClient(transport=mock_transport)` without `base_url`; in httpx 0.28.x `_send_single_request` calls `cookies.extract_cookies()` which requires absolute URLs → `ValueError: unknown url type`. Orchestrator fix: thread `client.base_url` through the 4 mock clients.
- **Task 12** (NEW): brief uses `cell_size` (actual model field is `resolution`), flat `cells=[Cell,Cell]` (actual model uses 2D `list[list[Cell]]` auto-populated from bounds+resolution), and `grid.dimensions()` (does not exist). Router implementation + tests adapted to actual model API while preserving brief intent (capacity validation: too-many-cells → 422).
- **Task 13** (NEW): architectural defect — brief creates one `_store = MemoryShellStore()` per router module; topology_shell and topology_import end up with separate in-memory stores, breaking `test_dxf_import_save` (POST /import/dxf/{site_id} → GET /shell/{site_id}). Orchestrator fix: added `default_memory_store()` singleton accessor in `services/shell_store.py`; both routers now resolve their store via the shared singleton.
- **Task 14** (NEW): brief uses `WallSegment.{x0,y0,x1,y1}`; actual model uses `{x0,z0,x1,z1}`. Router implementation used correct fields.
- **Task 15** (NEW): brief asserts `body["metadata"]["scenario"] == "cold_chain"`; real `cold_chain` template ships metadata keys `alert_types` + `highlight_color` (no `scenario`). Test adapted to assert against actual keys.
- **Task 17** (NEW): brief specifies `rcs-backend` service on port 8100 with `RCS_SERVICE_URL: http://rcs:8101`. The existing `rcs` service in this compose already binds 8100 → port collision. And there's no `rcs:8101` service — only `rcs:8100`. Patched to port 8102 (free) and `RCS_SERVICE_URL: http://rcs:8100` (matches the actual `rcs` service). Also added `volumes: rcs-data:` so the volume reference resolves.

## Final Whole-Branch Review

- 18 of 18 tasks DONE (Tasks 1-6 + 9-18 ✅, Tasks 7-8 ✅ from prior session).
- 9 commits added in this run (d2ddc08, 5ed6972, 9e95184, 0946603, 64fe1a6, a3cfecf, 15f6e49, a0ff60f), each with strict staging discipline (single concern per commit; only files in the brief's file list + plan-defect remediation).
- **Final test counts**: 70 passed / 0 failed (`pytest` at `rcs/backend/`).
  - 51 unit tests (Tasks 2-10 domain logic)
  - 19 integration tests (4 Task 11 + 3 Task 12 + 3 Task 13 + 2 Task 14 + 3 Task 15 + 4 Task 16)
- **Smoke test passed**: `uvicorn rcs_backend.main:app --port 8103` → `/health` returns 200 + version, `/api/rcs/topology/templates` returns all 6 scenarios.
- **Docker compose validated**: `deploy/docker-compose.yml` now has 4 services (broker, rcs, api, rcs-backend) + 1 named volume. Port allocation: broker 1883/9001, rcs 8100, api 8000, rcs-backend 8102.
- **Plan defect ledger**: 7 brief defects documented (Tasks 5, 6, 10, 12, 13, 14, 15, 17). All fixed at orchestrator level; subagents would have otherwise blocked on them. Task 12 alone had 3 defects in a single brief.

## Notes

- Authorization: implement on `main` branch (no worktree)
- Model: `inherit` for implementer and reviewer
- Spec + plan committed before Task 1 begins
- **Pip mirror (Windows / global)**: `~/.pip/pip.ini` points to Tsinghua + Aliyun. All subagents MUST use `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <pkg>` or rely on the global config. NEVER use the default PyPI URL in CI-like install steps.
- **npm/pnpm mirror** (when frontend plan starts): use `npm config set registry https://registry.npmmirror.com` and `pnpm config set registry https://registry.npmmirror.com` before any `pnpm install`.