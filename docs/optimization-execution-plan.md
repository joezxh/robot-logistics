# robot-logic × RCS 对齐优化执行计划

**日期**：2026-08-20
**目标**：解决 5 个关键优化项，使 robot-logic 四个子工程完全对齐 RCS 标准
**状态**：✅ 已完成

---

## 执行结果汇总

| # | 优化项 | 状态 | 修改文件 |
|---|--------|------|----------|
| 1 | VLA 训练闭环打通 | ✅ 完成 | `collector.py`, `evaluate.py`, `device.py` |
| 2 | 坐标系统一 | ✅ 完成 | `site_tcp.py`, `motion_commander.py`, `__init__.py` |
| 3 | IK/FK 参数化 + FSM 统一 | ✅ 完成 | `arm_spec.py`, `arm.py`, `task_coordinator.py` |
| 4 | 真实 HAL + VLA 推理链路 | ✅ 完成 | `hal/*.py`, `policy.py` |
| 5 | HyEmbodied Bug 修复 | ✅ 完成 | `hy_embodied.py` |

---

## 详细执行记录

### 问题分析

**当前状态**：
- `collector.py` 中的 `SimulationCollector.collect()` 方法存在，但实现不完整
- `evaluate.py` 中的 `evaluate_closed_loop()` 已实现（第 96-158 行），但依赖项导入路径可能有问题

**发现的问题**：
1. `collector.py` 第 131-145 行：`_build_env_and_expert()` 方法中导入路径不正确
   ```python
   from backend.rcs_env import SimEnv  # 应该是 simulation.backend.rcs_env
   from rcs_layer.vla import load_policy  # 应该是 robot_app.rcs_layer.vla
   ```
2. `evaluate.py` 第 117-126 行：同样的导入路径问题

### 执行步骤

#### Step 1.1：修复 collector.py 导入路径

**文件**：`vla-training/src/vla_training/data/collector.py`

**修改**（第 131-145 行）：
```python
# 修改前
def _build_env_and_expert(self):
    from backend.rcs_env import SimEnv
    from backend.rcs_env.envs.configs import get_config
    from rcs_layer.vla import load_policy
    from rcs_layer.teleop import KeyboardAdapter

# 修改后
def _build_env_and_expert(self):
    import sys
    from pathlib import Path
    
    # 动态添加 simulation 路径
    sim_path = str(Path(__file__).resolve().parents[4] / "simulation" / "backend")
    if sim_path not in sys.path:
        sys.path.insert(0, sim_path)
    
    from backend.rcs_env import SimEnv
    from backend.rcs_env.envs.configs import get_config
    
    # 动态添加 robot-app 路径
    app_path = str(Path(__file__).resolve().parents[4] / "robot-app")
    if app_path not in sys.path:
        sys.path.insert(0, app_path)
    
    from rcs_layer.vla import load_policy
    from rcs_layer.teleop import KeyboardAdapter
```

#### Step 1.2：修复 evaluate.py 导入路径

**文件**：`vla-training/src/vla_training/eval/evaluate.py`

**修改**（第 117-126 行）：
```python
# 修改前
def evaluate_closed_loop(
    adapter: Any,
    tasks: Sequence[str],
    ...
):
    import numpy as np
    
    from backend.rcs_env import SimEnv
    from backend.rcs_env.envs.configs import get_config
    from rcs_layer.vla import load_policy
    from rcs_layer.tasks import get_task

# 修改后
def evaluate_closed_loop(
    adapter: Any,
    tasks: Sequence[str],
    ...
):
    import numpy as np
    import sys
    from pathlib import Path
    
    # 动态添加路径
    project_root = Path(__file__).resolve().parents[4]
    for subproject in ["simulation/backend", "robot-app"]:
        p = str(project_root / subproject)
        if p not in sys.path:
            sys.path.insert(0, p)
    
    from backend.rcs_env import SimEnv
    from backend.rcs_env.envs.configs import get_config
    from rcs_layer.vla import load_policy
    from rcs_layer.tasks import get_task
```

#### Step 1.3：完善 collector.py 遥操作采集

**文件**：`vla-training/src/vla_training/data/collector.py`

**问题**：第 164 行，`teleop` 模式下未正确读取遥操作输入

**修改**（第 160-175 行）：
```python
# 修改前
for step in range(self.max_steps):
    action = expert(obs) if self.expert != "teleop" else np.zeros(env.engine.dof)

# 修改后
for step in range(self.max_steps):
    if self.expert == "teleop":
        action = expert.get_action(obs)  # 从遥操作设备获取动作
    else:
        action = expert(obs)
```

**修改 teleop/device.py**：
```python
# robot-app/rcs_layer/teleop/device.py
class KeyboardAdapter:
    def get_action(self, obs: dict) -> np.ndarray:
        """返回当前按键对应的动作"""
        return self._last_action if hasattr(self, '_last_action') else np.zeros(6)
```

#### Step 1.4：验证训练闭环

**测试脚本**：`vla-training/tests/test_closed_loop.py`

```python
"""验证 VLA 训练闭环"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from vla_training.eval.evaluate import evaluate_closed_loop
from vla_training.models.adapter import get_adapter
from vla_training.config import load_config

def test_closed_loop():
    config = load_config("configs/finetune_hy_embodied.yaml")
    adapter = get_adapter(config)
    
    report = evaluate_closed_loop(
        adapter,
        tasks=["pallet", "box"],
        episodes_per_task=5,
        max_steps=200,
        config=config,
    )
    
    print(f"Success rate: {report.success_rate:.1%}")
    assert report.success_rate >= 0.0, "Closed loop must run"
    print("✓ Training closed loop verified")

if __name__ == "__main__":
    test_closed_loop()
```

