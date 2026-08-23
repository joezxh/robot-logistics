"""Teleoperation layer (RCS ``teleop`` parity).

Bridges an external input source (keyboard / SpaceMouse / VR / leader-arm) into
robot actions, mirroring RCS's ``teleop`` demos that record expert trajectories
for imitation learning. The input adapter is abstracted so any device can feed
the same action stream consumed by the simulation / inference pipelines.
"""
from __future__ import annotations

from .device import KeyboardAdapter, SpaceMouseAdapter, TeleopInput

__all__ = ["TeleopInput", "KeyboardAdapter", "SpaceMouseAdapter"]
