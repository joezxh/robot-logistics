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
    """Scripted or teleoperated rollouts inside the Gazebo simulation.

    Skeleton: wiring this up requires a scripted policy or teleop interface in
    the ``simulation`` subproject that can be stepped deterministically.
    """

    def __init__(self, output_dir: str | Path, *, camera_names: list[str] | None = None) -> None:
        super().__init__(output_dir)
        self.camera_names = camera_names or ["wrist_cam", "overhead_cam"]

    def collect(self, num_episodes: int, instruction: str) -> Iterator[Episode]:
        raise NotImplementedError(
            "SimulationCollector requires a scripted/teleop policy in the "
            "simulation subproject; see vla-training/README.md"
        )


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
