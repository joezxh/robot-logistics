"""Tests for DAG node model: TaskNode, TaskType, SLOClass, and DAG exceptions."""
from __future__ import annotations

from datetime import datetime

from rcs.dag.node import TaskNode, TaskType, SLOClass
from rcs.dag.exceptions import DAGError


def test_task_node_creation_minimal():
    node = TaskNode(task_id="t1", type=TaskType.TRANSPORT)
    assert node.task_id == "t1"
    assert node.type == TaskType.TRANSPORT
    assert node.device_id is None
    assert node.dependencies == []
    assert node.deadline is None
    assert node.slo_class == SLOClass.SOFT


def test_task_node_creation_full():
    deadline = datetime(2026, 12, 1, 12, 0, 0)
    node = TaskNode(
        task_id="t2",
        type=TaskType.PICK,
        device_id="loader-01",
        params={"sku": "A"},
        dependencies=["t1"],
        deadline=deadline,
        slo_class=SLOClass.HARD,
    )
    assert node.device_id == "loader-01"
    assert node.params == {"sku": "A"}
    assert node.dependencies == ["t1"]
    assert node.deadline == deadline
    assert node.slo_class == SLOClass.HARD


def test_dag_error_raised():
    err = DAGError("test message")
    assert str(err) == "test message"
