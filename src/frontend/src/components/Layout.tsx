import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'

import { useApp } from '../AppContext'
import { useTheme, type Theme } from '../hooks/useTheme'
import { Alert, Spinner } from './ui'

const NAV = [
  { to: '/content', label: 'Content', icon: 'file-earmark-text' },
  { to: '/threads', label: 'Threads', icon: 'chat-dots' },
  { to: '/messages', label: 'Messages', icon: 'envelope' },
  { to: '/posts', label: 'Posts', icon: 'newspaper' },
  { to: '/assistants', label: 'Assistants', icon: 'robot' },
  { to: '/assistant-groups', label: 'Groups', icon: 'people' },
  { to: '/schemas', label: 'Schemas', icon: 'diagram-3' },
  { to: '/settings', label: 'Settings', icon: 'sliders' },
]

const THEMES: { value: Theme; label: string; icon: string }[] = [
  { value: 'light', label: 'Light', icon: 'sun-fill' },
  { value: 'dark', label: 'Dark', icon: 'moon-stars-fill' },
  { value: 'auto', label: 'Auto', icon: 'circle-half' },
]

function ThemeToggle() {
  const [theme, setTheme] = useTheme()
  return (
    <div className="btn-group" role="group" aria-label="Colour theme">
      {THEMES.map((option) => (
        <button
          key={option.value}
          type="button"
          className={`btn btn-sm ${theme === option.value ? 'btn-secondary' : 'btn-outline-secondary'}`}
          onClick={() => setTheme(option.value)}
          aria-pressed={theme === option.value}
          title={option.label}
        >
          <i className={`bi bi-${option.icon}`} aria-hidden="true" />
          <span className="visually-hidden">{option.label}</span>
        </button>
      ))}
    </div>
  )
}

export function Layout() {
  const { auth, site, loading, error } = useApp()
  const [navOpen, setNavOpen] = useState(false)

  if (loading) {
    return (
      <div className="container py-5">
        <Spinner label="Starting Barody Broject..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="container py-5">
        <Alert kind="danger">
          <strong>Could not reach the server.</strong> {error}
        </Alert>
      </div>
    )
  }

  return (
    <div className="d-flex flex-column min-vh-100">
      <nav className="navbar navbar-expand-lg bg-body-tertiary border-bottom">
        <div className="container-xl">
          <NavLink className="navbar-brand fw-semibold" to="/">
            <i className="bi bi-lightning-charge-fill text-warning me-2" aria-hidden="true" />
            {site?.name ?? 'Barody Broject'}
          </NavLink>
          <button
            className="navbar-toggler"
            type="button"
            aria-expanded={navOpen}
            aria-label="Toggle navigation"
            onClick={() => setNavOpen((open) => !open)}
          >
            <span className="navbar-toggler-icon" />
          </button>
          <div className={`collapse navbar-collapse ${navOpen ? 'show' : ''}`}>
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              {auth?.authenticated &&
                NAV.map((item) => (
                  <li className="nav-item" key={item.to}>
                    <NavLink
                      to={item.to}
                      className={({ isActive }) => `nav-link${isActive ? ' active fw-semibold' : ''}`}
                      onClick={() => setNavOpen(false)}
                    >
                      <i className={`bi bi-${item.icon} me-1 d-lg-none`} aria-hidden="true" />
                      {item.label}
                    </NavLink>
                  </li>
                ))}
              {site?.publications_url && (
                <li className="nav-item">
                  <a
                    className="nav-link text-nowrap"
                    href={site.publications_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Publications <i className="bi bi-box-arrow-up-right small" aria-hidden="true" />
                  </a>
                </li>
              )}
            </ul>
            <div className="d-flex align-items-center gap-2 flex-wrap">
              <ThemeToggle />
              {auth?.authenticated ? (
                <>
                  <a className="btn btn-sm btn-outline-secondary" href={site?.admin_url ?? '/admin/'}>
                    <i className="bi bi-gear me-1" aria-hidden="true" />
                    Admin
                  </a>
                  <span className="text-muted small d-none d-xl-inline">{auth.user?.username}</span>
                  <a className="btn btn-sm btn-outline-secondary" href={auth.logout_url}>
                    Sign out
                  </a>
                </>
              ) : (
                <a className="btn btn-sm btn-primary" href={auth?.login_url ?? '/accounts/login/'}>
                  <i className="bi bi-box-arrow-in-right me-1" aria-hidden="true" />
                  Sign in
                </a>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-grow-1">
        <div className="container-xl py-4">
          <Outlet />
        </div>
      </main>

      <footer className="bg-body-tertiary border-top py-3 mt-auto">
        <div className="container-xl d-flex flex-wrap justify-content-between align-items-center gap-2">
          <span className="text-muted small">
            &copy; {new Date().getFullYear()} {site?.name ?? 'Barody Broject'}
            {site?.version && <span className="ms-2 font-monospace">v{site.version}</span>}
          </span>
          <span className="d-flex align-items-center gap-3 small">
            {site?.powered_by?.length ? <span className="text-muted">Powered by</span> : null}
            {site?.powered_by?.map((item) => (
              <a
                key={item.id}
                className="link-secondary text-decoration-none"
                href={item.url}
                target="_blank"
                rel="nofollow noopener noreferrer"
                title={item.name}
              >
                <i className={`bi bi-${item.icon}`} aria-hidden="true" />
                <span className="ms-1 d-none d-lg-inline">{item.name}</span>
              </a>
            ))}
            {site?.github_issue_repo && (
              <a
                className="link-secondary text-decoration-none"
                href={`https://github.com/${site.github_issue_repo}/issues/new`}
                target="_blank"
                rel="noopener noreferrer"
              >
                <i className="bi bi-bug me-1" aria-hidden="true" />
                Report an issue
              </a>
            )}
          </span>
        </div>
      </footer>
    </div>
  )
}