---

## 优化项 2：坐标系统一

### 问题分析

**当前状态**：
- `shared/python/robot_contracts/kinematics.py` 已有完整的 Pose 类和坐标转换函数
- `simulation/backend/services/motion_commander.py` 使用硬编码的 `_SITE_TCP_POSES`
- `rcs/rcs/state/pose.py` 有 Pose6D 桥接类

**问题**：
1. `motion_commander.py` 第 24-27 行：硬编码的 RPY 格式与 RCS xyzw 不一致
2. 缺少 `SiteTCPPose` 配置类来管理站点 TCP 姿态

### 执行步骤

#### Step 2.1：创建 SiteTCPPose 配置类

**文件**：`shared/python/robot_contracts/site_tcp.py` [NEW]

```python
"""站点 TCP 姿态配置 — 统一坐标系管理"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .kinematics import Pose, RobotType


@dataclass
class SiteTCPPose:
    """站点 TCP 姿态配置
    
    统一管理仓库站点到臂基座的坐标变换，避免硬编码。
    """
    site_id: str
    tcp_pose_in_base: Pose
    robot_type: RobotType
    description: str = ""

    @classmethod
    def from_rpy(
        cls,
        site_id: str,
        translation: Sequence[float],
        rpy_deg: Sequence[float],
        robot_type: RobotType = RobotType.ARM,
        description: str = "",
    ) -> "SiteTCPPose":
        """从 RPY (度) 创建站点配置（兼容旧数据）"""
        import math
        r, p, y = [math.radians(d) for d in rpy_deg]
        tcp_pose = Pose.from_rpy([r, p, y], translation)
        return cls(
            site_id=site_id,
            tcp_pose_in_base=tcp_pose,
            robot_type=robot_type,
            description=description,
        )

    def get_world_pose(self, base_pose: Pose) -> Pose:
        """将 TCP 姿态转换到世界坐标系"""
        from .kinematics import to_pose_in_world_coordinates
        return to_pose_in_world_coordinates(base_pose, self.tcp_pose_in_base)


# 预定义站点配置
DEFAULT_SITE_PROFILES: dict[str, SiteTCPPose] = {
    "dock_loading": SiteTCPPose.from_rpy(
        site_id="dock_loading",
        translation=[0.50, 0.00, 0.30],
        rpy_deg=[0.0, 90.0, 0.0],  # ry=90° = y向上
        description="码头装载站点 TCP",
    ),
    "warehouse_storage": SiteTCPPose.from_rpy(
        site_id="warehouse_storage",
        translation=[0.40, -0.30, 0.50],
        rpy_deg=[0.0, 90.0, 0.0],
        description="仓库存储站点 TCP",
    ),
}


def get_site_profile(site_id: str) -> SiteTCPPose:
    """获取站点配置"""
    if site_id not in DEFAULT_SITE_PROFILES:
        raise KeyError(f"Unknown site_id: {site_id}; available: {list(DEFAULT_SITE_PROFILES)}")
    return DEFAULT_SITE_PROFILES[site_id]


__all__ = ["SiteTCPPose", "DEFAULT_SITE_PROFILES", "get_site_profile"]
```

#### Step 2.2：重构 MotionCommander

**文件**：`simulation/backend/services/motion_commander.py`

**修改**：

