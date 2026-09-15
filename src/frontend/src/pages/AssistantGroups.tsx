import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { assistantGroups as groupsApi, assistants as assistantsApi } from '../api/endpoints'
import type { AssistantGroup, GroupMembership } from '../api/types'
import { Column, DataTable } from '../components/DataTable'
import { Alert, ConfirmDialog, PageHeader, Spinner, formatDate } from '../components/ui'
import { useAction, useAsync } from '../hooks/useAsync'

const COLUMNS: Column<AssistantGroup>[] = [
  { key: 'name', header: 'Name' },
  { key: 'group_type', header: 'Type' },
  { key: 'sequence', header: 'Sequence', sort: 'number' },
  { key: 'priority', header: 'Priority', sort: 'number' },
  {
    key: 'members',
    header: 'Members',
    sort: 'number',
    value: (row) => row.memberships?.length ?? 0,
  },
  {
    key: 'is_active',
    header: 'Active',
    render: (row) =>
      row.is_active ? (
        <span className="badge text-bg-success">yes</span>
      ) : (
        <span className="badge text-bg-secondary">no</span>
      ),
  },
  {
    key: 'created_at',
    header: 'Created',
    sort: 'date',
    render: (row) => <span className="text-nowrap">{formatDate(row.created_at)}</span>,
  },
]

export function AssistantGroupsPage() {
  const navigate = useNavigate()
  const { data, loading, error } = useAsync(() => groupsApi.list(), [])

  return (
    <>
      <PageHeader
        title="Assistant groups"
        icon="people"
        description="Run several assistants in order, each one seeing the output before it."
        actions={
          <Link className="btn btn-primary" to="/assistant-groups/new">
            <i className="bi bi-plus-circle me-1" aria-hidden="true" />
            New group
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
          onRowClick={(row) => navigate(`/assistant-groups/${row.id}`)}
          ariaLabel="Assistant group listing"
          emptyMessage="No assistant groups yet."
        />
      )}
    </>
  )
}

