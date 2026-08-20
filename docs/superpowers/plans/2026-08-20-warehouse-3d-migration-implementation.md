# Warehouse 3D Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate warehouse_theatre_3d's complete 3D visualization capability to robot-logic/simulation as the simulation foundation framework.

**Architecture:** This migration extracts the Three.js 3D rendering engine from warehouse_theatre_3d (wt3d-vue.js ~4800 lines), converts the Frappe API layer to FastAPI, and integrates the resulting components into the simulation frontend. The frontend uses Vue 3 + Pinia for state management, with a modular architecture separating engine, zones, facilities, and UI components.

**Tech Stack:** Vue 3, Pinia, Three.js (npm), TypeScript, FastAPI, Pydantic, Python 3.11+

## Global Constraints

- **Vue 3**: Use Composition API with `<script setup>` syntax
- **Three.js**: Use npm package `three@^0.162.0` (already in simulation/package.json)
- **State Management**: Pinia store for warehouse state
- **API**: FastAPI REST endpoints, no Frappe dependency
- **Storage**: JSON files for demo data (no database required)
- **Commit Style**: One feature per commit, conventional commits format

## Phase 1: Project Setup

### Task 1.1: Create Directory Structure

**Files:**
- Create: `simulation/frontend/src/warehouse/engine/zones/.gitkeep`
- Create: `simulation/frontend/src/warehouse/engine/facilities/.gitkeep`
- Create: `simulation/frontend/src/warehouse/engine/docks/.gitkeep`
- Create: `simulation/frontend/src/warehouse/engine/vehicles/.gitkeep`
- Create: `simulation/frontend/src/warehouse/engine/shell/.gitkeep`
- Create: `simulation/frontend/src/warehouse/agv/.gitkeep`
- Create: `simulation/frontend/src/warehouse/components/.gitkeep`
- Create: `simulation/frontend/src/warehouse/store/.gitkeep`
- Create: `simulation/frontend/src/warehouse/api/.gitkeep`
- Create: `simulation/frontend/src/warehouse/composables/.gitkeep`
- Create: `simulation/frontend/src/warehouse/types/.gitkeep`
- Create: `simulation/frontend/src/warehouse/i18n/.gitkeep`
- Create: `simulation/frontend/src/warehouse/utils/.gitkeep`
- Create: `simulation/backend/routers/warehouse/.gitkeep`
- Create: `simulation/backend/models/warehouse/.gitkeep`
- Create: `simulation/backend/services/warehouse/.gitkeep`

**Interfaces:**
- Produces: Empty directory structure for all modules

- [ ] **Step 1: Create all warehouse directories**

```bash
mkdir -p simulation/frontend/src/warehouse/engine/zones
mkdir -p simulation/frontend/src/warehouse/engine/facilities
mkdir -p simulation/frontend/src/warehouse/engine/docks
mkdir -p simulation/frontend/src/warehouse/engine/vehicles
mkdir -p simulation/frontend/src/warehouse/engine/shell
mkdir -p simulation/frontend/src/warehouse/agv
mkdir -p simulation/frontend/src/warehouse/components
mkdir -p simulation/frontend/src/warehouse/store
mkdir -p simulation/frontend/src/warehouse/api
mkdir -p simulation/frontend/src/warehouse/composables
mkdir -p simulation/frontend/src/warehouse/types
mkdir -p simulation/frontend/src/warehouse/i18n
mkdir -p simulation/frontend/src/warehouse/utils
mkdir -p simulation/backend/routers/warehouse
mkdir -p simulation/backend/models/warehouse
mkdir -p simulation/backend/services/warehouse
```

- [ ] **Step 2: Create .gitkeep files**

```bash
touch simulation/frontend/src/warehouse/engine/zones/.gitkeep
touch simulation/frontend/src/warehouse/engine/facilities/.gitkeep
touch simulation/frontend/src/warehouse/engine/docks/.gitkeep
touch simulation/frontend/src/warehouse/engine/vehicles/.gitkeep
touch simulation/frontend/src/warehouse/engine/shell/.gitkeep
touch simulation/frontend/src/warehouse/agv/.gitkeep
touch simulation/frontend/src/warehouse/components/.gitkeep
touch simulation/frontend/src/warehouse/store/.gitkeep
touch simulation/frontend/src/warehouse/api/.gitkeep
touch simulation/frontend/src/warehouse/composables/.gitkeep
touch simulation/frontend/src/warehouse/types/.gitkeep
touch simulation/frontend/src/warehouse/i18n/.gitkeep
touch simulation/frontend/src/warehouse/utils/.gitkeep
touch simulation/backend/routers/warehouse/.gitkeep
touch simulation/backend/models/warehouse/.gitkeep
touch simulation/backend/services/warehouse/.gitkeep
```

- [ ] **Step 3: Commit**

```bash
git add simulation/frontend/src/warehouse/ simulation/backend/routers/warehouse/ simulation/backend/models/warehouse/ simulation/backend/services/warehouse/
git commit -m "chore: create warehouse 3D migration directory structure"
```

### Task 1.2: Create TypeScript Type Definitions

**Files:**
- Create: `simulation/frontend/src/warehouse/types/index.ts`
- Create: `simulation/frontend/src/warehouse/types/warehouse.ts`
- Create: `simulation/frontend/src/warehouse/types/zone.ts`
- Create: `simulation/frontend/src/warehouse/types/logistics.ts`
- Create: `simulation/frontend/src/warehouse/types/agv.ts`

**Interfaces:**
- Produces: Type definitions for all warehouse data models

- [ ] **Step 1: Create types/index.ts**

```typescript
export * from './warehouse'
export * from './zone'
export * from './logistics'
export * from './agv'
```

- [ ] **Step 2: Create types/warehouse.ts**

```typescript
export interface UOMCapacity {
  uom: string
  qty: number
  reserved: number
  cap: number
}

export interface ItemStock {
  code: string
  name: string
  uom: string
  group: string
  qty: number
  reserved: number
  rate: number
  stock_value: number
}

export interface SlotLevel {
  warehouse_id: string
  label: string
  uoms: UOMCapacity[]
  items: ItemStock[]
}

export interface Slot {
  warehouse_id: string
  label: string
  row: number
  col: number
  row_gap: number
  levels: SlotLevel[]
}

export interface WarehouseGroup {
  id: string
  name: string
  parent_id: string
  parent_name: string
  slot_count: number
}

export interface WarehouseDetail {
  name: string
  warehouse_name: string
  company: string
  wt_warehouse_type: 'Building' | 'Floor' | 'Slot' | 'Bin' | 'Dock'
  parent_warehouse: string
  is_group: boolean
  disabled: boolean
  wt_row: number
  wt_col: number
  wt_row_gap: number
  uom_capacities: UOMCapacity[]
}

export type ViewMode = '3d' | '2d' | 'editor'
export type Language = 'zh' | 'en'
export type Theme = 'dark' | 'light'
```

- [ ] **Step 3: Create types/zone.ts**

```typescript
export type ZoneType = 'rack' | 'flow_rack' | 'automated' | 'high_rack' | 'mezzanine' | 'temp' | 'temp_bagged' | 'returns'

export interface Bounds {
  w: number
  d: number
}

export interface Wall {
  x0: number
  z0: number
  x1: number
  z1: number
  h: number
  dock_bumper?: boolean
}

export interface DockPlacement {
  ref: string
  x: number
  z: number
  rot?: number
}

export interface FacilityPlacement {
  ref: string
  kind: string
  x: number
  z: number
  w: number
  d: number
}

export interface Corridor {
  x0: number
  z0: number
  x1: number
  z1: number
  main?: boolean
}

export interface ShellBlueprint {
  bounds: Bounds
  walls: Wall[]
  docks: DockPlacement[]
  facilities: FacilityPlacement[]
  corridors: Corridor[]
  zones?: any[]
  markings?: any[]
  vehicles?: any[]
}

export interface Zone {
  ref: string
  name: string
  type: ZoneType
  x: number
  z: number
  w: number
  d: number
  levels?: number
  slots?: Slot[]
  cells?: AsrsCell[]
  bulks?: BulkArea[]
  occ?: { used: number; total: number }
}

export interface Facility {
  ref: string
  kind: string
  name: string
  x?: number
  z?: number
  w?: number
  d?: number
}

export interface Dock {
  name: string
  warehouse_name: string
  parent_warehouse: string
  slot_count: number
  wt_x?: number
  wt_z?: number
  flow?: 'inbound' | 'outbound'
}

export interface FloorFull {
  shell: ShellBlueprint | null
  zones: Zone[]
  facilities: Facility[]
  docks: Dock[]
}
```

