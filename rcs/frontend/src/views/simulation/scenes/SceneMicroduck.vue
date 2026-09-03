<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { MjcfLoader } from '../three/MjcfLoader'
import { microduckQposToViewer } from '../three/microduckQpos'

const MJCF_URL = '/sim-assets/robots/microduck/robot_walk.xml'
const STREAM_URL = '/sim/stream'

const canvasHost = ref<HTMLDivElement | null>(null)
const status = ref<'loading' | 'ready' | 'error'>('loading')
const streamOn = ref(false)
const errMsg = ref('')

let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let controls: OrbitControls | null = null
let robot: Awaited<ReturnType<typeof MjcfLoader.load>> | null = null
let raf = 0
let es: EventSource | null = null

function renderLoop() {
  if (!renderer || !scene || !camera) return
  controls?.update()
  renderer.render(scene, camera)
  raf = requestAnimationFrame(renderLoop)
}

function applyViewerPose(qpos: number[]) {
  if (!robot) return
  const { freeJoint, joints } = microduckQposToViewer(qpos)
  robot.setFreeJointPose(freeJoint)
  for (const [name, angle] of Object.entries(joints)) robot.setJointAngle(name, angle)
}

function onStreamMessage(ev: MessageEvent) {
  try {
    const payload = JSON.parse(ev.data)
    const qpos: number[] = payload.data?.qpos ?? payload.qpos
    if (Array.isArray(qpos) && qpos.length >= 21) applyViewerPose(qpos)
  } catch {
    /* ignore malformed frames */
  }
}

function startStream() {
  if (es) return
  es = new EventSource(STREAM_URL)
  es.onmessage = onStreamMessage
  es.onerror = () => {
    streamOn.value = false
  }
  streamOn.value = true
}

function stopStream() {
  es?.close()
  es = null
  streamOn.value = false
}

onMounted(async () => {
  try {
    robot = await MjcfLoader.load(MJCF_URL)
    scene = new THREE.Scene()
    scene.background = new THREE.Color(0x101418)
    camera = new THREE.PerspectiveCamera(50, 1, 0.01, 100)
    camera.position.set(0.6, 0.4, 0.6)
    const host = canvasHost.value!
    renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(host.clientWidth || 480, host.clientHeight || 360)
    host.appendChild(renderer.domElement)
    scene.add(robot.root)
    scene.add(new THREE.GridHelper(2, 20, 0x335577, 0x223344))
    scene.add(new THREE.AmbientLight(0xffffff, 0.7))
    const dir = new THREE.DirectionalLight(0xffffff, 0.8)
    dir.position.set(1, 2, 1)
    scene.add(dir)
    controls = new OrbitControls(camera, renderer.domElement)
    controls.target.set(0, 0.1, 0)
    // Identity floating-base pose (qw = 1) so the duck stands upright at rest.
    const init = new Array(21).fill(0)
    init[3] = 1
    applyViewerPose(init)
    status.value = 'ready'
    renderLoop()
  } catch (e) {
    errMsg.value = String(e)
    status.value = 'error'
  }
})

onBeforeUnmount(() => {
  cancelAnimationFrame(raf)
  stopStream()
  renderer?.dispose()
})
</script>

<template>
  <div class="microduck-stage">
    <div ref="canvasHost" class="canvas-host"></div>
    <div class="toolbar">
      <span v-if="status === 'loading'">加载 Microduck 模型中…</span>
      <span v-else-if="status === 'error'">加载失败：{{ errMsg }}</span>
      <span v-else>Microduck · robot_walk</span>
      <button :disabled="status !== 'ready'" @click="streamOn ? stopStream() : startStream()">
        {{ streamOn ? '停止遥测' : '开始遥测' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.microduck-stage {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.canvas-host {
  flex: 1;
  min-height: 320px;
}
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 8px;
}
</style>
