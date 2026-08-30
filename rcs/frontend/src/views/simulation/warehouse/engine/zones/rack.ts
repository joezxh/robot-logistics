/**
 * Rack Zone Builder
 * Renders rack/flow_rack zones with slot-based storage visualization
 */
import * as THREE from 'three'
import type { ThreeEngine } from '../ThreeEngine'
import type { Zone, Slot } from '../../types'

const LV = 1.1       // Level height
const RACK_W = 2.4   // Rack width (X)
const RACK_D = 1.0   // Rack depth (Z)
const BAY_D = 2.4    // Bay depth
const CORRIDOR = 1.2 // Corridor width

// Color helper for the HTML/2D view. The numeric twin (`FC`) was unused.
function FCH(p: number): string {
  return p >= 90 ? '#f87171' : p >= 70 ? '#fb923c' : p >= 40 ? '#facc15' : '#4ade80'
}

function lvFill(lv: any): number {
  const wc = (lv.uoms || []).filter((u: any) => u.cap > 0)
  if (!wc.length) return (lv.uoms || []).some((u: any) => u.qty > 0) ? 50 : 0
  return Math.round(wc.reduce((s: number, u: any) => s + Math.min(100, Math.round((u.qty / u.cap) * 100)), 0) / wc.length)
}

function hasStock(lv: any): boolean {
  return (lv.uoms || []).some((u: any) => u.qty > 0)
}

export function buildRackZone(engine: ThreeEngine, zone: Zone, slots: Slot[]): void {
  const zoneSlots = slots.filter(s => {
    const label = s.label || s.wh || ''
    const ref = zone.ref || ''
    return label.includes(ref) || ref === 'LEGACY'
  })

  if (!zoneSlots.length) return

  // Calculate grid dimensions
  const rows: Record<number, Slot[]> = {}
  zoneSlots.forEach(s => {
    const row = s.row ?? 0
    if (!rows[row]) rows[row] = []
    rows[row].push(s)
  })

  const sortedRows = Object.keys(rows).map(Number).sort((a, b) => a - b)
  const maxCols = Math.max(...sortedRows.map(r => rows[r].length))

  const totalW = maxCols * (RACK_W + CORRIDOR) + CORRIDOR
  const totalD = sortedRows.length * BAY_D

  // Create rack structure using InstancedMesh
  const rackMesh = createRackStructure(engine, zone, zoneSlots, rows, sortedRows, totalW, totalD)
  engine.pickables.push(rackMesh)

  // Create goods boxes
  const goodsMesh = createGoodsBoxes(engine, zone, zoneSlots, rows, sortedRows, totalW, totalD)
  if (goodsMesh) engine.pickables.push(goodsMesh)

  // Zone chrome (label)
  addZoneChrome(engine, zone)
}

function createRackStructure(
  engine: ThreeEngine,
  zone: Zone,
  zoneSlots: Slot[],
  rows: Record<number, Slot[]>,
  sortedRows: number[],
  totalW: number,
  totalD: number
): THREE.InstancedMesh {
  const totalInstances = zoneSlots.reduce((sum, s) => sum + s.levels.length, 0)

  const geometry = new THREE.BoxGeometry(RACK_W, 0.06, RACK_D)
  const material = new THREE.MeshStandardMaterial({
    color: 0x64748b,
    roughness: 0.7,
    metalness: 0.3,
  })

  const mesh = new THREE.InstancedMesh(geometry, material, totalInstances)
  const matrix = new THREE.Matrix4()

  let idx = 0
  const cols = Math.max(...sortedRows.map(r => rows[r].length))

  sortedRows.forEach((row, ri) => {
    const rowSlots = rows[row]
    for (let ci = 0; ci < cols; ci++) {
      const slot = rowSlots[ci]
      if (!slot) continue

      const x = zone.x - totalW / 2 + CORRIDOR + ci * (RACK_W + CORRIDOR) + RACK_W / 2
      const z = zone.z - totalD / 2 + ri * BAY_D + BAY_D / 2

      slot.levels.forEach((lv) => {
        const y = 0.3 + (lvFill(lv) / 100) * (LV - 0.06)
        matrix.makeTranslation(x, y / 2, z)
        mesh.setMatrixAt(idx++, matrix)
      })
    }
  })

  mesh.instanceMatrix.needsUpdate = true
  mesh.castShadow = true
  mesh.receiveShadow = true
  mesh.userData = { kind: 'zone', ref: zone.ref, name: zone.name }

  engine.rootGrp.add(mesh)
  return mesh
}