- [ ] **Step 4: Create types/logistics.ts**

```typescript
export type TaskType = 'inbound' | 'outbound' | 'transfer'
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface TaskItem {
  item_code: string
  qty: number
}

export interface LogisticsTask {
  task_id: string
  task_type: TaskType
  status: TaskStatus
  source_dock: string
  target_slot: string
  items: TaskItem[]
  created_at: string
}

export interface LogisticsStats {
  total_inbound: number
  total_outbound: number
  avg_processing_time: number
  dock_utilization: number
}

export interface DockDetail extends Dock {
  slots?: DockSlot[]
}

export interface DockSlot {
  warehouse_id: string
  label: string
}
```

- [ ] **Step 5: Create types/agv.ts**

```typescript
export type CellType = 0 | 1 | 2 | 3  // blocked, walkable, main corridor, restricted

export interface AGVCell {
  t: CellType
  w: number
}

export interface AGVNode {
  id: string
  ref?: string
  type: 'dock' | 'aisle_entry' | 'charger' | 'entrance'
  gx: number
  gz: number
}

export interface AGVGrid {
  cellSize: number
  originX: number
  originZ: number
  cols: number
  rows: number
  cells: AGVCell[]
  nodes: AGVNode[]
}

export interface AisleGap {
  label: string
  z: number
}

export interface AGVPath {
  points: Array<{ x: number; z: number }>
  cost: number
}
```

- [ ] **Step 6: Commit**

```bash
git add simulation/frontend/src/warehouse/types/
git commit -m "feat(warehouse): add TypeScript type definitions"
```

### Task 1.3: Create Backend Data Models

**Files:**
- Create: `simulation/backend/models/warehouse/__init__.py`
- Create: `simulation/backend/models/warehouse/slot.py`
- Create: `simulation/backend/models/warehouse/zone.py`
- Create: `simulation/backend/models/warehouse/layout.py`
- Create: `simulation/backend/models/warehouse/logistics.py`
- Create: `simulation/backend/models/warehouse/agv.py`

**Interfaces:**
- Produces: Pydantic models for warehouse data

- [ ] **Step 1: Create models/warehouse/__init__.py**

```python
from .slot import UOMCapacity, ItemStock, SlotLevel, Slot, WarehouseGroup, WarehouseDetail
from .zone import (
    ZoneType, Bounds, Wall, DockPlacement, FacilityPlacement, Corridor,
    ShellBlueprint, Zone, Facility, Dock, FloorFull
)
from .logistics import TaskItem, LogisticsTask, LogisticsStats, DockDetail
from .agv import AGVCell, AGVNode, AGVGrid, CellType

__all__ = [
    "UOMCapacity", "ItemStock", "SlotLevel", "Slot", "WarehouseGroup", "WarehouseDetail",
    "ZoneType", "Bounds", "Wall", "DockPlacement", "FacilityPlacement", "Corridor",
    "ShellBlueprint", "Zone", "Facility", "Dock", "FloorFull",
    "TaskItem", "LogisticsTask", "LogisticsStats", "DockDetail",
    "AGVCell", "AGVNode", "AGVGrid", "CellType",
]
```

- [ ] **Step 2: Create models/warehouse/slot.py**

```python
from pydantic import BaseModel, Field
from typing import Optional


class UOMCapacity(BaseModel):
    uom: str
    qty: float = 0
    reserved: float = 0
    cap: float


class ItemStock(BaseModel):
    code: str = Field(alias="code")
    name: str = Field(alias="name")
    uom: str
    group: str
    qty: float = 0
    reserved: float = 0
    rate: float = 0
    stock_value: float = 0

    class Config:
        populate_by_name = True


class SlotLevel(BaseModel):
    warehouse_id: str
    label: str
    uoms: list[UOMCapacity] = []
    items: list[ItemStock] = []


class Slot(BaseModel):
    warehouse_id: str
    label: str
    row: int
    col: int
    row_gap: float = 0
    levels: list[SlotLevel] = []


class WarehouseGroup(BaseModel):
    id: str
    name: str
    parent_id: str
    parent_name: str
    slot_count: int = 0


class WarehouseDetail(BaseModel):
    name: str
    warehouse_name: str
    company: str = ""
    wt_warehouse_type: str = "Slot"
    parent_warehouse: str = ""
    is_group: bool = True
    disabled: bool = False
    wt_row: int = 0
    wt_col: int = 0
    wt_row_gap: float = 0
    uom_capacities: list[UOMCapacity] = []
```

- [ ] **Step 3: Create models/warehouse/zone.py**

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ZoneType(str, Enum):
    RACK = "rack"
    FLOW_RACK = "flow_rack"
    AUTOMATED = "automated"
    HIGH_RACK = "high_rack"
    MEZZANINE = "mezzanine"
    TEMP = "temp"
    TEMP_BAGGED = "temp_bagged"
    RETURNS = "returns"


class Bounds(BaseModel):
    w: float
    d: float


class Wall(BaseModel):
    x0: float
    z0: float
    x1: float
    z1: float
    h: float = 3.0
    dock_bumper: bool = False


class DockPlacement(BaseModel):
    ref: str
    x: float
    z: float
    rot: float = 0


class FacilityPlacement(BaseModel):
    ref: str
    kind: str
    x: float
    z: float
    w: float = 2
    d: float = 2


class Corridor(BaseModel):
    x0: float
    z0: float
    x1: float
    z1: float
    main: bool = False


class ShellBlueprint(BaseModel):
    bounds: Bounds
    walls: list[Wall] = []
    docks: list[DockPlacement] = []
    facilities: list[FacilityPlacement] = []
    corridors: list[Corridor] = []


class Zone(BaseModel):
    ref: str
    name: str
    type: ZoneType
    x: float
    z: float
    w: float
    d: float
    levels: int = 3
    slots: Optional[list[dict]] = None
    cells: Optional[list[dict]] = None
    bulks: Optional[list[dict]] = None
    occ: Optional[dict] = None


class Facility(BaseModel):
    ref: str
    kind: str
    name: str
    x: Optional[float] = None
    z: Optional[float] = None
    w: Optional[float] = None
    d: Optional[float] = None


class Dock(BaseModel):
    name: str
    warehouse_name: str
    parent_warehouse: str
    slot_count: int = 0
    wt_x: Optional[float] = None
    wt_z: Optional[float] = None
    flow: Optional[str] = None


class FloorFull(BaseModel):
    shell: Optional[ShellBlueprint] = None
    zones: list[Zone] = []
    facilities: list[Facility] = []
    docks: list[Dock] = []
