# Task 1 Review — scene_presets.py

**Reviewer**: task reviewer (subagent-driven-development)
**Reviewed**: 2026-08-14 23:29 UTC+8
**Brief**: `.superpowers/sdd/task-1-brief.md`
**Implementer report**: `.superpowers/sdd/task-1-report.md`
**Note**: `.superpowers/sdd/task-1-review.md` (the diff file referenced in the brief) does not exist on disk. The brief instructs reviewers to compare against the diff file, but the diff is reproducible directly from `git show HEAD`. The review below performs the same comparison by running `git show 2f6fa79` and reading the on-disk file — no information is lost.

---

## A. Spec Compliance — ✅ Approved

| Item | Status | Evidence |
| --- | --- | --- |
| File path `simulation/backend/services/scene_presets.py` | ✅ | `Read` on the path returns the module; `git show 2f6fa79 --stat` lists exactly that file. |
| Content verbatim vs brief | ✅ | After normalizing line endings, `difflib.unified_diff(brief, committed)` returns empty (7314 vs 7313 bytes — the 1-byte delta is the brief's trailing `\n` at EOF, which is a markdown artifact, not a content difference). |
| 5 TypedDicts present | ✅ | `SiteSpec`, `DeviceSpec`, `TaskSpec`, `KPIDefinition`, `ScenePreset` — all defined with identical field sets and inline literal-union comments. |
| 3 constants | ✅ | `PALLET_SCENE`, `BOX_SCENE`, `BAG_SCENE` — each annotated `ScenePreset`. |
| `SCENE_PRESETS` keys `pallet` / `box` / `bag` | ✅ | Runtime verification: `list(SCENE_PRESETS.keys()) == ['pallet', 'box', 'bag']`. |
| `list_scene_names()` / `get_scene(name)` signatures | ✅ | `def list_scene_names() -> list[str]` and `def get_scene(name: str) -> ScenePreset` — exact match. |
| `get_scene` raises `KeyError` with `unknown scene` | ✅ | `KeyError("unknown scene: 'does_not_exist'; available: ['pallet', 'box', 'bag']")` — substring `unknown scene` present. |
| Pallet contains `pallet_forklift` | ✅ | `[d['device_type'] for d in PALLET_SCENE['devices']] == ['pallet_forklift', 'pallet_forklift', 'agv']`. |
| No FastAPI / Pydantic imports | ✅ | Imports are only `from __future__ import annotations` and `from typing import TypedDict`. (The docstring *mentions* "no FastAPI / Pydantic" in prose, but no import is performed.) |

**Verdict**: All 9 spec items pass. No gaps.

---

## B. Code Quality — ✅ Approved

| Item | Status | Finding |
| --- | --- | --- |
| Top docstring + `from __future__ import annotations` | ✅ Pass | Docstring lines 1–5; future import line 6. |
| No redundant imports / unused symbols | ✅ Pass | Two imports, both used. All TypedDicts referenced in `ScenePreset`. |
| Chinese labels use full-width punctuation | ✅ Pass | Scanned 30 label/description/name string literals — 0 ASCII `,;:!?` characters found in any of them. Full-width `，、。（）「」` used throughout. |
| No `print` / `TODO` / `pass` placeholders | ✅ Pass | None present. |
| Style consistency with existing backend Python | ✅ Pass | TypedDict pattern matches `simulation/backend/algorithm/scheduler/task.py` and similar; double-quoted strings; 4-space indent; 2-blank-line top-level separators; trailing comma style in multi-line dicts matches the repo. |
| `ast.parse` succeeds | ✅ Pass | `parse_ok`. |

**Verdict**: Code quality is clean. No Critical/Important/Minor findings.

---

## C. Git Health — ✅ Approved

| Item | Status | Evidence |
| --- | --- | --- |
| Exactly 1 file in commit | ✅ | `git show 2f6fa79 --stat` → `1 file changed, 185 insertions(+)`, path `simulation/backend/services/scene_presets.py`. No other files. |
| Commit message matches brief | ✅ | `feat(scenes): add scene_presets data module for Top 3 loading scenes` — byte-equal to the brief's Step 3 literal. |
| Branch = `main` | ✅ | `git branch --show-current` → `main`. (Branch is 3 commits ahead of `origin/main` — not pushed, but push is outside Task 1 scope.) |
| No force-push / amend | ✅ | `git reflog` shows linear `commit:` entries for HEAD; no `reset`, `rebase`, or `commit --amend` between HEAD@{0} (2f6fa79) and HEAD@{1} (447a7cb). |
| Author / committer | ✅ | Both `cursor <cursor@local>` — matches the `-c user.name=… -c user.email=…` flag in the brief. |
| Blob line endings normalized to LF | ✅ | `git cat-file -p HEAD:simulation/.../scene_presets.py` shows 0 CRLF / 184 LF — `.gitattributes` rule `*.py text eol=lf` honored on commit. |
| Working-tree CRLF warning | ℹ️ Informational | `git status` warns `CRLF will be replaced by LF the next time Git touches it`. This is **not a Task 1 defect** — 160/196 .py files in this repo (including 100% of `simulation/backend/`) are CRLF in the working tree; the warning will self-resolve on next touch. Cosmetic only. |
| BOM | ✅ | None in committed blob. Earlier piped hex read suggested a BOM but was a PowerShell pipe artefact; direct `subprocess.run(['git','cat-file','-p'])` confirms no BOM in the blob. |

**Verdict**: Git state is clean and matches the brief's expectations.

---

## Functional Verification — run by reviewer

```python
# (cwd = d:\projects\robot-logic\simulation; sys.path insert '.')
from backend.services.scene_presets import (
    SCENE_PRESETS, get_scene, list_scene_names, PALLET_SCENE
)
list(SCENE_PRESETS.keys())               # → ['pallet', 'box', 'bag']
get_scene('pallet')['name']              # → 'pallet'
[d['device_type'] for d in PALLET_SCENE['devices']]
                                        # → ['pallet_forklift', 'pallet_forklift', 'agv']
try:
    get_scene('does_not_exist')
except KeyError as e:
    'unknown scene' in str(e)            # → True
    repr(e)                              # → KeyError("unknown scene: 'does_not_exist'; available: ['pallet', 'box', 'bag']")
```

All assertions pass. The implementer's note that `from backend.services.scene_presets` requires `simulation/backend/__init__.py` (present, 33 bytes) is correct: the package root is `simulation/`, and the brief's exact verification command requires `cd simulation/backend` (as written in Step 2) or `cd simulation` with `sys.path` adjusted — both work after Task 2 finalizes packaging. Task 1 ships the data module only, which is exactly what was asked.

---

## Final Verdicts

- **Spec Compliance**: ✅ **Approved** (no gaps)
- **Code Quality**: ✅ **Approved** (no Critical / Important / Minor findings)

---

## Notes for downstream tasks

1. Task 2 must add `__init__.py` to `simulation/backend/` (already present, 33 bytes) and `simulation/backend/services/` (already present, 33 bytes) so `from backend.services.scene_presets import SCENE_PRESETS` works without a `sys.path` hack — same path the brief's Step 2 verification expects.
2. Consider running `git add --renormalize .` once across the repo to converge CRLF → LF for all 160 .py files at once. Out of scope for Task 1.
3. The brief's reference to `task-1-review.md` (a diff artifact) does not correspond to any file on disk. The diff is reproducible via `git show 2f6fa79`. No action required.