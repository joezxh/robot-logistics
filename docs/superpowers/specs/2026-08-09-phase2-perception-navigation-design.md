# Phase 2: 感知与导航 — 设计规格书

- **日期**: 2026-08-09
- **状态**: 已确认
- **前置**: Phase 1 双臂 AGV 装卸机器人已完成（237 tests pass）
- **预计工期**: 3-4 周

---

## 1. 范围

**在范围内**：
- 仿真后端合成传感器数据（点云 + 激光扫描 + ground truth）
- `robot_perception` 完整点云处理管线（PCL）
- `BaseExecutor` 重构为 Nav2 NavigateToPose action client
- Nav2 配置与集成
- 前端感知可视化（检测框 + 导航路径 + costmap）
- 新增 SSE 端点（detections / nav_path）

**不在范围内**（Phase 3+）：
- 真实深度相机驱动
- VLA 推理接入
- 真实硬件 HAL

---

## 2. 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Simulation Backend (FastAPI)                       │
│                                                                       │
│  ┌──────────────────┐    ┌──────────────────┐                        │
│  │ PointCloudGen     │    │ LaserScanGen      │                       │
│  │ (合成货箱点云)    │    │ (合成激光扫描)    │                       │
│  └────────┬─────────┘    └────────┬─────────┘                        │
│           │ MQTT                    │ MQTT                            │
│           │ sim/{id}/point_cloud    │ sim/{id}/scan                   │
│           └───────────┬─────────────┘                                │
└───────────────────────┼──────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    MQTT Broker                                         │
│                                                                       │
│  sim/{id}/point_cloud ──► gateway ──► /camera/depth/points           │
│  sim/{id}/scan ─────────► gateway ──► /scan                           │
│  rcs/{id}/command ──────► gateway ──► ~/motion_command                │
│  rcs/{id}/state ◄───────gateway ◄── /detections, /nav_path           │
└──────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    robot-app (ROS 2)                                   │
│                                                                       │
│  robot_gateway          robot_perception          robot_decision       │
│  ┌──────────────┐      ┌───────────────────┐    ┌─────────────────┐  │
│  │ MQTT→ROS2    │      │ PointCloudPipeline │    │ TaskCoordinator │  │
│  │              │      │  PassThrough       │    │                 │  │
│  │ /scan ───────┼──────┤  VoxelGrid         │    │ BaseExecutor    │  │
│  │ /camera/     │      │  StatisticalOutlier│    │  → Nav2 Action  │  │
│  │  depth/      │      │  RANSAC Segment    │    │    Client       │  │
│  │  points      │      │  EuclideanCluster  │    │                 │  │
│  │              │      │  BBox + Pose       │    │ ArmExecutor     │  │
│  │ /detections  │      │  → Detection3DArray│    │ HugController   │  │
│  │  (out)       │      └───────────────────┘    │ SafetyMonitor   │  │
│  └──────────────┘                                └─────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    Simulation Frontend (Vue 3 + Three.js)              │
│                                                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────────┐   │
│  │ DetectionOverlay │  │ NavPathOverlay   │  │ CostmapOverlay     │   │
│  │ (3D bbox 线框)  │  │ (规划轨迹线)     │  │ (安全区域边界)     │   │
│  └─────────────────┘  └─────────────────┘  └────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

**关键数据通路**：
- **感知**：合成点云 → MQTT → gateway → `/camera/depth/points` → robot_perception → `Detection3DArray` → gateway → MQTT → SSE → 前端
- **导航**：TaskCoordinator → BaseExecutor → Nav2 `NavigateToPose.action` → `/cmd_vel` → gateway → MQTT → simulation
- **可视化**：检测结果 + 导航路径 → gateway → MQTT → simulation → SSE → Three.js overlay

---

## 3. 仿真后端 — 合成传感器

### 3.1 PointCloudGenerator

**文件**: `simulation/backend/algorithm/simulator/point_cloud_gen.py`

**职责**: 根据仓库场景中货箱位置生成合成点云数据。

**参数**:
| 参数 | 默认值 | 说明 |
|------|--------|------|
| resolution | 0.01m | 点云分辨率 |
| noise_std | 0.005m | 高斯噪声标准差 |
| fov_h | 60° | 水平视场角 |
| fov_v | 45° | 垂直视场角 |
| max_range | 5.0m | 最大探测距离 |
| publish_rate | 10Hz | 发布频率 |

