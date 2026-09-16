import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'

import { setCsrfToken } from './api/client'
import { auth as authApi, site as siteApi } from './api/endpoints'
import type { AuthState, SiteInfo } from './api/types'

interface AppContextValue {
  auth: AuthState | null
  site: SiteInfo | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

const AppContext = createContext<AppContextValue>({
  auth: null,
  site: null,
  loading: true,
  error: null,
  refresh: async () => {},
})

/**
 * Loads the session and site metadata once and shares them app-wide.
 *
 * The CSRF token travels with the who-am-I response, so refreshing this
 * context is also how the app recovers a token after signing in elsewhere.
 */
export function AppProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState | null>(null)
  const [site, setSite] = useState<SiteInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const authState = await authApi.me()
      setCsrfToken(authState.csrf_token)
      setAuth(authState)
      // Site metadata is public, but only worth fetching once signed in.
      setSite(await siteApi.info())
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const value = useMemo(
    () => ({ auth, site, loading, error, refresh }),
    [auth, site, loading, error, refresh],
  )
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useApp(): AppContextValue {
  return useContext(AppContext)
}
