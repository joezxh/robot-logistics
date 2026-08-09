# Phase 5 M3 (Gazebo + MoveIt) — Progress Report

> **Date**: 2026-07-24
> **Scope**: Phase 5 M1 of `docs/superpowers/specs/2026-07-23-robot-logic-phase5-design.md` (the Gazebo + MoveIt bring-up planned inside the Phase 5 spec, which the user colloquially refers to as "M3").
> **Status**: ✅ End-to-end smoke test passes on `USE_GAZEBO=false` (mock backend). Gazebo Harmonic path is wired but not yet exercised in this session.

---

## 1. What works today

A `scripts/verify_m3.sh` run (with `USE_GAZEBO=false`) performs the following on a fresh WSL Ubuntu 24.04 + ROS2 Jazzy environment:

1. Static checks for all 12 required artifacts (URDF, xacro hardware, SRDF, controller YAMLs, OMPL YAML, kinematics YAML, joint-limits YAML, RViz config, Gazebo world, launch files).
2. Build the `ros2_ws` via `colcon build`.
3. Launch `ros2 launch robot_bringup arm.launch.py use_gazebo:=false use_sim_time:=false`, which spins up:
   - `robot_state_publisher` with the URDF.
   - `ros2_control_node` with `mock_components/GenericSystem` (the M1 dry-run backend).
   - `joint_state_broadcaster`, `arm_controller` (JointTrajectoryController), `gripper_controller` (JointGroupPositionController).
4. Wait for `/controller_manager/list_controllers` to appear and for all 3 controllers to reach `active` state.
5. Launch `ros2 launch robot_moveit_config move_group.launch.py` and wait for `/plan_kinematic_path`.
6. Send a `MotionPlanRequest` via a Python client: goal = "ready" configuration, start_state = "home" configuration.
7. Call `/plan_kinematic_path` with a `WorkspaceParameters` cube of 1.5 m around `base_link`.
8. Verify the response — `MotionPlanResponse.error_code == 1` (SUCCESS) and at least 5 waypoints.
9. Send the resulting `JointTrajectory` to `/arm_controller/follow_joint_trajectory` and wait for the action result with `error_code == 0`.
10. Print the green "live OK" banner.

The exit code is 0 and the final log line is `[M3] live OK - use_gazebo=false + 3 controllers + MoveIt plan/execute`.

---

## 2. What was fixed along the way

The biggest learning is that ROS2 MoveIt + OMPL has many small YAML / launch / SRDF / hardware-interface traps. The fixes are listed below, in roughly the order they were needed.

### 2.1 Hardware interface selection

`arm_hal.ros2_control.xacro` now branches on a `use_gazebo` xacro argument:

```xml
<xacro:if value="${use_gazebo}">
  <hardware>
    <plugin>gz_ros2_control/GzSystem</plugin>
  </hardware>
</xacro:if>
<xacro:unless value="${use_gazebo}">
  <hardware>
    <plugin>mock_components/GenericSystem</plugin>
    <param name="mock_sensor_commands">true</param>
  </hardware>
</xacro:unless>
```

Mirrored in `robot.urdf.xacro` with a `use_gazebo` xacro argument and a `<gazebo>` plugin block that wires `gz_ros2_control-system`.

### 2.2 Mock vs. Gazebo control manager

When `use_gazebo=true`, the controller manager is owned by `gz_sim` (via `gz_ros2_control`). The standalone `ros2_control_node` must NOT be launched in that mode. The launch file now uses `launch_conditions`:

```python
control_node = Node(
    package="controller_manager",
    executable="ros2_control_node",
    ...,
    condition=launch_conditions.UnlessCondition(use_gazebo),
)
```

### 2.3 ROS2 parameter YAML wrapping

MoveIt-loadable YAML files (kinematics, joint_limits, OMPL) must be wrapped under `/**: ros__parameters:`. The relevant files are:

- `robot_moveit_config/config/kinematics.yaml`
- `robot_moveit_config/config/joint_limits.yaml`
- `robot_moveit_config/config/ompl_planning.yaml`

`move_group.launch.py` loads them with `yaml.safe_load` and extracts the inner map explicitly (no `os.path.join` magic at runtime).

