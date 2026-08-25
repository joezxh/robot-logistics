# Task 1 Report: rcs/backend 工程骨架

## Status: DONE_WITH_CONCERNS

## Commit(s)
| Hash | Message |
|------|---------|
| `a8c1a66e0619cbbe0729dfec8ada739bc2900d78` | `feat(rcs-backend): scaffold v2.2 unified backend (pyproject + main + config + docker)` |

## TDD Evidence
### Smoke test
```
$ cd D:\projects\robot-logic\rcs\backend; python -m pytest -v
============================= test session starts ==============================
platform win32 -- Python 3.11.0, pytest-8.0.1, pluggy-1.0.0
configfile: pyproject.toml
rootdir: D:\projects\robot-logic\rcs\backend
collected 0 items

tests\conftest.py:5: in <module>
    from rcs_backend.main import create_app
rcs_backend\__init__.py:2: in <module>
    from rcs_backend.main import create_app
rcs_backend\main.py:6: in <module>
    from rcs_backend.api import (
E   ImportError: cannot import name 'topology_shell' from 'rcs_backend.api' (D:\projects\robot-logic\rcs\backend\rcs_backend\api\__init__.py)
ERROR: could not load D:\projects\robot-logic\rcs\backend\tests\conftest.py
=========================== no tests ran, 1 error in 0.21s ===========================
EXIT: 4
```

**Result:** pytest collection FAILS with exit code 4 (conftest ImportError). The brief's stated expectation ("PASS — no tests yet, but pytest must collect") is not met.

### Plan defect root cause

The brief contains an internal contradiction:

- **Step 7 (`rcs_backend/main.py`)** — as specified, imports six submodules from the `api` package:
  ```python
  from rcs_backend.api import (
      topology_shell, topology_grid, topology_import,
      topology_export, topology_templates, orders,
  )
  ```
- **Step 10 (`rcs_backend/api/__init__.py`)** — as specified, is an empty placeholder:
  ```python
  # 空文件（待后续 task 填充）
  ```

Because `tests/conftest.py` does `from rcs_backend.main import create_app`, pytest always loads `main.py` at conftest-collection time. With `api/__init__.py` empty, the six `from rcs_backend.api import ...` names do not exist → `ImportError`.

**No fix applied** per instruction "DO NOT silently fix the plan". The six routers are scheduled for Tasks 11–16; once those land, collection will succeed automatically. The defect is **transient** and self-resolving once the plan advances.

## Files Created (line counts via `Get-Content | Measure-Object -Line`)

| Path | Lines |
|------|-------|
| `rcs/backend/pyproject.toml` | 32 |
| `rcs/backend/README.md` | 31 |
| `rcs/backend/Dockerfile` | 18 |
| `rcs/backend/conftest.py` | 8 |
| `rcs/backend/rcs_backend/__init__.py` | 6 |
| `rcs/backend/rcs_backend/config.py` | 35 |
| `rcs/backend/rcs_backend/main.py` | 42 |
| `rcs/backend/rcs_backend/api/__init__.py` | 1 |
| `rcs/backend/tests/__init__.py` | 1 |
| `rcs/backend/tests/unit/__init__.py` | 1 |
| `rcs/backend/tests/conftest.py` | 15 |

> Note: counts include trailing newlines / final blank line. Brief file bodies are reproduced verbatim; no paraphrasing or "improvements".

## Concerns

1. **Smoke test fails (plan defect)** — see TDD Evidence above. The brief's Step 7 (main.py router imports) and Step 10 (empty api/__init__.py) are mutually incompatible. The expected "pytest can collect" outcome cannot be achieved with the brief's literal files. Flagged for the orchestrator / reviewer; no code change made.
2. **`flit` not installed locally** — irrelevant for the smoke test (we did not invoke `flit install`); the Dockerfile installs flit at build time. Dev installation of the package itself is also not required for the smoke test (the root `conftest.py` adds `rcs/backend/` to `sys.path`).
3. **Pre-existing root `pyproject.toml` is plain prose-with-headers, not valid TOML.** Pytest 8 reads the *current-directory* `pyproject.toml` and emits a benign warning during `--version`; the smoke test still runs the rcs/backend configfile (`rcs/backend/pyproject.toml`) as intended. Out of scope for this task (not in `rcs/backend/`, not in the brief).
4. **CRLF line endings** — Windows write emitted CRLF. Git warned at `git add` time that it will normalize to LF on commit. Verified in commit: files stored as LF. Cosmetic only.
5. **Brief declared 10 files in the list but Step 8 also creates `tests/unit/__init__.py`** — 11 files were created. Matches the brief's Step 8 explicitly.

## Self-Review
- **Completeness:** All 11 files from the brief are created with verbatim contents; commit landed on `main` (no worktree, as authorized).
- **Quality:** Type hints preserved on all public functions (`get_settings`, `create_app`, `_lifespan`, `health`); `Literal["memory","sqlite"]` on `Settings.storage` matches the `Interfaces` contract in the brief. No `rcs` package name used (correctly `rcs_backend` with underscore).
- **Discipline:** Did not modify `rcs/rcs/`, `shared/`, `simulation/`, `rcs/tests/`, or `deploy/`. Only created files under `rcs/backend/`. No paraphrase / "improvement" of the brief.
- **Testing:** Ran `python -m pytest -v` in `rcs/backend/`. Result captured verbatim above. Did not mask the failure; did not "fix" the plan to make it pass.
