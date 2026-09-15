import { useState } from 'react'

import { useApp } from '../AppContext'
import { providers as providersApi } from '../api/endpoints'
import type { Provider } from '../api/types'
import { Alert, Modal, PageHeader, Spinner } from '../components/ui'
import { useAction, useAsync } from '../hooks/useAsync'

interface ConfigDraft {
  slug: string
  api_key: string
  base_url: string
  organization_id: string
  project_id: string
  default_model: string
  clear_api_key: boolean
}

function draftFor(provider: Provider): ConfigDraft {
  return {
    slug: provider.slug,
    api_key: '',
    base_url: provider.config?.base_url ?? '',
    organization_id: provider.config?.organization_id ?? '',
    project_id: provider.config?.project_id ?? '',
    default_model: provider.config?.default_model ?? '',
    clear_api_key: false,
  }
}

function ProviderCard({
  provider,
  isStaff,
  pending,
  onEdit,
  onSync,
  onTest,
  onMakeDefault,
}: {
  provider: Provider
  isStaff: boolean
  pending: boolean
  onEdit: () => void
  onSync: () => void
  onTest: () => void
  onMakeDefault: () => void
}) {
  return (
    <div className={`card h-100 ${provider.is_default ? 'border-primary' : ''}`}>
      <div className="card-body d-flex flex-column">
        <div className="d-flex justify-content-between align-items-start gap-2">
          <div>
            <h2 className="h5 mb-1">{provider.display_name}</h2>
            <code className="small text-muted">{provider.slug}</code>
          </div>
          <div className="text-end">
            {provider.is_default && <span className="badge text-bg-primary d-block mb-1">Default</span>}
            {provider.configured ? (
              <span className="badge text-bg-success">Credential found</span>
            ) : (
              <span className="badge text-bg-warning text-dark">Not configured</span>
            )}
          </div>
        </div>

        <p className="text-muted mt-2 mb-3">{provider.description}</p>

        <dl className="row small mb-3">
          <dt className="col-5">Default model</dt>
          <dd className="col-7 font-monospace">{provider.default_model || '—'}</dd>
          <dt className="col-5">Credential from</dt>
          <dd className="col-7">{provider.credential_source || 'not set'}</dd>
          <dt className="col-5">Env vars</dt>
          <dd className="col-7 font-monospace small">
            {provider.credential_env_vars.join(', ') || '—'}
          </dd>
          <dt className="col-5">Models synced</dt>
          <dd className="col-7">{provider.catalogue_count}</dd>
        </dl>

        <div className="mt-auto d-flex flex-wrap gap-2">
          <button type="button" className="btn btn-sm btn-outline-secondary" onClick={onSync} disabled={pending}>
            <i className="bi bi-arrow-repeat me-1" aria-hidden="true" />
            Sync models
          </button>
          <button
            type="button"
            className="btn btn-sm btn-outline-secondary"
            onClick={onTest}
            disabled={pending || !provider.configured}
            title={provider.configured ? 'Send a one-word test prompt' : 'Add a credential first'}
          >
            <i className="bi bi-activity me-1" aria-hidden="true" />
            Test
          </button>
          {isStaff && (
            <>
              <button type="button" className="btn btn-sm btn-outline-primary" onClick={onEdit} disabled={pending}>
                <i className="bi bi-key me-1" aria-hidden="true" />
                Configure
              </button>
              {!provider.is_default && (
                <button
                  type="button"
                  className="btn btn-sm btn-primary ms-auto"
                  onClick={onMakeDefault}
                  disabled={pending}
                >
                  Make default
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export function SettingsPage() {
  const { auth } = useApp()
  const isStaff = Boolean(auth?.user?.is_staff)
  const providersState = useAsync(() => providersApi.list(), [])
  const { run, pending, error: actionError, clearError } = useAction()
  const [draft, setDraft] = useState<ConfigDraft | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  const save = async () => {
    if (!draft) return
    const payload: Record<string, unknown> = {
      base_url: draft.base_url,
      organization_id: draft.organization_id,
      project_id: draft.project_id,
      default_model: draft.default_model,
    }
    if (draft.api_key) payload.api_key = draft.api_key
    if (draft.clear_api_key) payload.clear_api_key = true
    const saved = await run(() => providersApi.saveConfig(draft.slug, payload))
    if (saved) {
      setDraft(null)
      setNotice(`Saved configuration for ${saved.display_name}.`)
      providersState.reload()
    }
  }

  return (
    <>
      <PageHeader
        title="AI providers"
        icon="sliders"
        description="The application is provider-agnostic: pick the default here, and every assistant can still override it by choosing a model."
      />

      {providersState.error && <Alert kind="danger">{providersState.error}</Alert>}
      {actionError && <Alert kind="danger" onDismiss={clearError}>{actionError}</Alert>}
      {notice && <Alert kind="success" onDismiss={() => setNotice(null)}>{notice}</Alert>}
      {!isStaff && (
        <Alert kind="info">
          You can sync models and run a test, but only staff accounts can change credentials.
        </Alert>
      )}

      {providersState.loading ? (
        <Spinner label="Loading providers..." />
      ) : (
        <div className="row g-4">
          {(providersState.data ?? []).map((provider) => (
            <div className="col-lg-6" key={provider.slug}>
              <ProviderCard
                provider={provider}
                isStaff={isStaff}
                pending={pending}
                onEdit={() => setDraft(draftFor(provider))}
                onSync={async () => {
                  const report = await run(() => providersApi.sync(provider.slug))
                  if (report) {
                    setNotice(
                      `${report.provider}: ${report.created.length} new, ${report.updated.length} updated, ${report.total} total.`,
                    )
                    providersState.reload()
                  }
                }}
                onTest={async () => {
                  const result = await run(() => providersApi.test(provider.slug))
                  if (result) setNotice(`${provider.display_name} replied with "${result.text}" (${result.model}).`)
                }}
                onMakeDefault={async () => {
                  const saved = await run(() => providersApi.setDefault(provider.slug))
                  if (saved) {
                    setNotice(`${saved.display_name} is now the default provider.`)
                    providersState.reload()
                  }
                }}
              />
            </div>
          ))}
        </div>
      )}

      {draft && (
        <Modal
          title={`Configure ${draft.slug}`}
          onClose={() => setDraft(null)}
          footer={
            <>
              <button type="button" className="btn btn-secondary" onClick={() => setDraft(null)} disabled={pending}>
                Cancel
              </button>
              <button type="button" className="btn btn-primary" onClick={save} disabled={pending}>
                {pending && <span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />}
                Save
              </button>
            </>
          }
        >
          <div className="mb-3">
            <label className="form-label" htmlFor="api-key">
              Credential
            </label>
            <input
              id="api-key"
              type="password"
              className="form-control"
              autoComplete="off"
              value={draft.api_key}
              placeholder="Leave blank to keep the stored value"
              onChange={(event) => setDraft({ ...draft, api_key: event.target.value })}
            />
            <div className="form-text">
              Stored in the database and used in preference to the environment variables. For Claude Code this is
              the token from <code>claude setup-token</code>.
            </div>
            <div className="form-check mt-2">
              <input
                id="clear-key"
                className="form-check-input"
                type="checkbox"
                checked={draft.clear_api_key}
                onChange={(event) => setDraft({ ...draft, clear_api_key: event.target.checked })}
              />
              <label className="form-check-label" htmlFor="clear-key">
                Remove the stored credential and fall back to environment variables
              </label>
            </div>
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="default-model">
              Default model
            </label>
            <input
              id="default-model"
              className="form-control"
              value={draft.default_model}
              onChange={(event) => setDraft({ ...draft, default_model: event.target.value })}
              placeholder="provider default"
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="base-url">
              Base URL
            </label>
            <input
              id="base-url"
              className="form-control"
              value={draft.base_url}
              onChange={(event) => setDraft({ ...draft, base_url: event.target.value })}
              placeholder="only for gateways or proxies"
            />
          </div>
          <div className="row g-2 mb-0">
            <div className="col">
              <label className="form-label" htmlFor="org-id">
                Organization ID
              </label>
              <input
                id="org-id"
                className="form-control"
                value={draft.organization_id}
                onChange={(event) => setDraft({ ...draft, organization_id: event.target.value })}
              />
            </div>
            <div className="col">
              <label className="form-label" htmlFor="project-id">
                Project ID
              </label>
              <input
                id="project-id"
                className="form-control"
                value={draft.project_id}
                onChange={(event) => setDraft({ ...draft, project_id: event.target.value })}
              />
            </div>
          </div>
        </Modal>
      )}
    </>
  )
}