**输出格式**: JSON via MQTT
```json
{
  "frame_id": "camera_link",
  "timestamp": 1723190400.0,
  "points": [[x, y, z], ...],
  "ground_truth": [
    {"id": "box-01", "position": [x, y, z], "size": [sx, sy, sz]}
  ]
}
```

**MQTT Topic**: `sim/{device_id}/point_cloud`

### 3.2 LaserScanGenerator

**文件**: `simulation/backend/algorithm/simulator/laser_scan_gen.py`

**职责**: 根据设备位置和仓库障碍物生成合成激光扫描数据。

**参数**:
| 参数 | 默认值 | 说明 |
|------|--------|------|
| angle_min | -π/2 | 最小扫描角 |
| angle_max | π/2 | 最大扫描角 |
| angle_increment | 0.01rad | 角度分辨率 |
| range_min | 0.1m | 最小探测距离 |
| range_max | 10.0m | 最大探测距离 |
| publish_rate | 10Hz | 发布频率 |

**输出格式**: JSON via MQTT
```json
{
  "frame_id": "base_laser_link",
  "angle_min": -1.5708,
  "angle_max": 1.5708,
  "angle_increment": 0.01,
  "ranges": [2.5, 2.6, ...],
  "intensities": [100, 95, ...]
}
```

**MQTT Topic**: `sim/{device_id}/scan`

### 3.3 Runtime 集成

`simulation/backend/services/runtime.py` 变更：
- 在 `__init__` 中为每个设备创建 PointCloudGenerator 和 LaserScanGenerator
- 在 `tick()` 中调用生成器，通过 mqtt_bridge 发布

---

## 4. robot_perception — 点云处理管线

### 4.1 PointCloudProcessorNode

**文件**: `robot-app/ros2_ws/src/robot_perception/robot_perception/point_cloud_processor.py`

**订阅**: `/camera/depth/points` (`sensor_msgs/PointCloud2`)

**发布**: `/detections` (`vision_msgs/Detection3DArray`)

**处理管线**:

```
PointCloud2
    │
    ▼
[1] PassThrough filter          z: [0.1, 2.0]m — 去除地面/天花板
    │
    ▼
[2] VoxelGrid downsample        leaf_size: 0.01m
    │
    ▼
[3] StatisticalOutlier removal  mean_k=50, std_thresh=1.0
    │
    ▼
[4] RANSAC plane segmentation   distance_threshold=0.01m
    │                           去除最大平面（地面/桌面）
    ▼
[5] EuclideanCluster extraction cluster_tolerance=0.02m
    │                           min_cluster_size=100
    │                           max_cluster_size=25000
    ▼
[6] BoundingBox fitting         每个 cluster → 3D bbox
    │                           (中心 + 尺寸 + 方向)
    ▼
[7] Pose estimation             bbox 中心 = 位置
    │                           主方向 = 朝向
    ▼
Detection3DArray
```

**参数**（`config/point_cloud_processor.yaml`）:
```yaml
point_cloud_processor:
  ros__parameters:
    passthrough_z_min: 0.1
    passthrough_z_max: 2.0
    voxel_leaf_size: 0.01
    sor_mean_k: 50
    sor_std_thresh: 1.0
    ransac_distance_threshold: 0.01
    cluster_tolerance: 0.02
    min_cluster_size: 100
    max_cluster_size: 25000
    min_detection_confidence: 0.3
```

### 4.2 消息类型

**输出**: `vision_msgs/Detection3DArray`

每个 `Detection3D`:
```python
{
    "id": "cluster_0",
    "bbox": {
        "center": {"position": {"x": 0.5, "y": 0.3, "z": 0.8}},
        "size": {"x": 0.3, "y": 0.2, "z": 0.15}
    },
    "results": [{"hypothesis": {"class_id": "box", "score": 0.85}}]
}
```

### 4.3 性能目标

| 指标 | 目标 |
|------|------|
| 单帧处理时间 | < 50ms |
| 检测精度（与 ground truth） | 位置误差 < 0.05m |
| 虚警率 | < 5% |

---

## 5. Nav2 导航集成

