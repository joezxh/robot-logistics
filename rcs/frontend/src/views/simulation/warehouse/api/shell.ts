// Where the warehouse *geometry* comes from.
//
// Split by layer (see ../adapters/floorShell.ts for the data mapping):
//   geometry  -> RCS topology API (FloorShell), single source of truth
//   inventory -> simulation backend, until RCS gains an inventory domain
import { getShell } from '@/api/topologyShell'
import { previewWarehouseTheatre } from '@/api/warehouse'
import type { FloorShell } from '@/types'

/** Same site the RCS topology editors read/write. */
export const WAREHOUSE_SITE_ID = 'warehouse-theatre-3d'

export type ShellOrigin = 'rcs' | 'preview' | 'simulation'

export interface ShellSource {
  shell: FloorShell
  origin: Exclude<ShellOrigin, 'simulation'>
}

/**
 * Resolve the floor shell, best source first:
 *
 *  1. `GET /api/rcs/topology/shell/{site}` — persisted shell; survives edits made
 *     through the RCS topology editors.
 *  2. `GET /api/rcs/import/warehouse-theatre/preview` — converts the built-in
 *     blueprint on the fly, for sites that were never imported.
 *  3. `null` — caller keeps the simulation backend's geometry, so the page
 *     still renders when the RCS backend is unreachable.
 */
export async function fetchWarehouseShell(): Promise<ShellSource | null> {
  try {
    const shell = await getShell(WAREHOUSE_SITE_ID)
    if (shell) return { shell, origin: 'rcs' }
  } catch {
    // Site not imported yet, or RCS unreachable — try the converter below.
  }
  try {
    const preview = await previewWarehouseTheatre()
    if (preview?.shell) return { shell: preview.shell, origin: 'preview' }
  } catch {
    // Fall through: the simulation backend's own geometry is the last resort.
  }
  return null
}
