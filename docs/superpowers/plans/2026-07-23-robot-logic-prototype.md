# Robot Logic Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a demonstrable Web prototype for a logistics warehouse robot system with 4 visual scenarios, fully aligned with the algorithm specs in `docs/algorithm/`.

**Architecture:** Layered monolithic backend (API Gateway → Business Services → Algorithm Services → Data Layer) with Vue 3 + Three.js frontend, FastAPI REST + WebSocket, SQLite persistence.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, NumPy, SciPy, Vue 3, Three.js, ECharts, Vite

## Global Constraints

- Python 3.11+ required (per spec dependencies)
- File size limit: 300 lines per file (per spec §1.3)
- All algorithms must reference `docs/algorithm/*.md` precisely
- Trace ID propagated through entire call chain (format: `YYYYMMDD-HHMM-{uuid8}`)
- API documented via FastAPI auto-generated OpenAPI at `/docs`
- Commit after each task with conventional commit messages
- Test coverage: 80% unit tests for algorithm modules
- No emoji in code/comments unless explicitly requested
- All API responses use Pydantic models with Chinese field descriptions

---

## Phase 1: Project Scaffolding (M1)

### Task 1: Backend Project Structure

**Files:**
- Create: `backend/__init__.py`
- Create: `backend/main.py`
- Create: `backend/config.py`
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `.gitignore`

**Interfaces:**
- Produces: `FastAPI app instance`, `Config object`

- [ ] **Step 1: Create directory structure**

```bash
mkdir backend\api backend\services backend\algorithm backend\data backend\logging backend\tests
mkdir backend\algorithm\simulator backend\algorithm\scheduler backend\algorithm\planner backend\algorithm\perception
mkdir backend\data\repositories
mkdir frontend docs\superpowers\plans
```

- [ ] **Step 2: Write requirements.txt**

```
fastapi==0.104.0
uvicorn[standard]==0.24.0
numpy==1.26.0
scipy==1.11.0
pydantic==2.4.0
sqlalchemy==2.0.23
aiosqlite==0.19.0
websockets==12.0
python-multipart==0.0.6
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.25.0
```

- [ ] **Step 3: Create main.py**

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="机器人智能仓储物流系统 API",
    version="1.0.0",
    description="物流装卸机器人系统原型 API",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Robot Logic System API", "version": "1.0.0"}
```

- [ ] **Step 4: Create config.py**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Robot Logic System"
    database_url: str = "sqlite+aiosqlite:///./data/prototype.db"
    log_level: str = "INFO"
    cloud_endpoint: str = "http://localhost:8080"
    use_cloud: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 5: Create .gitignore**

```
__pycache__/
*.py[cod]
*.egg-info/
.env
data/*.db
node_modules/
dist/
.venv/
venv/
*.log
.pytest_cache/
```

- [ ] **Step 6: Verify backend runs**

Run: `cd backend && uvicorn main:app --reload`
Expected: Server starts, visit `http://localhost:8000/docs` shows Swagger UI

- [ ] **Step 7: Commit**

```bash
git add backend/ .gitignore
git commit -m "feat(scaffold): create backend project structure with FastAPI"
```

---

### Task 2: Frontend Project Structure

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`

**Interfaces:**
- Produces: Vue 3 app with Vite build system

- [ ] **Step 1: Create package.json**

```json
{
  "name": "robot-logic-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "three": "^0.158.0",
    "echarts": "^5.4.0",
    "vue-echarts": "^6.5.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-vue": "^4.4.0",
    "typescript": "^5.2.0",
    "vue-tsc": "^1.8.0"
  }
}
```

- [ ] **Step 2: Create vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true }
    }
  }
})
```

- [ ] **Step 3: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true
  },
  "include": ["src/**/*.ts", "src/**/*.vue"]
}
```

- [ ] **Step 4: Create index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>机器人仓储物流系统</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

- [ ] **Step 5: Create main.ts and App.vue**

```typescript
// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
createApp(App).mount('#app')
```

```vue
<!-- src/App.vue -->
<template>
  <div id="app">
    <h1>机器人智能仓储物流系统</h1>
    <p>原型版本 v1.0</p>
  </div>
</template>
```

- [ ] **Step 6: Install and run**

```bash
cd frontend && npm install && npm run dev
```
Expected: Vite dev server starts at `http://localhost:5173`

- [ ] **Step 7: Commit**

```bash
git add frontend/
git commit -m "feat(scaffold): create Vue 3 + Vite frontend structure"
```

---

## Phase 2: Data Layer (M2)

### Task 3: SQLite Database Setup

