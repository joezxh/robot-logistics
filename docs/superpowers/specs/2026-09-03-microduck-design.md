# Microduck 集成设计规格（A+B+C+D 全量）

- **日期**：2026-09-03
- **状态**：待用户评审（评审通过后进入实施计划）
- **范围**：robot-logic 内建成 Microduck 的「模型接入 → 仿真 → 前端显示 → 训练」完整闭环
- **参考来源**：`docs/microduck.md`（X 长文整理版）、`d:\projects\github\microduck_rl`（官方 MJCF 与训练仓库，只读参考）

## 决策摘要（已与用户确认）

| 项 | 决策 |
|---|---|
| 推进范围 | A+B+C+D 一次做完完整方案 |
| 训练路线 | **双轨**：内置 SB3 PPO 训练 + 支持导入外部 ONNX 策略 |
| 前端展示形态 | **B · 嵌入现有场景列表**（复用 `ScenesEntry` 架构，Microduck 作为场景之一） |
| 模型变体覆盖 | **全部 7 个变体**（walk / groundcontact / allcollisions / rollers / 3 个 backlash） |

---

## 1. 背景与现状勘察

### 1.1 上游模型（microduck_rl）

- `src/mjlab_microduck/robot/microduck/` 含 7 个 MJCF 与 `assets/`（43 个 `.stl`），`meshdir="assets"`。
- `robot_walk.xml` 是**纯 MuJoCo 模型**：14 个 `<position>` 执行器 + `<freejoint name="trunk_base_freejoint"/>`，**不依赖 mjlab/torch 即可加载**。
- 变体清单：

| 变体 XML | 用途 | 被动关节 |
|---|---|---|
| `robot_walk.xml` | 行走（Velocity 任务，招牌能力） | — |
| `robot_groundcontact.xml` | 起身 / 坐站 / 触地拾取 / 踢球 / 前滚翻 | — |
| `robot_allcollisions.xml` | 全身接触（暂无任务使用） | — |
| `robot_groundcontact_rollers.xml` | 轮滑 | `passive_*wheel` |
| `robot_walk_backlash.xml` | 行走 + 回差 | `passive_*_backlash`（±1°） |
| `robot_groundcontact_backlash.xml` | 地面接触 + 回差 | 同上 |
| `robot_groundcontact_rollers_backlash.xml` | 轮滑 + 回差 | 两者 |

- home pose（STAND2）数值见 `microduck_constants.HOME_FRAME`，已抄录至 §7.3。
- 官方 RL 训练依赖 **mjlab + CUDA**（BAM M6 电压执行器、4096 并行环境、domain randomization）。
- 仓库内**没有任何预训练 ONNX/checkpoint**。

### 1.2 robot-logic 现状

- 后端 `simulation/backend/rcs_env/`：`engine.py`（MuJoCoEngine）、`renderer.py`、`envs/base.py`（SimEnv）、`envs/composer.py`（ModelComposer）、`envs/configs.py`（机器人名单 + ENV_FACTORIES）、`envs/vec.py`、`envs/twin.py`（DigitalTwinSink）、`training/example.py`（SB3 PPO）。
- **`SimEnv` 是深度机械臂向的**：观测 = 末端位姿(7)+关节(dof)+夹爪(1)，动作 = 目标关节位置，自带 OMPL 运动规划，任务 = 到达 EE 目标位姿。**与浮动基座双足行走不是同一范式，不可继承。**
- 前端 `rcs/frontend/src/views/simulation/`：`MjcfLoader.ts`（仅 **OBJLoader**）、`RobotModelViewer.vue`、`TwinFeed.ts`、`scenes/`（SceneBag/SceneBox/ScenePallet/ScenesPage）。
- 资产经 `/sim-assets/robots/...` 由 vite 代理到 `simulation/backend/assets/`。

### 1.3 三个必须先解决的硬约束

1. **网格格式不兼容**：Microduck 用 `.stl`，`MjcfLoader` 只有 OBJLoader。
2. **前端不支持浮动基座**：`MjcfLoader` 把每个 `<joint>` 当单轴旋转 Group，无 freejoint（6-DOF 位姿）处理。
3. **训练栈不同**：microduck_rl 用 mjlab+CUDA；robot-logic 用 SB3 PPO。

---

## 2. 目标 / 非目标

### 目标

1. 7 个 MJCF 变体全部接入 `MuJoCoEngine` 并可无错 step。
2. 提供符合官方 61 维/14 维契约的双足 locomotion Gym 环境。
3. 浏览器内可看到 Microduck，并随仿真实时运动。
4. 内置 SB3 PPO 可训练；支持导入外部 ONNX 策略直接播放。

### 非目标

