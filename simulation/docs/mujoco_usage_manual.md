# MuJoCo 仿真使用手册（robot-logic/simulation）

> 本文档整理 `robot-logic/simulation` 中**所有使用 MuJoCo 的方式**，覆盖 C++ 物理内核
> (`rcs_sim_core`) 与 Python 适配层 (`rcs_env`) 两个层次，给出 API 用法、数据流与示例。
>
> 配套文档与代码：
> - `backend/examples/loader_robot_demo.py` — **可直接运行的完整范例**（装卸机器人抓放，见 §9）
> - `simulation/docs/rcs_migration_plan.md` — 能力迁移计划
> - `robot-control-stack/simulation.md` — 原始 RCS 能力清单（参考）

---

## 1. 架构总览

仿真采用**双层结构**，MuJoCo 在两层均有使用：

```
┌─────────────────────────────────────────────────────────────┐
│  Python 适配层  (backend/rcs_env)                            │
│   Gym 环境 / OMPL 规划器 / 渲染器 / 扩展注册                  │
│   - engine.MuJoCoEngine  (纯 Python，直接 import mujoco)      │
│   - renderer.SimRenderer   (纯 Python offscreen 渲染)         │
└───────────────────────────┬─────────────────────────────────┘
                            │  import rcs._core  (编译产物)
┌───────────────────────────┴─────────────────────────────────┐
│  C++ 物理内核  (backend/rcs_sim_core)                         │
│   Sim / SimRobot / SimGripper / SimCameraSet / Renderer       │
│   MjIK (MuJoCo 原生逆运动学)                                  │
│   → 全部用 mujoco C API (mj_step / mj_forward / mj_jacSite …)│
└─────────────────────────────────────────────────────────────┘
```

**两种接入路径**：
1. **轻量路径**（已落地、无需编译）：`rcs_env.engine.MuJoCoEngine` —— 纯 Python `import mujoco`，直接调用 `MjModel/MjData`。
2. **高性能路径**（规划中、需编译）：`rcs_sim_core` 的 `rcs._core.sim.Sim` 系列 —— C++ 封装，`MjIK` 提供原生 IK。

两者共享同一套 `EngineConfig` / `PhysicsEngine` 抽象接口（`engine.py`），环境层 (`envs`) 不感知具体引擎。

---

## 2. Python 层用法（MuJoCoEngine + SimRenderer）

文件：`backend/rcs_env/engine.py`、`backend/rcs_env/renderer.py`

### 2.1 加载模型与基础步进

```python
import numpy as np
from rcs_env.engine import EngineConfig, MuJoCoEngine

cfg = EngineConfig(
    robot_type=RobotType.FR3,
    mjcf_path="path/to/fr3.xml",   # 必须是 MJCF 文件
    dt=0.002,
    gravity=(0.0, 0.0, -9.81),
)
engine = MuJoCoEngine(cfg)

# 关键 MuJoCo 调用（engine.py 内部）:
#   self._model = mujoco.MjModel.from_xml_path(cfg.mjcf_path)
#   self._data  = mujoco.MjData(self._model)
#   mujoco.mj_step(self._model, self._data)        # step()
#   mujoco.mj_resetData(self._model, self._data)   # reset()
#   mujoco.mj_forward(self._model, self._data)     # set_qpos 后刷新
```

### 2.2 关节控制与状态读取

```python
# 控制：直接写 ctrl，然后 mj_step
engine.step([0, -0.78, 0, -1.57, 0, 1.0, 0])   # action 长度 = dof

# 状态读取
qpos = engine.qpos()          # mjData.qpos[:dof]
qvel = engine.qvel()          # mjData.qvel[:dof]
low, high = engine.joint_limits()   # mjModel.jnt_range[:dof]

# 直接置位（规划器 / 回放用）：写 qpos 后 mj_forward
engine.set_qpos([0, 0, 0, 0, 0, 0, 0])
```

### 2.3 正运动学（FK）

```python
ee: Pose = engine.forward_kinematics(joint_cfg)
# 内部实现：
#   self.set_qpos(qpos)
#   body_id = self._model.body("ee").id
#   mat = self._data.xmat[body_id].reshape(3, 3)   # 行主序旋转矩阵
#   pos = self._data.xpos[body_id]
#   quat = _rotmat_to_xyzw(mat)                    # 旋转矩阵 → xyzw 四元数
# 返回 robot_contracts.Pose(translation=pos, quaternion=quat)
```

#### `xmat` 的内存布局（已实测确认）

MuJoCo 把旋转矩阵按 **9 元一维数组行主序（row-major）** 存放，即
`[m00, m01, m02, m10, m11, m12, m20, m21, m22]`。

