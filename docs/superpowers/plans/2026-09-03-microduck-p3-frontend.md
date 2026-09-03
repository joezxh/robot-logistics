# Microduck Frontend Implementation Plan (P3 显示)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render the Microduck biped in the RCS frontend as a scene in the existing scene list, driven in real time by simulation telemetry (including freejoint translation/tilt).

**Architecture:** `MjcfLoader` is extended in two additive ways — an STL mesh loader (Microduck ships 43 STL meshes; the loader only had OBJLoader) and freejoint support (a 6-DOF joint carrying `pos` + `quat`, which is currently filtered out entirely). A new `SceneMicroduck.vue` (modelled on `RobotModelViewer.vue`) renders the model. Telemetry arrives as SSE from a stdlib-only dev server that steps `MicroduckEnv` and streams `qpos`.

**Tech Stack:** Vue 3 (script setup), TypeScript, three.js (OBJLoader + STLLoader), Vite, vitest (`npm test`), Python stdlib `http.server`

### Prerequisites

- **P1 + P2 must be complete** (plan `2026-09-03-microduck-p1-p2-backend.md`): assets at `simulation/backend/assets/robots/microduck/`, `rcs_env.envs.microduck.MicroduckEnv`, gym ID `rcs/microduck-walk-v0`.
- Frontend test command: `cd rcs/frontend && npm test` (vitest run).
- Dev server: `cd rcs/frontend && npm run dev` (Vite on 5173, `/sim-assets/*` already served from `simulation/backend/assets/*` and `.stl` already has a MIME entry).

### Verified facts (measured, do not re-derive)

- `vite.config.ts` MIME map **already contains** `'.stl': 'model/stl'` (line 18) — no change needed there.
- `MjcfLoader.ts` line 218 filters body children with `tagName === 'joint'`, so **`<freejoint>` is silently ignored** today.
- Mesh asset keys strip only `.obj` (lines 148 and 282) — must become extension-agnostic.
- `MjcfRobot` exposes `root`, `joints: Map<string, JointNode>`, `setJointAngle(name, rad)`, `getJointState()`, `loadMesh(file, baseUrl, meshdir)`.
- `robot_walk.xml` qpos layout: `[0:3]` base position, `[3:7]` base quaternion **wxyz**, `[7:21]` the 14 joints in `POLICY_JOINTS` order.
- `ScenesPage.vue` tabs are `pallet | box | bag`; `SceneStage.vue` switches on `sceneName` and calls `useSceneKPI(sceneName)`.
- There is **no existing frontend telemetry channel** for simulation (`TwinFeed.ts` no longer exists) and no SSE in the RCS backend — P3 creates one.

---

## File Structure

| File | Responsibility |
|---|---|
| `rcs/frontend/src/views/simulation/three/MjcfLoader.ts` | Add STLLoader dispatch + freejoint (6-DOF) support |
| `rcs/frontend/src/views/simulation/three/MjcfLoader.spec.ts` | Vitest coverage for STL + freejoint |
| `rcs/frontend/src/views/simulation/scenes/SceneMicroduck.vue` | **New** — renders the duck, joint sliders, consumes SSE |
| `rcs/frontend/src/views/simulation/scenes/SceneStage.vue` | Add `microduck` case + guard the warehouse-only KPI hook |
| `rcs/frontend/src/views/simulation/scenes/ScenesPage.vue` | Add the Microduck tab |
| `rcs/frontend/vite.config.ts` | Add `/sim` proxy to the SSE dev server |
| `rcs/frontend/src/views/simulation/three/microduckQpos.ts` | **New** — qpos → joint mapping shared by scene + tests |
| `simulation/backend/rcs_env/serve/microduck_stream.py` | **New** — stdlib SSE server streaming `qpos` |

---

### Task 1: STL mesh loading

**Files:**
- Modify: `rcs/frontend/src/views/simulation/three/MjcfLoader.ts:80,109-113,148,282`
- Test: `rcs/frontend/src/views/simulation/three/MjcfLoader.spec.ts`

- [ ] **Step 1: Write the failing test**

