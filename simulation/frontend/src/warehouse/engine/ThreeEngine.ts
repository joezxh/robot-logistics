/**
 * ThreeEngine - Core 3D rendering engine for warehouse visualization
 * Migrated from warehouse_theatre_3d/wt3d-vue.js
 */
import * as THREE from 'three'
import type { Slot } from '../types'
import type { FloorFull, Zone, ShellBlueprint } from '../types'

export interface PickResult {
  kind: 'slot' | 'zone' | 'facility' | 'dock' | 'vehicle'
  ref: string
  name?: string
  slot?: string
  lv?: string
  vehicleRef?: string
}

export interface HoverCallback {
  (result: PickResult | null, x: number, y: number): void
}

export interface ClickCallback {
  (result: PickResult | null, wasSelected: boolean, isDouble: boolean): void
}

export class ThreeEngine {
  // Scene objects
  renderer!: THREE.WebGLRenderer
  scene!: THREE.Scene
  camera!: THREE.PerspectiveCamera
  rootGrp!: THREE.Group
  pickables: THREE.Object3D[] = []

  // Canvas
  canvas!: HTMLCanvasElement
  cwEl!: HTMLElement

  // Camera state (orbit mode)
  theta = 0.65
  phi = 0.78
  radius = 28
  panX = 0
  panZ = 0

  // Target camera state (smooth interpolation)
  tT = 0.65
  tP = 0.78
  tR = 28
  tPX = 0
  tPZ = 0

  // Mouse drag state
  drag = false
  rDrag = false
  lx = 0
  ly = 0

  // Hover state
  hovKey: string | null = null

  // Animation
  _animRunning = false

  // Aisle view mode
  aisleMode = false
  fpX = 0
  fpY = 2.2
  fpZ = 0
  fpYaw = Math.PI
  fpPitch = 0
  fpSpeed = 0.15

  // Shell visual groups
  wallGroup!: THREE.Group
  markingsGroup!: THREE.Group
  corridorGroup!: THREE.Group

  // Point light for ambient animation
  ptL!: THREE.PointLight

  // Selected mesh key
  selKey: string | null = null

  // Mesh map for highlighting
  meshMap: Record<string, THREE.Object3D> = {}

  // Shell framing flag
  _shellFramed = false

  // Highlight meshes
  private _highlightMesh?: THREE.Mesh

  constructor() {
    this.meshMap = {}
    this.theta = 0.65
    this.phi = 0.78
    this.radius = 28
    this.panX = 0
    this.panZ = 0
    this.tT = 0.65
    this.tP = 0.78
    this.tR = 28
    this.tPX = 0
    this.tPZ = 0
    this.drag = false
    this.rDrag = false
    this.lx = 0
    this.ly = 0
    this.hovKey = null
    this._animRunning = false
    this.aisleMode = false
  }

