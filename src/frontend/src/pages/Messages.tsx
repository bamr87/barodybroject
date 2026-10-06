import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { assistants as assistantsApi, messages as messagesApi } from '../api/endpoints'
import type { Message } from '../api/types'
import { Column, DataTable } from '../components/DataTable'
import {
  Alert,
  ConfirmDialog,
  PageHeader,
  ProviderBadge,
  Spinner,
  StatusBadge,
  formatDate,
  truncate,
} from '../components/ui'
import { useAction, useAsync } from '../hooks/useAsync'

export function MessagesPage() {
  const navigate = useNavigate()
  const messagesState = useAsync(() => messagesApi.list(), [])
  const assistantsState = useAsync(() => assistantsApi.list(), [])
  const { run, pending, error: actionError, clearError } = useAction()
  const [toDelete, setToDelete] = useState<Message | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  const assistants = assistantsState.data ?? []

  const assign = async (message: Message, assistant: string) => {
    const updated = await run(() => messagesApi.assign(message.id, assistant || null))
    if (updated) messagesState.reload()
  }

  const columns: Column<Message>[] = [
    {
      key: 'thread_name',
      header: 'Thread',
      render: (row) =>
        row.thread ? (
          <Link to={`/threads/${row.thread}`} onClick={(event) => event.stopPropagation()}>
            {truncate(row.thread_name || row.thread, 40)}
          </Link>
        ) : (
          <span className="text-muted">none</span>
        ),
    },
    { key: 'role', header: 'Role', className: 'text-capitalize' },
    {
      key: 'content_text',
      header: 'Content',
      render: (row) => <span className="text-muted">{truncate(row.content_text || row.error, 90)}</span>,
    },
    {
      key: 'assistant_name',
      header: 'Assistant',
      filterable: false,
      render: (row) => (
        <select
          className="form-select form-select-sm"
          style={{ minWidth: '10rem' }}
          value={row.assistant ?? ''}
          disabled={pending}
          onClick={(event) => event.stopPropagation()}
          onChange={(event) => assign(row, event.target.value)}
          aria-label={`Assign assistant to message ${row.id}`}
        >
          <option value="">Unassigned</option>
          {assistants.map((assistant) => (
            <option key={assistant.id} value={assistant.id}>
              {assistant.name}
            </option>
          ))}
        </select>
      ),
    },
    { key: 'status', header: 'Status', render: (row) => <StatusBadge status={row.status} /> },
    { key: 'provider', header: 'Provider', render: (row) => <ProviderBadge provider={row.provider} /> },
    {
      key: 'created_at',
      header: 'Created',
      sort: 'date',
      render: (row) => <span className="text-nowrap">{formatDate(row.created_at)}</span>,
    },
    {
      key: 'actions',
      header: 'Actions',
      filterable: false,
      render: (row) => (
        <div className="btn-group btn-group-sm" onClick={(event) => event.stopPropagation()}>
          <button
            type="button"
            className="btn btn-outline-success"
            disabled={pending || !row.assistant}
            title="Run the assigned assistant"
            onClick={async () => {
              const reply = await run(() => messagesApi.run(row.id))
              if (reply) {
                setNotice('Assistant replied.')
                messagesState.reload()
              }
            }}
          >
            <i className="bi bi-play-circle" aria-hidden="true" />
            <span className="visually-hidden">Run</span>
          </button>
          <button
            type="button"
            className="btn btn-outline-primary"
            disabled={pending || !row.content_text}
            title="Create a post from this message"
            onClick={async () => {
              const post = await run(() => messagesApi.createPost(row.id))
              if (post) navigate(`/posts/${post.id}`)
            }}
          >
            <i className="bi bi-file-earmark-text" aria-hidden="true" />
            <span className="visually-hidden">Create post</span>
          </button>
          <button
            type="button"
            className="btn btn-outline-info"
            disabled={pending || !row.content_text}
            title="Create content from this message"
            onClick={async () => {
              const detail = await run(() => messagesApi.createContent(row.id))
              if (detail) navigate(`/content/${detail.id}`)
            }}
          >
            <i className="bi bi-plus-circle" aria-hidden="true" />
            <span className="visually-hidden">Create content</span>
          </button>
          <button
            type="button"
            className="btn btn-outline-danger"
            disabled={pending}
            onClick={() => setToDelete(row)}
          >
            <i className="bi bi-trash" aria-hidden="true" />
            <span className="visually-hidden">Delete</span>
          </button>
        </div>
      ),
    },
  ]

  return (
    <>
      <PageHeader
        title="Messages"
        icon="envelope"
        description="Every turn across every thread, with the assistant that produced it."
      />
      {messagesState.error && <Alert kind="danger">{messagesState.error}</Alert>}
      {actionError && <Alert kind="danger" onDismiss={clearError}>{actionError}</Alert>}
      {notice && <Alert kind="success" onDismiss={() => setNotice(null)}>{notice}</Alert>}

      {messagesState.loading ? (
        <Spinner />
      ) : (
        <DataTable
          rows={messagesState.data ?? []}
          columns={columns}
          rowKey={(row) => row.id}
          ariaLabel="Message listing"
          emptyMessage="No messages yet."
        />
      )}

      {toDelete && (
        <ConfirmDialog
          message="Delete this message? The thread keeps its other turns."
          pending={pending}
          onCancel={() => setToDelete(null)}
          onConfirm={async () => {
            const ok = await run(() => messagesApi.remove(toDelete.id))
            setToDelete(null)
            if (ok !== null) messagesState.reload()
          }}
        />
      )}
    </>
  )
}
