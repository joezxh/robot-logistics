/**
 * MjcfLoader — load a MuJoCo MJCF model into a three.js scene.
 *
 * MuJoCo XML (MJCF) is *not* a format three.js can read directly. This loader
 * bridges the gap on the client: it fetches the `.xml`, walks the `worldbody`
 * tree and rebuilds it as a hierarchy of `THREE.Object3D`s where every
 * `<joint>` becomes a pivot `Group` (so joint angles can be driven live, e.g.
 * from an MQTT/SSE digital-twin feed), and every `<geom>` becomes a mesh or a
 * primitive (box / sphere / capsule / cylinder) coloured by its `<material>`.
 *
 * Visual meshes are referenced from `<asset><mesh file=.../></asset>` and loaded
 * with `OBJLoader` (the robot assets in `simulation/backend/assets` ship `.obj`
 * visual meshes). The mesh path is resolved relative to the MJCF document URL
 * through `meshdir`.
 *
 * This is intentionally lightweight: it depends only on `three` and the bundled
 * `OBJLoader`. It does *not* run physics (MuJoCo does that) — it is a renderer /
 * visualiser that can be driven from simulation joint state.
 */
import * as THREE from 'three'
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'

export interface MjcfLoadOptions {
  /** Base URL that the MJCF document is fetched from. Mesh references are
   *  resolved against `new URL(meshFile, baseUrl)` after applying `meshdir`.
   *  If the MJCF is served from e.g. `/sim-assets/robots/ur5e/ur5e.xml`, pass
   *  that same URL here. */
  baseUrl: string
  /** Render collision-group geoms (capsules/cylinders) too. Default false —
   *  usually only the visual meshes are wanted for a clean render. */
  showCollision?: boolean
  /** Group index to render. MJCF `geom group="N"`. Default 2 (visual). */
  visualGroup?: number
  /** On-demand material resolver override (advanced). */
  materialResolver?: (name: string) => THREE.Material
}

interface JointNode {
  name: string
  group: THREE.Group
  axis: THREE.Vector3
  range: [number, number] | null
  qpos0: number
  /** Last applied angle (radians), for read-back via getJointState(). */
  applied: number
  /** Degrees of freedom: 1 for hinge/slide, 6 for a freejoint. */
  dof: number
  /** True for 6-DOF floating-base joints (positioned via setFreeJointPose). */
  freejoint: boolean
}

interface AssetMesh {
  file: string
}

interface AssetMaterial {
  name: string
  rgba: [number, number, number, number] | null
}

/** Parse "a b c d" into a number[] (MJCF space-separated attributes). */
function parseVec(s: string | null | undefined): number[] {
  if (!s) return []
  return s.trim().split(/\s+/).map(Number)
}

/** Mesh assets are keyed by file name without a mesh extension (obj or stl). */
function meshKey(file: string): string {
  return file.replace(/\.(obj|stl)$/i, '')
}

/** Parse "w x y z" quaternion into THREE.Quaternion (MuJoCo is xyzw order). */
function parseQuat(q: string | null | undefined): THREE.Quaternion {
  const v = parseVec(q)
  if (v.length !== 4) return new THREE.Quaternion()
  return new THREE.Quaternion(v[1], v[2], v[3], v[0]) // x,y,z,w
}

function parsePos(p: string | null | undefined): THREE.Vector3 {
  const v = parseVec(p)
  if (v.length !== 3) return new THREE.Vector3()
  return new THREE.Vector3(v[0], v[1], v[2])
}

export class MjcfRobot {
  readonly root: THREE.Group
  readonly joints: Map<string, JointNode> = new Map()
  readonly modelName: string
  private objLoader = new OBJLoader()
  private stlLoader = new STLLoader()

  constructor(modelName: string) {
    this.modelName = modelName
    this.root = new THREE.Group()
    this.root.name = `mjcf:${modelName}`
  }

  /** Set a joint's angle (radians). Out-of-range values are clamped. */
  setJointAngle(name: string, rad: number): void {
    const j = this.joints.get(name)
    if (!j) return
    if (j.freejoint) return // freejoints are posed via setFreeJointPose()
    let v = rad
    if (j.range) v = Math.min(j.range[1], Math.max(j.range[0], v))
    const delta = v - j.qpos0
    j.group.setRotationFromAxisAngle(j.axis, delta)
    j.applied = v
  }

  /**
   * Pose a 6-DOF freejoint: `q = [x, y, z, qw, qx, qy, qz]`.
   * Positions the freejoint body in world space (no child-chain rotation).
   */
  setFreeJointPose(q: number[] | Float32Array | Float64Array): void {
    const j = this.joints.get('trunk_base_freejoint')
    if (!j || !j.freejoint) return
    const pos = [q[0], q[1], q[2]]
    // THREE.Quaternion components are (x, y, z, w); MuJoCo qpos is (qw, qx, qy, qz).
    j.group.position.fromArray(pos)
    j.group.quaternion.set(q[4], q[5], q[6], q[3])
  }

