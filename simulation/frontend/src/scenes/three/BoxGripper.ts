import * as THREE from 'three'

export class BoxGripper {
  readonly mesh: THREE.Group

  constructor() {
    this.mesh = new THREE.Group()
    this.mesh.name = 'BoxGripper'

    const palmMat = new THREE.MeshStandardMaterial({ color: 0x1f8a4c, metalness: 0.5, roughness: 0.4 })
    const fingerMat = new THREE.MeshStandardMaterial({ color: 0x2a72d8, metalness: 0.7, roughness: 0.3 })

    const palm = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.15, 0.3), palmMat)
    palm.position.y = 0.075
    this.mesh.add(palm)

    const fingerGeom = new THREE.BoxGeometry(0.05, 0.4, 0.15)
    const fingerL = new THREE.Mesh(fingerGeom, fingerMat)
    fingerL.position.set(-0.13, 0.2, 0)
    const fingerR = new THREE.Mesh(fingerGeom, fingerMat)
    fingerR.position.set(0.13, 0.2, 0)
    this.mesh.add(fingerL, fingerR)

    const grooveMat = new THREE.MeshStandardMaterial({ color: 0x0d2a5c, roughness: 0.9 })
    for (let i = 0; i < 4; i++) {
      const groove = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.02, 0.16), grooveMat)
      groove.position.set(-0.13, 0.05 + i * 0.08, 0)
      this.mesh.add(groove)
      const grooveR = groove.clone()
      grooveR.position.set(0.13, 0.05 + i * 0.08, 0)
      this.mesh.add(grooveR)
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