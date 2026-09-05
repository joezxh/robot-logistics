// Where the warehouse *geometry* comes from.
//
// Split by layer (see ../adapters/floorShell.ts for the data mapping):
//   geometry  -> RCS unified-maps import blueprint (FloorShell)
//   inventory -> simulation backend, until RCS gains an inventory domain
//
// NOTE: the legacy `topology/shell` router was removed (see
// rcs/backend/rcs/api/__init__.py) in favour of the unified-maps import API, so
// geometry is now produced by the import blueprint preview endpoint.
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
 * Resolve the floor shell from the unified-maps import blueprint preview:
 *
 *   `GET /api/rcs/import/warehouse-theatre/preview` — converts the built-in
 *   blueprint on the fly. This is the single source of truth since the legacy
 *   `topology/shell` router was removed (it 404s).
 *
 * Returns `null` when the RCS backend is unreachable, so the caller falls back
 * to the simulation backend's geometry and the page still renders.
 */
export async function fetchWarehouseShell(): Promise<ShellSource | null> {
  try {
    const preview = await previewWarehouseTheatre()
    if (preview?.shell) return { shell: preview.shell, origin: 'preview' }
  } catch {
    // RCS backend unreachable — caller keeps the simulation backend's geometry.
  }
  return null
}