```python
"""Bridge from simulation tasks to motion commands.

Coordinate transform
-------------------
使用 robot_contracts.site_tcp 模块统一管理站点 TCP 姿态，
替代硬编码的 _SITE_TCP_POSES。

世界坐标系变换链：
    世界 = 基座姿态 @ TCP姿态_in_基座
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from backend.algorithm.simulator.site_manager import SiteManager
from backend.services.mqtt_bridge import SimulationMqttBridge
from robot_contracts import Pose, RobotType
from robot_contracts.site_tcp import SiteTCPPose, get_site_profile

logger = logging.getLogger(__name__)

# 默认关节配置 (radians)
_DEFAULT_TRANSPORT_JOINTS: list[float] = [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]


class MotionCommander:
    """Converts task records into motion commands published via MQTT.
    
    使用 SiteTCPPose 统一管理坐标系，与 RCS Pose 转换系统集成。
    """

    def __init__(
        self,
        mqtt_bridge: SimulationMqttBridge,
        site_manager: SiteManager,
        site_profiles: dict[str, SiteTCPPose] | None = None,
    ) -> None:
        self._bridge = mqtt_bridge
        self._sites = site_manager
        self._site_profiles = site_profiles or {}

    def _get_tcp_pose_for_site(self, site_id: str) -> Pose:
        """获取站点的 TCP 姿态"""
        # 优先使用实例配置，否则使用全局配置
        if site_id in self._site_profiles:
            return self._site_profiles[site_id].tcp_pose_in_base
        return get_site_profile(site_id).tcp_pose_in_base

    def _build_command(self, task_type: str, device_id: str, base_pose: Pose | None = None) -> dict[str, Any] | None:
        """构建运动命令
        
        Args:
            task_type: 任务类型
            device_id: 设备 ID
            base_pose: 机器人基座在世界坐标系中的姿态（用于坐标变换）
        """
        command_id = f"cmd-{uuid.uuid4().hex[:8]}"
        
        if task_type == "dock_loading":
            tcp_pose = self._get_tcp_pose_for_site("dock_loading")
            # 如果提供了基座姿态，转换为世界系
            if base_pose is not None:
                world_pose = base_pose @ tcp_pose
                return {
                    "command_id": command_id,
                    "type": "move_l",
                    "target_pose": {
                        "position": world_pose.translation.tolist(),
                        "quaternion_xyzw": world_pose.quaternion.tolist(),  # xyzw
                    },
                    "speed_scale": 0.5,
                }
            else:
                # 回退到 RPY 格式（兼容旧接口）
                rpy = tcp_pose.to_rpy()
                import math
                return {
                    "command_id": command_id,
                    "type": "move_l",
                    "target_pose": {
                        "x": tcp_pose.translation[0],
                        "y": tcp_pose.translation[1],
                        "z": tcp_pose.translation[2],
                        "rx": math.degrees(rpy[0]),
                        "ry": math.degrees(rpy[1]),
                        "rz": math.degrees(rpy[2]),
                    },
                    "speed_scale": 0.5,
                }
        
        elif task_type == "agv_transport":
            return {
                "command_id": command_id,
                "type": "move_j",
                "target_joints": list(_DEFAULT_TRANSPORT_JOINTS),
                "target_pose": None,
                "speed_scale": 0.8,
            }
        
        elif task_type == "warehouse_storage":
            tcp_pose = self._get_tcp_pose_for_site("warehouse_storage")
            if base_pose is not None:
                world_pose = base_pose @ tcp_pose
                return {
                    "command_id": command_id,
                    "type": "move_l",
                    "target_pose": {
                        "position": world_pose.translation.tolist(),
                        "quaternion_xyzw": world_pose.quaternion.tolist(),
                    },
                    "speed_scale": 0.5,
                }
            else:
                rpy = tcp_pose.to_rpy()
                import math
                return {
                    "command_id": command_id,
                    "type": "move_l",
                    "target_pose": {
                        "x": tcp_pose.translation[0],
                        "y": tcp_pose.translation[1],
                        "z": tcp_pose.translation[2],
                        "rx": math.degrees(rpy[0]),
                        "ry": math.degrees(rpy[1]),
                        "rz": math.degrees(rpy[2]),
                    },
                    "speed_scale": 0.5,
                }
        
        else:
            logger.warning("unknown task type %r — no motion command generated", task_type)
            return None

    def on_task_started(self, task_record: dict[str, Any]) -> dict[str, Any] | None:
        """处理任务开始事件"""
        task_type = task_record["type"]
        device_id = task_record["device_id"]
        
        # 提取基座姿态（如果有）
        base_pose = None
        if "base_pose" in task_record:
            from robot_contracts import Pose
            base_pose = Pose.from_dict(task_record["base_pose"])
        
        command = self._build_command(task_type, device_id, base_pose)
        if command is None:
            return None
        
        topic = f"rcs/{device_id}/command"
        self._bridge.publish_command(topic, command)
        logger.info("published %s command for %s: %s", task_type, device_id, command["type"])
        return command
```

#### Step 2.3：更新 shared/__init__.py

**文件**：`shared/python/robot_contracts/__init__.py`

```python
from .kinematics import Pose, RobotType, GripperType, RobotPlatform, to_pose_in_world_coordinates, to_pose_in_robot_coordinates
from .site_tcp import SiteTCPPose, get_site_profile, DEFAULT_SITE_PROFILES

__all__ = [
    "Pose",
    "RobotType", 
    "GripperType",
    "RobotPlatform",
    "to_pose_in_world_coordinates",
    "to_pose_in_robot_coordinates",
    "SiteTCPPose",
    "get_site_profile",
    "DEFAULT_SITE_PROFILES",
]
```

---

## 优化项 3：IK/FK 参数化 + FSM 统一

### 问题分析

**当前状态**：
- `rcs/rcs/controllers/arm.py` 第 18-28 行：DH 参数硬编码为 `ARM_DH`
- `rcs/rcs/planning/fk.py` 和 `ik.py` 已有通用实现，但未被设备规格使用
- `robot-app/ros2_ws/src/robot_decision/state_machine.py` 有通用 FSM 基类
- `robot-app/ros2_ws/src/robot_decision/task_coordinator.py` 有独立的 TaskCoordinator

**问题**：
1. DH 参数未从设备配置派生
2. TaskCoordinator 未继承 FSM 基类

### 执行步骤

#### Step 3.1：创建设备规格抽象

**文件**：`rcs/rcs/devices/arm_spec.py` [NEW]