| 读取方式 | 结果 |
|----------|------|
| NumPy `arr.reshape(3, 3)`（默认 C 序） | ✅ 正确 |
| NumPy `arr.reshape(3, 3, order="F")` | ❌ 得到转置 |
| Eigen `Map<const Matrix3d>`（默认 **ColMajor**） | ❌ 得到转置 |
| Eigen `Map<const Matrix3d, RowMajor>` | ✅ 正确 |

实测方法（绕 Z 轴 90°，矩阵非对称，结论唯一）：

```python
quat = np.array([np.cos(np.pi/4), 0, 0, np.sin(np.pi/4)])   # w,x,y,z
d.qpos[3:7] = quat           # freejoint 的朝向
mujoco.mj_forward(m, d)
raw = np.array(d.site_xmat).ravel()
# raw = [0, -1, 0, 1, 0, 0, 0, 0, 1]
raw.reshape(3, 3)            # [[0,-1,0],[1,0,0],[0,0,1]]  ✅ 与 mju_quat2Mat 一致
raw.reshape(3, 3, order="F") # [[0,1,0],[-1,0,0],[0,0,1]]   ❌ 转置
```

> **结论**：Python 侧直接 `reshape(3, 3)` 即可；C++ 侧因为 Eigen 默认按列主序解释，
> 必须显式写 `Eigen::RowMajor`（这正是 `MjIK` 中的写法，见 §4.3）。
> 两者并不矛盾——差别来自 Eigen 的默认序，而不是 MuJoCo。

### 2.4 碰撞检测

```python
free = engine.collision_free(qpos)   # set_qpos 后检查 mjData.ncon == 0
```

### 2.5 Offscreen 渲染（SimRenderer）

文件：`backend/rcs_env/renderer.py`

```python
from rcs_env.renderer import SimRenderer

renderer = SimRenderer(
    mj_model, mj_data,
    camera_name="default",
    width=320, height=240,
)
frames = renderer.render()
# 返回 {"rgb": HxWx3 uint8, "depth": HxWx1 float32}

if not renderer.available():
    frames = renderer._zero_frames()   # 无 mujoco 时返回零帧占位
```

`render()` 内部使用的 MuJoCo 渲染 API：

```python
scene = mujoco.MjvScene(model, maxgeom=100)
mujoco.mjv_updateScene(model, data, None, None, None,
                       mujoco.MjvOption(), camera_id, mjCAT_ALL, scene)
ctx = mujoco.MjrContext(model, mjFONTSCALE_150)
viewport = mujoco.MjrRect(0, 0, width, height)
mujoco.mjr_render(viewport, scene, ctx)
mujoco.mjr_readPixels(rgb, depth, viewport, ctx)
camera_id = mujoco.mj_name2id(model, mjOBJ_CAMERA, name)
```

---

## 3. Gym 环境与 OMPL 规划器

文件：`backend/rcs_env/envs/base.py`、`backend/rcs_env/ompl.py`

### 3.1 SimEnv（引擎无关）

```python
from rcs_env.envs import SimEnv
from robot_contracts import RobotType

env = SimEnv(
    robot_type=RobotType.FR3,
    mjcf_path="fr3.xml",      # 有 mujoco 时自动走 MuJoCoEngine
    planner=Planner.RRTConnect,
    render_mode="rgb_array",
)

obs, info = env.reset()
obs, reward, terminated, truncated, info = env.step(action)
# obs = [ee_xyz(3), ee_quat_xyzw(4), joints(dof), gripper(1)]
```

`build_engine()` 工厂（engine.py）：优先 `MuJoCoEngine`（需 `mjcf_path` + mujoco 可用），
否则回退到 `LogicEngine`（运动学近似，无 MuJoCo 依赖）。

### 3.2 MjOMPL 运动规划

```python
env.plan_to(goal_qpos, planner=Planner.RRTConnect)   # 关节空间规划
env.plan_to_pose(goal_pose_7vec, planner=Planner.RRTConnect)  # SE(3) 目标
```

- 纯 Python 实现的 RRT / RRT-Connect / RRT* / PRM。
- `collision_free` 钩子直接复用 `engine.collision_free`（即 MuJoCo `ncon` 检测）。
- `ik()` 为无雅可比的随机重启 + 前向运动学搜索（非 MuJoCo 雅可比法）。C++ 内核的
  `MjIK` 才是 MuJoCo 雅可比 DLS 解法，见 §4.3。

---

## 4. C++ 物理内核（rcs_sim_core）

文件：`backend/rcs_sim_core/src/sim/*.cpp`、`src/rcs/MjIK.cpp`

编译产物为 `rcs._core`，提供 `rcs.sim` 与 `rcs.common` 两个 pybind11 子模块。

### 4.1 Sim —— 仿真主循环

核心方法（sim.cpp）：

