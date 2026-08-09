# MQTT 主题规范

RCS 与装卸机器人端应用之间的消息总线契约。**本文件是规范性定义**，`shared/python/robot_contracts/topics.py` 是其可执行实现，双方必须通过该 Python 包引用主题，不得硬编码字符串。

## 主题一览

| 主题 | 方向 | QoS | Retain | 载荷 Schema |
| --- | --- | --- | --- | --- |
| `rcs/{device_id}/command` | 下行：外部/机器人端 → RCS | 1 | false | `command.schema.json` |
| `rcs/{device_id}/state` | 上行：RCS → 机器人端 | 0 | **true** | `state.schema.json` |
| `rcs/{device_id}/alert` | 上行：RCS → 机器人端 | 1 | false | `alert.schema.json` |
| `robot/{device_id}/telemetry` | 上行：机器人端 → RCS | 0 | false | `telemetry.schema.json` |

`{device_id}` 为 RCS 设备注册表中的标识（如 `robot-01`、`agv-01`、`stacker-01`），不含 `/`、`+`、`#`。

## 通配订阅

| 订阅方 | 主题过滤器 |
| --- | --- |
| RCS 订阅全部设备命令 | `rcs/+/command` |
| 机器人端订阅全部设备状态 | `rcs/+/state` |
| 机器人端订阅全部告警 | `rcs/+/alert` |
| RCS 订阅全部遥测 | `robot/+/telemetry` |

## 主题前缀

多租户 broker 场景下可配置全局前缀（RCS 侧环境变量 `RCS_MQTT_TOPIC_PREFIX`）。前缀会拼接在最前面，例如前缀 `site-a` 时命令主题为 `site-a/rcs/robot-01/command`。**通信双方必须配置相同前缀**，否则彼此不可见。

## QoS 与 Retain 的取舍依据

- **命令 QoS 1**：命令不可丢失。使用 `command_id` 做幂等，重复投递由 RCS 侧的命令队列去重处理。
- **状态 QoS 0**：状态是高频、可被下一帧取代的数据。QoS 1 的确认开销在 10Hz × N 设备下不划算，且丢一帧无实质影响。
- **状态 Retain = true**：迟到的订阅者能立即获知当前状态，无需等待下一个采样周期。
- **告警 QoS 1**：故障事件不可丢失。
- **告警 Retain = false**：告警是瞬时事件，保留会让新订阅者收到历史故障并误判为当前故障。

## 发布频率

- 状态：默认 10Hz。RCS 的 `StateStream` 内部已限速 10Hz，MQTT 适配器可通过 `RCS_MQTT_STATE_PUBLISH_HZ` 进一步降采样以减轻 broker 压力（设为 0 则关闭状态发布）。
- 告警：事件驱动，无固定频率。
- 遥测：由机器人端自行决定，建议 1Hz。

> **关键约束**：RCS 的控制回路最高 1000Hz（`robot-01`），**任何 MQTT I/O 都不得进入 tick 循环**。适配器完全运行在独立协程中，通过 `StateStream.subscribe()` 队列与 `EventBus` 消费数据。

## 命令入口一致性

MQTT 命令与 REST 命令走**完全相同**的处理路径：

```
MQTT rcs/{id}/command ─┐
                       ├─→ registry.get_controller(id).on_command(cmd) ─→ 命令队列(容量1024) ─→ ControlLoop tick
REST /api/rcs/{id}/command ─┘
```

因此载荷字段必须与 REST 的 `CommandRequest` 严格一致（见 `command.schema.json`）。任何一侧新增字段都必须同步修改本契约。

## 变更流程

1. 修改 `shared/contracts/*.schema.json`（规范）
2. 同步修改 `shared/python/robot_contracts/payloads.py`（实现）
3. 提升 `robot_contracts.__version__`
4. 同时更新 RCS 侧适配器与 robot-app 侧桥接节点
5. 补充双侧契约一致性测试

契约变更对通信双方都是破坏性的，禁止单侧修改。
