// HTTP client for the system-administration API (/api/sys/**).
//
// Extends the project's plain `fetch` wrapper from `./http` with:
//   * an `Authorization: Bearer <token>` header injected from localStorage
//   * a normalised error object carrying the status code and server detail
//   * a 401 hook that clears the session so the router guard can redirect
//
// The legacy /api/rcs client (`./http`) is intentionally left untouched.

const TOKEN_KEY = 'rcs.console.token'

export interface SysHttpOptions {
  baseUrl?: string
  fetchFn?: typeof fetch
}

/** Raised for any non-2xx response; `detail` holds the server message. */
export class ApiError extends Error {
  readonly status: number
  readonly detail: unknown

  constructor(status: number, detail: unknown, message?: string) {
    super(message ?? `HTTP ${status}`)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

/** Human-readable message extracted from a FastAPI error body. */
export function extractDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail
  if (detail && typeof detail === 'object') {
    const rec = detail as Record<string, unknown>
    if (typeof rec.detail === 'string') return rec.detail
    if (typeof rec.message === 'string') return rec.message
    if (Array.isArray(rec.detail)) {
      // Pydantic validation errors: [{loc, msg, type}, ...]
      return rec.detail
        .map((d) => (d && typeof d === 'object' ? ((d as Record<string, unknown>).msg as string) : String(d)))
        .join('; ')
    }
  }
  return ''
}

export class SysHttpClient {
  readonly baseUrl: string
  private readonly fetchFn: typeof fetch
  /** Called when the server rejects the token so the caller can reset state. */
  onUnauthorized: (() => void) | null = null

  constructor(opts: SysHttpOptions = {}) {
    this.baseUrl = opts.baseUrl ?? import.meta.env?.VITE_SYS_API_BASE ?? '/api/sys'
    this.fetchFn = opts.fetchFn ?? (globalThis.fetch?.bind(globalThis) as typeof fetch)
  }

  static get token(): string {
    try {
      return globalThis.localStorage?.getItem(TOKEN_KEY) ?? ''
    } catch {
      return ''
    }
  }

  static setToken(token: string): void {
    try {
      if (token) globalThis.localStorage?.setItem(TOKEN_KEY, token)
      else globalThis.localStorage?.removeItem(TOKEN_KEY)
    } catch {
      /* storage unavailable (SSR / privacy mode) — session stays in memory */
    }
  }

  static clearToken(): void {
    SysHttpClient.setToken('')
  }

  private headers(init?: RequestInit): HeadersInit {
    const base: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept-Language': currentLocale(),
    }
    const token = SysHttpClient.token
    if (token) base.Authorization = `Bearer ${token}`
    return { ...base, ...(init?.headers as Record<string, string> | undefined) }
  }

  async request<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await this.fetchFn(`${this.baseUrl}${path}`, {
      ...init,
      headers: this.headers(init),
    })

    if (!res.ok) {
      let detail: unknown = res.statusText
      try {
        detail = await res.json()
      } catch {
        /* body was empty or not JSON */
      }
      if (res.status === 401) this.onUnauthorized?.()
      throw new ApiError(res.status, detail, extractDetail(detail) || `HTTP ${res.status}`)
    }
    if (res.status === 204) return undefined as T
    const text = await res.text()
    return (text ? JSON.parse(text) : undefined) as T
  }

  get<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'GET' })
  }

  post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, { method: 'POST', body: body === undefined ? undefined : JSON.stringify(body) })
  }

  put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, { method: 'PUT', body: body === undefined ? undefined : JSON.stringify(body) })
  }

  delete<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'DELETE' })
  }
}

/** Locale used for the `Accept-Language` header (kept in sync by the app store). */
function currentLocale(): string {
  try {
    return globalThis.localStorage?.getItem('rcs.console.locale') ?? 'zh-CN'
  } catch {
    return 'zh-CN'
  }
}

export const sysHttp = new SysHttpClient()

/** Build a query string, skipping null/undefined/empty values. */
export function qs<T extends object>(params: T): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params as Record<string, unknown>)) {
    if (value === undefined || value === null || value === '') continue
    search.set(key, String(value))
  }
  const s = search.toString()
  return s ? `?${s}` : ''
}
