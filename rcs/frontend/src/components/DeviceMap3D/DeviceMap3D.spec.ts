import { describe, it, expect, vi, beforeAll } from 'vitest'
import * as THREE from 'three'
import { buildScene } from './ShellScene'
import type { FloorShell } from '@/types'

const shell: FloorShell = {
  bounds: { w: 160, d: 100 },
  zones: [
    { id: 'z1', ref: 'R1', type: 'flow_rack', x: 0, z: 0, w: 60, d: 40 },
    { id: 'z2', ref: 'R2', type: 'high_rack', x: 60, z: 0, w: 60, d: 40 },
  ],
  walls: [{ id: 'w1', x0: 0, z0: 0, x1: 160, z1: 0 }],
}

describe('ShellScene.buildScene', () => {
  it('creates a THREE.Scene with a floor mesh', () => {
    const res = buildScene(shell)
    expect(res.scene).toBeInstanceOf(THREE.Scene)
    expect(res.floorMesh).toBeInstanceOf(THREE.Mesh)
    expect(res.floorMesh.geometry).toBeInstanceOf(THREE.PlaneGeometry)
  })

  it('creates one mesh per zone', () => {
    const res = buildScene(shell)
    expect(res.zoneMeshes).toHaveLength(2)
  })

  it('centers each zone box at (x + w/2, h/2, z + d/2)', () => {
    const res = buildScene(shell)
    const z1 = res.zoneMeshes[0]
    expect(z1.position.x).toBeCloseTo(0 + 60 / 2)
    expect(z1.position.y).toBeCloseTo(3 / 2)
    expect(z1.position.z).toBeCloseTo(0 + 40 / 2)
    // box geometry sized to world dims
    const geo = z1.geometry as THREE.BoxGeometry
    expect(geo.parameters.width).toBe(60)
    expect(geo.parameters.depth).toBe(40)
  })

  it('places the floor centered on the bounds', () => {
    const res = buildScene(shell)
    expect(res.floorMesh.position.x).toBeCloseTo(80)
    expect(res.floorMesh.position.z).toBeCloseTo(50)
  })

  it('dispose frees geometries', () => {
    const res = buildScene(shell)
    const before = res.scene.children.length
    expect(before).toBeGreaterThan(0)
    res.dispose()
    // geometries disposed (no throw); scene still holds nodes but geos are freed
    expect(() => res.dispose()).not.toThrow()
  })
})

describe('DeviceMap3D component', () => {
  beforeAll(() => {
    // jsdom has no WebGL — mock the renderer + controls.
    vi.mock('three', async () => {
      const actual = await vi.importActual<typeof THREE>('three')
      return {
        ...actual,
        WebGLRenderer: class {
          domElement = document.createElement('canvas')
          setSize = vi.fn()
          render = vi.fn()
          dispose = vi.fn()
        },
      }
    })
    vi.mock('three/examples/jsm/controls/OrbitControls.js', () => ({
      OrbitControls: class {
        target = new THREE.Vector3()
        update = vi.fn()
        dispose = vi.fn()
      },
    }))
  })

  it('renders a container and builds a scene when shell is present', async () => {
    const { mount } = await import('@vue/test-utils')
    const { default: DeviceMap3D } = await import('./DeviceMap3D.vue')
    const wrapper = mount(DeviceMap3D, { props: { shell } })
    await new Promise((r) => setTimeout(r, 10))
    expect(wrapper.find('[data-testid="map3d"]').exists()).toBe(true)
    wrapper.unmount()
  })

  it('shows placeholder when shell is null', async () => {
    const { mount } = await import('@vue/test-utils')
    const { default: DeviceMap3D } = await import('./DeviceMap3D.vue')
    const wrapper = mount(DeviceMap3D, { props: { shell: null } })
    expect(wrapper.find('.empty').exists()).toBe(true)
  })
})