### 2.4 OMPL planner_configs as a map

`ompl_planning.yaml` originally had `planner_configs` as a list of dicts. MoveIt expects a map keyed by planner name. The fix is documented in the file:

```yaml
ompl:
  planner_configs:
    RRTConnectConfigDefault:
      type: geometric::RRTConnect
      ...
    RRTstarkConfigDefault:
      type: geometric::RRTstar
      ...
    AnytimeConfigDefault:
      type: geometric::AnytimePathShortening
      ...
```

### 2.5 Mimic joints and command interfaces

`gripper_right` is a mimic joint of `gripper_left` in the URDF. ROS2 control rejects mimic joints with command interfaces:

> `Joint 'gripper_right' has mimic attribute not set to false: Activated mimic joints cannot have command interfaces.`

`arm_hal.ros2_control.xacro` therefore defines only `gripper_left` as a controllable joint; `gripper_right` is left for `ros2_control` to mirror automatically.

### 2.6 Self-collision at the home configuration

The biggest runtime bug: OMPL refused to initialise its start tree at the home configuration, even though home-to-home is a trivial plan. The URDF uses cylinder primitives for link collisions, and the cylinder-vs-cylinder FCL check produces false positives at folded configurations. The fix is in `robot.srdf`:

```xml
<!-- 9 adjacent link pairs -->
<disable_collisions link1="base_link" link2="shoulder_link" reason="adjacent"/>
...
<!-- 19 cross-link pairs that never touch -->
<disable_collisions link1="upper_arm_link" link2="wrist_1_link" reason="never"/>
...
```

With these disables, the home pose is valid and OMPL finds a path on the first attempt.

### 2.7 Trajectory timestamp spacing

MoveIt sometimes emits trajectories where two consecutive points share the same `time_from_start`. The `joint_trajectory_controller` rejects them with:

> `Time between points 0 and 1 is not strictly increasing`

The verify script enforces a minimum spacing of 0.05 s between waypoints before submitting to the action server. This is a client-side workaround; it does not affect real move_group planning; the JTC server side will be patched in a follow-up.

### 2.8 Workspace parameters

OMPL requires the planning volume to be specified, otherwise it fails with `Motion planning start tree could not be initialized`. The verify script sends a `WorkspaceParameters` cube of 1.5 m around `base_link` on every plan request.

---

## 3. What is still pending

| # | Item | Notes |
|---|------|-------|
| 1 | **Gazebo live smoke test** | `USE_GAZEBO=true` would launch `gz_sim` headlessly, spawn the robot, and run the same plan. Not yet exercised in this session; the launch plumbing is in place but gz_physics round-trips need a separate run. |
| 2 | **Trajectory spacing on the server side** | Either configure `moveit_ros_planning` `post_processing` adapters (e.g. add a `FixWorkspaceBounds` + `FixStartStateBounds` adapter) or relax `allowed_goal_duration_margin` so the JTC accepts single-spacing plans. The client-side workaround is fine for the smoke test but not for production. |
| 3 | **JointTrajectory spaced start positions** | The verify script supplies explicit start and goal joint states; in practice the controller should just read them from `/joint_states`. The move_group already listens to `/joint_states`; the explicit start is only needed because the smoke test runs against the mock backend, which publishes once on activation. |
| 4 | **PickPlace action** (Phase 5 spec M3 proper) | The state-machine + PickPlace closed-loop is the *other* "M3" in the spec. It is out of scope for this bring-up; not started. |
| 5 | **Perception + point-cloud publishing** | No Gazebo RGB-D sensor is spawned yet; the world is just the ground plane. |
| 6 | **Decision-state machine** | `robot_decision` package exists but is not yet wired into the move_group call site. |
| 7 | **FastAPI gateway + WS** | `backend/gateway/` is the planned home; the `robot_gateway` ROS2 package is the bridge stub. End-to-end coupling not yet built. |

---

## 4. Repository layout (final)

