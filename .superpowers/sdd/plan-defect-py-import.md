# Plan Defect: Verification Commands

## Issue

`docs/superpowers/plans/2026-08-14-top3-simulation-plan.md` 的多个 Task 中，Python 验证命令形如：

```bash
cd d:/projects/robot-logic/simulation/backend
python -c "from backend.services.X import Y"
```

**此命令在 PowerShell/Windows 上不可用**，因为：
- `backend` 包的根是 `simulation/`（不是 `simulation/backend/`）
- `simulation/backend/__init__.py` 是空文件（PEP 420 implicit namespace 不被普遍启用）
- 必须从 `simulation/` 目录运行 python，且 `simulation/` 在 `sys.path` 中

## Fix Template (for all future Task briefs)

```bash
python -c "import os, sys; os.chdir(r'D:\projects\robot-logic\simulation'); sys.path.insert(0, '.'); from backend.services.MODULE import X; print(X)"
```

或在 `simulation/` 目录下运行：
```bash
cd d:/projects/robot-logic/simulation
python -c "from backend.services.MODULE import X; print(X)"
```

## Affected Tasks

- Task 1: Step 2 验证命令（已通过 reviewer 用正确方式验证通过）
- Task 2: Step 4 验证命令（需修正）
- Task 3: Step 3 curl 验证（**正常**，与本缺陷无关）
- Task 4: Step 4 / Step 5 pytest 命令（**需修正**：需在 `simulation/` 目录运行，或设置 `PYTHONPATH=simulation`）
- 后续所有使用 `from backend...` 的命令

## Status

- 已在 brief 模板中标注
- 不影响 Task 1 的 review 结论（Task 1 reviewer 已用正确命令验证通过）
