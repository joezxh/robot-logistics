# robot-logic × robot-control-stack 深度对齐优化分析报告

**日期**：2026-08-20  
**范围**：`rcs` / `robot-app` / `vla-training` / `simulation` 四个子工程深度对齐 RCS  
**数据来源**：CodeBuddy 执行结果 + RCS 源码分析（`python/rcs` + `extensions/` + C++ 核心库）

---

## 1. 现状评估

### 1.1 CodeBuddy 已完成工作 ✅

| 子工程 | 完成度 | 关键实现 |
|--------|--------|----------|
| `shared/` | 95% | `Pose` (xyzw)、`RobotType`、`世界↔基座` 变换 |
| `simulation/rcs_env` | 80% | `PhysicsEngine` 抽象、`LogicEngine`/`MuJoCoEngine`、`MjOMPL`、Gymnasium wrappers |
| `rcs/` | 85% | `RobotType` 注册、`ControlMode` 枚举、`HAL` 抽象 |
| `robot-app/rcs_layer` | 60% | `LogisticsTask` 基类、`Policy`/`VLAPolicy` 抽象 |
| `vla-training/` | 50% | `InferenceManifest` + `robot_type`、模型导出框架 |

### 1.2 RCS 原生能力对照

```
RCS 原生能力                          | robot-logic 对齐状态
--------------------------------------|----------------------
C++ Pinocchio 运动学 (Kinematics.cpp) | ❌ 未实现 (仅 Python FK/IK)
MuJoCo 高保真仿真                     | ⚠️ 框架存在, MJCF 模型缺失
OMPL 原生绑定 (ompl::geometric)       | ⚠️ 仅纯 Python 采样规划器
MultiRobotWrapper (多机协调)          | ❌ 未实现
greenlet 并发仿真循环                  | ❌ 未实现
CameraSetWrapper 真实相机渲染          | ⚠️ 仅零帧占位
extensions/ 插件化扩展                 | ⚠️ 框架存在, 注册机制不完整
RPC 通信层 (rcs/rpc/)                | ❌ 未实现
遥操作采集 (teleop)                   | ⚠️ 仅设备抽象, 无采集链路
```

---

## 2. 深度优化方案

### 2.1 simulation 优化

#### 2.1.1 MJCF 模型补全

**现状**：`LogicEngine.forward_kinematics` 仅用简单近似公式，无真实动力学。

**优化方案**：

```python
# simulation/backend/rcs_env/models/  新增目录
"""
ARM/AGV/STACKER 的 MuJoCo MJCF 模型
"""
```

| 模型 | 关键要素 |
|------|----------|
| `arm_arm7.xml` | 6-DoF 关节链、collision geoms、TCP site |
| `agv_diff_drive.xml` | 差速驱动轮系、地面接触 |
| `stacker_telescopic.xml` | 伸缩柱关节、门架结构 |

**RCS 参考**：`robot-control-stack` 的 `src/sim/` 使用 `ModelComposer` 组合模型。

#### 2.1.2 CameraSetWrapper 真实渲染

**现状**：`CameraSetWrapper._render_frames` 返回零帧。

**优化方案**：

```python
# 新增 simulation/backend/rcs_env/renderer.py
class SimRenderer:
    """对接 MuJoCo 的 offscreen 渲染"""
    
    def render(self, camera_name: str, width: int, height: int) -> dict:
        """返回 {'rgb': np.ndarray, 'depth': np.ndarray}"""
        # 1. 设置相机视角
        # 2. mujoco.MjvScene / mjrContext 渲染
        # 3. 读取像素数据
```

**RCS 参考**：`robot-control-stack/python/rcs/camera/sim.py`

#### 2.1.3 Pinocchio 运动学集成（可选）

**现状**：无 C++ 运动学库依赖。

**优化方案**：若需要高精度 IK，可引入 `pinocchio`：

```bash
pip install pin
```

```python
# simulation/backend/rcs_env/kinematics.py
class PinocchioKinematics:
    """基于 Pinocchio 的解析 IK/FK"""
    
    def forward(self, q: np.ndarray) -> Pose:
        """Pinocchio FK"""
        
    def inverse(self, target: Pose, q_init: np.ndarray) -> np.ndarray:
        """Pinocchio IK"""
```

### 2.2 rcs 优化

#### 2.2.1 HAL base_pose 完善

**现状**：`SimHAL.base_pose()` 在 `registry.py` 中是可选回退。

**优化方案**：

```python
# rcs/rcs/hal/protocol.py
class DeviceHAL(Protocol):
    def base_pose(self, device_id: str) -> Pose:
        """返回设备基座在 world 系中的位姿"""
        ...
```

#### 2.2.2 控制模式完整性

**现状**：`ControlMode` 包含 JOINT/CARTESIAN/TQUAT/RELATIVE。