Append to `MjcfLoader.spec.ts`:

```ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import * as THREE from 'three'

// A 12-triangle STL (binary header + 1 triangle) is the smallest valid payload.
function makeBinaryStl(): ArrayBuffer {
  const buf = new ArrayBuffer(84 + 50)
  const view = new DataView(buf)
  // 80-byte header (zeros) + uint32 triangle count = 1
  view.setUint32(80, 1, true)
  // 1 triangle: normal(3x float32) + 3 vertices(3x float32) + uint16 attr
  let o = 84
  const floats = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
  for (const f of floats) { view.setFloat32(o, f, true); o += 4 }
  view.setUint16(o, 0, true)
  return buf
}

describe('MjcfLoader STL support', () => {
  beforeEach(() => {
    global.fetch = vi.fn(async (url: string) => {
      if (String(url).endsWith('.xml')) {
        const xml = `<mujoco model="stlbot">
          <compiler meshdir="assets"/>
          <asset><mesh name="body" file="body.stl"/></asset>
          <worldbody>
            <body name="base">
              <geom type="mesh" mesh="body" material="mat"/>
            </body>
          </worldbody>
        </mujoco>`
        return { ok: true, status: 200, text: async () => xml } as unknown as Response
      }
      if (String(url).endsWith('.stl')) {
        return {
          ok: true, status: 200,
          arrayBuffer: async () => makeBinaryStl(),
        } as unknown as Response
      }
      return { ok: false, status: 404, text: async () => '' } as unknown as Response
    })
  })

  it('loads an .stl mesh referenced by the MJCF', async () => {
    const robot = await MjcfLoader.load('/sim-assets/robots/stlbot/stlbot.xml', {
      baseUrl: '/sim-assets/robots/stlbot/stlbot.xml',
    })
    let meshes = 0
    robot.root.traverse((o) => { if ((o as THREE.Mesh).isMesh) meshes++ })
    expect(meshes).toBeGreaterThan(0)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd rcs/frontend && npm test -- MjcfLoader`
Expected: FAIL — the OBJLoader cannot parse the STL payload (mesh count 0 or parse error).

- [ ] **Step 3: Implement**

In `MjcfLoader.ts`:

1. Add the STLLoader import next to OBJLoader:

```ts
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
```

2. Add an extension-agnostic mesh-key helper (near `parseVec`), and use it for both
   the asset map (line 148) and the geom lookup (line 282):

```ts
/** Mesh assets are keyed by file name without a mesh extension. */
function meshKey(file: string): string {
  return file.replace(/\.(obj|stl)$/i, '')
}
```

Line 148 becomes:

```ts
      if (file) meshes.set(meshKey(file), { file })
```

Line 282 becomes:

```ts
      const asset = meshName ? ctx.meshes.get(meshKey(meshName)) : undefined
```

3. Replace `loadMesh` with an extension-aware version and add the loader field:

```ts
  private objLoader = new OBJLoader()
  private stlLoader = new STLLoader()

  /** Load a referenced mesh (.obj or .stl), cached by file name. */
  async loadMesh(file: string, baseUrl: string, meshdir: string): Promise<THREE.Object3D | null> {
    const url = new URL(meshdir ? `${meshdir}/${file}` : file, baseUrl).href
    if (/\.stl$/i.test(file)) {
      const geom = await this.stlLoader.loadAsync(url)
      geom.computeVertexNormals()
      // STL carries no material; the caller applies the MJCF <material>.
      return new THREE.Mesh(geom, new THREE.MeshStandardMaterial({ color: 0xcccccc }))
    }
    return await this.objLoader.loadAsync(url)
  }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd rcs/frontend && npm test -- MjcfLoader`
Expected: PASS (including the pre-existing OBJ tests — no regression).

- [ ] **Step 5: Commit**

```bash
git add rcs/frontend/src/views/simulation/three/MjcfLoader.ts rcs/frontend/src/views/simulation/three/MjcfLoader.spec.ts
git commit -m "feat(frontend): MjcfLoader supports STL meshes (P3)"
```