```

- [ ] **Step 4: Create models/warehouse/logistics.py**

```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class TaskType(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    TRANSFER = "transfer"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskItem(BaseModel):
    item_code: str
    qty: float


class LogisticsTask(BaseModel):
    task_id: str
    task_type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    source_dock: str
    target_slot: str
    items: list[TaskItem] = []
    created_at: str


class LogisticsStats(BaseModel):
    total_inbound: int = 0
    total_outbound: int = 0
    avg_processing_time: float = 0
    dock_utilization: float = 0


class DockSlot(BaseModel):
    warehouse_id: str
    label: str


class DockDetail(BaseModel):
    name: str
    warehouse_name: str
    parent_warehouse: str
    slot_count: int = 0
    slots: list[DockSlot] = []
```

- [ ] **Step 5: Create models/warehouse/agv.py**

```python
from pydantic import BaseModel
from typing import Optional
from enum import IntEnum


class CellType(IntEnum):
    BLOCKED = 0
    WALKABLE = 1
    MAIN_CORRIDOR = 2
    RESTRICTED = 3


class AGVCell(BaseModel):
    t: int
    w: float = 1.0


class AGVNode(BaseModel):
    id: str
    ref: Optional[str] = None
    type: str  # 'dock' | 'aisle_entry' | 'charger' | 'entrance'
    gx: int
    gz: int


class AGVGrid(BaseModel):
    cellSize: float = 1.0
    originX: float = 0
    originZ: float = 0
    cols: int = 0
    rows: int = 0
    cells: list[AGVCell] = []
    nodes: list[AGVNode] = []
```

- [ ] **Step 6: Commit**

```bash
git add simulation/backend/models/warehouse/
git commit -m "feat(warehouse): add Pydantic data models"
```

---

## Phase 2: Frontend 3D Engine

### Task 2.1: Create ThreeEngine Core

**Files:**
- Create: `simulation/frontend/src/warehouse/engine/ThreeEngine.ts`
- Modify: `simulation/frontend/src/warehouse/engine/index.ts`

**Interfaces:**
- Consumes: THREE from npm package
- Produces: ThreeEngine class with init, buildScene, bindMouse, highlight methods

- [ ] **Step 1: Create engine/ThreeEngine.ts**

```typescript
import * as THREE from 'three'

// Re-export types for convenience
export type { WarehouseState } from '../types'

export interface EngineConfig {
  isDark: boolean
  showWalls: boolean
  showMarkings: boolean
}

export class ThreeEngine {
  private canvas: HTMLCanvasElement | null = null
  private cwEl: HTMLElement | null = null
  private renderer!: THREE.WebGLRenderer
  private scene!: THREE.Scene
  private camera!: THREE.PerspectiveCamera
  private rootGrp!: THREE.Group

  // Camera state
  private theta = 0.65
  private phi = 0.78
  private radius = 28
  private panX = 0
  private panZ = 0
  private targetTheta = 0.65
  private targetPhi = 0.78
  private targetRadius = 28
  private targetPanX = 0
  private targetPanZ = 0

  // Interaction state
  private drag = false
  private rightDrag = false
  private shiftDrag = false
  private lastX = 0
  private lastY = 0
  private hovKey: string | null = null
  private hovPick: THREE.Object3D | null = null
  private animRunning = false

  // Aisle mode
  public aisleMode = false
  public fpX = 0
  public fpY = 2.2
  public fpZ = 0
  public fpYaw = Math.PI
  public fpPitch = 0
  public fpSpeed = 0.15

  // Scene data
  public meshMap: Record<string, any> = {}
  public pickables: THREE.Object3D[] = []
  private wallGroup: THREE.Group | null = null
  private markingsGroup: THREE.Group | null = null
  private corridorGroup: THREE.Group | null = null
  private vehicleGroup: THREE.Group | null = null
  private dockGroup: THREE.Group | null = null
  private dockMeshMap: Record<string, any> = {}

  // Callbacks
  private onHover: ((data: any, x: number, y: number) => void) | null = null
  private onClick: ((data: any, wasSel: boolean, isDouble: boolean) => void) | null = null

  private config: EngineConfig = { isDark: true, showWalls: true, showMarkings: true }
  private ptL!: THREE.PointLight

  init(canvas: HTMLCanvasElement, cwEl: HTMLElement, config: EngineConfig = { isDark: true, showWalls: true, showMarkings: true }) {
    this.canvas = canvas
    this.cwEl = cwEl
    this.config = config

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false })
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.shadowMap.enabled = true
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap

    this.scene = new THREE.Scene()
    this._updateBackground()

    this.camera = new THREE.PerspectiveCamera(45, 1, 0.1, 200)
    this.camera.position.set(14, 18, 24)
    this.camera.lookAt(0, 0, 0)

    // Lights
    this.scene.add(new THREE.AmbientLight(0xffffff, 0.4))
    const dL = new THREE.DirectionalLight(0xffffff, 0.8)
    dL.position.set(12, 22, 12)
    dL.castShadow = true
    dL.shadow.mapSize.set(2048, 2048)
    dL.shadow.camera.left = -30
    dL.shadow.camera.right = 30
    dL.shadow.camera.top = 30
    dL.shadow.camera.bottom = -30
    this.scene.add(dL)
    this.scene.add(new THREE.DirectionalLight(0x4060ff, 0.25))

    this.ptL = new THREE.PointLight(0x60a5fa, 0.5, 60)
    this.ptL.position.set(0, 16, 0)
    this.scene.add(this.ptL)

    // Ground
    const fl = new THREE.Mesh(
      new THREE.PlaneGeometry(80, 80),
      new THREE.MeshStandardMaterial({ color: 0x0a0c12, roughness: 0.95, metalness: 0.05 })
    )
    fl.rotation.x = -Math.PI / 2
    fl.position.y = -0.02
    fl.receiveShadow = true
    this.scene.add(fl)

    // Grid
    const gc = this.config.isDark ? 0x181c28 : 0xdde1e7
    this.scene.add(new THREE.GridHelper(80, 40, gc, gc))

    this.rootGrp = new THREE.Group()
    this.scene.add(this.rootGrp)

    this._sizeRenderer()
    this._startAnimate()
    new ResizeObserver(() => this._sizeRenderer()).observe(cwEl)
  }

  private _updateBackground() {
    const bgCol = this.config.isDark ? 0x0c0e14 : 0xf0f2f5
    this.renderer.setClearColor(bgCol, 1)
    this.scene.background = new THREE.Color(bgCol)
    this.scene.fog = new THREE.Fog(bgCol, 50, 130)
  }

  private _sizeRenderer() {
    if (!this.cwEl) return
    const w = this.cwEl.clientWidth
    const h = this.cwEl.clientHeight
    if (!w || !h) return
    this.renderer.setSize(w, h, false)
    this.camera.aspect = w / h
    this.camera.updateProjectionMatrix()
  }

  private _startAnimate() {
    if (this.animRunning) return
    this.animRunning = true
    const loop = () => {
      requestAnimationFrame(loop)
      const t = performance.now() * 0.001
      this.theta += (this.targetTheta - this.theta) * 0.08
      this.phi += (this.targetPhi - this.phi) * 0.08
      this.radius += (this.targetRadius - this.radius) * 0.08
      this.panX += (this.targetPanX - this.panX) * 0.08
      this.panZ += (this.targetPanZ - this.panZ) * 0.08
      this._updateCamera()
      this.ptL.position.x = Math.sin(t * 0.35) * 7
      this.ptL.position.z = Math.cos(t * 0.35) * 7
      this.renderer.render(this.scene, this.camera)
    }
    loop()
  }

  private _updateCamera() {
    if (this.aisleMode) {
      this.camera.position.set(this.fpX, this.fpY, this.fpZ)
      this.camera.lookAt(
        this.fpX + Math.sin(this.fpYaw),
        this.fpY + this.fpPitch,
        this.fpZ + Math.cos(this.fpYaw)
      )
      return
    }
    this.camera.position.set(
      this.panX + this.radius * Math.sin(this.phi) * Math.sin(this.theta),
      this.radius * Math.cos(this.phi),
      this.panZ + this.radius * Math.sin(this.phi) * Math.cos(this.theta)
    )
    this.camera.lookAt(this.panX, 0, this.panZ)
  }

  // Placeholder for buildScene - will be implemented in zone renderer tasks
  buildScene(data: any) {
    // To be implemented in Task 2.2
  }

  clearRoot() {
    this.rootGrp.traverse(o => {
      if (o.geometry) o.geometry.dispose()
      if (o.material) {
        if ((o.material as THREE.Material).map) (o.material as THREE.Material).map!.dispose()
        o.material.dispose()
      }
    })
    while (this.rootGrp.children.length) this.rootGrp.remove(this.rootGrp.children[0])
    this.pickables = []
    this.meshMap = {}
  }

  bindMouse(cwEl: HTMLElement, onHover: (data: any, x: number, y: number) => void, onClick: (data: any, wasSel: boolean, isDouble: boolean) => void) {
    this.onHover = onHover
    this.onClick = onClick

    const rc = new THREE.Raycaster()
    const mouse = new THREE.Vector2()

    cwEl.addEventListener('mousedown', e => {
      this.drag = true
      this.rightDrag = e.button === 2
      this.shiftDrag = e.shiftKey
      this.lastX = e.clientX
      this.lastY = e.clientY
    })

    cwEl.addEventListener('contextmenu', e => e.preventDefault())
    window.addEventListener('mouseup', () => { this.drag = false })
    window.addEventListener('mousemove', e => {
      if (!this.drag) return
      const dx = e.clientX - this.lastX
      const dy = e.clientY - this.lastY
      this.lastX = e.clientX
      this.lastY = e.clientY

      if (this.aisleMode) {
        this.moveAisle(0, 0, -dx, -dy)
      } else if (this.rightDrag || this.shiftDrag) {
        const panScale = this.radius * 0.003
        const cosT = Math.cos(this.theta)
        const sinT = Math.sin(this.theta)
        this.targetPanX += (-dx * cosT - dy * sinT * Math.cos(this.phi)) * panScale
        this.targetPanZ += (dx * sinT - dy * cosT * Math.cos(this.phi)) * panScale
      } else {
        this.targetTheta -= dx * 0.008
        this.targetPhi = Math.max(0.08, Math.min(1.45, this.targetPhi + dy * 0.008))
      }
    })

    cwEl.addEventListener('wheel', e => {
      e.preventDefault()
      this.targetRadius = Math.max(2, Math.min(300, this.targetRadius + e.deltaY * 0.08))
    }, { passive: false })

    cwEl.addEventListener('mousemove', e => {
      if (this.drag) { onHover(null, 0, 0); return }
      const r = cwEl.getBoundingClientRect()
      mouse.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1)
      rc.setFromCamera(mouse, this.camera)
      const hits = rc.intersectObjects(Object.values(this.meshMap).map(d => d.proxy).filter(Boolean))
      if (hits.length) {
        this.hovKey = hits[0].object.userData.key
        this.hovPick = null
        onHover(this.meshMap[this.hovKey], e.clientX - r.left, e.clientY - r.top)
        cwEl.style.cursor = 'pointer'
        return
      }
      this.hovKey = null
      this.hovPick = null
      onHover(null, 0, 0)
      cwEl.style.cursor = 'grab'
    })

    cwEl.addEventListener('click', () => {
      if (this.hovKey && this.onClick) {
        const d = this.meshMap[this.hovKey]
        if (d) this.onClick(d, false, false)
      } else if (this.hovPick && this.hovPick.userData && this.onClick) {
        this.onClick({ pick: this.hovPick.userData }, false, false)
      }
    })
  }

  moveAisle(forward: number, strafe: number, turnY: number, turnX: number) {
    if (!this.aisleMode) return
    this.fpYaw += turnY * 0.02
    this.fpPitch = Math.max(-0.8, Math.min(0.8, this.fpPitch + turnX * 0.02))
    this.fpX += Math.sin(this.fpYaw) * forward * this.fpSpeed + Math.cos(this.fpYaw) * strafe * this.fpSpeed
    this.fpZ += Math.cos(this.fpYaw) * forward * this.fpSpeed - Math.sin(this.fpYaw) * strafe * this.fpSpeed
  }

  highlight(key: string | null) {
    // Placeholder - will be implemented with zone renderers
  }

  centerView() {
    this.targetTheta = 0
    this.targetPhi = Math.PI / 4
    this.targetRadius = 80
    this.targetPanX = 0
    this.targetPanZ = 0
  }

  setDarkMode(isDark: boolean) {
    this.config.isDark = isDark
    this._updateBackground()
  }

  setShowWalls(show: boolean) {
    this.config.showWalls = show
    if (this.wallGroup) this.wallGroup.visible = show
    if (this.vehicleGroup) {
      this.vehicleGroup.traverse(o => {
        if (o.userData.isRoof) o.visible = show
      })
    }
  }

  setShowMarkings(show: boolean) {
    this.config.showMarkings = show
    if (this.markingsGroup) this.markingsGroup.visible = show
  }
}