  /** Read current joint angles (radians) for all joints. */
  getJointState(): Record<string, number> {
    const out: Record<string, number> = {}
    this.joints.forEach((j, name) => {
      out[name] = j.applied
    })
    return out
  }

  /** Load a referenced mesh (OBJ or STL), cached by file name. */
  async loadMesh(file: string, baseUrl: string, meshdir: string): Promise<THREE.Object3D | null> {
    const url = new URL(meshdir ? `${meshdir}/${file}` : file, baseUrl).href
    if (/\.stl$/i.test(file)) {
      // STLLoader resolves to a BufferGeometry; wrap it in a Mesh.
      const geom = await this.stlLoader.loadAsync(url)
      const mesh = new THREE.Mesh(
        geom,
        new THREE.MeshStandardMaterial({ color: 0xcccccc, metalness: 0.1, roughness: 0.8 }),
      )
      mesh.name = meshKey(file)
      return mesh
    }
    const obj = await this.objLoader.loadAsync(url)
    return obj
  }
}

export class MjcfLoader {
  /** Load an MJCF document from `xmlUrl` and return a renderable robot model. */
  static async load(xmlUrl: string, options?: Partial<MjcfLoadOptions>): Promise<MjcfRobot> {
    const res = await fetch(xmlUrl)
    if (!res.ok) {
      throw new Error(`MjcfLoader: failed to fetch ${xmlUrl} (${res.status})`)
    }
    const text = await res.text()
    const doc = new DOMParser().parseFromString(text, 'application/xml')
    const mj = doc.querySelector('mujoco')
    if (!mj) throw new Error('MjcfLoader: <mujoco> root not found')

    const modelName = mj.getAttribute('model') || 'model'
    const robot = new MjcfRobot(modelName)

    const compiler = mj.querySelector('compiler')
    const meshdir = compiler?.getAttribute('meshdir') || ''
    const baseUrl = options?.baseUrl ?? xmlUrl

    // ── assets ──
    const materials = new Map<string, AssetMaterial>()
    mj.querySelectorAll('asset > material').forEach((el) => {
      const name = el.getAttribute('name') || el.getAttribute('class') || ''
      const rgba = parseVec(el.getAttribute('rgba'))
      materials.set(name, {
        name,
        rgba: rgba.length === 4 ? [rgba[0], rgba[1], rgba[2], rgba[3]] : null,
      })
    })
    const meshes = new Map<string, AssetMesh>()
    mj.querySelectorAll('asset > mesh').forEach((el) => {
      const file = el.getAttribute('file')
      if (file) meshes.set(meshKey(file), { file })
    })

    const showCollision = options?.showCollision ?? false
    const visualGroup = options?.visualGroup ?? 2

    const defaultMaterial = new THREE.MeshStandardMaterial({
      color: 0x999999,
      metalness: 0.1,
      roughness: 0.6,
    })

    const resolveMaterial = (name: string | null): THREE.Material => {
      if (options?.materialResolver && name) return options.materialResolver(name)
      if (name && materials.has(name)) {
        const m = materials.get(name)!
        if (m.rgba) {
          return new THREE.MeshStandardMaterial({
            color: new THREE.Color(m.rgba[0], m.rgba[1], m.rgba[2]),
            transparent: m.rgba[3] < 1,
            opacity: m.rgba[3],
            metalness: 0.2,
            roughness: 0.55,
          })
        }
      }
      return defaultMaterial
    }

    // ── worldbody ──
    const world = mj.querySelector('worldbody')
    if (world) {
      for (const bodyEl of Array.from(world.children)) {
        if (bodyEl.tagName.toLowerCase() !== 'body') continue
        const node = await MjcfLoader.buildBody(bodyEl, robot, {
          baseUrl,
          meshdir,
          meshes,
          resolveMaterial,
          showCollision,
          visualGroup,
        })
        robot.root.add(node)
      }
    }

    return robot
  }

