# Microduck SDD Progress Ledger

Tracks per-task review state for the three Microduck plans:
- `docs/superpowers/plans/2026-09-03-microduck-p1-p2-backend.md` (8 tasks)
- `docs/superpowers/plans/2026-09-03-microduck-p3-frontend.md` (7 tasks)
- `docs/superpowers/plans/2026-09-03-microduck-p4-p5-training.md` (6 tasks)

Spec: `docs/superpowers/specs/2026-09-03-microduck-design.md` (commit `db58cb7`).
Branch: `feat/scene-map-management` (feature branch, not main/master).

## Pre-Flight Findings (recorded before Task 1)

- **PF-1 (conflict, resolved)**: plans specify regression checks with
  `pytest rcs_env/tests/...`, but `simulation/backend/pytest.ini` also collects
  `simulation/backend/tests/`. Measured: **no single env runs both suites** —
  * `rcs_sim_core/.venv` (mujoco 3.12.0 / gymnasium 1.3.0 / SB3 2.9.0 / pytest 9.1.1,
    **no fastapi**) → runs `rcs_env/tests/` only.
  * root `.venv` (fastapi 0.141.1, **no mujoco**) → runs `simulation/backend/tests/` only.
  Attempting the combined run in `rcs_sim_core/.venv` dies at collection:
  `services/security.py:13 ModuleNotFoundError: No module named 'fastapi'`
  (3 collection errors, exit 2).
  Resolution: regression baseline for Microduck = `rcs_env/tests/` under
  `rcs_sim_core/.venv` (**11 passed**). The API suite under `simulation/backend/tests/`
  is unrelated to Microduck (no API changes until the P3 SSE server, which is a new
  file) — verify it with the root venv only if a task touches `services/` or `api/`.
- **PF-2 (environment)**: `onnxruntime` is not installed — P5 Task 4 installs it.
  `pytest` was missing and has been installed into `rcs_sim_core/.venv`.
- **PF-3 (carried over from earlier ledgers)**: `httpx` must stay `<0.28` or
  `TestClient`-based tests break; stale `__pycache__` can produce ghost failures.
- **PF-4 (spec deviation)**: the approved spec §3 says "reuse MuJoCoEngine".
  Measured: `MuJoCoEngine.step()` writes `data.qpos` directly (teleport, not ctrl)
  and `_detect_robot_config()` injects a TCP site and reloads the MJCF — unusable
  for a freejoint biped. Plans add `FreeBaseMuJoCoEngine` instead (additive).

## Baselines (captured 2026-09-03)

- `python -m pytest rcs_env/tests/test_envs.py -q` → **11 passed**
- Full suite: `cd simulation/backend && python -m pytest -q` → (to capture at Task 1)

## Completed Tasks (15/21)

> **P1+P2+P3 complete (15 tasks).** Verified: `pytest rcs_env/tests/` → 24 passed
> (11 baseline env tests + 13 Microduck-specific); frontend vitest 110 passed; vue-tsc clean.
> Next: P4/P5 Training (6 tasks).

