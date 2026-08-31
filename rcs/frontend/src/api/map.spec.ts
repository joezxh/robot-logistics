import { describe, it, expect, vi, beforeEach } from 'vitest'
import { http } from './http'
import {
  listMaps,
  getMap,
  createMap,
  updateMap,
  deleteMap,
  listTemplates,
  seedTemplates,
  createFromTemplate,
  importMap,
  exportMap,
  listVersions,
  restoreVersion,
  listDynamic,
  putDynamic,
  deleteDynamic,
  type UnifiedMapDTO,
  type MapTemplateInfo,
  type DynamicStateDTO,
} from './map'

// `http` is a module-level singleton (an HttpClient instance built from
// import.meta.env), so mocking the module is the cleanest way to assert on the
// paths this client builds — stubbing `globalThis.fetch` instead would only
// prove the URL ends up correct, not that the client asked for it.
vi.mock('./http', () => ({
  http: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    request: vi.fn(),
  },
}))

type MockFn = ReturnType<typeof vi.fn>

const httpMock = http as unknown as {
  get: MockFn
  post: MockFn
  put: MockFn
  delete: MockFn
}

/** Minimal but type-checked GET /maps/{id} response. */
function mapFixture(over: Partial<UnifiedMapDTO> = {}): UnifiedMapDTO {
  return {
    map_id: 'tpl-x',
    name: '示例仓',
    name_en: 'Demo WH',
    is_template: true,
    kind: 'warehouse',
    current_version: 1,
    bounds: { w: 160, d: 100 },
    geometry: { bounds: { w: 160, d: 100 }, zones: [] },
    topology: { nodes: [], edges: [] },
    semantic: { scenario: 'ecommerce' },
    dynamic: {},
    created_at: '2026-01-01T00:00:00',
    updated_at: '2026-01-02T00:00:00',
    ...over,
  }
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('map API — relative paths', () => {
  it('getMap GETs /maps/:id relative to the /api/rcs base URL', async () => {
    const payload = mapFixture()
    httpMock.get.mockResolvedValueOnce(payload)

    const out = await getMap('tpl-x')

    // NOT '/api/rcs/maps/tpl-x' — http.baseUrl already defaults to '/api/rcs',
    // so an /api/rcs prefix here would double up into /api/rcs/api/rcs/...
    expect(httpMock.get).toHaveBeenCalledWith('/maps/tpl-x')
    expect(out).toEqual(payload)
    expect(out.geometry.bounds.w).toBe(160)
  })

  it('every request this client issues is a relative /maps path', async () => {
    httpMock.get.mockResolvedValue([])
    httpMock.post.mockResolvedValue({})
    httpMock.put.mockResolvedValue({})
    httpMock.delete.mockResolvedValue(undefined)

    await listMaps()
    await getMap('m1')
    await createMap({ name: 'n' })
    await updateMap('m1', { name: 'n' })
    await deleteMap('m1')
    await listTemplates()
    await seedTemplates()
    await createFromTemplate('k')
    await importMap('m1', {})
    await exportMap('m1')
    await listVersions('m1')
    await restoreVersion('m1', 'v1')
    await listDynamic('m1')
    await putDynamic('m1', 'z1', { state: 'free' })
    await deleteDynamic('m1', 'z1')

    const paths = [
      ...httpMock.get.mock.calls,
      ...httpMock.post.mock.calls,
      ...httpMock.put.mock.calls,
      ...httpMock.delete.mock.calls,
    ].map((c) => c[0] as string)

    expect(paths).toHaveLength(15)
    for (const p of paths) {
      expect(p.startsWith('/maps')).toBe(true)
      expect(p.startsWith('/api')).toBe(false)
    }
  })
})

describe('map API — maps CRUD', () => {
  it('listMaps defaults to include_templates=false', async () => {
    httpMock.get.mockResolvedValueOnce([mapFixture({ is_template: false })])

    const out = await listMaps()

    expect(httpMock.get).toHaveBeenCalledWith('/maps?include_templates=false')
    expect(out[0].is_template).toBe(false)
  })

  it('listMaps(true) asks the backend for templates too', async () => {
    httpMock.get.mockResolvedValueOnce([])
    await listMaps(true)
    expect(httpMock.get).toHaveBeenCalledWith('/maps?include_templates=true')
  })

  it('createMap POSTs the unified body to /maps', async () => {
    httpMock.post.mockResolvedValueOnce(mapFixture({ map_id: 'new', is_template: false }))
    const body = {
      name: 'My WH',
      geometry: { bounds: { w: 10, d: 20 } },
      topology: { nodes: [], edges: [] },
      semantic: {},
      is_template: false,
      kind: 'warehouse',
    }

    const out = await createMap(body)

    expect(httpMock.post).toHaveBeenCalledWith('/maps', body)
    expect(out.map_id).toBe('new')
  })

  it('updateMap PUTs to /maps/:id and encodes the map id', async () => {
    httpMock.put.mockResolvedValueOnce(mapFixture({ map_id: 'my/map' }))

    await updateMap('my/map', { name: 'renamed' })

    expect(httpMock.put).toHaveBeenCalledWith('/maps/my%2Fmap', { name: 'renamed' })
  })

  it('deleteMap DELETEs /maps/:id (204 → undefined)', async () => {
    httpMock.delete.mockResolvedValueOnce(undefined)

    const out = await deleteMap('m1')

    expect(httpMock.delete).toHaveBeenCalledWith('/maps/m1')
    expect(out).toBeUndefined()
  })
})

describe('map API — templates', () => {
  it('listTemplates returns the slim {map_id, name, name_en, kind} shape', async () => {
    const rows: MapTemplateInfo[] = [
      { map_id: 'tpl-ecommerce_large', name: '大型电商仓', name_en: 'Large Ecommerce', kind: 'warehouse' },
      { map_id: 'tpl-ecommerce', name: 'Ecommerce', name_en: 'Ecommerce', kind: 'scenario' },
    ]
    httpMock.get.mockResolvedValueOnce(rows)

    const out = await listTemplates()

    expect(httpMock.get).toHaveBeenCalledWith('/maps/templates')
    expect(out).toHaveLength(2)
    expect(out[0].map_id).toBe('tpl-ecommerce_large')
    expect(out[0].kind).toBe('warehouse')
    // The unified endpoint is slimmer than the legacy
    // warehouseTemplates.WarehouseTemplateInfo: no site_id / category / bounds.
    expect(Object.keys(out[0])).not.toContain('site_id')
    expect((out[0] as unknown as Record<string, unknown>).site_id).toBeUndefined()
  })

  it('seedTemplates POSTs an empty body to /maps/templates/seed', async () => {
    httpMock.post.mockResolvedValueOnce([mapFixture()])

    const out = await seedTemplates()

    expect(httpMock.post).toHaveBeenCalledWith('/maps/templates/seed', {})
    expect(out).toHaveLength(1)
  })

  it('createFromTemplate POSTs {template_key, name} to /maps/from-template', async () => {
    httpMock.post.mockResolvedValueOnce(mapFixture({ map_id: 'live-1', is_template: false }))

    const out = await createFromTemplate('ecommerce_large', 'My WH')

    expect(httpMock.post).toHaveBeenCalledWith('/maps/from-template', {
      template_key: 'ecommerce_large',
      name: 'My WH',
    })
    expect(out.is_template).toBe(false)
  })
})

describe('map API — import / export / versions', () => {
  it('importMap POSTs the bundle to /maps/:id/import', async () => {
    httpMock.post.mockResolvedValueOnce(mapFixture())
    const bundle = { geometry: { bounds: { w: 1, d: 2 } }, topology: { nodes: [], edges: [] } }

    await importMap('m1', bundle)

    expect(httpMock.post).toHaveBeenCalledWith('/maps/m1/import', bundle)
  })

  it('exportMap GETs /maps/:id/export', async () => {
    httpMock.get.mockResolvedValueOnce({
      map_id: 'm1',
      name: 'My WH',
      geometry: { bounds: { w: 1, d: 2 } },
      topology: { nodes: [], edges: [] },
      semantic: {},
    })

    const out = await exportMap('m1')

    expect(httpMock.get).toHaveBeenCalledWith('/maps/m1/export')
    expect(out.map_id).toBe('m1')
  })

  it('listVersions GETs /maps/:id/versions (empty until versioning lands)', async () => {
    httpMock.get.mockResolvedValueOnce([])

    const out = await listVersions('m1')

    expect(httpMock.get).toHaveBeenCalledWith('/maps/m1/versions')
    expect(out).toEqual([])
  })

  it('restoreVersion POSTs to the encoded /maps/:id/versions/:vid/restore path', async () => {
    httpMock.post.mockResolvedValueOnce(mapFixture())

    await restoreVersion('m1', 'v 1')

    expect(httpMock.post).toHaveBeenCalledWith('/maps/m1/versions/v%201/restore', {})
  })
})

describe('map API — dynamic state', () => {
  it('listDynamic GETs /maps/:id/dynamic', async () => {
    const rows: DynamicStateDTO[] = [
      { element_id: 'z1', state: 'occupied', payload: { robot: 'R1' }, updated_at: null },
    ]
    httpMock.get.mockResolvedValueOnce(rows)

    const out = await listDynamic('m1')

    expect(httpMock.get).toHaveBeenCalledWith('/maps/m1/dynamic')
    expect(out[0].element_id).toBe('z1')
  })

  it('putDynamic PUTs /maps/:id/dynamic/:element_id', async () => {
    const row: DynamicStateDTO = {
      element_id: 'z1',
      state: 'occupied',
      payload: null,
      updated_at: '2026-01-01T00:00:00',
    }
    httpMock.put.mockResolvedValueOnce(row)

    const out = await putDynamic('m1', 'z1', { state: 'occupied' })

    expect(httpMock.put).toHaveBeenCalledWith('/maps/m1/dynamic/z1', { state: 'occupied' })
    expect(out.state).toBe('occupied')
  })

  it('putDynamic forwards a payload as well as a state', async () => {
    httpMock.put.mockResolvedValueOnce({ element_id: 'd1', state: 'open', payload: { q: 3 } })

    await putDynamic('m1', 'd1', { state: 'open', payload: { q: 3 } })

    expect(httpMock.put).toHaveBeenCalledWith('/maps/m1/dynamic/d1', {
      state: 'open',
      payload: { q: 3 },
    })
  })

  it('deleteDynamic DELETEs /maps/:id/dynamic/:element_id', async () => {
    httpMock.delete.mockResolvedValueOnce(undefined)

    const out = await deleteDynamic('m1', 'z1')

    expect(httpMock.delete).toHaveBeenCalledWith('/maps/m1/dynamic/z1')
    expect(out).toBeUndefined()
  })
})
