# Task 10 Brief — BoxGripper + BagGripper

## Files

- **Create**: `d:\projects\robot-logic\simulation\frontend\src\scenes\three\BoxGripper.ts`
- **Create**: `d:\projects\robot-logic\simulation\frontend\src\scenes\three\BagGripper.ts`

## Step 1: BoxGripper.ts（verbatim）

```typescript
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
```

## Step 2: BagGripper.ts（verbatim）

```typescript
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
```

## Step 3: 类型检查

```bash
cd "d:/projects/robot-logic/simulation/frontend" && npx vue-tsc --noEmit
```

## Step 4: 提交

```bash
cd d:/projects/robot-logic
git add simulation/frontend/src/scenes/three/BoxGripper.ts
git add simulation/frontend/src/scenes/three/BagGripper.ts
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): add BoxGripper + BagGripper end-effectors"
```

## Return

`Status: DONE | commit: <7位> | test: <一行> | concerns: <无或简要>`