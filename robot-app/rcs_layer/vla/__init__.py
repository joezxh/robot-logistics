"""VLA inference layer (RCS ``inference`` parity).

Loads a trained policy produced by ``vla-training`` and maps an environment
observation (state + optional camera frames) to a robot action. The policy is
abstracted behind :class:`Policy` so both a learned VLA model and a scripted
baseline can be plugged in interchangeably.
"""
from __future__ import annotations

from .policy import Policy, ScriptedPolicy, load_policy

__all__ = ["Policy", "ScriptedPolicy", "load_policy"]