- 真机部署（Radxa 主控、Dynamixel 总线、imu_to_dxl 桥接、电源树）。
- CAD 重建与工程件出图。
- BAM M6 电压执行器物理建模（首期不做，见 §8 风险 1）。
- 摄像头 / ToF / 音频 / NFC 等感知扩展。

---

## 3. 架构总览

```
microduck_rl（只读参考源）              robot-logic
────────────────────────────          ────────────────────────────────────────
robot/microduck/*.xml      ──复制─▶  simulation/backend/assets/robots/microduck/
robot/microduck/assets/*.stl ─复制─▶  同上 assets/（43 个 STL）
microduck_constants.py     ──抄录─▶  rcs_env/envs/microduck_cfg.py
                                            │
                        ┌───────────────────┼────────────────────┐
                        ▼                   ▼                    ▼
                  A 模型接入            B 仿真环境             C 前端显示
          configs.py + RobotType.    envs/microduck.py      scenes/SceneMicroduck.vue
          MICRODUCK + 变体注册表      （gym.Env，不继承        + MjcfLoader 扩展：
                                      SimEnv；复用 engine/     STLLoader + freejoint
                                      vec/twin）               + TwinFeed 遥测
                        └───────────────────┼────────────────────┘
                                            ▼
                                    D 训练（双轨）
                          轨1 SB3 PPO（内置）  轨2 ONNX 导入播放
                                            │
                                            ▼
                          envs/twin.py DigitalTwinSink → 前端 50Hz 实时遥测
```

**复用原则**：环境与前端为新增代码；引擎、向量化、遥测、训练脚手架全部复用现有基建。

---

## 4. A · 模型接入

### 4.1 资产落地

将以下复制到 `simulation/backend/assets/robots/microduck/`，保留 `meshdir="assets"` 相对结构：

- 7 个 `robot_*.xml`
- `assets/*.stl`（43 个视觉网格）

`.part` 文件为上游 replica 工具产物，MuJoCo 不引用，**不复制**。

### 4.2 类型与注册表

- `shared/python/robot_contracts/kinematics.py`：`RobotType` 新增 `MICRODUCK = "Microduck"`。
- `rcs_env/envs/configs.py`：新增 `MICRODUCK_VARIANTS` 注册表，字段为：

```python
@dataclass
class MicroduckVariant:
    name: str            # "walk" | "groundcontact" | "allcollisions" | ...
    xml: str             # 相对 assets/robots/microduck 的路径
    home_pose: dict      # 关节名 -> 弧度（见 §7.3）
    passive_joints: tuple  # 该变体的被动关节名前缀，如 ("passive_",)
    n_action: int = 14   # 策略动作维数（被动关节不参与）
```

- 7 个变体注册进 `ENV_FACTORIES`，命名 `microduck_<variant>`。
- **新增变体 = 加一行配置，不改代码。**

### 4.3 backlash 变体的坑

backlash 变体中被动回差关节名为 `passive_<joint>_backlash`，范围仅 ±1°。home pose 的模式匹配是 **first-match-wins**，必须让 `.*_backlash$` 规则**排在最前**并置 0，否则会把伺服关节的 home 值（如 -0.0873 rad）写进回差关节导致越界。

---

## 5. B · 仿真环境

### 5.1 形态

新增 `rcs_env/envs/microduck.py`：`MicroduckEnv(gym.Env)`。

- **不继承 `SimEnv`**（原因见 §1.2）。
- 复用：`MuJoCoEngine`（加载/step/读状态）、`envs/vec.py`（向量化）、`envs/twin.py`（遥测发布）。
- 由变体配置参数化，一个实现覆盖 7 个变体。

### 5.2 时间步

- 仿真 `dt = 0.002`（2 ms）
- 控制周期 `0.02`（50 Hz），即**每 10 个仿真步执行一次策略，期间动作保持**

### 5.3 观测：严格实现官方 61 维契约

见 §7.1。这是能导入官方 ONNX 的前提，字段顺序与单位不可偏离。

### 5.4 动作与映射

见 §7.2。**14 维动作 → 15 槽目标数组**是全局最易错点，必须单测覆盖。

### 5.5 奖励（Velocity 行走任务）

组成与**初始默认权重**（P4 实施时可调，最终值记录进环境配置文件）：

