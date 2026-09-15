import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import {
  assistantGroups as groupsApi,
  assistants as assistantsApi,
  messages as messagesApi,
  threads as threadsApi,
} from '../api/endpoints'
import type { Message, Thread } from '../api/types'
import { Column, DataTable } from '../components/DataTable'
import { Markdown } from '../components/Markdown'
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

const COLUMNS: Column<Thread>[] = [
  { key: 'name', header: 'Name', render: (row) => truncate(row.name, 60) },
  { key: 'description', header: 'Description', render: (row) => truncate(row.description, 80) },
  { key: 'assistant_group_name', header: 'Group' },
  {
    key: 'provider',
    header: 'Provider',
    render: (row) => <ProviderBadge provider={row.provider} />,
  },
  { key: 'message_count', header: 'Messages', sort: 'number' },
  {
    key: 'created_at',
    header: 'Created',
    sort: 'date',
    render: (row) => <span className="text-nowrap">{formatDate(row.created_at)}</span>,
  },
]

export function ThreadsPage() {
  const navigate = useNavigate()
  const { data, loading, error } = useAsync(() => threadsApi.list(), [])

  return (
    <>
      <PageHeader
        title="Threads"
        icon="chat-dots"
        description="Conversations replayed to whichever provider is configured."
      />
      {error && <Alert kind="danger">{error}</Alert>}
      {loading ? (
        <Spinner />
      ) : (
        <DataTable
          rows={data ?? []}
          columns={COLUMNS}
          rowKey={(row) => row.id}
          onRowClick={(row) => navigate(`/threads/${row.id}`)}
          ariaLabel="Thread listing"
          emptyMessage="No threads yet. Start one from a piece of content."
        />
      )}
    </>
  )
}

function Turn({
  message,
  assistantNames,
  onAssign,
  onRun,
  onCreatePost,
  onDelete,
  pending,
}: {
  message: Message
  assistantNames: { id: string; name: string }[]
  onAssign: (assistant: string) => void
  onRun: () => void
  onCreatePost: () => void
  onDelete: () => void
  pending: boolean
}) {
  const failed = message.status === 'failed'
  const kind = failed ? 'failed' : message.role === 'user' ? 'user' : 'assistant'
  return (
    <div className={`chat-turn chat-turn--${kind} mb-3`}>
      <div className="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
        <div className="d-flex align-items-center gap-2 flex-wrap">
          <span className="badge text-bg-secondary text-capitalize">{message.role}</span>
          {message.assistant_name && <span className="fw-semibold">{message.assistant_name}</span>}
          <StatusBadge status={message.status} />
          {message.provider && <ProviderBadge provider={message.provider} />}
          {message.model_id && <span className="text-muted small font-monospace">{message.model_id}</span>}
          <span className="text-muted small">{formatDate(message.created_at)}</span>
        </div>
        <div className="btn-group btn-group-sm">
          <select
            className="form-select form-select-sm"
            style={{ maxWidth: '12rem' }}
            value={message.assistant ?? ''}
            onChange={(event) => onAssign(event.target.value)}
            aria-label="Assign assistant to this message"
          >
            <option value="">Unassigned</option>
            {assistantNames.map((assistant) => (
              <option key={assistant.id} value={assistant.id}>
                {assistant.name}
              </option>
            ))}
          </select>
          <button
            type="button"
            className="btn btn-outline-success"
            onClick={onRun}
            disabled={pending || !message.assistant}
            title={message.assistant ? 'Run the assigned assistant' : 'Assign an assistant first'}
          >
            <i className="bi bi-play-circle" aria-hidden="true" />
            <span className="visually-hidden">Run assistant</span>
          </button>
          <button
            type="button"
            className="btn btn-outline-primary"
            onClick={onCreatePost}
            disabled={pending || !message.content_text}
            title="Create a post from this message"
          >
            <i className="bi bi-file-earmark-text" aria-hidden="true" />
            <span className="visually-hidden">Create post</span>
          </button>
          <button type="button" className="btn btn-outline-danger" onClick={onDelete} disabled={pending}>
            <i className="bi bi-trash" aria-hidden="true" />
            <span className="visually-hidden">Delete message</span>
          </button>
        </div>
      </div>
      {failed && message.error ? (
        <p className="mb-0 text-danger-emphasis">
          <i className="bi bi-exclamation-triangle me-1" aria-hidden="true" />
          {message.error}
        </p>
      ) : (
        <Markdown text={message.content_text} className="prose" />
      )}
    </div>
  )
}

