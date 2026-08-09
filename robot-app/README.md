# robot-app — 装卸机器人端应用

机器人本体上运行的 ROS 2 应用。通过 MQTT 消息总线与 [RCS](../rcs/README.md) 双向通信：
接收控制命令并转为本地 ROS 2 动作，同时上报状态与遥测。

## 职责边界

| 做什么 | 不做什么 |
| --- | --- |
| 订阅 RCS 下发的运动命令并在本机执行 | 不做轨迹规划与插补（那是 RCS 的职责） |
| 上报机器人自身可观测的遥测（电量、温度、连通性） | 不做多设备调度（那是仿真编排后端的职责） |
| 提供机械臂硬件抽象（`robot_arm_hal`） | 不直接暴露 HTTP 接口 |

## 包结构

```
ros2_ws/src/
├── robot_arm_hal/      机械臂硬件抽象；同时作为仿真工作区的 underlay
├── robot_msgs/         消息契约（与 shared/contracts 严格对齐）
├── robot_gateway/      MQTT ↔ ROS 2 桥接
├── robot_decision/     决策层（预留 VLA 推理接入点）
└── robot_perception/   感知层
```

### robot_gateway 分层

自下而上，越靠下越不依赖 ROS，便于脱离 ROS 环境做单元测试：

| 模块 | 职责 | 需要 rclpy |
| --- | --- | --- |
| `mqtt_link.py` | MQTT 传输、断线重连、离线缓冲 | 否 |
| `contract.py` | 线上载荷 ↔ `robot_msgs` 转换 | 否 |
| `bridge.py` | 命令路由、遥测/状态上报 | 否 |
| `mqtt_bridge_node.py` | ROS 2 节点、参数、定时器 | 是 |

## 通信契约

主题与载荷定义在 [`shared/`](../shared/README.md)，RCS 与本工程共同引用，避免契约漂移。

| 主题 | 方向 | QoS | 说明 |
| --- | --- | --- | --- |
| `rcs/{device_id}/command` | 下行 | 1 | 运动命令，不可丢失 |
| `rcs/{device_id}/state` | 上行 | 0 | 状态帧，retain |
| `rcs/{device_id}/alert` | 上行 | 1 | 故障事件 |
| `robot/{device_id}/telemetry` | 上行 | 0 | 机器人遥测 |

### 两条关键设计约定

**急停走独立通路。** `estop` 命令由 `estop_sink` 处理，与普通运动命令的 `motion_sink`
分离，确保运动执行阻塞时急停仍能立即生效。

**遥测缓冲、状态不缓冲。** 断线期间遥测进入有界缓冲区（默认 256 条，超出丢弃最旧的），
重连后补发——这正是事后排查掉线原因所需的数据。状态帧则直接丢弃：补发一帧过期状态比
不发更危险。

## 构建

两个 ROS 2 工作区存在 underlay/overlay 依赖：`simulation` 的 URDF 通过
`$(find robot_arm_hal)` 引用本工程的包，因此**必须先构建并 source 本工程**。

```bash
./scripts/build_ros2_ws.sh          # 按正确顺序构建两个工作区
./scripts/build_ros2_ws.sh underlay # 只构建 robot-app
```

手工构建等价于：

```bash
source /opt/ros/jazzy/setup.bash
cd robot-app/ros2_ws && colcon build --symlink-install
source install/setup.bash                      # ← 关键：overlay 依赖此步
cd ../../simulation/ros2_ws && colcon build --symlink-install
```

## 运行

```bash
pip install -r robot-app/requirements.txt

ros2 run robot_gateway mqtt_bridge_node --ros-args \
  -p device_id:=robot-01 \
  -p broker_host:=127.0.0.1 \
  -p broker_port:=1883 \
  -p telemetry_hz:=1.0
```

### 节点参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `device_id` | `robot-01` | 本机身份；发往其他设备的命令会被忽略 |
| `broker_host` / `broker_port` | `127.0.0.1` / `1883` | Mosquitto 地址 |
| `broker_username` / `broker_password` | 空 | 可选鉴权 |
| `topic_prefix` | 空 | 多租户 broker 的全局前缀 |
| `telemetry_hz` | `1.0` | 遥测频率；设为 0 关闭 |

## 测试

网关的 ROS 无关层可直接用 pytest 运行，无需 ROS 2 环境：

```bash
cd robot-app/ros2_ws/src/robot_gateway
python -m pytest tests -q
```