---

### Task 2: freejoint (6-DOF) support

**Files:**
- Modify: `rcs/frontend/src/views/simulation/three/MjcfLoader.ts:38-46,88-97,215-236`
- Test: `rcs/frontend/src/views/simulation/three/MjcfLoader.spec.ts`

- [ ] **Step 1: Write the failing tests**

```ts
describe('MjcfLoader freejoint support', () => {
  beforeEach(() => {
    global.fetch = vi.fn(async () => {
      const xml = `<mujoco model="duck">
        <worldbody>
          <body name="trunk">
            <freejoint name="trunk_base_freejoint"/>
            <geom type="box" size="0.1 0.1 0.1"/>
            <body name="thigh">
              <joint name="left_knee" type="hinge" axis="0 1 0" range="-1 1"/>
              <geom type="box" size="0.05 0.05 0.05"/>
            </body>
          </body>
        </worldbody>
      </mujoco>`
      return { ok: true, status: 200, text: async () => xml } as unknown as Response
    })
  })

  it('registers the freejoint as a 6-DOF joint', async () => {
    const robot = await MjcfLoader.load('/duck.xml', { baseUrl: '/duck.xml' })
    const j = robot.joints.get('trunk_base_freejoint')
    expect(j).toBeDefined()
    expect(j!.type).toBe('free')
  })

  it('moves and rotates the robot root via setFreeJointPose', async () => {
    const robot = await MjcfLoader.load('/duck.xml', { baseUrl: '/duck.xml' })
    robot.setFreeJointPose('trunk_base_freejoint', [1, 2, 3], [1, 0, 0, 0])
    const j = robot.joints.get('trunk_base_freejoint')!
    expect(j.group.position.toArray()).toEqual([1, 2, 3])
    // rotation unchanged: identity quaternion
    expect(j.group.quaternion.toArray()).toEqual([0, 0, 0, 1])

    // 90 deg about Z: (w=cos45, x=0, y=0, z=sin45)
    const s = Math.SQRT1_2
    robot.setFreeJointPose('trunk_base_freejoint', [0, 0, 0], [s, 0, 0, s])
    const q = j.group.quaternion
    expect(q.x).toBeCloseTo(0)
    expect(q.z).toBeCloseTo(s)
  })

  it('leaves hinge joints working after the change', async () => {
    const robot = await MjcfLoader.load('/duck.xml', { baseUrl: '/duck.xml' })
    robot.setJointAngle('left_knee', 0.5)
    expect(robot.getJointState()['left_knee']).toBeCloseTo(0.5)
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd rcs/frontend && npm test -- MjcfLoader`
Expected: FAIL — `trunk_base_freejoint` is not in `robot.joints`; `setFreeJointPose` is not a function.

- [ ] **Step 3: Implement**

1. Extend `JointNode` with a joint type:

```ts
interface JointNode {
  name: string
  group: THREE.Group
  type: 'hinge' | 'slide' | 'free'
  axis: THREE.Vector3
  range: [number, number] | null
  qpos0: number
  /** Last applied angle (radians), for read-back via getJointState(). */
  applied: number
}
```

2. Add the freejoint setter to `MjcfRobot` (after `setJointAngle`):

```ts
  /**
   * Set a freejoint's pose: 6-DOF base transform.
   * @param pos  world position [x, y, z]
   * @param quat MuJoCo quaternion [w, x, y, z] (three.js uses [x, y, z, w])
   */
  setFreeJointPose(name: string, pos: [number, number, number], quat: [number, number, number, number]): void {
    const j = this.joints.get(name)
    if (!j) return
    if (j.type !== 'free') {
      throw new Error(`MjcfRobot: '${name}' is a ${j.type} joint, not a freejoint`)
    }
    j.group.position.set(pos[0], pos[1], pos[2])
    j.group.quaternion.set(quat[1], quat[2], quat[3], quat[0])
    j.applied = 0
  }
```

3. Make `setJointAngle` refuse free joints (a free joint has no single axis):