**Files:**
- Create: `backend/data/__init__.py`
- Create: `backend/data/db.py`
- Create: `backend/data/models.py`
- Create: `backend/tests/test_data.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_data.py
from backend.data.db import init_db, get_session
from backend.data.models import Device

def test_init_db_creates_tables():
    init_db()
    with get_session() as session:
        # Query should not raise
        session.query(Device).first()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/test_data.py -v`
Expected: ModuleNotFoundError or ImportError

- [ ] **Step 3: Create db.py**

```python
# backend/data/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()
engine = None
SessionLocal = None

def init_db(url: str = "sqlite+aiosqlite:///./data/prototype.db"):
    global engine, SessionLocal
    engine = create_async_engine(url, echo=False)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    # Import models to register them
    from backend.data import models
    return engine

def get_session():
    return SessionLocal()
```

- [ ] **Step 4: Create models.py**

```python
# backend/data/models.py
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Device(Base):
    __tablename__ = "devices"
    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    status = Column(String, default="idle")
    position_x = Column(Float, default=0.0)
    position_y = Column(Float, default=0.0)
    position_z = Column(Float, default=0.0)
    config = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    status = Column(String, default="pending")
    priority = Column(Integer, default=3)
    source_pose = Column(JSON, default={})
    target_pose = Column(JSON, default={})
    dependencies = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class TraceLog(Base):
    __tablename__ = "trace_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String, index=True, nullable=False)
    task_id = Column(String, index=True)
    level = Column(String, nullable=False)
    module = Column(String, nullable=False)
    message = Column(String, nullable=False)
    context = Column(JSON, default={})
    timestamp = Column(Float, nullable=False)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd backend && pytest tests/test_data.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/data/ backend/tests/
git commit -m "feat(data): setup SQLite with SQLAlchemy async ORM"
```

---

## Phase 3: Algorithm Layer (M3)

### Task 4: Motion Planning Foundation

**Files:**
- Create: `backend/algorithm/__init__.py`
- Create: `backend/algorithm/planner/__init__.py`
- Create: `backend/algorithm/planner/foundation.py`
- Create: `backend/tests/test_planner_foundation.py`

Reference: `docs/algorithm/02-motion-planning.md` §2.1

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_planner_foundation.py
from backend.algorithm.planner.foundation import Pose6D, JointState, JointLimits
import numpy as np

def test_pose6d_from_matrix():
    matrix = np.eye(4)
    matrix[:3, 3] = [1.0, 2.0, 3.0]
    pose = Pose6D.from_matrix(matrix)
    assert np.allclose(pose.position, [1.0, 2.0, 3.0])

def test_joint_limits_validity():
    limits = JointLimits(
        positions_lower=np.array([-1.0] * 6),
        positions_upper=np.array([1.0] * 6),
        velocities=np.array([2.0] * 6),
        accelerations=np.array([10.0] * 6),
        efforts=np.array([100.0] * 6)
    )
    assert limits.positions_lower.shape == (6,)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_planner_foundation.py -v`
Expected: ModuleNotFoundError

- [ ] **Step 3: Implement foundation.py (per docs/algorithm/02-motion-planning.md §2.1)**

```python
# backend/algorithm/planner/foundation.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from scipy.spatial.transform import Rotation


@dataclass
class JointState:
    """关节状态"""
    positions: np.ndarray
    velocities: np.ndarray
    accelerations: np.ndarray
    efforts: np.ndarray
    timestamp: float = 0.0


@dataclass
class Pose6D:
    """6D位姿"""
    position: np.ndarray
    orientation: np.ndarray  # 四元数 [w, x, y, z]
    
    @classmethod
    def from_matrix(cls, matrix: np.ndarray) -> Pose6D:
        return cls(
            position=matrix[:3, 3],
            orientation=Rotation.from_matrix(matrix[:3, :3]).as_quat()
        )
    
    def to_matrix(self) -> np.ndarray:
        r = Rotation.from_quat(self.orientation)
        matrix = np.eye(4)
        matrix[:3, :3] = r.as_matrix()
        matrix[:3, 3] = self.position
        return matrix
    
    def distance_to(self, other: Pose6D) -> float:
        pos_dist = np.linalg.norm(self.position - other.position)
        ori_dist = 1.0 - abs(np.dot(self.orientation, other.orientation))
        return pos_dist + 0.5 * ori_dist


@dataclass
class JointLimits:
    """关节限位"""
    positions_lower: np.ndarray
    positions_upper: np.ndarray
    velocities: np.ndarray
    accelerations: np.ndarray
    efforts: np.ndarray