### 5.1 BaseExecutor 重构

**文件**: `robot-app/ros2_ws/src/robot_decision/robot_decision/base_executor.py`

**当前实现**（Phase 1 占位）:
```python
class BaseExecutor:
    def follow_waypoint(self, x, y, yaw): ...  # P-controller 占位
    def get_cmd_vel(self): ...                  # 返回 (0, 0)
```

**Phase 2 重构**:
```python
class BaseExecutor:
    """Nav2 NavigateToPose action client wrapper."""
    
    def __init__(self, node: rclpy.node.Node) -> None:
        self._node = node
        self._nav_client = None  # ActionClient for NavigateToPose
        self._state = BaseState.IDLE
        self._current_goal = None
    
    def setup(self) -> None:
        """Initialize Nav2 action client (called from node __init__)."""
        from nav2_msgs.action import NavigateToPose
        self._nav_client = ActionClient(
            self._node, NavigateToPose, 'navigate_to_pose'
        )
    
    def follow_waypoint(self, x: float, y: float, yaw: float) -> None:
        """Send NavigateToPose goal to Nav2."""
        from geometry_msgs.msg import PoseStamped
        goal = PoseStamped()
        goal.header.frame_id = 'map'
        goal.header.stamp = self._node.get_clock().now().to_msg()
        goal.pose.position.x = x
        goal.pose.position.y = y
        # quaternion from yaw
        goal.pose.orientation.z = math.sin(yaw / 2)
        goal.pose.orientation.w = math.cos(yaw / 2)
        
        self._nav_client.send_goal_async(goal)
        self._state = BaseState.FOLLOWING
    
    def cancel(self) -> None:
        """Cancel current navigation goal."""
        if self._current_goal:
            self._current_goal.cancel_goal_async()
        self._state = BaseState.STOPPED
    
    def stop(self) -> None:
        self.cancel()
    
    def on_feedback(self, feedback):
        """Nav2 feedback callback."""
        # Update position from feedback
        pass
    
    def on_result(self, result):
        """Nav2 result callback — advance coordinator phase."""
        self._state = BaseState.IDLE
```

### 5.2 Nav2 参数

**文件**: `robot-app/ros2_ws/src/robot_decision/config/nav2_params.yaml`

```yaml
navigate_to_pose:
  ros__parameters:
    use_sim_time: false

bt_navigator:
  ros__parameters:
    default_bt_xml_filename: "navigate_w_replanning_time.xml"
    plugin_lib_names:
      - nav2_compute_path_to_pose_action_bt_node
      - nav2_follow_path_action_bt_node
      - nav2_goal_reached_condition_bt_node
      - nav2_goal_updated_condition_bt_node
      - nav2_recovery_node_bt_node

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: false
      rolling_window: false
      width: 20
      height: 20
      resolution: 0.05
      plugins: [static_layer, obstacle_layer, inflation_layer]
      obstacle_layer:
        enabled: true
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          obstacle_max_range: 10.0
          obstacle_min_range: 0.1
      inflation_layer:
        inflation_radius: 0.5
        cost_scaling_factor: 5.0

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: false
      rolling_window: true
      width: 3
      height: 3
      resolution: 0.05
      plugins: [obstacle_layer, inflation_layer]

controller_server:
  ros__parameters:
    controller_plugins: [FollowPath]
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      max_vel_x: 0.5
      min_vel_x: -0.1
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.5

recovery_server:
  ros__parameters:
    recovery_plugins: [spin, backup, wait]
    spin:
      plugin: "nav2_recoveries::Spin"
    backup:
      plugin: "nav2_recoveries::BackUp"
    wait:
      plugin: "nav2_recoveries::Wait"
```

### 5.3 与 SafetyMonitor 集成

```
TaskCoordinator → BaseExecutor.follow_waypoint()
                        │
                        ▼
                   Nav2 NavigateToPose
                        │
                        ├── /cmd_vel ──► SafetyMonitor.intercept_cmd_vel()
                        │                    │
                        │                    ├── SAFE → pass through
                        │                    ├── SLOWDOWN → scale velocity
                        │                    └── EMERGENCY → zero velocity
                        │
                        └── Nav2 cancel on estop
```

---

## 6. 前端感知可视化

### 6.1 DetectionOverlay

