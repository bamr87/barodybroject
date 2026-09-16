import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError, api, getCsrfToken, listAll, request, setCsrfToken } from './client'

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json' },
  })
}

describe('api client', () => {
  beforeEach(() => {
    setCsrfToken('test-token')
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('sends the CSRF token on unsafe methods only', async () => {
    // A Response body can only be read once, so each call needs a fresh one.
    const fetchMock = vi.fn().mockImplementation(async () => jsonResponse({ ok: true }))
    vi.stubGlobal('fetch', fetchMock)

    await api.get('/api/threads/')
    await api.post('/api/threads/', { name: 'x' })

    const [, getInit] = fetchMock.mock.calls[0]
    const [, postInit] = fetchMock.mock.calls[1]
    expect(getInit.headers['X-CSRFToken']).toBeUndefined()
    expect(postInit.headers['X-CSRFToken']).toBe('test-token')
    expect(postInit.credentials).toBe('same-origin')
    expect(JSON.parse(postInit.body)).toEqual({ name: 'x' })
  })

  it('refreshes the token when the session says so', () => {
    setCsrfToken('fresh')
    expect(getCsrfToken()).toBe('fresh')
    // An empty token must not clobber a working one.
    setCsrfToken('')
    expect(getCsrfToken()).toBe('fresh')
  })

  it('drops empty query parameters', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]))
    vi.stubGlobal('fetch', fetchMock)

    await request('/api/messages/', { params: { thread: 'abc', assistant: undefined, q: '' } })

    expect(fetchMock.mock.calls[0][0]).toBe('/api/messages/?thread=abc')
  })

  it('raises ApiError carrying the server detail', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ detail: 'Claude declined the request' }, 502)),
    )

    await expect(api.post('/api/threads/1/run/')).rejects.toMatchObject({
      name: 'ApiError',
      status: 502,
      detail: 'Claude declined the request',
    })
  })

  it('exposes DRF field errors from a 400', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({ name: ['This field is required.'] }, 400)))

    try {
      await api.post('/api/assistants/', {})
      expect.unreachable('should have thrown')
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError)
      expect((error as ApiError).fieldErrors).toEqual({ name: ['This field is required.'] })
    }
  })

  it('explains a 403 in plain language', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('', { status: 403 })))

    await expect(api.get('/api/threads/')).rejects.toThrow(/not signed in/i)
  })

  it('follows pagination until the last page', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ count: 3, next: 'http://testserver/api/posts/?page=2', previous: null, results: [1, 2] }),
      )
      .mockResolvedValueOnce(jsonResponse({ count: 3, next: null, previous: null, results: [3] }))
    vi.stubGlobal('fetch', fetchMock)

    await expect(listAll<number>('/api/posts/')).resolves.toEqual([1, 2, 3])
    expect(fetchMock.mock.calls[1][0]).toBe('/api/posts/?page=2')
  })

  it('accepts an unpaginated list unchanged', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse([{ id: 1 }])))

    await expect(listAll<{ id: number }>('/api/providers/')).resolves.toEqual([{ id: 1 }])
  })
})
