from datetime import datetime, timedelta
from rcs.dag.node import TaskNode, TaskType, SLOClass
from rcs.scheduler.policy import compute_utility, UtilityWeights


def test_compute_utility_urgent_task_higher():
    now = datetime(2026, 1, 1, 12, 0, 0)
    soon = TaskNode(task_id="t1", type=TaskType.TRANSPORT, deadline=now + timedelta(seconds=10))
    late = TaskNode(task_id="t2", type=TaskType.TRANSPORT, deadline=now + timedelta(seconds=600))
    weights = UtilityWeights()
    assert compute_utility(soon, now, weights) > compute_utility(late, now, weights)


def test_compute_utility_hard_slo_higher():
    now = datetime(2026, 1, 1, 12, 0, 0)
    hard = TaskNode(task_id="t1", type=TaskType.TRANSPORT, deadline=now + timedelta(seconds=60), slo_class=SLOClass.HARD)
    best = TaskNode(task_id="t2", type=TaskType.TRANSPORT, deadline=now + timedelta(seconds=60), slo_class=SLOClass.BEST_EFFORT)
    weights = UtilityWeights()
    assert compute_utility(hard, now, weights) > compute_utility(best, now, weights)


def test_compute_utility_no_deadline_returns_lowest():
    now = datetime(2026, 1, 1, 12, 0, 0)
    node = TaskNode(task_id="t1", type=TaskType.TRANSPORT, deadline=None)
    weights = UtilityWeights()
    score = compute_utility(node, now, weights)
    assert score < 0.0
