# 端到端仿真闭环实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现从遥操作采集 → 仿真环境 → VLA 推理 → 策略评估的完整闭环，包括 SimRenderer 相机渲染、VLAInferenceEngine 推理引擎和 TeleopCollector 数据采集。

**Architecture:** 采用混合仿真引擎（LogicEngine 纯 Python 回退 + MuJoCoEngine 高保真），VLA 双模推理（ScriptedPolicy 快速验证 + VLAPolicy 真实模型），遥操作通过操作器抽象支持多种输入设备。

**Tech Stack:** Python 3.10+, MuJoCo 3.0+, Gymnasium, numpy, torch, transformers

## Global Constraints

- Python >= 3.10（使用 `from __future__ import annotations`）
- MuJoCo >= 3.0（可选依赖，提供 `available()` 回退）
- 所有新增模块需添加 `__all__` 导出
- 测试文件放置在 `tests/` 目录

---

## 1. SimRenderer 相机渲染器

### 1.1 SimRenderer 基础实现

**Files:**
- Create: `simulation/backend/rcs_env/renderer.py`
- Test: `simulation/backend/tests/test_renderer.py`

**Interfaces:**
- Produces: `class SimRenderer` with `render()` method returning `{"rgb": HxWx3 uint8, "depth": HxWx1 float32}`
- Produces: `SimRenderer.available() -> bool` static method

- [ ] **Step 1: 编写失败测试**

```python
# simulation/backend/tests/test_renderer.py
import numpy as np
import pytest

def test_sim_renderer_available():
    """Test SimRenderer.available() returns boolean"""
    from rcs_env.renderer import SimRenderer
    result = SimRenderer.available()
    assert isinstance(result, bool)


def test_sim_renderer_returns_dict():
    """Test SimRenderer.render() returns rgb/depth dict when available"""
    from rcs_env.renderer import SimRenderer
    
    if not SimRenderer.available():
        pytest.skip("MuJoCo not available")
    
    import mujoco
    model = mujoco.MjModel.from_xml_string("""
    <mujoco model="test">
        <worldbody>
            <body name="test_body" pos="0 0 0.5">
                <geom type="box" size="0.1 0.1 0.1"/>
            </body>
        </worldbody>
    </mujoco>
    """)
    data = mujoco.MjData(model)
    renderer = SimRenderer(model, data, camera_name="default")
    
    result = renderer.render()
    
    assert "rgb" in result
    assert "depth" in result
    assert isinstance(result["rgb"], np.ndarray)
    assert result["rgb"].dtype == np.uint8
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd D:/projects/robot-logic/simulation && python -m pytest backend/tests/test_renderer.py -v`
Expected: FAIL - module 'rcs_env.renderer' has no attribute 'SimRenderer'

- [ ] **Step 3: 编写最小实现**

