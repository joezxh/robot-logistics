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
- pybind11 绑定 + 编译产物 `rcs._core`（扩展模块），并通过 `rcs/__init__.py` 暴露 `rcs.sim` / `rcs.common` 子模块
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
│   │   └── pyproject.toml          # 用 scikit-build 编译出 rcs._core 扩展模块
│   ├── rcs_env/                     # 现有：改为“薄适配层”，转发到 rcs_sim_core + 补齐 Python
│   │   ├── engine.py                # MuJoCoEngine 改为包装 rcs.sim.Sim
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
- 新增 `backend/rcs_sim_core/pyproject.toml`：用 `scikit-build-core` 编译，产物模块名 `rcs._core`
  - 依赖：`mujoco`（C++ 头/lib，RCS 已依赖）、`Boost.Interprocess`（共享内存 GUI）、`Eigen`、`pybind11`
- 编译验证：`pip install -e backend/rcs_sim_core`，确认 `import rcs` 可用且 `rcs.sim.Sim` / `SimRobot` / `SimGripper` / `SimCameraSet` 存在
  - 注：`rcs/__init__.py` 已在导入 `_core` 前调用 `os.add_dll_directory` 注册 mujoco 的 DLL 目录，避免 Windows 上 "DLL load failed"
- 注意：RCS `src/pybind/rcs.cpp` 可能把整个 `rcs` 包暴露为 `rcs.sim`。我们只需 `sim` 子模块，可裁剪 `rcs.cpp` 仅保留 `sim` 相关绑定，避免把 RCS 全部 operator/ROS 代码拉进来。

### Phase 1 — 引擎层对接（MuJoCoEngine → rcs.sim.Sim）
**P1.1** 重写 `engine.py`（✅ 已完成，2026-08-30）：
- `MuJoCoEngine.__init__`：经 `rcs.sim.Sim(xml_path)` 加载 MJCF（Sim 内部 `mj_loadXML` 并拥有 model/data），再 `rcs.sim.SimRobot(sim, SimRobotConfig())` 构造机械臂控制句柄。模型路径在 `<pkg>/assets/robots/**` 下递归解析；因 MuJoCo 按 cwd 解析 meshdir，`_try_load` 会临时 `chdir` 到模型目录。
- `step(action)` → `SimRobot.set_joint_position(action)`（位置控制设 `d->ctrl`）后 `Sim.step(1)`
- `qpos()` / `qvel()` → `SimRobot.get_joint_position()` / `get_joint_velocity()`
- `set_qpos(q)` → `SimRobot.set_joints_hard(q)` + `Sim.forward()`（teleport 后刷新前向运动学）
- `forward_kinematics(q)` → `set_qpos` + `SimRobot.get_cartesian_position()`（世界系），并把 wxyz 四元数转成 `robot_contracts.Pose` 的 xyzw 约定
- `joint_limits()` → `SimRobot.joint_limits()`；`collision_free(q)` → `Sim.ncon()==0`
- `dof` 取 `get_joint_position()` 长度（= 受控关节数）
- 保留 `LogicEngine`（物流逻辑仿真，不依赖 RCS）作为 `RobotType.AGV/STACKER` 等设备的回退
- 新增 `shared/python/robot_contracts` 包（`Pose`/`RobotType`，numpy 轻依赖），作为 `rcs_env` 与 `backend` 服务的统一契约类型（此前缺失，导致 `engine.py` 无法 import）

**P1.2** `renderer.py`（✅ 已完成，2026-08-30）：
- 新增 `SimRenderer`，包装 `rcs.sim.SimCameraSet`：`render()` 返回 `{"rgb": HxWx3 uint8, "depth": HxWx1 float32}`，`render_all()` 返回 `{name: {rgb, depth}}`，与现有 `CameraSetWrapper` obs 兼容
- 相机配置：`{name: (identifier, frame_rate, width, height)}`，构造 `SimCameraConfig(identifier, frame_rate, width, height, type=CameraType.kColor)`，再 `SimCameraSet(sim, camera_configs, render_on_demand, max_buffer_frames=1)`
- `MuJoCoEngine` 新增 `sim` 属性、`build_renderer(cameras)`、`render()`；`build_renderer` 在 GL 不可用时降级为零帧占位
- 注意：`SimCameraSet` 依赖 GL 上下文（见"已知问题"）；`SimRenderer.available()` 做导入级可用性判断，`_ensure_camera_set` 在运行时兜底，headless 下返回零帧不崩溃

**已知问题（rcs_sim_core 原生层，非本次 Python 重构引入）**：
- ⚠️ 原生 CRT 冲突已于 2026-08-30 **修复**（见 3.1 节）：`Sim::renderer` 改为懒加载 + `Sim::close()` + `MuJoCoEngine.close()`/上下文管理器，`rcs + MjOMPL` 同进程联调现已干净退出（EXIT=0）。
- FR3 资产初始位姿 `qpos0=全零` 在该桌面场景自碰撞（`ncon=4`，`reset()` 不暴露），属模型 home 配置问题；联调用抬臂/关键帧无碰撞起点，或修正 FR3 资产 home。

