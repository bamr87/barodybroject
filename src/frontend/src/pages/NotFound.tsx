import { Link } from 'react-router-dom'

import { EmptyState } from '../components/ui'

export function NotFoundPage() {
  return (
    <EmptyState icon="compass" title="Page not found">
      <p className="mb-3">That address does not match anything in the app.</p>
      <Link className="btn btn-primary" to="/">
        Back to the dashboard
      </Link>
    </EmptyState>
  )
}
