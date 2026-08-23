from rcs.dag.node import TaskNode, TaskType
from rcs.scheduler.allocator import DeviceCandidate, select_device


def test_select_device_prefers_closest():
    task = TaskNode(task_id="t1", type=TaskType.TRANSPORT)
    candidates = [
        DeviceCandidate(device_id="agv-01", type="diff_drive", load_capacity=100, current_utilization=0.5),
        DeviceCandidate(device_id="agv-02", type="diff_drive", load_capacity=100, current_utilization=0.1),
    ]
    selected = select_device(task, candidates)
    assert selected.device_id == "agv-02"


def test_select_device_no_candidate_returns_none():
    task = TaskNode(task_id="t1", type=TaskType.TRANSPORT)
    assert select_device(task, []) is None


def test_select_device_skips_overloaded():
    task = TaskNode(task_id="t1", type=TaskType.TRANSPORT)
    candidates = [
        DeviceCandidate(device_id="busy", type="diff_drive", load_capacity=100, current_utilization=0.95),
        DeviceCandidate(device_id="free", type="diff_drive", load_capacity=100, current_utilization=0.1),
    ]
    selected = select_device(task, candidates, max_utilization=0.9)
    assert selected.device_id == "free"