### Phase 2 — 场景组合与注册（ModelComposer + envs）
**P2.1** 新增 `composer.py`（✅ 已完成，2026-08-30）：
- 从 RCS `python/rcs/sim/composer.py` 移植 `ModelComposer`，基于 `mujoco.MjSpec` 编程拼装（机器人/夹爪/物体/相机），按 prefix 隔离多实例
- 位姿使用 `robot_contracts.Pose`（xyzw 约定），内部转 MuJoCo 的 wxyz；提供 `add_robot/add_gripper/add_object/add_camera/load_base_scene`
- 新增 dataclass：`EnvConfig`/`RobotSpec`/`GripperSpec`/`ObjectSpec`/`CameraSpec`（场景层配置）
- 便捷入口：`build_engine()`（拼装后写入临时 MJCF 并交给 `MuJoCoEngine` 加载）、`compose_env(env_config)`（`EnvConfig` → `MuJoCoEngine` 一键构建）
- `add_gravcomp` 支持（按 prefix 标记 `body.gravcomp=1` / `joint.actgravcomp=True`）
**P2.2** `envs/creator.py`（✅ 已完成，2026-08-30）：
- `SimEnvCreatorConfig` 增加 `scene: EnvConfig | None` 字段（"配置即场景"）
- `SimEnvCreator.__call__`：当 `scene` 给定而 `mjcf_path` 为空时，先经 `compose_env(scene)` 用 `ModelComposer` 拼装出 `MuJoCoEngine`，再据此构建 `SimEnv`（替换默认引擎 + 重建 OMPL planner），最后套用 wrappers
**P2.3** `envs/configs.py`（✅ 已完成，2026-08-30）：
- 完整机器人名册：`ROBOT_ASSETS`（fr3/panda/ur5e/xarm7/so101/yam）+ `LOGISTICS_ASSETS`（agv/stacker）+ `GRIPPER_ASSETS`；每个指向 `assets/robots/<type>/<type>.xml` 与 `RobotType`
- 提供 `get_config(name)` 返回 `SimEnvCreatorConfig`，以及 per-robot 工厂（`fr3()`/`panda()`/...）与扁平 `CONFIGS` 注册表
- 注：RCS 在 `ROBOTS` 注册表里硬编码每个机器人的关节/执行器列表；robot-logic 改为由 `MuJoCoEngine` **加载时自动探测**关节/基座/TCP 站点（见 engine `_detect_robot_config`），因此 configs 只需资产路径，整套名册与 `SimRobot` 解耦
**P2.4** `envs/scenes.py`（✅ 已完成，2026-08-30）：
- 场景预设：`empty_world`/`tabletop_pick`/`tabletop_stack`/`duo`/`hand_manipulation`，均以 `EnvConfig`（经 `ModelComposer` 拼装）表达
- `get_scene(name)` 返回 `SimEnvCreatorConfig(scene=EnvConfig(...))`；`duo` 用 `fr3_duo_mount` 摆双机；`tabletop_pick` 带 `CameraSpec`
- 修复 `ModelComposer.add_object(attach_to=None)` 的 body 查找（attach 用 frame 包裹后保留原名）

### Phase 3 — Gym 环境能力补齐
**P3.1** `envs/base.py`（✅ 已完成，2026-08-30）：
- `SimEnv` 补齐 Gym 契约：`metadata`/`spec`、`action_space`/`observation_space`、
  `reset`/`step`/`close`；`reset` 默认采样无碰撞目标（`goal_ee`）
- 任务/奖励：`compute_reward`（密集奖励 = -‖EE_pos − goal_pos‖ + 成功 bonus）、
  `compute_terminated`（EE 距目标 < `GOAL_TOLERANCE=0.02m` 判定成功）、`_sample_goal`（IK+碰撞校验采样）
- `render()` 返回 `rgb_array`（HxWx3）；`close()` 显式释放引擎（避免退出堆损坏）
- `MuJoCoEngine.inverse_kinematics(goal, seed)`：经 `SimRobot.get_ik()` → `MjIK.inverse` 求解（robot_contracts.Pose xyzw → common.Pose wxyz）
- `register_envs()`（`gym.register` 稳定 ID：`rcs/<robot>-reach-v0`、`rcs/<scene>-v0`）+ `make_env(task_id)`
**P3.2** 新增 wrappers（⏳ 待做，沿用 RCS 清单）：
- `envs/gripper.py`：`GripperWrapperSim`（归一化宽度、抓握判定）
- `envs/hand.py`：`HandWrapperSim`（16-actuator 截取、归一化关节角）
- `envs/storage.py`：`StorageWrapper`（Parquet + DuckDB，图像单独落盘）
- `envs/digital_twin.py`：`DigitalTwin`（双 env 并行，sim + real 对照）
- 保留现有 `RobotWrapper`/`CameraSetWrapper`/`TaskWrapper` 并适配