  init(canvas: HTMLCanvasElement, cwEl: HTMLElement): void {
    this.canvas = canvas
    this.cwEl = cwEl

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false })
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.shadowMap.enabled = true
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap

    this.scene = new THREE.Scene()

    const bgCol = 0x0c0e14
    this.renderer.setClearColor(bgCol, 1)
    this.scene.background = new THREE.Color(bgCol)
    this.scene.fog = new THREE.Fog(bgCol, 50, 130)

    this.camera = new THREE.PerspectiveCamera(45, 1, 0.1, 200)
    this.camera.position.set(14, 18, 24)
    this.camera.lookAt(0, 0, 0)

    // Lighting
    this.scene.add(new THREE.AmbientLight(0xffffff, 0.4))

    const dL = new THREE.DirectionalLight(0xffffff, 0.8)
    dL.position.set(12, 22, 12)
    dL.castShadow = true
    dL.shadow.mapSize.set(2048, 2048)
    dL.shadow.camera.left = -30
    dL.shadow.camera.right = 30
    dL.shadow.camera.top = 30
    dL.shadow.camera.bottom = -30
    this.scene.add(dL)

    const fL = new THREE.DirectionalLight(0x4060ff, 0.25)
    fL.position.set(-10, 6, -10)
    this.scene.add(fL)

    this.ptL = new THREE.PointLight(0x60a5fa, 0.5, 60)
    this.ptL.position.set(0, 16, 0)
    this.scene.add(this.ptL)

    // Ground plane
    const fl = new THREE.Mesh(
      new THREE.PlaneGeometry(80, 80),
      new THREE.MeshStandardMaterial({ color: 0x0a0c12, roughness: 0.95, metalness: 0.05 })
    )
    fl.rotation.x = -Math.PI / 2
    fl.position.y = -0.02
    fl.receiveShadow = true
    this.scene.add(fl)

    // Grid
    this.scene.add(new THREE.GridHelper(80, 40, 0x181c28, 0x181c28))

    // Root group for warehouse content
    this.rootGrp = new THREE.Group()
    this.scene.add(this.rootGrp)

    this._sizeRenderer()
    this._startAnimate()

    new ResizeObserver(() => this._sizeRenderer()).observe(cwEl)
  }

  private _sizeRenderer(): void {
    const w = this.cwEl.clientWidth
    const h = this.cwEl.clientHeight
    if (!w || !h) return
    this.renderer.setSize(w, h, false)
    this.camera.aspect = w / h
    this.camera.updateProjectionMatrix()
  }

  private _startAnimate(): void {
    if (this._animRunning) return
    this._animRunning = true

    const loop = () => {
      requestAnimationFrame(loop)
      const t = performance.now() * 0.001

      // Smooth camera interpolation
      this.theta += (this.tT - this.theta) * 0.08
      this.phi += (this.tP - this.phi) * 0.08
      this.radius += (this.tR - this.radius) * 0.08
      this.panX += (this.tPX - this.panX) * 0.08
      this.panZ += (this.tPZ - this.panZ) * 0.08

      this._updateCamera()

      // Animate point light for ambient effect
      this.ptL.position.x = Math.sin(t * 0.35) * 7
      this.ptL.position.z = Math.cos(t * 0.35) * 7

      this.renderer.render(this.scene, this.camera)
    }
    loop()
  }

  private _updateCamera(): void {
    if (this.aisleMode) {
      // First-person aisle view
      this.camera.position.set(this.fpX, this.fpY, this.fpZ)
      this.camera.lookAt(
        this.fpX + Math.sin(this.fpYaw),
        this.fpY + this.fpPitch,
        this.fpZ + Math.cos(this.fpYaw)
      )
      return
    }

    // Orbit camera
    this.camera.position.set(
      this.panX + this.radius * Math.sin(this.phi) * Math.sin(this.theta),
      this.radius * Math.cos(this.phi),
      this.panZ + this.radius * Math.sin(this.phi) * Math.cos(this.theta)
    )
    this.camera.lookAt(this.panX, 0, this.panZ)
  }

  enterAisleView(aisleZ: number): void {
    this.aisleMode = true
    this.fpX = 0
    this.fpY = 2.2
    this.fpZ = aisleZ
    this.fpYaw = Math.PI
    this.fpPitch = 0
  }

  exitAisleView(): void {
    this.aisleMode = false
    this.tT = 0.65
    this.tP = 0.78
    this.tR = 28
    this.tPX = 0
    this.tPZ = 0
  }

  moveAisle(forward: number, strafe: number, turnY: number, turnX: number): void {
    if (!this.aisleMode) return
    this.fpYaw += turnY * 0.02
    this.fpPitch = Math.max(-0.8, Math.min(0.8, this.fpPitch + turnX * 0.02))
    this.fpX += Math.sin(this.fpYaw) * forward * this.fpSpeed + Math.cos(this.fpYaw) * strafe * this.fpSpeed
    this.fpZ += Math.cos(this.fpYaw) * forward * this.fpSpeed - Math.sin(this.fpYaw) * strafe * this.fpSpeed
  }

  buildScene(slots: Slot[], floorFull?: FloorFull): void {
    this.clearRoot()
    this.meshMap = {}
    this.selKey = null
    this._shellFramed = false

    if (floorFull?.shell && (floorFull.zones || []).length) {
      this.buildShell(floorFull.shell)
      ;(floorFull.zones || []).forEach((z: Zone) => {
        const sz = (floorFull.shell?.zones || []).find((s: any) => s.ref === z.ref)
        if (sz) {
          z.x = sz.x
          z.z = sz.z
          z.w = sz.w
          z.d = sz.d
        }
        this.buildZone(z, slots)
      })
      this.buildFacilities(floorFull.facilities || [], floorFull.shell)
      this.buildDocks(floorFull.docks || [], floorFull.shell)
      this.buildVehicles((floorFull.shell?.vehicles) || [], floorFull.shell)
      return
    }

    // Legacy fallback: single rack matrix
    this.buildRackZone({ ref: 'LEGACY', type: 'rack', x: 0, z: 0, w: 20, d: 15 }, slots)
  }

  clearRoot(): void {
    // Dispose geometry/material before clearing
    this.rootGrp.traverse((o: THREE.Object3D) => {
      if (o instanceof THREE.Mesh) {
        o.geometry?.dispose()
        if (o.material) {
          if ((o.material as THREE.MeshStandardMaterial).map) {
            ;(o.material as THREE.MeshStandardMaterial).map?.dispose()
          }
          o.material.dispose()
        }
      }
    })
    while (this.rootGrp.children.length) {
      this.rootGrp.remove(this.rootGrp.children[0])
    }
    this.pickables = []
    this._highlightMesh = undefined
  }

  buildShell(shell: ShellBlueprint): void {
    const B = shell.bounds
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(B.w, B.d),
      new THREE.MeshStandardMaterial({ color: 0x0a0c12, roughness: 0.95, metalness: 0.05 })
    )
    ground.rotation.x = -Math.PI / 2
    ground.position.y = -0.018
    ground.receiveShadow = true
    this.rootGrp.add(ground)

    // Corridors
    this.corridorGroup = new THREE.Group()
    ;(shell.corridors || []).forEach((c) => {
      const w = Math.abs(c.x1 - c.x0) || Math.abs(c.z1 - c.z0)
      const d = Math.abs(c.z1 - c.z0) || Math.abs(c.x1 - c.x0)
      const m = new THREE.Mesh(
        new THREE.PlaneGeometry(w, d),
        new THREE.MeshBasicMaterial({
          color: c.main ? 0x3b82f6 : 0x4ade80,
          transparent: true,
          opacity: c.main ? 0.18 : 0.12,
          depthWrite: false,
        })
      )
      m.rotation.x = -Math.PI / 2
      m.position.set((c.x0 + c.x1) / 2, 0.015, (c.z0 + c.z1) / 2)
      this.corridorGroup.add(m)
    })
    this.rootGrp.add(this.corridorGroup)

    this.buildWalls(shell)
    this.buildMarkings(shell)
  }

  buildWalls(shell: ShellBlueprint): void {
    if (this.wallGroup) this.wallGroup.visible = false
    this.wallGroup = new THREE.Group()

    const wallMat = new THREE.MeshStandardMaterial({
      color: 0x94a3b8,
      transparent: true,
      opacity: 0.35,
      roughness: 0.85,
      metalness: 0.1,
      depthWrite: false,
    })

    ;(shell.walls || []).forEach((w) => {
      const len = Math.hypot(w.x1 - w.x0, w.z1 - w.z0)
      if (!len) return
      const h = w.h || 3
      let mat = wallMat

      if (w.dock_bumper) {
        const bc = document.createElement('canvas')
        bc.width = 64
        bc.height = 64
        const bctx = bc.getContext('2d')!
        bctx.fillStyle = '#facc15'
        bctx.fillRect(0, 0, 64, 64)
        bctx.fillStyle = '#000'
        for (let i = -64; i < 128; i += 16) {
          bctx.beginPath()
          bctx.moveTo(i, 0)
          bctx.lineTo(i + 8, 0)
          bctx.lineTo(i + 72, 64)
          bctx.lineTo(i + 64, 64)
          bctx.closePath()
          bctx.fill()
        }
        const bTex = new THREE.CanvasTexture(bc)
        bTex.wrapS = bTex.wrapT = THREE.RepeatWrapping
        bTex.repeat.set(Math.max(1, Math.round(len / 0.5)), 1)
        mat = new THREE.MeshStandardMaterial({
          map: bTex,
          roughness: 0.7,
          metalness: 0.2,
          depthWrite: false,
        })
      }

      const m = new THREE.Mesh(new THREE.BoxGeometry(len, h, 0.2), mat)
      m.position.set((w.x0 + w.x1) / 2, h / 2, (w.z0 + w.z1) / 2)
      if (Math.abs(w.x1 - w.x0) < Math.abs(w.z1 - w.z0)) m.rotation.y = Math.PI / 2
      this.wallGroup.add(m)
    })

    // Warehouse roof
    const roofH = (shell.walls?.length ? shell.walls[0].h : 3.5) ?? 3.5
    const roofMat = new THREE.MeshStandardMaterial({
      color: 0x374151,
      transparent: true,
      opacity: 0.3,
      side: THREE.DoubleSide,
      depthWrite: false,
      roughness: 0.9,
      metalness: 0.05,
    })
    const roofMesh = new THREE.Mesh(new THREE.PlaneGeometry(B.w, B.d), roofMat)
    roofMesh.rotation.x = -Math.PI / 2
    roofMesh.position.y = roofH
    this.wallGroup.add(roofMesh)

    this.rootGrp.add(this.wallGroup)

    if (!this._shellFramed) {
      this._shellFramed = true
      this.tR = Math.max(this.tR, Math.min(B.w, B.d) * 1.05)
      if (this.scene.fog) this.scene.fog.far = Math.max(this.scene.fog.far, Math.max(B.w, B.d) * 2.4)
    }
  }

  buildMarkings(shell: ShellBlueprint): void {
    if (this.markingsGroup) this.markingsGroup.visible = false
    this.markingsGroup = new THREE.Group()

    const markings = shell.markings || []
    if (!markings.length) return

    markings.forEach((mk) => {
      const isH = mk.type === 'hazard_border'
      const mat = new THREE.MeshBasicMaterial({
        color: mk.color,
        transparent: true,
        opacity: 0.7,
        depthWrite: false,
        side: THREE.DoubleSide,
      })

      for (let i = 0; i < mk.pts.length - 1; i++) {
        const [x0, z0] = mk.pts[i]
        const [x1, z1] = mk.pts[i + 1]
        const dx = x1 - x0
        const dz = z1 - z0
        const len = Math.hypot(dx, dz)
        if (len < 0.01) continue

        if (mk.dashed) {
          const dash = 1.0
          const gap = 0.5
          const step = dash + gap
          const nD = Math.max(1, Math.floor(len / step))
          for (let d = 0; d < nD; d++) {
            const t0 = d / len
            const t1 = Math.min((d + dash) / len, 1)
            const sl = (t1 - t0) * len
            if (sl < 0.01) continue
            const g = new THREE.PlaneGeometry(sl, mk.width)
            const m = new THREE.Mesh(g, mat)
            const mx = x0 + (t0 + t1) / 2 * dx
            const mz = z0 + (t0 + t1) / 2 * dz
            m.position.set(mx, 0.02, mz)
            m.rotation.order = 'YXZ'
            m.rotation.y = -Math.atan2(dz, dx)
            m.rotation.x = -Math.PI / 2
            this.markingsGroup.add(m)
          }
        } else {
          const g = new THREE.PlaneGeometry(len, mk.width)
          const m = new THREE.Mesh(g, mat)
          m.position.set((x0 + x1) / 2, 0.02, (z0 + z1) / 2)
          m.rotation.order = 'YXZ'
          m.rotation.y = -Math.atan2(dz, dx)
          m.rotation.x = -Math.PI / 2
          this.markingsGroup.add(m)
        }
      }
    })

    this.rootGrp.add(this.markingsGroup)
  }

  setShowWalls(show: boolean): void {
    if (this.wallGroup) this.wallGroup.visible = show
  }

  setShowMarkings(show: boolean): void {
    if (this.markingsGroup) this.markingsGroup.visible = show
  }

  setDarkMode(isDark: boolean): void {
    const bgCol = isDark ? 0x0c0e14 : 0xf0f2f5
    this.scene.background.setHex(bgCol)
    if (this.scene.fog) this.scene.fog.color.setHex(bgCol)
    this.renderer.setClearColor(bgCol, 1)
  }

  centerView(): void {
    this.tT = 0.65
    this.tP = 0.78
    this.tR = Math.max(28, this.radius * 0.8)
    this.tPX = 0
    this.tPZ = 0
  }

  highlight(key: string | null): void {
    if (this._highlightMesh) {
      this.rootGrp.remove(this._highlightMesh)
      this._highlightMesh = undefined
    }

    if (!key) return

    const mesh = this.meshMap[key]
    if (!mesh) return

    const box = new THREE.Box3().setFromObject(mesh)
    const size = box.getSize(new THREE.Vector3())
    const center = box.getCenter(new THREE.Vector3())

    const geo = new THREE.BoxGeometry(size.x + 0.1, size.y + 0.1, size.z + 0.1)
    const mat = new THREE.MeshBasicMaterial({
      color: 0x3b82f6,
      transparent: true,
      opacity: 0.3,
      depthWrite: false,
      side: THREE.DoubleSide,
    })
    this._highlightMesh = new THREE.Mesh(geo, mat)
    this._highlightMesh.position.copy(center)
    this.rootGrp.add(this._highlightMesh)
  }

  // Placeholder methods for zone builders - implemented in zones/index.ts
  buildZone(zone: Zone, slots: Slot[]): void {
    if (zone.type === 'rack' || zone.type === 'flow_rack') {
      this.buildRackZone(zone, slots)
    } else if (zone.type === 'automated') {
      this.buildAsrsZone(zone)
    } else if (zone.type === 'high_rack') {
      this.buildHighRackZone(zone)
    } else if (zone.type === 'mezzanine') {
      this.buildMezzanineZone(zone)
    } else if (zone.type === 'temp_bagged') {
      this.buildTempBaggedZone(zone)
    } else if (zone.type === 'returns') {
      this.buildReturnsZone(zone)
    } else {
      this.buildTempZone(zone)
    }
  }

  buildRackZone(zone: Zone, slots: Slot[]): void {
    // Import dynamically to avoid circular dependency
    import('./zones/rack').then(({ buildRackZone: buildRack }) => {
      buildRack(this, zone, slots)
    })
  }

  buildAsrsZone(zone: Zone): void {
    // Placeholder - implemented in zones/asrs.ts
  }

  buildHighRackZone(zone: Zone): void {
    // Placeholder - implemented in zones/highRack.ts
  }

  buildMezzanineZone(zone: Zone): void {
    // Placeholder - implemented in zones/mezzanine.ts
  }

  buildTempZone(zone: Zone): void {
    // Placeholder - implemented in zones/temp.ts
  }

  buildTempBaggedZone(zone: Zone): void {
    // Placeholder - implemented in zones/tempBagged.ts
  }

  buildReturnsZone(zone: Zone): void {
    // Placeholder - implemented in zones/returns.ts
  }

  buildFacilities(facilities: any[], shell: ShellBlueprint | undefined): void {
    // Placeholder - implemented in facilities/index.ts
  }

  buildDocks(docks: any[], shell: ShellBlueprint | undefined): void {
    // Placeholder - implemented in docks/index.ts
  }

  buildVehicles(vehicles: any[], shell: ShellBlueprint | undefined): void {
    // Placeholder - implemented in vehicles/index.ts
  }

  bindMouse(cwEl: HTMLElement, onHover: HoverCallback, onClick: ClickCallback): void {
    const canvas = this.canvas

    const getPickResult = (event: MouseEvent): { result: PickResult | null; isSelected: boolean } => {
      const rect = canvas.getBoundingClientRect()
      const x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      const y = -((event.clientY - rect.top) / rect.height) * 2 + 1

      const raycaster = new THREE.Raycaster()
      raycaster.setFromCamera(new THREE.Vector2(x, y), this.camera)
      const hits = raycaster.intersectObjects(this.pickables, true)

      if (!hits.length) return { result: null, isSelected: false }

      let obj: THREE.Object3D | null = hits[0].object
      while (obj && !obj.userData.kind) obj = obj.parent

      if (!obj?.userData.kind) return { result: null, isSelected: false }

      const kind = obj.userData.kind as PickResult['kind']
      const ref = obj.userData.ref || ''
      const wasSelected = this.selKey === ref

      return {
        result: { kind, ref, name: obj.userData.name, slot: obj.userData.slot, lv: obj.userData.lv, vehicleRef: obj.userData.vehicleRef },
        isSelected: wasSelected,
      }
    }

    let clickTimeout: ReturnType<typeof setTimeout> | null = null
    let lastClickTime = 0

    canvas.addEventListener('mousemove', (e) => {
      const { result } = getPickResult(e)
      const rect = canvas.getBoundingClientRect()
      onHover(result, e.clientX - rect.left, e.clientY - rect.top)
    })

    canvas.addEventListener('mousedown', (e) => {
      if (e.button === 2) return // Ignore right-click
      this.lx = e.clientX
      this.ly = e.clientY
      if (e.button === 1) {
        this.rDrag = true
      } else {
        this.drag = true
      }
    })

    canvas.addEventListener('mouseup', (e) => {
      const dx = e.clientX - this.lx
      const dy = e.clientY - this.ly

      if (Math.abs(dx) < 5 && Math.abs(dy) < 5) {
        const now = Date.now()
        const isDouble = now - lastClickTime < 300
        lastClickTime = now

        const { result, isSelected } = getPickResult(e)

        if (result) {
          this.selKey = isSelected ? null : result.ref
          if (!isSelected) {
            onClick(result, false, isDouble)
          } else {
            onClick(null, true, false)
          }
        } else {
          onClick(null, isSelected, false)
        }
      }

      this.drag = false
      this.rDrag = false
    })

    canvas.addEventListener('wheel', (e) => {
      e.preventDefault()
      const delta = e.deltaY > 0 ? 1.1 : 0.9
      this.tR = Math.max(5, Math.min(150, this.tR * delta))
    }, { passive: false })

    canvas.addEventListener('contextmenu', (e) => e.preventDefault())
  }
}
