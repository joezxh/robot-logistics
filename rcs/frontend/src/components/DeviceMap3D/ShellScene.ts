// Three.js scene builder for a FloorShell blueprint.
// Pure geometry (no WebGL renderer) — works in jsdom for unit tests.
import * as THREE from 'three'
import type { FloorShell, Zone, WallSegment } from '@/types'
import { zoneColor } from '@/components/DeviceMap2D/option'

const ZONE_DEFAULT_HEIGHT = 3

export interface BuildResult {
  scene: THREE.Scene
  zoneMeshes: THREE.Mesh[]
  floorMesh: THREE.Mesh
  dispose: () => void
}

export function buildScene(shell: FloorShell): BuildResult {
  const scene = new THREE.Scene()
  scene.background = new THREE.Color('#0f172a')

  const { w, d } = shell.bounds

  // Floor plane (XZ), centered at origin.
  const floorGeo = new THREE.PlaneGeometry(w, d)
  const floorMat = new THREE.MeshStandardMaterial({ color: '#1e293b', side: THREE.DoubleSide })
  const floorMesh = new THREE.Mesh(floorGeo, floorMat)
  floorMesh.rotation.x = -Math.PI / 2
  floorMesh.position.set(w / 2, 0, d / 2)
  scene.add(floorMesh)

  // Zone boxes: world (x,z) bottom-left corner, center at (x+w/2, h/2, z+d/2).
  const zoneMeshes: THREE.Mesh[] = []
  for (const z of shell.zones ?? []) {
    const mesh = zoneToMesh(z)
    scene.add(mesh)
    zoneMeshes.push(mesh)
  }

  // Walls as thin boxes along each segment.
  for (const wall of shell.walls ?? []) {
    const seg = wallSegmentMesh(wall)
    if (seg) scene.add(seg)
  }

  const dispose = () => {
    scene.traverse((obj) => {
      if (obj instanceof THREE.Mesh) {
        obj.geometry.dispose()
        const m = obj.material
        if (Array.isArray(m)) m.forEach((mm) => mm.dispose())
        else m.dispose()
      }
    })
  }

  return { scene, zoneMeshes, floorMesh, dispose }
}

function zoneToMesh(z: Zone): THREE.Mesh {
  const h = ZONE_DEFAULT_HEIGHT
  const geo = new THREE.BoxGeometry(z.w, h, z.d)
  const mat = new THREE.MeshStandardMaterial({ color: zoneColor(z.type), transparent: true, opacity: 0.85 })
  const mesh = new THREE.Mesh(geo, mat)
  mesh.position.set(z.x + z.w / 2, h / 2, z.z + z.d / 2)
  mesh.name = `zone:${z.id}`
  return mesh
}

function wallSegmentMesh(wall: WallSegment) {
  const dx = wall.x1 - wall.x0
  const dz = wall.z1 - wall.z0
  const length = Math.hypot(dx, dz)
  if (length === 0) return null
  const h = wall.h ?? 3.5
  const geo = new THREE.BoxGeometry(length, h, 0.2)
  const mat = new THREE.MeshStandardMaterial({ color: '#475569' })
  const mesh = new THREE.Mesh(geo, mat)
  const cx = (wall.x0 + wall.x1) / 2
  const cz = (wall.z0 + wall.z1) / 2
  mesh.position.set(cx, h / 2, cz)
  // rotate around Y to align with segment direction
  mesh.rotation.y = -Math.atan2(dz, dx)
  mesh.name = `wall:${wall.id}`
  return mesh
}

// Build a camera + renderer-ready scene wrapper (used by the Vue component).
export function createShellScene(shell: FloorShell): BuildResult {
  return buildScene(shell)
}
