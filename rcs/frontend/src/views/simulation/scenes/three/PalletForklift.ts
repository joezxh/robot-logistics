import * as THREE from 'three'

export class PalletForklift {
  private readonly group = new THREE.Group()
  private readonly body: THREE.Mesh
  private readonly cabin: THREE.Mesh
  private readonly mast: THREE.Group
  private readonly forks: THREE.Group
  private readonly load: THREE.Group
  private targetMast = 0
  private currentMast = 0
  private targetExt = 0
  private currentExt = 0

  constructor() {
    const bodyGeom = new THREE.BoxGeometry(1.6, 0.6, 1.0)
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0xd68910, metalness: 0.4, roughness: 0.6 })
    this.body = new THREE.Mesh(bodyGeom, bodyMat)
    this.body.position.y = 0.3
    this.group.add(this.body)

    const cabinGeom = new THREE.BoxGeometry(0.6, 0.8, 1.0)
    const cabinMat = new THREE.MeshStandardMaterial({ color: 0x1c2333, roughness: 0.4 })
    this.cabin = new THREE.Mesh(cabinGeom, cabinMat)
    this.cabin.position.set(-0.4, 1.0, 0)
    this.group.add(this.cabin)

    const wheelGeom = new THREE.CylinderGeometry(0.2, 0.2, 0.18, 16)
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.9 })
    const wheelPositions: [number, number][] = [
      [0.6, 0.4], [-0.6, 0.4], [0.6, -0.4], [-0.6, -0.4],
    ]
    for (const [x, z] of wheelPositions) {
      const wheel = new THREE.Mesh(wheelGeom, wheelMat)
      wheel.rotation.z = Math.PI / 2
      wheel.position.set(x, 0.2, z)
      this.group.add(wheel)
    }

    this.mast = new THREE.Group()
    const mastMat = new THREE.MeshStandardMaterial({ color: 0xb0b0b0, metalness: 0.7, roughness: 0.3 })
    const mastGeom = new THREE.BoxGeometry(0.08, 2.0, 0.08)
    const mastL = new THREE.Mesh(mastGeom, mastMat)
    mastL.position.set(0.7, 1.0, -0.3)
    const mastR = new THREE.Mesh(mastGeom, mastMat)
    mastR.position.set(0.7, 1.0, 0.3)
    this.mast.add(mastL, mastR)
    this.group.add(this.mast)

    this.forks = new THREE.Group()
    const forkMat = new THREE.MeshStandardMaterial({ color: 0xe0e0e0, metalness: 0.8, roughness: 0.2 })
    const forkGeom = new THREE.BoxGeometry(1.0, 0.05, 0.1)
    const forkL = new THREE.Mesh(forkGeom, forkMat)
    forkL.position.set(0.2, 0.0, -0.25)
    const forkR = new THREE.Mesh(forkGeom, forkMat)
    forkR.position.set(0.2, 0.0, 0.25)
    this.forks.add(forkL, forkR)
    this.mast.add(this.forks)
    this.forks.position.set(0.7, 0.3, 0)

    this.load = new THREE.Group()
    const palletMat = new THREE.MeshStandardMaterial({ color: 0xc4a76c, roughness: 0.8 })
    const palletGeom = new THREE.BoxGeometry(1.2, 0.15, 1.0)
    const palletMesh = new THREE.Mesh(palletGeom, palletMat)
    palletMesh.position.y = 0.075
    this.load.add(palletMesh)
    const boxMat = new THREE.MeshStandardMaterial({ color: 0x8b6f3c, roughness: 0.7 })
    const boxGeom = new THREE.BoxGeometry(1.0, 0.5, 0.8)
    const boxMesh = new THREE.Mesh(boxGeom, boxMat)
    boxMesh.position.y = 0.4
    this.load.add(boxMesh)
    this.load.position.set(0.7, 0.3, 0)
    this.load.visible = false
    this.mast.add(this.load)
  }

  addToScene(scene: THREE.Scene, position: THREE.Vector3): void {
    this.group.position.copy(position)
    scene.add(this.group)
  }

  setMastHeight(h: number): void {
    this.targetMast = Math.max(0, Math.min(1.8, h))
  }

  setExtension(e: number): void {
    this.targetExt = Math.max(0, Math.min(0.3, e))
  }

  setLoad(loaded: boolean): void {
    this.load.visible = loaded
  }

  update(dt: number): void {
    const k = 1 - Math.exp(-dt * 5)
    this.currentMast += (this.targetMast - this.currentMast) * k
    this.currentExt += (this.targetExt - this.currentExt) * k
    this.forks.position.y = 0.3 + this.currentMast * 0.9
    this.forks.position.x = 0.7 + this.currentExt
    this.load.position.copy(this.forks.position)
  }

  dispose(): void {
    this.group.traverse((obj) => {
      const mesh = obj as THREE.Mesh
      if (mesh.geometry) mesh.geometry.dispose()
      const mat = mesh.material
      if (Array.isArray(mat)) mat.forEach((m) => m.dispose())
      else if (mat) (mat as THREE.Material).dispose()
    })
  }
}