| 方法 | MuJoCo 调用 | 说明 |
|------|------------|------|
| `Sim(m, d)` 构造 | — | 持有 `mjModel*` / `mjData*` |
| `step(k)` | `mj_step1` / `mj_step2` | 步进 k 帧，期间触发回调 |
| `step_until_convergence()` | `step` + 条件回调 | 同步控制：等到 `all_callbacks` 全 true 或 `any_callbacks` 任一 true |
| `reset()` | `mj_resetData` | 复位 data |
| `set_dynamic_joint_state(schema, state)` | `mj_forward` | 回放：写入 qpos/qvel 后 `mj_forward` 刷新 |
| `get_dynamic_joint_state()` | 读 `d->qpos/qvel` | 导出当前关节状态 |
| `start_gui_server(id)` | — | 共享内存 GUI（Boost，Linux） |

**关节规范解析**（构造时）：

```cpp
for (int j = 0; j < m->njnt; ++j) {
  const char* name = mj_id2name(m, mjOBJ_JOINT, j);
  spec.type   = m->jnt_type[j];       // mjJNT_HINGE / SLIDE / BALL / FREE
  spec.qpos_adr = m->jnt_qposadr[j];  // 在 qpos 向量中的偏移
  spec.qvel_adr = m->jnt_dofadr[j];   // 在 qvel 向量中的偏移
  // qpos 长度: FREE=7, BALL=4, HINGE/SLIDE=1
}
```

**回调系统**：`register_cb`（每 N 秒）、`register_any_cb` / `register_all_cb`
（收敛判定），驱动机器人/夹爪的到达检测与碰撞检测。

### 4.2 SimRobot / SimGripper —— 机器人控制

构造（SimRobot.cpp）：

```cpp
// 推荐：2 参构造，内部用 MuJoCo 原生 MjIK
auto robot = std::make_shared<SimRobot>(sim, SimRobotConfig{...});

// 或显式传入 IK 求解器（可替换为 pinocchio）
auto robot = std::make_shared<SimRobot>(sim, ik_solver, cfg, true);
```

常用 MuJoCo 调用：

```cpp
// 名称 → ID 解析（所有对象类型）
mj_name2id(m, mjOBJ_JOINT,  "joint1");   // 关节
mj_name2id(m, mjOBJ_ACTUATOR,"actuator0");// 执行器
mj_name2id(m, mjOBJ_SITE,   "attachment_site"); // TCP site
mj_name2id(m, mjOBJ_BODY,   "base");      // 基座 body
mj_name2id(m, mjOBJ_GEOM,   "link_collision"); // 碰撞体

// 读取 site 位姿（xmat 为 9 元行主序数组）
Eigen::Matrix3d R(Eigen::Map<const Eigen::Matrix<double,3,3,Eigen::RowMajor>>(
    sim->d->site_xmat + 9*site_id));     // 必须显式 RowMajor（Eigen 默认 ColMajor）
Eigen::Vector3d p(sim->d->site_xpos + 3*site_id);

// 关节读取
q[i] = sim->d->qpos[m->jnt_qposadr[joint_id]];

// 控制：写入 ctrl
sim->d->ctrl[actuator_id] = target_angle;

// 基座位姿
Eigen::Vector3d bp(sim->d->xpos + 3*base_id);
Eigen::Quaterniond bq(sim->d->xquat + 4*base_id);

// 碰撞检测：遍历 contact
for (int i=0; i<sim->d->ncon; ++i) {
  geom0 = sim->d->contact[i].geom[0];
  geom1 = sim->d->contact[i].geom[1];
}
```

夹爪 (`SimGripper`)：归一化宽度 `set_normalized_width(0..1)` 映射到
`[min_actuator_width, max_actuator_width]` 写入 `ctrl`；`get_normalized_width()` 由
`qpos` 反算；`is_grasped()` 用 libfranka 逻辑判定。

### 4.3 MjIK —— MuJoCo 原生逆运动学（核心亮点）

文件：`src/rcs/MjIK.cpp`

替代 RCS 原 pinocchio 依赖（Windows 不可用），用 MuJoCo 雅可比做阻尼最小二乘 (DLS) IK。

```cpp
MjIK ik(m, d, joint_names, site_name, base_name);  // 构造即解析 ID
auto q = ik.inverse(target_pose, q0, tcp_offset);   // 逆解 → 关节角
auto pose = ik.forward(q0, tcp_offset);             // 正解 → TCP pose
```

**算法核心（`_step`）**：

