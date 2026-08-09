/**
 * Procedural 6-DOF robot arm built from basic Three.js geometries.
 * Phase 1: simple cylinders/boxes aligned with URDF link dimensions.
 * Phase 2: replace with GLTF model.
 */
import * as THREE from 'three'

const LINK_DIMS = {
  base: { radius: 0.08, height: 0.1 },
  shoulder: { radius: 0.06, height: 0.15 },
  upper_arm: { radius: 0.05, height: 0.425 },
  forearm: { radius: 0.04, height: 0.392 },
  wrist: { radius: 0.03, height: 0.08 },
}

const JOINT_NAMES = [
  'shoulder_pan', 'shoulder_lift', 'elbow',
  'wrist_1', 'wrist_2', 'wrist_3',
]

export type ArmStatus = 'idle' | 'moving' | 'error' | 'estop'

const STATUS_COLORS: Record<ArmStatus, number> = {
  idle: 0x888888,
  moving: 0x3b82f6,
  error: 0xef4444,
  estop: 0xff0000,
}

export class RobotArm {
  public group: THREE.Group
  private joints: THREE.Group[] = []
  private targets: number[] = new Array(6).fill(0)
  private current: number[] = new Array(6).fill(0)
  private status: ArmStatus = 'idle'
  private meshes: THREE.Mesh[] = []
  private lerpAlpha = 0.3

  constructor() {
    this.group = new THREE.Group()
    this.group.name = 'RobotArm'
    this.build()
  }

  private build() {
    const mat = new THREE.MeshStandardMaterial({ color: STATUS_COLORS.idle })

    // base_link
    const base = new THREE.Mesh(
      new THREE.CylinderGeometry(LINK_DIMS.base.radius, LINK_DIMS.base.radius, LINK_DIMS.base.height, 16),
      mat.clone()
    )
    base.position.y = LINK_DIMS.base.height / 2
    this.group.add(base)
    this.meshes.push(base)

    // Build kinematic chain: each joint is a Group that rotates around Y or Z
    const jointAxes: ('y' | 'z')[] = ['y', 'z', 'z', 'z', 'y', 'z']
    const links = [
      { name: 'shoulder', r: LINK_DIMS.shoulder.radius, h: LINK_DIMS.shoulder.height },
      { name: 'upper_arm', r: LINK_DIMS.upper_arm.radius, h: LINK_DIMS.upper_arm.height },
      { name: 'forearm', r: LINK_DIMS.forearm.radius, h: LINK_DIMS.forearm.height },
      { name: 'wrist_1', r: LINK_DIMS.wrist.radius, h: LINK_DIMS.wrist.height },
      { name: 'wrist_2', r: LINK_DIMS.wrist.radius, h: LINK_DIMS.wrist.height },
      { name: 'wrist_3', r: LINK_DIMS.wrist.radius, h: LINK_DIMS.wrist.height },
    ]

    let parent = this.group
    for (let i = 0; i < 6; i++) {
      const pivot = new THREE.Group()
      pivot.name = JOINT_NAMES[i]
      // Position pivot at top of previous link
      if (i === 0) {
        pivot.position.y = LINK_DIMS.base.height
      } else {
        pivot.position.y = links[i - 1].h
      }
      parent.add(pivot)
      this.joints.push(pivot)

      const link = links[i]
      const mesh = new THREE.Mesh(
        new THREE.CylinderGeometry(link.r, link.r, link.h, 12),
        mat.clone()
      )
      mesh.position.y = link.h / 2
      // Rotate mesh so cylinder aligns with joint axis
      if (jointAxes[i] === 'z') {
        mesh.rotation.x = Math.PI / 2
        mesh.position.y = 0
        mesh.position.z = link.h / 2
      }
      pivot.add(mesh)
      this.meshes.push(mesh)
      parent = pivot
    }
  }

  /** Set target joint positions (radians). Actual positions lerp toward targets. */
  setJointPositions(positions: number[]) {
    for (let i = 0; i < Math.min(positions.length, 6); i++) {
      this.targets[i] = positions[i]
    }
  }

  setStatus(status: ArmStatus) {
    if (this.status === status) return
    this.status = status
    const color = STATUS_COLORS[status]
    this.meshes.forEach(m => {
      (m.material as THREE.MeshStandardMaterial).color.setHex(color)
    })
  }

  /** Per-frame update: lerp joints toward targets. */
  update(_dt: number) {
    for (let i = 0; i < 6; i++) {
      this.current[i] += (this.targets[i] - this.current[i]) * this.lerpAlpha
      const axis = i === 0 || i === 4 ? 'y' : 'z'
      ;(this.joints[i].rotation as any)[axis] = this.current[i]
    }
  }

  addToScene(scene: THREE.Scene, position?: THREE.Vector3) {
    if (position) this.group.position.copy(position)
    scene.add(this.group)
  }
}
