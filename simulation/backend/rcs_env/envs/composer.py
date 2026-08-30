"""ModelComposer — MuJoCo 场景组合器（rcs.sim 对齐）

Mirrors ``robot-control-stack.rcs.sim.composer.ModelComposer``：
* 基于 ``mujoco.MjSpec`` 以编程方式拼装世界场景（机器人 / 夹爪 / 物体 / 相机）
* 支持世界坐标系下按位姿放置，并按 prefix 隔离多实例
* ``compile`` 后交给 :class:`MuJoCoEngine` 加载（engine 通过 rcs.sim.Sim 读取 MJCF）

与 RCS 版本的差异：
* 位姿使用 :class:`robot_contracts.Pose`（xyzw 约定），内部转换为 MuJoCo 的 wxyz
* 不依赖 ``rcs._core.common.Pose``，保持 robot-logic 自有契约
* 提供 :meth:`build_engine` 便捷入口，直接产出已加载的 :class:`MuJoCoEngine`

需要 MuJoCo；在无头/无 MuJoCo 环境下，构造与拼装方法会延迟到调用时才报错。
"""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from robot_contracts import Pose, RobotType

from ..engine import EngineConfig, MuJoCoEngine

# mujoco is optional at import time; imported lazily inside _require_mujoco()
mujoco = None


@dataclass
class EnvConfig:
    """场景组成配置（RCS SimEnvCreatorConfig 之上的场景层）。

    robot-logic 用 EnvConfig 描述一个"世界"：一台或多台机器人 + 物体 + 相机，
    再由 ModelComposer 拼装成 MJCF，最后交给 MuJoCoEngine 加载。
    """

    name: str = "rcs_scene"
    base_xml: str | None = None  # 世界骨架（地面 / 灯光 / 默认相机）
    robots: list["RobotSpec"] = field(default_factory=list)
    objects: list["ObjectSpec"] = field(default_factory=list)
    cameras: list["CameraSpec"] = field(default_factory=list)
    add_gravcomp: bool = False
    dt: float = 0.002


@dataclass
class RobotSpec:
    xml_path: str
    prefix: str
    pose: Pose = field(default_factory=Pose)
    gripper: Optional["GripperSpec"] = None


@dataclass
class GripperSpec:
    xml_path: str
    prefix: str = "gripper_"
    attachment_site: str = "attachment_site"
    pose: Pose = field(default_factory=Pose)


@dataclass
class ObjectSpec:
    xml_path: str
    prefix: str
    pose: Pose = field(default_factory=Pose)
    attach_to: str | None = None  # robot prefix；为 None 则挂在世界坐标系
    attachment_site: str = "attachment_site"
    register_free_joints: bool = False


@dataclass
class CameraSpec:
    name: str
    resolution: tuple[int, int] = (320, 240)
    fovy: float = 45.0
    pose: Pose = field(default_factory=Pose)
    attach_to: str | None = None  # robot prefix；为 None 则挂在世界坐标系
    attachment_site: str = "attachment_site"


