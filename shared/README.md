# shared — 共享通信契约层

RCS 机器人控制系统与装卸机器人端应用之间的**唯一契约来源**。

## 为什么存在

RCS 与 robot-app 是两个独立部署、独立演进的子工程，它们之间通过 MQTT 通信。如果双方各自定义主题字符串与载荷结构，任何一侧的修改都会静默破坏另一侧。本层把契约收敛为单一来源，让不一致在编译/测试期暴露而非运行期。

## 内容

```
shared/
├── contracts/                    # 规范性定义（语言无关）
│   ├── mqtt_topics.md            #   主题命名、QoS、Retain、频率约定
│   ├── command.schema.json       #   下行命令载荷
│   ├── state.schema.json         #   上行状态载荷
│   ├── alert.schema.json         #   上行告警载荷
│   └── telemetry.schema.json     #   上行遥测载荷
└── python/robot_contracts/       # Python 可执行实现
    ├── topics.py                 #   主题常量与构造/解析函数
    └── payloads.py               #   Pydantic 载荷模型
```

## 依赖方向

```
rcs/       ──→ shared/
robot-app/ ──→ shared/
```

**严格单向**。`shared/` 不得 import 任何子工程，也不得包含业务逻辑。它只有 `pydantic` 一个运行时依赖。

## 引用方式

把 `shared/python` 加入 `PYTHONPATH`：

```bash
export PYTHONPATH="$REPO_ROOT/shared/python:$PYTHONPATH"
```

或以可编辑方式安装：

```bash
pip install -e shared/python
```

然后：

```python
from robot_contracts import (
    command_topic, state_topic, QOS_COMMAND, QOS_STATE,
    CommandPayload, StatePayload,
)

topic = command_topic("robot-01")          # "rcs/robot-01/command"
cmd = CommandPayload(type="move_j", target_joints=[0.0] * 6)
client.publish(topic, cmd.model_dump_json(), qos=QOS_COMMAND)
```

容器内路径见 `rcs/Dockerfile` 与 `simulation/backend/Dockerfile`（均通过 `PYTHONPATH` 注入）。

## 变更流程

契约变更对通信双方都是**破坏性的**，禁止单侧修改：

1. 改 `contracts/*.schema.json`（规范先行）
2. 同步改 `python/robot_contracts/payloads.py`
3. 提升 `robot_contracts.__version__`
4. 同时更新 RCS 适配器（`rcs/rcs/mqtt/`）与机器人端桥接（`robot-app/ros2_ws/src/robot_gateway/`）
5. 补充/更新双侧契约一致性测试

## 与 REST 的关系

命令载荷字段与 RCS REST 接口的 `CommandRequest` **严格一致**，保证同一条命令无论从 REST 还是 MQTT 进入，行为完全相同。修改 REST 模型时必须同步本契约。
