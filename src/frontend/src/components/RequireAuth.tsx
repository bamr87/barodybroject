import type { ReactNode } from 'react'

import { useApp } from '../AppContext'
import { EmptyState } from './ui'

/**
 * Gate for every authoring screen.
 *
 * Authentication is Django's (allauth), so an unauthenticated visitor is sent
 * to the server-rendered sign-in page rather than a React form, with `next`
 * set so they land back where they were.
 */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { auth } = useApp()
  if (auth?.authenticated) return <>{children}</>

  const next = encodeURIComponent(window.location.pathname + window.location.search)
  const loginUrl = `${auth?.login_url ?? '/accounts/login/'}?next=${next}`
  return (
    <EmptyState icon="shield-lock" title="Sign in to continue">
      <p className="mb-3">This page needs an account.</p>
      <a className="btn btn-primary" href={loginUrl}>
        <i className="bi bi-box-arrow-in-right me-1" aria-hidden="true" />
        Sign in
      </a>
    </EmptyState>
  )
}
