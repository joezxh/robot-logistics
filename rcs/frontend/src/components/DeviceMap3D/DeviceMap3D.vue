<script setup lang="ts">
// Three.js view of a FloorShell blueprint.
//
// Rendering goes through an EffectComposer (RenderPass → UnrealBloomPass →
// OutputPass) so the emissive zone materials glow and the map reads as a
// holographic blueprint instead of flat geometry. When the composer cannot be
// created we transparently fall back to a plain renderer.
import { onMounted, onBeforeUnmount, ref, watch, shallowRef } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js'
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js'
import type { FloorShell } from '@/types'
import { buildScene, type BuildResult } from './ShellScene'

const props = defineProps<{
  shell: FloorShell | null
  floorIndex?: number
}>()

const el = ref<HTMLDivElement | null>(null)
const scene = shallowRef<BuildResult | null>(null)

let renderer: THREE.WebGLRenderer | null = null
let camera: THREE.PerspectiveCamera | null = null
let controls: OrbitControls | null = null
let composer: EffectComposer | null = null
let renderPass: RenderPass | null = null
let frame = 0

// Bloom tuning: strong enough to make the emissive zones glow, with a 0.2
// threshold so the dark floor plane stays out of the bloom.
const BLOOM_STRENGTH = 0.85
const BLOOM_RADIUS = 0.5
const BLOOM_THRESHOLD = 0.2

/** Render through the composer when present, else straight to the renderer. */
function renderFrame() {
  if (!renderer || !camera) return
  if (composer) {
    composer.render()
  } else if (scene.value) {
    renderer.render(scene.value.scene, camera)
  }
}

function build() {
  if (!props.shell) return
  scene.value?.dispose()
  const built = buildScene(props.shell)
  scene.value = built
  // Rebuilding produces a brand new Scene object, so the render pass has to be
  // re-pointed at it — otherwise the composer keeps drawing the stale scene.
  if (renderPass) renderPass.scene = built.scene
  if (renderer && el.value) {
    fitCamera()
    renderFrame()
  }
}

function fitCamera() {
  if (!camera || !props.shell) return
  const { w, d } = props.shell.bounds
  camera.position.set(w / 2, Math.max(w, d) * 0.8, d + Math.max(w, d) * 0.6)
  camera.lookAt(w / 2, 0, d / 2)
  controls?.target.set(w / 2, 0, d / 2)
  controls?.update()
}

function onResize() {
  if (!el.value || !renderer || !camera) return
  const w = el.value.clientWidth
  const h = el.value.clientHeight
  renderer.setSize(w, h)
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  // EffectComposer applies the renderer's pixel ratio internally, so it takes
  // CSS pixels here.
  composer?.setSize(w, h)
}

onMounted(() => {
  if (!el.value) return
  const w = el.value.clientWidth || 800
  const h = el.value.clientHeight || 600

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.setSize(w, h)
  el.value.appendChild(renderer.domElement)

  camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 5000)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true

  // build() must run before the composer is created so RenderPass gets a real
  // scene. Lights now ship with the scene itself (see ShellScene.buildScene).
  build()

  if (scene.value && camera && renderer) {
    composer = new EffectComposer(renderer)
    renderPass = new RenderPass(scene.value.scene, camera)
    composer.addPass(renderPass)

    composer.addPass(
      new UnrealBloomPass(
        new THREE.Vector2(w, h),
        BLOOM_STRENGTH,
        BLOOM_RADIUS,
        BLOOM_THRESHOLD,
      ),
    )

    // OutputPass converts the linear HDR buffer back to sRGB for the canvas.
    composer.addPass(new OutputPass())
    composer.setSize(w, h)
  }

  const animate = () => {
    frame = requestAnimationFrame(animate)
    controls?.update()
    renderFrame()
  }
  animate()
  window.addEventListener('resize', onResize)
})

watch(() => [props.shell, props.floorIndex], build, { deep: true })

onBeforeUnmount(() => {
  cancelAnimationFrame(frame)
  window.removeEventListener('resize', onResize)
  controls?.dispose()
  composer?.dispose()
  scene.value?.dispose()
  renderer?.dispose()
  renderer?.domElement.remove()
  renderer = null
  camera = null
  controls = null
  composer = null
  renderPass = null
})
</script>

<template>
  <div class="device-map-3d">
    <div v-if="!shell" class="empty">—</div>
    <div v-show="shell" ref="el" class="canvas" data-testid="map3d"></div>
  </div>
</template>

<style scoped>
.device-map-3d {
  width: 100%;
  height: 100%;
}

.canvas {
  width: 100%;
  height: 100%;
  min-height: 320px;
}

.empty {
  color: var(--fg-muted);
  display: grid;
  place-items: center;
  height: 100%;
}
</style>
