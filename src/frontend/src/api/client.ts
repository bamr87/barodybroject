/**
 * Thin typed wrapper over fetch for the Django REST API.
 *
 * Authentication is the ordinary Django session cookie. Unsafe methods need
 * the CSRF token, which is read from the `csrf-token` meta tag the SPA shell
 * renders and refreshed from `GET /api/auth/me/`, so a login in another tab
 * cannot leave the app posting with a stale token.
 */

import type { Paginated } from './types'

export class ApiError extends Error {
  readonly status: number
  readonly detail: string
  readonly body: unknown

  constructor(status: number, detail: string, body: unknown) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
    this.body = body
  }

  /** Field-level errors from a DRF serializer, if the failure was a 400. */
  get fieldErrors(): Record<string, string[]> {
    if (this.status !== 400 || typeof this.body !== 'object' || this.body === null) return {}
    const out: Record<string, string[]> = {}
    for (const [key, value] of Object.entries(this.body as Record<string, unknown>)) {
      if (key === 'detail') continue
      out[key] = Array.isArray(value) ? value.map(String) : [String(value)]
    }
    return out
  }
}

function readMetaToken(): string {
  if (typeof document === 'undefined') return ''
  return document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content ?? ''
}

let csrfToken = readMetaToken()

export function setCsrfToken(token: string): void {
  if (token) csrfToken = token
}

export function getCsrfToken(): string {
  return csrfToken
}

const UNSAFE = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

async function parseBody(response: Response): Promise<unknown> {
  const type = response.headers.get('content-type') ?? ''
  if (response.status === 204) return null
  if (type.includes('application/json')) return response.json()
  return response.text()
}

function messageFor(status: number, body: unknown): string {
  if (typeof body === 'string' && body.trim()) return body.slice(0, 300)
  if (body && typeof body === 'object') {
    const record = body as Record<string, unknown>
    if (typeof record.detail === 'string') return record.detail
    const first = Object.entries(record)[0]
    if (first) {
      const [field, value] = first
      const text = Array.isArray(value) ? value.join(' ') : String(value)
      return `${field}: ${text}`
    }
  }
  if (status === 403) return 'You are not signed in, or your session expired.'
  return `Request failed (HTTP ${status})`
}

export interface RequestOptions {
  method?: string
  body?: unknown
  signal?: AbortSignal
  /** Query string parameters; empty values are dropped. */
  params?: Record<string, string | number | boolean | undefined | null>
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, signal, params } = options
  let url = path
  if (params) {
    const search = new URLSearchParams()
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== '') search.set(key, String(value))
    }
    const query = search.toString()
    if (query) url += (url.includes('?') ? '&' : '?') + query
  }

  const headers: Record<string, string> = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (UNSAFE.has(method.toUpperCase())) headers['X-CSRFToken'] = csrfToken

  const response = await fetch(url, {
    method,
    headers,
    credentials: 'same-origin',
    body: body === undefined ? undefined : JSON.stringify(body),
    signal,
  })

  const parsed = await parseBody(response)
  if (!response.ok) throw new ApiError(response.status, messageFor(response.status, parsed), parsed)
  return parsed as T
}

export const api = {
  get: <T>(path: string, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'GET' }),
  post: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'POST', body: body ?? {} }),
  put: <T>(path: string, body: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'PUT', body }),
  patch: <T>(path: string, body: unknown, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'PATCH', body }),
  delete: <T>(path: string, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(path, { ...options, method: 'DELETE' }),
}

/**
 * Fetch every page of a paginated list endpoint.
 *
 * The lists in this app are small (assistants, schemas, threads), and the UI
 * filters and sorts client-side, so loading them whole keeps the components
 * simple. `limit` stops a runaway loop if the API ever returns a huge set.
 */
export async function listAll<T>(
  path: string,
  options: Omit<RequestOptions, 'method' | 'body'> = {},
  limit = 2000,
): Promise<T[]> {
  const results: T[] = []
  let url: string | null = path
  let first = true
  while (url && results.length < limit) {
    const page: Paginated<T> | T[] = await request<Paginated<T> | T[]>(
      url,
      first ? { ...options, method: 'GET' } : { method: 'GET', signal: options.signal },
    )
    first = false
    if (Array.isArray(page)) return page
    results.push(...page.results)
    url = page.next ? new URL(page.next).pathname + new URL(page.next).search : null
  }
  return results
}
