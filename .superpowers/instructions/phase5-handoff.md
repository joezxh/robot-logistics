# Phase 5 后续 Agent 交付清单

> **目的**：为下一位接手 Phase 5（仿真真跑 + Gazebo + ROS2）的实施 / 验收 Agent 提供"一次性看完即可开工"的口袋手册。
> **设计规范**：`docs/superpowers/specs/2026-07-23-robot-logic-phase5-design.md`
> **既有实施计划**：`docs/superpowers/plans/2026-07-23-robot-logic-prototype.md`（Phase 1–4，仅作对照，**不要修改**）

---

## A. 开工前自检（必做）

1. **范围确认**：本阶段仅在 `backend/gateway/`、`frontend/src/edge/`、`frontend/src/supervisor/`、`ros2_ws/`、`scripts/verify_m*.sh` 新增内容；**不要触碰** `backend/api/`、`backend/services/`、`backend/algorithm/`、`backend/data/`、`backend/logging/`、`backend/main.py`、`backend/config.py`、`backend/data/prototype.db` 已有逻辑。
2. **不要重命名/删除** Phase 1–4 的接口；Phase 5 的 `tasks.py` / `ws_*.py` 是新增的"网关桥"，不是替代。
3. **任务幂等**：所有 Action 调用必须带 `task_id`，`/api/devices/{id}/tasks` 收到重复 `task_id` 返回原 task 状态而非重新下发。
4. **限速护栏**：M1 起即在 MoveIt 配置中写入 `default_velocity_scaling=0.2`（安全位）与 `default_acceleration_scaling=0.2`，后续可放开。
5. **急停优先**：所有"清零"操作只能由本地 HMI 触发，FastAPI/前端**不**提供清零按钮。

---

## B. 推荐实施顺序（M0 → M5 顺次）

### M0 骨架（1 天）
- 目录：`ros2_ws/src/{robot_msgs,robot_bringup,robot_moveit_config,robot_arm_hal,robot_perception,robot_decision,robot_gateway}`
- 包配置文件：`package.xml`、`setup.py`、`setup.cfg`
- launch：`launch/empty_world.launch.py`（仅 Gazebo 空世界 + robot_description）
- 验收：`scripts/verify_m0.sh`

### M1 机器人与仿真（2–3 天）
- `urdf/robot.urdf.xacro` + `srdf/robot.srdf` + `config/joint_limits.yaml` + `config/kinematics.yaml`
- MoveIt：`moveit_config/`，含 `ompl_planning.yaml` 与 `controllers.yaml`
- `ros2_control`：`robot_arm_hal/config/controllers.yaml` + `hardware/arm_hal_gazebo.hpp`
- 验收：`scripts/verify_m1.sh` —— 关节轨迹 home → target → home，关节误差 ≤ 1e-3 rad

### M2 感知（2 天）
- 相机：`robot_perception/src/camera_node.cpp`（Gazebo RGB-D plugin）
- 检测：`robot_perception/src/unified_detector_node.cpp`（mock YOLO + YOLO-World 融合）
- 6D 位姿：mock CosyPose 节点 + `/perception/{device_id}/scene_delta`
- rosbag2：`scripts/record_m2.sh` → `data/rosbag2/m2_baseline/`
- 验收：`scripts/verify_m2.sh` —— 与人工标注差异 ≤ 阈值

### M3 决策闭环（2 天）
- `robot_decision`：`state_machine.cpp` 实现 11 阶段状态机 + 故障注入服务 `fault_injection`（仅 CI）
- `robot_gateway`：Action Server `PickPlace`
- 验收：`scripts/verify_m3.sh` —— PickPlace 闭环 + Gazebo 回放

### M4 Web Gateway + 边缘视角（2 天）
- `backend/gateway/tasks.py`：POST `/api/devices/{id}/tasks`，内部发 ROS2 Action；幂等 `task_id`。
- WS：`/ws/devices`、`/ws/edge/{id}`、`/ws/alerts`、`/ws/logs`
- 前端：`frontend/src/edge/{EdgeView,CameraOverlay,PointCloudOverlay,StageTimeline,SafetyPanel}.vue`
- `frontend/src/supervisor/{DbStatus,ManualOverride}.vue`
- `frontend/src/composables/taskWatcher.ts` 已存在，按 Phase 5 合约接入
- 验收：`scripts/verify_m4.sh` —— 提交任务 + UI 阶段进度 + 审计日志匹配

### M5 一键演示（1 天）
- `scripts/verify_m5.sh`：一键启动 Gazebo + bringup + decision + gateway + FastAPI + Vite + rosbag2 录制
- 录像：mp4 H.264 5 Mbps + 验收单 JSON
- 验收：CI nightly 自动跑，记录耗时与产出

---