| 类别 | 项 | 初始权重 |
|---|---|---|
| 跟踪 | 线速度 `vx, vy` 跟踪误差（指数核 `exp(-err²/σ)`，σ=0.25） | +1.0 |
| 跟踪 | 角速度 `vyaw` 跟踪误差（指数核） | +0.5 |
| 存活 | 每控制步固定存活奖励 | +0.1 |
| 惩罚 | 躯干偏离直立（`projected_gravity` 水平分量 L2） | -0.2 |
| 惩罚 | 关节接近/越过软限位 | -0.1 |
| 惩罚 | 动作变化率（相邻步 action 差分 L2，平滑） | -0.01 |
| 惩罚 | 力矩 / 能耗 | -0.001 |
| 惩罚 | 足底打滑（接触点水平速度） | -0.05 |

**终止（terminated）**：躯干高度 < **0.15 m**，或躯干倾斜角（`projected_gravity` 与竖直方向夹角）> **60°**。
**截断（truncated）**：达到单回合最大步数（默认 1000 控制步 = 20 s）。

### 5.6 其他任务

`standup` / `rollers` 变体提供 env + 简化奖励骨架（可训，但不承诺调参到收敛）。`allcollisions` 仅接入不配任务。

### 5.7 Domain randomization（SB3 轨，克制使用）

首期最小集合：地面摩擦、躯干质量扰动、观测噪声、随机推力扰动。因 SB3 并行规模小，DR 强度需保守。

---

## 6. C · 前端显示（嵌入现有场景列表）

### 6.1 场景接入

- 新增 `scenes/SceneMicroduck.vue`，结构仿照现有 `SceneBag.vue` / `SceneBox.vue` / `ScenePallet.vue`。
- 在 `ScenesPage.vue` 的场景清单中注册 Microduck 条目。
- 底栏播放控制：播放 / 暂停 / 步进 / 重置 / 策略选择。

### 6.2 `MjcfLoader.ts` 两处扩展（对现有 OBJ 路径无回归）

1. **STLLoader**：three 自带 `examples/jsm/loaders/STLLoader.js`。按扩展名分派——`.stl` → STLLoader，`.obj` → OBJLoader。颜色仍由 MJCF `<material>` 决定（STL 无色，不影响）。
2. **freejoint 支持**：识别 `<freejoint>`，在该 joint Group 上应用 `pos(3)` + `quat(4)`（平移 + 旋转），而非单轴旋转。否则鸭子只能原地扭关节，无法平移/倾斜。

### 6.3 实时遥测

复用 `envs/twin.py` 的 `DigitalTwinSink` 发布 `JointStatePayload` / `TelemetryPayload`，前端 `TwinFeed.ts` 接收并驱动关节（含 freejoint 位姿）。

---

## 7. 数据契约（集中定义，实施以本节为准）

### 7.1 61 维观测布局

| 区间 | 维数 | 内容 | 单位 |
|---|---|---|---|
| 0..3 | 3 | 躯干坐标系角速度 `gyro` | rad/s |
| 3..6 | 3 | 躯干坐标系投影重力 `projected_gravity` | 单位向量 |
| 6..20 | 14 | 关节位置 − home_pose（嘴部除外） | rad |
| 20..34 | 14 | 关节速度（嘴部除外） | rad/s |
| 34..48 | 14 | 上一时刻策略原始输出（缩放前） | — |
| 48..61 | 13 | 命令块 | 见下 |

命令块 = `twist(3) + head_pose(4) + body_pose(6)`：

```
48..51  vx, vy, vyaw            # vx/vy: m/s，vyaw: rad/s
51..55  neck_pitch, head_pitch, head_yaw, head_roll   # rad
55..61  body x, y, z, roll, pitch, yaw                # z: m，roll/pitch: rad
```

运行时把 body 的 `x`、`y`、`yaw` 固定为 0；`z`、`roll`、`pitch` 仅在 body-pose 模式非零。**槽位不可删除**——共享 61 维布局是不同策略可切换的前提。

### 7.2 14 维动作 → 15 槽目标数组

策略动作顺序与总线 ID：

| action | 关节 | 总线 ID |
|---|---|---|
| 0 | 左 hip_yaw | 20 |
| 1 | 左 hip_roll | 21 |
| 2 | 左 hip_pitch | 22 |
| 3 | 左 knee | 23 |
| 4 | 左 ankle | 24 |
| 5 | neck_pitch | 30 |
| 6 | head_pitch | 31 |
| 7 | head_yaw | 32 |
| 8 | head_roll | 33 |
| — | **mouth（不在策略动作中）** | 34 |
| 9 | 右 hip_yaw | 10 |
| 10 | 右 hip_roll | 11 |
| 11 | 右 hip_pitch | 12 |
| 12 | 右 knee | 13 |
| 13 | 右 ankle | 14 |

15 槽电机目标数组布局：

```
[左腿 5 | 头颈 4 | 嘴 1 | 右腿 5]
  0..4     5..8     9      10..14
```

策略动作数组布局：