**RCS 对齐**：RCS `ControlMode` 支持：
- `JOINTS` - 关节位置控制
- `CARTESIAN_TRPY` - 笛卡尔 RPY 姿态
- `CARTESIAN_TQuat` - 笛卡尔四元数姿态

**优化**：考虑增加 `VELOCITY` / `TORQUE` 控制模式，支持力控场景。

#### 2.2.3 多机器人协调

**RCS 参考**：`MultiRobotWrapper` 支持多机协调控制。

**优化方案**：

```python
# rcs/rcs/control_multi.py
class MultiRobotController:
    """多机器人协调控制"""
    
    def __init__(self, robots: dict[str, Controller]):
        self.robots = robots
        
    def sync_step(self, actions: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        """同步执行多机动作"""
```

### 2.3 robot-app 优化

#### 2.3.1 VLA 推理链路完善

**现状**：`VLAPolicy` 模型加载为 stub。

**优化方案**：

```python
# robot-app/rcs_layer/vla/loader.py
class VLAInferenceEngine:
    """完整的 VLA 推理引擎"""
    
    def __init__(self, model_path: Path, device: str = "cuda"):
        self._load_model(model_path)
        
    def predict(self, obs: dict) -> np.ndarray:
        """从 SimEnv observation 预测动作"""
        # 1. 提取图像 (通过 CameraSetWrapper)
        # 2. 编码观察
        # 3. 模型推理
        # 4. 解码动作
```

#### 2.3.2 遥操作采集链路

**RCS 参考**：`robot-control-stack/python/rcs/operator/` 包含 Quest/SpaceMouse 操作器。

**优化方案**：

```python
# robot-app/rcs_layer/teleop/
class TeleopCollector:
    """遥操作数据采集"""
    
    def __init__(self, operator: "Operator", env: gym.Env):
        self.operator = operator
        self.env = env
        
    def collect_episode(self, task: LogisticsTask) -> list[dict]:
        """采集一个演示episode"""
        episodes = []
        obs, _ = self.env.reset()
        while not task.done({}):
            action = self.operator.get_action(obs)
            obs, reward, terminated, truncated, info = self.env.step(action)
            episodes.append({"obs": obs, "action": action, "reward": reward})
        return episodes
```

#### 2.3.3 ROS2 集成完善

**现状**：robot-app 有 ROS2 workspace 但集成不完整。

**优化方案**：

```python
# robot-app/ros2_ws/src/robot_decision/robot_decision/
class RCSBridge:
    """RCS 控制层 ↔ ROS2 通信桥"""
    
    def __init__(self, rcs_controller: Controller):
        self.rcs = rcs_controller
        self._setup_ros2_topics()
        
    def rcs_to_ros2(self, state: dict) -> JointState:
        """RCS 状态 → ROS2 JointState"""
        
    def ros2_to_rcs(self, cmd: JointTrajectory) -> np.ndarray:
        """ROS2 指令 → RCS 动作"""
```

### 2.4 vla-training 优化

#### 2.4.1 数据采集真实化

**现状**：`SimulationCollector` 为 stub。

**优化方案**：

```python
# vla-training/src/vla_training/data/collector.py
class RealSimulationCollector:
    """真实 SimEnv 数据采集器"""
    
    def __init__(self, sim_env: SimEnv, policy: Policy):
        self.env = sim_env
        self.policy = policy
        
    def collect(
        self, 
        num_episodes: int,
        task: LogisticsTask,
        save_dir: Path
    ) -> DatasetManifest:
        """采集并保存演示数据"""
        for ep in range(num_episodes):
            episode_data = self._collect_episode(task)
            self._save_episode(episode_data, save_dir / f"episode_{ep}.npz")
        return self._compute_stats(save_dir)
```

#### 2.4.2 闭环评估

**现状**：`evaluate.py` 为 stub。

**优化方案**：

```python
# vla-training/src/vla_training/eval/evaluate.py
def evaluate_closed_loop(
    env: SimEnv,
    policy: Policy,
    num_episodes: int = 100
) -> EvalResult:
    """在 SimEnv 上评估策略"""
    successes = []
    for ep in range(num_episodes):
        obs, _ = env.reset()
        policy.reset()
        terminated = False
        while not terminated:
            action = policy(obs)
            obs, reward, terminated, truncated, info = env.step(action)
        successes.append(info.get("task_success", False))
    
    return EvalResult(
        success_rate=sum(successes) / len(successes),
        avg_episode_length=...,
    )
```

#### 2.4.3 训练流程完善

**RCS 参考**：`robot-control-stack` 无内置训练，但 `vla-training` 应支持：
- 模仿学习 (BC)
- 离线 RL (IQL/CQL)
- 视觉-动作模型 (VLA)

**优化方案**：