```ts
  setJointAngle(name: string, rad: number): void {
    const j = this.joints.get(name)
    if (!j || j.type === 'free') return
    ...
  }
```

4. In the body walk (`MjcfLoader.ts:216-239`), accept `<freejoint>` in the child filter
   and branch on the joint type. Replace lines 216-239 with:

```ts
    // joints -> pivot groups (a body may have 0..n joints; typically 1).
    // <freejoint> is 6-DOF: it drives the pivot group's position and quaternion
    // instead of a single-axis rotation.
    const jointEls = Array.from(bodyEl.children).filter(
      (c) => c.tagName.toLowerCase() === 'joint' || c.tagName.toLowerCase() === 'freejoint',
    )
    let attachUnder: THREE.Object3D = bodyGroup
    for (const je of jointEls) {
      const isFree = je.tagName.toLowerCase() === 'freejoint'
      const jg = new THREE.Group()
      jg.name = `joint:${je.getAttribute('name') || 'j'}`
      const axisRaw = parseVec(je.getAttribute('axis'))
      const axisVec = axisRaw.length === 3
        ? new THREE.Vector3(axisRaw[0], axisRaw[1], axisRaw[2]).normalize()
        : new THREE.Vector3(0, 1, 0)
      const rangeAttr = je.getAttribute('range')
      const range = parseVec(rangeAttr)
      const joint: JointNode = {
        name: je.getAttribute('name') || '',
        group: jg,
        type: isFree ? 'free' : 'hinge',
        axis: axisVec,
        // a freejoint has no scalar range and no single rotation axis
        range: !isFree && range.length === 2 ? [range[0], range[1]] : null,
        qpos0: 0,
        applied: 0,
      }
      if (joint.name) robot.joints.set(joint.name, joint)
      attachUnder.add(jg)
      attachUnder = jg
    }
```

The existing pivot-`Group` nesting (`attachUnder`) is unchanged — the freejoint simply
drives that group's `position`/`quaternion` instead of an axis-angle rotation.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd rcs/frontend && npm test -- MjcfLoader`
Expected: PASS (all STL + freejoint + pre-existing OBJ tests).

- [ ] **Step 5: Commit**

```bash
git add rcs/frontend/src/views/simulation/three/MjcfLoader.ts rcs/frontend/src/views/simulation/three/MjcfLoader.spec.ts
git commit -m "feat(frontend): MjcfLoader supports freejoint 6-DOF pose (P3)"
```

---

### Task 3: qpos → joint mapping helper

**Files:**
- Create: `rcs/frontend/src/views/simulation/three/microduckQpos.ts`
- Test: `rcs/frontend/src/views/simulation/three/microduckQpos.spec.ts`

- [ ] **Step 1: Write the failing test**

```ts
import { describe, it, expect } from 'vitest'
import { POLICY_JOINTS, applyQpos, MICRODUCK_QPOS_LAYOUT } from './microduckQpos'

describe('applyQpos', () => {
  it('splits qpos into base pose and 14 joint angles', () => {
    const q = new Array(21).fill(0)
    q[2] = 0.26            // trunk height
    q[3] = 1               // quat w
    for (let i = 0; i < 14; i++) q[7 + i] = i / 100

    const applied: Record<string, number> = {}
    let pose: { pos: number[]; quat: number[] } | null = null
    const robot = {
      setJointAngle: (n: string, v: number) => { applied[n] = v },
      setFreeJointPose: (n: string, p: [number,number,number], qu: [number,number,number,number]) => {
        pose = { pos: p, quat: qu }
      },
    }
    applyQpos(robot as never, q)
    expect(pose).not.toBeNull()
    expect(pose!.pos).toEqual([0, 0, 0.26])
    expect(pose!.quat).toEqual([1, 0, 0, 0])
    expect(Object.keys(applied)).toHaveLength(14)
    expect(applied['left_hip_yaw']).toBeCloseTo(0)
    expect(applied['right_ankle']).toBeCloseTo(0.13)
  })

  it('rejects a qpos of the wrong length', () => {
    expect(() => applyQpos({} as never, new Array(20).fill(0))).toThrow()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd rcs/frontend && npm test -- microduckQpos`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement `microduckQpos.ts`**

