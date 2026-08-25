<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, shallowRef } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import type { FloorShell } from '@/types'
import { buildScene, type BuildResult } from './ShellScene'

const props = defineProps<{
  shell: FloorShell | null
  floorIndex?: number
}>()

const el = ref<HTMLDivElement | null>(null)
const scene = shallowRef<BuildResult | null>(null)
let renderer: THREE.WebGLRenderer | null = null
let controls: OrbitControls | null = null
let frame = 0

function build() {
  if (!props.shell) return
  scene.value?.dispose()
  const built = buildScene(props.shell)
  scene.value = built
  if (renderer && el.value) {
    fitCamera()
    renderer.render(built.scene, (renderer as unknown as { camera: THREE.Camera }).camera)
  }
}

function fitCamera() {
  const cam = (renderer as unknown as { camera: THREE.PerspectiveCamera }).camera
  const { w, d } = props.shell!.bounds
  cam.position.set(w / 2, Math.max(w, d) * 0.8, d + Math.max(w, d) * 0.6)
  cam.lookAt(w / 2, 0, d / 2)
  controls?.target.set(w / 2, 0, d / 2)
  controls?.update()
}

onMounted(() => {
  if (!el.value) return
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(el.value.clientWidth || 800, el.value.clientHeight || 600)
  el.value.appendChild(renderer.domElement)
  ;(renderer as unknown as { camera: THREE.PerspectiveCamera }).camera =
    new THREE.PerspectiveCamera(50, (el.value.clientWidth || 800) / (el.value.clientHeight || 600), 0.1, 5000)
  const cam = (renderer as unknown as { camera: THREE.PerspectiveCamera }).camera
  scene.value?.scene.add(new THREE.AmbientLight(0xffffff, 0.8))
  const dir = new THREE.DirectionalLight(0xffffff, 0.6)
  dir.position.set(50, 100, 50)
  scene.value?.scene.add(dir)
  controls = new OrbitControls(cam, renderer.domElement)
  build()
  const animate = () => {
    frame = requestAnimationFrame(animate)
    controls?.update()
    if (scene.value && renderer) renderer.render(scene.value.scene, cam)
  }
  animate()
  window.addEventListener('resize', onResize)
})

function onResize() {
  if (!el.value || !renderer) return
  const cam = (renderer as unknown as { camera: THREE.PerspectiveCamera }).camera
  renderer.setSize(el.value.clientWidth, el.value.clientHeight)
  cam.aspect = el.value.clientWidth / el.value.clientHeight
  cam.updateProjectionMatrix()
}

watch(() => [props.shell, props.floorIndex], build, { deep: true })

onBeforeUnmount(() => {
  cancelAnimationFrame(frame)
  window.removeEventListener('resize', onResize)
  controls?.dispose()
  scene.value?.dispose()
  renderer?.dispose()
})
</script>

<template>
  <div class="device-map-3d">
    <div v-if="!shell" class="empty">—</div>
    <div v-show="shell" ref="el" class="canvas" data-testid="map3d"></div>
  </div>
</template>

<style scoped>
.device-map-3d { width: 100%; height: 100%; }
.canvas { width: 100%; height: 100%; min-height: 320px; }
.empty { color: var(--fg-soft); display: grid; place-items: center; height: 100%; }
</style>
