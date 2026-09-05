<script setup lang="ts">
/**
 * Render a unified map's wt_floor_shell geometry as a 3D scene.
 *
 * Two render modes, toggleable at runtime (see the toolbar buttons):
 *  - "static"  : the existing `MjcfLoader` pipeline parses the backend MJCF
 *                into three.js primitives. Pure visualisation, no physics.
 *  - "physics" : the same MJCF is compiled in DeepMind's MuJoCo WASM engine
 *                (`@mujoco/mujoco`) running in the browser; `mj_step` advances
 *                the real simulation each frame and `mjData.geom_xpos` /
 *                `geom_xmat` drive the identical three.js meshes.
 *
 * Both modes share the same three.js renderer / camera / controls, so the
 * viewer can switch between them without rebuilding the WebGL context.
 */
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { MjcfLoader, type MjcfRobot } from '@/views/simulation/three/MjcfLoader'
import { getMapMjcfUrl } from '@/api/map'
import { createMujocoScene, type MujocoScene } from './mujocoScene'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = withDefaults(
  defineProps<{ mapId: string; reloadKey?: number; mode?: 'static' | 'physics' }>(),
  { mode: 'static' },
)
const emit = defineEmits<{ (e: 'update:mode', v: 'static' | 'physics'): void }>()

const canvas = ref<HTMLCanvasElement | null>(null)
const status = ref('')
const mode = ref<'static' | 'physics'>(props.mode)
const physicsBusy = ref(false)

let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let controls: OrbitControls | null = null
let raf = 0
let loadedUrl: string | null = null
let mujoco: MujocoScene | null = null

function loop() {
  raf = requestAnimationFrame(loop)
  controls?.update()
  if (mujoco) mujoco.step()
  if (canvas.value && renderer && scene && camera) renderer.render(scene, camera)
}

function disposeObject(obj: THREE.Object3D) {
  obj.traverse((o) => {
    const mesh = o as THREE.Mesh
    if (mesh.geometry) mesh.geometry.dispose()
    const mat = mesh.material as THREE.Material | THREE.Material[] | undefined
    if (Array.isArray(mat)) mat.forEach((m) => m.dispose())
    else if (mat) mat.dispose()
  })
}

function clearMap() {
  if (mujoco) {
    mujoco.dispose()
    mujoco = null
  }
  if (!scene) return
  for (const c of [...scene.children]) {
    if (c.userData?.isMap) {
      // The MuJoCo group's meshes were already disposed above.
      if (!c.userData?.isMujoco) disposeObject(c)
      scene.remove(c)
    }
  }
}

function frame(center: THREE.Vector3, size: number) {
  if (!camera) return
  camera.position.set(center.x + size * 0.9, center.y + size * 0.6, center.z + size * 0.9)
  camera.lookAt(center)
  controls?.target.copy(center)
}

async function loadStatic(url: string) {
  try {
    const r: MjcfRobot = await MjcfLoader.load(url, { baseUrl: url, showCollision: false })
    if (!scene) return
    clearMap()
    r.root.userData.isMap = true
    scene.add(r.root)
    const box = new THREE.Box3().setFromObject(r.root)
    const size = box.getSize(new THREE.Vector3()).length() || 1
    const center = box.getCenter(new THREE.Vector3())
    frame(center, size)
    status.value = `${t('maps.modeStatic')}: ${r.modelName}`
  } catch (e) {
    status.value = `error: ${(e as Error).message}`
    console.error(e)
  }
}

async function loadPhysics(url: string) {
  try {
    physicsBusy.value = true
    status.value = t('maps.physicsLoading')
    const xml = await (await fetch(url)).text()
    const ms = await createMujocoScene(xml)
    if (!scene) {
      ms.dispose()
      return
    }
    clearMap()
    mujoco = ms
    ms.group.userData.isMap = true
    scene.add(ms.group)
    const box = new THREE.Box3().setFromObject(ms.group)
    const size = box.getSize(new THREE.Vector3()).length() || 1
    const center = box.getCenter(new THREE.Vector3())
    frame(center, size)
    physicsBusy.value = false
    status.value = t('maps.modePhysics')
  } catch (e) {
    physicsBusy.value = false
    status.value = `error: ${(e as Error).message}`
    console.error(e)
  }
}

