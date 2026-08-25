// Pure (testable) ECharts option builder for the 2D site map.
import type { EChartsOption } from 'echarts'
import type { FloorShell, Zone } from '@/types'

export interface ZoneRect {
  id: string
  ref: string
  type: string
  // axis-space rectangle (meters): bottom-left corner + size
  x: number
  y: number
  w: number
  h: number
  color: string
}

// Color palette keyed by zone category prefix.
const PALETTE: Record<string, string> = {
  flow_rack: '#38bdf8',
  high_rack: '#0ea5e9',
  mezzanine: '#22d3ee',
  automated: '#6366f1',
  temp: '#f59e0b',
  returns: '#ef4444',
  production_line: '#a78bfa',
  wip_buffer: '#c084fc',
  parts_storage: '#818cf8',
  staging: '#64748b',
  cold_zone: '#3b82f6',
  frozen_zone: '#2563eb',
  ambient_zone: '#94a3b8',
  loading_bay: '#fbbf24',
  container_yard: '#10b981',
  customs_area: '#14b8a6',
  returns_received: '#f87171',
  qc_staging: '#fb7185',
  reshelving: '#34d399',
  disposal: '#dc2626',
  floor_1: '#7c3aed',
  floor_2: '#8b5cf6',
  floor_3: '#a855f7',
  elevator_shaft: '#e11d48',
}

export function zoneColor(type: string): string {
  return PALETTE[type] ?? '#94a3b8'
}

// Flatten a shell (or a single floor) into axis rectangles.
export function shellToRects(shell: FloorShell, floorIndex?: number): ZoneRect[] {
  const source: Zone[] = floorIndex === undefined
    ? shell.zones ?? []
    : shell.floors?.[floorIndex]?.zones ?? []
  return source.map((z: Zone) => ({
    id: z.id,
    ref: z.ref,
    type: z.type,
    x: z.x,
    y: 0, // placeholder, real y computed below
    w: z.w,
    h: z.d,
    color: zoneColor(z.type),
  }))
}

export interface MapOptionInput {
  shell: FloorShell
  floorIndex?: number
}

export function buildMapOption(input: MapOptionInput): EChartsOption {
  const { shell, floorIndex } = input
  const bounds = floorIndex === undefined
    ? shell.bounds
    : shell.floors?.[floorIndex]?.bounds ?? shell.bounds

  const zones = floorIndex === undefined
    ? shell.zones ?? []
    : shell.floors?.[floorIndex]?.zones ?? []

  const rects: ZoneRect[] = zones.map((z) => ({
    id: z.id,
    ref: z.ref,
    type: z.type,
    x: z.x,
    y: z.z, // floor-plan: z maps to y axis
    w: z.w,
    h: z.d,
    color: zoneColor(z.type),
  }))

  const data = rects.map((r) => ({
    name: r.ref,
    value: [r.x, r.y, r.w, r.h],
    itemStyle: { color: r.color },
    _zone: r,
  }))

  return {
    backgroundColor: 'transparent',
    tooltip: {
      formatter: (p: unknown) => {
        const z = (p as { data?: { _zone?: ZoneRect } }).data?._zone
        return z ? `${z.ref} (${z.type})` : ''
      },
    },
    grid: { left: 40, right: 16, top: 16, bottom: 32 },
    xAxis: {
      type: 'value',
      min: 0,
      max: bounds.w,
      name: 'X (m)',
      axisLine: { lineStyle: { color: '#475569' } },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: bounds.d,
      name: 'Z (m)',
      inverse: true, // floor plan: +z points down
      axisLine: { lineStyle: { color: '#475569' } },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    series: [
      {
        type: 'custom',
        renderItem: (_params: unknown, api: any) => {
          const [x, y, w, h] = api.value([0, 1, 2, 3])
          const p1 = api.coord([x, y])
          const p2 = api.coord([x + w, y + h])
          return {
            type: 'rect',
            shape: { x: p1[0], y: p1[1], width: p2[0] - p1[0], height: p2[1] - p1[1] },
            style: api.style(),
          }
        },
        data,
        encode: { x: [0, 2], y: [1, 3] },
      },
    ],
  }
}