export function AssistantGroupDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isNew = !id
  const groupId = id ? Number(id) : null

  const groupState = useAsync(
    () => (groupId ? groupsApi.get(groupId) : Promise.resolve(null)),
    [groupId],
  )
  const assistantsState = useAsync(() => assistantsApi.list(), [])
  const { run, pending, error: actionError, clearError } = useAction()

  const [form, setForm] = useState({ name: '', group_type: 'default', sequence: 0, priority: 0, is_active: true })
  const [members, setMembers] = useState<GroupMembership[]>([])
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)

  const group = groupState.data
  useEffect(() => {
    if (!group) return
    setForm({
      name: group.name,
      group_type: group.group_type,
      sequence: group.sequence,
      priority: group.priority,
      is_active: group.is_active,
    })
    setMembers([...(group.memberships ?? [])].sort((a, b) => a.position - b.position))
  }, [group])

  const assistants = assistantsState.data ?? []

  const move = (index: number, delta: number) => {
    const next = [...members]
    const target = index + delta
    if (target < 0 || target >= next.length) return
    ;[next[index], next[target]] = [next[target], next[index]]
    setMembers(next.map((member, i) => ({ ...member, position: i + 1 })))
  }

  const save = async () => {
    const payload = {
      ...form,
      memberships: members
        .filter((member) => member.assistant)
        .map((member, index) => ({ assistant: member.assistant, position: index + 1 })),
    }
    const saved = isNew
      ? await run(() => groupsApi.create(payload))
      : await run(() => groupsApi.update(groupId as number, payload))
    if (saved) {
      setNotice('Saved.')
      if (isNew) navigate(`/assistant-groups/${saved.id}`, { replace: true })
      else groupState.setData(saved)
    }
  }

  if (!isNew && groupState.loading) return <Spinner />
  if (!isNew && groupState.error) return <Alert kind="danger">{groupState.error}</Alert>

  return (
    <>
      <PageHeader
        title={isNew ? 'New assistant group' : form.name || 'Assistant group'}
        icon="people"
        actions={
          <Link className="btn btn-outline-secondary" to="/assistant-groups">
            <i className="bi bi-arrow-left me-1" aria-hidden="true" />
            All groups
          </Link>
        }
      />

      {actionError && <Alert kind="danger" onDismiss={clearError}>{actionError}</Alert>}
      {notice && <Alert kind="success" onDismiss={() => setNotice(null)}>{notice}</Alert>}

      <div className="row g-4">
        <div className="col-lg-5">
          <div className="card">
            <div className="card-header">Group</div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label" htmlFor="group-name">
                  Name
                </label>
                <input
                  id="group-name"
                  className="form-control"
                  value={form.name}
                  onChange={(event) => setForm({ ...form, name: event.target.value })}
                />
              </div>
              <div className="mb-3">
                <label className="form-label" htmlFor="group-type">
                  Type
                </label>
                <input
                  id="group-type"
                  className="form-control"
                  value={form.group_type}
                  onChange={(event) => setForm({ ...form, group_type: event.target.value })}
                />
              </div>
              <div className="row g-2 mb-3">
                <div className="col">
                  <label className="form-label" htmlFor="group-sequence">
                    Sequence
                  </label>
                  <input
                    id="group-sequence"
                    type="number"
                    className="form-control"
                    value={form.sequence}
                    onChange={(event) => setForm({ ...form, sequence: Number(event.target.value) })}
                  />
                </div>
                <div className="col">
                  <label className="form-label" htmlFor="group-priority">
                    Priority
                  </label>
                  <input
                    id="group-priority"
                    type="number"
                    className="form-control"
                    value={form.priority}
                    onChange={(event) => setForm({ ...form, priority: Number(event.target.value) })}
                  />
                </div>
              </div>
              <div className="form-check">
                <input
                  id="group-active"
                  className="form-check-input"
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(event) => setForm({ ...form, is_active: event.target.checked })}
                />
                <label className="form-check-label" htmlFor="group-active">
                  Active
                </label>
              </div>
            </div>
          </div>
        </div>

        <div className="col-lg-7">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <span>Pipeline</span>
              <button
                type="button"
                className="btn btn-sm btn-outline-primary"
                onClick={() => setMembers([...members, { assistant: '', position: members.length + 1 }])}
              >
                <i className="bi bi-plus-lg me-1" aria-hidden="true" />
                Add step
              </button>
            </div>
            <div className="card-body">
              {members.length === 0 && (
                <p className="text-muted mb-0">
                  No steps yet. Add assistants in the order they should run.
                </p>
              )}
              {members.map((member, index) => (
                <div className="input-group mb-2" key={index}>
                  <span className="input-group-text">{index + 1}</span>
                  <select
                    className="form-select"
                    value={member.assistant ?? ''}
                    aria-label={`Assistant for step ${index + 1}`}
                    onChange={(event) => {
                      const next = [...members]
                      next[index] = { ...member, assistant: event.target.value }
                      setMembers(next)
                    }}
                  >
                    <option value="">Select an assistant</option>
                    {assistants.map((assistant) => (
                      <option key={assistant.id} value={assistant.id}>
                        {assistant.name}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => move(index, -1)}
                    disabled={index === 0}
                    aria-label={`Move step ${index + 1} up`}
                  >
                    <i className="bi bi-arrow-up" aria-hidden="true" />
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => move(index, 1)}
                    disabled={index === members.length - 1}
                    aria-label={`Move step ${index + 1} down`}
                  >
                    <i className="bi bi-arrow-down" aria-hidden="true" />
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline-danger"
                    onClick={() => setMembers(members.filter((_, i) => i !== index))}
                    aria-label={`Remove step ${index + 1}`}
                  >
                    <i className="bi bi-x-lg" aria-hidden="true" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="d-flex flex-wrap gap-2 mt-4">
        <button type="button" className="btn btn-primary" onClick={save} disabled={pending}>
          {pending && <span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />}
          <i className="bi bi-save me-1" aria-hidden="true" />
          {isNew ? 'Create group' : 'Save changes'}
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
          message="Delete this group? Its assistants are kept; threads pointing at it are deleted."
          pending={pending}
          onCancel={() => setConfirmDelete(false)}
          onConfirm={async () => {
            const ok = await run(() => groupsApi.remove(groupId as number))
            if (ok !== null) navigate('/assistant-groups')
          }}
        />
      )}
    </>
  )
}