```cpp
// 1. 把当前猜测写入"临时" data（不污染在线仿真）
for (i) d_scratch->qpos[dof_adr[i]] = q[i];
mj_forward(m, d_scratch);                 // 刷新临时状态

// 2. 取 site 当前位姿（xmat 为行主序 9 元数组）
cur_pos = d_scratch->site_xpos + 3*site_id;
cur_rot = Map<const Matrix<double,3,3,RowMajor>>(d_scratch->site_xmat + 9*site_id);

// 3. 空间误差 = 目标 * 当前^-1 （位置 + 轴角旋转）
err_pose = target * cur.inverse();
p_err = err_pose.translation();
r_err = AngleAxis(err_pose.rotation()).angle() * axis();

// 4. 全雅可比（site，6 x nv）
mj_jacSite(m, d_scratch, Jpos, Jrot, site_id);
Jfull.topRows(3)=Jrot; Jfull.bottomRows(3)=Jpos;
J = Jfull.cols(vel_adr);                 // 仅保留受控 dof

// 5. 阻尼最小二乘迭代
JJt = J*Jᵀ; JJt.diag() += damp;
dq = Jᵀ * (JJt.ldlt().solve(-err));
q[dof_adr] += dq * DT;
```

**关键点（`xmat` 行主序，见 §2.3 的实测结论）**：

```cpp
// MuJoCo 的 site_xmat 是 9 元**行主序**数组；
// 但 Eigen::Map 默认按**列主序**解释，直接写会读到转置矩阵。
Eigen::Map<const Eigen::Matrix<double,3,3>> cur_rot(     // ❌ 默认 ColMajor
    d_scratch->site_xmat + 9*site_id);
// 正确写法：显式指定 RowMajor
Eigen::Map<const Eigen::Matrix<double,3,3,Eigen::RowMajor>> cur_rot(
    d_scratch->site_xmat + 9*site_id);                   // ✅
```

> 此规则已在 `MjIK` 与 `SimRobot::get_cartesian_flange_position` 中落实（均使用 `RowMajor`）。
> Python 侧不存在此问题：`np.reshape(3, 3)` 默认 C 序即行主序，直接可用。

### 4.4 Renderer（C++ offscreen）

文件：`src/sim/renderer.cpp`

```cpp
Renderer r(m);                       // mjv_defaultScene + mjv_makeScene(maxgeom=2000)
r.register_context(id, w, h);        // mjr_makeContext + mjr_setBuffer(OFFSCREEN)
                                   // + mjr_resizeOffscreen
ctx = r.get_context(id);             // mjr_setBuffer(OFFSCREEN, ctx) 后返回
// 调用方用 mjv_updateScene + mjr_render + mjr_readPixels 取帧
```

---

## 5. MJCF 资产

`backend/assets/` 复制自 RCS：

```
assets/
├── robots/     # fr3, panda, ur5e, xarm7, so101, yam 等 MJCF + mesh
├── grippers/   # robotiq 2f85, franka hand
├── objects/    # 抓取物体
├── scenes/     # 场景 MJCF（tabletop / empty / duo）
└── cameras/    # 相机 MJCF 定义
```

加载方式：Python 层 `mujoco.MjModel.from_xml_path(...)`；C++ 层由
`rcs.sim.Sim(xml_path, SimConfig())` 内部解析（见 `rcs_sim_core/python/rcs/__init__.py`）。

---

## 6. 扩展注册（Extension）

文件：`backend/rcs_env/extensions/__init__.py`

每个机器人/传感器是独立扩展，携带 `mjcf_path`：

```python
Extension(
    key="robotiq_2f85",
    kind="sensor",
    robot_type=RobotType.UR5E,
    mjcf_path=None,            # 实际模型在 assets/ 下
    make=lambda: {"type": "gripper", "fingers": 2},
)
```

`build_engine_config()` 返回 `EngineConfig`（含 `mjcf_path`），驱动 `MuJoCoEngine` 构造。

---

## 7. 快速开始

### 7.1 Python 轻量路径（已可用）

```bash
cd robot-logic/simulation/backend
pip install mujoco gymnasium
python -c "
from rcs_env.engine import EngineConfig, MuJoCoEngine, RobotType
from rcs_env.envs import SimEnv
e = MuJoCoEngine(EngineConfig(robot_type=RobotType.FR3, mjcf_path='assets/robots/fr3/fr3.xml'))
e.reset(); e.step([0]*7); print('qpos', e.qpos())
"
```

### 7.2 C++ 内核路径（需编译）

```bash
cd robot-logic/simulation/backend/rcs_sim_core
pip install -e .            # scikit-build-core 编译 rcs._core
python -c "
import rcs
sim = rcs.sim.Sim(xml_path, rcs.sim.SimConfig())
robot = rcs.sim.SimRobot(sim, 'robot0_')
robot.set_qpos([0, -0.78, 0, -1.57, 0, 1.0, 0])
"
```