```ts
/**
 * Mapping from Microduck MuJoCo `qpos` to MjcfRobot joint commands.
 *
 * qpos layout (verified against robot_walk.xml):
 *   [0:3]   freejoint position  (x, y, z)
 *   [3:7]   freejoint quaternion (w, x, y, z) — MuJoCo order
 *   [7:21]  the 14 policy joints, in POLICY_JOINTS order
 */
import type { MjcfRobot } from './MjcfLoader'

export const POLICY_JOINTS: readonly string[] = [
  'left_hip_yaw', 'left_hip_roll', 'left_hip_pitch', 'left_knee', 'left_ankle',
  'neck_pitch', 'head_pitch', 'head_yaw', 'head_roll',
  'right_hip_yaw', 'right_hip_roll', 'right_hip_pitch', 'right_knee', 'right_ankle',
] as const

export const FREE_JOINT_NAME = 'trunk_base_freejoint'
export const MICRODUCK_QPOS_LAYOUT = { pos: 0, quat: 3, joints: 7, length: 21 } as const

export function applyQpos(robot: MjcfRobot, qpos: ArrayLike<number>): void {
  const q = Array.from(qpos)
  if (q.length !== MICRODUCK_QPOS_LAYOUT.length) {
    throw new Error(`applyQpos: expected ${MICRODUCK_QPOS_LAYOUT.length} values, got ${q.length}`)
  }
  robot.setFreeJointPose(
    FREE_JOINT_NAME,
    [q[0], q[1], q[2]],
    [q[3], q[4], q[5], q[6]],
  )
  POLICY_JOINTS.forEach((name, i) => {
    robot.setJointAngle(name, q[MICRODUCK_QPOS_LAYOUT.joints + i])
  })
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd rcs/frontend && npm test -- microduckQpos`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add rcs/frontend/src/views/simulation/three/microduckQpos.ts rcs/frontend/src/views/simulation/three/microduckQpos.spec.ts
git commit -m "feat(frontend): Microduck qpos -> joint mapping helper (P3)"
```

---

### Task 4: `SceneMicroduck.vue`

**Files:**
- Create: `rcs/frontend/src/views/simulation/scenes/SceneMicroduck.vue`

- [ ] **Step 1: Implement the scene component**

Modelled on `RobotModelViewer.vue` (same three.js setup), but with a ground grid and
a live telemetry toggle:

```vue
<script setup lang="ts">
/**
 * Microduck scene: renders the vendored MJCF through MjcfLoader and, when the
 * SSE stream is enabled, drives all 14 joints + the freejoint base pose from
 * simulation telemetry at ~50 Hz.
 */
import { onMounted, onUnmounted, ref, shallowRef } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { MjcfLoader, type MjcfRobot } from '../three/MjcfLoader'
import { applyQpos, POLICY_JOINTS } from '../three/microduckQpos'

const MODEL_URL = '/sim-assets/robots/microduck/robot_walk.xml'
const STREAM_URL = '/sim/stream'

const canvas = ref<HTMLCanvasElement | null>(null)
const status = ref('loading…')
const live = ref(false)
const joints = ref<{ name: string; value: number }[]>([])

let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let controls: OrbitControls | null = null
let raf = 0
let source: EventSource | null = null
const robot = shallowRef<MjcfRobot | null>(null)

function loop() {
  raf = requestAnimationFrame(loop)
  controls?.update()
  if (canvas.value && renderer && scene && camera) renderer.render(scene, camera)
}

async function load() {
  try {
    const r = await MjcfLoader.load(MODEL_URL, { baseUrl: MODEL_URL, showCollision: false })
    robot.value = r
    scene?.add(r.root)

    const box = new THREE.Box3().setFromObject(r.root)
    const size = box.getSize(new THREE.Vector3()).length() || 1
    const center = box.getCenter(new THREE.Vector3())
    camera?.position.set(center.x + size * 0.9, center.y + size * 0.6, center.z + size * 0.9)
    camera?.lookAt(center)
    if (controls) controls.target.copy(center)

    joints.value = POLICY_JOINTS.map((name) => ({ name, value: 0 }))
    status.value = `loaded: ${r.modelName} (${r.joints.size} joints)`
  } catch (e) {
    status.value = `error: ${(e as Error).message}`
    console.error(e)
  }
}