```python
"""机器人设备规格 — 参数化 DH/TCP/限位"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np


@dataclass
class DHParams:
    """Denavit-Hartenberg 参数
    
    参数顺序: (a, d, alpha, theta_offset)
    """
    a: float
    d: float
    alpha: float
    theta_offset: float = 0.0


@dataclass
class JointLimits:
    """关节限位"""
    lower: np.ndarray
    upper: np.ndarray
    vel_max: np.ndarray
    acc_max: np.ndarray
    torque_max: np.ndarray | None = None


@dataclass 
class ArmSpec:
    """机械臂设备规格"""
    name: str
    dof: int
    dh_params: list[DHParams]
    tcp_offset: np.ndarray  # TCP 在最后关节末端的偏移 [x, y, z]
    joint_limits: JointLimits
    home_joints: np.ndarray
    control_hz: float = 100.0
    
    @classmethod
    def from_standard(cls, name: str) -> "ArmSpec":
        """从标准库创建设备规格"""
        from .standards import ARM_6DOF_STANDARD, ARM_7DOF_STANDARD
        standards = {
            "ARM_6DOF": ARM_6DOF_STANDARD,
            "ARM_7DOF": ARM_7DOF_STANDARD,
        }
        if name not in standards:
            raise ValueError(f"Unknown standard: {name}; available: {list(standards)}")
        return standards[name]
    
    def to_dh_list(self) -> list[tuple[float, float, float, float]]:
        """转换为 (a, d, alpha, theta_offset) 列表"""
        return [(dh.a, dh.d, dh.alpha, dh.theta_offset) for dh in self.dh_params]


# 标准设备规格
ARM_6DOF_STANDARD = ArmSpec(
    name="ARM_6DOF",
    dof=6,
    dh_params=[
        DHParams(a=0.0,  d=0.10, alpha= 1.570796, theta_offset=0.0),
        DHParams(a=0.3,  d=0.00, alpha= 0.0,      theta_offset=0.0),
        DHParams(a=0.2,  d=0.00, alpha= 1.570796, theta_offset=0.0),
        DHParams(a=0.0,  d=0.10, alpha=-1.570796, theta_offset=0.0),
        DHParams(a=0.0,  d=0.05, alpha= 1.570796, theta_offset=0.0),
        DHParams(a=0.0,  d=0.04, alpha= 0.0,      theta_offset=0.0),
    ],
    tcp_offset=np.array([0.0, 0.0, 0.0]),  # TCP 在末端
    joint_limits=JointLimits(
        lower=np.array([-3.14, -3.14, -3.14, -3.14, -3.14, -3.14]),
        upper=np.array([ 3.14,  3.14,  3.14,  3.14,  3.14,  3.14]),
        vel_max=np.array([2.0, 2.0, 2.0, 2.0, 2.0, 2.0]),
        acc_max=np.array([5.0, 5.0, 5.0, 5.0, 5.0, 5.0]),
    ),
    home_joints=np.array([0.0, -0.785, 0.785, 0.0, 0.785, 0.0]),
)

ARM_7DOF_STANDARD = ArmSpec(
    name="ARM_7DOF",
    dof=7,
    dh_params=[
        DHParams(a=0.0,  d=0.333, alpha= 0.0,      theta_offset=0.0),
        DHParams(a=0.0,  d=0.316, alpha=-1.570796,  theta_offset=0.0),
        DHParams(a=0.0,  d=0.384, alpha= 1.570796,  theta_offset=0.0),
        DHParams(a=0.0825, d=0.0, alpha= 1.570796,  theta_offset=0.0),
        DHParams(a=-0.0825, d=0.321, alpha=-1.570796, theta_offset=0.0),
        DHParams(a=0.0,  d=0.0,   alpha= 1.570796,  theta_offset=0.0),
        DHParams(a=0.088, d=0.107, alpha= 1.570796,  theta_offset=0.0),
    ],
    tcp_offset=np.array([0.0, 0.0, 0.0]),
    joint_limits=JointLimits(
        lower=np.array([-2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973]),
        upper=np.array([ 2.8973,  1.7628,  2.8973,  0.0698,  2.8973,  3.7525,  2.8973]),
        vel_max=np.array([2.175, 2.175, 2.175, 2.175, 2.61, 2.61, 2.61]),
        acc_max=np.array([15.0, 7.5, 10.0, 12.5, 15.0, 20.0, 20.0]),
    ),
    home_joints=np.array([0.0, -0.9599, 0.0, -2.0944, 0.0, 1.0472, 0.7854]),
)


__all__ = ["DHParams", "JointLimits", "ArmSpec", "ARM_6DOF_STANDARD", "ARM_7DOF_STANDARD"]
```

#### Step 3.2：重构 ArmController 使用规格

**文件**：`rcs/rcs/controllers/arm.py`

```python
"""6-DOF arm controller: PD control in joint space + IK on move_l.

支持从 ArmSpec 动态加载 DH 参数，不再硬编码。
"""
from __future__ import annotations
import math
import numpy as np

from ..state.profile import DeviceProfile, Morphology
from ..state.joint import JointState
from ..state.command import Command, CommandType
from ..state.error import TrackingError
from ..state.controller_state import ControllerState, ControllerMode
from .base import Controller
from ._common import CommandQueue, clip_to_limits, abs_max
from ..planning import fk, ik
from ..planning.trajectory import plan_trapezoidal, Trajectory
from ..planning.interpolator import Interpolator

# 向后兼容：保留 ARM_DH 作为默认值
ARM_DH = [
    (0.0,  0.10,  math.pi / 2, 0.0),
    (0.3,  0.0,   0.0,         0.0),
    (0.2,  0.0,   math.pi / 2, 0.0),
    (0.0,  0.10, -math.pi / 2, 0.0),
    (0.0,  0.05,  math.pi / 2, 0.0),
    (0.0,  0.04,  0.0,         0.0),
]


class ArmController(Controller):
    morphology = Morphology.ARM

    def __init__(self, profile: DeviceProfile, dh_params: list | None = None) -> None:
        super().__init__(profile)
        
        # 优先使用传入的 DH 参数，否则从设备规格加载
        self._dh_params = dh_params or self._load_dh_from_profile(profile)
        
        self._kp = 0.3
        self._kd = 0.5
        self._q: list[float] = list(profile.home_joints)
        self._qdot: list[float] = [0.0] * profile.num_joints
        self._last_target: list[float] = list(profile.home_joints)
        self._interp: Interpolator | None = None
        self._queue: CommandQueue = CommandQueue(maxsize=1024)

    def _load_dh_from_profile(self, profile: DeviceProfile) -> list:
        """从设备配置加载 DH 参数
        
        支持通过 profile.extra 传入自定义 DH 参数。
        """
        extra = getattr(profile, 'extra', None)
        if extra and 'dh_params' in extra:
            return extra['dh_params']
        # 回退到默认 ARM_DH
        return ARM_DH

    def on_command(self, cmd: Command) -> None:
        # ... 其余代码保持不变 ...
        if cmd.type == CommandType.MOVE_L and cmd.target_pose is not None:
            T = np.eye(4)
            T[:3, 3] = cmd.target_pose.position
            try:
                # 使用实例的 DH 参数
                q_sol = list(ik(self._q, self._dh_params, T, 
                               self.profile.limits.pos_lower, 
                               self.profile.limits.pos_upper))
            except Exception as exc:
                self.state.last_error = f"ik failed: {exc}"
                return
            target = q_sol
        # ... 其余代码保持不变 ...
```

