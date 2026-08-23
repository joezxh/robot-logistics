# 端到端仿真闭环优化设计方案

**日期**：2026-08-20
**状态**：设计阶段
**负责人**：robot-logic 对齐改造

## 1. 背景与目标

### 1.1 问题陈述

当前 `robot-logic` 的四个子工程（`rcs`、`robot-app`、`vla-training`、`simulation`）已完成基础 RCS 对齐，但端到端仿真闭环存在以下瓶颈：

| 组件 | 当前状态 | 问题 |
|------|----------|------|
| **PhysicsEngine** | `LogicEngine` 简化 FK | 无真实动力学/碰撞检测 |
| **CameraSetWrapper** | 返回零帧 | VLA 无法获取视觉输入 |
| **VLA 推理** | `VLAPolicy._load_model` stub | 无法真实推理 |
| **遥操作采集** | 无实现 | 无法采集演示数据 |

### 1.2 目标

实现从遥操作采集 → 仿真环境 → VLA 推理 → 策略评估的完整闭环，参考 `robot-control-stack` 的架构设计。

## 2. 技术选型

### 2.1 仿真引擎：混合模式

| 模式 | 实现 | 适用场景 |
|------|------|----------|
| **LogicEngine** | 纯 Python 简化 FK | 快速验证、无 MuJoCo 依赖 |
| **MuJoCoEngine** | MuJoCo 高保真物理 | 需要碰撞检测、真实动力学 |

工厂函数优先选择 MuJoCo（当可用时）。

### 2.2 VLA 推理：双模支持

| 模式 | 实现 | 适用场景 |
|------|------|----------|
| **ScriptedPolicy** | 脚本化基线策略 | 快速验证、单元测试 |
| **VLAPolicy** | HuggingFace Transformers 模型 | 真实 VLA 推理 |

### 2.3 遥操作：操作器抽象

支持多种操作器输入：
- **键盘适配器**：通用、零依赖
- **SpaceMouse 适配器**：高精度遥操作

## 3. 架构设计

### 3.1 系统架构

```mermaid
graph TB
    subgraph APP["robot-app/rcs_layer"]
        TASKS[LogisticsTask<br/>PalletTask]
        TELEOP[TeleopCollector<br/>SpaceMouse/Keyboard]
        VLA[VLAInferenceEngine<br/>ScriptedPolicy | VLAPolicy]
    end
    
    subgraph SIM["simulation/rcs_env"]
        ENG[PhysicsEngine 抽象层]
        LOGIC[LogicEngine<br/>纯 Python FK]
        MJ[MuJoCoEngine<br/>可选依赖]
        WRAPS[RobotWrapper<br/>GripperWrapper<br/>CameraSetWrapper<br/>TaskWrapper]
        RENDER[SimRenderer<br/>MuJoCo offscreen]
    end
    
    subgraph TRAIN["vla-training"]
        COLLECT[SimulationCollector<br/>真实采集]
        EVAL[evaluate_closed_loop<br/>闭环评估]
    end
    
    ENG --> LOGIC
    ENG --> MJ
    WRAPS --> RENDER
    TELEOP --> COLLECT
    COLLECT --> VLA
    VLA --> SIM
    SIM --> TASKS
    TASKS --> EVAL
    EVAL --> VLA
```

### 3.2 数据流

```
SpaceMouse/Keyboard → TeleopCollector
         ↓
    动作 (np.ndarray)
         ↓
    SimEnv.step(action)
         ↓
    observation (dict) ← CameraSetWrapper 注入 RGB/Depth
         ↓
    VLAInferenceEngine.predict(obs)
         ↓
    下一动作
```

## 4. 接口设计

### 4.1 SimRenderer 相机渲染

**文件**：`simulation/backend/rcs_env/renderer.py`

```python
class SimRenderer:
    """MuJoCo offscreen 渲染器
    
    当 MuJoCo 可用时提供真实 RGB/Depth 渲染，
    否则返回零帧占位。
    """
    
    def __init__(self, mj_model, mj_data, camera_name: str = "default"):
        self._model = mj_model
        self._data = mj_data
        self._camera_name = camera_name
        self._width = 320
        self._height = 240
        
    def render(self) -> dict[str, np.ndarray]:
        """渲染当前帧
        
        Returns:
            dict: {"rgb": HxWx3 uint8, "depth": HxWx1 float32}
        """
        # 1. 查找相机 ID
        # 2. 配置 mjrContext
        # 3. offscreen 渲染
        # 4. 读取缓冲区
        ...
        
    @staticmethod
    def available() -> bool:
        """检查 MuJoCo 渲染是否可用"""
        try:
            import mujoco
            return hasattr(mujoco, "mjr_readPixels")
        except ImportError:
            return False
```

