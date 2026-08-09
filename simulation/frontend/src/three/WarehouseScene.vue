<template>
  <div class="wrap">
    <div ref="container" class="warehouse"></div>
    <div class="hud" @click.stop>
      <button class="hud-btn" :title="t.scene.pause" @click="togglePause">
        {{ paused ? '▶' : '⏸' }}
      </button>
      <button class="hud-btn" :title="t.scene.reset" @click="reset">⟲</button>
      <label class="hud-speed" :title="t.scene.speed">
        <span class="lbl">{{ t.scene.speed }}</span>
        <input type="range" min="0.25" max="3" step="0.25" v-model.number="speed" />
        <span class="val">{{ speed.toFixed(2) }}×</span>
      </label>
      <label class="hud-auto">
        <input type="checkbox" v-model="autoRotate" />
        <span>{{ t.scene.auto_rotate }}</span>
      </label>
      <button
        v-if="followTarget"
        class="hud-btn follow"
        :title="`Following ${followTarget}`"
        @click="followTarget = ''"
      >📍 {{ followTarget }} ×</button>
    </div>
    <div class="legend">
      <span><span class="dot running"></span>运行</span>
      <span><span class="dot idle"></span>空闲</span>
      <span><span class="dot charging"></span>充电</span>
      <span><span class="dot fault"></span>故障</span>
      <span class="hint">◯ 目标点</span>
      <span class="hint">▭ 月台 / 仓库</span>
    </div>
    <div class="sitecount">{{ dockCount }} docks · {{ rackCount }} racks · {{ deviceCount }} devices</div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, defineExpose, computed } from 'vue'
import * as THREE from 'three'
import axios from 'axios'
import { useI18n } from '../i18n'
import { info, success } from '../composables/toast'
import { RobotArm } from './RobotArm'
import { LoaderRobot } from './LoaderRobot'

const { t } = useI18n()

const container = ref<HTMLDivElement | null>(null)
let renderer: THREE.WebGLRenderer | undefined
let scene: THREE.Scene | undefined
let camera: THREE.PerspectiveCamera | undefined
let animationId: number | undefined
let resizeObserver: ResizeObserver | undefined

const deviceMeshes: Record<string, THREE.Mesh> = {}
const deviceTrails: Record<string, THREE.Line> = {}
const deviceTargets: Record<string, THREE.Mesh> = {}
const siteMeshes: Record<string, THREE.Group> = {}
let robotArm: RobotArm | undefined
let loaderRobot: LoaderRobot | undefined
let jointEventSource: EventSource | undefined
let loaderJointEventSource: EventSource | undefined
const statusColors: Record<string, number> = {
  idle: 0x5b6478,
  running: 0x1f8a4c,
  charging: 0x5eb0ff,
  fault: 0xc0392b,
}

const paused = ref(false)
const speed = ref(1)
const autoRotate = ref(true)
const followTarget = ref('')
const dockCount = ref(0)
const rackCount = ref(0)
const deviceCount = ref(0)