export function ThreadDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const threadId = id as string

  const threadState = useAsync(() => threadsApi.get(threadId), [threadId])
  const assistantsState = useAsync(() => assistantsApi.list(), [])
  const groupsState = useAsync(() => groupsApi.list(), [])
  const { run, pending, error: actionError, clearError } = useAction()

  const [reply, setReply] = useState('')
  const [runAssistant, setRunAssistant] = useState('')
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)

  const thread = threadState.data
  const assistants = (assistantsState.data ?? []).map((a) => ({ id: a.id, name: a.name }))
  const groups = groupsState.data ?? []

  const refresh = (next?: Thread | null) => {
    if (next) threadState.setData(next)
    else threadState.reload()
  }

  const sendReply = async () => {
    if (!reply.trim()) return
    const next = await run(() => threadsApi.addMessage(threadId, reply.trim()))
    if (next) {
      setReply('')
      refresh(next)
    }
  }

  const doRun = async () => {
    if (!runAssistant) return
    const result = await run(() => threadsApi.run(threadId, runAssistant))
    if (result) {
      refresh(result.thread)
      setNotice(`${result.message.assistant_name || 'Assistant'} replied via ${result.message.provider}.`)
    }
  }

  const doRunGroup = async () => {
    const result = await run(() => threadsApi.runGroup(threadId, thread?.assistant_group ?? null))
    if (result) {
      refresh(result.thread)
      setNotice(`Ran ${result.messages.length} assistant(s) in the group.`)
    }
  }

  const setGroup = async (groupId: string) => {
    const next = await run(() =>
      threadsApi.update(threadId, { assistant_group: groupId ? Number(groupId) : null }),
    )
    if (next) refresh(next)
  }

  if (threadState.loading) return <Spinner />
  if (threadState.error) return <Alert kind="danger">{threadState.error}</Alert>
  if (!thread) return <Alert kind="warning">Thread not found.</Alert>

  return (
    <>
      <PageHeader
        title={thread.name}
        icon="chat-dots"
        description={thread.description || `Thread ${thread.id}`}
        actions={
          <>
            <Link className="btn btn-outline-secondary" to="/threads">
              <i className="bi bi-arrow-left me-1" aria-hidden="true" />
              All threads
            </Link>
            <button type="button" className="btn btn-outline-danger" onClick={() => setConfirmDelete(true)}>
              <i className="bi bi-trash me-1" aria-hidden="true" />
              Delete thread
            </button>
          </>
        }
      />

      {actionError && <Alert kind="danger" onDismiss={clearError}>{actionError}</Alert>}
      {notice && <Alert kind="success" onDismiss={() => setNotice(null)}>{notice}</Alert>}

      <div className="card mb-4">
        <div className="card-body d-flex flex-wrap gap-3 align-items-end">
          <div className="flex-grow-1" style={{ minWidth: '14rem' }}>
            <label className="form-label" htmlFor="run-assistant">
              Run a single assistant
            </label>
            <div className="input-group">
              <select
                id="run-assistant"
                className="form-select"
                value={runAssistant}
                onChange={(event) => setRunAssistant(event.target.value)}
              >
                <option value="">Select an assistant</option>
                {assistants.map((assistant) => (
                  <option key={assistant.id} value={assistant.id}>
                    {assistant.name}
                  </option>
                ))}
              </select>
              <button className="btn btn-success" type="button" onClick={doRun} disabled={pending || !runAssistant}>
                {pending && <span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />}
                <i className="bi bi-play-circle me-1" aria-hidden="true" />
                Run
              </button>
            </div>
          </div>
          <div className="flex-grow-1" style={{ minWidth: '14rem' }}>
            <label className="form-label" htmlFor="run-group">
              Assistant group
            </label>
            <div className="input-group">
              <select
                id="run-group"
                className="form-select"
                value={thread.assistant_group ?? ''}
                onChange={(event) => setGroup(event.target.value)}
              >
                <option value="">No group</option>
                {groups.map((group) => (
                  <option key={group.id} value={group.id}>
                    {group.name}
                  </option>
                ))}
              </select>
              <button
                className="btn btn-primary"
                type="button"
                onClick={doRunGroup}
                disabled={pending || !thread.assistant_group}
                title={thread.assistant_group ? 'Run every assistant in order' : 'Pick a group first'}
              >
                <i className="bi bi-collection-play me-1" aria-hidden="true" />
                Run group
              </button>
            </div>
          </div>
        </div>
      </div>

      <h2 className="h5 mb-3">
        Conversation <span className="badge text-bg-secondary">{thread.messages?.length ?? 0}</span>
      </h2>

      {(thread.messages ?? []).map((message) => (
        <Turn
          key={message.id}
          message={message}
          assistantNames={assistants}
          pending={pending}
          onAssign={async (assistant) => {
            const updated = await run(() => messagesApi.assign(message.id, assistant || null))
            if (updated) refresh()
          }}
          onRun={async () => {
            const result = await run(() => messagesApi.run(message.id))
            if (result) refresh()
          }}
          onCreatePost={async () => {
            const post = await run(() => messagesApi.createPost(message.id))
            if (post) navigate(`/posts/${post.id}`)
          }}
          onDelete={async () => {
            const ok = await run(() => messagesApi.remove(message.id))
            if (ok !== null) refresh()
          }}
        />
      ))}

      <div className="card mt-4">
        <div className="card-body">
          <label className="form-label" htmlFor="reply">
            Add a message
          </label>
          <textarea
            id="reply"
            className="form-control mb-2"
            rows={3}
            value={reply}
            onChange={(event) => setReply(event.target.value)}
            placeholder="Give the next assistant something to work with..."
          />
          <button type="button" className="btn btn-outline-primary" onClick={sendReply} disabled={pending || !reply.trim()}>
            <i className="bi bi-send me-1" aria-hidden="true" />
            Add message
          </button>
        </div>
      </div>

      {confirmDelete && (
        <ConfirmDialog
          message="Delete this thread and all of its messages?"
          pending={pending}
          onCancel={() => setConfirmDelete(false)}
          onConfirm={async () => {
            const ok = await run(() => threadsApi.remove(threadId))
            if (ok !== null) navigate('/threads')
          }}
        />
      )}
    </>
  )
}