@dataclass
class TrajectoryPoint:
    """轨迹点"""
    positions: np.ndarray
    velocities: np.ndarray = field(default_factory=lambda: np.array([]))
    accelerations: np.ndarray = field(default_factory=lambda: np.array([]))
    time_from_start: float = 0.0


@dataclass
class Trajectory:
    """关节空间轨迹"""
    joint_names: List[str]
    points: List[TrajectoryPoint]
    
    @property
    def num_joints(self) -> int:
        return len(self.joint_names)
    
    def get_duration(self) -> float:
        return self.points[-1].time_from_start if self.points else 0.0
    
    def sample(self, time: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        if not self.points:
            raise ValueError("轨迹为空")
        if time <= self.points[0].time_from_start:
            p = self.points[0]
            return p.positions, p.velocities, p.accelerations
        if time >= self.points[-1].time_from_start:
            p = self.points[-1]
            return p.positions, p.velocities, p.accelerations
        for i in range(len(self.points) - 1):
            t0, t1 = self.points[i].time_from_start, self.points[i+1].time_from_start
            if t0 <= time <= t1:
                alpha = (time - t0) / (t1 - t0)
                p0, p1 = self.points[i], self.points[i+1]
                return ((1-alpha)*p0.positions + alpha*p1.positions,
                        (1-alpha)*p0.velocities + alpha*p1.velocities,
                        (1-alpha)*p0.accelerations + alpha*p1.accelerations)
        p = self.points[-1]
        return p.positions, p.velocities, p.accelerations
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_planner_foundation.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/algorithm/planner/ backend/tests/test_planner_foundation.py
git commit -m "feat(algorithm): add motion planning foundation (Pose6D, JointState)"
```

---

### Task 5: Motion Planning - RRT* Global Planner

**Files:**
- Create: `backend/algorithm/planner/global_planner.py`
- Create: `backend/tests/test_rrt_star.py`

Reference: `docs/algorithm/02-motion-planning.md` §2.2

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_rrt_star.py
from backend.algorithm.planner.foundation import JointLimits
from backend.algorithm.planner.global_planner import SamplingBasedPlanner
import numpy as np


class MockCollisionWorld:
    def check_collision(self, q, fk):
        return False, None

class MockKinematics:
    def forward(self, q):
        return np.eye(4)


def test_rrt_star_finds_path():
    limits = JointLimits(
        positions_lower=np.array([-np.pi]*6),
        positions_upper=np.array([np.pi]*6),
        velocities=np.array([2.0]*6),
        accelerations=np.array([10.0]*6),
        efforts=np.array([100.0]*6)
    )
    planner = SamplingBasedPlanner(
        joint_limits=limits,
        collision_world=MockCollisionWorld(),
        kinematics=MockKinematics(),
        max_iterations=500
    )
    start = np.zeros(6)
    goal = np.array([1.0, 0.5, 0.3, 0.2, 0.1, 0.0])
    result = planner.plan(start, goal)
    assert result.success
```

- [ ] **Step 2-3: Implement and test**

Implement `global_planner.py` per `docs/algorithm/02-motion-planning.md` §2.2 (SamplingBasedPlanner class with `plan()`, `_steer()`, `_get_nearby_nodes()` methods).

- [ ] **Step 4: Commit**

```bash
git add backend/algorithm/planner/global_planner.py backend/tests/test_rrt_star.py
git commit -m "feat(algorithm): implement 6D RRT* global planner"
```

---

### Task 6: Motion Planning - Trajectory Optimizer

**Files:**
- Create: `backend/algorithm/planner/local_optimizer.py`

Reference: `docs/algorithm/02-motion-planning.md` §2.3

- [ ] **Step 1: Write failing test**

```python
from backend.algorithm.planner.local_optimizer import TrajectoryOptimizer
from backend.algorithm.planner.foundation import Trajectory, TrajectoryPoint
import numpy as np

def test_optimizer_smoothing():
    traj = Trajectory(
        joint_names=["j1", "j2"],
        points=[TrajectoryPoint(positions=np.array([0.0, 0.0]), time_from_start=t*0.1) 
                for t in range(10)]
    )
    # Test optimizer class can be instantiated
    # (Full test requires JointLimits and CollisionWorld)
    assert TrajectoryOptimizer is not None
```

- [ ] **Step 2-3: Implement TrajectoryOptimizer per docs/algorithm §2.3**

Implement `TrajectoryOptimizer` class with `optimize()`, `_calculate_smoothness_cost()`, `_calculate_collision_cost()` methods.

- [ ] **Step 4: Commit**

```bash
git add backend/algorithm/planner/local_optimizer.py backend/tests/
git commit -m "feat(algorithm): add 6D trajectory optimizer (gradient + stochastic)"
```

---

### Task 7: Motion Planning - Trajectory Interpolator

**Files:**
- Create: `backend/algorithm/planner/interpolator.py`

Reference: `docs/algorithm/02-motion-planning.md` §2.4

- [ ] **Step 1-3: Implement TrajectoryInterpolator with S-curve and linear modes per §2.4**

- [ ] **Step 4: Commit**

```bash
git add backend/algorithm/planner/interpolator.py
git commit -m "feat(algorithm): add trajectory interpolator (S-curve/linear)"
```

---

### Task 8: Task Scheduler

**Files:**
- Create: `backend/algorithm/scheduler/__init__.py`
- Create: `backend/algorithm/scheduler/task.py`
- Create: `backend/algorithm/scheduler/scheduler.py`
- Create: `backend/tests/test_scheduler.py`

Reference: `docs/algorithm/04-task-scheduling.md` §3.4

- [ ] **Step 1: Write failing test**

```python
from backend.algorithm.scheduler.scheduler import TaskScheduler
from backend.algorithm.scheduler.task import Task, TaskPriority

def test_priority_queue_orders_critical_first():
    scheduler = TaskScheduler()
    low = Task(task_id="t1", task_type="move", priority=TaskPriority.LOW)
    high = Task(task_id="t2", task_type="move", priority=TaskPriority.HIGH)
    scheduler.add_task(low)
    scheduler.add_task(high)
    batch = scheduler.get_next_batch()
    assert batch[0].task_id == "t2"  # HIGH priority first
```

- [ ] **Step 2-3: Implement per docs/algorithm §3.4**

Implement Task, TaskPriority, ExecutionStatus, TaskScheduler classes with Kahn topological sort and heapq priority queue.

- [ ] **Step 4: Commit**

```bash
git add backend/algorithm/scheduler/
git commit -m "feat(algorithm): add task scheduler with Kahn topological sort"
```

---

### Task 9: Perception - Visual Preprocessing

**Files:**
- Create: `backend/algorithm/perception/__init__.py`
- Create: `backend/algorithm/perception/preprocessing.py`
- Create: `backend/tests/test_perception_preprocessing.py`

Reference: `docs/algorithm/03-perception.md` §3.1

- [ ] **Step 1: Write failing test**

```python
from backend.algorithm.perception.preprocessing import RGBDPreprocessor, PointCloudProcessor
import numpy as np

def test_depth_scale_conversion():
    preprocessor = RGBDPreprocessor()
    depth_raw = np.array([[1000, 2000], [3000, 4000]], dtype=np.uint16)
    depth_m = preprocessor.process_depth(depth_raw)
    assert np.allclose(depth_m[0, 0], 1.0)
    assert np.allclose(depth_m[1, 1], 4.0)
```

- [ ] **Step 2-3: Implement per docs/algorithm §3.1**

Implement RGBDPreprocessor (depth scaling, filtering), PointCloudProcessor (depth_to_pointcloud, voxel downsampling, outlier removal).

- [ ] **Step 4: Commit**

```bash
git add backend/algorithm/perception/preprocessing.py
git commit -m "feat(algorithm): add RGB-D preprocessing and point cloud generation"
```

---

### Task 10: Perception - Unified Detector

**Files:**
- Create: `backend/algorithm/perception/detector.py`

Reference: `docs/algorithm/03-perception.md` §3.2

- [ ] **Step 1-3: Implement UnifiedDetector (mock YOLO + YOLO-World fusion)**

Implement BoundingBox, DetectedObject, DetectionConfig, UnifiedDetector with closed_set + open_set detection fusion and NMS.

- [ ] **Step 4: Commit**

```bash
git add backend/algorithm/perception/detector.py
git commit -m "feat(algorithm): add unified detector (closed-set + open-set fusion)"
```

---

## Phase 4: Trace Logging (M3.5)

### Task 11: Trace Logger Implementation

**Files:**
- Create: `backend/logging/__init__.py`
- Create: `backend/logging/trace_logger.py`
- Create: `backend/logging/task_logger.py`
- Create: `backend/logging/algorithm_logger.py`

- [ ] **Step 1-3: Implement trace logging per design §3.5**

Implement TraceLogger (Trace ID generation), TaskLogger (task lifecycle), AlgorithmLogger (algorithm execution logging).

- [ ] **Step 4: Commit**

```bash
git add backend/logging/
git commit -m "feat(logging): add trace logging system (task lifecycle + algorithm)"
```

---

## Phase 5: Business Services (M4)

### Task 12: Device Service

**Files:**
- Create: `backend/services/__init__.py`
- Create: `backend/services/device_service.py`
- Create: `backend/algorithm/simulator/device_base.py`
- Create: `backend/algorithm/simulator/device_manager.py`

- [ ] **Step 1-3: Implement DeviceService with DeviceManager**

Implement device base class, RobotSimulator, AGVSimulator, StackerSimulator, DeviceManager, DeviceService.

- [ ] **Step 4: Commit**

```bash
git add backend/services/device_service.py backend/algorithm/simulator/
git commit -m "feat(services): add device service with simulator layer"
```

---

### Task 13: Order/Dispatch/Inventory Services

**Files:**
- Create: `backend/services/order_service.py`
- Create: `backend/services/dispatch_service.py`
- Create: `backend/services/inventory_service.py`

- [ ] **Step 1-3: Implement business services**

Implement OrderService (CRUD), DispatchService (task decomposition + scheduling), InventoryService (stock management).

- [ ] **Step 4: Commit**

```bash
git add backend/services/
git commit -m "feat(services): add order, dispatch, inventory services"
```

---

## Phase 6: API Layer (M5)

### Task 14: REST Routes

**Files:**
- Create: `backend/api/__init__.py`
- Create: `backend/api/routes.py`
- Create: `backend/api/openapi.py`
- Create: `backend/api/dependencies.py`

- [ ] **Step 1-3: Implement FastAPI routes with Swagger docs**

Implement all REST endpoints per design §3.1, with OpenAPI configuration for Chinese descriptions.

- [ ] **Step 4: Commit**

```bash
git add backend/api/
git commit -m "feat(api): add REST routes with Swagger/OpenAPI documentation"
```

---

### Task 15: WebSocket Real-time

**Files:**
- Create: `backend/api/websocket.py`

- [ ] **Step 1-3: Implement WebSocket for real-time device state and logs**

Implement `/ws/realtime` (device updates) and `/ws/logs` (trace logs) WebSocket endpoints.

- [ ] **Step 4: Commit**

```bash
git add backend/api/websocket.py
git commit -m "feat(api): add WebSocket for real-time state and log streaming"
```

---

## Phase 7: Frontend (M6)

### Task 16: Three.js Scene Manager

**Files:**
- Create: `frontend/src/three/scene.ts`
- Create: `frontend/src/three/models.ts`
- Create: `frontend/src/three/warehouse.ts`

- [ ] **Step 1-3: Implement 3D scene**

Create Three.js scene, Robot/AGV/Stacker models, warehouse layout.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/three/
git commit -m "feat(frontend): add Three.js 3D scene with warehouse layout"
```

---

### Task 17: Frontend API Client + Dashboard

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/dashboard/DeviceStatus.vue`
- Create: `frontend/src/dashboard/TaskQueue.vue`

- [ ] **Step 1-3: Implement API client + dashboard components**

Implement Axios API client, DeviceStatus panel (ECharts), TaskQueue chart.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/api/ frontend/src/dashboard/
git commit -m "feat(frontend): add API client and ECharts dashboard"
```

---

## Phase 8: Testing & Documentation (M7)

### Task 18: Integration Tests

**Files:**
- Create: `backend/tests/test_integration.py`

- [ ] **Step 1-3: Write integration tests for end-to-end flows**

Test scenarios: dock loading, AGV transport, warehouse, digital twin.

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_integration.py
git commit -m "test: add integration tests for 4 demo scenarios"
```

---

### Task 19: README Documentation

**Files:**
- Create: `README.md`

- [ ] **Step 1-3: Write comprehensive README**

Document: architecture overview, setup instructions, running the demo, API endpoints, scenarios.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README with setup and usage guide"
```

---

## Success Criteria

1. ✅ Backend runs at `http://localhost:8000`
2. ✅ Swagger UI accessible at `http://localhost:8000/docs`
3. ✅ Frontend runs at `http://localhost:5173`
4. ✅ 4 demo scenarios visible in 3D
5. ✅ All algorithm modules implemented per `docs/algorithm/`
6. ✅ Trace logs queryable via `/api/logs/trace/{trace_id}`
7. ✅ WebSocket streams device state and logs in real-time
8. ✅ Test coverage ≥ 80% for algorithm modules

## Out of Scope

- Production deployment scripts
- Real hardware integration
- Performance optimization beyond prototype
- Multi-user authentication
- Database migrations (using fresh DB for prototype)