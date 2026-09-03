import { describe, it, expect, vi, beforeEach } from 'vitest'
import * as THREE from 'three'
import { MjcfLoader } from './MjcfLoader'

/** Minimal MJCF with two revolute joints + a primitive geom (no mesh) so the
 *  loader path can be exercised without real OBJ assets. */
const SAMPLE_XML = `<?xml version="1.0"?>
<mujoco model="test_arm">
  <compiler meshdir="assets"/>
  <asset>
    <material name="red" rgba="0.8 0.1 0.1 1"/>
  </asset>
  <worldbody>
    <body name="base" pos="0 0 0.1">
      <joint name="j1" axis="0 0 1" range="-1.5 1.5"/>
      <geom type="box" size="0.1 0.1 0.05" material="red"/>
      <body name="link2" pos="0 0 0.3">
        <joint name="j2" axis="1 0 0" range="-3 3"/>
        <geom type="sphere" size="0.08" material="red"/>
      </body>
    </body>
  </worldbody>
</mujoco>`

describe('MjcfLoader.load (stubbed fetch/OBJ)', () => {
  beforeEach(() => {
    // Stub fetch to return the sample XML.
    globalThis.fetch = vi.fn(async () => ({
      ok: true,
      status: 200,
      text: async () => SAMPLE_XML,
    })) as any
  })

  it('builds a joint hierarchy and applies joint angles', async () => {
    const robot = await MjcfLoader.load('/sim-assets/robots/test_arm/test_arm.xml', {
      baseUrl: '/sim-assets/robots/test_arm/test_arm.xml',
      showCollision: false,
    })
    expect(robot.modelName).toBe('test_arm')
    expect(robot.joints.size).toBe(2)
    expect(robot.joints.has('j1')).toBe(true)
    expect(robot.joints.has('j2')).toBe(true)

    // Drive j1 to 1.0 rad (within range) and verify the pivot rotated about Z.
    robot.setJointAngle('j1', 1.0)
    const j1 = robot.joints.get('j1')!
    const e = new THREE.Euler().setFromQuaternion(j1.group.quaternion, 'XYZ')
    expect(Math.abs(e.z - 1.0)).toBeLessThan(1e-6)
    expect(Math.abs(e.x)).toBeLessThan(1e-6)
    expect(Math.abs(e.y)).toBeLessThan(1e-6)

    // Out-of-range value is clamped.
    robot.setJointAngle('j1', 99)
    const e2 = new THREE.Euler().setFromQuaternion(j1.group.quaternion, 'XYZ')
    expect(Math.abs(e2.z - 1.5)).toBeLessThan(1e-6)
  })

  it('exposes joint state via getJointState', async () => {
    const robot = await MjcfLoader.load('/x.xml', { baseUrl: '/x.xml' })
    robot.setJointAngle('j2', -2.0)
    const state = robot.getJointState()
    expect(state['j2']).toBeCloseTo(-2.0, 3)
  })

  it('attaches geom meshes under the joint pivot so rotation propagates', async () => {
    const robot = await MjcfLoader.load('/x.xml', { baseUrl: '/x.xml' })
    const j2 = robot.joints.get('j2')!
    // The sphere geom of link2 should be a descendant of j2's pivot group.
    let found = false
    j2.group.traverse((o) => {
      if ((o as THREE.Mesh).isMesh) found = true
    })
    expect(found).toBe(true)
  })
})