```
[左腿 5 | 头颈 4 | 右腿 5]
  0..4     5..8      9..13
```

**因此：action 9..13 必须写入 15 槽数组的 index 10..14，绝不可直接写 index 9**（index 9 是嘴）。写错会把右髋命令写到嘴上并让整条右腿错位，且网络仍能正常推理、不易察觉。

### 7.3 home pose（STAND2，抄录自 microduck_constants.HOME_FRAME）

| 关节 | 弧度 |
|---|---|
| `.*hip_yaw.*` | 0.0 |
| `left_hip_roll` | -0.0873 |
| `right_hip_roll` | +0.0873 |
| `left_hip_pitch` | -0.4579 |
| `right_hip_pitch` | +0.4579 |
| `left_knee` | -0.0049 |
| `right_knee` | +0.0049 |
| `left_ankle` | +0.4530 |
| `right_ankle` | -0.4530 |
| `neck_pitch` | 0.3491 |
| `head_pitch` | 0.3491 |
| `head_yaw` | 0.0 |
| `head_roll` | 0.0 |

backlash 变体追加规则：`.*_backlash$` → 0.0，且**置于匹配列表首位**。

### 7.4 ONNX 契约

- 输入形状 `[1, 61]`，输出形状 `[1, 14]`
- 关节顺序与 §7.2 一致
- 观测归一化器已烘入 ONNX
- 推理前做一次 warm-up，避免首帧延迟落入控制周期
- 单次推理须稳定小于控制周期预算（20 ms）

---

## 8. 关键取舍与已知风险

1. **执行器保真度（已接受）**：XML 使用原生 `<position>` 执行器，而官方策略由 **BAM M6 电压模型 + domain randomization** 训练。用 position 执行器运行官方 ONNX **存在域差异**，可能仍能行走但不保证质量。首期按此实施；BAM 建模列为后续可选项。
2. **SB3 步态质量（已接受）**：双足行走 RL 对并行规模极敏感。CPU 上 SB3 PPO 训练 14-DoF 双足，行走步态大概率不如官方策略；站立/平衡类任务可行。这正是采用「双轨」的原因——轨 2（ONNX 导入）兜底高质量演示。
3. **工作量（已接受）**：全量 7 变体 + 4 模块，是本项目当前最大改动。按 §9 分期提交，每期可独立验收。
4. **新增依赖**：后端 `onnxruntime`；前端无新依赖（STLLoader 已在 three 内）。

---

## 9. 分期与验收

本 spec 覆盖完整方案（A+B+C+D）。实施按 **P1–P5 分期推进**，每期独立验收通过后再进入下一期；单期内失败不阻塞已完成部分。

| 期 | 内容 | 验收标准 |
|---|---|---|
| **P1** | A 模型接入 + 7 变体注册表 | `MuJoCoEngine` 可加载全部 7 个 MJCF 并无错 step；`get_config("microduck_walk")` 可用 |
| **P2** | B 仿真 env（61/14 契约 + 映射） | 单测覆盖 action→15 槽映射（含嘴部槽位与 backlash home 置 0）；随机策略可跑通 |
| **P3** | C 前端显示（STL + freejoint + 场景 + 遥测） | 浏览器内可见 Microduck，并随仿真实时运动（含整体平移/倾斜） |
| **P4** | D1 SB3 训练 | PPO 可训练，站立/行走指标可在日志中观测 |
| **P5** | D2 ONNX 导入播放 | 外部 ONNX 可加载并驱动鸭子行走 |

---

## 10. 影响面与注意事项

- **改动文件**：`robot_contracts/kinematics.py`（加枚举）、`rcs_env/envs/configs.py`（注册表）、新增 `rcs_env/envs/microduck.py` 与 `microduck_cfg.py`、`rcs_env/training/train_microduck.py`、新增 ONNX wrapper、新增 `assets/robots/microduck/**`、前端 `MjcfLoader.ts`（加 STL/freejoint）、新增 `scenes/SceneMicroduck.vue`、`ScenesPage.vue`（注册）。
- **不改动**：`SimEnv` / `ModelComposer` / `MuJoCoEngine` 的既有行为；现有 OBJ 机器人的加载路径保持不变。
- **测试**：`rcs_env/tests/` 下新增映射契约单测；`MjcfLoader.spec.ts` 扩展 STL 与 freejoint 用例。

---

## 附录：参考来源

- `docs/microduck.md` —— X 长文「如何从零 DIY 复刻一只可爱的 Microduck」整理版（含 61 维契约、关节顺序、BOM、调试流程）
- `d:\projects\github\microduck_rl` —— 官方 MJCF、`microduck_constants.py`（home pose）、mjlab 任务与 BAM 执行器定义
