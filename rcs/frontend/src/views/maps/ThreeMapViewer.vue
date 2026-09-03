<script setup lang="ts">
/**
 * Render a unified map's wt_floor_shell geometry as a 3D scene.
 *
 * Fetches the backend-generated MJCF via `getMapMjcfUrl(mapId)` and loads it
 * with the same `MjcfLoader` pipeline that `RobotModelViewer` uses for robots.
 * No physics — pure visualisation (orbit / zoom / pan).
 */
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { MjcfLoader, type MjcfRobot } from '@/views/simulation/three/MjcfLoader'
import { getMapMjcfUrl } from '@/api/map'

const props = withDefaults(defineProps<{ mapId: string; reloadKey?: number }>(), {})
const canvas = ref<HTMLCanvasElement | null>(null)
const status = ref('loading…')
let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let controls: OrbitControls | null = null
let raf = 0
const robot = ref<MjcfRobot | null>(null)
let loadedUrl: string | null = null

function loop() {
  raf = requestAnimationFrame(loop)
  controls?.update()
  if (canvas.value && renderer && scene && camera) renderer.render(scene, camera)
}

async function load(url: string) {
  try {
    const r = await MjcfLoader.load(url, { baseUrl: url, showCollision: false })
    robot.value = r
    if (scene) {
      // drop any previously loaded map root before mounting the new one
      for (const c of [...scene.children]) {
        if (c.userData?.isMap) scene.remove(c)
      }
      r.root.userData.isMap = true
      scene.add(r.root)
      const box = new THREE.Box3().setFromObject(r.root)
      const size = box.getSize(new THREE.Vector3()).length() || 1
      const center = box.getCenter(new THREE.Vector3())
      if (camera) {
        camera.position.set(center.x + size * 0.9, center.y + size * 0.6, center.z + size * 0.9)
        camera.lookAt(center)
      }
      controls?.target.copy(center)
    }
    status.value = `loaded: ${r.modelName}`
  } catch (e) {
    status.value = `error: ${(e as Error).message}`
    console.error(e)
  }
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
  void load(loadedUrl)
})

watch(url, (u) => {
  loadedUrl = u
  void load(u)
})

onUnmounted(() => {
  cancelAnimationFrame(raf)
  window.removeEventListener('resize', resize)
  controls?.dispose()
  renderer?.dispose()
})

defineExpose({ reload: () => { if (loadedUrl) void load(loadedUrl) } })
</script>

<template>
  <div class="tmv-root">
    <div class="tmv-bar"><span>{{ status }}</span></div>
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
  padding: 4px 10px;
  font: 12px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace;
  color: #9fb3ff;
  background: #161b2e;
}
.tmv-canvas {
  flex: 1;
  width: 100%;
  min-height: 0;
  display: block;
}
</style>
