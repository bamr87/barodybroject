import { useCallback, useEffect, useState } from 'react'

export type Theme = 'light' | 'dark' | 'auto'

const STORAGE_KEY = 'theme'

function stored(): Theme {
  try {
    const value = localStorage.getItem(STORAGE_KEY)
    if (value === 'light' || value === 'dark' || value === 'auto') return value
  } catch {
    // Private mode or blocked storage: fall through to the default.
  }
  return 'auto'
}

function apply(theme: Theme): void {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const resolved = theme === 'auto' ? (prefersDark ? 'dark' : 'light') : theme
  document.documentElement.setAttribute('data-bs-theme', resolved)
}

/** Bootstrap 5.3 colour mode, persisted per browser and following the OS in `auto`. */
export function useTheme(): [Theme, (next: Theme) => void] {
  const [theme, setTheme] = useState<Theme>(stored)

  useEffect(() => {
    apply(theme)
    if (theme !== 'auto') return
    const media = window.matchMedia('(prefers-color-scheme: dark)')
    const listener = () => apply('auto')
    media.addEventListener('change', listener)
    return () => media.removeEventListener('change', listener)
  }, [theme])

  const update = useCallback((next: Theme) => {
    setTheme(next)
    try {
      localStorage.setItem(STORAGE_KEY, next)
    } catch {
      // Not persisting is acceptable; the choice still applies for this page.
    }
  }, [])

  return [theme, update]
}