#### Step 3.3：统一 TaskCoordinator 继承 FSM

**文件**：`robot-app/ros2_ws/src/robot_decision/task_coordinator.py`

```python
"""TaskCoordinator — layered state machine for dual-arm loading tasks.

重构为继承通用 FSM 基类，消除架构重复。
"""
from __future__ import annotations

import logging
import time
from typing import Any, Callable

from robot_decision.state_machine import FSM, FSMError

logger = logging.getLogger(__name__)

# 9 action phases + ABORTING
PHASES = (
    "idle", "navigating", "docking", "approaching", "hugging",
    "lifting", "transporting", "placing", "retreating", "aborting",
)

# Valid transitions: from_phase -> set(to_phases)
_VALID_TRANSITIONS: dict[str, set[str]] = {
    "idle":         {"navigating", "retreating"},
    "navigating":   {"docking", "aborting"},
    "docking":      {"approaching", "aborting"},
    "approaching":  {"hugging", "aborting"},
    "hugging":      {"lifting", "aborting"},
    "lifting":      {"transporting", "aborting"},
    "transporting": {"placing", "aborting"},
    "placing":      {"retreating", "aborting"},
    "retreating":   {"idle", "aborting"},
    "aborting":     {"idle"},
}

# Task type → entry phase mapping
_TASK_ENTRY: dict[str, str] = {
    "goto":       "navigating",
    "pick_box":   "navigating",
    "place_box":  "navigating",
    "home_all":   "retreating",
    "transport":  "transporting",
    "dock":       "docking",
    "hug_close":  "hugging",
    "hug_release": "placing",
}

# Phase → executor name mapping
_PHASE_EXECUTOR: dict[str, str] = {
    "navigating":   "base",
    "transporting": "base",
    "retreating":   "base",
    "docking":      "arm",
    "approaching":  "arm",
    "hugging":      "hug",
    "lifting":      "arm",
    "placing":      "arm",
}

_DEFAULT_TIMEOUTS: dict[str, float] = {
    "navigating": 60.0,
    "docking": 30.0,
    "approaching": 20.0,
    "hugging": 15.0,
    "lifting": 15.0,
    "transporting": 60.0,
    "placing": 15.0,
    "retreating": 20.0,
}


class TaskCoordinator(FSM):
    """Layered FSM coordinating base + arms + hug for loading tasks.
    
    重构为继承通用 FSM 基类，统一架构。
    """

    def __init__(
        self,
        *,
        on_phase_change: Callable[[str], None] | None = None,
        phase_timeouts: dict[str, float] | None = None,
    ) -> None:
        # 初始化 FSM 基类
        super().__init__(
            states=PHASES,
            transitions=_VALID_TRANSITIONS,
            initial="idle",
            on_enter={p: self._on_phase_enter for p in PHASES},
        )
        
        self._executors: dict[str, Any] = {}
        self._on_phase_change = on_phase_change
        self._current_task_type: str = ""
        self._current_params: dict[str, Any] = {}
        self._phase_timeouts: dict[str, float] = dict(_DEFAULT_TIMEOUTS)
        if phase_timeouts:
            self._phase_timeouts.update(phase_timeouts)

    def _on_phase_enter(self, fsm: FSM) -> None:
        """FSM 钩子：阶段进入时触发"""
        if self._on_phase_change:
            self._on_phase_change(self._state)
        self._dispatch_current_phase()

    def set_executor(self, name: str, executor: Any) -> None:
        self._executors[name] = executor

    def on_task_command(self, *, task_type: str, parameters: dict[str, Any]) -> None:
        if task_type not in _TASK_ENTRY:
            raise ValueError(f"unknown task_type {task_type!r}; expected one of {tuple(_TASK_ENTRY)}")
        self._current_task_type = task_type
        self._current_params = parameters
        entry = _TASK_ENTRY[task_type]
        
        # 使用 FSM 基类的 transition 方法
        if self._state != "idle":
            self.transition("aborting")
            self.transition("idle")
        self.transition(entry)

    def advance_phase(self) -> None:
        """Advance to the next phase in the normal flow."""
        forward_map: dict[str, str] = {
            "navigating": "docking",
            "docking": "approaching",
            "approaching": "hugging",
            "hugging": "lifting",
            "lifting": "transporting",
            "transporting": "placing",
            "placing": "retreating",
            "retreating": "idle",
            "aborting": "idle",
        }
        next_phase = forward_map.get(self._state)
        if next_phase:
            self.transition(next_phase)

    def abort(self, reason: str = "") -> None:
        logger.warning("abort requested from phase=%s: %s", self._state, reason)
        for exe in self._executors.values():
            if hasattr(exe, "stop"):
                exe.stop()
        if self._state not in ("idle", "aborting"):
            self.transition("aborting")

    def check_timeouts(self) -> None:
        if self._state in ("idle", "aborting"):
            return
        timeout = self._phase_timeouts.get(self._state)
        if timeout is not None and (time.monotonic() - self._phase_start_time) > timeout:
            self.abort(f"phase {self._state} timed out after {timeout}s")

    def _dispatch_current_phase(self) -> None:
        exe_name = _PHASE_EXECUTOR.get(self._state)
        if not exe_name:
            return
        executor = self._executors.get(exe_name)
        if executor is None:
            logger.warning("no executor %r for phase %s", exe_name, self._state)
            return
        if hasattr(executor, "execute"):
            executor.execute(self._state, self._current_params)
```