function init() {
  if (!container.value) return
  const w = container.value.clientWidth
  const h = container.value.clientHeight

  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0b1220)
  scene.fog = new THREE.Fog(0x0b1220, 30, 50)

  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100)
  camera.position.set(0, 18, 22)
  camera.lookAt(0, 0, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(w, h)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.value.appendChild(renderer.domElement)

  scene.add(new THREE.AmbientLight(0xffffff, 0.5))
  const directional = new THREE.DirectionalLight(0xffffff, 0.9)
  directional.position.set(10, 20, 10)
  scene.add(directional)
  const fill = new THREE.PointLight(0x5eb0ff, 0.4, 40)
  fill.position.set(-5, 5, -5)
  scene.add(fill)

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(36, 24),
    new THREE.MeshStandardMaterial({ color: 0x152238, roughness: 0.9 })
  )
  ground.rotation.x = -Math.PI / 2
  scene.add(ground)

  const grid = new THREE.GridHelper(36, 36, 0x2a3f5f, 0x1a2640)
  ;(grid.material as THREE.Material).opacity = 0.4
  ;(grid.material as THREE.Material).transparent = true
  grid.position.y = 0.01
  scene.add(grid)

  // ResizeObserver is more robust than window resize for layout-driven sizing.
  if ('ResizeObserver' in window) {
    resizeObserver = new ResizeObserver(onResize)
    resizeObserver.observe(container.value)
  } else {
    window.addEventListener('resize', onResize)
  }

  // Robot arm (Phase 1: procedural geometry)
  robotArm = new RobotArm()
  robotArm.addToScene(scene, new THREE.Vector3(-6, 0, 5))  // near dock area

  // Loader robot (Phase 1: dual-arm AGV)
  loaderRobot = new LoaderRobot()
  loaderRobot.addToScene(scene, new THREE.Vector3(-3, 0, 0))

  // SSE subscription for joint updates
  jointEventSource = new EventSource('/api/devices/robot-01/joints')
  jointEventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.positions && robotArm) {
        robotArm.setJointPositions(data.positions)
        robotArm.setStatus('moving')
      }
    } catch { /* ignore parse errors */ }
  }

  // SSE subscription for loader-01 joint updates
  loaderJointEventSource = new EventSource('/api/devices/loader-01/joints')
  loaderJointEventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.positions && loaderRobot) {
        loaderRobot.setJointPositions(data.positions)
      }
    } catch { /* ignore parse errors */ }
  }
}

function onResize() {
  if (!container.value || !renderer || !camera) return
  const w = container.value.clientWidth
  const h = container.value.clientHeight
  renderer.setSize(w, h)
  camera.aspect = w / h
  camera.updateProjectionMatrix()
}

interface DeviceSnapshot {
  device_id: string
  device_type?: string
  position: [number, number, number]
  status: string
  route?: [number, number, number][]
}

interface SiteSnapshot {
  id: string
  kind: 'dock' | 'warehouse'
  name: string
  position: [number, number, number]
  width: number
  height: number
  depth: number
  rotation: number
  color: string
  status: string
}

function ensureDeviceMesh(id: string): THREE.Mesh {
  let mesh = deviceMeshes[id]
  if (!mesh) {
    mesh = new THREE.Mesh(
      new THREE.BoxGeometry(0.9, 0.9, 0.9),
      new THREE.MeshStandardMaterial({ color: statusColors.idle, emissive: 0x000000 })
    )
    scene?.add(mesh)
    deviceMeshes[id] = mesh

    const trailGeom = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()])
    const trailMat = new THREE.LineDashedMaterial({
      color: 0x5eb0ff, dashSize: 0.3, gapSize: 0.2, transparent: true, opacity: 0.7,
    })
    const trail = new THREE.Line(trailGeom, trailMat)
    trail.computeLineDistances()
    scene?.add(trail)
    deviceTrails[id] = trail

    const ringGeom = new THREE.RingGeometry(0.45, 0.65, 24)
    const ringMat = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide, transparent: true, opacity: 0.7 })
    const ring = new THREE.Mesh(ringGeom, ringMat)
    ring.rotation.x = -Math.PI / 2
    ring.visible = false
    scene?.add(ring)
    deviceTargets[id] = ring
  }
  return mesh
}

function buildSiteGroup(site: SiteSnapshot): THREE.Group {
  const group = new THREE.Group()
  const w = site.width
  const h = Math.max(0.5, site.height)
  const d = site.depth
  const colorHex = parseInt(site.color.replace('#', ''), 16)

  // Body — solid block. Docks are flat platforms; warehouses are taller racks.
  const body = new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    new THREE.MeshStandardMaterial({ color: colorHex, roughness: 0.5, metalness: 0.1 })
  )
  body.position.set(0, h / 2, 0)
  group.add(body)

  // Outline edges for legibility on dark scenes.
  const edges = new THREE.EdgesGeometry(body.geometry)
  const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.35 }))
  line.position.copy(body.position)
  group.add(line)

  // Status tint: blocked → red overlay
  if (site.status === 'blocked') {
    const tint = new THREE.Mesh(
      new THREE.BoxGeometry(w * 1.05, h * 1.05, d * 1.05),
      new THREE.MeshBasicMaterial({ color: 0xc0392b, transparent: true, opacity: 0.25 })
    )
    tint.position.copy(body.position)
    group.add(tint)
  }

  // Floor mark on top — a thin slab to show "occupied surface"
  const cap = new THREE.Mesh(
    new THREE.BoxGeometry(w * 0.9, 0.05, d * 0.9),
    new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: 0.18, roughness: 0.8 })
  )
  cap.position.set(0, h + 0.04, 0)
  group.add(cap)

  group.position.set(site.position[0], 0, site.position[2])
  group.rotation.y = site.rotation
  return group
}