export const engine = new ThreeEngine()
```

- [ ] **Step 2: Create engine/index.ts**

```typescript
export { ThreeEngine, engine } from './ThreeEngine'
```

- [ ] **Step 3: Commit**

```bash
git add simulation/frontend/src/warehouse/engine/
git commit -m "feat(warehouse): create ThreeEngine core class"
```

### Task 2.2: Create Zone Renderers

**Files:**
- Create: `simulation/frontend/src/warehouse/engine/zones/RackZone.ts`
- Create: `simulation/frontend/src/warehouse/engine/zones/AsrsZone.ts`
- Create: `simulation/frontend/src/warehouse/engine/zones/HighRackZone.ts`
- Create: `simulation/frontend/src/warehouse/engine/zones/MezzanineZone.ts`
- Create: `simulation/frontend/src/warehouse/engine/zones/TempZone.ts`
- Create: `simulation/frontend/src/warehouse/engine/zones/TempBaggedZone.ts`
- Create: `simulation/frontend/src/warehouse/engine/zones/ReturnsZone.ts`
- Create: `simulation/frontend/src/warehouse/engine/zones/index.ts`

**Interfaces:**
- Consumes: ThreeEngine instance, Zone data, Slot data
- Produces: Zone mesh groups added to scene

- [ ] **Step 1: Create zones/RackZone.ts**

```typescript
import * as THREE from 'three'
import { Slot, Zone } from '../../types'

// Helper functions from wt3d-vue.js
function lvFill(lv: any): number {
  const wc = (lv.uoms || []).filter((u: any) => u.cap > 0)
  if (!wc.length) return (lv.uoms || []).some((u: any) => u.qty > 0) ? 50 : 0
  return Math.round(wc.reduce((s: number, u: any) => s + Math.min(100, Math.round(u.qty / u.cap * 100)), 0) / wc.length)
}

function FC(p: number): number {
  return p >= 90 ? 0xf87171 : p >= 70 ? 0xfb923c : p >= 40 ? 0xfacc15 : 0x4ade80
}

const SW = 2.2, SD = 2.2, GAP = 0.6, LVH = 1.0, BASE = 0.1

