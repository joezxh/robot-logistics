/**
 * Composite loader robot: AGV base + dual arms + hug paddles.
 */
import * as THREE from 'three'
import { RobotArm } from './RobotArm'
import { AgvBase } from './AgvBase'

export class LoaderRobot {
  public group: THREE.Group
  public base: AgvBase
  public leftArm: RobotArm
  public rightArm: RobotArm
  private paddles: THREE.Mesh[] = []

  constructor() {
    this.group = new THREE.Group()
    this.group.name = 'LoaderRobot'
    this.base = new AgvBase()
    this.leftArm = new RobotArm()
    this.rightArm = new RobotArm()
    this.build()
  }

  private build() {
    this.group.add(this.base.group)

    // Position arms on left/right sides of chassis
    this.leftArm.group.position.set(-0.25, 0.2, 0)
    this.group.add(this.leftArm.group)
    this.rightArm.group.position.set(0.25, 0.2, 0)
    this.group.add(this.rightArm.group)

    // Hug paddles (prismatic joints)
    const paddleMat = new THREE.MeshStandardMaterial({ color: 0xed8936 })
    const paddleGeom = new THREE.BoxGeometry(0.02, 0.3, 0.15)
    for (const side of [-1, 1]) {
      const paddle = new THREE.Mesh(paddleGeom, paddleMat)
      paddle.position.set(side * 0.35, 0.35, 0)
      this.group.add(paddle)
      this.paddles.push(paddle)
    }
  }

  setJointPositions(positions: number[]) {
    // Split 14 joints: base(0) + left_arm(1-6) + right_arm(7-12) + paddles(13)
    if (positions.length >= 7) {
      this.leftArm.setJointPositions(positions.slice(1, 7))
    }
    if (positions.length >= 13) {
      this.rightArm.setJointPositions(positions.slice(7, 13))
    }
  }

  update(dt: number) {
    this.leftArm.update(dt)
    this.rightArm.update(dt)
  }

  addToScene(scene: THREE.Scene, position?: THREE.Vector3) {
    if (position) this.group.position.copy(position)
    scene.add(this.group)
  }
}