构建依赖：C++17、CMake、Ninja、pybind11、mujoco（含 lib+headers）、Eigen3。
GUI（Boost.Interprocess）与 EGL 渲染在 Windows 上被条件编译守卫（`RCS_HAVE_BOOST` /
`RCS_HAVE_EGL`）跳过。

---

## 8. 关键 API 速查表

| 功能 | Python | C++ 内核 |
|------|--------|----------|
| 加载模型 | `MjModel.from_xml_path` | `Sim(m, d)` / `Sim(xml, cfg)` |
| 步进 | `mj_step` | `Sim::step` / `step_until_convergence` |
| 复位 | `mj_resetData` | `Sim::reset` |
| 关节控制 | `data.ctrl[:] = a` | `SimRobot::set_joint_position` / `set_cartesian_position` |
| 正运动学 | `xpos/xmat + body()` | `MjIK::forward` / `get_cartesian_position` |
| 逆运动学 | 随机重启（ompl.ik） | `MjIK::inverse`（DLS 雅可比） |
| 碰撞 | `data.ncon == 0` | 遍历 `data->ncon` 的 `contact.geom` |
| 渲染 | `mjv_updateScene + mjr_render` | `Renderer` + `mjr_readPixels` |
| 名称解析 | `model.body("ee").id` | `mj_name2id(m, mjOBJ_*, name)` |

---

## 9. 注意事项与已知坑

1. **`xmat` 内存序**：MuJoCo 存的是**行主序** 9 元数组。Python 用 `reshape(3, 3)`（C 序）
   即正确；C++/Eigen 因默认 `ColMajor`，必须显式写 `Eigen::RowMajor`，否则读到转置。
   （详见 §2.3 的实测对比表）
2. **scratch data**：`MjIK` 用 `mj_makeData` + `mj_copyData` 创建临时 `mjData`，IK 迭代不污染
   在线仿真状态。
3. **收敛控制**：`step_until_convergence` 依赖 `all_callbacks`（机器人到达+静止）或
   `any_callbacks`（碰撞）触发停止，用于控制同步。
4. **关节偏移**：读写具体关节必须用 `jnt_qposadr` / `jnt_dofadr` 偏移，不能假设连续排列。
5. **Windows 编译**：GUI / EGL 被守卫跳过；核心（Sim / SimRobot / MjIK / Renderer 头）可编译。
6. **逻辑回退**：无 `mjcf_path` 或无 mujoco 时，`build_engine` 自动回退 `LogicEngine`（纯运动学）。

## 9. 完整范例：装卸机器人（Pick & Place）

> **配套代码**：`simulation/backend/examples/loader_robot_demo.py`（可直接运行，单文件、中文注释）
>
> 本章以「物流装卸机器人」为例，端到端演示在 MuJoCo 中
> **建模 → 场景搭建 → 任务定义 → 位置/力控制 → 仿真参数配置 → 可视化与数据记录** 的完整流程。
> 模型由 Python 生成 MJCF 字符串，不依赖任何外部 mesh 资产。

### 9.1 运行方式

```bash
cd robot-logic/simulation/backend
pip install mujoco numpy

# 无头运行（默认）：输出 CSV + 终端 ASCII 曲线
python examples/loader_robot_demo.py

# 指定输出目录、渲染帧数、记录频率
python examples/loader_robot_demo.py --out loader_demo_out --frames 60 --rec-hz 100

# 打开实时可视化窗口（需图形环境）
python examples/loader_robot_demo.py --view
```

可选依赖：`matplotlib`（导出矢量曲线图）、`mujoco.viewer`（实时窗口）。缺失时自动降级，不影响仿真。

### 9.2 机器人与场景模型

**运动学链**（全部 `coordinate="local"`，6 自由度 + 二指夹爪）：

```
world
 └ base_link            固定基座
    └ link1   j1: hinge  Z   基座偏航
       └ link2 j2: hinge  Y   大臂俯仰     (肩高 z = 0.16+0.10 = 0.26)
          └ link3 j3: hinge Y 小臂俯仰     (大臂 0.36)
             └ link4 j4: hinge Z 小臂自转  (小臂 0.30 + 0.12)
                └ link5 j5: hinge Y 腕部俯仰 (0.10)
                   └ link6 j6: hinge Z 腕部自转
                      └ gripper_base  euler="π 0 0"  ← 翻转 180° 使夹爪朝下
                         ├ finger_l  slide −Y
                         ├ finger_r  slide +Y
                         └ site tcp
```

> **为什么给 `gripper_base` 加 `euler="3.14159 0 0"`**：
> 不加时零位构型下夹爪朝上。翻转后 gripper 局部 +Z 指向世界 −Z，
> 于是 `tcp` site 的 Z 轴就是「工具前向」且默认朝下，顶抓目标姿态可直接构造。