```python
# simulation/backend/rcs_env/renderer.py
"""SimRenderer - MuJoCo offscreen 渲染器

提供 RGB/Depth 帧渲染能力，当 MuJoCo 不可用时返回零帧占位。
"""
from __future__ import annotations

from typing import Any

import numpy as np


class SimRenderer:
    """MuJoCo offscreen 渲染器
    
    当 MuJoCo 可用时提供真实 RGB/Depth 渲染，
    否则返回零帧占位以保持兼容性。
    """
    
    def __init__(
        self, 
        mj_model, 
        mj_data, 
        camera_name: str = "default",
        width: int = 320, 
        height: int = 240,
    ):
        self._model = mj_model
        self._data = mj_data
        self._camera_name = camera_name
        self._width = width
        self._height = height
        
    def render(self) -> dict[str, np.ndarray]:
        """渲染当前帧
        
        Returns:
            dict: {"rgb": HxWx3 uint8, "depth": HxWx1 float32}
        """
        if not self.available():
            return self._zero_frames()
            
        import mujoco
        from mujoco import mjr
        
        # 查找相机 ID
        camera_id = self._get_camera_id()
        
        # 配置渲染上下文
        scene = mujoco.MjvScene(self._model, maxgeom=100)
        mujoco.mjv_updateScene(
            self._model, self._data, None, None, None,
            mujoco.MjvOption(), 0, mujoco.MjvCatOpt.mjCAT_ALL, scene
        )
        
        # offscreen 渲染
        rgb = np.zeros((self._height, self._width, 3), dtype=np.uint8)
        depth = np.zeros((self._height, self._width, 1), dtype=np.float32)
        
        ctx = mujoco.MjrContext(self._model, mujoco.MjtFontScale.mjFONTSCALE_150)
        
        viewport = mujoco.MjrRect(0, 0, self._width, self._height)
        mujoco.mjr_render(viewport, scene, ctx)
        mujoco.mjr_readPixels(rgb, depth, viewport, ctx)
        
        return {"rgb": rgb, "depth": depth}
        
    def _get_camera_id(self) -> int:
        """获取相机 ID"""
        if not self.available():
            return 0
        import mujoco
        camera_id = mujoco.mj_name2id(
            self._model, mujoco.mjtObj.mjOBJ_CAMERA, self._camera_name
        )
        return max(0, camera_id)
        
    def _zero_frames(self) -> dict[str, np.ndarray]:
        """返回零帧占位"""
        return {
            "rgb": np.zeros((self._height, self._width, 3), dtype=np.uint8),
            "depth": np.zeros((self._height, self._width, 1), dtype=np.float32),
        }
        
    @staticmethod
    def available() -> bool:
        """检查 MuJoCo 渲染是否可用"""
        try:
            import mujoco
            return hasattr(mujoco, "mjr_readPixels")
        except ImportError:
            return False


__all__ = ["SimRenderer"]
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd D:/projects/robot-logic/simulation && python -m pytest backend/tests/test_renderer.py -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
cd D:/projects/robot-logic
git add simulation/backend/rcs_env/renderer.py simulation/backend/tests/test_renderer.py
git commit -m "feat(simulation): add SimRenderer for offscreen camera rendering"
```

---

## 2. CameraSetWrapper 增强

### 2.1 增强 CameraSetWrapper

**Files:**
- Modify: `simulation/backend/rcs_env/envs/wrappers.py`（添加 `renderer` 参数）
- Test: `simulation/backend/tests/test_rcs_env.py`（添加相机测试）

**Interfaces:**
- Consumes: `SimRenderer` from task 1.1
- Produces: `CameraSetWrapper` with `renderer` optional parameter

- [ ] **Step 1: 编写失败测试**

```python
# simulation/backend/tests/test_rcs_env.py 新增测试函数

def test_camera_wrapper_with_renderer():
    """CameraSetWrapper + SimRenderer 集成测试"""
    from rcs_env.renderer import SimRenderer
    from rcs_env.envs.wrappers import CameraSetWrapper
    
    if not SimRenderer.available():
        pytest.skip("MuJoCo not available")
    
    import mujoco
    model = mujoco.MjModel.from_xml_string("""
    <mujoco model="test">
        <worldbody>
            <body name="test_body" pos="0 0 0.5">
                <geom type="box" size="0.1 0.1 0.1"/>
            </body>
        </worldbody>
    </mujoco>
    """)
    data = mujoco.MjData(model)
    renderer = SimRenderer(model, data, width=160, height=120)
    
    # 创建 mock env
    class MockEnv:
        def reset(self):
            return np.zeros(14), {}
        def step(self, action):
            return np.zeros(14), 0.0, False, False, {}
        observation_space = gym.spaces.Box(low=-1, high=1, shape=(14,))
    
    import gymnasium as gym
    env = MockEnv()
    wrapped = CameraSetWrapper(env, renderer=renderer, width=160, height=120)
    
    obs, _ = wrapped.reset()
    
    assert "rgb" in obs
    assert obs["rgb"].shape == (120, 160, 3)
    assert obs["rgb"].dtype == np.uint8


def test_camera_wrapper_without_renderer():
    """CameraSetWrapper 无 renderer 时返回零帧"""
    from rcs_env.envs.wrappers import CameraSetWrapper
    
    import gymnasium as gym
    
    class MockEnv:
        def reset(self):
            return np.zeros(14), {}
        def step(self, action):
            return np.zeros(14), 0.0, False, False, {}
        observation_space = gym.spaces.Box(low=-1, high=1, shape=(14,))
    
    env = MockEnv()
    wrapped = CameraSetWrapper(env, renderer=None, width=160, height=120)
    
    obs, _ = wrapped.reset()
    
    assert "rgb" in obs
    assert obs["rgb"].shape == (120, 160, 3)
    assert np.all(obs["rgb"] == 0)  # 零帧
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd D:/projects/robot-logic/simulation && python -m pytest backend/tests/test_rcs_env.py::test_camera_wrapper_with_renderer -v`
Expected: FAIL - TypeError: __init__() got an unexpected keyword argument 'renderer'

