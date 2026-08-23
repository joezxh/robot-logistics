"""Trajectory collection from the simulator and from real robots.

Two backends behind one interface so downstream code never branches on source:

* :class:`SimulationCollector` -- drives the ``simulation`` subproject.
* :class:`MqttCollector` -- passively records the live MQTT bus (the same
  ``rcs/{device_id}/state`` stream the robot gateway publishes), which is how
  teleoperated real-robot demonstrations get captured.

Episodes are written as JSON manifests plus image files rather than one large
binary: it keeps collection crash-tolerant and makes individual episodes
inspectable, which matters far more during data collection than read throughput.
"""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator

import numpy as np

from .types import Episode, Frame, SourceType

logger = logging.getLogger(__name__)


class TrajectoryCollector(ABC):
    """Interface every collection backend implements."""

    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def collect(self, num_episodes: int, instruction: str) -> Iterator[Episode]:
        """Yield episodes one at a time.

        Streaming rather than returning a list: a collection run can produce far
        more data than fits in memory, and a crash at episode 900 must not lose
        the first 899.
        """

    def save(self, episode: Episode) -> Path:
        """Persist one episode as a JSON manifest. Image files are referenced by
        path and are expected to already exist on disk."""
        episode.validate()
        path = self.output_dir / f"{episode.episode_id}.json"
        payload = {
            "episode_id": episode.episode_id,
            "instruction": episode.instruction,
            "source": episode.source.value,
            "success": episode.success,
            "metadata": episode.metadata,
            "frames": [
                {
                    "timestamp_ns": f.timestamp_ns,
                    "images": f.images,
                    "joint_positions": f.joint_positions,
                    "joint_velocities": f.joint_velocities,
                    "action": f.action,
                    "gripper": f.gripper,
                }
                for f in episode.frames
            ],
        }
        # Write-then-rename so an interrupted run never leaves a half-written
        # manifest that the converter would later choke on.
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload), encoding="utf-8")
        tmp.replace(path)
        logger.info("saved episode %s (%d frames)", episode.episode_id, len(episode))
        return path

    @staticmethod
    def load(path: str | Path) -> Episode:
        """Read back an episode manifest written by :meth:`save`."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return Episode(
            episode_id=data["episode_id"],
            instruction=data["instruction"],
            source=SourceType(data["source"]),
            success=bool(data.get("success", True)),
            metadata=data.get("metadata", {}),
            frames=[
                Frame(
                    timestamp_ns=int(f["timestamp_ns"]),
                    images=f.get("images", {}),
                    joint_positions=f.get("joint_positions", []),
                    joint_velocities=f.get("joint_velocities", []),
                    action=f.get("action", []),
                    gripper=float(f.get("gripper", 0.0)),
                )
                for f in data["frames"]
            ],
        )


class SimulationCollector(TrajectoryCollector):
    """Scripted or teleoperated rollouts inside the ``simulation`` Gym env.

    RCS-aligned (mirrors RCS imitation/teleop demos): the expert can be either a
    :class:`Policy` (robot-app ``rcs_layer.vla``) or a teleop device
    (robot-app ``rcs_layer.teleop``). Both drive the ``simulation.rcs_env.SimEnv``
    so demonstrations are collected in the *same* observation/action space the
    trained policy will later run in -- closing the sim-to-real loop.

    The module stays importable without the simulation/robot-app packages: the env
    is constructed lazily inside :meth:`collect`, so a missing dependency raises a
    clear error only when collection is actually run.
    """

    def __init__(
        self,
        output_dir: str | Path,
        *,
        camera_names: list[str] | None = None,
        config_name: str = "LogisticsArm",
        max_steps: int = 200,
        expert: str = "scripted",  # "scripted" | "teleop"
        seed: int = 0,
    ) -> None:
        super().__init__(output_dir)
        self.camera_names = camera_names or ["wrist_cam", "overhead_cam"]
        self.config_name = config_name
        self.max_steps = max_steps
        self.expert = expert
        self.seed = seed

    def _build_env_and_expert(self):
        """懒加载 simulation 和 robot-app 依赖"""
        import sys
        from pathlib import Path

        # 动态添加 simulation/backend 路径
        project_root = Path(__file__).resolve().parents[4]
        sim_backend = project_root / "simulation" / "backend"
        if str(sim_backend) not in sys.path:
            sys.path.insert(0, str(sim_backend))

        # 动态添加 robot-app 路径
        robot_app = project_root / "robot-app"
        if str(robot_app) not in sys.path:
            sys.path.insert(0, str(robot_app))

        from backend.rcs_env import SimEnv
        from backend.rcs_env.envs.configs import get_config
        from rcs_layer.vla import load_policy
        from rcs_layer.teleop import KeyboardAdapter

        cfg = get_config(self.config_name)
        env = SimEnv(
            robot_type=cfg.robot_type,
            mjcf_path=cfg.mjcf_path,
            logic_device_id=cfg.logic_device_id,
            planner=cfg.planner,
        )
        env.reset(seed=self.seed)
        if self.expert == "teleop":
            expert = KeyboardAdapter()
        else:
            expert = load_policy(kind="scripted", action_dim=env.engine.dof)
        return env, expert

    def collect(self, num_episodes: int, instruction: str) -> Iterator[Episode]:
        env, expert = self._build_env_and_expert()
        # optionally wrap with a task (robot-app) to mark episode success
        try:
            from robot_app.rcs_layer.tasks import get_task

            task = get_task(instruction) if instruction in ("pallet", "box", "bag") else None
        except Exception:
            task = None
        if task is not None:
            task.reset()

        for ep_idx in range(num_episodes):
            obs, info = env.reset()
            frames: list[Frame] = []
            success = True
            for step in range(self.max_steps):
                if self.expert == "teleop":
                    action = expert.get_action(obs)
                else:
                    action = expert(obs)
                obs, reward, terminated, truncated, info = env.step(action)
                frames.append(
                    Frame(
                        timestamp_ns=step,
                        images={cam: f"sim/{cam}/{ep_idx}/{step}.png" for cam in self.camera_names},
                        joint_positions=list(info.get("joints", [])),
                        joint_velocities=[0.0] * env.engine.dof,
                        action=list(np.asarray(action, dtype=float)),
                        gripper=float(info.get("gripper", 0.0)),
                    )
                )
                if task is not None and task.done(info):
                    success = True
                    break
                if terminated or truncated:
                    success = False
                    break
            yield self.save_episode(f"{self.config_name}_{ep_idx}", instruction, success, frames, task)

    def save_episode(self, episode_id, instruction, success, frames, task) -> Episode:
        ep = Episode(
            episode_id=episode_id,
            instruction=instruction,
            source=SourceType.SIMULATION,
            success=success,
            metadata={"config_name": self.config_name, "expert": self.expert,
                      "task": getattr(task, "name", None)},
            frames=frames,
        )
        self.save(ep)
        return ep


class MqttCollector(TrajectoryCollector):
    """Passively records demonstrations off the live MQTT bus.

    Subscribes to ``rcs/{device_id}/state`` -- the same stream the robot gateway
    publishes -- so recording a real-robot demonstration needs no changes to the
    robot itself. Episode boundaries are driven by explicit
    :meth:`start_episode` / :meth:`end_episode` calls from the operator tooling,
    because there is no reliable way to infer them from the state stream alone.
    """

    def __init__(
        self,
        output_dir: str | Path,
        *,
        device_id: str,
        broker_host: str = "127.0.0.1",
        broker_port: int = 1883,
    ) -> None:
        super().__init__(output_dir)
        self.device_id = device_id
        self.broker_host = broker_host
        self.broker_port = broker_port

    def collect(self, num_episodes: int, instruction: str) -> Iterator[Episode]:
        raise NotImplementedError(
            "MqttCollector requires operator tooling to mark episode boundaries; "
            "see vla-training/README.md"
        )
