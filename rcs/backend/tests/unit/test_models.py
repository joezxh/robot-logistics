from rcs.db import models


def test_all_tables_present():
    expected = {"robot_devices", "robot_orders", "robot_order_items", "robot_order_tasks",
                "robot_unified_maps", "robot_map_dynamic_state", "robot_planning_profiles",
                "robot_scheduler_configs", "robot_command_logs", "robot_event_logs"}
    assert expected.issubset(set(models.Base.metadata.tables.keys()))


def test_device_has_spec_json():
    assert "spec_json" in models.Device.__table__.columns


def test_device_has_limits_json():
    assert "limits_json" in models.Device.__table__.columns


def test_device_has_home_joints_json():
    assert "home_joints_json" in models.Device.__table__.columns


def test_device_has_status():
    assert "status" in models.Device.__table__.columns


def test_orders_has_status():
    assert "status" in models.Order.__table__.columns


def test_order_task_has_status():
    assert "status" in models.OrderTask.__table__.columns