### Phase 4 — 渲染/相机/GUI/回放 补齐
**P4.1** `camera.py`：包装 `rcs.sim.SimCameraSet` + `ColorFrame/DepthFrame`，提供 `get_latest_frameset/get_timestamp_frameset`
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
| 物流 `LogicEngine` 与 MuJoCo 并存 | 保留双引擎：`RobotType.AGV/STACKER` 走 `LogicEngine`；机械臂走 `MuJoCoEngine`（rcs.sim） |
| 坐标系语义差异（RCS 用 `robot_contracts.Pose`） | 复用 RL-SIM 已有 `robot_contracts.Pose`，在 `MuJoCoEngine` 做 xyz+quat ↔ MuJoCo 转换 |
| 资产 mesh 路径在复制后失效 | `composer.py` 解析 `include` 为绝对路径（RCS 已处理），确认 `backend/assets` 下相对引用正确 |
| 共享内存 GUI 在 Windows 调试不便 | `GuiClient` 默认关闭，端到端测试用 headless + `render_mode="rgb_array"`；GUI 单独文档说明 |

---

## 3.1 已知问题与修复记录

### 进程退出堆损坏 0xC0000374（原生 CRT 冲突）— ✅ 已修复 2026-08-30
- **现象**：`rcs.sim.Sim` + `MjOMPL`（纯 Python planner）同进程运行后，进程退出时崩溃
  `0xc0000374`（ntdll!RtlReportCriticalFailure，CRT 堆损坏）。
- **历史误判**：早期怀疑是 `rcs` + C++ `ompl` 同进程引发（0xc0000005）。经核查
  `MjOMPL` 实际是纯 Python，**不存在 C++ ompl 绑定**；该次崩溃同属退出堆损坏。
- **根因**：`Sim` 作为成员持有 `rcs::sim::Renderer renderer;`，其构造函数在**每次**
  `Sim` 构造时即 `mjv_makeScene` 分配 MuJoCo GL 场景/上下文；进程退出时
  `Renderer::~Renderer` 在静态析构阶段释放这些内存，此时 CRT 堆已部分销毁 → 损坏。
- **修复**：
  1. `sim.h`：`renderer` 成员改为 `Renderer* renderer{nullptr}`，不在构造时建场景。
  2. 新增 `Sim::get_renderer()` 懒加载（仅首次渲染使用时 `new Renderer(m)`）。
  3. 新增 `Sim::close()`（幂等）：先 `delete renderer` 再 `mj_deleteData`/`mj_deleteModel`
     并置空，避免静态析构期晚释放。
  4. `~Sim()` 改为调用 `close()`（空指针安全）。
  5. pybind 暴露 `Sim.close()`；`camera.cpp` 改用 `sim->get_renderer()`。
  6. `MuJoCoEngine` 增加 `close()` + 上下文管理器（`__enter__`/`__exit__`）+ 受保护
     `__del__`，使 MuJoCo 堆在正常执行期释放，而非 atexit。
- **验证**：`rcs_sim_core` 重新 `pip install -e .`；`MuJoCoEngine(FR3) + MjOMPL` 同进程
  用 `with` 与普通 GC 两种路径运行均 `EXIT_CODE=0`；给定无碰撞起点 RRT 规划成功
  （`plan success: True`），MjOMPL 联调可用。

### FR3 模型初始位姿与桌面碰撞（场景/资产问题，非原生 bug）
- **现象**：`engine.reset()` 后 `engine.qpos()` 返回全零，调用 `set_qpos(全零)` 或
  `forward()` 后 `ncon()==4`（4 处接触）。`reset()` 本身不暴露——`mj_resetData`
  将 `ncon` 置 0 但未做碰撞检测。
- **结论**：FR3 模型 `qpos0=全零` 在该桌面场景下确实自碰撞/触桌，属模型 home 配置问题。
- **影响**：`MjOMPL.collision_free(home)` 返回 False，导致以 home 为起点的规划失败。
- **规避**：联调时使用抬臂（如 `j6≈1.5`）等无碰撞起点/关键帧；或修正 FR3 资产 home。

---

## 4. 验收标准（Definition of Done）

- [ ] `pip install -e backend/rcs_sim_core` 成功，`import rcs` 可用
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
2. `feat(core)`: 引入 C++ sim + pybind，编译出 rcs._core（暴露 rcs.sim / rcs.common）
3. `refactor(engine)`: MuJoCoEngine 对接 rcs.sim.Sim
4. `feat(composer)`: ModelComposer + envs 重组
5. `feat(gym)`: ControlMode/RelativeTo/相机 obs/wrappers 补齐
6. `feat(camera-gui-replay)`: camera/gui/egl/replayer
7. `feat(extensions)`: 注册 RCS 机器人/夹爪
8. `test(docs)`: 测试 + README

---

*计划版本 v1.0 — 2026-08-25*
