# robot-logic 跨子工程集成契约（对齐 robot-control-stack）

本文件是 robot-logic 四个子工程（`rcs` / `robot-app` / `vla-training` / `simulation`）
无缝集成的**唯一权威契约**。所有跨子工程的数据流都通过这些约定，确保具备与
`robot-control-stack`（RCS）同等甚至更优的系统能力。

## 1. 共享根契约：`shared/python/robot_contracts`

所有子工程**只能**通过 `robot_contracts` 交换位姿与机器人类型，禁止各自定义
四元数/坐标系：

| 概念 | 定义 | 来源 |
|------|------|------|
| `Pose` | 6D 位姿，平移(米) + 四元数 **[x,y,z,w]** (xyzw) | `kinematics.py` |
| 世界系(world) | 右手系 x前/y左/z上 | `kinematics.py` |
| `RobotType` | FR3/Panda/UR5e/XArm7/SO100/SO101/Yam + ARM/AGV/STACKER | `kinematics.py` |
| 坐标转换 | `to_pose_in_world_coordinates` / `to_pose_in_robot_coordinates` | RCS `MjORobot` 对齐 |
| MuJoCo 约定 | `Pose.wxyz` / `Pose.from_wxyz()` 互转 [w,x,y,z] | RCS qpos 对齐 |

JSON 规范见 `shared/contracts/pose.schema.json`，语义见 `shared/contracts/pose.md`。

## 2. 子工程角色再定位（对齐 RCS）

| 子工程 | RCS 对标 | 职责 |
|--------|----------|------|
| `simulation` | `python/rcs` + `extensions/` | MuJoCo/Pinocchio 物理引擎、Gymnasium `Env` + Wrapper 栈、OMPL 运动规划、硬件扩展注册 |
| `rcs` | app / 运行时控制层 | 统一 `RobotType` 注册表、HAL 抽象、世界系↔基座系 `Pose`、控制模式（关节/笛卡尔/TQuat/相对） |
| `robot-app` | teleop / inference / imitation | 物流 FSM 封装为 RCS `TaskWrapper` 任务、VLA 推理、遥操作 |
| `vla-training` | training / datasets | 数据集预处理 → 训练 → 模型导出，向 `robot-app` 提供策略 |

## 3. 数据流（端到端闭环）

```
遥操作/脚本策略 (robot-app.teleop / vla.policy)
        │ action
        ▼
simulation.rcs_env.SimEnv  (Gym env, RCS 物理/规划)
        │ obs = {state, rgb, depth}  (CameraSetWrapper)
        ▼
vla-training.SimulationCollector  (录制演示, SourceType.SIMULATION)
        │ 数据集
        ▼
vla-training.train  →  export.inference_manifest (含 robot_type)
        │ 策略权重 + 归一化统计 + robot_type
        ▼
robot-app.rcs_layer.vla.load_policy  (推理, RCS inference 对齐)
        │ action
        ▼
rcs 控制平面  →  仿真/真实硬件 (HAL)
```

## 4. 集成门禁

- 统一工具链：`pyproject.toml`（ruff/black/pytest）+ `Makefile`（`install/lint/format/test`）。
- 任一子工程修改 `Pose`/`RobotType` 语义，必须同步 `shared/contracts/` 与 `tests`。
- 跨子工程集成由 `vla-training/tests/test_integration_rcs.py` 端到端验证。

## 5. 依赖方向（单向，禁止环）

```
vla-training ──▶ simulation ──▶ shared (robot_contracts)
     │              │
     └──▶ robot-app ┘
所有子工程 ──▶ shared (唯一共享)
```
