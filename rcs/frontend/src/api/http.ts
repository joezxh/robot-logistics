// Thin fetch-based HTTP client with a configurable base URL.
// Honors VITE_API_BASE at build time, otherwise defaults to '/api/rcs'.

export interface HttpClientOptions {
  baseUrl?: string
  fetchFn?: typeof fetch
}

export class HttpClient {
  readonly baseUrl: string
  private readonly fetchFn: typeof fetch

  constructor(opts: HttpClientOptions = {}) {
    this.baseUrl = opts.baseUrl ?? import.meta.env?.VITE_API_BASE ?? '/api/rcs'
    this.fetchFn = opts.fetchFn ?? (globalThis.fetch?.bind(globalThis) as typeof fetch)
  }

  async request<T>(path: string, init?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${path}`
    const res = await this.fetchFn(url, {
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
      ...init,
    })
    if (!res.ok) {
      let detail: unknown = res.statusText
      try {
        detail = await res.json()
      } catch {
        /* ignore parse errors */
      }
      throw new Error(`HTTP ${res.status}: ${JSON.stringify(detail)}`)
    }
    if (res.status === 204) return undefined as T
    const text = await res.text()
    return (text ? JSON.parse(text) : undefined) as T
  }

  get<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'GET' })
  }

  post<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>(path, { method: 'POST', body: JSON.stringify(body) })
  }

  put<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>(path, { method: 'PUT', body: JSON.stringify(body) })
  }
  delete<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'DELETE' })
  }
}

export const http = new HttpClient()
