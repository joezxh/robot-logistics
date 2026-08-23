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