**场景**：地面 + 上料输送带（顶面 z=0.358）+ 下料托盘（顶面 z=0.304）+ 6 cm 立方货物箱（2 kg，`freejoint`）。

**关键尺寸约束**（这些是实际调通过程中踩出来的）：

| 部件 | 取值 | 原因 |
|------|------|------|
| 腕部俯仰 `j5` 量程 | ±2.6 rad | 末端保持竖直向下伸到低处时 `j5 ≈ −(j2+j3)` 会到 −2.05，±2.0 会**无解** |
| 工具长度 `tcp.z − gripper_base.z` | 0.15 m | 太短（如 0.035）会把腕部关节压到货物/台面以下，既夹不到也持续碰撞 |
| 手指横向半间距 | 0.065 m | 小于 0.06 时手指会蹭到腕部 `link4`（47 N 接触力把机器人卡在半空） |
| 指垫竖直半长 | 0.022 m | 再长会伸到台面以下，下探时先撞输送带 |
| 手指伺服 `kp` | 2000 | kp=1000 时夹持力仅约 18 N，处于 2 kg 箱体的临界，转运中会滑移 |

### 9.3 仿真参数配置

```xml
<option timestep="0.002" gravity="0 0 -9.81"
        integrator="Euler" solver="Newton"
        iterations="100" ls_iterations="50" noslip_iterations="10"
        cone="elliptic" jacobian="auto"
        tolerance="1e-8" ls_tolerance="1e-10" noslip_tolerance="1e-8"/>

<default>
  <!-- 关节阻尼用 joint/damping（隐式积分，无条件稳定），
       不要用执行器的 kv·q̇ 项（显式速度反馈，小惯量腕部会发散） -->
  <joint damping="25" armature="0.05" limited="true"/>
  <!-- condim=4：3 个平动 + 1 个扭转摩擦分量，抓取更稳 -->
  <geom condim="4" friction="1.0 0.05 0.001"
        solref="0.02 1" solimp="0.9 0.95 0.001"
        margin="0.001" gap="0.001"/>
</default>
```

**碰撞过滤**（关键）：

```xml
<contact>
  <!-- 相邻连杆在关节处必然贴合，不排除会持续产生接触力，使伺服瞬间饱和 -->
  <exclude body1="base_link" body2="link1"/>
  <exclude body1="link1"     body2="link2"/>
  ... 逐级相邻对 ...
  <!-- 腕部折叠时手指会绕到小臂旁（非父子，filterparent 不管） -->
  <exclude body1="link4" body2="finger_l"/>
  <exclude body1="link4" body2="finger_r"/>
</contact>
```

### 9.4 关节位置控制

用 `<general>` 执行器的**仿射偏置**实现带阻尼的 PD 位置伺服：

```xml
<general class="arm_servo" joint="j1"
         dyntype="none" gaintype="affine" biastype="affine"
         gainprm="2500 0 0" biasprm="0 -2500 -10" forcerange="-600 600"/>
```

输出力矩 = `gainprm0·ctrl + biasprm0 + biasprm1·q + biasprm2·q̇`
= `2500·(ctrl − q) − 10·q̇`，即 `ctrl` 直接就是**目标关节角**。

**重力前馈**（消除大臂下垂）：纯 P 控制的稳态误差 = `τ_gravity / kp`，实测可达 4 cm。
用 `mj_rne` 在零速条件下求纯重力力矩，折算成指令偏置：

```python
def gravity_torque(self) -> np.ndarray:
    sd = self._gdata                 # 独立的 scratch mjData
    sd.qpos[:] = self.sim.data.qpos[:]
    sd.qvel[:] = 0.0                 # 置零 → 只剩纯重力项
    mujoco.mj_forward(self.sim.model, sd)
    mujoco.mj_rne(self.sim.model, sd, 0, self._gtau)
    return self._gtau[self.sim.kin.arm_dof_adr]

def _tick(self, q_cmd):
    q_cmd = np.clip(q_cmd, q_low, q_high)
    if self.gravity_comp:
        q_cmd = q_cmd + self.gravity_torque() / self.kp   # 折算为指令偏置
    self.sim.step(q_cmd, self.grip_cmd)
```

> 效果：TCP 稳态误差从 **33 mm → 0.7 mm**。
> 注：MuJoCo 3.3+ 才有 `gravitycomp` 属性，3.1x 需按上式自行前馈。

### 9.5 逆运动学（DLS + 解析种子 + 碰撞筛选）

与 C++ 内核 `MjIK` 同构：scratch `mjData` → `mj_forward` → `mj_jacSite` →
`dq = Jᵀ(JJᵀ+λ²I)⁻¹·err`。

单纯的数值 DLS 有两个实际坑，范例里各自给了对策：