```python
# vla-training/src/vla_training/train/finetune.py
class VLATrainer:
    """VLA 微调训练器"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        
    def train(self, dataset: Dataset, output_dir: Path):
        """完整训练流程"""
        # 1. 数据预处理
        # 2. 模型初始化
        # 3. 训练循环
        # 4. Checkpoint 保存
        # 5. WandB/MLFlow 日志
```

### 2.5 Monorepo 基础设施完善

#### 2.5.1 扩展注册机制

**RCS 参考**：`extensions/` 包模式。

**优化方案**：

```python
# shared/python/robot_contracts/extensions.py
class ExtensionRegistry:
    """RCS 风格扩展注册表"""
    
    _extensions: dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, ext_type: type):
        cls._extensions[name] = ext_type
        
    @classmethod
    def create(cls, name: str, **kwargs):
        return cls._extensions[name](**kwargs)

# 用法
@ExtensionRegistry.register("arm_7dof")
class Arm7DoF(RobotInterface): ...
```

#### 2.5.2 CI/CD 流水线

**现状**：无 GitHub Actions 配置。

**优化方案**：`.github/workflows/` 目录：

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e shared/
          pip install -e rcs/
          pip install -e simulation/
          pip install -e robot-app/
          pip install -e vla-training/
      - name: Run tests
        run: make test-all
      - name: Lint
        run: make lint
```

#### 2.5.3 文档生成

**RCS 参考**：Sphinx 文档站点。

**优化方案**：

```python
# docs/conf.py
project = "robot-logic"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]
```

---

## 3. 优先级排序

### P0 - 必须完成（阻塞集成）

| 任务 | 负责子工程 | 依赖 |
|------|-----------|------|
| MJCF ARM/AGV/STACKER 模型 | simulation | RCS 资产库参考 |
| CameraSetWrapper 真实渲染 | simulation | MuJoCo offscreen API |
| VLA 推理引擎真实化 | robot-app | vla-training 导出 |

### P1 - 高优先级（核心能力）

| 任务 | 负责子工程 | 依赖 |
|------|-----------|------|
| SimEnv ↔ rcs 控制桥 | simulation + rcs | shared Pose |
| 遥操作数据采集链路 | robot-app | SimEnv |
| 仿真数据采集真实化 | vla-training | SimEnv + VLA |
| HAL base_pose 完善 | rcs | shared Pose |

### P2 - 中优先级（体验优化）

| 任务 | 负责子工程 | 依赖 |
|------|-----------|------|
| MultiRobotWrapper | simulation | RCS MultiRobotWrapper 参考 |
| Pinocchio 运动学（可选） | simulation | C++ 构建链 |
| CI/CD 流水线 | Monorepo | 测试完成 |
| 文档站点 | Monorepo | API 稳定 |

### P3 - 低优先级（长期规划）

| 任务 | 负责子工程 | 依赖 |
|------|-----------|------|
| ROS2 深度集成 | robot-app | ROS2 环境 |
| 离线 RL 训练 | vla-training | 仿真数据 |
| 硬件扩展包 | rcs + simulation | 真实硬件 |

---

## 4. 实施路径建议

### 阶段 1：仿真闭环（P0）
```
simulation/rcs_env → 添加 ARM MJCF → CameraSetWrapper 渲染
                         ↓
                 SimEnv 可视化验证
                         ↓
robot-app/rcs_layer → VLA 推理链路
```

### 阶段 2：数据链路（P1）
```
robot-app/teleop → 遥操作采集
                         ↓
vla-training/data → SimulationCollector 真实化
                         ↓
vla-training/eval → 闭环评估
```

### 阶段 3：多机与集成（P2）
```
simulation/ → MultiRobotWrapper
                    ↓
rcs/ → 多机协调 HAL
                    ↓
CI/CD → 自动化测试
```

---

## 5. 关键参考文件

### RCS 源码
- `python/rcs/envs/base.py` - Gymnasium wrappers 实现
- `python/rcs/sim/sim.py` - MuJoCo Sim 封装
- `python/rcs/ompl/mj_ompl.py` - OMPL 规划器
- `include/rcs/Robot.h` - C++ Robot 接口

### robot-logic 当前实现
- `shared/python/robot_contracts/kinematics.py` - 共享 Pose/RobotType
- `simulation/backend/rcs_env/engine.py` - 引擎抽象
- `rcs/rcs/state/profile.py` - 设备配置
- `robot-app/rcs_layer/vla/policy.py` - 策略抽象

---

## 6. 总结

CodeBuddy 的计划执行质量高，核心对齐层（Pose/RobotType/控制接口）已完成。剩余优化主要集中在：

1. **仿真保真度**：MJCF 模型 + 相机渲染
2. **数据闭环**：采集 → 训练 → 推理全链路
3. **多机能力**：MultiRobotWrapper
4. **工程基础设施**：CI/CD、文档

建议按优先级分阶段实施，优先确保 P0 任务完成以解除阻塞。