| # | Plan | Task | Commit(s) | Status |
|---|------|------|-----------|--------|
| 1 | P1+P2 | vendor 7 MJCF variants + 43 STL meshes + asset test | 375a26b | ✅ assets present, asset test pass, joint-order test now active (passes); baseline 11 still pass |
| 2 | P1+P2 | RobotType.MICRODUCK enum + get_all() | (this commit) | ✅ test_robot_type.py: MICRODUCK.value=="Microduck", in get_all() |
| 3 | P1+P2 | microduck_cfg.py contract + variant registry | (this commit) | ✅ POLICY_JOINTS, HOME_POSE, VARIANTS(7), build_microduck_obs, policy_action_to_motor_targets, home_pose_vector, quat_wxyz_to_rot |
| 4 | P1+P2 | 14→15 slot mapping tests (impl in T3) | committed | ✅ 3 contract tests green |
| 5 | P1+P2 | FreeBaseMuJoCoEngine (ctrl-driven freejoint) | (this commit) | ✅ loads walk (nq21/nu14/nv20), freejoint valid post-step, ctrl converges joints to home |
| 6 | P1+P2 | MicroduckEnv (61 obs/14 act, reward, term) | (this commit) | ✅ 4 env tests; gyro/gravity unit, home-aligned blocks, 5-tuple step, fall termination. Deviations: gravity normalized (match contract); MIN_TRUNK_HEIGHT 0.07 (model stands ~0.099 m); home_pose_vector skips passive wheel joints (rollers) |
| 7 | P1+P2 | gym ids rcs/microduck-*-v0 | (this commit) | ✅ register_envs + package exports; 7 variant ids resolvable |
| 8 | P1+P2 | rollout + twin smoke script | committed | ✅ run smoke: 2x walk obs(61)/act(14), random rollout runs w/o error. telemetry wiring deferred to P5 (sink constructed, not fed by random_rollout) |
| 9 | P3 | MjcfLoader STL meshes | committed | ✅ MjcfLoader.microduck.spec.ts (STL + freejoint, 3 tests); loadMesh extension-aware; meshKey; freejoint filter+6DOF |
| 10 | P3 | MjcfLoader freejoint 6-DOF | committed | ✅ JointNode.dof/freejoint; setFreeJointPose; plan bugs fixed: freejoint tag not caught by joint filter; setFreeJointPose quaternion order (fromArray x,y,z,w) |
| 11 | P3 | microduckQpos.ts viewer mapping | committed | ✅ 2 tests; qpos(21) -> {freeJoint[7], joints[14]} |
| 12 | P3 | SceneMicroduck.vue viewer | committed | ✅ Three.js viewer; qpos identity-init fix (qw=1); SSE /sim/stream toggle |
| 13 | P3 | register Microduck scene tab | committed | ✅ ScenesPage + SceneStage; load() skipped for microduck (no backend scene) |
| 14 | P3 | SSE qpos stream server + vite /sim proxy | committed | ✅ rcs_env/serve/sse_qpos.py (stdlib) + 1 test; vite proxy /sim -> 8110 |
| 15 | P3 | verification (vitest + vue-tsc + build) | committed | ✅ vitest 110 passed; vue-tsc --noEmit clean; vite build OK (dist/ bundled) |
| 16 | P4+P5 | MicroduckEnv velocity-command sampling | (this commit) | ✅ T1: cmd_vx/vy/vyaw ranges + cmd_period; `_sample_command`/`_step_command`; reset `_n_steps`=1; `config.robot_type=MICRODUCK`; 2 new tests (nonzero cmd + 13-slot block) |
| 17 | P4+P5 | PPO training entry `train_microduck.py` | (this commit) | ✅ T2: SB3 PPO train/eval/export CLI (`--total-timesteps`,`--export`,`--policy`,`--out`); 2048-step smoke saved `_smoke/md.zip` |
| 18 | P4+P5 | digital-twin telemetry wired into rollout | (this commit) | ✅ T3: `DigitalTwinWrapper` around sub-env in `microduck_rollout`; 68 telemetry records on smoke |
| 19 | P4+P5 | digital-twin telemetry tests | (this commit) | ✅ T4: `test_digital_twin.py` — push / forward-to-sink round-trip |
| 20 | P4+P5 | ONNX export/inference bridge | (this commit) | ✅ T5: `rcs_env/onnx/microduck_onnx.py` `export_microduck_onnx` (deterministic actor MLP, opset13) + `MicroduckOnnxPolicy.predict`; `onnxruntime` dep; matches torch within tol |
| 21 | P4+P5 | SSE server `--policy` + ONNX playback | (this commit) | ✅ T6: `sse_qpos.make_server` accepts `--policy` (.onnx/.zip); wrapped env emits digital-twin telemetry into sink (62 records on smoke); README run note |

## Pending Tasks (0)

P1+P2 backend: ✅ all 8 committed
P3 frontend: ✅ all 7 committed
P4+P5 training: ✅ all 6 committed (this session)

### P4+P5 deviations from plan (intentional)
- Plan named the SSE server `rcs_env/serve/microduck_stream.py`; implementation lives in
  existing `rcs_env/serve/sse_qpos.py` (P3 T6) extended with `--policy` — no new file.
- Plan named the ONNX policy `rcs_env/envs/microduck_policy.py` (`OnnxPolicy`);
  implementation is `rcs_env/onnx/microduck_onnx.py` (`MicroduckOnnxPolicy`) so the
  `onnx/` package owns all export/inference code.
- ONNX export exports only the deterministic actor MLP (`_ActorMean`) — torch dynamo
  exporter fails on the `Normal` action distribution's data-dependent guard.
- SSE server wraps the env in `DigitalTwinWrapper` so the `sink` actually receives
  telemetry (previously the sink was constructed but never fed). `QposHandler` reads
  `env.unwrapped.engine`.

---

# Top 3 Simulation SDD Progress Ledger

Tracks per-task review state for plan `docs/superpowers/plans/2026-08-14-top3-simulation-plan.md`.

## Completed Tasks (17/17)

