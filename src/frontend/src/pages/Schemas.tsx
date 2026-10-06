import { useState } from 'react'

import { schemas as schemasApi } from '../api/endpoints'
import type { JSONSchemaRecord } from '../api/types'
import { Column, DataTable } from '../components/DataTable'
import { Alert, ConfirmDialog, Modal, PageHeader, Spinner, truncate } from '../components/ui'
import { useAction, useAsync } from '../hooks/useAsync'

interface EditorState {
  id: number | null
  name: string
  description: string
  schema: string
}

const BLANK: EditorState = {
  id: null,
  name: '',
  description: '',
  schema: JSON.stringify(
    { type: 'object', properties: {}, required: [], additionalProperties: false },
    null,
    2,
  ),
}

export function SchemasPage() {
  const schemasState = useAsync(() => schemasApi.list(), [])
  const { run, pending, error: actionError, clearError } = useAction()
  const [editor, setEditor] = useState<EditorState | null>(null)
  const [jsonError, setJsonError] = useState<string | null>(null)
  const [toDelete, setToDelete] = useState<JSONSchemaRecord | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  const save = async () => {
    if (!editor) return
    let parsed: Record<string, unknown>
    try {
      parsed = JSON.parse(editor.schema)
    } catch (error) {
      setJsonError(`That is not valid JSON: ${(error as Error).message}`)
      return
    }
    setJsonError(null)
    const payload = { name: editor.name, description: editor.description, schema: parsed }
    const saved = editor.id
      ? await run(() => schemasApi.update(editor.id as number, payload))
      : await run(() => schemasApi.create(payload))
    if (saved) {
      setEditor(null)
      setNotice('Schema saved.')
      schemasState.reload()
    }
  }

  const importBundled = async () => {
    const bundled = await run(() => schemasApi.bundled())
    if (!bundled) return
    // Compare against a freshly fetched list rather than whatever this screen
    // happens to hold: importing before the table finished loading would
    // otherwise create a second copy of every bundled schema.
    const current = await run(() => schemasApi.list())
    if (!current) return
    const existing = new Set(current.map((schema) => schema.name))
    const missing = bundled.filter((schema) => !existing.has(schema.name))
    if (missing.length === 0) {
      setNotice('Every bundled schema is already imported.')
      return
    }
    for (const schema of missing) {
      await run(() =>
        schemasApi.create({
          name: schema.name,
          description: 'Imported from the schemas shipped with the app',
          schema: schema.schema,
        }),
      )
    }
    setNotice(`Imported ${missing.length} bundled schema(s).`)
    schemasState.reload()
  }

  const columns: Column<JSONSchemaRecord>[] = [
    { key: 'name', header: 'Name' },
    { key: 'description', header: 'Description', render: (row) => truncate(row.description, 90) },
    {
      key: 'keys',
      header: 'Top-level keys',
      filterable: false,
      render: (row) => (
        <span className="font-monospace small">
          {Object.keys((row.schema?.properties as Record<string, unknown>) ?? {})
            .slice(0, 5)
            .join(', ') || '—'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      filterable: false,
      render: (row) => (
        <div className="btn-group btn-group-sm">
          <button
            type="button"
            className="btn btn-outline-secondary"
            onClick={() =>
              setEditor({
                id: row.id,
                name: row.name,
                description: row.description,
                schema: JSON.stringify(row.schema, null, 2),
              })
            }
          >
            <i className="bi bi-pencil" aria-hidden="true" />
            <span className="visually-hidden">Edit</span>
          </button>
          <a
            className="btn btn-outline-secondary"
            href={`/api/json-schemas/${row.id}/export/`}
            title="Download as JSON"
          >
            <i className="bi bi-download" aria-hidden="true" />
            <span className="visually-hidden">Export</span>
          </a>
          <button type="button" className="btn btn-outline-danger" onClick={() => setToDelete(row)}>
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
        title="JSON schemas"
        icon="diagram-3"
        description="Attach a schema to an assistant and every provider must return output that validates against it."
        actions={
          <>
            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={importBundled}
              disabled={pending || schemasState.loading}
            >
              <i className="bi bi-box-arrow-in-down me-1" aria-hidden="true" />
              Import bundled
            </button>
            <button type="button" className="btn btn-primary" onClick={() => setEditor({ ...BLANK })}>
              <i className="bi bi-plus-circle me-1" aria-hidden="true" />
              New schema
            </button>
          </>
        }
      />

      {schemasState.error && <Alert kind="danger">{schemasState.error}</Alert>}
      {actionError && <Alert kind="danger" onDismiss={clearError}>{actionError}</Alert>}
      {notice && <Alert kind="success" onDismiss={() => setNotice(null)}>{notice}</Alert>}

      {schemasState.loading ? (
        <Spinner />
      ) : (
        <DataTable
          rows={schemasState.data ?? []}
          columns={columns}
          rowKey={(row) => row.id}
          ariaLabel="Schema listing"
          emptyMessage="No schemas yet. Import the bundled ones to get started."
        />
      )}

      {editor && (
        <Modal
          title={editor.id ? `Edit ${editor.name}` : 'New JSON schema'}
          onClose={() => setEditor(null)}
          footer={
            <>
              <button type="button" className="btn btn-secondary" onClick={() => setEditor(null)} disabled={pending}>
                Cancel
              </button>
              <button type="button" className="btn btn-primary" onClick={save} disabled={pending}>
                {pending && <span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />}
                Save schema
              </button>
            </>
          }
        >
          {jsonError && <Alert kind="danger">{jsonError}</Alert>}
          <div className="mb-3">
            <label className="form-label" htmlFor="schema-name">
              Name
            </label>
            <input
              id="schema-name"
              className="form-control"
              value={editor.name}
              onChange={(event) => setEditor({ ...editor, name: event.target.value })}
            />
            <div className="form-text">Letters, numbers, underscores and hyphens.</div>
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="schema-description">
              Description
            </label>
            <input
              id="schema-description"
              className="form-control"
              value={editor.description}
              onChange={(event) => setEditor({ ...editor, description: event.target.value })}
            />
          </div>
          <div className="mb-0">
            <label className="form-label" htmlFor="schema-body">
              Schema (JSON)
            </label>
            <textarea
              id="schema-body"
              className="form-control code-editor"
              value={editor.schema}
              onChange={(event) => setEditor({ ...editor, schema: event.target.value })}
              spellCheck={false}
            />
          </div>
        </Modal>
      )}

      {toDelete && (
        <ConfirmDialog
          message={`Delete the schema "${toDelete.name}"? Assistants using it fall back to free-form text.`}
          pending={pending}
          onCancel={() => setToDelete(null)}
          onConfirm={async () => {
            const ok = await run(() => schemasApi.remove(toDelete.id))
            setToDelete(null)
            if (ok !== null) schemasState.reload()
          }}
        />
      )}
    </>
  )
}