### 4.2 CameraSetWrapper 增强

**文件**：`simulation/backend/rcs_env/envs/wrappers.py`

```python
class CameraSetWrapper(gym.Wrapper):
    """相机观测注入包装器
    
    支持两种模式：
    - 有 SimRenderer：真实 RGB/Depth 渲染
    - 无 SimRenderer：零帧占位（保持兼容性）
    """
    
    RGB_KEY = "rgb"
    DEPTH_KEY = "depth"
    
    def __init__(
        self, 
        env: gym.Env, 
        renderer: SimRenderer | None = None,
        height: int = 240, 
        width: int = 320,
        include_depth: bool = True,
    ):
        super().__init__(env)
        self._renderer = renderer
        self.height = height
        self.width = width
        self.include_depth = include_depth
        
        self.observation_space = gym.spaces.Dict({
            "state": env.observation_space,
            self.RGB_KEY: gym.spaces.Box(
                low=0, high=255, 
                shape=(height, width, 3), 
                dtype=np.uint8
            ),
        })
        if include_depth:
            self.observation_space.spaces[self.DEPTH_KEY] = gym.spaces.Box(
                low=0.0, high=10.0,
                shape=(height, width, 1),
                dtype=np.float32
            )
            
    def _render_frames(self) -> dict:
        if self._renderer is None:
            return {
                self.RGB_KEY: np.zeros(
                    (self.height, self.width, 3), dtype=np.uint8
                ),
                self.DEPTH_KEY: np.zeros(
                    (self.height, self.width, 1), dtype=np.float32
                ) if self.include_depth else np.array([[[0.0]]]),
            }
        return self._renderer.render()
```

### 4.3 VLAInferenceEngine

**文件**：`robot-app/rcs_layer/vla/inference_engine.py`

```python
class VLAInferenceEngine:
    """VLA 推理引擎
    
    支持两种策略：
    - ScriptedPolicy：快速验证
    - VLAPolicy：真实模型推理
    """
    
    def __init__(
        self,
        model_path: str | Path | None = None,
        device: str = "cuda",
        action_dim: int = 6,
        robot_type: str = "ARM",
    ):
        self._policy = load_policy(
            path=str(model_path) if model_path else None,
            kind="vla" if model_path else "scripted",
            action_dim=action_dim,
            robot_type=robot_type,
            device=device,
        )
        
    def predict(self, obs: dict) -> np.ndarray:
        """从 observation 预测动作
        
        Args:
            obs: Gymnasium observation dict，包含：
                - state: 关节状态
                - rgb: RGB 图像（可选）
                - depth: 深度图像（可选）
                
        Returns:
            np.ndarray: 动作向量
        """
        return self._policy(obs)
        
    def reset(self) -> None:
        """重置策略状态"""
        self._policy.reset()
        
    def __call__(self, obs: dict) -> np.ndarray:
        return self.predict(obs)


def load_policy(
    path: str | None = None,
    kind: str = "scripted",
    **kwargs
) -> Policy:
    """策略加载工厂"""
    if path is None or kind == "scripted":
        return ScriptedPolicy(**kwargs)
    if kind == "vla":
        return VLAPolicy(path, **kwargs)
    raise ValueError(f"unknown policy kind: {kind}")
```

### 4.4 TeleopCollector

**文件**：`robot-app/rcs_layer/teleop/collector.py`

