import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import {
  assistantGroups as groupsApi,
  assistants as assistantsApi,
  content as contentApi,
} from '../api/endpoints'
import type { Assistant, AssistantGroup, ContentDetail, GenerateResponse } from '../api/types'
import { Column, DataTable } from '../components/DataTable'
import { Markdown } from '../components/Markdown'
import { Alert, ConfirmDialog, PageHeader, Spinner, formatDate, truncate } from '../components/ui'
import { useAction, useAsync } from '../hooks/useAsync'

const COLUMNS: Column<ContentDetail>[] = [
  { key: 'id', header: 'ID', sort: 'number', className: 'text-nowrap' },
  { key: 'title', header: 'Title', render: (row) => truncate(row.title || '(untitled)', 70) },
  { key: 'author', header: 'Author' },
  {
    key: 'description',
    header: 'Description',
    render: (row) => <span className="text-muted">{truncate(row.description, 90)}</span>,
  },
  {
    key: 'published_at',
    header: 'Published',
    sort: 'date',
    render: (row) => <span className="text-nowrap">{formatDate(row.published_at)}</span>,
  },
]

export function ContentPage() {
  const navigate = useNavigate()
  const { data, loading, error } = useAsync(() => contentApi.list(), [])

  return (
    <>
      <PageHeader
        title="Content"
        icon="file-earmark-text"
        description="Prompts and the articles generated from them."
        actions={
          <Link className="btn btn-primary" to="/content/new">
            <i className="bi bi-plus-circle me-1" aria-hidden="true" />
            New content
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
          onRowClick={(row) => navigate(`/content/${row.id}`)}
          ariaLabel="Content listing"
          emptyMessage="No content yet. Create one to get started."
        />
      )}
    </>
  )
}

