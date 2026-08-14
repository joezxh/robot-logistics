# Tasks 13/14/15 Briefs — ScenePallet / SceneBox / SceneBag

## Plan Defect Corrected

Plan Tasks 14/15 使用 `import { LoaderRobot } from '@/three/LoaderRobot'`，但 tsconfig.json 未配置 `@/` 别名。**修正**：改用相对路径 `../three/LoaderRobot`。

---

## Task 13 — ScenePallet.vue

文件路径：`d:\projects\robot-logic\simulation\frontend\src\scenes\ScenePallet.vue`

完整内容（verbatim from plan）：

```vue
<template>
  <div ref="container" class="scene-container"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import * as THREE from 'three'
import axios from 'axios'
import { PalletForklift } from './three/PalletForklift'

const container = ref<HTMLDivElement | null>(null)
let renderer: THREE.WebGLRenderer | undefined
let scene: THREE.Scene | undefined
let camera: THREE.PerspectiveCamera | undefined
let animationId: number | undefined
const forklifts: Record<string, PalletForklift> = {}

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
  const wh = new THREE.Mesh(
    new THREE.BoxGeometry(4, 3, 3),
    new THREE.MeshStandardMaterial({ color: 0x58c47e })
  )
  wh.position.set(6, 1.5, -2)
  scene.add(wh)

  for (let i = 0; i < 2; i++) {
    const fk = new PalletForklift()
    fk.addToScene(scene, new THREE.Vector3(-3, 0, 2 - i * 4))
    forklifts[`forklift-0${i + 1}`] = fk
  }
}

function animate() {
  animationId = requestAnimationFrame(animate)
  if (camera && scene && renderer) {
    Object.values(forklifts).forEach((f) => f.update(0.016))
    renderer.render(scene, camera)
  }
}

async function syncDevices() {
  try {
    const res = await axios.get<Array<{
      device_id: string; device_type: string; position: [number, number, number]; status: string
    }>>('/api/devices')
    for (const d of res.data) {
      if (d.device_type !== 'pallet_forklift') continue
      const fk = forklifts[d.device_id]
      if (fk && d.status === 'running') {
        fk.setMastHeight(1.2)
        fk.setExtension(0.2)
        fk.setLoad(true)
      } else if (fk) {
        fk.setMastHeight(0)
        fk.setExtension(0)
        fk.setLoad(false)
      }
    }
  } catch { /* backend may be down */ }
}

onMounted(() => {
  init()
  animate()
  syncDevices()
  const t = window.setInterval(syncDevices, 1000)
  onUnmounted(() => clearInterval(t))
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  Object.values(forklifts).forEach((f) => f.dispose())
  renderer?.dispose()
})
</script>

<style scoped>
.scene-container { width: 100%; height: 100%; }
</style>
```

---

## Task 14 — SceneBox.vue

文件路径：`d:\projects\robot-logic\simulation\frontend\src\scenes\SceneBox.vue`

```vue
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
```

注：`loader.addEndEffector?.(...) ?? void 0` 用 optional chaining，LoaderRobot 类无该方法时安全跳过。

---

## Task 15 — SceneBag.vue

文件路径：`d:\projects\robot-logic\simulation\frontend\src\scenes\SceneBag.vue`

```vue
<template>
  <div ref="container" class="scene-container"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import * as THREE from 'three'
import { LoaderRobot } from '../three/LoaderRobot'
import { BagGripper } from './three/BagGripper'

const container = ref<HTMLDivElement | null>(null)
let renderer: THREE.WebGLRenderer | undefined
let scene: THREE.Scene | undefined
let camera: THREE.PerspectiveCamera | undefined
let animationId: number | undefined
let loader: LoaderRobot | undefined
let bagGripper: BagGripper | undefined

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
  bagGripper = new BagGripper()
  loader.addEndEffector?.(bagGripper.mesh) ?? void 0
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
  bagGripper?.dispose()
  renderer?.dispose()
})
</script>

<style scoped>
.scene-container { width: 100%; height: 100%; }
</style>
```

---

## Common Steps for Each Task

1. **覆写** stub 文件（ScenePallet/Box/Bag.vue 已被 Task 12 创建为 stub）
2. 类型检查：`cd "d:/projects/robot-logic/simulation/frontend" && npx vue-tsc --noEmit`
3. 提交（每个 Task 单独 commit）：

Task 13：
```bash
cd d:/projects/robot-logic
git add simulation/frontend/src/scenes/ScenePallet.vue
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): add ScenePallet with PalletForklift visualization"
```

Task 14：
```bash
git add simulation/frontend/src/scenes/SceneBox.vue
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): add SceneBox with LoaderRobot + BoxGripper"
```

Task 15：
```bash
git add simulation/frontend/src/scenes/SceneBag.vue
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): add SceneBag with LoaderRobot + BagGripper"
```

## Acceptance (each Task)

- [ ] 文件覆写 stub
- [ ] vue-tsc 0 new errors
- [ ] 单独 commit

## Return

3 行汇总：
```
Task 13: Status: DONE | commit: <7位>
Task 14: Status: DONE | commit: <7位>
Task 15: Status: DONE | commit: <7位>
```

或 1 行：`Status: DONE | t13/t14/t15 commits: <a/b/c> | vue-tsc: <0 new errors> | concerns: <...>`
