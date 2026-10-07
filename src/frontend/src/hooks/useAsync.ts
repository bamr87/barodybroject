import { useCallback, useEffect, useRef, useState } from 'react'

import { ApiError } from '../api/client'

export interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: string | null
  /** Re-run the loader. */
  reload: () => void
  /** Replace the data locally, e.g. after a mutation returns the new row. */
  setData: (value: T | null) => void
}

/**
 * Load data on mount and whenever `deps` change.
 *
 * The in-flight request is aborted when the component unmounts or the deps
 * change, so a slow response for a screen the user has left cannot overwrite
 * the state of the screen they are on.
 */
export function useAsync<T>(loader: (signal: AbortSignal) => Promise<T>, deps: unknown[]): AsyncState<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [nonce, setNonce] = useState(0)
  const loaderRef = useRef(loader)
  loaderRef.current = loader

  useEffect(() => {
    const controller = new AbortController()
    let active = true
    setLoading(true)
    setError(null)
    loaderRef
      .current(controller.signal)
      .then((value) => {
        if (active) {
          setData(value)
          setLoading(false)
        }
      })
      .catch((err: unknown) => {
        if (!active || controller.signal.aborted) return
        setError(err instanceof ApiError ? err.detail : String(err))
        setLoading(false)
      })
    return () => {
      active = false
      controller.abort()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce])

  const reload = useCallback(() => setNonce((n) => n + 1), [])
  return { data, loading, error, reload, setData }
}

/**
 * Run a mutation, tracking pending state and surfacing errors as strings.
 * Returns `null` when the call failed, so callers can branch without try/catch.
 */
export function useAction(): {
  run: <T>(fn: () => Promise<T>) => Promise<T | null>
  pending: boolean
  error: string | null
  clearError: () => void
} {
  const [pending, setPending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const mounted = useRef(true)
  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])

  const run = useCallback(async <T,>(fn: () => Promise<T>): Promise<T | null> => {
    setPending(true)
    setError(null)
    try {
      return await fn()
    } catch (err: unknown) {
      if (mounted.current) setError(err instanceof ApiError ? err.detail : String(err))
      return null
    } finally {
      if (mounted.current) setPending(false)
    }
  }, [])

  return { run, pending, error, clearError: useCallback(() => setError(null), []) }
}
