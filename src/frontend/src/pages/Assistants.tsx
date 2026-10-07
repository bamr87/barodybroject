import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import {
  aiModels as modelsApi,
  assistants as assistantsApi,
  schemas as schemasApi,
} from '../api/endpoints'
import type { AIModel, Assistant, JSONSchemaRecord } from '../api/types'
import { Column, DataTable } from '../components/DataTable'
import {
  Alert,
  ConfirmDialog,
  PageHeader,
  ProviderBadge,
  Spinner,
  formatDate,
  truncate,
} from '../components/ui'
import { useAction, useAsync } from '../hooks/useAsync'

const COLUMNS: Column<Assistant>[] = [
  { key: 'name', header: 'Name' },
  { key: 'description', header: 'Description', render: (row) => truncate(row.description, 80) },
  {
    key: 'provider',
    header: 'Provider',
    render: (row) => <ProviderBadge provider={row.provider} />,
  },
  {
    key: 'model',
    header: 'Model',
    value: (row) => row.model_detail?.model_id ?? '',
    render: (row) => <span className="font-monospace small">{row.model_detail?.model_id ?? '—'}</span>,
  },
  { key: 'json_schema_name', header: 'Schema', render: (row) => row.json_schema_name || '—' },
  {
    key: 'created_at',
    header: 'Created',
    sort: 'date',
    render: (row) => <span className="text-nowrap">{formatDate(row.created_at)}</span>,
  },
]

export function AssistantsPage() {
  const navigate = useNavigate()
  const { data, loading, error } = useAsync(() => assistantsApi.list(), [])

  return (
    <>
      <PageHeader
        title="Assistants"
        icon="robot"
        description="A persona, the model that runs it, and the shape of its output."
        actions={
          <Link className="btn btn-primary" to="/assistants/new">
            <i className="bi bi-plus-circle me-1" aria-hidden="true" />
            New assistant
          </Link>
        }
      />
      {error && <Alert kind="danger">{error}</Alert>}
      {loading ? (
        <Spinner />
      ) : (
        <DataTable
          rows={data ?? []}
          columns={COLUMNS}
          rowKey={(row) => row.id}
          onRowClick={(row) => navigate(`/assistants/${row.id}`)}
          ariaLabel="Assistant listing"
          emptyMessage="No assistants yet."
        />
      )}
    </>
  )
}