class ModelComposer:
    """MuJoCo 场景组合器（MjSpec + 灵活位姿 + prefix 隔离）。"""

    def __init__(self, model_name: str = "rcs_scene", add_gravcomp: bool = False) -> None:
        self._require_mujoco()
        self.spec = mujoco.MjSpec()  # type: ignore[attr-defined]
        self.spec.modelname = model_name
        self.spec.compiler.autolimits = True
        self.add_gravcomp = add_gravcomp
        self._gravcomp_prefixes: set[str] = set()

    # ---- 依赖 ---------------------------------------------------------------- #
    @staticmethod
    def _require_mujoco():
        global mujoco
        if mujoco is not None:
            return mujoco
        try:
            import mujoco as _mj
        except ImportError as exc:  # pragma: no cover - optional dep
            raise RuntimeError("ModelComposer requires mujoco") from exc
        mujoco = _mj
        return mujoco

    # ---- 工具 ---------------------------------------------------------------- #
    def _resolve_asset_paths(self, spec, xml_path: str) -> None:
        xml_dir = os.path.dirname(os.path.abspath(xml_path))
        mesh_base = os.path.join(xml_dir, spec.meshdir or "")
        tex_base = os.path.join(xml_dir, spec.texturedir or "")
        for mesh in spec.meshes:
            if mesh.file and not os.path.isabs(mesh.file):
                mesh.file = os.path.abspath(os.path.join(mesh_base, mesh.file))
        for tex in spec.textures:
            if tex.file and not os.path.isabs(tex.file):
                tex.file = os.path.abspath(os.path.join(tex_base, tex.file))

    def _find_site(self, name: str):
        for s in self.spec.sites:
            if s.name == name:
                return s
        return None

    def _find_body(self, name: str):
        try:
            return self.spec.body(name)
        except ValueError:
            return None

    def _find_camera(self, name: str):
        for camera in self.spec.cameras:
            if camera.name == name:
                return camera
        return None

    @staticmethod
    def _wxyz(pose: Pose):
        """robot_contracts.Pose (xyzw) -> MuJoCo (w, x, y, z) 列表。"""
        q = pose.quaternion
        return [float(q[3]), float(q[0]), float(q[1]), float(q[2])]

    def _apply_pose(self, body, pose: Pose) -> None:
        body.pos = list(np.asarray(pose.translation, dtype=float))
        body.quat = self._wxyz(pose)

    # ---- 组成 ---------------------------------------------------------------- #
    def load_base_scene(self, xml_path: str) -> None:
        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"Base scene XML not found: {xml_path}")
        self.spec = mujoco.MjSpec.from_file(xml_path)  # type: ignore[attr-defined]
        self._resolve_asset_paths(self.spec, xml_path)

    def add_robot(self, xml_path: str, prefix: str, pose: Pose | None = None):
        if pose is None:
            pose = Pose()
        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"Robot MJCF not found: {xml_path}")
        child_spec = mujoco.MjSpec.from_file(xml_path)  # type: ignore[attr-defined]
        self._resolve_asset_paths(child_spec, xml_path)
        frame = self.spec.worldbody.add_frame()
        self.spec.attach(child_spec, prefix=prefix, frame=frame)
        root_name = child_spec.worldbody.first_body().name
        robot_root = self._find_body(root_name)
        if not robot_root:
            raise ValueError(f"Could not find robot root '{root_name}' after attach")
        self._apply_pose(robot_root, pose)
        if prefix:
            self._gravcomp_prefixes.add(prefix)
        return robot_root

    def add_gripper(
        self,
        xml_path: str,
        robot_prefix: str,
        gripper_prefix: str = "gripper_",
        attachment_site_name: str = "attachment_site",
        pose: Pose | None = None,
    ):
        if pose is None:
            pose = Pose()
        site = self._find_site(robot_prefix + attachment_site_name)
        if not site:
            raise ValueError(f"Attachment site '{robot_prefix}{attachment_site_name}' not found")
        gripper_spec = mujoco.MjSpec.from_file(xml_path)  # type: ignore[attr-defined]
        self._resolve_asset_paths(gripper_spec, xml_path)
        root = gripper_spec.worldbody.first_body()
        root = site.attach_body(root, gripper_prefix, "")
        self._apply_pose(root, pose)
        if gripper_prefix:
            self._gravcomp_prefixes.add(gripper_prefix)
        return root

    def add_object(
        self,
        xml_path: str,
        object_prefix: str,
        pose: Pose | None = None,
        attach_to: str | None = None,
        attachment_site_name: str = "attachment_site",
        register_free_joints: bool = False,
    ):
        if pose is None:
            pose = Pose()
        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"Object MJCF not found: {xml_path}")
        child_spec = mujoco.MjSpec.from_file(xml_path)  # type: ignore[attr-defined]
        self._resolve_asset_paths(child_spec, xml_path)
        if attach_to is None:
            frame = self.spec.worldbody.add_frame()
            self.spec.attach(child_spec, prefix=object_prefix, suffix="", frame=frame)
            # attach wraps the child in a frame; the body keeps its original name
            root_name = child_spec.worldbody.first_body().name
            obj_root = self._find_body(root_name)
        else:
            site = self._find_site(attach_to + attachment_site_name)
            if not site:
                raise ValueError(f"Attachment site '{attach_to}{attachment_site_name}' not found")
            root = child_spec.worldbody.first_body()
            obj_root = site.attach_body(root, prefix=object_prefix, suffix="")
        if obj_root is None:
            raise ValueError(f"Could not attach object '{object_prefix}'")
        self._apply_pose(obj_root, pose)
        return obj_root

    def add_camera(self, spec: CameraSpec):
        if spec.pose is None:
            pose = Pose()
        else:
            pose = spec.pose
        if spec.attach_to is None:
            mount = self.spec.worldbody.add_body()
            mount.name = f"{spec.name}_mount"
        else:
            site = self._find_site(spec.attach_to + spec.attachment_site)
            if not site:
                raise ValueError(f"Attachment site '{spec.attach_to}{spec.attachment_site}' not found")
            mount_body = mujoco.MjSpec().worldbody.add_body()  # type: ignore[attr-defined]
            mount_body.name = "mount"
            mount = site.attach_body(mount_body, f"{spec.name}_", "")
        self._apply_pose(mount, pose)
        camera = mount.add_camera()
        camera.name = spec.name
        camera.resolution = spec.resolution
        camera.fovy = spec.fovy
        return camera

    # ---- 输出 ---------------------------------------------------------------- #
    def compile_spec(self):
        self._apply_gravcomp()
        return self.spec.compile()

    def save_mjcf(self, output_path: str) -> str:
        self._apply_gravcomp()
        self.spec.compile()
        xml_str = self.spec.to_xml()
        with open(output_path, "w") as f:
            f.write(xml_str)
        return xml_str

    def _apply_gravcomp(self) -> None:
        if not self.add_gravcomp or not self._gravcomp_prefixes:
            return
        for body in self.spec.bodies:
            if body.name and any(body.name.startswith(p) for p in self._gravcomp_prefixes):
                body.gravcomp = 1
        for joint in self.spec.joints:
            if joint.name and any(joint.name.startswith(p) for p in self._gravcomp_prefixes):
                joint.actgravcomp = True

    # ---- 便捷入口 ------------------------------------------------------------ #
    def build_engine(self, config: EngineConfig | None = None) -> MuJoCoEngine:
        """拼装场景并产出已加载的 MuJoCoEngine（写入临时 MJCF）。"""
        fd, tmp = tempfile.mkstemp(suffix=".xml", prefix="rcs_composed_")
        os.close(fd)
        try:
            self.save_mjcf(tmp)
            cfg = config or EngineConfig()
            cfg.mjcf_path = tmp
            return MuJoCoEngine(cfg)
        finally:
            # 引擎在自身目录加载后即拷贝进 Sim，可清理临时文件
            try:
                os.remove(tmp)
            except OSError:
                pass


def compose_env(env_config: EnvConfig, robot_type=None, dt: float | None = None) -> MuJoCoEngine:
    """从 EnvConfig 一键拼装并构建 MuJoCoEngine。"""
    composer = ModelComposer(model_name=env_config.name, add_gravcomp=env_config.add_gravcomp)
    if env_config.base_xml:
        composer.load_base_scene(env_config.base_xml)
    for r in env_config.robots:
        composer.add_robot(r.xml_path, r.prefix, r.pose)
        if r.gripper:
            g = r.gripper
            composer.add_gripper(g.xml_path, r.prefix, g.prefix, g.attachment_site, g.pose)
    for o in env_config.objects:
        composer.add_object(
            o.xml_path, o.prefix, o.pose, o.attach_to, o.attachment_site, o.register_free_joints
        )
    for c in env_config.cameras:
        composer.add_camera(c)
    return composer.build_engine(
        EngineConfig(robot_type=robot_type or RobotType.ARM, dt=dt or env_config.dt)
    )


__all__ = [
    "ModelComposer",
    "EnvConfig",
    "RobotSpec",
    "GripperSpec",
    "ObjectSpec",
    "CameraSpec",
    "compose_env",
]