- [ ] **Step 3: 修改 CameraSetWrapper**

```python
# simulation/backend/rcs_env/envs/wrappers.py

class CameraSetWrapper(gym.Wrapper):
    """Injects RGB/depth camera frames into the observation dict.

    Mirrors RCS ``CameraSetWrapper`` data-injection for vision policies
    (used by vla-training / robot-app inference).
    
    Args:
        env: Base Gymnasium environment
        renderer: SimRenderer instance for rendering. If None, returns zero frames.
        height: Image height in pixels
        width: Image width in pixels
        color_dim: Number of color channels (3 for RGB)
        include_depth: Whether to include depth channel
    """

    RGB_KEY = "rgb"
    DEPTH_KEY = "depth"

    def __init__(
        self, 
        env: gym.Env, 
        renderer: "SimRenderer | None" = None,
        height: int = 240, 
        width: int = 320,
        color_dim: int = 3,
        include_depth: bool = True,
    ) -> None:
        super().__init__(env)
        self._renderer = renderer
        self.height = height
        self.width = width
        self.color_dim = color_dim
        self.include_depth = include_depth
        
        # 构建观测空间
        self.observation_space = gym.spaces.Dict({
            "state": env.observation_space,
            self.RGB_KEY: gym.spaces.Box(
                low=0, high=255, 
                shape=(height, width, color_dim), 
                dtype=np.uint8
            ),
        })
        if include_depth:
            self.observation_space.spaces[self.DEPTH_KEY] = gym.spaces.Box(
                low=0.0, high=10.0,
                shape=(height, width, 1),
                dtype=np.float32
            )

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        frames = self._render_frames()
        return {"state": obs, **frames}, info

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        frames = self._render_frames()
        return {"state": obs, **frames}, reward, terminated, truncated, info

    def _render_frames(self) -> dict:
        if self._renderer is None:
            return {
                self.RGB_KEY: np.zeros(
                    (self.height, self.width, self.color_dim), dtype=np.uint8
                ),
                self.DEPTH_KEY: np.zeros(
                    (self.height, self.width, 1), dtype=np.float32
                ) if self.include_depth else np.array([[[0.0]]]),
            }
        result = self._renderer.render()
        return {
            self.RGB_KEY: result.get("rgb", np.zeros((self.height, self.width, self.color_dim), dtype=np.uint8)),
            self.DEPTH_KEY: result.get("depth", np.zeros((self.height, self.width, 1), dtype=np.float32)),
        }
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd D:/projects/robot-logic/simulation && python -m pytest backend/tests/test_rcs_env.py::test_camera_wrapper_with_renderer backend/tests/test_rcs_env.py::test_camera_wrapper_without_renderer -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
cd D:/projects/robot-logic
git add simulation/backend/rcs_env/envs/wrappers.py simulation/backend/tests/test_rcs_env.py
git commit -m "feat(simulation): enhance CameraSetWrapper with renderer support"
```

---

## 3. VLAInferenceEngine 推理引擎

### 3.1 VLAInferenceEngine 基础实现

**Files:**
- Create: `robot-app/rcs_layer/vla/inference_engine.py`
- Test: `robot-app/tests/test_vla_inference.py`

**Interfaces:**
- Produces: `class VLAInferenceEngine` with `predict(obs) -> np.ndarray` and `reset()`
- Produces: `load_policy(path, kind, **kwargs) -> Policy` factory function

- [ ] **Step 1: 编写失败测试**

