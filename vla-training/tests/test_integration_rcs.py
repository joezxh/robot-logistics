"""Cross-subproject integration test: vla-training <-> simulation <-> robot-app.

Verifies the RCS-aligned data loop closes: the SimulationCollector records
demonstrations inside the simulation Gym env using a robot-app policy, and the
closed-loop evaluator runs a policy through the same env + tasks. All four
subprojects share the robot_contracts Pose/RobotType vocabulary.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("d:/projects/robot-logic")
for p in [
    ROOT / "shared" / "python",
    ROOT / "simulation",
    ROOT / "robot-app",
    Path(__file__).resolve().parents[1] / "src",
]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import numpy as np  # noqa: E402

from vla_training.data.collector import SimulationCollector  # noqa: E402
from vla_training.data.types import SourceType  # noqa: E402
from vla_training.eval.evaluate import evaluate_closed_loop  # noqa: E402


def test_simulation_collector_records_episodes():
    collector = SimulationCollector(
        output_dir="tests/_tmp_collect", config_name="LogisticsArm",
        max_steps=10, expert="scripted", seed=0,
    )
    episodes = list(collector.collect(2, "pallet"))
    assert len(episodes) == 2
    for ep in episodes:
        assert ep.source == SourceType.SIMULATION
        assert len(ep.frames) > 0
        # frames carry joint positions + actions in the shared schema
        assert len(ep.frames[0].joint_positions) == 6
        assert len(ep.frames[0].action) == 6


def test_closed_loop_eval_runs_against_sim():
    report = evaluate_closed_loop(
        adapter=None, tasks=["pallet"], episodes_per_task=1, max_steps=5,
        config={"sim": {"config_name": "LogisticsArm"}, "action": {"robot_type": "ARM"}},
    )
    assert report.num_rollouts == 1
    assert 0.0 <= report.success_rate <= 1.0
