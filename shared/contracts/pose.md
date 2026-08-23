# Pose / 坐标系契约

本文件定义 robot-logic 四个子工程（rcs / robot-app / vla-training / simulation）共享的
位姿（Pose）与坐标系约定。它**严格对齐** `robot-control-stack`（`rcs._core.common`）的语义，
由 `shared/python/robot_contracts/kinematics.py` 作为单一可执行来源实现，并由
`shared/contracts/pose.schema.json` 作为语言无关规范。

## 坐标系约定

- **世界系（world）**：右手系，x 向前、y 向左、z 向上。
- **基座系（robot）**：以机械臂基座/AGV 中心为原点的局部坐标系。
- **转换函数**（对标 RCS `MjORobot`）：
  - `to_pose_in_world_coordinates(world_from_base, base_from_point)`：基座系坐标 → 世界系坐标。
  - `to_pose_in_robot_coordinates(world_from_base, world_from_point)`：世界系坐标 → 基座系坐标。
  - 内部使用 SE(3) 复合 `Pose @ Pose` 与 `Pose.inverse()`。

## 四元数约定

- **内部存储**：`[x, y, z, w]`（xyzw），与 RCS 一致。
- **MuJoCo qpos**：`[w, x, y, z]`（wxyz），提供 `Pose.wxyz` 与 `Pose.from_wxyz()` 互转。
- **RPY**：内旋 XYZ（roll/pitch/yaw），提供 `Pose.from_rpy()` 与 `Pose.to_rpy()`。

## RobotType / GripperType

- RCS 标准臂：`FR3`、`Panda`、`UR5e`、`XArm7`、`SO100`、`SO101`、`Yam`。
- robot-logic 物流形态：`ARM`（通用六轴）、`AGV`、`STACKER`。
- 末端执行器：`FrankaHand`、`Robotiq2F85`、`Yam`、`LogisticsGripper`、`None`。

## 变更流程

位姿语义是跨子工程集成的根契约。修改 `kinematics.py` 必须：
1. 同步更新本文件与 `pose.schema.json`；
2. 提升 `robot_contracts.__version__`；
3. 运行 `tests/test_kinematics.py` 确认转换正确性。
