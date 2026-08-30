import * as THREE from 'three'

export class BagGripper {
  readonly mesh: THREE.Group

  constructor() {
    this.mesh = new THREE.Group()
    this.mesh.name = 'BagGripper'

    const plateMat = new THREE.MeshStandardMaterial({ color: 0x8b6f3c, roughness: 0.7 })
    const plateGeom = new THREE.BoxGeometry(0.5, 0.3, 0.25)
    const plate = new THREE.Mesh(plateGeom, plateMat)
    plate.position.y = 0.15
    this.mesh.add(plate)

    const toothMat = new THREE.MeshStandardMaterial({ color: 0x444444, roughness: 0.95 })
    const toothGeom = new THREE.BoxGeometry(0.04, 0.05, 0.06)
    for (let x = -0.2; x <= 0.2; x += 0.1) {
      for (let z = -0.1; z <= 0.1; z += 0.1) {
        const tooth = new THREE.Mesh(toothGeom, toothMat)
        tooth.position.set(x, 0.32, z)
        this.mesh.add(tooth)
      }
    }
  }

  dispose(): void {
    this.mesh.traverse((obj) => {
      const m = obj as THREE.Mesh
      if (m.geometry) m.geometry.dispose()
      const mat = m.material
      if (Array.isArray(mat)) mat.forEach((mm) => mm.dispose())
      else if (mat) (mat as THREE.Material).dispose()
    })
  }
}