```
ros2_ws/src/
├── robot_bringup/
│   ├── launch/
│   │   ├── arm.launch.py           # Unified bring-up (mock or Gazebo)
│   │   └── empty_world.launch.py   # M0 stub
│   ├── urdf/
│   │   └── robot.urdf.xacro        # 6-DOF arm + gripper + use_gazebo arg
│   ├── worlds/
│   │   └── empty.sdf               # Gazebo Harmonic world
│   └── setup.py
├── robot_arm_hal/
│   ├── urdf/
│   │   └── arm_hal.ros2_control.xacro  # GenericSystem OR GzSystem
│   ├── robot_arm_hal/stub.py       # M1: publishes /joint_states
│   └── setup.py
├── robot_moveit_config/
│   ├── config/
│   │   ├── robot.srdf              # planning groups + disable_collisions
│   │   ├── ros2_controllers.yaml   # JTC + JointGroupPositionController
│   │   ├── ompl_planning.yaml      # RRTConnect / RRTstar / Anytime
│   │   ├── kinematics.yaml         # KDL
│   │   ├── joint_limits.yaml       # robot_description_planning
│   │   └── moveit.rviz             # visualisation
│   └── launch/
│       ├── move_group.launch.py    # move_group node + all configs
│       └── planning_context.launch.py  # standalone helper (RSP)
└── robot_msgs/                     # placeholder package

scripts/
├── verify_m0.sh                    # earlier milestone
├── verify_m1.sh                    # earlier milestone
├── verify_m3.sh                    # this milestone
├── install_m3_deps.sh              # apt-get install ros-jazzy-{ros-gz,gz-ros2-control,rviz2,moveit}
└── check_gz_moveit.sh              # diagnostic for what's installed
```

---

## 5. How to run

### 5.1 Once-off dependency install

```bash
bash scripts/install_m3_deps.sh
```

This installs `ros-jazzy-ros-gz`, `ros-jazzy-ros-gz-sim`, `ros-jazzy-ros-gz-bridge`, `ros-jazzy-gz-ros2-control`, `ros-jazzy-rviz2`, `ros-jazzy-moveit`, plus the planner / kinematics packages.

### 5.2 Mock-backend smoke test (works today)

```bash
USE_GAZEBO=false bash scripts/verify_m3.sh
```

Expected tail:

```
[M3] all required controllers active
[M3] launching move_group.launch.py...
[M3] move_group up
[M3] planning home -> ready via /plan_kinematic_path...
[M3] plan SUCCESS: 8 waypoints, 6 joints
[M3] execute goal: reached!
[M3] MoveIt + trajectory PASSED
[M3] live OK - use_gazebo=false + 3 controllers + MoveIt plan/execute
```

### 5.3 Gazebo live smoke test (planned)

```bash
USE_GAZEBO=true bash scripts/verify_m3.sh
```

Will run the same plan inside `gz_sim`. The launch plumbing is wired; the smoke test will be run end-to-end in a follow-up session.

### 5.4 Manual bring-up

```bash
# Gazebo
ros2 launch robot_bringup arm.launch.py use_gazebo:=true

# In another shell
ros2 launch robot_moveit_config move_group.launch.py

# Visualisation
ros2 launch robot_moveit_config move_group.launch.py &
rviz2 -d $(ros2 pkg prefix robot_moveit_config)/share/robot_moveit_config/config/moveit.rviz

# From Python:
ros2 run robot_arm_hal arm_hal_stub_node  # only needed for the mock backend
```

---

## 6. Open questions for the next iteration

1. Should the trajectory-spacing fix live on the server side (a `FixStartStateBounds` + `FixWorkspaceBounds` MoveIt request adapter) or on the client side (the verify script)? Production users will hit this too.
2. Should the SRDF's `disable_collisions` table be regenerated with the MoveIt Setup Assistant? The current set is hand-curated and works for the cylinder collisions of our URDF; if the URDF gains convex meshes, some disables may need to be removed.
3. Where does the `PickPlace` state machine live? `robot_decision` is the existing package; the skill spec mentions SMACH or FlexBE. The bring-up so far has not picked one.
4. Do we want to keep the `mock_components/GenericSystem` backend for CI runs without a display, or drop it now that `USE_GAZEBO=true` is the long-term target? Mock gives us fast unit-style tests; Gazebo gives us physics.
