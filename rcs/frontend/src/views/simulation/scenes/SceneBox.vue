<template>
  <div ref="container" class="scene-container"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import * as THREE from 'three'
import { LoaderRobot } from '../three/LoaderRobot'
import { BoxGripper } from './three/BoxGripper'

const container = ref<HTMLDivElement | null>(null)
let renderer: THREE.WebGLRenderer | undefined
let scene: THREE.Scene | undefined
let camera: THREE.PerspectiveCamera | undefined
let animationId: number | undefined
let loader: LoaderRobot | undefined
let boxGripper: BoxGripper | undefined

function init() {
  if (!container.value) return
  const w = container.value.clientWidth
  const h = container.value.clientHeight
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0b1220)
  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100)
  camera.position.set(0, 14, 18)
  camera.lookAt(0, 0, 0)
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(w, h)
  container.value.appendChild(renderer.domElement)
  scene.add(new THREE.AmbientLight(0xffffff, 0.5))
  const dir = new THREE.DirectionalLight(0xffffff, 0.9)
  dir.position.set(10, 20, 10)
  scene.add(dir)

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(36, 24),
    new THREE.MeshStandardMaterial({ color: 0x152238, roughness: 0.9 })
  )
  ground.rotation.x = -Math.PI / 2
  scene.add(ground)

  const dock = new THREE.Mesh(
    new THREE.BoxGeometry(6, 0.6, 4),
    new THREE.MeshStandardMaterial({ color: 0x5eb0ff })
  )
  dock.position.set(-6, 0.3, 4)
  scene.add(dock)

  loader = new LoaderRobot()
  loader.addToScene(scene, new THREE.Vector3(-3, 0, 2))
  boxGripper = new BoxGripper()
  loader.addEndEffector?.(boxGripper.mesh) ?? void 0
}

function animate() {
  animationId = requestAnimationFrame(animate)
  if (camera && scene && renderer) {
    loader?.update(0.016)
    renderer.render(scene, camera)
  }
}

onMounted(() => {
  init()
  animate()
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  boxGripper?.dispose()
  renderer?.dispose()
})
</script>

<style scoped>
.scene-container { width: 100%; height: 100%; }
</style>