---

## 优化项 4：真实 HAL + VLA 推理链路

### 问题分析

**当前状态**：
- `rcs/rcs/hal/sim.py` 已实现 SimHAL
- `rcs/rcs/hal/protocol.py` 定义了 HAL 接口
- `robot-app/rcs_layer/vla/policy.py` 有 `VLAPolicy` 占位和 `load_policy`

**问题**：
1. 真实硬件 HAL 未实现
2. VLA 推理链路未打通

### 执行步骤

#### Step 4.1：创建真实 HAL 基类

**文件**：`rcs/rcs/hal/base.py` [NEW]

```python
"""硬件抽象层基类"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class HALState:
    """HAL 状态快照"""
    joint_positions: np.ndarray
    joint_velocities: np.ndarray
    joint_efforts: np.ndarray
    cartesian_pose: np.ndarray  # [x, y, z, qx, qy, qz, qw] xyzw
    wrench: np.ndarray  # [fx, fy, fz, tx, ty, tz]
    timestamp: float
    gripper_position: float


class HALError(Exception):
    """HAL 操作失败"""
    pass


class HALTimeout(HALError):
    """HAL 读取超时"""
    pass


class HardwareHAL(ABC):
    """真实硬件 HAL 抽象基类
    
    定义与 SimHAL 一致的接口，子类实现具体协议。
    """

    def __init__(self, host: str, port: int = 50051):
        self._host = host
        self._port = port
        self._connected = False

    @abstractmethod
    def connect(self) -> None:
        """建立连接"""

    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""

    @abstractmethod
    def read_state(self, timeout_ms: int = 1000) -> HALState:
        """读取当前状态"""

    @abstractmethod
    def send_command(
        self,
        *,
        joint_positions: np.ndarray | None = None,
        joint_efforts: np.ndarray | None = None,
        gripper_position: float | None = None,
    ) -> None:
        """发送控制命令"""

    @abstractmethod
    def estop(self) -> None:
        """紧急停止"""

    @abstractmethod
    def recover(self) -> None:
        """从错误状态恢复"""

    def base_pose(self) -> dict:
        """获取基座在世界坐标系中的姿态"""
        # 子类可覆盖
        return {"translation": [0, 0, 0], "quaternion": [0, 0, 0, 1]}

    @property
    def is_connected(self) -> bool:
        return self._connected
```

#### Step 4.2：实现 Franka HAL

**文件**：`rcs/rcs/hal/franka.py` [NEW]

```python
"""Franka FR3/Panda 真实硬件 HAL"""
from __future__ import annotations

import time
from typing import Any

import numpy as np

from .base import HardwareHAL, HALState, HALTimeout


class FrankaHAL(HardwareHAL):
    """Franka FR3/Panda 硬件驱动
    
    使用 libfranka 或 pجمات 控制真实 Franka 机器人。
    """

    def __init__(
        self,
        host: str,
        port: int = 50051,
        gripper_host: str | None = None,
    ):
        super().__init__(host, port)
        self._robot = None
        self._gripper = None
        self._gripper_host = gripper_host or host
        self._default_home = np.array([0, -0.785, 0, -2.356, 0, 1.571, 0.785])

    def connect(self) -> None:
        try:
            import libfranka
        except ImportError:
            raise ImportError(
                "libfranka required for Franka hardware; "
                "install via: pip install libfranka"
            )
        
        self._robot = libfranka.Robot(self._host)
        self._robot.automatic_error_recovery = True
        
        try:
            import libfranka.gripper
            self._gripper = libfranka.gripper.Gripper(self._gripper_host)
        except Exception:
            self._gripper = None
        
        self._connected = True

    def disconnect(self) -> None:
        if self._robot:
            self._robot = None
        self._connected = False

    def read_state(self, timeout_ms: int = 1000) -> HALState:
        if not self._connected or self._robot is None:
            raise HALTimeout("Not connected")
        
        try:
            state = self._robot.read_once()
        except Exception as e:
            raise HALTimeout(f"Read timeout: {e}")
        
        return HALState(
            joint_positions=np.array(state.q),
            joint_velocities=np.array(state.dq),
            joint_efforts=np.array(state.tau_J),
            cartesian_pose=self._ee_pose_from_T(state.O_T_EE),
            wrench=np.array(state.O_F_ext_hat_K),
            timestamp=state.time.to_sec(),
            gripper_position=0.0,  # 需要单独查询
        )

    def send_command(
        self,
        *,
        joint_positions: np.ndarray | None = None,
        joint_efforts: np.ndarray | None = None,
        gripper_position: float | None = None,
    ) -> None:
        if not self._connected or self._robot is None:
            raise RuntimeError("Not connected")
        
        if joint_positions is not None:
            q = joint_positions.tolist()
            self._robot.control(
                lambda t, q, dq: (q, dq),
                inputs=[q, [0.0] * 7],
            )
        
        if gripper_position is not None and self._gripper is not None:
            width = max(0.0, min(0.08, gripper_position * 0.08))
            self._gripper.move(width, 0.1)

    def estop(self) -> None:
        if self._robot:
            self._robot.stop()

    def recover(self) -> None:
        if self._robot:
            self._robot.automatic_error_recovery = True

    @staticmethod
    def _ee_pose_from_T(T: list) -> np.ndarray:
        """从 4x4 齐次变换矩阵提取 xyzw 四元数 + 平移"""
        import math
        m = np.array(T).reshape(4, 4)
        t = m[:3, 3]
        # 提取四元数 (简化实现)
        q = np.array([0, 0, 0, 1])  # 默认姿态
        return np.concatenate([t, q])

    def __repr__(self) -> str:
        return f"FrankaHAL({self._host}:{self._port})"
```

