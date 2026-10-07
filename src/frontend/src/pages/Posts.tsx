import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { posts as postsApi } from '../api/endpoints'
import type { Post, PostVersion } from '../api/types'
import { Column, DataTable } from '../components/DataTable'
import { Markdown } from '../components/Markdown'
import {
  Alert,
  ConfirmDialog,
  Modal,
  PageHeader,
  Spinner,
  StatusBadge,
  formatDate,
  truncate,
} from '../components/ui'
import { useAction, useAsync } from '../hooks/useAsync'

const COLUMNS: Column<Post>[] = [
  { key: 'id', header: 'ID', sort: 'number', className: 'text-nowrap' },
  {
    key: 'content_detail_title',
    header: 'Title',
    render: (row) => truncate(row.content_detail_title || `Post ${row.id}`, 60),
  },
  { key: 'assistant_name', header: 'Assistant' },
  { key: 'status', header: 'Status', render: (row) => <StatusBadge status={row.status} /> },
  { key: 'version_count', header: 'Versions', sort: 'number' },
  {
    key: 'updated_at',
    header: 'Updated',
    sort: 'date',
    render: (row) => <span className="text-nowrap">{formatDate(row.updated_at)}</span>,
  },
]

export function PostsPage() {
  const navigate = useNavigate()
  const { data, loading, error } = useAsync(() => postsApi.list(), [])

  return (
    <>
      <PageHeader
        title="Posts"
        icon="newspaper"
        description="Drafts ready to publish to the Jekyll site as a pull request."
      />
      {error && <Alert kind="danger">{error}</Alert>}
      {loading ? (
        <Spinner />
      ) : (
        <DataTable
          rows={data ?? []}
          columns={COLUMNS}
          rowKey={(row) => row.id}
          onRowClick={(row) => navigate(`/posts/${row.id}`)}
          ariaLabel="Post listing"
          emptyMessage="No posts yet. Create one from a thread message."
        />
      )}
    </>
  )
}