**文件**: `simulation/frontend/src/three/DetectionOverlay.ts`

**职责**: 渲染 3D bbox 线框叠加在仓库场景中。

```typescript
import * as THREE from 'three';

export interface Detection3D {
  id: string;
  position: { x: number; y: number; z: number };
  size: { x: number; y: number; z: number };
  confidence: number;
}

export class DetectionOverlay {
  private group = new THREE.Group();
  private boxes: THREE.LineSegments[] = [];

  get sceneObject(): THREE.Group {
    return this.group;
  }

  update(detections: Detection3D[]): void {
    this.clear();
    for (const det of detections) {
      const geo = new THREE.BoxGeometry(det.size.x, det.size.y, det.size.z);
      const edges = new THREE.EdgesGeometry(geo);
      const color = det.confidence > 0.7 ? 0x00ff00 : 0xffff00;
      const mat = new THREE.LineBasicMaterial({
        color,
        opacity: 0.6,
        transparent: true,
      });
      const line = new THREE.LineSegments(edges, mat);
      line.position.set(det.position.x, det.position.y, det.position.z);
      this.boxes.push(line);
      this.group.add(line);
    }
  }

  clear(): void {
    for (const box of this.boxes) {
      box.geometry.dispose();
      (box.material as THREE.Material).dispose();
      this.group.remove(box);
    }
    this.boxes = [];
  }
}
```

### 6.2 NavPathOverlay

**文件**: `simulation/frontend/src/three/NavPathOverlay.ts`

**职责**: 渲染规划导航路径。

```typescript
export class NavPathOverlay {
  private line: THREE.Line | null = null;
  private group = new THREE.Group();

  get sceneObject(): THREE.Group {
    return this.group;
  }

  update(path: { x: number; y: number; z: number }[]): void {
    this.clear();
    if (path.length < 2) return;
    const points = path.map(p => new THREE.Vector3(p.x, p.y, p.z));
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({
      color: 0x00aaff,
      linewidth: 2,
      opacity: 0.8,
      transparent: true,
    });
    this.line = new THREE.Line(geometry, material);
    this.group.add(this.line);
  }

  clear(): void {
    if (this.line) {
      this.line.geometry.dispose();
      (this.line.material as THREE.Material).dispose();
      this.group.remove(this.line);
      this.line = null;
    }
  }
}
```

### 6.3 CostmapOverlay

**文件**: `simulation/frontend/src/three/CostmapOverlay.ts`

**职责**: 渲染 costmap 热力图（安全区域边界）。

```typescript
export class CostmapOverlay {
  private mesh: THREE.Mesh | null = null;
  private group = new THREE.Group();

  get sceneObject(): THREE.Group {
    return this.group;
  }

  update(costmap: { data: number[]; width: number; height: number; resolution: number }): void {
    this.clear();
    const geometry = new THREE.PlaneGeometry(
      costmap.width * costmap.resolution,
      costmap.height * costmap.resolution,
      costmap.width - 1,
      costmap.height - 1
    );
    // Color vertices by cost value
    const colors = new Float32Array(costmap.data.length * 3);
    for (let i = 0; i < costmap.data.length; i++) {
      const cost = costmap.data[i] / 255;
      colors[i * 3] = cost;       // R
      colors[i * 3 + 1] = 0;      // G
      colors[i * 3 + 2] = 1 - cost; // B
    }
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    const material = new THREE.MeshBasicMaterial({
      vertexColors: true,
      opacity: 0.3,
      transparent: true,
      side: THREE.DoubleSide,
    });
    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.rotation.x = -Math.PI / 2;
    this.group.add(this.mesh);
  }

  clear(): void {
    if (this.mesh) {
      this.mesh.geometry.dispose();
      (this.mesh.material as THREE.Material).dispose();
      this.group.remove(this.mesh);
      this.mesh = null;
    }
  }
}
```

### 6.4 SSE 端点

**新增**:

| 端点 | 数据 | 频率 |
|------|------|------|
| `GET /api/devices/{device_id}/detections` | 检测结果 JSON | 10Hz |
| `GET /api/devices/{device_id}/nav_path` | 导航路径 JSON | 1Hz |

