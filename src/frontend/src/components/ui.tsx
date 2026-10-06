import type { ReactNode } from 'react'
import { useEffect, useRef } from 'react'

export function Spinner({ label = 'Loading...' }: { label?: string }) {
  return (
    <div className="d-flex align-items-center gap-2 text-muted py-4" role="status">
      <span className="spinner-border spinner-border-sm" aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}

export function Alert({
  kind = 'danger',
  children,
  onDismiss,
}: {
  kind?: 'danger' | 'warning' | 'success' | 'info'
  children: ReactNode
  onDismiss?: () => void
}) {
  return (
    <div className={`alert alert-${kind} ${onDismiss ? 'alert-dismissible' : ''}`} role="alert">
      {children}
      {onDismiss && <button type="button" className="btn-close" aria-label="Dismiss" onClick={onDismiss} />}
    </div>
  )
}

export function PageHeader({
  title,
  icon,
  description,
  actions,
}: {
  title: string
  icon?: string
  description?: ReactNode
  actions?: ReactNode
}) {
  return (
    <div className="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-3">
      <div>
        <h1 className="h3 mb-1">
          {icon && <i className={`bi bi-${icon} me-2`} aria-hidden="true" />}
          {title}
        </h1>
        {description && <p className="text-muted mb-0">{description}</p>}
      </div>
      {actions && <div className="d-flex gap-2 flex-wrap">{actions}</div>}
    </div>
  )
}

export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { cls: string; icon: string }> = {
    draft: { cls: 'secondary', icon: 'pencil' },
    queued: { cls: 'secondary', icon: 'clock' },
    initial: { cls: 'secondary', icon: 'clock' },
    in_progress: { cls: 'warning text-dark', icon: 'arrow-repeat' },
    completed: { cls: 'success', icon: 'check-circle' },
    published: { cls: 'success', icon: 'cloud-check' },
    failed: { cls: 'danger', icon: 'x-circle' },
  }
  const style = map[status] ?? { cls: 'info', icon: 'info-circle' }
  return (
    <span className={`badge text-bg-${style.cls}`}>
      <i className={`bi bi-${style.icon} me-1`} aria-hidden="true" />
      {status.replace(/_/g, ' ')}
    </span>
  )
}

export function ProviderBadge({ provider }: { provider: string }) {
  if (!provider) return <span className="text-muted">default</span>
  return <span className="badge text-bg-light border font-monospace">{provider}</span>
}

/** Bootstrap-styled modal rendered inline (no Bootstrap JS needed). */
export function Modal({
  title,
  children,
  footer,
  onClose,
}: {
  title: string
  children: ReactNode
  footer?: ReactNode
  onClose: () => void
}) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    ref.current?.focus()
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <>
      <div className="modal-backdrop show" onClick={onClose} />
      <div className="modal d-block" role="dialog" aria-modal="true" aria-label={title}>
        <div className="modal-dialog modal-dialog-centered modal-lg">
          <div className="modal-content" ref={ref} tabIndex={-1}>
            <div className="modal-header">
              <h2 className="modal-title h5">{title}</h2>
              <button type="button" className="btn-close" aria-label="Close" onClick={onClose} />
            </div>
            <div className="modal-body">{children}</div>
            {footer && <div className="modal-footer">{footer}</div>}
          </div>
        </div>
      </div>
    </>
  )
}

export function ConfirmDialog({
  title = 'Confirm action',
  message,
  confirmLabel = 'Delete',
  onConfirm,
  onCancel,
  pending = false,
}: {
  title?: string
  message: string
  confirmLabel?: string
  onConfirm: () => void
  onCancel: () => void
  pending?: boolean
}) {
  return (
    <Modal
      title={title}
      onClose={onCancel}
      footer={
        <>
          <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={pending}>
            Cancel
          </button>
          <button type="button" className="btn btn-danger" onClick={onConfirm} disabled={pending}>
            {pending && <span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />}
            {confirmLabel}
          </button>
        </>
      }
    >
      <p className="mb-0">{message}</p>
    </Modal>
  )
}

export function EmptyState({ icon, title, children }: { icon: string; title: string; children?: ReactNode }) {
  return (
    <div className="text-center text-muted py-5">
      <i className={`bi bi-${icon}`} style={{ fontSize: '2.5rem' }} aria-hidden="true" />
      <p className="h5 mt-3">{title}</p>
      {children}
    </div>
  )
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function truncate(value: string, length = 120): string {
  const flat = (value ?? '').replace(/\s+/g, ' ').trim()
  return flat.length > length ? `${flat.slice(0, length)}...` : flat
}