function onJointInput() {
  const r = robot.value
  if (!r || live.value) return
  for (const j of joints.value) r.setJointAngle(j.name, j.value)
}

function toggleLive() {
  live.value = !live.value
  if (live.value) startStream()
  else stopStream()
}

function startStream() {
  stopStream()
  source = new EventSource(STREAM_URL)
  source.onmessage = (ev) => {
    const r = robot.value
    if (!r) return
    const q = (JSON.parse(ev.data) as { qpos: number[] }).qpos
    applyQpos(r, q)
  }
  source.onerror = () => {
    status.value = 'stream error (is the SSE server running?)'
    live.value = false
    stopStream()
  }
}

function stopStream() {
  source?.close()
  source = null
}

function resize() {
  if (!canvas.value || !renderer || !camera) return
  const w = canvas.value.clientWidth
  const h = canvas.value.clientHeight
  renderer.setSize(w, h, false)
  camera.aspect = w / h
  camera.updateProjectionMatrix()
}

onMounted(async () => {
  if (!canvas.value) return
  renderer = new THREE.WebGLRenderer({ canvas: canvas.value, antialias: true })
  renderer.setPixelRatio(window.devicePixelRatio)
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0f1520)
  camera = new THREE.PerspectiveCamera(45, 1, 0.01, 100)
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true

  scene.add(new THREE.HemisphereLight(0xffffff, 0x222233, 1.0))
  const dir = new THREE.DirectionalLight(0xffffff, 1.2)
  dir.position.set(1, 2, 1)
  scene.add(dir)
  // Ground grid so freejoint translation/tilt is visible.
  const grid = new THREE.GridHelper(4, 40, 0x334155, 0x1e293b)
  scene.add(grid)

  window.addEventListener('resize', resize)
  resize()
  await load()
  loop()
})

onUnmounted(() => {
  cancelAnimationFrame(raf)
  stopStream()
  window.removeEventListener('resize', resize)
  renderer?.dispose()
})
</script>

<template>
  <div class="microduck-scene">
    <div class="toolbar">
      <span class="status">{{ status }}</span>
      <button :class="{ on: live }" @click="toggleLive">
        {{ live ? '■ 停止遥测' : '▶ 实时遥测' }}
      </button>
    </div>
    <canvas ref="canvas" class="view" />
    <div class="sliders">
      <label v-for="j in joints" :key="j.name">
        <span>{{ j.name }}</span>
        <input
          v-model.number="j.value"
          type="range" min="-1.5" max="1.5" step="0.01"
          :disabled="live"
          @input="onJointInput"
        />
      </label>
    </div>
  </div>
</template>