1. **会收敛到「肘部朝下」解** —— 小臂钻到台面以下，与场景持续碰撞、伺服饱和。
   → 增加**解析种子**：末端朝下时腕段竖直，可解析求出「肘部朝上」的初始构型。

   ```python
   # 末端朝下 ⇒ 腕二段竖直，先在竖直方向扣除 wrist 与 tool，再解平面 2R
   t_h = hypot(x, y);  t_v = (z + tool - shoulder_z) - wrist
   cos_phi = (dist² + upper² - fore²) / (2·dist·upper)
   j2 = atan2(t_h, t_v) - arccos(cos_phi)      # 取「肘部朝上」分支
   j5 = -(j2 + j3)                              # 保证末端竖直向下
   ```
2. **收敛解可能与场景碰撞** → 对每个候选解做「臂 geom vs 场景 geom」筛选后再采纳。

候选初值优先级：`q_init`（热启动）→ 解析种子 → 局部扰动 → 全局随机，取第一个「收敛且无碰撞」的解。

### 9.6 力控制：导纳式保护下探

放置货物时无法（也不必）精确知道台面高度，改为一边下探一边读接触力：

```python
def guarded_move_down(self, z_stop, force_target, v_max, max_seconds, increment):
    hold_steps = max(1, round(increment / (v_max * dt)))   # 由速度决定每个增量保持几拍
    while steps < n:
        if pos[2] <= z_stop: break
        pos[2] -= increment                                  # 设定点**分步**下压
        q_cmd, _ = kin.ik(..., max_iter=80, n_restart=0)     # n_restart=0 保持解族连续
        for _ in range(hold_steps):
            self._tick(q_cmd); steps += 1
            if self.sim.cargo_support_force() >= force_target: break
    # 卸载回退：接触瞬间力会过冲，反向微调设定点把力收敛回目标
    while relaxed < 5e-3 and self.sim.cargo_support_force() > force_target * 1.2:
        pos[2] += increment; ...
    return self.sim.cargo_support_force()
```

接触力读取（`mj_contactForce` 取真实接触力螺旋）：

```python
def contact_force_between(self, geom_a, geom_b):
    ga, gb = self._gid[geom_a], self._gid[geom_b]
    total, wrench = 0.0, np.zeros(6)
    for i in range(self.data.ncon):
        c = self.data.contact[i]
        if {c.geom[0], c.geom[1]} == {ga, gb}:
            mujoco.mj_contactForce(self.model, self.data, i, wrench)
            total += np.linalg.norm(wrench[:3])
    return total
```

> **三个实现要点（都是实测踩出来的）**：
> 1. 设定点必须**分步**下压。若写成 `pos[2] -= v*dt` 逐周期微推（每拍 ~4e-6 m），
>    位移小于逆解收敛容差（5e-4 m），逆解会认为「已到位」而原地不动——机器人永远降不下来。
> 2. 增量式下探必须 `n_restart=0`（纯热启动）。中途随机重启会跳到另一解族，
>    基座偏航翻转，货物被横向甩出 9 cm。
> 3. 接触力要每周期都读并立即跳出；接触后再回退微调，力才能收敛到目标
>    （否则过冲到 40–250 N）。

### 9.7 任务状态机

```
HOME → APPROACH → DESCEND → GRASP → LIFT → TRANSFER → FORCE_PLACE → RELEASE → RETREAT → DONE
```

```python
ctrl.set_gripper(GRIPPER_OPEN, settle=0.3)
ctrl.move_to_pose(HOME_POS, duration=1.2)
ctrl.move_to_pose(PICK_APPROACH, duration=1.6)      # 笛卡尔位置控制
ctrl.move_to_pose(PICK_GRASP, duration=1.2)         # TCP 与箱心重合
grasped = ctrl.close_until_grasp(force_threshold=8.0)   # 力反馈判定抓紧
ctrl.move_to_pose(PICK_APPROACH, duration=1.2)      # 提升
ctrl.move_to_pose(PLACE_APPROACH, duration=2.0)     # 转运
ctrl.move_to_pose(pre_contact, duration=1.2)        # 位置控制快降到接触前 6mm
force = ctrl.guarded_move_down(z_stop=..., force_target=22.0)  # 力控接管
ctrl.set_gripper(GRIPPER_OPEN, settle=0.5)          # 释放
ctrl.move_to_pose(PLACE_APPROACH, duration=1.2)     # 回退
```

成功判据：抓到了 ∧ 货物落在托盘上（高度接近目标）∧ 水平误差 < 3 cm。

### 9.8 可视化与数据记录