| # | Task | Commit(s) | Status |
|---|------|-----------|--------|
| 1 | scene_presets.py | `2f6fa79` | ✅ Spec+Quality, review clean |
| 2 | DeviceManager + Runtime.reset/load_scene | `ef9bcab` | ✅ Spec+Quality, review clean |
| 3 | /api/scenes endpoints | `2d23310` | ✅ Spec+Quality, review clean (minor: cosmetic 404 quote) |
| 4 | pytest for presets/runtime/api | `1a49897` | ✅ Spec+Quality, 19 new + 19 existing pass |
| 5 | Vue Router + /scenes entry | `e734c47` | ✅ Spec+Quality, vue-tsc 0 new errors |
| 6 | useSceneAPI composable | `ed928da` | ✅ vue-tsc 0 new errors |
| 7 | useSceneStage state machine | `c5ef9d3` | ✅ vue-tsc 0 new errors |
| 8 | useSceneKPI composable | `caff84c` | ✅ vue-tsc 0 new errors |
| 9 | PalletForklift Three.js class | `474481f` | ✅ vue-tsc clean |
| 10 | BoxGripper + BagGripper | `8d5b2a5` | ✅ vue-tsc clean |
| 11 | ScenesPage.vue (top route + Tab) | `0600eda` | ✅ vue-tsc 0 new errors |
| 12 | SceneStage.vue (5-panel framework) | `4d2f126` + `f4b4144` | ✅ vue-tsc 0 new errors |
| 13 | ScenePallet.vue | `d0f2c09` | ✅ vue-tsc 0 new errors |
| 14 | SceneBox.vue | `3fd1757` | ✅ vue-tsc 0 new errors (also adds LoaderRobot.addEndEffector) |
| 15 | SceneBag.vue | `07ff37e` | ✅ vue-tsc 0 new errors |
| 16 | vitest for useSceneAPI + useSceneStage | `69d143f` | ✅ 6 tests pass |

## Pending Tasks (1)

- Task 17: E2E browser verification (**manual**, requires user browser interaction)

## Final Test Status

- **Backend pytest**: 108 passed (including 19 new scene tests + 89 existing tests)
- **Frontend vitest**: 6 passed (2 test files for useSceneAPI + useSceneStage)
- **vue-tsc**: 0 new errors introduced by any Task; 1 pre-existing `WarehouseScene.vue:122` baseline error remains (out of scope)

## Minor Findings Roll-up

- Task 3 Minor-1: `str(exc)` 产生双引号转义（cosmetic，404 错误响应路径），客户端可正常 JSON.parse。不阻塞。
- Task 5: Dashboard = App.vue 是临时方案（plan 缺 DashboardPage 拆分 Task），不阻塞。如需要后续 PR 拆分。
- Task 14: LoaderRobot.addEndEffector 同时随 Task 14 commit 提交（plan defect 修复），仅 4 行方法。
- Task 16: vitest.config.ts 因 jsdom env required 添加；commit `c99849f` 因外部 staged 文件污染被 reset → 重新 commit 为 `69d143f`（更干净）。

## Plan Defects Documented

- `plan-defect-py-import.md`: plan 中 `cd simulation/backend && python -c "from backend..."` 验证命令路径错误（包根是 simulation/）。已用 `os.chdir + sys.path.insert` 修正。
- `plan-gap-dashboard-split.md`: plan 缺 DashboardPage 拆分 Task（App.vue 既是布局又是路由叶子）。建议后续 PR。
- Task 14: LoaderRobot.addEndEffector 缺失（`?.` optional chaining 不绕过 TS2339）。已在 commit 中修复。

---

# Top 3 RCS + Robot-App SDD Progress Ledger

Tracks per-task review state for plan `docs/superpowers/plans/2026-08-14-top3-rcs-robotapp-plan.md`.

## Completed Tasks (19/19)

| # | Task | Commit(s) | Status |
|---|------|-----------|--------|
| 1 | CommandType.EXECUTE_TASK + test | `b95c66a` | ✅ Spec+Quality |
| 2 | ForkliftSpec + DualArmLoaderSpec | `8c76e4e` | ✅ Spec+Quality |
| 3 | ForkliftController (3 PID) | `0e4f00e` | ✅ Spec+Quality |
| 4 | DualArmLoaderController (双 PD) | `81db9eb` | ✅ Spec+Quality |
| 5 | MQTT Forklift + Loader adapters | `3beadff` | ✅ Spec+Quality |
| 6 | Top3PresetManager | `209a967` | ✅ Spec+Quality |
| 7 | RCS test suite (full pytest) | `8bbc0fc` + Batch B | ✅ pytest.ini + conftest bootstrap |
| 8 | Robot-App 工程骨架 | `e433f5a` | ✅ |
| 9 | robot_arm_hal (HAL + 双模式) | `ed45a3e` | ✅ |
| 10 | ForkliftDriverNode + GripperDriverNode | `7a49bf5` | ✅ |
| 11 | mqtt_bridge | `17eaa0f` | ✅ |
| 12 | 通用 FSM 基类 | `b14f937` | ✅ (24 tests) |
| 13 | PalletTaskExecutor | `1fe374f` | ✅ |
| 14 | BoxTaskExecutor | `9507e9f` | ✅ |
| 15 | BagTaskExecutor | `82614c5` | ✅ |
| 16 | 3 motion planners | `69d7353` | ✅ (4 tests) |
| 17 | robot_perception | `42e1d13` | ✅ |
| 18 | E2E smoke test placeholder | `cd27e34` | ✅ 3 pass + 1 skip (ROS2 env) |
| 19 | README + OPERATIONS docs | (this commit) | ✅ |