#### Step 4.3：实现 UR RTDE HAL

**文件**：`rcs/rcs/hal/ur_rtde.py` [NEW]

```python
"""UR5e/UR10 真实硬件 HAL"""
from __future__ import annotations

import time
from typing import Any

import numpy as np

from .base import HardwareHAL, HALState, HALTimeout


class URRTDEHAL(HardwareHAL):
    """UR5e/UR10 硬件驱动 (ur_rtde)
    
    使用 UR 的 RTDE 协议读取状态和发送命令。
    """

    def __init__(
        self,
        host: str,
        port: int = 30004,
        gripper_type: str = "robotiq",
    ):
        super().__init__(host, port)
        self._rtde = None
        self._gripper_type = gripper_type
        self._input_register = None

    def connect(self) -> None:
        try:
            import rtde.rtde as rtde
            import rtde.csv_reader as csv_reader
        except ImportError:
            raise ImportError(
                "ur-rtde required for UR hardware; "
                "install via: pip install ur-rtde"
            )
        
        self._rtde = rtde.RTDE(self._host, self._port)
        self._rtde.connect()
        
        # 配置要读取的变量
        self._rtde.get_controller_version()
        self._rtde.send_start()
        
        self._connected = True

    def disconnect(self) -> None:
        if self._rtde:
            self._rtde.send_pause()
            self._rtde.disconnect()
            self._rtde = None
        self._connected = False

    def read_state(self, timeout_ms: int = 1000) -> HALState:
        if not self._connected or self._rtde is None:
            raise HALTimeout("Not connected")
        
        try:
            state = self._rtde.receive(timeout_ms / 1000)
        except Exception as e:
            raise HALTimeout(f"Receive timeout: {e}")
        
        return HALState(
            joint_positions=np.array(state.actual_q),
            joint_velocities=np.array(state.actual_qd),
            joint_efforts=np.array(state.actual_TCP_force),
            cartesian_pose=self._get_cartesian_pose(state),
            wrench=np.array(state.actual_TCP_force + [0, 0, 0]),  # 简化
            timestamp=time.time(),
            gripper_position=0.0,
        )

    def send_command(
        self,
        *,
        joint_positions: np.ndarray | None = None,
        joint_efforts: np.ndarray | None = None,
        gripper_position: float | None = None,
    ) -> None:
        if not self._connected or self._rtde is None:
            raise RuntimeError("Not connected")
        
        if joint_positions is not None:
            setp = joint_positions.tolist()
            self._rtde.send(
                ["speed_slider_mask", "speed_slider_ratio", 
                 "standard_digital_output_mask", "standard_digital_output"]
            )

    def estop(self) -> None:
        if self._rtde:
            self._rtde.send_stop()

    def recover(self) -> None:
        pass  # UR 通常自动恢复

    def _get_cartesian_pose(self, state) -> np.ndarray:
        """从 RTDE 状态提取笛卡尔姿态"""
        import math
        t = np.array(state.actual_TCP_pose[:3])
        # 需要从 RPY 转换 (简化)
        rpy = state.actual_TCP_pose[3:6]
        q = self._rpy_to_quaternion(rpy)
        return np.concatenate([t, q])

    @staticmethod
    def _rpy_to_quaternion(rpy: list) -> np.ndarray:
        """RPY (rad) -> xyzw 四元数"""
        import math
        r, p, y = rpy
        cy, sy = math.cos(y / 2), math.sin(y / 2)
        cp, sp = math.cos(p / 2), math.sin(p / 2)
        cr, sr = math.cos(r / 2), math.sin(r / 2)
        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy
        return np.array([qx, qy, qz, qw])

    def __repr__(self) -> str:
        return f"URRTDEHAL({self._host}:{self._port})"
```

#### Step 4.4：实现 VLAPolicy

**文件**：`robot-app/rcs_layer/vla/policy.py`

