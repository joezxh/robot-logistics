import { describe, it, expect, beforeEach, vi } from 'vitest'
import * as THREE from 'three'
import { MjcfLoader } from './MjcfLoader'

// --- STL mesh loading (Microduck ships .stl meshes, not .obj) ---------------
const STL_XML = `<?xml version="1.0"?>
<mujoco model="stlbot">
  <worldbody>
    <body name="base">
      <geom type="mesh" mesh="body" />
      <joint name="j1" type="hinge" axis="0 0 1" range="-1.5 1.5" />
      <body name="link2">
        <geom type="mesh" mesh="arm" />
        <joint name="j2" type="hinge" axis="0 0 1" range="-1.5 1.5" />
      </body>
    </body>
  </worldbody>
  <asset>
    <mesh name="body" file="body.stl" />
    <mesh name="arm" file="arm.stl" />
  </asset>
</mujoco>`

// Minimal valid binary STL: 80-byte header + uint32 triangle count + 1 triangle.
function makeStlBytes(): ArrayBuffer {
  const buf = new ArrayBuffer(84 + 50)
  const dv = new DataView(buf)
  dv.setUint32(80, 1, true) // 1 triangle
  const f = (off: number, x: number, y: number, z: number) => {
    dv.setFloat32(off, x, true)
    dv.setFloat32(off + 4, y, true)
    dv.setFloat32(off + 8, z, true)
  }
  f(84, 0, 0, 0)
  f(96, 1, 0, 0)
  f(108, 0, 1, 0)
  f(120, -1, 0, 0)
  dv.setUint16(132, 0, true)
  return buf
}

describe('MjcfLoader STL meshes', () => {
  beforeEach(() => {
    global.fetch = vi.fn(async (u: any) => {
      // three's FileLoader calls fetch(new Request(url, ...)) — so `u` is a
      // Request object, and the URL lives on `u.url`, not on the arg itself.
      const url = (u && typeof u.url === 'string') ? u.url : String(u)
      if (url.endsWith('.stl')) {
        return { ok: true, status: 200, arrayBuffer: async () => makeStlBytes() } as any
      }
      return { ok: true, status: 200, text: async () => STL_XML } as any
    })
  })

  it('loads binary STL meshes referenced by geoms', async () => {
    const robot = await MjcfLoader.load('/sim-assets/robots/stlbot/stlbot.xml', {
      baseUrl: 'http://localhost/sim-assets/robots/stlbot/stlbot.xml',
    })
    let found = false
    let stlMesh = false
    robot.root.traverse((o) => {
      if ((o as THREE.Mesh).isMesh) {
        found = true
        const m = o as THREE.Mesh
        if (m.geometry && (m.geometry as THREE.BufferGeometry).isBufferGeometry) stlMesh = true
      }
    })
    expect(found).toBe(true)
    expect(stlMesh).toBe(true)
  })
})

// --- Freejoint 6-DOF (Microduck floating base) -----------------------------
const FREE_XML = `<?xml version="1.0"?>
<mujoco model="fd">
  <worldbody>
    <body name="trunk">
      <freejoint name="trunk_base_freejoint" />
      <geom type="box" size="0.1 0.1 0.1" />
    </body>
  </worldbody>
</mujoco>`

describe('MjcfLoader freejoint 6-DOF', () => {
  beforeEach(() => {
    global.fetch = vi.fn(async () => ({
      ok: true,
      status: 200,
      text: async () => FREE_XML,
    } as any))
  })

  it('registers a 6-DOF freejoint (trunk_base_freejoint)', async () => {
    const robot = await MjcfLoader.load('http://localhost/sim-assets/robots/fd.xml', {
      baseUrl: 'http://localhost/sim-assets/robots/fd.xml',
    })
    expect(robot.joints.has('trunk_base_freejoint')).toBe(true)
    const j = robot.joints.get('trunk_base_freejoint')!
    expect(j.dof).toBe(6)
    expect(j.freejoint).toBe(true)
    expect(j.axis.length()).toBeGreaterThan(0)
  })

  it('setFreeJointPose positions the freejoint body in world space', async () => {
    const robot = await MjcfLoader.load('http://localhost/sim-assets/robots/fd.xml', {
      baseUrl: 'http://localhost/sim-assets/robots/fd.xml',
    })
    robot.setFreeJointPose([0.5, 0.2, 0.3, 1, 0, 0, 0])
    // setFreeJointPose moves the freejoint pivot group (child of the trunk body),
    // which holds the 6-DOF world pose of the floating base.
    const trunk = robot.root.getObjectByName('joint:trunk_base_freejoint')
    expect(trunk).toBeTruthy()
    expect(trunk!.position.x).toBeCloseTo(0.5, 3)
    expect(trunk!.position.y).toBeCloseTo(0.2, 3)
    expect(trunk!.position.z).toBeCloseTo(0.3, 3)
    expect(Math.abs(trunk!.quaternion.w - 1)).toBeLessThan(1e-6)
  })
})