export function AssistantDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isNew = !id

  const assistantState = useAsync(
    () => (id ? assistantsApi.get(id) : Promise.resolve(null)),
    [id],
  )
  const modelsState = useAsync(() => modelsApi.list({ active: 'true' }), [])
  const schemasState = useAsync(() => schemasApi.list(), [])
  const { run, pending, error: actionError, clearError } = useAction()

  const [form, setForm] = useState({
    name: '',
    description: '',
    instructions: '',
    model: '',
    json_schema: '',
    temperature: '',
  })
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)

  const assistant = assistantState.data
  useEffect(() => {
    if (!assistant) return
    setForm({
      name: assistant.name ?? '',
      description: assistant.description ?? '',
      instructions: assistant.instructions ?? '',
      model: assistant.model ? String(assistant.model) : '',
      json_schema: assistant.json_schema ? String(assistant.json_schema) : '',
      temperature: assistant.temperature === null ? '' : String(assistant.temperature),
    })
  }, [assistant])

  const models: AIModel[] = modelsState.data ?? []
  const schemas: JSONSchemaRecord[] = schemasState.data ?? []
  const byProvider = models.reduce<Record<string, AIModel[]>>((acc, model) => {
    ;(acc[model.provider] ??= []).push(model)
    return acc
  }, {})

  const save = async () => {
    const payload = {
      name: form.name,
      description: form.description,
      instructions: form.instructions,
      model: form.model ? Number(form.model) : null,
      json_schema: form.json_schema ? Number(form.json_schema) : null,
      temperature: form.temperature === '' ? null : Number(form.temperature),
    }
    const saved = isNew
      ? await run(() => assistantsApi.create(payload))
      : await run(() => assistantsApi.update(id as string, payload))
    if (saved) {
      setNotice('Saved.')
      if (isNew) navigate(`/assistants/${saved.id}`, { replace: true })
      else assistantState.setData(saved)
    }
  }

  if (!isNew && assistantState.loading) return <Spinner />
  if (!isNew && assistantState.error) return <Alert kind="danger">{assistantState.error}</Alert>

  return (
    <>
      <PageHeader
        title={isNew ? 'New assistant' : form.name || 'Assistant'}
        icon="robot"
        description={isNew ? undefined : <span className="font-monospace small">{id}</span>}
        actions={
          <Link className="btn btn-outline-secondary" to="/assistants">
            <i className="bi bi-arrow-left me-1" aria-hidden="true" />
            All assistants
          </Link>
        }
      />

      {actionError && <Alert kind="danger" onDismiss={clearError}>{actionError}</Alert>}
      {notice && <Alert kind="success" onDismiss={() => setNotice(null)}>{notice}</Alert>}

      <div className="row g-4">
        <div className="col-lg-7">
          <div className="card">
            <div className="card-header">Persona</div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label" htmlFor="name">
                  Name
                </label>
                <input
                  id="name"
                  className="form-control"
                  value={form.name}
                  onChange={(event) => setForm({ ...form, name: event.target.value })}
                />
              </div>
              <div className="mb-3">
                <label className="form-label" htmlFor="description">
                  Description
                </label>
                <input
                  id="description"
                  className="form-control"
                  value={form.description}
                  onChange={(event) => setForm({ ...form, description: event.target.value })}
                />
              </div>
              <div className="mb-0">
                <label className="form-label" htmlFor="instructions">
                  Instructions
                </label>
                <textarea
                  id="instructions"
                  className="form-control"
                  rows={14}
                  value={form.instructions}
                  onChange={(event) => setForm({ ...form, instructions: event.target.value })}
                  placeholder="You are a satirical news writer who..."
                />
                <div className="form-text">Sent as the system prompt on every run.</div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-lg-5">
          <div className="card">
            <div className="card-header">Model and output</div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label" htmlFor="model">
                  Model
                </label>
                <select
                  id="model"
                  className="form-select"
                  value={form.model}
                  onChange={(event) => setForm({ ...form, model: event.target.value })}
                >
                  <option value="">Use the default provider and model</option>
                  {Object.entries(byProvider).map(([provider, group]) => (
                    <optgroup key={provider} label={provider}>
                      {group.map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.display_name || model.model_id}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
                <div className="form-text">
                  The model decides the provider. <Link to="/settings">Sync models</Link> if this list looks empty.
                </div>
              </div>
              <div className="mb-3">
                <label className="form-label" htmlFor="schema">
                  JSON schema
                </label>
                <select
                  id="schema"
                  className="form-select"
                  value={form.json_schema}
                  onChange={(event) => setForm({ ...form, json_schema: event.target.value })}
                >
                  <option value="">Free-form text</option>
                  {schemas.map((schema) => (
                    <option key={schema.id} value={schema.id}>
                      {schema.name}
                    </option>
                  ))}
                </select>
                <div className="form-text">
                  Structured output is validated before it is stored.
                </div>
              </div>
              <div className="mb-0">
                <label className="form-label" htmlFor="temperature">
                  Temperature
                </label>
                <input
                  id="temperature"
                  className="form-control"
                  type="number"
                  step="0.1"
                  min="0"
                  max="2"
                  value={form.temperature}
                  onChange={(event) => setForm({ ...form, temperature: event.target.value })}
                  placeholder="provider default"
                />
                <div className="form-text">Ignored by models that run adaptive thinking.</div>
              </div>
            </div>
          </div>
          {assistant?.groups?.length ? (
            <div className="card mt-3">
              <div className="card-header">Member of</div>
              <ul className="list-group list-group-flush">
                {assistant.groups.map((group) => (
                  <li className="list-group-item" key={group.id}>
                    <Link to={`/assistant-groups/${group.id}`}>{group.name}</Link>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      </div>

      <div className="d-flex flex-wrap gap-2 mt-4">
        <button type="button" className="btn btn-primary" onClick={save} disabled={pending}>
          {pending && <span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />}
          <i className="bi bi-save me-1" aria-hidden="true" />
          {isNew ? 'Create assistant' : 'Save changes'}
        </button>
        {!isNew && (
          <button
            type="button"
            className="btn btn-outline-danger ms-auto"
            onClick={() => setConfirmDelete(true)}
            disabled={pending}
          >
            <i className="bi bi-trash me-1" aria-hidden="true" />
            Delete
          </button>
        )}
      </div>

      {confirmDelete && (
        <ConfirmDialog
          message="Delete this assistant? Content and messages it produced are kept."
          pending={pending}
          onCancel={() => setConfirmDelete(false)}
          onConfirm={async () => {
            const ok = await run(() => assistantsApi.remove(id as string))
            if (ok !== null) navigate('/assistants')
          }}
        />
      )}
    </>
  )
}