  private static async buildBody(
    bodyEl: Element,
    robot: MjcfRobot,
    ctx: {
      baseUrl: string
      meshdir: string
      meshes: Map<string, AssetMesh>
      resolveMaterial: (n: string | null) => THREE.Material
      showCollision: boolean
      visualGroup: number
    },
  ): Promise<THREE.Group> {
    const bodyGroup = new THREE.Group()
    bodyGroup.name = bodyEl.getAttribute('name') || 'body'
    const pos = parsePos(bodyEl.getAttribute('pos'))
    if (pos.lengthSq() > 0) bodyGroup.position.copy(pos)
    const quat = parseQuat(bodyEl.getAttribute('quat'))
    if (!quat.equals(new THREE.Quaternion())) bodyGroup.quaternion.copy(quat)

    // joints -> pivot groups (a body may have 0..n joints; typically 1)
    // `freejoint` carries the floating-base DOF and is parsed like a joint.
    const jointEls = Array.from(bodyEl.children).filter((c) => {
      const t = c.tagName.toLowerCase()
      return t === 'joint' || t === 'freejoint'
    })
    let attachUnder: THREE.Object3D = bodyGroup
    for (const je of jointEls) {
      const jg = new THREE.Group()
      jg.name = `joint:${je.getAttribute('name') || 'j'}`
      const axis = parseVec(je.getAttribute('axis'))
      const axisVec = axis.length === 3 ? new THREE.Vector3(axis[0], axis[1], axis[2]).normalize() : new THREE.Vector3(0, 1, 0)
      const rangeAttr = je.getAttribute('range')
      const range = parseVec(rangeAttr)
      const jtype = je.tagName.toLowerCase() === 'freejoint'
        ? 'free'
        : (je.getAttribute('type') || 'hinge').toLowerCase()
      const isFree = jtype === 'free'
      const joint: JointNode = {
        name: je.getAttribute('name') || '',
        group: jg,
        axis: axisVec,
        range: range.length === 2 ? [range[0], range[1]] : null,
        qpos0: 0,
        applied: 0,
        dof: isFree ? 6 : 1,
        freejoint: isFree,
      }
      if (joint.name) robot.joints.set(joint.name, joint)
      attachUnder.add(jg)
      attachUnder = jg
    }

    // geoms
    for (const g of Array.from(bodyEl.children).filter((c) => c.tagName.toLowerCase() === 'geom')) {
      const obj = await MjcfLoader.buildGeom(g, robot, ctx)
      if (obj) attachUnder.add(obj)
    }

    // child bodies
    for (const cb of Array.from(bodyEl.children).filter((c) => c.tagName.toLowerCase() === 'body')) {
      const child = await MjcfLoader.buildBody(cb, robot, ctx)
      attachUnder.add(child)
    }

    return bodyGroup
  }

  private static async buildGeom(
    g: Element,
    robot: MjcfRobot,
    ctx: {
      baseUrl: string
      meshdir: string
      meshes: Map<string, AssetMesh>
      resolveMaterial: (n: string | null) => THREE.Material
      showCollision: boolean
      visualGroup: number
    },
  ): Promise<THREE.Object3D | null> {
    const group = g.getAttribute('class') // e.g. "visual" | "collision" | "eef_collision"
    const isCollision = group === 'collision' || group === 'eef_collision'
    if (isCollision && !ctx.showCollision) return null

    const type = g.getAttribute('type') || (g.getAttribute('mesh') ? 'mesh' : 'box')
    const material = ctx.resolveMaterial(g.getAttribute('material'))
    const gpos = parsePos(g.getAttribute('pos'))
    const gquat = parseQuat(g.getAttribute('quat'))
    const size = parseVec(g.getAttribute('size')) // radii/lengths, MJCF semantics per type

    let mesh3d: THREE.Object3D | null = null

    if (type === 'mesh') {
      const meshName = g.getAttribute('mesh')
      const asset = meshName ? ctx.meshes.get(meshKey(meshName)) : undefined
      if (asset) {
        try {
          mesh3d = await robot.loadMesh(asset.file, ctx.baseUrl, ctx.meshdir)
        } catch (e) {
          console.warn(`MjcfLoader: failed to load mesh ${asset.file}:`, e)
          mesh3d = null
        }
      }
      if (!mesh3d) return null
      mesh3d.traverse((o) => {
        if ((o as THREE.Mesh).isMesh) {
          const m = o as THREE.Mesh
          m.material = material
          m.castShadow = true
          m.receiveShadow = true
        }
      })
    } else {
      const prim = MjcfLoader.primitive(type, size, material)
      if (!prim) return null
      mesh3d = prim
    }

    mesh3d.position.copy(gpos)
    if (!gquat.equals(new THREE.Quaternion())) mesh3d.quaternion.copy(gquat)
    return mesh3d
  }

  /** Build a primitive geometry for non-mesh geoms. */
  private static primitive(
    type: string,
    size: number[],
    material: THREE.Material,
  ): THREE.Object3D | null {
    let geo: THREE.BufferGeometry | null = null
    switch (type) {
      case 'box': {
        const h = size.length >= 3 ? [size[0] * 2, size[1] * 2, size[2] * 2] : [0.1, 0.1, 0.1]
        geo = new THREE.BoxGeometry(h[0], h[1], h[2])
        break
      }
      case 'sphere': {
        const r = size.length >= 1 ? size[0] : 0.05
        geo = new THREE.SphereGeometry(r, 24, 16)
        break
      }
      case 'cylinder': {
        // MJCF cylinder: size=[radius, halflength]
        const r = size.length >= 1 ? size[0] : 0.05
        const hl = size.length >= 2 ? size[1] : 0.1
        geo = new THREE.CylinderGeometry(r, r, hl * 2, 24)
        break
      }
      case 'capsule': {
        // MJCF capsule: size=[radius, halflength]; three.js capsule axis is Y
        const r = size.length >= 1 ? size[0] : 0.05
        const hl = size.length >= 2 ? size[1] : 0.1
        geo = new THREE.CapsuleGeometry(r, hl * 2, 8, 16)
        break
      }
      default:
        return null
    }
    const mesh = new THREE.Mesh(geo, material)
    mesh.castShadow = true
    mesh.receiveShadow = true
    return mesh
  }
}