```python
from dataclasses import dataclass
from typing import Protocol


class Operator(Protocol):
    """操作器协议"""
    def get_action(self, obs: dict) -> np.ndarray: ...


@dataclass
class EpisodeData:
    """采集的 episode 数据"""
    observations: list[dict]
    actions: list[np.ndarray]
    rewards: list[float]
    task_success: bool
    task_name: str = ""


class TeleopCollector:
    """遥操作数据采集器"""
    
    def __init__(
        self, 
        operator: Operator,
        env: gym.Env,
        task: LogisticsTask,
    ):
        self.operator = operator
        self.env = env
        self.task = task
        
    def collect_episode(self) -> EpisodeData:
        """采集一个演示 episode
        
        Returns:
            EpisodeData: 包含完整 episode 数据
        """
        obs, _ = self.env.reset()
        self.task.reset()
        
        observations = []
        actions = []
        rewards = []
        
        while not self.task.done({}):
            # 操作器输入
            op_action = self.operator.get_action(obs)
            
            # 环境 step
            obs, reward, terminated, truncated, info = self.env.step(op_action)
            
            observations.append(obs)
            actions.append(op_action)
            rewards.append(reward)
            
            if terminated or truncated:
                break
                
        return EpisodeData(
            observations=observations,
            actions=actions,
            rewards=rewards,
            task_success=self.task.done({}),
            task_name=self.task.name,
        )
        
    def collect_dataset(
        self, 
        num_episodes: int,
        save_dir: Path,
    ) -> list[EpisodeData]:
        """采集多个 episode 并保存
        
        Args:
            num_episodes: 采集 episode 数量
            save_dir: 保存目录
            
        Returns:
            list[EpisodeData]: 所有采集的 episode
        """
        save_dir.mkdir(parents=True, exist_ok=True)
        episodes = []
        
        for i in range(num_episodes):
            episode = self.collect_episode()
            episodes.append(episode)
            
            # 保存单个 episode
            np.savez(
                save_dir / f"episode_{i:04d}.npz",
                observations=episode.observations,
                actions=np.array(episode.actions),
                rewards=np.array(episode.rewards),
            )
            
        return episodes
```

### 4.5 KeyboardOperator

**文件**：`robot-app/rcs_layer/teleop/keyboard.py`

```python
class KeyboardOperator:
    """键盘遥操作适配器
    
    按键映射：
    - W/S: X 方向
    - A/D: Y 方向
    - Q/E: Z 方向
    - J/L: Roll
    - I/K: Pitch
    - N/M: Yaw
    - G: 夹爪闭合
    - H: 夹爪张开
    """
    
    def __init__(self, action_dim: int = 6, step_size: float = 0.05):
        self.action_dim = action_dim
        self.step_size = step_size
        self._current_action = np.zeros(action_dim)
        self._gripper = 0.0
        self._running = False
        
    def get_action(self, obs: dict) -> np.ndarray:
        """获取当前动作（需要外部调用 key_handler）"""
        return self._current_action.copy()
        
    def key_handler(self, key: str) -> None:
        """处理按键事件"""
        step = self.step_size
        if key == "w": self._current_action[0] += step
        elif key == "s": self._current_action[0] -= step
        elif key == "a": self._current_action[1] += step
        elif key == "d": self._current_action[1] -= step
        elif key == "q": self._current_action[2] += step
        elif key == "e": self._current_action[2] -= step
        elif key == "g": self._gripper = 0.0  # 闭合
        elif key == "h": self._gripper = 1.0  # 张开
            
    def start(self) -> None:
        self._running = True
        
    def stop(self) -> None:
        self._running = False
```

## 5. 文件结构

```
robot-logic/
├── simulation/
│   └── backend/
│       └── rcs_env/
│           ├── renderer.py          # [NEW] SimRenderer
│           └── envs/
│               └── wrappers.py     # [MODIFY] CameraSetWrapper 增强
│
├── robot-app/
│   └── rcs_layer/
│       ├── vla/
│       │   ├── inference_engine.py # [NEW] VLAInferenceEngine
│       │   └── policy.py          # [MODIFY] VLAPolicy 真实化
│       └── teleop/
│           ├── collector.py        # [NEW] TeleopCollector
│           ├── operator.py        # [NEW] Operator 协议
│           └── keyboard.py        # [NEW] KeyboardOperator
│
└── vla-training/
    └── src/vla_training/
        ├── data/
        │   └── collector.py        # [MODIFY] SimulationCollector 真实化
        └── eval/
            └── evaluate.py         # [MODIFY] evaluate_closed_loop 真实化
```

## 6. 依赖

### 6.1 simulation/pyproject.toml

```toml
[project.optional-dependencies]
mujoco = ["mujoco>=3.0"]
camera = ["mujoco>=3.0"]
all = ["mujoco>=3.0"]
```

### 6.2 robot-app/pyproject.toml

```toml
[project.optional-dependencies]
vla = ["transformers", "torch"]
teleop = ["pyspacemouse"]
all = ["transformers", "torch", "pyspacemouse"]
```

## 7. 测试验证

### 7.1 单元测试