## C. 验证脚本模板（请按 M0 → M5 复用）

```bash
#!/usr/bin/env bash
# scripts/verify_m0.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HERE"

source /opt/ros/${ROS_DISTRO:-humble}/setup.bash
[[ -f ros2_ws/install/setup.bash ]] && source ros2_ws/install/setup.bash

echo "[M0] launching empty world ..."
ros2 launch robot_bringup empty_world.launch.py &
LPID=$!
trap "kill $LPID 2>/dev/null || true" EXIT

sleep 8
ros2 topic list | grep -E '/clock|/tf|/joint_states' >/dev/null
echo "[M0] OK"
```

`scripts/verify_m5.sh` 示例结构：

```bash
#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HERE"

# 1. 启动 Gazebo + bringup + decision + gateway
ros2 launch robot_bringup full_system.launch.py &
LPID=$!
trap "kill $LPID 2>/dev/null || true" EXIT
sleep 15

# 2. 启动 rosbag2 录制
ros2 bag record -o data/rosbag2/m5_$(date +%Y%m%d_%H%M%S) \
  /camera/robot_01/color/image_raw \
  /perception/robot_01/poses \
  /robot/robot_01/state \
  /planning_scene_motion &
BPID=$!

# 3. 启动 FastAPI
( cd backend && uvicorn main:app --port 8000 ) &
FPID=$!

# 4. 启动前端
( cd frontend && npm run dev ) &
NPID=$!

# 5. 提交任务（10 次）
for i in 1 2 3 4 5 6 7 8 9 10; do
  curl -fsS -X POST http://localhost:8000/api/devices/robot_01/tasks \
    -H "Content-Type: application/json" \
    -d '{"task_id":"demo-'$i'","target":{...},"place":{...}}'
  sleep 90
done

# 6. 收尾
kill $NPID $FPID $BPID $LPID 2>/dev/null || true
echo "[M5] artifacts: data/rosbag2/, data/verify_artifacts/"
```

---

## D. 验收度量（CI 必须守住）

| 度量 | 阈值 | 测试入口 |
|------|------|---------|
| 闭环成功率 | ≥ 90%（10 次 ≥ 9 次） | `verify_m5.sh` 循环 |
| 动作最长周期 | ≤ 90 s | `verify_m3.sh` |
| 急停 → 停机 | ≤ 200 ms | `verify_m3.sh` + 故障注入 |
| WS 重连 UI 对齐 | ≤ 2 s | `verify_m4.sh` + 模拟断开 |
| 单元测试覆盖率 | ≥ 80% | `pytest --cov` |

---

## E. 不在 Phase 5 范围（明确划出）

- 修改 Phase 1–4 的 `backend/api/routes.py`、业务服务、模拟器、数据层。
- 修改现有 SQLite 表结构（`devices/tasks/trace_logs`）——Phase 5 仅新增表 `override_log`。
- 真机 EtherCAT 调试（仅 `arm_hal_ethercat` 占位 + 编译验证）。
- 多用户认证 / RBAC 完整实现（Phase 5 仅前端做角色切换 stub）。
- 部署脚本 / Helm / k8s。

---

## F. 提交与回滚约定

- 每个里程碑一个 PR，PR 名 `phase5/Mx: <一句话>`。
- 不要 `git push --force`；不要 `git rebase -i`。
- CI nightly 失败 → 先修 CI，不阻塞 PR；连续 3 天失败则停止 Phase 6 启动。
- `override_log` 一旦写入**永不删除**（业务审计需求）。

---

## G. 风险与回退开关（速记）

| 风险 | 启动参数开关 | 默认 |
|------|--------------|------|
| URDF/SRDF 不一致导致规划失败 | `disable_collision_objects:=true` | false |
| 感知误报 | `perception_gate_min_consistent_frames:=3` | 3 |
| `ros2_control` 差异 | `arm_hal_backend:=gazebo` | gazebo |
| WS 反压 | `ws_max_payload_kb:=64` | 64 |
| 录像带宽 | `record_bitrate_mbps:=5` | 5 |

---

## H. 下一位 Agent 的"开工模板"

把以下内容粘进 `.cursor/projects/.../phase5-session.md` 或自己项目的 todo：

```
- [ ] M0: ros2_ws + robot_bringup + 空世界启动
- [ ] M1: URDF/SRDF + MoveIt + ros2_control + arm_hal_gazebo
- [ ] M2: 相机 + 检测 + 6D 位姿 + PlanningScene + rosbag2
- [ ] M3: 11 阶段状态机 + PickPlace Action + 故障注入
- [ ] M4: backend/gateway + ws_devices/edge/alerts/logs + 边缘视角 + supervisor 面板
- [ ] M5: verify_m5.sh 一键全链 + 录像 + 验收单 + CI nightly
```