function createGoodsBoxes(
  engine: ThreeEngine,
  zone: Zone,
  // Unused: slot geometry is derived from `rows` below. Prefixed rather than
  // removed because callers pass it positionally.
  _zoneSlots: Slot[],
  rows: Record<number, Slot[]>,
  sortedRows: number[],
  totalW: number,
  totalD: number
): THREE.InstancedMesh | null {
  const occupiedSlots: { slot: Slot; lv: any; idx: number }[] = []

  sortedRows.forEach((row) => {
    const rowSlots = rows[row]
    const cols = Math.max(...sortedRows.map(r => rows[r].length))
    for (let ci = 0; ci < cols; ci++) {
      const slot = rowSlots[ci]
      if (!slot) continue

      slot.levels.forEach((lv, li) => {
        if (hasStock(lv)) {
          occupiedSlots.push({ slot, lv, idx: li })
        }
      })
    }
  })

  if (!occupiedSlots.length) return null

  const geometry = new THREE.BoxGeometry(RACK_W - 0.2, LV * 0.7, RACK_D - 0.1)
  const material = new THREE.MeshStandardMaterial({
    color: 0x60a5fa,
    roughness: 0.5,
    metalness: 0.2,
  })

  const mesh = new THREE.InstancedMesh(geometry, material, occupiedSlots.length)
  const matrix = new THREE.Matrix4()
  const maxCols = Math.max(...sortedRows.map(r => rows[r].length))

  occupiedSlots.forEach(({ slot, lv, idx }, i) => {
    const ri = sortedRows.indexOf(slot.row ?? 0)
    const x = zone.x - totalW / 2 + CORRIDOR + ((slot.col ?? 0) % maxCols) * (RACK_W + CORRIDOR) + RACK_W / 2
    const z = zone.z - totalD / 2 + ri * BAY_D + BAY_D / 2
    const y = 0.35 + idx * LV

    matrix.makeTranslation(x, y, z)
    mesh.setMatrixAt(i, matrix)

    // Set color based on fill level
    const color = new THREE.Color(FCH(lvFill(lv)))
    mesh.setColorAt(i, color)
  })

  mesh.instanceMatrix.needsUpdate = true
  if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true
  mesh.castShadow = true
  mesh.userData = { kind: 'zone', ref: zone.ref, name: zone.name }

  engine.rootGrp.add(mesh)
  return mesh
}

function addZoneChrome(engine: ThreeEngine, zone: Zone): void {
  const label = makeLabel(zone.name || zone.ref, 0xffffff)
  label.position.set(zone.x, 4, zone.z)
  engine.rootGrp.add(label)
}

function makeLabel(text: string, color: number): THREE.Sprite {
  const canvas = document.createElement('canvas')
  canvas.width = 512
  canvas.height = 128
  const ctx = canvas.getContext('2d')!
  ctx.fillStyle = 'rgba(0,0,0,0.6)'
  ctx.fillRect(0, 0, 512, 128)
  ctx.fillStyle = `#${color.toString(16).padStart(6, '0')}`
  ctx.font = 'bold 48px sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText(text, 256, 80)

  const texture = new THREE.CanvasTexture(canvas)
  const material = new THREE.SpriteMaterial({ map: texture, transparent: true })
  const sprite = new THREE.Sprite(material)
  sprite.scale.set(6, 1.5, 1)
  return sprite
}