export function buildRackZone(
  rootGrp: THREE.Group,
  meshMap: Record<string, any>,
  zone: Zone,
  slots: Slot[],
  isDark: boolean
) {
  const THREE = (window as any).THREE

  // Filter slots for this zone
  let zs = zone.ref === 'RACK-LEGACY' ? slots
    : slots.filter(s => (s.warehouse_id || '').startsWith(zone.ref + '-'))

  if (!zs.length) return

  const rowOf = (s: Slot) => s.row
  const colOf = (s: Slot) => s.col
  const gapOf = (s: Slot) => s.row_gap

  const cols = Math.max(...zs.map(colOf), 0) + 1
  const maxRow = Math.max(...zs.map(rowOf), 0)
  const rowZOffset: Record<number, number> = {}
  let cumZ = 0

  for (let r = 0; r <= maxRow; r++) {
    rowZOffset[r] = cumZ
    const rowSlots = zs.filter(s => rowOf(s) === r)
    const rowGap = rowSlots.length ? (parseFloat(String(gapOf(rowSlots[0]))) || 0) : 0
    cumZ += SD + GAP + rowGap
  }
  const totalDepth = cumZ - GAP

  const ox = (zone.x || 0) - (cols * (SW + GAP) - GAP) / 2
  const oz = (zone.z || 0) - totalDepth / 2

  const baseMat = new THREE.MeshStandardMaterial({ color: isDark ? 0x1a2235 : 0xdde3ef, roughness: 0.8, metalness: 0.25 })
  const pilMat = new THREE.MeshStandardMaterial({ color: isDark ? 0x2d3a52 : 0xc5cdd8, roughness: 0.7, metalness: 0.4 })
  const shelfMat = new THREE.MeshStandardMaterial({ color: isDark ? 0x22304a : 0xcfd6e0, roughness: 0.9 })

  zs.forEach(sl => {
    const nL = sl.levels.length
    const cx = ox + colOf(sl) * (SW + GAP) + SW / 2
    const cz = oz + (rowZOffset[rowOf(sl)] || 0) + SD / 2

    // Base
    const base = new THREE.Mesh(new THREE.BoxGeometry(SW, BASE, SD), baseMat)
    base.position.set(cx, BASE / 2, cz)
    base.castShadow = true
    base.receiveShadow = true
    rootGrp.add(base)

    // Pillars
    [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([dx, dz]) => {
      const p = new THREE.Mesh(new THREE.BoxGeometry(0.06, nL * LVH + BASE, 0.06), pilMat)
      p.position.set(cx + dx * (SW / 2 - 0.04), (nL * LVH + BASE) / 2, cz + dz * (SD / 2 - 0.04))
      p.castShadow = true
      rootGrp.add(p)
    })

    // Levels
    sl.levels.forEach((lv, li) => {
      const lp = lvFill(lv)
      const hs = (lv.uoms || []).some((u: any) => u.qty > 0)
      const col = hs ? FC(lp) : (isDark ? 0x101827 : 0xe8edf5)
      const y0 = BASE + li * LVH

      // Shelf board
      const shelf = new THREE.Mesh(new THREE.BoxGeometry(SW, 0.024, SD), shelfMat)
      shelf.position.set(cx, y0 + 0.012, cz)
      rootGrp.add(shelf)

      // Goods fill
      if (hs) {
        const fh = Math.max(0.05, (lp / 100) * (LVH - 0.12))
        const fillM = new THREE.Mesh(
          new THREE.BoxGeometry(SW - 0.26, fh, SD - 0.26),
          new THREE.MeshStandardMaterial({ color: col, roughness: 0.38, metalness: 0.14, emissive: col, emissiveIntensity: 0.2 })
        )
        fillM.position.set(cx, y0 + 0.06 + fh / 2, cz)
        fillM.castShadow = true
        rootGrp.add(fillM)
      }

      // Invisible pick proxy
      const proxy = new THREE.Mesh(
        new THREE.BoxGeometry(SW - 0.06, LVH - 0.02, SD - 0.06),
        new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, depthWrite: false })
      )
      proxy.position.set(cx, y0 + LVH / 2, cz)
      proxy.userData = { slot: sl, lv, key: sl.warehouse_id + '__' + lv.warehouse_id }
      rootGrp.add(proxy)

      meshMap[sl.warehouse_id + '__' + lv.warehouse_id] = { lv, slot: sl, li, col, proxy }
    })
  })
}
```

- [ ] **Step 2: Create zones/index.ts**

```typescript
export { buildRackZone } from './RackZone'
// Additional zone exports will be added as they are implemented
```

- [ ] **Step 3: Commit**

```bash
git add simulation/frontend/src/warehouse/engine/zones/
git commit -m "feat(warehouse): create RackZone renderer"
```

### Task 2.3: Create Pinia Store

**Files:**
- Create: `simulation/frontend/src/warehouse/store/warehouse.ts`
- Create: `simulation/frontend/src/warehouse/store/index.ts`

**Interfaces:**
- Produces: Pinia store with reactive warehouse state

- [ ] **Step 1: Create store/warehouse.ts**

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  WarehouseGroup, Slot, SlotDetail, WarehouseDetail,
  FloorFull, Dock, LogisticsTask, LogisticsStats, AGVGrid, AisleGap
} from '../types'

export const useWarehouseStore = defineStore('warehouse', () => {
  // View state
  const isDark = ref(true)
  const lang = ref<'zh' | 'en'>('zh')
  const curView = ref<'3d' | '2d' | 'editor'>('3d')

  // Warehouse data
  const groups = ref<WarehouseGroup[]>([])
  const curGroup = ref<WarehouseGroup | null>(null)
  const slots = ref<Slot[]>([])

  // Selection state
  const selKey = ref<string | null>(null)
  const detailPanelOpen = ref(false)
  const detailData = ref<any | null>(null)
  const itemModalOpen = ref(false)
  const itemData = ref<any | null>(null)

  // Layout
  const floorFull = ref<FloorFull | null>(null)
  const showWalls = ref(true)
  const showMarkings = ref(true)

  // Docks & Logistics
  const docks = ref<Dock[]>([])
  const logisticsTasks = ref<LogisticsTask[]>([])
  const logisticsStats = ref<LogisticsStats>({ total_inbound: 0, total_outbound: 0, avg_processing_time: 0, dock_utilization: 0 })
  const selectedTask = ref<LogisticsTask | null>(null)
  const logisticsOpen = ref(false)

  // AGV
  const agvGrid = ref<AGVGrid | null>(null)
  const agvOverlay = ref(false)
  const agvOpen = ref(false)
  const agvTool = ref<'walk' | 'block' | 'main' | 'restricted'>('walk')
  const agvCellSize = ref(1.0)

  // Camera
  const aisleMode = ref(false)
  const aisleGaps = ref<AisleGap[]>([])

  // UI state
  const loading = ref(false)
  const setupComplete = ref(true) // Demo mode skips setup
  const sidebarOpen = ref(true)

  // Editors
  const configOpen = ref(false)
  const configSlot = ref<Slot | null>(null)

  // Stats computed
  const hudStats = computed(() => {
    const bins = slots.value.flatMap(sl => sl.levels)
    const total = bins.length
    const occ = bins.filter(l => (l.uoms || []).some(u => u.qty > 0)).length
    const qty = slots.value.reduce((s, sl) => s + sl.levels.reduce((ss, l) => ss + (l.uoms || []).reduce((sss, u) => sss + (u.qty || 0), 0), 0), 0)
    return { total, occ, free: total - occ, qty }
  })

  return {
    // View
    isDark, lang, curView,
    // Warehouse
    groups, curGroup, slots,
    // Selection
    selKey, detailPanelOpen, detailData, itemModalOpen, itemData,
    // Layout
    floorFull, showWalls, showMarkings,
    // Docks & Logistics
    docks, logisticsTasks, logisticsStats, selectedTask, logisticsOpen,
    // AGV
    agvGrid, agvOverlay, agvOpen, agvTool, agvCellSize,
    // Camera
    aisleMode, aisleGaps,
    // UI
    loading, setupComplete, sidebarOpen,
    // Editors
    configOpen, configSlot,
    // Computed
    hudStats,
  }
})
```

- [ ] **Step 2: Create store/index.ts**

```typescript
export { useWarehouseStore } from './warehouse'
```

- [ ] **Step 3: Commit**

```bash
git add simulation/frontend/src/warehouse/store/
git commit -m "feat(warehouse): create Pinia store"
```

---

## Phase 3: API Client

### Task 3.1: Create Backend API Router

**Files:**
- Create: `simulation/backend/routers/warehouse/__init__.py`
- Create: `simulation/backend/routers/warehouse/slots.py`
- Create: `simulation/backend/routers/warehouse/layout.py`
- Create: `simulation/backend/routers/warehouse/logistics.py`
- Create: `simulation/backend/routers/warehouse/agv.py`
- Modify: `simulation/backend/main.py`

**Interfaces:**
- Produces: FastAPI router with warehouse API endpoints

- [ ] **Step 1: Create routers/warehouse/__init__.py**

```python
from fastapi import APIRouter
from . import slots, layout, logistics, agv

router = APIRouter(prefix="/api/warehouse", tags=["warehouse"])

router.include_router(slots.router)
router.include_router(layout.router)
router.include_router(logistics.router)
router.include_router(agv.router)

__all__ = ["router"]
```

- [ ] **Step 2: Create routers/warehouse/slots.py**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
from pathlib import Path

from ...models.warehouse import Slot, WarehouseGroup, WarehouseDetail