export function ContentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isNew = id === 'new'
  const numericId = isNew ? null : Number(id)

  const detailState = useAsync(
    () => (numericId ? contentApi.get(numericId) : Promise.resolve(null)),
    [numericId],
  )
  const assistantsState = useAsync(() => assistantsApi.list(), [])
  const groupsState = useAsync(() => groupsApi.list(), [])
  const { run, pending, error: actionError, clearError } = useAction()

  const [form, setForm] = useState({
    title: '',
    description: '',
    author: '',
    slug: '',
    prompt: '',
    assistant: '',
  })
  const [generated, setGenerated] = useState<GenerateResponse | null>(null)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)

  const detail = detailState.data
  useEffect(() => {
    if (!detail) return
    const item = detail.items?.[0]
    setForm({
      title: detail.title ?? '',
      description: detail.description ?? '',
      author: detail.author ?? '',
      slug: detail.slug ?? '',
      prompt: item?.prompt ?? '',
      assistant: item?.assistant ?? '',
    })
  }, [detail])

  const assistants: Assistant[] = assistantsState.data ?? []
  const groups: AssistantGroup[] = groupsState.data ?? []
  const body = detail?.items?.[0]?.content_text ?? ''

  const save = async () => {
    const payload = {
      title: form.title,
      description: form.description,
      author: form.author,
      slug: form.slug || undefined,
      prompt: form.prompt,
      assistant: form.assistant || null,
    }
    const saved = isNew
      ? await run(() => contentApi.create(payload))
      : await run(() => contentApi.update(numericId as number, payload))
    if (saved) {
      setNotice('Saved.')
      if (isNew) navigate(`/content/${saved.id}`, { replace: true })
      else detailState.reload()
    }
  }

  const generate = async () => {
    if (!numericId) return
    setGenerated(null)
    const result = await run(() => contentApi.generate(numericId))
    if (result) {
      setGenerated(result)
      detailState.setData(result.content_detail)
      setNotice(`Generated with ${result.provider} (${result.model}).`)
    }
  }

  const createThread = async () => {
    if (!numericId) return
    const thread = await run(() => contentApi.createThread(numericId, { name: form.title }))
    if (thread) navigate(`/threads/${thread.id}`)
  }

  const remove = async () => {
    if (!numericId) return
    const ok = await run(() => contentApi.remove(numericId))
    if (ok !== null) navigate('/content')
  }

  if (!isNew && detailState.loading) return <Spinner />
  if (!isNew && detailState.error) return <Alert kind="danger">{detailState.error}</Alert>

  return (
    <>
      <PageHeader
        title={isNew ? 'New content' : form.title || `Content ${numericId}`}
        icon="pencil-square"
        description={isNew ? 'Describe what the assistant should write.' : `Content #${numericId}`}
        actions={
          <Link className="btn btn-outline-secondary" to="/content">
            <i className="bi bi-arrow-left me-1" aria-hidden="true" />
            All content
          </Link>
        }
      />

      {actionError && <Alert kind="danger" onDismiss={clearError}>{actionError}</Alert>}
      {notice && <Alert kind="success" onDismiss={() => setNotice(null)}>{notice}</Alert>}
      {generated?.warnings?.length ? (
        <Alert kind="warning">
          {generated.warnings.map((warning) => (
            <div key={warning}>{warning}</div>
          ))}
        </Alert>
      ) : null}

      <div className="row g-4">
        <div className="col-lg-6">
          <div className="card">
            <div className="card-header">Prompt</div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label" htmlFor="assistant">
                  Assistant
                </label>
                <select
                  id="assistant"
                  className="form-select"
                  value={form.assistant}
                  onChange={(event) => setForm({ ...form, assistant: event.target.value })}
                >
                  <option value="">Select an assistant</option>
                  {assistants.map((assistant) => (
                    <option key={assistant.id} value={assistant.id}>
                      {assistant.name}
                      {assistant.model_detail ? ` — ${assistant.model_detail.label}` : ''}
                    </option>
                  ))}
                </select>
                {assistants.length === 0 && !assistantsState.loading && (
                  <div className="form-text">
                    No assistants yet. <Link to="/assistants/new">Create one</Link>.
                  </div>
                )}
              </div>
              <div className="mb-3">
                <label className="form-label" htmlFor="prompt">
                  Prompt
                </label>
                <textarea
                  id="prompt"
                  className="form-control"
                  rows={8}
                  value={form.prompt}
                  onChange={(event) => setForm({ ...form, prompt: event.target.value })}
                  placeholder="Write a satirical article about..."
                />
              </div>
            </div>
          </div>
        </div>

        <div className="col-lg-6">
          <div className="card">
            <div className="card-header">Publication detail</div>
            <div className="card-body">
              {(['title', 'author', 'slug'] as const).map((field) => (
                <div className="mb-3" key={field}>
                  <label className="form-label text-capitalize" htmlFor={field}>
                    {field}
                  </label>
                  <input
                    id={field}
                    className="form-control"
                    value={form[field]}
                    onChange={(event) => setForm({ ...form, [field]: event.target.value })}
                  />
                </div>
              ))}
              <div className="mb-0">
                <label className="form-label" htmlFor="description">
                  Description
                </label>
                <textarea
                  id="description"
                  className="form-control"
                  rows={4}
                  value={form.description}
                  onChange={(event) => setForm({ ...form, description: event.target.value })}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="d-flex flex-wrap gap-2 mt-4">
        <button type="button" className="btn btn-primary" onClick={save} disabled={pending}>
          {pending && <span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />}
          <i className="bi bi-save me-1" aria-hidden="true" />
          {isNew ? 'Create' : 'Save changes'}
        </button>
        {!isNew && (
          <>
            <button
              type="button"
              className="btn btn-success"
              onClick={generate}
              disabled={pending || !form.assistant}
              title={form.assistant ? undefined : 'Pick an assistant first'}
            >
              <i className="bi bi-stars me-1" aria-hidden="true" />
              Generate content
            </button>
            <button type="button" className="btn btn-info" onClick={createThread} disabled={pending}>
              <i className="bi bi-chat-dots me-1" aria-hidden="true" />
              Create thread
            </button>
            <button
              type="button"
              className="btn btn-outline-danger ms-auto"
              onClick={() => setConfirmDelete(true)}
              disabled={pending}
            >
              <i className="bi bi-trash me-1" aria-hidden="true" />
              Delete
            </button>
          </>
        )}
      </div>

      {groups.length > 0 && !isNew && (
        <p className="form-text mt-2">
          Threads can run an assistant group; pick one on the thread once it exists.
        </p>
      )}

      {body && (
        <div className="card mt-4">
          <div className="card-header d-flex justify-content-between align-items-center">
            <span>Generated article</span>
            {generated && (
              <span className="text-muted small">
                {generated.provider} · {generated.model}
                {typeof generated.usage?.output_tokens === 'number' && (
                  <> · {generated.usage.output_tokens} output tokens</>
                )}
              </span>
            )}
          </div>
          <div className="card-body">
            <Markdown text={body} className="prose" />
          </div>
        </div>
      )}

      {confirmDelete && (
        <ConfirmDialog
          message="Delete this content and everything generated from it? This cannot be undone."
          pending={pending}
          onCancel={() => setConfirmDelete(false)}
          onConfirm={remove}
        />
      )}
    </>
  )
}
