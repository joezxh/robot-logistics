# robot-logic × robot-control-stack (RCS) 对齐改造报告

**日期**：2026-08-20
**范围**：`rcs` / `robot-app` / `vla-training` / `simulation` 四个子工程对齐 RCS 标准
**数据来源**：`robot-control-stack` 文档 + 源码（`python/rcs`、`extensions/`、CMake 构建体系）

---

## 1. 目标与总体架构

将四个子工程重新定位，使其分别与 RCS 的能力层一一对应，并通过**共享数据契约**
（`shared/python/robot_contracts`）实现无缝集成：

| 子工程 | RCS 对标 | 核心职责 |
|--------|----------|----------|
| `simulation` | `python/rcs` + `extensions/` | MuJoCo/Pinocchio 物理引擎、Gymnasium `Env` + Wrapper 栈、OMPL 运动规划、硬件扩展注册 |
| `rcs` | app / 运行时控制层 | 统一 `RobotType` 注册表、HAL 抽象、世界系↔基座系 `Pose`、控制模式 |
| `robot-app` | teleop / inference / imitation | 物流 FSM → `TaskWrapper` 任务、VLA 推理、遥操作 |
| `vla-training` | training / datasets | 数据集预处理 → 训练 → 模型导出（含 `robot_type` 标签） |

依赖方向严格单向：`vla-training`/`robot-app` → `simulation` → `shared`；所有子工程 → `shared`。

---

## 2. 共享根契约（Step 1）

**落点**：`shared/python/robot_contracts/kinematics.py` + `shared/contracts/`

- `Pose`：6D 位姿，平移(米) + 四元数 **[x,y,z,w]**（xyzw，RCS 一致）；提供 `wxyz`↔`xyzw` 互转、RPY↔四元数、SE(3) 复合 `(@)` 与 `inverse()`。
- `RobotType`：FR3/Panda/UR5e/XArm7/SO100/SO101/Yam + ARM/AGV/STACKER（统一 RCS 标准臂与 robot-logic 物流形态）。
- 世界系↔基座系转换：`to_pose_in_world_coordinates` / `to_pose_in_robot_coordinates`（RCS `MjORobot` 对齐）。
- 语言无关规范：`shared/contracts/pose.schema.json` + `pose.md`。
- **验证**：`shared/python/tests/test_kinematics.py`（7 项，全过）。

---

## 3. simulation 对齐（Step 2）

**落点**：`simulation/backend/rcs_env/`（新增，不改动既有逻辑仿真）

- `engine.py`：`PhysicsEngine` 抽象 + `LogicEngine`（复用既有设备仿真）+ `MuJoCoEngine`（RCS `rcs.sim` 对齐，可选依赖）；`build_engine` 工厂在 MuJoCo 可用时优先。
- `ompl.py`：`MjOMPL` 接口对齐 RCS（`plan` / `plan_SE3` / `solve` / `collision_free` / `ik` / `set_joint_limts`）；纯 Python RRT / RRTConnect / RRT* / PRM 采样规划器。
- `envs/`：`SimEnv`（Gymnasium env）、`SimEnvCreator`/`SimEnvCreatorConfig`（RCS 工厂）、`configs.py`（场景配置）、`scenes.py`、`wrappers.py`（`RobotWrapper`/`GripperWrapper`/`CameraSetWrapper`/`TaskWrapper`）。
- `extensions/`：硬件扩展注册表（RCS `extensions/` 包模式），内置 container_robot/loading_robot/agv/stacker/pallet_forklift + 传感器。
- 新增 `/api/rcs-env` HTTP 路由，复用既有服务端口。
- **验证**：`simulation/tests/test_rcs_env.py`（5 项，全过）；全量 113 项无回归。

---

## 4. rcs 对齐（Step 3）

**落点**：`rcs/rcs/state/`、`rcs/rcs/hal/`、`rcs/rcs/control.py`（新增）

- `state/profile.py`：`DeviceProfile` 增加 `robot_type`（`RobotType`）+ `base_pose_in_world`（`Pose`），`__post_init__` 自动从形态派生。
- `state/pose.py`：本地 `Pose6D`（wxyz）桥接到共享 `Pose`（xyzw），保留 legacy 适配。
- `hal/protocol.py` + `hal/sim.py`：HAL 协议新增 `base_pose()`，对齐 RCS 世界系查询。
- `control.py`（新增）：`ControlMode`（关节/笛卡尔/TQuat/相对）+ 世界系↔基座系指令转换 `command_in_world`/`command_in_robot`/`ee_pose_in_world`。
- `registry.py`：新增 `robot_type()` / `base_pose()` 访问器，从配置解析 `RobotType`。
- **验证**：`rcs/tests/unit/test_rcs_alignment.py`（8 项，全过）；全量 125 项无回归。