**WarehouseScene.vue 变更**:
- 新增 `DetectionOverlay`、`NavPathOverlay`、`CostmapOverlay` import
- 新增 SSE 订阅 `loader-01` 的 detections 和 nav_path
- `animate()` 中更新 overlay 位置

---

## 7. 测试策略

| 层级 | 测试内容 | 工具 | 预期数量 |
|------|---------|------|---------|
| L1 单元 | PointCloudGenerator 合成数据正确性 | pytest | ~10 |
| L1 单元 | LaserScanGenerator 射线计算 | pytest | ~8 |
| L1 单元 | Nav2 action client mock | pytest + mock | ~6 |
| L1 单元 | BaseExecutor 重构后行为 | pytest | ~8 |
| L1 单元 | 前端 overlay 数据解析 | vitest | ~5 |
| L2 集成 | 合成点云 → MQTT → gateway → ROS 2 topic | pytest | ~5 |
| L2 集成 | Nav2 goal → cmd_vel → MQTT → simulation | pytest | ~5 |
| L3 端到端 | 完整感知→导航→可视化链路 | docker-compose | 手动 |

**预期总测试数**: 237（当前） + ~47 = ~284

---

## 8. 新增/改动文件清单

### 新增

| 文件 | 说明 |
|------|------|
| `simulation/backend/algorithm/simulator/point_cloud_gen.py` | 合成点云生成器 |
| `simulation/backend/algorithm/simulator/laser_scan_gen.py` | 合成激光扫描生成器 |
| `simulation/backend/tests/test_point_cloud_gen.py` | 点云生成测试 |
| `simulation/backend/tests/test_laser_scan_gen.py` | 激光扫描测试 |
| `robot-app/.../robot_perception/robot_perception/point_cloud_processor.py` | 点云处理节点 |
| `robot-app/.../robot_perception/config/point_cloud_processor.yaml` | 感知参数 |
| `robot-app/.../robot_perception/tests/test_point_cloud_processor.py` | 感知测试 |
| `robot-app/.../robot_decision/config/nav2_params.yaml` | Nav2 参数 |
| `robot-app/.../robot_decision/tests/test_base_executor_nav2.py` | Nav2 集成测试 |
| `simulation/frontend/src/three/DetectionOverlay.ts` | 检测框叠加 |
| `simulation/frontend/src/three/NavPathOverlay.ts` | 导航路径叠加 |
| `simulation/frontend/src/three/CostmapOverlay.ts` | costmap 叠加 |

### 改动

| 文件 | 变更 |
|------|------|
| `simulation/backend/services/runtime.py` | 注册 PointCloud/LaserScan 生成器 |
| `simulation/backend/services/mqtt_bridge.py` | 发布点云/扫描到 MQTT |
| `simulation/backend/main.py` | 新增 detections/nav_path SSE 端点 |
| `robot-app/.../robot_decision/robot_decision/base_executor.py` | 重构为 Nav2 action client |
| `robot-app/.../robot_decision/robot_decision/task_coordinator_node.py` | Nav2 生命周期管理 |
| `robot-app/.../robot_perception/setup.py` | 添加 entry_points |
| `simulation/frontend/src/three/WarehouseScene.vue` | 集成 overlay 组件 |

---

## 9. 风险

| 风险 | 缓解 |
|------|------|
| PCL 在 Windows 上安装困难 | 提供 Docker 开发环境；备选 open3d |
| Nav2 引入大量 ROS 2 依赖 | 使用 `nav2_bringup` 标准配置；BaseExecutor 接口保持纯 Python 可测 |
| 合成点云与真实点云差异大 | 参数可调；ground truth 用于精度评估 |
| 前端 overlay 性能 | 限制最大检测数（100）；LOD 降级 |
| SSE 端点增多 | 合并为单一 `/api/devices/{id}/perception` 端点（可选） |

---

## 10. 里程碑

| 周 | 交付物 | 验证标准 |
|----|--------|---------|
| W1 | 合成传感器 + MQTT 发布 | 点云/扫描数据可通过 MQTT 接收 |
| W2 | robot_perception 点云管线 | Detection3DArray 发布，精度 < 0.05m |
| W3 | Nav2 集成 + BaseExecutor 重构 | NavigateToPose goal 可达 |
| W4 | 前端可视化 + 集成测试 | overlay 实时渲染，~284 tests pass |
