# Robot-App (ROS2)

Top 3 loading-scene ROS2 device drivers + MQTT bridge to RCS.

## Packages

| Package | Role |
|---------|------|
| `robot_arm_hal` | Forklift / gripper / dual-arm HAL with SIM/REAL dual-mode |
| `robot_decision` | Per-task executors driven by a generic FSM |
| `robot_perception` | Detection, monitoring, and collision avoidance |
| `mqtt_bridge` | ROS2 ↔ MQTT bidirectional bridge |

## Quick start

### Docker Compose (recommended)

```bash
cd robot-app
docker-compose up -d
docker-compose logs -f robot_app
```

### Local ROS2 Humble + Python 3.10+

```bash
cd robot-app/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch robot_arm_hal forklift_driver.launch.py
ros2 launch mqtt_bridge mqtt_bridge.launch.py
ros2 launch robot_decision pallet_executor  # or box_executor / bag_executor
```

## HAL mode

Selectable via environment variable:

```bash
HAL_MODE=sim    # default: in-memory mock driver
HAL_MODE=real   # real hardware via MQTT_BROKER_HOST/PLC_TOPIC_*
```

## Topics with RCS

The `mqtt_bridge` subscribes / publishes the following RCS MQTT topics:

| ROS2 Topic | MQTT Topic |
|------------|-----------|
| `/forklift/command` | `rcs/forklift-01/command` |
| `/forklift/joint_states` | `rcs/forklift-01/joint_states` |
| `/gripper/command` | `rcs/loader-01/command` |
| `/gripper/wrench` | `rcs/loader-01/wrench` |

See `mqtt_bridge/topic_mapping.yaml` for the full mapping.