---

## 5. robot-app 对齐（Step 4）

**落点**：`robot-app/rcs_layer/`（新增，纯 Python 可单测）

- `tasks/`：`LogisticsTask` 基类实现 RCS `TaskWrapper` 协议（`reset`/`reward`/`done`/`progress`）；`PalletTask` 封装既有 `PalletTaskExecutor` FSM，并在无 ROS2 时回退到内置 `_ScriptedExecutor`，保证仿真可运行。
- `vla/`：`load_policy` / `ScriptedPolicy`（RCS `inference` 对齐），预留真实 VLA 权重加载扩展点。
- `teleop/`：`KeyboardAdapter` / `SpaceMouseAdapter`（RCS `teleop` 对齐）。
- **验证**：`robot-app/tests/rcs_layer/test_rcs_layer.py`（4 项，全过）。

---

## 6. vla-training 对齐（Step 5）

**落点**：`vla-training/src/vla_training/`

- `data/collector.py`：`SimulationCollector` 从 stub 升级为真实实现——在 `simulation` 的 `SimEnv` 中由 `robot-app` 的策略/遥操作采集演示，关闭「仿真↔训练」数据环路。
- `eval/evaluate.py`：`evaluate_closed_loop` 从 stub 升级为在 `SimEnv` + `robot-app` 任务上跑策略、统计成功率（RCS `inference` 评估对齐）。
- `export/to_inference.py`：`InferenceManifest` 增加 `robot_type` 字段，`validate_against_robot` 增加类型校验，确保权重与机器人强绑定。
- **验证**：`vla-training/tests/test_integration_rcs.py`（跨子工程集成，2 项，全过）；全量 42 项无回归。

---

## 7. 统一构建与 Monorepo 契约（Step 6）

- `pyproject.toml`（根）：统一 ruff/black/isort 工具配置（RCS 的 clang-format/lint 等价物）。
- `Makefile`（根）：`install` / `lint` / `format` / `test` / `test-integration` 统一门禁。
- `robot-logic.code-workspace`：纳入 `shared`、配置 `python.analysis.extraPaths`、保存时 ruff 格式化。
- `CONTRACT.md`：跨子工程集成契约（位姿/RobotType/数据流/依赖方向）。
- 各子工程补充 `pytest.ini` 锚定配置，避免根 pyproject 冲突。

---

## 8. 测试结果汇总

| 子工程 | 测试命令 | 结果 |
|--------|----------|------|
| `shared/python` | `pytest tests` | 7 / 7 ✓ |
| `rcs` | `pytest tests` | 125 / 125 ✓ |
| `simulation/backend` | `pytest tests` | 113 / 113 ✓ |
| `robot-app` | `pytest tests` | 10 / 10 ✓ |
| `vla-training` | `pytest tests` | 42 / 42 ✓ |
| **跨子工程集成** | `vla-training tests/test_integration_rcs.py` | 2 / 2 ✓ |

---

## 9. 后续建议（未执行，供参考）

1. **MuJoCo MJCF 模型**：为 ARM/AGV/STACKER 建立 MJCF，启用 `MuJoCoEngine` 高保真动力学。
2. **OMPL 原生加速**：当 `pip install ompl` 可用时，将 `MjOMPL` 后端切换为原生 OMPL。
3. **VLA 训练闭环**：将 `vla-training/training` 接入真实模型（torch/onnxruntime）替换 `ScriptedPolicy`，跑通 imitation → RL 全流程。
4. **硬件扩展包**：将 `rcs`/`simulation` 的真实设备驱动以 RCS `extensions/` 包模式独立构建。
5. **CI 接入**：在 Monorepo 中加入 GitHub Actions，复用 `Makefile` 门禁。

---

## 免责声明

本报告由 AI 基于 `robot-control-stack` 文档与源码、以及 `robot-logic` 现有代码自动生成，
用于改造方案对齐参考。实际部署请结合真实硬件与专业工程评审。
