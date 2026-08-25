# RCS 仿真能力迁移计划（robot-control-stack → robot-logic/simulation）

> 目标：把 `robot-control-stack`（`d:\projects\github\robot-control-stack`，以下简称 RCS）的全部仿真能力迁移到
> `robot-logic/simulation`（`d:\projects\robot-logic\simulation`，以下简称 RL-SIM）。
> 依据 `robot-control-stack/simulation.md` 罗列的能力清单。
>
> 用户决策：
> 1. **混合模式**：C++ MuJoCo 内核（来自 RCS `src/sim` + pybind11 绑定）接入 + Python 层补齐。
> 2. **完整覆盖**：simulation.md 中全部 25+ 能力。
> 3. **资产复制**：把 RCS `assets/` 复制到 RL-SIM 自包含。

---

## 0. 现状对照（迁移前）

### RL-SIM 已有（需要保留/扩展的“镜像”）
| 模块 | 文件 | 说明 |
|---|---|---|
| 引擎抽象 | `backend/rcs_env/engine.py` | `PhysicsEngine` / `MuJoCoEngine` / `LogicEngine` / `build_engine` |
| 规划器 | `backend/rcs_env/ompl.py` | 纯 Python RRT/RRT-Connect/PRM（`MjOMPL`） |
| Gym 环境 | `backend/rcs_env/envs/base.py` | `SimEnv`（reset/step/obs/info） |
| 工厂 | `backend/rcs_env/envs/creator.py` | `SimEnvCreator` / `SimEnvCreatorConfig` |
| 配置/场景 | `backend/rcs_env/envs/configs.py`, `scenes.py` | `EnvConfig` / `Scene` |
| 包装器 | `backend/rcs_env/envs/wrappers.py` | `RobotWrapper` / `GripperWrapper` / `CameraSetWrapper` / `TaskWrapper` |
| 扩展注册 | `backend/rcs_env/extensions/__init__.py` | 物流设备注册表 |
| 渲染 | `backend/rcs_env/renderer.py` | 占位 `CameraRenderer`（非 MuJoCo offscreen） |
| 测试 | `backend/tests/test_rcs_env.py`, `test_renderer.py` | pytest 骨架 |

### RCS 有、RL-SIM 缺（必须补齐，来自 `simulation.md`）
- C++ 内核：`Sim` / `SimRobot` / `SimGripper` / `SimTilburgHand` / `Renderer` / `SimCameraSet` / `GuiServer`/`GuiClient` 共享内存桥接
- pybind11 绑定 + 编译产物 `rcs._sim`（或 `rcs.sim`）
- Python 高层：`composer.py`（`ModelComposer`）/ `egl_bootstrap.py` / `replayer.py` / `camera/sim.py`
- `SimEnv` 完整能力：多机、`ControlMode`、`RelativeTo`、IK 收敛步进、回调系统、`StorageWrapper`/`DigitalTwin`、相机 RGB+Depth 帧
- 资产：`assets/robots` / `assets/grippers` / `assets/objects` / `assets/scenes` / `assets/cameras`

---

## 1. 总体架构（迁移后）

