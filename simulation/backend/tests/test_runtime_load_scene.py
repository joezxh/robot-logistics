"""Tests for Runtime.reset() and Runtime.load_scene()."""
from backend.algorithm.scheduler.task import TaskPriority
from backend.services.runtime import Runtime


def test_reset_clears_devices_tasks_logs():
    runtime = Runtime()
    initial_device_count = len(runtime.devices.devices)
    assert initial_device_count > 0  # seeded devices
    runtime.create_task("dock_loading", "x", TaskPriority.NORMAL, "robot-01")
    assert len(runtime.tasks) > 0
    runtime.reset()
    assert len(runtime.devices.devices) == 0
    assert len(runtime.tasks) == 0
    assert len(runtime.logs) > 0  # reset logs its own entry


def test_load_scene_pallet_registers_expected_devices():
    runtime = Runtime()
    result = runtime.load_scene("pallet")
    assert result["scene"] == "pallet"
    device_ids = {d["device_id"] for d in result["devices"]}
    assert {"forklift-01", "forklift-02", "agv-01"}.issubset(device_ids)
    assert runtime.current_scene == "pallet"


def test_load_scene_box_loads_correctly():
    runtime = Runtime()
    result = runtime.load_scene("box")
    assert result["scene"] == "box"
    device_ids = {d["device_id"] for d in result["devices"]}
    assert "loader-01" in device_ids
    assert "stacker-01" in device_ids


def test_load_scene_bag_loads_correctly():
    runtime = Runtime()
    result = runtime.load_scene("bag")
    assert result["scene"] == "bag"
    device_ids = {d["device_id"] for d in result["devices"]}
    assert "loader-01" in device_ids


def test_load_scene_unknown_raises_keyerror():
    runtime = Runtime()
    try:
        runtime.load_scene("does-not-exist")
    except KeyError:
        return
    assert False, "expected KeyError"


def test_load_scene_clears_previous_state():
    runtime = Runtime()
    runtime.load_scene("pallet")
    count_after_pallet = len(runtime.devices.devices)
    runtime.load_scene("box")
    assert len(runtime.devices.devices) != count_after_pallet  # different device set
    device_ids = {d["device_id"] for d in runtime.devices.list()}
    assert "forklift-01" not in device_ids  # pallet-only device gone


def test_scene_kpi_returns_dict():
    runtime = Runtime()
    runtime.load_scene("pallet")
    kpi = runtime._scene_kpi("pallet")
    assert kpi["scene"] == "pallet"
    assert "throughput_per_hour" in kpi
    assert "success_rate" in kpi
