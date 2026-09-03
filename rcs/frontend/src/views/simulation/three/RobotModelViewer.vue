<script setup lang="ts">
/**
 * Demo: load a MuJoCo MJCF robot model into three.js via MjcfLoader.
 *
 * Point `MODEL_URL` at a served MJCF document. In dev the Vite proxy exposes
 * the simulation assets at `/sim-assets/...` (see vite.config.ts), so the UR5e
 * shipped in `simulation/backend/assets/robots/ur5e/ur5e.xml` is reachable at
 * `/sim-assets/robots/ur5e/ur5e.xml`.
 */
import { onMounted, onUnmounted, ref, shallowRef } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { MjcfLoader, type MjcfRobot } from './MjcfLoader'

const MODEL_URL = '/sim-assets/robots/ur5e/ur5e.xml'
// NOTE: deviceId is accepted for API symmetry with the simulation console but
// the demo pins MODEL_URL; leave the prop declared (no unused warning).
withDefaults(defineProps<{ deviceId?: string }>(), {
  deviceId: 'robot/ur5e-0',
})

const canvas = ref<HTMLCanvasElement | null>(null)
const status = ref('loading…')
const joints = ref<{ name: string; value: number }[]>([])

let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let controls: OrbitControls | null = null
let raf = 0
const robot = shallowRef<MjcfRobot | null>(null)

function loop() {
  raf = requestAnimationFrame(loop)
  controls?.update()
  if (canvas.value && renderer && scene && camera) {
    renderer.render(scene, camera)
  }
}

async function load() {
  try {
    const r = await MjcfLoader.load(MODEL_URL, {
      baseUrl: MODEL_URL,
      showCollision: false,
    })
    robot.value = r
    if (scene) scene.add(r.root)

    // frame the model
    const box = new THREE.Box3().setFromObject(r.root)
    const size = box.getSize(new THREE.Vector3()).length() || 1
    const center = box.getCenter(new THREE.Vector3())
    if (camera) {
      camera.position.set(center.x + size * 0.9, center.y + size * 0.6, center.z + size * 0.9)
      camera.lookAt(center)
    }
    controls?.target.copy(center)

    // expose joint sliders (clamped to declared range)
    joints.value = Array.from(r.joints.values()).map((j) => ({ name: j.name, value: j.range ? j.range[0] : 0 }))
    status.value = `loaded: ${r.modelName} (${r.joints.size} joints)`
  } catch (e) {
    status.value = `error: ${(e as Error).message}`
    console.error(e)
  }
}

function onJointInput() {
  const r = robot.value
  if (!r) return
  for (const j of joints.value) r.setJointAngle(j.name, j.value)
}

function resize() {
  const c = canvas.value
  if (!c || !renderer || !camera) return
  const w = c.clientWidth || 480
  const h = c.clientHeight || 360
  renderer.setSize(w, h, false)
  camera.aspect = w / h
  camera.updateProjectionMatrix()
}

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

  scene.add(new THREE.AmbientLight(0xffffff, 0.5))
  const dir = new THREE.DirectionalLight(0xffffff, 1.0)
  dir.position.set(3, 6, 4)
  dir.castShadow = true
  scene.add(dir)
  scene.add(new THREE.GridHelper(4, 16, 0x335, 0x223))

  resize()
  window.addEventListener('resize', resize)
  loop()
  void load()
})

onUnmounted(() => {
  cancelAnimationFrame(raf)
  window.removeEventListener('resize', resize)
  controls?.dispose()
  renderer?.dispose()
})
</script>

<template>
  <div class="rmv-root">
    <div class="rmv-bar">
      <span>{{ status }}</span>
    </div>
    <canvas ref="canvas" class="rmv-canvas"></canvas>
    <div v-if="joints.length" class="rmv-joints">
      <label v-for="j in joints" :key="j.name" class="rmv-joint">
        <span>{{ j.name }}</span>
        <input type="range" min="-3.14" max="3.14" step="0.01" v-model.number="j.value" @input="onJointInput" />
      </label>
    </div>
  </div>
</template>

<style scoped>
.rmv-root {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #0f1320;
}
.rmv-bar {
  padding: 4px 10px;
  font: 12px/1.4 ui-monospace, monospace;
  color: #9fb3ff;
  background: #161b2e;
  display: flex;
  gap: 14px;
  align-items: center;
}
.rmv-canvas {
  flex: 1;
  width: 100%;
  min-height: 0;
  display: block;
}
.rmv-joints {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 14px;
  padding: 8px 10px;
  background: #161b2e;
  max-height: 38%;
  overflow: auto;
}
.rmv-joint {
  display: flex;
  align-items: center;
  gap: 6px;
  font: 11px/1 ui-monospace, monospace;
  color: #cdd6ff;
}
.rmv-joint input {
  width: 120px;
}
</style>