```
robot-logic/simulation/
├── backend/
│   ├── rcs_sim_core/                # 新增：C++ 内核 + pybind（来自 RCS src/sim + src/pybind）
│   │   ├── include/rcs/sim/         # *.h（Sim.h, SimRobot.h, SimGripper.h, SimTilburgHand.h,
│   │   │                           #        camera.h, renderer.h, gui.h）
│   │   ├── src/sim/                 # *.cpp
│   │   ├── src/pybind/              # rcs.cpp + CMakeLists.txt + gen_mujoco_bindings.sh
│   │   ├── CMakeLists.txt
│   │   └── pyproject.toml          # 用 scikit-build 编译出 rcs._sim 轮子
│   ├── rcs_env/                     # 现有：改为“薄适配层”，转发到 rcs_sim_core + 补齐 Python
│   │   ├── engine.py                # MuJoCoEngine 改为包装 rcs._sim.Sim
│   │   ├── composer.py              # 新增：ModelComposer（来自 RCS）
│   │   ├── egl_bootstrap.py         # 新增
│   │   ├── replayer.py              # 新增：StorageWrapper + 回放
│   │   ├── camera.py                # 新增：SimCameraSet Python 封装（来自 RCS camera/sim.py）
│   │   ├── gui.py                   # 新增：GuiClient 包装
│   │   ├── envs/                    # 扩展 base/creator/configs/scenes/wrappers
│   │   │   ├── base.py              # 加 ControlMode / RelativeTo / 多机 / 相机 obs
│   │   │   ├── creator.py           # 加 SimEnvCreatorConfig 全字段（机器人/夹爪/相机/物体）
│   │   │   ├── gripper.py           # 新增：SimGripperWrapper（抓握检测）
│   │   │   ├── hand.py              # 新增：HandWrapperSim（灵巧手）
│   │   │   ├── storage.py           # 新增：StorageWrapper（Parquet/DuckDB）
│   │   │   ├── digital_twin.py      # 新增：DigitalTwin
│   │   │   ├── configs.py           # 补全所有 RCS env（fr3/panda/ur5e/xarm7/so101/yam + 灵巧手）
│   │   │   └── scenes.py            # 补全
│   │   └── extensions/              # 保留：物流扩展 + 注册 RCS 机器人
│   ├── assets/                      # 新增（复制自 RCS assets/）
│   │   ├── robots/ grippers/ objects/ scenes/ cameras/
│   └── tests/                       # 扩展 pytest 覆盖新能力
```

**依赖关系**：`rcs_env` 不再自己实现物理，而是 `import rcs_sim_core`（编译后的 C++ 扩展）。`engine.MuJoCoEngine` 持有 `rcs_sim_core.Sim`，把 Gym 动作翻译成 `SimRobot.set_target` 等调用。

---

## 2. 分阶段执行计划

### Phase 0 — 资产与 C++ 内核落地（基础设施）
**P0.1 复制资产**
- `copy d:\projects\github\robot-control-stack\assets\* → d:\projects\robot-logic\simulation\backend\assets\*`
- 保留目录结构：`robots/ grippers/ objects/ scenes/ cameras/`
- 在 `backend/pyproject.toml` 或 `backend/config.py` 增加 `RCS_ASSETS_ROOT = backend/assets`

**P0.2 引入 C++ 内核**
- 复制 `d:\projects\github\robot-control-stack\src\sim\*.{h,cpp}` → `backend/rcs_sim_core/include/rcs/sim/` 与 `backend/rcs_sim_core/src/sim/`
- 复制 `d:\projects\github\robot-control-stack\src\pybind\*`（含 `rcs.cpp`、`CMakeLists.txt`、`gen_mujoco_bindings.sh`）
- 新增 `backend/rcs_sim_core/pyproject.toml`：用 `scikit-build-core` 编译，产物模块名 `rcs._sim`
  - 依赖：`mujoco`（C++ 头/lib，RCS 已依赖）、`Boost.Interprocess`（共享内存 GUI）、`Eigen`、`pybind11`
- 编译验证：`pip install -e backend/rcs_sim_core`，确认 `import rcs._sim` 可用且 `rcs._sim.Sim` / `SimRobot` / `SimGripper` / `SimCameraSet` 存在
- 注意：RCS `src/pybind/rcs.cpp` 可能把整个 `rcs` 包暴露为 `rcs.sim`。我们只需 `sim` 子模块，可裁剪 `rcs.cpp` 仅保留 `sim` 相关绑定，避免把 RCS 全部 operator/ROS 代码拉进来。