function rebuildSites(sites: SiteSnapshot[]) {
  // Remove old site meshes
  for (const id of Object.keys(siteMeshes)) {
    const group = siteMeshes[id]
    group.traverse((obj) => {
      if ((obj as THREE.Mesh).geometry) (obj as THREE.Mesh).geometry.dispose()
      const mat = (obj as THREE.Mesh).material
      if (Array.isArray(mat)) mat.forEach((m) => m.dispose())
      else if (mat) (mat as THREE.Material).dispose()
    })
    scene?.remove(group)
    delete siteMeshes[id]
  }
  for (const s of sites) {
    const group = buildSiteGroup(s)
    scene?.add(group)
    siteMeshes[s.id] = group
  }
  dockCount.value = sites.filter((s) => s.kind === 'dock').length
  rackCount.value = sites.filter((s) => s.kind === 'warehouse').length
}

async function syncSites() {
  try {
    const res = await axios.get<SiteSnapshot[]>('/api/sites')
    rebuildSites(res.data)
  } catch { /* backend may be down */ }
}

async function syncDevices() {
  if (paused.value) return
  try {
    const res = await axios.get<DeviceSnapshot[]>('/api/devices')
    deviceCount.value = res.data.length
    const present = new Set<string>()
    for (const d of res.data) {
      present.add(d.device_id)
      const mesh = ensureDeviceMesh(d.device_id)
      mesh.position.set(d.position[0], 0.45, d.position[2])
      const material = mesh.material as THREE.MeshStandardMaterial
      const target = statusColors[d.status] ?? statusColors.idle
      material.color.setHex(target)
      material.emissive.setHex(target)
      material.emissiveIntensity = d.status === 'running' ? 0.5 : 0

      const trail = deviceTrails[d.device_id]
      if (trail && d.route && d.route.length > 1) {
        const points = d.route.map(p => new THREE.Vector3(p[0], 0.2, p[2]))
        trail.geometry.setFromPoints(points)
        trail.computeLineDistances()
        ;(trail.material as THREE.LineDashedMaterial).color.setHex(target)
        ;(trail.material as THREE.LineDashedMaterial).opacity = d.status === 'running' ? 0.85 : 0.25
      }

      const ring = deviceTargets[d.device_id]
      if (ring && d.route && d.route.length > 0) {
        const last = d.route[d.route.length - 1]
        ring.position.set(last[0], 0.05, last[2])
        ;(ring.material as THREE.MeshBasicMaterial).color.setHex(target)
        ring.visible = d.status === 'running'
      }
    }
    // Prune meshes for devices that no longer exist on the backend.
    for (const id of Object.keys(deviceMeshes)) {
      if (!present.has(id)) {
        scene?.remove(deviceMeshes[id])
        delete deviceMeshes[id]
        if (deviceTrails[id]) { scene?.remove(deviceTrails[id]); delete deviceTrails[id] }
        if (deviceTargets[id]) { scene?.remove(deviceTargets[id]); delete deviceTargets[id] }
      }
    }
  } catch { /* backend may be down */ }
}

let frame = 0
function animate() {
  animationId = requestAnimationFrame(animate)
  frame++
  if (camera && scene && renderer) {
    for (const id of Object.keys(deviceTrails)) {
      const trail = deviceTrails[id]
      const mat = trail.material as THREE.LineDashedMaterial & { dashOffset?: number }
      mat.dashOffset = -frame * 0.02 * speed.value
    }
    // Update robot arm joints
    if (robotArm) robotArm.update(0.016 * speed.value)
    if (loaderRobot) loaderRobot.update(0.016 * speed.value)
    if (followTarget.value && deviceMeshes[followTarget.value]) {
      autoRotate.value = false
      const mesh = deviceMeshes[followTarget.value]
      camera.position.lerp(new THREE.Vector3(mesh.position.x + 4, 6, mesh.position.z + 6), 0.05 * speed.value)
      camera.lookAt(mesh.position.x, 0.5, mesh.position.z)
    } else if (autoRotate.value) {
      const tt = frame * 0.0025 * speed.value
      camera.position.x = Math.cos(tt) * 22
      camera.position.z = Math.sin(tt) * 22
      camera.position.y = 16
      camera.lookAt(0, 0, 0)
    }
    renderer.render(scene, camera)
  }
}