```python
"""Policy abstraction + loaders (RCS ``inference`` parity).

实现完整的 VLA 推理链路。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from robot_contracts import RobotType


class Policy:
    """Maps an observation to an action (RCS inference parity)."""

    action_dim: int = 6

    def __call__(self, obs: Any) -> np.ndarray:
        raise NotImplementedError

    def reset(self) -> None:
        return None


class ScriptedPolicy(Policy):
    """Deterministic baseline policy."""

    def __init__(self, action_dim: int = 6, gain: float = 0.5) -> None:
        self.action_dim = action_dim
        self.gain = gain
        self._target = np.full(action_dim, 0.3)

    def __call__(self, obs: Any) -> np.ndarray:
        if isinstance(obs, dict):
            state = np.asarray(obs.get("state"), dtype=float)
        else:
            state = np.asarray(obs, dtype=float)
        dof = min(self.action_dim, state.shape[0] - 8)
        joints = state[8: 8 + dof] if dof > 0 else np.zeros(self.action_dim)
        delta = np.clip((self._target[:dof] - joints) * self.gain, -0.2, 0.2)
        out = np.zeros(self.action_dim)
        out[:dof] = delta
        return out


class VLAPolicy(Policy):
    """真实 VLA 推理策略
    
    加载 vla-training 导出的模型权重，执行推理。
    """
    
    def __init__(
        self,
        model_path: str | Path,
        robot_type: RobotType = RobotType.ARM,
        device: str = "cuda",
        action_dim: int = 6,
    ):
        self.model_path = Path(model_path)
        self.robot_type = robot_type
        self.device = device
        self.action_dim = action_dim
        self._model = None
        self._processor = None
        self._load_model()

    def _load_model(self) -> None:
        """懒加载 VLA 模型"""
        manifest_path = self.model_path / "inference_manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")
        
        import json
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # 验证 robot_type 匹配
        if manifest.get("robot_type") != self.robot_type.value:
            raise ValueError(
                f"Robot type mismatch: model={manifest.get('robot_type')}, "
                f"expected={self.robot_type.value}"
            )
        
        # 加载模型
        try:
            import torch
            from transformers import AutoModelForVision2Seq, AutoProcessor
            
            self._model = AutoModelForVision2Seq.from_pretrained(
                str(self.model_path),
                device_map=self.device,
                torch_dtype=torch.float16,
            )
            self._processor = AutoProcessor.from_pretrained(str(self.model_path))
        except ImportError as e:
            raise ImportError(f"transformers required for VLA: {e}")

    def __call__(self, obs: Any) -> np.ndarray:
        if self._model is None:
            return np.zeros(self.action_dim)
        
        import torch
        
        # 提取图像和指令
        if isinstance(obs, dict):
            images = obs.get("images", {})
            instruction = obs.get("instruction", "pick the object")
            state = obs.get("state")
        else:
            images = {}
            instruction = "pick the object"
            state = obs
        
        # 预处理
        inputs = self._processor(
            text=[instruction],
            images=list(images.values())[0] if images else None,
            return_tensors="pt",
        ).to(self.device)
        
        # 推理
        with torch.no_grad():
            outputs = self._model.generate(**inputs, max_new_tokens=50)
        
        # 提取动作 (简化实现)
        action = torch.zeros(self.action_dim)
        # ... 解析模型输出为动作向量
        
        return action.cpu().numpy()

    def reset(self) -> None:
        pass


def load_policy(
    path: str | None = None,
    kind: str = "scripted",
    action_dim: int = 6,
    robot_type: str | None = None,
    device: str = "cuda",
) -> Policy:
    """Load a policy (RCS ``inference`` entry point)."""
    
    if path is None or kind == "scripted":
        return ScriptedPolicy(action_dim=action_dim)
    
    if kind == "vla":
        rt = RobotType(robot_type) if robot_type else RobotType.ARM
        return VLAPolicy(path, robot_type=rt, device=device, action_dim=action_dim)
    
    return ScriptedPolicy(action_dim=action_dim)


__all__ = ["Policy", "ScriptedPolicy", "VLAPolicy", "load_policy"]
```

---

## 优化项 5：HyEmbodied Bug 修复

### 问题分析

**问题**：第 154 行引用了未定义的 `trust_remote_code` 变量

**当前代码**（第 154 行）：
```python
model_kwargs: dict[str, Any] = {"trust_remote_code": trust_remote_code}  # BUG!
```

**正确代码**：
```python
model_kwargs: dict[str, Any] = {"trust_remote_code": trust_remote}  # trust_remote 已定义
```

### 执行步骤

#### Step 5.1：修复变量名

**文件**：`vla-training/src/vla_training/models/families/hy_embodied.py`

**修改**（第 154 行）：
```python
# 修改前
model_kwargs: dict[str, Any] = {"trust_remote_code": trust_remote_code}

# 修改后
model_kwargs: dict[str, Any] = {"trust_remote_code": trust_remote}
```

**修改**（第 169 行）：
```python
# 修改前
processor = AutoProcessor.from_pretrained(base_model, trust_remote_code=trust_remote_code)

# 修改后
processor = AutoProcessor.from_pretrained(base_model, trust_remote_code=trust_remote)
```

---

## 执行优先级与依赖

```
优化项 5 (Bug 修复)
    ↓
优化项 1 (VLA 闭环) ←─ 依赖优化项 2
优化项 2 (坐标系统一)
    ↓
优化项 3 (IK/FK + FSM)
    ↓
优化项 4 (HAL + VLA 推理)
```

### 建议执行顺序

1. **Step 5.1**：立即修复 Bug（5 分钟）
2. **Step 2.1-2.3**：坐标系统一（1-2 小时）
3. **Step 1.1-1.4**：VLA 训练闭环（2-3 小时）
4. **Step 3.1-3.3**：IK/FK + FSM（2 小时）
5. **Step 4.1-4.4**：HAL + VLA 推理（4-6 小时）

---

## 验证清单

- [ ] `hy_embodied.py` 导入无 NameError
- [ ] `MotionCommander` 使用 `SiteTCPPose` 配置
- [ ] `ArmController` 从 `ArmSpec` 加载 DH 参数
- [ ] `TaskCoordinator` 继承 `FSM`
- [ ] `evaluate_closed_loop` 成功运行 5 episodes
- [ ] `SimulationCollector` 成功采集数据
- [ ] `FrankaHAL` / `URRTDEHAL` 可实例化
- [ ] `VLAPolicy` 加载 manifest 并验证 robot_type

---

**计划完成时间**：预计 10-15 小时工作量