export function PostDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const postId = Number(id)

  const postState = useAsync(() => postsApi.get(postId), [postId])
  const { run, pending, error: actionError, clearError } = useAction()

  const [form, setForm] = useState({
    post_content: '',
    status: 'draft',
    title: '',
    description: '',
    author: '',
    slug: '',
  })
  const [versions, setVersions] = useState<PostVersion[] | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)
  const [publishedUrl, setPublishedUrl] = useState<string | null>(null)

  const post = postState.data
  useEffect(() => {
    if (!post) return
    setForm({
      post_content: post.post_content ?? '',
      status: post.status ?? 'draft',
      title: post.front_matter?.title ?? post.content_detail_title ?? '',
      description: post.front_matter?.description ?? '',
      author: post.front_matter?.author ?? '',
      slug: post.front_matter?.slug ?? '',
    })
  }, [post])

  const save = async () => {
    const saved = await run(() =>
      postsApi.update(postId, {
        post_content: form.post_content,
        status: form.status,
        front_matter: {
          title: form.title,
          description: form.description,
          author: form.author,
          slug: form.slug,
          published_at: post?.front_matter?.published_at ?? new Date().toISOString(),
        },
      }),
    )
    if (saved) {
      postState.setData(saved)
      setNotice('Saved.')
    }
  }

  const publish = async () => {
    const result = await run(() => postsApi.publish(postId))
    if (result) {
      postState.setData(result.post)
      setPublishedUrl(result.url)
      setNotice(`Published as version ${result.version.version_number}.`)
    }
  }

  if (postState.loading) return <Spinner />
  if (postState.error) return <Alert kind="danger">{postState.error}</Alert>
  if (!post) return <Alert kind="warning">Post not found.</Alert>

  return (
    <>
      <PageHeader
        title={form.title || `Post ${post.id}`}
        icon="file-earmark-text"
        description={
          <>
            <StatusBadge status={post.status} />
            {post.filename && <span className="ms-2 font-monospace small">{post.filename}</span>}
          </>
        }
        actions={
          <Link className="btn btn-outline-secondary" to="/posts">
            <i className="bi bi-arrow-left me-1" aria-hidden="true" />
            All posts
          </Link>
        }
      />

      {actionError && <Alert kind="danger" onDismiss={clearError}>{actionError}</Alert>}
      {notice && <Alert kind="success" onDismiss={() => setNotice(null)}>{notice}</Alert>}
      {publishedUrl && (
        <Alert kind="success" onDismiss={() => setPublishedUrl(null)}>
          Pull request opened:{' '}
          <a href={publishedUrl} target="_blank" rel="noopener noreferrer" className="alert-link">
            review it on GitHub <i className="bi bi-box-arrow-up-right" aria-hidden="true" />
          </a>
        </Alert>
      )}

      <div className="row g-4">
        <div className="col-lg-4">
          <div className="card">
            <div className="card-header">Front matter</div>
            <div className="card-body">
              {(['title', 'author', 'slug'] as const).map((field) => (
                <div className="mb-3" key={field}>
                  <label className="form-label text-capitalize" htmlFor={`fm-${field}`}>
                    {field}
                  </label>
                  <input
                    id={`fm-${field}`}
                    className="form-control"
                    value={form[field]}
                    onChange={(event) => setForm({ ...form, [field]: event.target.value })}
                  />
                </div>
              ))}
              <div className="mb-3">
                <label className="form-label" htmlFor="fm-description">
                  Description
                </label>
                <textarea
                  id="fm-description"
                  className="form-control"
                  rows={3}
                  value={form.description}
                  onChange={(event) => setForm({ ...form, description: event.target.value })}
                />
              </div>
              <div className="mb-0">
                <label className="form-label" htmlFor="fm-status">
                  Status
                </label>
                <select
                  id="fm-status"
                  className="form-select"
                  value={form.status}
                  onChange={(event) => setForm({ ...form, status: event.target.value })}
                >
                  {['draft', 'review', 'published', 'archived'].map((value) => (
                    <option key={value} value={value}>
                      {value}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>

        <div className="col-lg-8">
          <div className="card">
            <div className="card-header">Markdown body</div>
            <div className="card-body">
              <textarea
                className="form-control code-editor"
                value={form.post_content}
                onChange={(event) => setForm({ ...form, post_content: event.target.value })}
                aria-label="Post body"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="d-flex flex-wrap gap-2 mt-4">
        <button type="button" className="btn btn-primary" onClick={save} disabled={pending}>
          {pending && <span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />}
          <i className="bi bi-save me-1" aria-hidden="true" />
          Save
        </button>
        <button type="button" className="btn btn-success" onClick={publish} disabled={pending}>
          <i className="bi bi-cloud-upload me-1" aria-hidden="true" />
          Publish to GitHub
        </button>
        <button
          type="button"
          className="btn btn-outline-secondary"
          disabled={pending}
          onClick={async () => {
            const rendered = await run(() => postsApi.render(postId))
            if (rendered) setPreview(rendered.document)
          }}
        >
          <i className="bi bi-eye me-1" aria-hidden="true" />
          Preview file
        </button>
        <button
          type="button"
          className="btn btn-outline-secondary"
          disabled={pending}
          onClick={async () => {
            const list = await run(() => postsApi.versions(postId))
            if (list) setVersions(list)
          }}
        >
          <i className="bi bi-clock-history me-1" aria-hidden="true" />
          Versions ({post.version_count})
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
      </div>

      <div className="card mt-4">
        <div className="card-header">Rendered preview</div>
        <div className="card-body">
          <Markdown text={form.post_content} className="prose" />
        </div>
      </div>

      {preview && (
        <Modal title="Published file" onClose={() => setPreview(null)}>
          <pre className="code-block mb-0">{preview}</pre>
        </Modal>
      )}

      {versions && (
        <Modal title="Version history" onClose={() => setVersions(null)}>
          {versions.length === 0 ? (
            <p className="mb-0 text-muted">No versions yet. Publishing creates one.</p>
          ) : (
            <ul className="list-group list-group-flush">
              {versions.map((version) => (
                <li className="list-group-item px-0" key={version.id}>
                  <div className="d-flex justify-content-between">
                    <strong>Version {version.version_number}</strong>
                    <span className="text-muted small">{formatDate(version.created_at)}</span>
                  </div>
                  <pre className="code-block mb-0 mt-2">{truncate(version.content, 400)}</pre>
                </li>
              ))}
            </ul>
          )}
        </Modal>
      )}

      {confirmDelete && (
        <ConfirmDialog
          message="Delete this post? Published pull requests are not affected."
          pending={pending}
          onCancel={() => setConfirmDelete(false)}
          onConfirm={async () => {
            const ok = await run(() => postsApi.remove(postId))
            if (ok !== null) navigate('/posts')
          }}
        />
      )}
    </>
  )
}