```python
# robot-app/tests/test_vla_inference.py
import numpy as np
import pytest

def test_inference_engine_scripted():
    """VLAInferenceEngine with ScriptedPolicy"""
    from rcs_layer.vla.inference_engine import VLAInferenceEngine
    
    engine = VLAInferenceEngine(action_dim=6)
    obs = {"state": np.zeros(14)}
    action = engine.predict(obs)
    
    assert action.shape == (6,)
    assert isinstance(action, np.ndarray)


def test_inference_engine_reset():
    """VLAInferenceEngine reset()"""
    from rcs_layer.vla.inference_engine import VLAInferenceEngine
    
    engine = VLAInferenceEngine(action_dim=6)
    engine.reset()  # 不应抛出异常


def test_load_policy_scripted():
    """load_policy returns ScriptedPolicy when kind='scripted'"""
    from rcs_layer.vla.inference_engine import load_policy
    
    policy = load_policy(kind="scripted", action_dim=6)
    assert policy is not None
    obs = {"state": np.zeros(14)}
    action = policy(obs)
    assert action.shape == (6,)
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd D:/projects/robot-logic/robot-app && python -m pytest tests/test_vla_inference.py -v`
Expected: FAIL - No module named 'rcs_layer'

- [ ] **Step 3: 编写最小实现**

```python
# robot-app/rcs_layer/vla/inference_engine.py
"""VLA 推理引擎

支持两种策略：
- ScriptedPolicy：快速验证
- VLAPolicy：真实模型推理
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .policy import Policy, ScriptedPolicy


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
    """策略加载工厂
    
    Args:
        path: 模型权重路径
        kind: 策略类型，"scripted" | "vla"
        **kwargs: 传递给策略的额外参数
        
    Returns:
        Policy 实例
    """
    if path is None or kind == "scripted":
        return ScriptedPolicy(
            action_dim=kwargs.get("action_dim", 6),
            gain=kwargs.get("gain", 0.5),
        )
    if kind == "vla":
        from .vla_policy import VLAPolicy
        return VLAPolicy(
            path=path,
            robot_type=kwargs.get("robot_type", "ARM"),
            device=kwargs.get("device", "cuda"),
            action_dim=kwargs.get("action_dim", 6),
        )
    raise ValueError(f"unknown policy kind: {kind}")


__all__ = ["VLAInferenceEngine", "load_policy"]
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd D:/projects/robot-logic/robot-app && python -m pytest tests/test_vla_inference.py -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
cd D:/projects/robot-logic
git add robot-app/rcs_layer/vla/inference_engine.py robot-app/tests/test_vla_inference.py
git commit -m "feat(robot-app): add VLAInferenceEngine for policy inference"
```

---

## 4. TeleopCollector 遥操作采集

### 4.1 操作器协议定义

**Files:**
- Create: `robot-app/rcs_layer/teleop/operator.py`
- Test: `robot-app/tests/test_teleop.py`

**Interfaces:**
- Produces: `class Operator` Protocol with `get_action(obs) -> np.ndarray`

- [ ] **Step 1: 编写失败测试**

```python
# robot-app/tests/test_teleop.py
import numpy as np

def test_operator_protocol():
    """Operator 协议定义"""
    from rcs_layer.teleop.operator import Operator
    
    class MockOperator:
        def get_action(self, obs):
            return np.zeros(6)
    
    op: Operator = MockOperator()  # 类型检查
    assert op.get_action({}).shape == (6,)


def test_episode_data():
    """EpisodeData 数据类"""
    from rcs_layer.teleop.collector import EpisodeData
    
    data = EpisodeData(
        observations=[{"state": np.zeros(14)}],
        actions=[np.zeros(6)],
        rewards=[0.0],
        task_success=True,
    )
    assert len(data.observations) == 1
    assert len(data.actions) == 1
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd D:/projects/robot-logic/robot-app && python -m pytest tests/test_teleop.py -v`
Expected: FAIL - No module named 'rcs_layer.teleop'

- [ ] **Step 3: 编写最小实现**

```python
# robot-app/rcs_layer/teleop/operator.py
"""操作器协议定义

定义遥操作输入的抽象接口。
"""
from __future__ import annotations

from typing import Protocol

import numpy as np


class Operator(Protocol):
    """遥操作器协议
    
    所有操作器（键盘、SpaceMouse、轨迹回放等）
    都应实现此协议。
    """
    
    def get_action(self, obs: dict) -> np.ndarray:
        """从当前观测获取动作
        
        Args:
            obs: 当前环境观测
            
        Returns:
            np.ndarray: 动作向量
        """
        ...


__all__ = ["Operator"]
```