<style scoped>
.microduck-scene { display: flex; flex-direction: column; height: 100%; gap: 8px; }
.toolbar { display: flex; align-items: center; gap: 12px; }
.status { font-size: 12px; color: var(--fg-soft); }
.toolbar button {
  background: var(--bg-card-alt); border: 1px solid var(--border); color: var(--fg);
  padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 12px;
}
.toolbar button.on { background: var(--accent); color: #fff; border-color: var(--accent); }
.view { flex: 1; width: 100%; min-height: 0; border-radius: 8px; }
.sliders { max-height: 150px; overflow-y: auto; display: grid; grid-template-columns: 1fr 1fr; gap: 4px 12px; }
.sliders label { display: flex; align-items: center; gap: 8px; font-size: 11px; }
.sliders span { min-width: 120px; color: var(--fg-soft); }
.sliders input { flex: 1; }
</style>
```

- [ ] **Step 2: Type-check**

Run: `cd rcs/frontend && npx vue-tsc --noEmit`
Expected: no new errors.

- [ ] **Step 3: Commit**

```bash
git add rcs/frontend/src/views/simulation/scenes/SceneMicroduck.vue
git commit -m "feat(frontend): add SceneMicroduck viewer with live telemetry toggle (P3)"
```

---

### Task 5: Register the scene

**Files:**
- Modify: `rcs/frontend/src/views/simulation/scenes/SceneStage.vue:41-58`
- Modify: `rcs/frontend/src/views/simulation/scenes/ScenesPage.vue:37-56`

- [ ] **Step 1: Extend `SceneStage.vue`**

Change the prop union and add the case:

```ts
interface Props {
  sceneName: 'pallet' | 'box' | 'bag' | 'microduck'
}
const props = defineProps<Props>()

const sceneComponent = computed(() => {
  switch (props.sceneName) {
    case 'pallet':
      return () => import('./ScenePallet.vue')
    case 'box':
      return () => import('./SceneBox.vue')
    case 'bag':
      return () => import('./SceneBag.vue')
    case 'microduck':
      return () => import('./SceneMicroduck.vue')
    default:
      return null
  }
})
```

Guard the warehouse-only KPI hook so the Microduck tab does not poll a
non-existent KPI endpoint:

```ts
const isWarehouseScene = computed(() => props.sceneName !== 'microduck')
const { kpi, start: startKpi, stop: stopKpi } = useSceneKPI(props.sceneName)

onMounted(() => { if (isWarehouseScene.value) startKpi() })
onUnmounted(() => { if (isWarehouseScene.value) stopKpi() })
```

And hide the KPI panel for non-warehouse scenes by changing `v-if="kpi"` to
`v-if="isWarehouseScene && kpi"`.

- [ ] **Step 2: Add the tab in `ScenesPage.vue`**

```ts
interface TabSpec {
  name: 'pallet' | 'box' | 'bag' | 'microduck'
  label: string
}

const tabs: TabSpec[] = [
  { name: 'pallet', label: '📦 托盘 (🥇)' },
  { name: 'box', label: '📦 箱装 (🥈)' },
  { name: 'bag', label: '📦 袋装 (🥉)' },
  { name: 'microduck', label: '🦆 Microduck' },
]

const currentTab = ref<'' | 'pallet' | 'box' | 'bag' | 'microduck'>('pallet')
```

and widen `onSwitch(name: 'pallet' | 'box' | 'bag' | 'microduck')`.

- [ ] **Step 3: Type-check**

Run: `cd rcs/frontend && npx vue-tsc --noEmit`
Expected: no new errors.

- [ ] **Step 4: Commit**

```bash
git add rcs/frontend/src/views/simulation/scenes/SceneStage.vue rcs/frontend/src/views/simulation/scenes/ScenesPage.vue
git commit -m "feat(frontend): register Microduck scene tab (P3)"
```

---

### Task 6: SSE telemetry (stdlib, no new dependencies)

**Files:**
- Create: `simulation/backend/rcs_env/serve/microduck_stream.py`
- Create: `simulation/backend/rcs_env/serve/__init__.py`
- Modify: `rcs/frontend/vite.config.ts` (add `/sim` proxy)

- [ ] **Step 1: Implement the SSE server**

```python
"""Dev-only SSE server that steps MicroduckEnv and streams qpos.

Stdlib only (fastapi/uvicorn are not installed in the sim venv). Run with:

    PYTHONPATH=<repo>/simulation/backend \
      <repo>/simulation/backend/rcs_sim_core/.venv/Scripts/python.exe \
      -m rcs_env.serve.microduck_stream --port 8110
"""
from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np


def _make_env(variant: str, hz: float):
    from rcs_env.envs.microduck import MicroduckEnv

    env = MicroduckEnv(variant=variant)
    env.reset(seed=0)
    return env, 1.0 / hz


class Handler(BaseHTTPRequestHandler):
    variant = "walk"
    hz = 50.0

    def do_GET(self) -> None:  # noqa: N802
        if not self.path.startswith("/stream"):
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        env, period = _make_env(self.variant, self.hz)
        # A slow sinusoidal command makes the base translate/tilt visibly,
        # proving the freejoint path works (not just joint wiggling).
        try:
            t = 0.0
            while True:
                action = np.zeros(14, dtype=float)
                action[0] = 0.3 * np.sin(t)  # left hip yaw sweep
                env.step(action)
                qpos = env.engine.qpos()
                payload = json.dumps({"qpos": [float(v) for v in qpos]})
                self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                self.wfile.flush()
                t += period
                time.sleep(period)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *args) -> None:  # silence per-request logging
        return


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8110)
    ap.add_argument("--variant", default="walk")
    ap.add_argument("--hz", type=float, default=50.0)
    args = ap.parse_args()
    Handler.variant = args.variant
    Handler.hz = args.hz
    print(f"[microduck-stream] http://localhost:{args.port}/stream  variant={args.variant}")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Add the Vite proxy**