defineExpose({
  follow(id: string) { followTarget.value = id },
  unfollow() { followTarget.value = '' },
  refreshSites: syncSites,
  refreshDevices: syncDevices,
})

let syncTimer: number | undefined
let sitesTimer: number | undefined
onMounted(() => {
  init()
  animate()
  syncDevices()
  syncSites()
  const applySpeed = () => {
    if (syncTimer) clearInterval(syncTimer)
    const interval = Math.max(150, Math.round(1000 / speed.value))
    syncTimer = window.setInterval(syncDevices, interval)
  }
  applySpeed()
  watch(speed, applySpeed)
  // Refresh sites every 5s so CRUD changes show up.
  sitesTimer = window.setInterval(syncSites, 5000)
})
onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (syncTimer) clearInterval(syncTimer)
  if (sitesTimer) clearInterval(sitesTimer)
  if (resizeObserver) resizeObserver.disconnect()
  else window.removeEventListener('resize', onResize)
  if (renderer) renderer.dispose()
  jointEventSource?.close()
  loaderJointEventSource?.close()
})

async function togglePause() {
  paused.value = !paused.value
  if (paused.value) {
    info(t.value.scene.pause)
    try { await axios.post('/api/control', { action: 'stop' }) } catch { /* ignore */ }
  } else {
    success(t.value.scene.resume)
    try { await axios.post('/api/control', { action: 'start' }) } catch { /* ignore */ }
  }
}

async function reset() {
  info(t.value.scene.reset)
  try { await axios.post('/api/control', { action: 'reset' }) } catch { /* ignore */ }
  await syncDevices()
  await syncSites()
}
</script>

<style scoped>
.wrap { position: relative; width: 100%; height: 100%; }
.warehouse { width: 100%; height: 100%; }
.hud {
  position: absolute;
  bottom: 12px;
  left: 12px;
  display: flex;
  gap: 8px;
  align-items: center;
  background: rgba(15, 25, 45, 0.78);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 10px;
  backdrop-filter: blur(8px);
  z-index: 5;
}
.hud-btn {
  background: var(--bg-sub);
  border: 1px solid var(--border);
  color: var(--fg);
  width: 30px;
  height: 30px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}
.hud-btn:hover { background: var(--accent); color: white; border-color: var(--accent); }
.hud-speed { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--fg-soft); }
.hud-speed input { width: 80px; }
.hud-speed .val { min-width: 36px; text-align: right; color: var(--fg); font-variant-numeric: tabular-nums; }
.hud-auto { display: flex; align-items: center; gap: 4px; font-size: 11px; color: var(--fg-soft); }
.hud-btn.follow { background: var(--accent); color: white; border-color: var(--accent); width: auto; padding: 0 10px; font-size: 12px; }
.legend {
  position: absolute;
  top: 8px;
  right: 12px;
  display: flex;
  gap: 10px;
  font-size: 10px;
  color: var(--fg-soft);
  background: rgba(15, 25, 45, 0.78);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 10px;
  backdrop-filter: blur(8px);
}
.legend .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
.legend .dot.running { background: #1f8a4c; }
.legend .dot.idle { background: #5b6478; }
.legend .dot.charging { background: #5eb0ff; }
.legend .dot.fault { background: #c0392b; }
.legend .hint { color: var(--fg-soft); font-style: italic; }
.sitecount {
  position: absolute;
  bottom: 12px;
  right: 12px;
  font-size: 10px;
  color: var(--fg-soft);
  background: rgba(15, 25, 45, 0.78);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 10px;
  backdrop-filter: blur(8px);
  z-index: 5;
}
</style>
