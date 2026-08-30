/**
 * Procedural AGV chassis: flat box + two drive wheels.
 */
import * as THREE from 'three'

const CHASSIS = { width: 0.8, height: 0.15, depth: 0.6 }
const WHEEL = { radius: 0.075, width: 0.04 }

export class AgvBase {
  public group: THREE.Group
  private wheels: THREE.Mesh[] = []

  constructor() {
    this.group = new THREE.Group()
    this.group.name = 'AgvBase'
    this.build()
  }

  private build() {
    const chassisMat = new THREE.MeshStandardMaterial({ color: 0x4a5568, roughness: 0.6 })
    const body = new THREE.Mesh(
      new THREE.BoxGeometry(CHASSIS.width, CHASSIS.height, CHASSIS.depth),
      chassisMat
    )
    body.position.y = WHEEL.radius + CHASSIS.height / 2
    this.group.add(body)

    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x2d3748 })
    const wheelGeom = new THREE.CylinderGeometry(WHEEL.radius, WHEEL.radius, WHEEL.width, 16)
    for (const side of [-1, 1]) {
      const wheel = new THREE.Mesh(wheelGeom, wheelMat)
      wheel.rotation.x = Math.PI / 2
      wheel.position.set(0, WHEEL.radius, side * (CHASSIS.depth / 2 + WHEEL.width / 2))
      this.group.add(wheel)
      this.wheels.push(wheel)
    }
  }

  addToScene(scene: THREE.Scene | THREE.Group, position?: THREE.Vector3) {
    if (position) this.group.position.copy(position)
    scene.add(this.group)
  }
}