In `rcs/frontend/vite.config.ts`, add before the catch-all `/api` entry (order matters):

```ts
      '/sim': {
        target: 'http://localhost:8110',
        changeOrigin: true,
      },
```

- [ ] **Step 3: Start the server and verify the stream**

```powershell
$env:PYTHONPATH = "d:/projects/robot-logic/simulation/backend"
& d:/projects/robot-logic/simulation/backend/rcs_sim_core/.venv/Scripts/python.exe `
  -m rcs_env.serve.microduck_stream --port 8110
```

In another shell:

```powershell
(Invoke-WebRequest -Uri "http://localhost:8110/stream" -TimeoutSec 3).RawContent
```

Expected: repeated `data: {"qpos": [...]}` lines with 21 values each.

- [ ] **Step 4: Commit**

```bash
git add simulation/backend/rcs_env/serve rcs/frontend/vite.config.ts
git commit -m "feat(microduck): SSE qpos stream server + vite proxy (P3)"
```

---

### Task 7: Browser verification (P3 acceptance)

- [ ] **Step 1: Start both servers**

```powershell
# terminal 1 — SSE stream
$env:PYTHONPATH = "d:/projects/robot-logic/simulation/backend"
& d:/projects/robot-logic/simulation/backend/rcs_sim_core/.venv/Scripts/python.exe `
  -m rcs_env.serve.microduck_stream --port 8110

# terminal 2 — frontend
cd d:/projects/robot-logic/rcs/frontend
npm run dev
```

- [ ] **Step 2: Verify**

Open `http://localhost:5173/simulation/scenes`, click the **🦆 Microduck** tab.

Acceptance checklist:
1. The duck renders (43 STL meshes visible, not a bare primitive soup).
2. Status reads `loaded: ... (15 joints)` — 14 hinges + 1 freejoint.
3. Dragging a joint slider rotates that joint (hinge path works).
4. Clicking **▶ 实时遥测** makes the duck move **and** translate/tilt as a whole
   (this is the freejoint path — if it only wiggles in place, the freejoint is broken).
5. No console errors.

- [ ] **Step 3: Commit a short verification note**

```bash
git commit --allow-empty -m "chore(microduck): P3 browser verification passed"
```

---

## Self-Review Notes

- **Spec coverage**: §6.1 scene embedded in the existing list (T5), §6.2.1 STLLoader (T1), §6.2.2 freejoint (T2), §6.3 real-time telemetry (T6/T7). §7.2's 15-slot mapping is a backend/ONNX concern and is already covered by the P1–P2 plan's tests; the frontend applies the 14 policy joints directly.
- **Deliberate simplification**: the SSE server drives the env with a scripted sinusoid rather than a trained policy, because P3 only needs to prove the render + telemetry path. Real policy playback arrives in P5 (ONNX import), which reuses this exact stream.
- **Known gap**: `SceneMicroduck.vue` hardcodes `robot_walk.xml`. Variant switching (the other 6 MJCFs) is not in P3; add it in P5 alongside the policy selector.
- **No regression**: `MjcfLoader` changes are additive (new loader branch, new joint type, new method); the full vitest suite must stay green.
