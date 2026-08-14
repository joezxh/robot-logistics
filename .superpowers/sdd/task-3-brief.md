# Task 3 Brief — /api/scenes/* endpoints

## Project Context

工程 `d:\projects\robot-logic\` Top 3 仿真模块。Task 1 完成 `scene_presets.py`（commit `2f6fa79`）。Task 2 完成 `Runtime.reset/load_scene/_scene_kpi` + `DeviceManager` + `SiteManager(seed=...)`（commit `ef9bcab`）。本 Task 注册 4 个 `/api/scenes/*` REST 端点 + 扩展 `device_type` 正则。

下游：Task 4 写 API 测试；前端 `useSceneAPI` composable（Task 6）。

## Files

- **Modify**: `d:\projects\robot-logic\simulation\backend\main.py`（仅此一个文件）

## Requirements

### Step 1: 扩展 `DeviceCreateRequest.device_type` 正则

找到原文件（约第 91~95 行），把正则扩展为：

```python
class DeviceCreateRequest(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=64)
    device_type: str = Field(
        ...,
        pattern="^(container_robot|loading_robot|agv|stacker|pallet_forklift)$",
    )
    name: str = Field(..., min_length=1, max_length=128)
    x: float = 0.0
    z: float = 0.0
```

### Step 2: 在 `/api/sites` 端点之后插入 4 个 scenes 端点

**位置**：在 `@app.delete("/api/sites/{site_id}", ...)` 函数定义**之后**插入（参考 main.py 当前结构，找到 delete_site 函数结束位置后插入）。

完整代码块：

```python
@app.get("/api/scenes", dependencies=[])
async def list_scenes():
    """List available scene presets plus currently active scene name."""
    from backend.services.scene_presets import list_scene_names
    return {
        "available": list_scene_names(),
        "current": runtime.current_scene,
    }


@app.post("/api/scenes/load/{name}", dependencies=[Depends(rate_limit_dep)])
async def load_scene(name: str):
    """Reset runtime and apply the named scene preset."""
    try:
        result = runtime.load_scene(name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return result


@app.get("/api/scenes/current", dependencies=[])
async def current_scene():
    """Return the active scene preset (or 404 if none loaded)."""
    from backend.services.scene_presets import get_scene
    if runtime.current_scene is None:
        raise HTTPException(status_code=404, detail="no scene is currently active")
    return get_scene(runtime.current_scene)


@app.get("/api/scenes/{name}/kpi", dependencies=[])
async def scene_kpi(name: str):
    """Compute KPI snapshot for the named scene."""
    from backend.services.scene_presets import get_scene
    try:
        get_scene(name)  # validate name
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return runtime._scene_kpi(name)
```

### Step 3: 启动后端并 curl 验证（Plan defect 修正）

**Plan 中此步的命令 `cd simulation/backend && python -m uvicorn backend.main:app` 不能直接运行**（包根是 `simulation/`，不是 `simulation/backend/`）。必须从 `simulation/` 目录启动。

执行步骤（用 PowerShell 等价命令）：

1. **后台启动 uvicorn**（从一个 terminal block）：

```powershell
python -c "import subprocess, time, sys, os; os.chdir(r'D:\projects\robot-logic\simulation'); sys.path.insert(0, '.'); p = subprocess.Popen(['python', '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE); time.sleep(4); print('PID:', p.pid); print('STDOUT:', p.stdout.read1(500).decode(errors='ignore') if p.stdout else 'n/a')"
```

如该命令复杂，可改用更直接的方法：**用 Python 子进程 + 时间等待**：

```python
python -c "import os, sys, subprocess, time, urllib.request, json; os.chdir(r'D:\projects\robot-logic\simulation'); sys.path.insert(0, '.'); p = subprocess.Popen(['python', '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8765'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT); time.sleep(4); import urllib.request; r = urllib.request.urlopen('http://127.0.0.1:8765/api/scenes'); print(r.read().decode()); r2 = urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765/api/scenes/load/pallet', method='POST')); print(r2.read().decode()[:200]); r3 = urllib.request.urlopen('http://127.0.0.1:8765/api/scenes/pallet/kpi'); print(r3.read().decode()); p.terminate()"
```

**期望输出（顺序）**：
- 第一行：`{"available":["pallet","box","bag"],"current":null}` 或类似
- 第二行：包含 `"scene": "pallet"` 字段
- 第三行：KPI 快照 dict

2. **测试 pallet_forklift 类型**：可以额外跑：

```python
python -c "import os, sys, subprocess, time, urllib.request, json; os.chdir(r'D:\projects\robot-logic\simulation'); sys.path.insert(0, '.'); p = subprocess.Popen(['python', '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8765'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT); time.sleep(4); body = json.dumps({'device_id':'test-fk','device_type':'pallet_forklift','name':'t','x':0.0,'z':0.0}).encode(); req = urllib.request.Request('http://127.0.0.1:8765/api/devices/register', data=body, headers={'Content-Type':'application/json'}, method='POST'); r = urllib.request.urlopen(req); print('status:', r.status, 'body:', r.read().decode()[:150]); p.terminate()"
```

期望：`status: 200 body: {"battery":100.0,...,"device_id":"test-fk",...}`

3. **错误路径**：

```python
python -c "import os, sys, subprocess, time, urllib.request; os.chdir(r'D:\projects\robot-logic\simulation'); sys.path.insert(0, '.'); p = subprocess.Popen(['python', '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8765'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT); time.sleep(4); 
try:
    urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765/api/scenes/load/nope', method='POST'))
except urllib.error.HTTPError as e:
    print('unknown scene status:', e.code, e.read().decode())
p.terminate()"
```

期望：`unknown scene status: 404 ...`

**注意**：端口 8765 用于避免与现有 Dashboard 端口冲突。`subprocess.Popen` 后必须 `p.terminate()` 避免端口占用。

### Step 4: 提交

```bash
cd d:/projects/robot-logic
git add simulation/backend/main.py
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): register /api/scenes endpoints + extend device_type enum"
```

## Acceptance Checklist

- [ ] `DeviceCreateRequest.device_type` 正则含 `pallet_forklift`
- [ ] 4 个端点已注册：`GET /api/scenes` / `POST /api/scenes/load/{name}` / `GET /api/scenes/current` / `GET /api/scenes/{name}/kpi`
- [ ] `GET /api/scenes` 返回 `{"available": [...], "current": null | "..."}`
- [ ] `POST /api/scenes/load/pallet` 返回 `{"scene": "pallet", "devices": [...], "sites": [...]}`
- [ ] `POST /api/scenes/load/nope` 返回 404
- [ ] `GET /api/scenes/current` 无激活场景时返回 404；加载后返回 ScenePreset
- [ ] `GET /api/scenes/pallet/kpi` 返回 KPI 字典（含 `throughput_per_hour` / `success_rate` / `scene`）
- [ ] `GET /api/scenes/nope/kpi` 返回 404
- [ ] `POST /api/devices/register` 接受 `device_type="pallet_forklift"` 返回 200
- [ ] 现有 19 个测试继续通过（不破坏 Dashboard）

## Global Constraints

- 仅修改 `simulation/backend/main.py`
- 端点路径严格按 plan 定义
- 错误处理用 `HTTPException` + 适当 status code
- 不要新增 Pydantic 模型（直接用 dict 即可）
- 提交后用 `git log -1 --stat` 确认仅 main.py 被修改

## Report Contract

将完整报告写入 `d:\projects\robot-logic\.superpowers\sdd\task-3-report.md`，包含：
1. 状态
2. commit hash（7 位）
3. Step 3 验证命令的实际输出（至少前 3 个 curl 等价命令的输出）
4. Acceptance checklist 勾选状态
5. 现有 19 个测试是否仍通过
6. concerns

返回仅含：状态 + commit + 1 行测试摘要 + concerns。