## Final Test Status

- **All-Python-test (228 from full repo)**: 230 passed, 1 skipped (`robot-app/tests/e2e/test_top3_e2e.py::test_robot_arm_hal_factory_importable` — only importable when sourced via ROS2 `install/setup.bash`)
  - `rcs/tests/unit/` — 43 (Top 3 RCS Tasks 1-4 + existing)
  - `rcs/tests/mqtt/` — 14 (existing publisher/subscriber)
  - `rcs/tests/integration/` — 7 (existing lifecycle)
  - `simulation/backend/tests/` — 80 (including 19+7+8 from Top 3 simulation)
  - `rcs/tests/{unit,mqtt}/` newly added by Batch B — 17 (10 MQTT adapter + 7 Top3 presets)
  - `vla-training/tests/` — 40 (existing, also passes)
- **Frontend vitest**: 6 passed
- **vue-tsc**: 0 new errors (1 pre-existing `WarehouseScene.vue:122` baseline)

### Earlier pre-existing failures — RESOLVED

Prior to the dependency fix the suite reported ~30 failures across `rcs/tests/integration/` and `simulation/backend/tests/test_*.py`. Root cause was two-layered:

1. **`httpx==0.28.1` was installed** despite `rcs/requirements.txt` and `simulation/backend/requirements.txt` pinning `httpx==0.25.0`. Newer httpx removed the `app=` kwarg accepted by `httpx.Client`, which `starlette 0.27 TestClient` still passes — producing `TypeError: Client.__init__() got an unexpected keyword argument 'app'` for every TestClient-based test.
2. Stale `__pycache__/*.pyc` files referenced the old `D:\projects\robot-logic\backend/...` layout (pre-rename to `simulation/backend/`), so even after restoring httpx, pytest showed ghost failures like `D:\projects\robot-logic\backend\tests\test_api.py:63: assert False`.

Fix: `python -m pip install "httpx==0.25.0"` then `find . -name __pycache__ -type d -exec rm -rf {} +` (via the equivalent Python pathlib loop). All 230 tests now pass with no source code modifications.

**Important for ops/CI**: a separate `unstructured-client` dependency pinned `httpx>=0.28.1`, so a naive `pip install -r requirements.txt` against a fresh environment may re-pull httpx 0.28 and re-break TestClient. Recommendation: pin `httpx<0.28` in both requirements files for this branch.

## Minor Findings / Adaptations Roll-up

- Batch A (Tasks 1-4): plan-verbatim code used 2-level imports `from rcs.rcs.X`. Project convention is 1-level `from rcs.X` (matches `rcs/tests/unit/test_arm_controller.py` etc.). Commit `8bbc0fc` switched all Batch A tests to 1-level, fixed `rcs/conftest.py` and `rcs/pytest.ini` for sys.path bootstrap.
- Batch B (Tasks 5-7): Task 5 needed `task_type`/`parameters` fields added to `Command` dataclass (planned for Task 5, deferred from Batch A). Test imports follow 1-level convention. Compatibility shim in `rcs/tests/unit/conftest.py` simplified to no-op stub.
- Task 18: ROS2 import (`robot_arm_hal.hal_interface`) uses `pytest.importorskip` so it skips cleanly when ROS2 env isn't sourced (e.g., plain CI). Becomes a real assertion inside the Docker stack as the plan documents.
- Task 19: README was already complete (added by Task 8 subagent at `e433f5a`); OPERATIONS.md / OPERATIONS-ZH.md got the planned "Top 3 deployment" appendices.

## Plan Defects Documented

- Tasks 1-4 verbatim code uses `from rcs.rcs.X import Y` which only resolves when `rcs` is `pip install -e .`. Project convention (verified against existing `test_arm_controller.py`) is 1-level `from rcs.X import Y`. Fixed in commit `8bbc0fc`. Plan should have noted this.
- `Command.task_type`/`parameters` fields are listed in Task 5 but the verbatim Task 5 adapter code expects them on the dataclass already. Batch A's monkey-patch shim (`rcs/tests/unit/conftest.py`) bridged the gap; Batch B added the fields natively and removed the shim.