router = APIRouter(prefix="/slots", tags=["warehouse/slots"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "warehouse"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SLOTS_FILE = DATA_DIR / "slots.json"
GROUPS_FILE = DATA_DIR / "groups.json"

def _load_slots() -> list[dict]:
    if SLOTS_FILE.exists():
        return json.loads(SLOTS_FILE.read_text())
    return []

def _save_slots(slots: list[dict]):
    SLOTS_FILE.write_text(json.dumps(slots, indent=2, ensure_ascii=False))

def _load_groups() -> list[dict]:
    if GROUPS_FILE.exists():
        return json.loads(GROUPS_FILE.read_text())
    # Default demo data
    return [{
        "id": "Ground Floor - DC",
        "name": "Ground Floor",
        "parent_id": "Main Campus - DC",
        "parent_name": "Main Campus",
        "slot_count": 0
    }]

def _save_groups(groups: list[dict]):
    GROUPS_FILE.write_text(json.dumps(groups, indent=2, ensure_ascii=False))

class SlotUpdate(BaseModel):
    warehouse_id: str
    label: str
    row: Optional[int] = None
    col: Optional[int] = None
    row_gap: Optional[float] = None

@router.get("/groups", response_model=list[dict])
async def get_groups():
    return _load_groups()

@router.get("", response_model=list[dict])
async def get_slots(group: Optional[str] = None):
    slots = _load_slots()
    if group:
        # Filter by group if needed
        pass
    return slots

@router.get("/{warehouse_id}", response_model=dict)
async def get_slot(warehouse_id: str):
    slots = _load_slots()
    for s in slots:
        if s.get("warehouse_id") == warehouse_id:
            return s
    raise HTTPException(status_code=404, detail="Slot not found")

@router.patch("/{warehouse_id}")
async def update_slot(warehouse_id: str, update: SlotUpdate):
    slots = _load_slots()
    for i, s in enumerate(slots):
        if s.get("warehouse_id") == warehouse_id:
            if update.label is not None:
                s["label"] = update.label
            if update.row is not None:
                s["row"] = update.row
            if update.col is not None:
                s["col"] = update.col
            if update.row_gap is not None:
                s["row_gap"] = update.row_gap
            slots[i] = s
            _save_slots(slots)
            return {"ok": True, "slot": s}
    raise HTTPException(status_code=404, detail="Slot not found")

class UOMCapacityUpdate(BaseModel):
    uom: str
    capacity: float

@router.patch("/{warehouse_id}/capacity")
async def update_capacity(warehouse_id: str, update: UOMCapacityUpdate):
    # Find and update capacity for a level
    slots = _load_slots()
    for s in slots:
        for lv in s.get("levels", []):
            if lv.get("warehouse_id") == warehouse_id:
                for u in lv.get("uoms", []):
                    if u.get("uom") == update.uom:
                        u["cap"] = update.capacity
                _save_slots(slots)
                return {"ok": True}
    return {"ok": True}  # Demo mode - acknowledge without persistence
```

- [ ] **Step 3: Create routers/warehouse/layout.py**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
from pathlib import Path

from ...models.warehouse import ShellBlueprint, FloorFull, Zone, Facility, Dock

router = APIRouter(prefix="/layout", tags=["warehouse/layout"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "warehouse"
DATA_DIR.mkdir(parents=True, exist_ok=True)

LAYOUT_DIR = DATA_DIR / "layout"
LAYOUT_DIR.mkdir(parents=True, exist_ok=True)

def _get_layout_file(floor: str) -> Path:
    return LAYOUT_DIR / f"{floor.replace('/', '_').replace(' ', '_')}.json"

@router.get("/floor/{floor}", response_model=dict)
async def get_floor(floor: str):
    layout_file = _get_layout_file(floor)
    if layout_file.exists():
        return json.loads(layout_file.read_text())
    # Return default demo layout
    return {
        "shell": {
            "bounds": {"w": 160, "d": 100},
            "walls": [
                {"x0": -80, "z0": -50, "x1": 80, "z1": -50, "h": 3.5},
                {"x0": -80, "z0": 50, "x1": 80, "z1": 50, "h": 3.5},
                {"x0": -80, "z0": -50, "x1": -80, "z1": 50, "h": 3.5},
                {"x0": 80, "z0": -50, "x1": 80, "z1": 50, "h": 3.5},
            ],
            "docks": [],
            "facilities": [],
            "corridors": [],
        },
        "zones": [{
            "ref": "RACK-LEGACY",
            "name": "货架仓储区",
            "type": "rack",
            "x": 0, "z": 0, "w": 40, "d": 40,
            "levels": 3
        }],
        "facilities": [],
        "docks": []
    }

@router.put("/shell/{floor}")
async def save_shell(floor: str, shell: dict):
    layout_file = _get_layout_file(floor)
    # Merge with existing layout
    if layout_file.exists():
        existing = json.loads(layout_file.read_text())
        existing["shell"] = shell
        layout_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
    else:
        layout_file.write_text(json.dumps({"shell": shell}, indent=2, ensure_ascii=False))
    return {"ok": True}
```

- [ ] **Step 4: Create routers/warehouse/logistics.py**

```python
from fastapi import APIRouter, Query
from typing import Optional
import json
from pathlib import Path
from datetime import datetime, timedelta

from ...models.warehouse import LogisticsTask, LogisticsStats, Dock, DockDetail

router = APIRouter(prefix="/logistics", tags=["warehouse/logistics"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "warehouse"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TASKS_FILE = DATA_DIR / "tasks.json"
DOCKS_FILE = DATA_DIR / "docks.json"

def _load_tasks() -> list[dict]:
    if TASKS_FILE.exists():
        return json.loads(TASKS_FILE.read_text())
    # Generate demo tasks
    tasks = []
    now = datetime.now()
    for i in range(15):
        t_type = ["inbound", "outbound", "transfer"][i % 3]
        days_ago = int(i * 0.7)
        date = (now - timedelta(days=days_ago)).isoformat().split("T")[0]
        tasks.append({
            "task_id": f"PR-{1000 + i:05d}" if t_type == "inbound" else f"DN-{2000 + i:05d}" if t_type == "outbound" else f"SE-{3000 + i:05d}",
            "task_type": t_type,
            "status": "completed",
            "source_dock": f"Dock {'A' if i % 2 == 0 else 'B'} - DC",
            "target_slot": f"A{(i % 5) + 1} - DC",
            "items": [{"item_code": f"ITM-{i + 1:04d}", "qty": 50 + i * 10}],
            "created_at": date
        })
    return tasks

def _save_tasks(tasks: list[dict]):
    TASKS_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False))

def _load_docks() -> list[dict]:
    if DOCKS_FILE.exists():
        return json.loads(DOCKS_FILE.read_text())
    return [
        {"name": "Dock A - DC", "warehouse_name": "Dock A", "parent_warehouse": "Ground Floor - DC", "slot_count": 3},
        {"name": "Dock B - DC", "warehouse_name": "Dock B", "parent_warehouse": "Ground Floor - DC", "slot_count": 2},
    ]

@router.get("/tasks", response_model=list[dict])
async def get_tasks(
    dock: Optional[str] = None,
    status: Optional[str] = None,
    date_range: Optional[str] = None
):
    tasks = _load_tasks()
    if dock:
        tasks = [t for t in tasks if t.get("source_dock") == dock or t.get("target_slot") == dock]
    if status and status != "all":
        tasks = [t for t in tasks if t.get("status") == status]
    return tasks

@router.get("/stats", response_model=dict)
async def get_stats(
    dock: Optional[str] = None,
    date_range: Optional[str] = None
):
    tasks = _load_tasks()
    if dock:
        tasks = [t for t in tasks if t.get("source_dock") == dock or t.get("target_slot") == dock]
    
    inbound = [t for t in tasks if t.get("task_type") == "inbound"]
    outbound = [t for t in tasks if t.get("task_type") == "outbound"]
    
    return {
        "total_inbound": len(inbound),
        "total_outbound": len(outbound),
        "avg_processing_time": 0,
        "dock_utilization": round(len(tasks) / 30, 2)
    }

@router.get("/docks", response_model=list[dict])
async def get_docks():
    return _load_docks()
```

- [ ] **Step 5: Create routers/warehouse/agv.py**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
from pathlib import Path

from ...models.warehouse import AGVGrid

router = APIRouter(prefix="/agv", tags=["warehouse/agv"])

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "warehouse"
DATA_DIR.mkdir(parents=True, exist_ok=True)

AGV_DIR = DATA_DIR / "agv"
AGV_DIR.mkdir(parents=True, exist_ok=True)

def _get_grid_file(group: str) -> Path:
    return AGV_DIR / f"{group.replace('/', '_').replace(' ', '_')}.json"

@router.get("/grid/{group}", response_model=dict)
async def get_grid(group: str):
    grid_file = _get_grid_file(group)
    if grid_file.exists():
        return json.loads(grid_file.read_text())
    # Return default empty grid
    return {
        "cellSize": 1.0,
        "originX": 0,
        "originZ": 0,
        "cols": 0,
        "rows": 0,
        "cells": [],
        "nodes": []
    }

@router.put("/grid/{group}")
async def save_grid(group: str, grid: dict):
    grid_file = _get_grid_file(group)
    grid_file.write_text(json.dumps(grid, indent=2, ensure_ascii=False))
    return {"ok": True}

class GridDeriveRequest(BaseModel):
    cell_size: float = 1.0
    margin: int = 2

@router.post("/grid/{group}/derive")
async def derive_grid(group: str, request: GridDeriveRequest):
    # Generate a default grid based on slots
    # Simplified - actual implementation would use slot positions
    return {
        "cellSize": request.cell_size,
        "originX": -20,
        "originZ": -20,
        "cols": 40,
        "rows": 40,
        "cells": [{"t": 1, "w": 1.0} for _ in range(1600)],
        "nodes": []
    }
```

- [ ] **Step 6: Modify main.py to register router**

Add to the imports section:
```python
from backend.routers.warehouse import router as warehouse_router
```

Add after app definition:
```python
app.include_router(warehouse_router)
```

- [ ] **Step 7: Commit**

```bash
git add simulation/backend/routers/warehouse/
git add simulation/backend/main.py
git commit -m "feat(warehouse): add FastAPI warehouse router"
```

---

## Phase 4: Frontend Integration

### Task 4.1: Create WarehouseView Component

**Files:**
- Create: `simulation/frontend/src/warehouse/components/WarehouseView.vue`
- Create: `simulation/frontend/src/warehouse/components/TopBar.vue`
- Create: `simulation/frontend/src/warehouse/components/BottomBar.vue`
- Create: `simulation/frontend/src/warehouse/components/Sidebar.vue`
- Create: `simulation/frontend/src/warehouse/components/DetailPanel.vue`
- Create: `simulation/frontend/src/warehouse/components/index.ts`

**Interfaces:**
- Consumes: Pinia store, ThreeEngine
- Produces: Main warehouse visualization view

- [ ] **Step 1: Create components/WarehouseView.vue**

```vue
<template>
  <div id="wt-app" :class="store.isDark ? 'dark' : 'light'">
    <Sidebar v-if="store.sidebarOpen" />
    <div id="wt-cw">
      <canvas id="wt-c"></canvas>
      <div v-if="store.loading" class="wt-loading">
        <div class="wt-spinner"></div>
        <div class="wt-loading-text">Loading warehouse data...</div>
      </div>
    </div>
    <TopBar />
    <BottomBar />
    <DetailPanel v-if="store.detailPanelOpen" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { store as warehouseStore } from '../store'
import { engine } from '../engine'
import { useWarehouseAPI } from '../composables/useWarehouseAPI'
import Sidebar from './Sidebar.vue'
import TopBar from './TopBar.vue'
import BottomBar from './BottomBar.vue'
import DetailPanel from './DetailPanel.vue'

const store = warehouseStore
const api = useWarehouseAPI()

let syncTimer: number | undefined

async function loadData() {
  store.loading = true
  try {
    await api.loadGroups()
  } finally {
    store.loading = false
  }
}

function handleResize() {
  // Handled by ResizeObserver in engine
}

onMounted(async () => {
  const canvas = document.getElementById('wt-c') as HTMLCanvasElement
  const cwEl = document.getElementById('wt-cw') as HTMLElement
  
  if (!canvas || !cwEl) return

  engine.init(canvas, cwEl, {
    isDark: store.isDark,
    showWalls: store.showWalls,
    showMarkings: store.showMarkings
  })

  engine.bindMouse(cwEl,
    (data, x, y) => {
      if (!data) {
        store.detailPanelOpen = false
        return
      }
      store.detailData = data
      store.detailPanelOpen = true
    },
    (data, wasSel, isDouble) => {
      if (data && data.slot) {
        if (isDouble) {
          // Open item modal
        } else {
          // Highlight and show detail
          if (wasSel) {
            store.detailPanelOpen = false
          } else {
            store.detailPanelOpen = true
          }
        }
      }
    }
  )

  await loadData()
  
  // Rebuild scene when slots change
  watch(() => store.slots, (slots) => {
    if (slots.length > 0) {
      engine.buildScene({ slots, floorFull: store.floorFull })
    }
  }, { deep: true })
})

onUnmounted(() => {
  if (syncTimer) clearInterval(syncTimer)
})
</script>

<style>
/* CSS will be migrated from wt3d-vue.js */
#wt-app {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--wt-bg, #0c0e14);
  font-family: -apple-system, "Inter", sans-serif;
  font-size: 12px;
  color: var(--wt-text, #fff);
  position: relative;
  overflow: hidden;
}

#wt-cw {
  flex: 1;
  position: relative;
  min-height: 0;
}

#wt-c {
  display: block;
  width: 100%;
  height: 100%;
}

