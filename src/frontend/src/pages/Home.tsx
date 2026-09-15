import { Link } from 'react-router-dom'

import { useApp } from '../AppContext'
import { providers as providersApi } from '../api/endpoints'
import { useAsync } from '../hooks/useAsync'
import { Alert, PageHeader, Spinner } from '../components/ui'

const CARDS = [
  {
    to: '/content',
    icon: 'file-earmark-text',
    colour: 'primary',
    title: 'Content',
    body: 'Write a prompt, generate an article, and edit the result.',
  },
  {
    to: '/threads',
    icon: 'chat-dots',
    colour: 'success',
    title: 'Threads',
    body: 'Run one assistant or a whole pipeline over a conversation.',
  },
  {
    to: '/posts',
    icon: 'newspaper',
    colour: 'warning',
    title: 'Posts',
    body: 'Edit front matter and publish to GitHub Pages.',
  },
  {
    to: '/assistants',
    icon: 'robot',
    colour: 'info',
    title: 'Assistants',
    body: 'Personas, models, and the JSON schema each one must satisfy.',
  },
]

export function HomePage() {
  const { auth, site } = useApp()
  const signedIn = Boolean(auth?.authenticated)
  const { data: providers, loading, error } = useAsync(
    () => (signedIn ? providersApi.list() : Promise.resolve([])),
    [signedIn],
  )

  const active = providers?.find((provider) => provider.is_default)

  return (
    <>
      <PageHeader
        title={`Welcome to ${site?.name ?? 'Barody Broject'}`}
        description="An AI-powered parody news generator. Bring your own AI provider."
      />

      {!signedIn && (
        <Alert kind="info">
          <a href={auth?.login_url ?? '/accounts/login/'} className="alert-link">
            Sign in
          </a>{' '}
          to generate content, run assistants, and publish posts.
        </Alert>
      )}

      {signedIn && (
        <>
          {loading && <Spinner label="Checking AI providers..." />}
          {error && <Alert kind="warning">Could not load providers: {error}</Alert>}
          {active && (
            <div className="card mb-4 border-0 bg-body-tertiary">
              <div className="card-body d-flex flex-wrap justify-content-between align-items-center gap-3">
                <div>
                  <h2 className="h6 text-uppercase text-muted mb-1">Active AI provider</h2>
                  <p className="h5 mb-1">
                    {active.display_name}
                    {active.configured ? (
                      <span className="badge text-bg-success ms-2">Ready</span>
                    ) : (
                      <span className="badge text-bg-warning text-dark ms-2">No credential</span>
                    )}
                  </p>
                  <p className="text-muted mb-0 small">
                    Default model <code>{active.default_model}</code>
                    {active.credential_source && <> · credential from {active.credential_source}</>}
                  </p>
                </div>
                <Link className="btn btn-outline-secondary" to="/settings">
                  <i className="bi bi-sliders me-1" aria-hidden="true" />
                  Manage providers
                </Link>
              </div>
            </div>
          )}
          {!loading && !active && !error && (
            <Alert kind="warning">
              No AI provider is configured yet. <Link to="/settings" className="alert-link">Set one up</Link> to
              start generating.
            </Alert>
          )}

          <div className="row g-4">
            {CARDS.map((card) => (
              <div className="col-md-6" key={card.to}>
                <div className="card h-100 shadow-sm">
                  <div className="card-body">
                    <h2 className="h5 card-title">
                      <i className={`bi bi-${card.icon} text-${card.colour} me-2`} aria-hidden="true" />
                      {card.title}
                    </h2>
                    <p className="card-text text-muted">{card.body}</p>
                    <Link className={`btn btn-${card.colour}`} to={card.to}>
                      Open {card.title}
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </>
  )
}