| 能力 | 实现 |
|------|------|
| 离屏渲染 RGB/Depth | `MjvScene` + `mjv_updateScene` + `mjr_render` + `mjr_readPixels` |
| 导出 PNG 序列 | **纯标准库** PNG 编码器（`zlib` + `struct`，无需 Pillow/imageio）；MuJoCo 像素原点在左下，需垂直翻转 |
| 实时 GUI | `mujoco.viewer.launch_passive`（`--view`，需图形环境） |
| 遥测 CSV | `np.savetxt`，29 列（关节角/速度、TCP 位姿、夹爪、力、货物位姿、接触数、阶段号） |
| 曲线图 | `matplotlib`（可选）；缺失时用终端 ASCII 折线图兜底 |

> 无头环境没有 OpenGL 时，`MjrContext` 会抛 `FatalError`。范例捕获后自动降级为
> 「只记录数据、不渲染」，并在 Linux 上提示安装 EGL/OSMesa。

### 9.9 实测结果

```
[模型] nq=15  nv=14  nu=8  ngeom=18  nsensor=19
[参数] timestep=0.002s  solver=mjSOL_NEWTON  integrator=mjINT_EULER  iterations=100

  [01] HOME
  [02] APPROACH     TCP 误差=   0.9 mm
  [03] DESCEND      TCP 误差=   0.4 mm
  [04] GRASP        指尖合力 = 140.00 N  -> 已抓紧
  [05] LIFT         TCP 误差=   8.7 mm
  [06] TRANSFER     TCP 误差=   8.6 mm
  [07] FORCE_PLACE  放置接触力 =  18.96 N
  [08] RELEASE / [09] RETREAT / [10] DONE

  成功         : 是
  水平落点误差 : 3.2 mm
  垂直误差     : 1.9 mm
  放置接触力   : 18.96 N      ← 收敛到 ≈ 箱体自重 19.6 N，即"刚好落座、不硬压"
  实时比       : 8.5x  (12.8 s 仿真 / 1.5 s 墙钟)
  IK 未收敛    : 0
```

遥测曲线物理自洽性校验（`F_support`）：

```
  21.06 N |**************************                            **************
   0.00 N |                           **************************               
          └── 在输送带上(≈自重) ──┘└── 被抓起，支撑力归零 ──┘└── 落到托盘上 ──┘
```

输出文件：

```
loader_demo_out/
├── loader_robot.xml   MJCF 模型（可直接在 MuJoCo 中打开）
├── telemetry.csv      遥测数据（~640 行 × 29 列）
├── telemetry.png      矢量曲线图（需 matplotlib）
└── frames/*.png       渲染帧序列（需 OpenGL）
```

### 9.10 调通过程中定位到的 8 个真实问题

这些坑在文档里通常不会写，但每一个都会让仿真"看起来在跑、实际是错的"：

| # | 现象 | 根因 | 对策 |
|---|------|------|------|
| 1 | 关节伺服全部饱和、TCP 原地不动 | 机械臂与自己的基座顶出 **2e16 N** 接触力：`<default><geom>` 显式写了 `contype/conaffinity`，会使 MuJoCo 的 `filterparent`（父子自动过滤）对该 geom 失效 | 相邻连杆一律用 `<contact><exclude>` 显式排除（实测：仅去掉 `contype/conaffinity` **不足以**解决，显式 exclude 才是确定行为） |
| 2 | 腕部关节跟踪不上（−1.03 vs 指令 −1.83） | 执行器的 `kv·q̇` 是**显式**速度反馈，小惯量腕部满足 `kv·dt/I > 2` 而数值发散 | 阻尼改用 `joint/damping`（隐式积分，无条件稳定），`kv` 降到 10 |
| 3 | TCP 到不了目标高度（差 33 mm） | 大臂重力下垂，稳态误差 `τ_g/kp` | `mj_rne` 零速求重力力矩做前馈 → 误差降至 0.7 mm |
| 4 | 逆解对某些航点不收敛 | 腕部俯仰量程 ±2.0 不够（需要 −2.05） | 放宽 `j5` 至 ±2.6 |
| 5 | 逆解收敛但小臂钻到台面以下 | 数值 DLS 落进「肘部朝下」解族 | 增加解析「肘部朝上」种子 + 解后碰撞筛选 |
| 6 | 下探时货物被推走 / 机器人卡住 | 夹爪太短 → 腕部关节压到台面以下；手指蹭到 `link4` | 加长工具到 0.15 m；`exclude` 夹爪 vs 自身小臂 |
| 7 | 力控下探永远读不到接触力 | 货物实际压在 `pallet_mark` 上，而力检测只列了 `pallet` | 力检测要覆盖**所有**可能承托的 geom |
| 8 | 力控下探时货物横向漂移 9 cm | 增量式下探中逆解随机重启跳到另一解族 | 增量下探强制 `n_restart=0`（纯热启动） |

---

*手册版本 v1.1 — 2026-08-29*
