"""Tests for the RCS-aligned robot-app layer (tasks, vla, teleop)."""
from __future__ import annotations

import sys
from types import SimpleNamespace

import numpy as np

# Make shared contract importable without install.
sys.path.insert(0, "d:/projects/robot-logic/shared/python")

from robot_contracts import Pose, RobotType  # noqa: E402

sys.path.insert(0, "d:/projects/robot-logic/robot-app")  # rcs_layer package

from rcs_layer.tasks import get_task, PalletTask  # noqa: E402
from rcs_layer.vla import load_policy, ScriptedPolicy  # noqa: E402
from rcs_layer.teleop import KeyboardAdapter  # noqa: E402


class _FakeExec:
    """Minimal stand-in for PalletTaskExecutor so the task is testable w/o ROS."""

    def __init__(self):
        self.state = "approach"
        self._failed = False
        self._stages = ["approach"]

    def start_task(self, params=None):
        self.state = "approach"
        self._stages = ["approach"]
        self._failed = False

    def advance(self):
        seq = ["approach", "engage", "lift", "transfer", "place", "idle"]
        i = seq.index(self.state)
        if i < len(seq) - 1:
            self.state = seq[i + 1]
            if self.state != "idle":
                self._stages.append(self.state)

    @property
    def _failed_flag(self):
        return self._failed


def test_pallet_task_runs_through_stages():
    task = PalletTask(executor=_FakeExec())
    task.reset()
    info = {"ee_pose": Pose.from_keywords(x=5.0, y=0.0, z=2.0)}
    assert task.reward(info) > 0.0
    for _ in range(6):
        task.step_stage()
    assert task.done(info) is True
    res = task.result()
    assert res.success
    assert "place" in res.completed_stages


def test_task_registry_lookup():
    t = get_task("pallet")
    assert isinstance(t, PalletTask)
    assert t.robot_type == RobotType.ARM


def test_vla_load_policy_default_is_scripted():
    policy = load_policy(kind="scripted", action_dim=6)
    assert isinstance(policy, ScriptedPolicy)
    obs = np.zeros(8 + 6)
    action = policy(obs)
    assert action.shape == (6,)


def test_teleop_keyboard_adapter():
    kb = KeyboardAdapter(step=0.01)
    kb.press("w")
    d = kb.read()
    assert d[0] == 0.01
    kb.release("w")
    assert np.allclose(kb.read(), 0.0)