### Phase 1 — 引擎层对接（MuJoCoEngine → rcs._sim.Sim）
**P1.1** 重写 `engine.py`：
- `MuJoCoEngine.__init__`：调用 `rcs._sim.Sim(xml_or_path, SimConfig)`，构造后创建 `SimRobot`（按 prefix）、可选 `SimGripper`/`SimTilburgHand`、`SimCameraSet`
- `step(qpos_target)` → `sim.step_until_convergence()`（默认同步控制）
- `qpos()` / `forward_kinematics()` → 从 `SimRobot.get_state()` 取
- `render()` → `SimCameraSet.get_latest_frameset()`（经 `CameraRenderer` 适配）
- `set_control_mode(ControlMode)` / `reset()` / `joint_limits()`
- 保留 `LogicEngine`（物流逻辑仿真，不依赖 RCS）作为 `RobotType.AGV/STACKER` 等设备的回退

**P1.2** `renderer.py`：
- `CameraRenderer` 改为包装 `SimCameraSet`：提供 `get_frameset()` 返回 `{name: {"rgb", "depth", "K", "pose"}}`，与现有 `metadata` 兼容

### Phase 2 — 场景组合与注册（ModelComposer + envs）
**P2.1** 新增 `composer.py`：从 RCS `python/rcs/sim/composer.py` 移植 `ModelComposer`（纯 Python MJCF 拼装 + 前缀化）
**P2.2** `envs/creator.py`：
- `SimEnvCreatorConfig` 增加字段：机器人/夹爪/相机/物体字典、`SimConfig`（async/realtime/frequency/conv_steps）、`RelativeTo`、坐标系偏移（root/shared/robot）
- `SimEnvCreator.__call__`：调用 `composer.compose()` → `MuJoCoEngine` → 返回 `SimEnv`（带 wrappers）
**P2.3** `envs/configs.py`：补全 RCS 全部 env（FR3/Panda/UR5e/xArm7/SO-101/YAM + Robotiq/FrankaHand + 灵巧手 tilburg）
**P2.4** `envs/scenes.py`：增加 `empty_world`、`tabletop_pick/stack`、`duo`（双机）、`hand_manipulation`

### Phase 3 — Gym 环境能力补齐
**P3.1** `envs/base.py`：
- 引入 `ControlMode`（JOINT_POSITION / VELOCITY / TORQUE / CARTESIAN_TQuat / CARTESIAN_POSE / DELTA_*）
- 引入 `RelativeTo`（LAST_STEP / CONFIGURED_ORIGIN / WORLD）
- obs 增加：多机关节、TCP pose、夹爪宽度、相机 RGB+Depth、instruction
- action 支持 dict（cartesian + gripper）或 joint 数组
- info 增加：collision / ik_success / is_sim_converged / frame_timestamp / is_grasped / sim_state / sim_state_schema
**P3.2** 新增 wrappers：
- `envs/gripper.py`：`GripperWrapperSim`（归一化宽度、抓握判定）
- `envs/hand.py`：`HandWrapperSim`（16-actuator 截取、归一化关节角）
- `envs/storage.py`：`StorageWrapper`（Parquet + DuckDB，图像单独落盘）
- `envs/digital_twin.py`：`DigitalTwin`（双 env 并行，sim + real 对照）
- 保留现有 `RobotWrapper`/`CameraSetWrapper`/`TaskWrapper` 并适配

### Phase 4 — 渲染/相机/GUI/回放 补齐
**P4.1** `camera.py`：包装 `rcs._sim.SimCameraSet` + `ColorFrame/DepthFrame`，提供 `get_latest_frameset/get_timestamp_frameset`
**P4.2** `gui.py`：`GuiClient` 包装（Boost 共享内存 → `mujoco.viewer`）
**P4.3** `egl_bootstrap.py`：从 RCS 移植，headless EGL 初始化
**P4.4** `replayer.py`：从 RCS 移植 `replay(dataset, output, headless, frequency, env_id)`，用 `info["sim_state"]` 严格恢复