```python
# robot-app/rcs_layer/teleop/collector.py
"""遥操作数据采集器"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class EpisodeData:
    """采集的 episode 数据"""
    observations: list[dict] = field(default_factory=list)
    actions: list[np.ndarray] = field(default_factory=list)
    rewards: list[float] = field(default_factory=list)
    task_success: bool = False
    task_name: str = ""
    
    def save(self, path: Path) -> None:
        """保存 episode 数据"""
        np.savez(
            path,
            observations=self.observations,
            actions=np.array(self.actions),
            rewards=np.array(self.rewards),
            task_success=self.task_success,
            task_name=self.task_name,
        )
    
    @classmethod
    def load(cls, path: Path) -> "EpisodeData":
        """加载 episode 数据"""
        data = np.load(path, allow_pickle=True)
        return cls(
            observations=list(data["observations"]),
            actions=list(data["actions"]),
            rewards=list(data["rewards"]),
            task_success=bool(data["task_success"]),
            task_name=str(data["task_name"]),
        )


class TeleopCollector:
    """遥操作数据采集器"""
    
    def __init__(
        self, 
        operator: "Operator",
        env: Any,
        task: Any,
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
        
        step_count = 0
        max_steps = 1000  # 防止无限循环
        
        while not self.task.done({}) and step_count < max_steps:
            # 操作器输入
            op_action = self.operator.get_action(obs)
            
            # 环境 step
            obs, reward, terminated, truncated, info = self.env.step(op_action)
            
            observations.append(obs)
            actions.append(op_action)
            rewards.append(reward)
            
            if terminated or truncated:
                break
                
            step_count += 1
            
        return EpisodeData(
            observations=observations,
            actions=actions,
            rewards=rewards,
            task_success=self.task.done({}),
            task_name=getattr(self.task, "name", "unknown"),
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
            episode.save(save_dir / f"episode_{i:04d}.npz")
            
        return episodes


__all__ = ["Operator", "EpisodeData", "TeleopCollector"]
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd D:/projects/robot-logic/robot-app && python -m pytest tests/test_teleop.py -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
cd D:/projects/robot-logic
git add robot-app/rcs_layer/teleop/operator.py robot-app/rcs_layer/teleop/collector.py robot-app/tests/test_teleop.py
git commit -m "feat(robot-app): add TeleopCollector for data collection"
```

### 4.2 KeyboardOperator 实现

**Files:**
- Create: `robot-app/rcs_layer/teleop/keyboard.py`
- Test: `robot-app/tests/test_teleop.py`（扩展）

**Interfaces:**
- Consumes: `Operator` Protocol from 4.1
- Produces: `class KeyboardOperator` implementing `Operator`

- [ ] **Step 1: 编写失败测试**

```python
# robot-app/tests/test_teleop.py 新增

def test_keyboard_operator():
    """KeyboardOperator 基本测试"""
    from rcs_layer.teleop.keyboard import KeyboardOperator
    
    op = KeyboardOperator(action_dim=6)
    action = op.get_action({})
    
    assert action.shape == (6,)
    assert isinstance(action, np.ndarray)
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd D:/projects/robot-logic/robot-app && python -m pytest tests/test_teleop.py::test_keyboard_operator -v`
Expected: FAIL - No module named 'rcs_layer.teleop.keyboard'

- [ ] **Step 3: 编写实现**