```python
# simulation/tests/test_rcs_env.py
def test_camera_wrapper_with_renderer():
    """CameraSetWrapper + SimRenderer 集成测试"""
    from rcs_env.renderer import SimRenderer
    from rcs_env.envs.wrappers import CameraSetWrapper
    
    # 跳过无 MuJoCo 环境
    if not SimRenderer.available():
        pytest.skip("MuJoCo not available")
    
    # 创建渲染器
    import mujoco
    model = mujoco.MjModel.from_xml_string(SIMPLE_XML)
    data = mujoco.MjData(model)
    renderer = SimRenderer(model, data)
    
    # 创建环境
    env = SimEnv(...)
    env = CameraSetWrapper(env, renderer=renderer)
    obs, _ = env.reset()
    
    assert "rgb" in obs
    assert obs["rgb"].shape == (240, 320, 3)
    assert not np.all(obs["rgb"] == 0)  # 非零帧


# robot-app/tests/test_vla_inference.py
def test_vla_inference_engine_scripted():
    """ScriptedPolicy 推理测试"""
    from rcs_layer.vla.inference_engine import VLAInferenceEngine
    
    engine = VLAInferenceEngine(action_dim=6)
    obs = {"state": np.zeros(14)}
    action = engine.predict(obs)
    
    assert action.shape == (6,)
    assert isinstance(action, np.ndarray)


def test_teleop_collector():
    """遥操作采集测试"""
    from rcs_layer.teleop.collector import TeleopCollector
    from rcs_layer.teleop.keyboard import KeyboardOperator
    
    class MockEnv:
        def reset(self): 
            return {"state": np.zeros(14)}, {}
        def step(self, action):
            return {"state": np.zeros(14)}, 0.0, False, False, {}
            
    class MockTask:
        name = "test"
        def done(self, _): return False
        def reset(self): pass
    
    operator = KeyboardOperator()
    env = MockEnv()
    task = MockTask()
    
    collector = TeleopCollector(operator, env, task)
    episode = collector.collect_episode()
    
    assert len(episode.actions) > 0
```

### 7.2 集成测试

```python
# simulation/tests/test_integration.py
def test_end_to_end_loop():
    """端到端闭环测试"""
    # 1. 创建环境
    env = make_env(has_camera=True)
    env = TaskWrapper(env, PalletTask())
    
    # 2. 创建 VLA 推理引擎
    engine = VLAInferenceEngine(action_dim=6)
    
    # 3. 运行 episode
    obs, _ = env.reset()
    engine.reset()
    
    for _ in range(100):
        action = engine.predict(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        
        if terminated or truncated:
            break
            
    # 4. 验证
    assert "rgb" in obs
    assert isinstance(reward, float)
```

## 8. 实施计划

| 阶段 | 任务 | 产出 | 优先级 |
|------|------|------|--------|
| **1a** | 实现 `SimRenderer` 类 | 相机渲染能力 | P0 |
| **1b** | 增强 `CameraSetWrapper` | 带渲染器的观测注入 | P0 |
| **2a** | 实现 `VLAInferenceEngine` | 推理引擎 + ScriptedPolicy | P0 |
| **2b** | 完善 `VLAPolicy` | HuggingFace 模型加载 | P1 |
| **3a** | 实现 `TeleopCollector` | 数据采集接口 | P1 |
| **3b** | 实现 `KeyboardOperator` | 键盘遥操作 | P2 |
| **4** | 集成测试 | 完整闭环验证 | P1 |

## 9. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| MuJoCo 渲染依赖 | 某些环境无 GPU | 提供零帧回退，保持兼容性 |
| VLA 模型格式 | 不同模型格式差异 | Manifest 标准化 + 类型校验 |
| 操作器驱动 | SpaceMouse SDK 兼容性 | 键盘适配器作为通用回退 |

## 10. 验收标准

- [ ] `SimRenderer` 在有 MuJoCo 时渲染真实 RGB/Depth
- [ ] `CameraSetWrapper` 在无渲染器时返回零帧占位
- [ ] `VLAInferenceEngine` 支持 ScriptedPolicy 和 VLAPolicy 切换
- [ ] `TeleopCollector` 可采集完整 episode 数据
- [ ] 端到端闭环测试通过

## 11. 参考

- RCS `python/rcs/envs/base.py` - CameraSetWrapper 参考
- RCS `python/rcs/camera/sim.py` - 相机仿真参考
- RCS `python/rcs/operator/` - 操作器接口参考
- CodeBuddy 对齐报告 `docs/rcs-alignment-report.md`