.wt-loading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 12px;
  z-index: 5;
  background: rgba(0, 0, 0, 0.5);
}

.wt-spinner {
  width: 28px;
  height: 28px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: wtSpin 0.7s linear infinite;
}

@keyframes wtSpin {
  to { transform: rotate(360deg); }
}

.wt-loading-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}
</style>
```

- [ ] **Step 2: Create components/TopBar.vue**

```vue
<template>
  <div id="wt-top">
    <div id="wt-search-wrap">
      <span id="wt-search-ico">🔍</span>
      <input
        id="wt-search"
        type="text"
        v-model="searchQuery"
        :placeholder="t('search_placeholder')"
      />
    </div>
    
    <div id="wt-switcher">
      <div class="wt-sw-group">
        <button
          v-for="view in ['3d', '2d']"
          :key="view"
          :class="['wt-sw-btn', { act: store.curView === view }]"
          @click="store.curView = view"
        >
          {{ view === '3d' ? '3D' : '2D' }}
        </button>
      </div>
    </div>
    
    <div class="wt-pills">
      <div :class="['wt-pill', statsClass]">
        <span class="wt-pv">{{ store.hudStats.occ }}</span>
        <span class="wt-pl">{{ t('active') }}</span>
      </div>
      <div class="wt-pill">
        <span class="wt-pv">{{ store.hudStats.total }}</span>
        <span class="wt-pl">{{ t('bins') }}</span>
      </div>
    </div>
    
    <button class="wt-theme-btn" @click="toggleTheme">
      {{ store.isDark ? '☀️' : '🌙' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useWarehouseStore } from '../store'

const store = useWarehouseStore()
const searchQuery = ref('')

const statsClass = computed(() => {
  const ratio = store.hudStats.occ / (store.hudStats.total || 1)
  if (ratio >= 0.8) return 'full'
  if (ratio >= 0.5) return 'mid'
  return 'free'
})

const t = (key: string) => {
  const i18n: Record<string, Record<string, string>> = {
    zh: {
      search_placeholder: '搜索商品编码...',
      active: '在用',
      bins: '库位'
    },
    en: {
      search_placeholder: 'Search item code...',
      active: 'Active',
      bins: 'Bins'
    }
  }
  return i18n[store.lang]?.[key] || key
}

function toggleTheme() {
  store.isDark = !store.isDark
}
</script>

<style scoped>
#wt-top {
  position: absolute;
  top: 0;
  left: 148px;
  right: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  background: linear-gradient(to bottom, rgba(12, 14, 20, 0.97) 55%, transparent);
  z-index: 10;
}

#wt-search-wrap {
  position: relative;
  flex: 1;
  max-width: 280px;
}

#wt-search {
  width: 100%;
  height: 28px;
  border-radius: 7px;
  border: 1px solid var(--wt-border, rgba(255, 255, 255, 0.08));
  background: var(--wt-card, rgba(255, 255, 255, 0.04));
  color: var(--wt-text, #fff);
  font-size: 11px;
  padding: 0 28px;
  outline: none;
}

#wt-search-ico {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11px;
  color: var(--wt-text3, rgba(255, 255, 255, 0.3));
}

#wt-switcher {
  display: flex;
  align-items: center;
  gap: 6px;
}

.wt-sw-group {
  display: flex;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 2px;
  gap: 2px;
}

.wt-sw-btn {
  height: 24px;
  padding: 0 9px;
  border-radius: 5px;
  border: none;
  font-size: 10px;
  font-weight: 700;
  cursor: pointer;
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  transition: all 0.18s;
}

.wt-sw-btn.act {
  background: #3b82f6;
  color: #fff;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
}

.wt-pills {
  display: flex;
  gap: 5px;
  margin-left: auto;
}

.wt-pill {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 7px;
  padding: 3px 9px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 46px;
}

.wt-pv {
  font-size: 13px;
  font-weight: 800;
  line-height: 1.1;
  color: var(--wt-text, #fff);
}

.wt-pl {
  font-size: 8px;
  color: rgba(255, 255, 255, 0.35);
  font-weight: 600;
  letter-spacing: 0.4px;
  margin-top: 1px;
}

.wt-pill.occ .wt-pv { color: #fb923c }
.wt-pill.free .wt-pv { color: #4ade80 }
.wt-pill.full .wt-pv { color: #f87171 }

.wt-theme-btn {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.08);
  cursor: pointer;
  font-size: 13px;
}
</style>
```

- [ ] **Step 3: Create components/BottomBar.vue**

```vue
<template>
  <div id="wt-bot">
    <div id="wt-hint">
      Drag to rotate | Right-drag to pan | Scroll to zoom
    </div>
    <div id="wt-legend">
      <div class="wt-li">
        <span class="wt-lb" style="background: #4ade80"></span>
        <span>空闲</span>
      </div>
      <div class="wt-li">
        <span class="wt-lb" style="background: #fbbf24"></span>
        <span>使用中</span>
      </div>
      <div class="wt-li">
        <span class="wt-lb" style="background: #f87171"></span>
        <span>满载</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useWarehouseStore } from '../store'
const store = useWarehouseStore()
</script>

<style scoped>
#wt-bot {
  position: absolute;
  bottom: 0;
  left: 148px;
  right: 0;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 9px 14px;
  background: linear-gradient(to top, rgba(12, 14, 20, 0.97) 55%, transparent);
  z-index: 10;
}

#wt-hint {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.25);
  line-height: 1.8;
}

#wt-legend {
  display: flex;
  gap: 8px;
  align-items: center;
}

.wt-li {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 9px;
  color: rgba(255, 255, 255, 0.4);
}

.wt-lb {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}
</style>
```

- [ ] **Step 4: Create components/Sidebar.vue**

```vue
<template>
  <div id="wt-sb">
    <div class="wt-sb-brand">仓库导航</div>
    
    <div class="wt-sb-label">仓库组</div>
    <div
      v-for="group in store.groups"
      :key="group.id"
      :class="['wt-g-item', { act: store.curGroup?.id === group.id }]"
      @click="selectGroup(group)"
    >
      <span class="wt-g-name">{{ group.name }}</span>
      <span class="wt-g-meta">{{ group.slot_count }} slots</span>
    </div>
    
    <div class="wt-sb-foot">
      <button class="wt-sb-btn" @click="centerView">
        🎯 居中视图
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useWarehouseStore } from '../store'
import { useWarehouseAPI } from '../composables/useWarehouseAPI'
import { engine } from '../engine'