```python
# robot-app/rcs_layer/teleop/keyboard.py
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
from __future__ import annotations

import numpy as np

from .operator import Operator


class KeyboardOperator:
    """键盘遥操作适配器
    
    简单键盘输入映射到笛卡尔空间动作。
    实际使用需要结合 curses 或 readchar 获取按键。
    """
    
    def __init__(self, action_dim: int = 6, step_size: float = 0.05):
        self.action_dim = action_dim
        self.step_size = step_size
        self._current_action = np.zeros(action_dim)
        self._gripper = 0.5  # 中间位置
        self._running = False
        
    def get_action(self, obs: dict) -> np.ndarray:
        """获取当前动作"""
        action = self._current_action.copy()
        # 添加夹爪维度
        if self.action_dim > 6:
            action = np.append(action, self._gripper)
        return action
        
    def set_action_from_keys(self, keys_pressed: set[str]) -> None:
        """根据按键状态更新动作
        
        Args:
            keys_pressed: 当前按下的按键集合
        """
        self._current_action = np.zeros(6)
        
        if "w" in keys_pressed:
            self._current_action[0] += self.step_size
        if "s" in keys_pressed:
            self._current_action[0] -= self.step_size
        if "a" in keys_pressed:
            self._current_action[1] += self.step_size
        if "d" in keys_pressed:
            self._current_action[1] -= self.step_size
        if "q" in keys_pressed:
            self._current_action[2] += self.step_size
        if "e" in keys_pressed:
            self._current_action[2] -= self.step_size
            
        # 夹爪
        if "g" in keys_pressed:
            self._gripper = 0.0  # 闭合
        elif "h" in keys_pressed:
            self._gripper = 1.0  # 张开
            
    def start(self) -> None:
        """开始采集"""
        self._running = True
        
    def stop(self) -> None:
        """停止采集"""
        self._running = False


__all__ = ["KeyboardOperator"]
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd D:/projects/robot-logic/robot-app && python -m pytest tests/test_teleop.py::test_keyboard_operator -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
cd D:/projects/robot-logic
git add robot-app/rcs_layer/teleop/keyboard.py
git commit -m "feat(robot-app): add KeyboardOperator for teleop input"
```

---

## 5. 集成测试

### 5.1 端到端闭环测试

**Files:**
- Create: `simulation/backend/tests/test_integration_loop.py`

**Interfaces:**
- Consumes: 所有前述任务成果

- [ ] **Step 1: 编写失败测试**

```python
# simulation/backend/tests/test_integration_loop.py
import numpy as np
import pytest


def test_end_to_end_loop():
    """端到端闭环测试：环境 → 推理 → 评估"""
    from rcs_env import SimEnv, Planner
    from rcs_env.envs.wrappers import CameraSetWrapper, TaskWrapper
    from rcs_env.envs.configs import LOGISTICS_ARM
    from robot_app.rcs_layer.vla.inference_engine import VLAInferenceEngine
    from robot_app.rcs_layer.tasks import PalletTask
    
    # 1. 创建环境
    env = SimEnv(
        robot_type=LOGISTICS_ARM.robot_type,
        logic_device_id=LOGISTICS_ARM.logic_device_id,
    )
    env = TaskWrapper(env, PalletTask())
    
    # 2. 创建 VLA 推理引擎
    engine = VLAInferenceEngine(action_dim=env.engine.dof)
    
    # 3. 运行 episode
    obs, _ = env.reset()
    engine.reset()
    
    for step in range(100):
        action = engine.predict(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        
        if terminated or truncated:
            break
    
    # 4. 验证
    assert "state" in obs
    assert isinstance(reward, float)
```

- [ ] **Step 2: 运行测试验证**

Run: `cd D:/projects/robot-logic && python -m pytest simulation/backend/tests/test_integration_loop.py -v`
Expected: 根据环境配置可能 FAIL 或 PASS

- [ ] **Step 3: 修复任何导入/集成问题**

根据实际测试结果调整代码

- [ ] **Step 4: 运行测试验证通过**

- [ ] **Step 5: 提交**

```bash
cd D:/projects/robot-logic
git add simulation/backend/tests/test_integration_loop.py
git commit -m "test: add end-to-end integration test for simulation loop"
```

---

## 实施顺序

1. **SimRenderer** - 相机渲染基础
2. **CameraSetWrapper** - 观测注入增强
3. **VLAInferenceEngine** - 推理引擎
4. **TeleopCollector** - 数据采集
5. **KeyboardOperator** - 键盘操作器
6. **集成测试** - 端到端验证

## 验收标准

- [ ] 所有单元测试通过
- [ ] CameraSetWrapper 支持 renderer 参数
- [ ] VLAInferenceEngine 支持 ScriptedPolicy
- [ ] TeleopCollector 可采集 episode 数据
- [ ] 端到端集成测试通过