### Phase 5 — 扩展注册 & 资产接入
**P5.1** `extensions/__init__.py`：为复制来的机器人/夹爪注册 `Extension`（fr3/panda/ur5e/xarm7/so101/yam + robotiq/franka_hand/tilburg），`mjcf_path` 指向 `backend/assets`
**P5.2** 保持物流扩展（container_robot/agv/stacker）走 `LogicEngine`

### Phase 6 — 测试 & 文档
**P6.1** 扩展 `tests/test_rcs_env.py`：覆盖多机、夹爪、相机 obs、ControlMode、回放
**P6.2** 新增 `tests/test_composer.py`、`test_gui_shm.py`、`test_storage.py`
**P6.3** 更新 `simulation/README.md`：架构图、构建步骤、快速上手
**P6.4** 保留 `simulation.md` 作为能力参照

---

## 3. 关键风险与缓解

| 风险 | 缓解 |
|---|---|
| C++ 编译环境（Boost/Eigen/MuJoCo 头）在 RL-SIM 缺失 | P0.2 用 scikit-build 声明依赖；CI 加 `mujoco` + `libboost-dev`；先在本地 `pip install -e` 验证 |
| RCS `rcs.cpp` 绑定把 operator/ROS 等无关代码也暴露 | 裁剪 `rcs.cpp` 仅保留 `sim` 子模块绑定（`Sim/SimRobot/SimGripper/SimTilburgHand/SimCameraSet/Renderer/GuiServer`） |
| 物流 `LogicEngine` 与 MuJoCo 并存 | 保留双引擎：`RobotType.AGV/STACKER` 走 `LogicEngine`；机械臂走 `MuJoCoEngine`（rcs._sim） |
| 坐标系语义差异（RCS 用 `robot_contracts.Pose`） | 复用 RL-SIM 已有 `robot_contracts.Pose`，在 `MuJoCoEngine` 做 xyz+quat ↔ MuJoCo 转换 |
| 资产 mesh 路径在复制后失效 | `composer.py` 解析 `include` 为绝对路径（RCS 已处理），确认 `backend/assets` 下相对引用正确 |
| 共享内存 GUI 在 Windows 调试不便 | `GuiClient` 默认关闭，端到端测试用 headless + `render_mode="rgb_array"`；GUI 单独文档说明 |

---

## 4. 验收标准（Definition of Done）

- [ ] `pip install -e backend/rcs_sim_core` 成功，`import rcs._sim` 可用
- [ ] `gym.make("rcs/empty_world_fr3")` 可 reset/step，obs 含 TCP pose + 关节 + 相机 RGB+Depth
- [ ] 夹爪（Robotiq/FrankaHand）归一化宽度可设可测
- [ ] 灵巧手（Tilburg）16-actuator 动作空间可用
- [ ] 多机场景（duo）可运行
- [ ] `ControlMode.CARTESIAN_TQuat` 经 IK 收敛步进生效
- [ ] `StorageWrapper` 写出 Parquet，`replayer.replay` 可严格回放
- [ ] `DigitalTwin` 双 env 并行成功
- [ ] `GuiClient` + `start_gui_server` 在独立进程可视化（Linux）
- [ ] 全部 pytest 通过（含新增 composer/gui_shm/storage）
- [ ] `simulation/README.md` 更新，含构建与示例

---

## 5. 执行顺序建议（原子提交）

1. `feat(assets)`: 复制 RCS assets → backend/assets
2. `feat(core)`: 引入 C++ sim + pybind，编译出 rcs._sim
3. `refactor(engine)`: MuJoCoEngine 对接 rcs._sim.Sim
4. `feat(composer)`: ModelComposer + envs 重组
5. `feat(gym)`: ControlMode/RelativeTo/相机 obs/wrappers 补齐
6. `feat(camera-gui-replay)`: camera/gui/egl/replayer
7. `feat(extensions)`: 注册 RCS 机器人/夹爪
8. `test(docs)`: 测试 + README

---

*计划版本 v1.0 — 2026-08-25*
