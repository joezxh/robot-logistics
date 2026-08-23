"""Tests for DAG graph: TaskDAG class with add/get, dependencies, topological sort, cycle detection, and ready-nodes."""
from __future__ import annotations

from rcs.dag.node import TaskNode, TaskType
from rcs.dag.graph import TaskDAG
from rcs.dag.exceptions import CycleError, NodeNotFoundError


def test_dag_add_and_get_node():
    dag = TaskDAG()
    node = TaskNode(task_id="t1", type=TaskType.TRANSPORT)
    dag.add_node(node)
    assert dag.get_node("t1") == node


def test_dag_get_unknown_node_raises():
    dag = TaskDAG()
    try:
        dag.get_node("unknown")
        assert False, "should have raised"
    except NodeNotFoundError:
        pass


def test_dag_topological_sort_linear():
    dag = TaskDAG()
    dag.add_node(TaskNode(task_id="t1", type=TaskType.PICK))
    dag.add_node(TaskNode(task_id="t2", type=TaskType.PLACE))
    dag.add_node(TaskNode(task_id="t3", type=TaskType.TRANSPORT))
    dag.add_dependency("t2", "t1")
    dag.add_dependency("t3", "t2")
    order = dag.topological_sort()
    assert order == ["t1", "t2", "t3"]


def test_dag_topological_sort_parallel():
    dag = TaskDAG()
    dag.add_node(TaskNode(task_id="t1", type=TaskType.PICK))
    dag.add_node(TaskNode(task_id="t2", type=TaskType.PICK))
    dag.add_node(TaskNode(task_id="t3", type=TaskType.PLACE))
    dag.add_dependency("t3", "t1")
    dag.add_dependency("t3", "t2")
    order = dag.topological_sort()
    assert order[0] in ("t1", "t2")
    assert order[1] in ("t1", "t2")
    assert order[2] == "t3"


def test_dag_cycle_detection():
    dag = TaskDAG()
    dag.add_node(TaskNode(task_id="t1", type=TaskType.PICK))
    dag.add_node(TaskNode(task_id="t2", type=TaskType.PLACE))
    dag.add_dependency("t1", "t2")
    try:
        dag.add_dependency("t2", "t1")
        assert False, "should have raised CycleError"
    except CycleError:
        pass


def test_dag_get_ready_nodes():
    dag = TaskDAG()
    dag.add_node(TaskNode(task_id="t1", type=TaskType.PICK))
    dag.add_node(TaskNode(task_id="t2", type=TaskType.PLACE))
    dag.add_node(TaskNode(task_id="t3", type=TaskType.TRANSPORT))
    dag.add_dependency("t2", "t1")
    ready = dag.get_ready_nodes()
    assert [n.task_id for n in ready] == ["t1"]
    dag.mark_completed("t1")
    ready = dag.get_ready_nodes()
    assert [n.task_id for n in ready] == ["t2"]