function applyMode(m: 'static' | 'physics') {
  if (m === mode.value) return
  mode.value = m
  emit('update:mode', m)
  const url = loadedUrl
  if (!url) return
  if (m === 'physics') void loadPhysics(url)
  else void loadStatic(url)
}

const url = computed(() => {
  const base = getMapMjcfUrl(props.mapId)
  // reloadKey busts the browser/HTTP cache after an edit so the 3D view
  // reflects freshly-saved geometry without a manual refresh.
  return props.reloadKey ? `${base}?t=${props.reloadKey}` : base
})

onMounted(() => {
  if (!canvas.value) return
  renderer = new THREE.WebGLRenderer({ canvas: canvas.value, antialias: true })
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.shadowMap.enabled = true
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0f1320)
  camera = new THREE.PerspectiveCamera(45, 1, 0.05, 500)
  controls = new OrbitControls(camera, canvas.value)
  controls.enableDamping = true
  scene.add(new THREE.AmbientLight(0xffffff, 0.6))
  const dir = new THREE.DirectionalLight(0xffffff, 1.0)
  dir.position.set(40, 80, 40)
  dir.castShadow = true
  scene.add(dir)
  scene.add(new THREE.GridHelper(80, 32, 0x334155, 0x1e293b))
  resize()
  window.addEventListener('resize', resize)
  loop()
  loadedUrl = url.value
  if (mode.value === 'physics') void loadPhysics(loadedUrl)
  else void loadStatic(loadedUrl)
})

watch(url, (u) => {
  loadedUrl = u
  if (mode.value === 'physics') void loadPhysics(u)
  else void loadStatic(u)
})

watch(
  () => props.mode,
  (m) => {
    if (m !== mode.value) applyMode(m)
  },
)

onUnmounted(() => {
  cancelAnimationFrame(raf)
  window.removeEventListener('resize', resize)
  clearMap()
  controls?.dispose()
  renderer?.dispose()
})

function resize() {
  const c = canvas.value
  if (!c || !renderer || !camera) return
  const w = c.clientWidth || 480
  const h = c.clientHeight || 360
  renderer.setSize(w, h, false)
  camera.aspect = w / h
  camera.updateProjectionMatrix()
}

defineExpose({
  reload: () => {
    if (loadedUrl) (mode.value === 'physics' ? loadPhysics(loadedUrl) : loadStatic(loadedUrl))
  },
})
</script>

<template>
  <div class="tmv-root">
    <div class="tmv-bar">
      <span class="tmv-status">{{ status }}</span>
      <span class="tmv-modes">
        <button type="button" :class="{ on: mode === 'static' }" :disabled="physicsBusy" @click="applyMode('static')">
          {{ t('maps.modeStatic') }}
        </button>
        <button type="button" :class="{ on: mode === 'physics' }" :disabled="physicsBusy" @click="applyMode('physics')">
          {{ t('maps.modePhysics') }}
        </button>
      </span>
    </div>
    <canvas ref="canvas" class="tmv-canvas" />
  </div>
</template>

<style scoped>
.tmv-root {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #0f1320;
}
.tmv-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 4px 10px;
  font: 12px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace;
  color: #9fb3ff;
  background: #161b2e;
}
.tmv-status {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.tmv-modes {
  display: inline-flex;
  gap: 4px;
  flex: none;
}
.tmv-modes button {
  cursor: pointer;
  border: 1px solid #334155;
  border-radius: 4px;
  background: #0f1320;
  color: #9fb3ff;
  padding: 2px 8px;
  font: 12px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace;
}
.tmv-modes button:hover:not(:disabled) {
  border-color: #4f7cff;
}
.tmv-modes button.on {
  background: #2563eb;
  border-color: #2563eb;
  color: #fff;
}
.tmv-modes button:disabled {
  opacity: 0.5;
  cursor: default;
}
.tmv-canvas {
  flex: 1;
  width: 100%;
  min-height: 0;
  display: block;
}
</style>