const store = useWarehouseStore()
const api = useWarehouseAPI()

async function selectGroup(group: any) {
  store.curGroup = group
  await api.loadSlots(group.id)
}

function centerView() {
  engine.centerView()
}
</script>

<style scoped>
#wt-sb {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 148px;
  background: rgba(10, 12, 18, 0.96);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  overflow-y: auto;
  z-index: 15;
  display: flex;
  flex-direction: column;
}

.wt-sb-brand {
  padding: 10px;
  font-size: 12px;
  font-weight: 800;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.wt-sb-label {
  padding: 9px 10px 2px;
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 1.2px;
  color: rgba(255, 255, 255, 0.3);
  text-transform: uppercase;
}

.wt-g-item {
  padding: 7px 10px;
  cursor: pointer;
  border-left: 3px solid transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  transition: background 0.1s;
}

.wt-g-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.wt-g-item.act {
  background: rgba(255, 255, 255, 0.06);
  border-left-color: #3b82f6;
}

.wt-g-name {
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  display: block;
}

.wt-g-item.act .wt-g-name {
  color: #60a5fa;
}

.wt-g-meta {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.3);
}

.wt-sb-foot {
  margin-top: auto;
  padding: 8px 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.wt-sb-btn {
  width: 100%;
  height: 28px;
  border-radius: 6px;
  border: 1px solid rgba(59, 130, 246, 0.4);
  background: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
  font-size: 10px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
</style>
```

- [ ] **Step 5: Create components/DetailPanel.vue**

```vue
<template>
  <div id="wt-dp" :class="{ open: store.detailPanelOpen }">
    <button id="wt-dp-x" @click="close">×</button>
    
    <template v-if="store.detailData?.slot">
      <div class="wt-dp-title">{{ store.detailData.slot.label }}</div>
      <div class="wt-dp-sub">{{ store.detailData.slot.warehouse_id }}</div>
      
      <span class="wt-dp-sec">层级</span>
      <div
        v-for="lv in store.detailData.slot.levels"
        :key="lv.warehouse_id"
        class="wt-dp-lv"
        :class="{ sel: selectedLevel?.warehouse_id === lv.warehouse_id }"
        @click="selectLevel(lv)"
      >
        <div class="wt-dp-lv-hdr">
          <span class="wt-dp-lv-name">{{ lv.label }}</span>
          <span class="wt-dp-lv-pct" :style="{ color: levelColor(lv) }">
            {{ levelPct(lv) }}%
          </span>
        </div>
        <div
          v-for="u in lv.uoms"
          :key="u.uom"
          class="wt-urow"
        >
          <span class="wt-ulbl">{{ u.uom }}</span>
          <div class="wt-utrack">
            <div class="wt-ufill" :style="{ width: Math.min(100, (u.qty / u.cap * 100)) + '%', background: u.qty > 0 ? '#4ade80' : '#374151' }"></div>
          </div>
          <span class="wt-uval">{{ u.qty }} / {{ u.cap }}</span>
        </div>
      </div>
      
      <template v-if="selectedLevel?.items?.length">
        <span class="wt-dp-items-lbl">物品</span>
        <div
          v-for="item in selectedLevel.items"
          :key="item.code"
          class="wt-dp-item"
        >
          <div>
            <div class="wt-dp-icode">{{ item.code }}</div>
            <div class="wt-dp-imeta">{{ item.name }}</div>
          </div>
          <span class="wt-dp-iqty">{{ item.qty }}</span>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useWarehouseStore } from '../store'

const store = useWarehouseStore()
const selectedLevel = ref<any>(null)

function close() {
  store.detailPanelOpen = false
}

function selectLevel(lv: any) {
  selectedLevel.value = lv
}

function levelPct(lv: any): number {
  const wc = (lv.uoms || []).filter((u: any) => u.cap > 0)
  if (!wc.length) return (lv.uoms || []).some((u: any) => u.qty > 0) ? 50 : 0
  return Math.round(wc.reduce((s: number, u: any) => s + Math.min(100, Math.round(u.qty / u.cap * 100)), 0) / wc.length)
}

function levelColor(lv: any): string {
  const p = levelPct(lv)
  return p >= 90 ? '#f87171' : p >= 70 ? '#fb923c' : p >= 40 ? '#facc15' : '#4ade80'
}
</script>

<style scoped>
#wt-dp {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 216px;
  background: rgba(19, 21, 30, 1);
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 20;
  overflow-y: auto;
  padding: 12px;
}

#wt-dp.open {
  transform: translateX(0);
}

#wt-dp-x {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 5px;
  color: rgba(255, 255, 255, 0.6);
  width: 22px;
  height: 22px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wt-dp-title {
  font-size: 13px;
  font-weight: 800;
  margin-bottom: 1px;
  padding-right: 26px;
  color: #fff;
}

.wt-dp-sub {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 12px;
}

.wt-dp-sec {
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 6px;
  display: block;
}

.wt-dp-lv {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 6px;
  cursor: pointer;
}

.wt-dp-lv.sel {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.08);
}

.wt-dp-lv-hdr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 5px;
}

.wt-dp-lv-name {
  font-size: 10px;
  font-weight: 700;
  color: #fff;
}

.wt-dp-lv-pct {
  font-size: 10px;
  font-weight: 800;
}

.wt-urow {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 4px;
}

.wt-ulbl {
  font-size: 8px;
  color: rgba(255, 255, 255, 0.6);
  min-width: 28px;
}

.wt-utrack {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
}

.wt-ufill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s;
}

.wt-uval {
  font-size: 8px;
  color: rgba(255, 255, 255, 0.6);
  min-width: 52px;
  text-align: right;
}

.wt-dp-items-lbl {
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.3);
  margin: 8px 0 5px;
  display: block;
}

.wt-dp-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 7px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 5px;
  margin-bottom: 3px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.wt-dp-icode {
  font-size: 9px;
  font-weight: 700;
  color: #60a5fa;
}

.wt-dp-imeta {
  font-size: 8px;
  color: rgba(255, 255, 255, 0.3);
  margin-top: 1px;
}

.wt-dp-iqty {
  font-size: 10px;
  font-weight: 800;
  color: #4ade80;
}
</style>
```

- [ ] **Step 6: Create components/index.ts**

```typescript
export { default as WarehouseView } from './WarehouseView.vue'
export { default as TopBar } from './TopBar.vue'
export { default as BottomBar } from './BottomBar.vue'
export { default as Sidebar } from './Sidebar.vue'
export { default as DetailPanel } from './DetailPanel.vue'
```

- [ ] **Step 7: Commit**

```bash
git add simulation/frontend/src/warehouse/components/
git commit -m "feat(warehouse): create main Vue components"
```

---

## Phase 5: Integration & Demo

### Task 5.1: Create Demo Entry Point

**Files:**
- Create: `simulation/frontend/src/warehouse/WarehouseDemo.vue`
- Create: `simulation/demo/warehouse-demo/index.html` (optional standalone demo)
- Modify: `simulation/frontend/src/router/index.ts`

**Interfaces:**
- Consumes: WarehouseView component
- Produces: Standalone demo page or integrated route

- [ ] **Step 1: Create demo integration**

```vue
<!-- This will be added to an existing page or used standalone -->
<template>
  <WarehouseView />
</template>

<script setup lang="ts">
import { WarehouseView } from './components'
</script>
```

- [ ] **Step 2: Add to router (optional)**

```typescript
// In router/index.ts
const routes = [
  // ... existing routes ...
  {
    path: '/warehouse',
    name: 'Warehouse',
    component: () => import('./warehouse/WarehouseDemo.vue')
  }
]
```

- [ ] **Step 3: Commit**

```bash
git add simulation/frontend/src/warehouse/
git commit -m "feat(warehouse): add demo integration"
```

---

## Implementation Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 1.1-1.3 | Project setup: directories, types, backend models |
| 2 | 2.1-2.3 | 3D engine: core, zones, store |
| 3 | 3.1 | Backend API: FastAPI router with all endpoints |
| 4 | 4.1 | Frontend integration: main components |
| 5 | 5.1 | Demo integration |

---

*Plan version: 1.0*  
*Last updated: 2026-08-20*
