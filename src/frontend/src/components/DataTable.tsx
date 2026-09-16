import { useMemo, useState, type ReactNode } from 'react'

/**
 * Sortable, per-column-filterable table.
 *
 * Replaces the old `includes/model_table.html` + `table_utils.js` pair. The
 * behaviour those carried is preserved deliberately:
 *
 * - every column header sorts, toggling asc/desc, one column at a time;
 * - numeric and date columns sort by value, not lexicographically (so 10
 *   sorts after 2), driven by the column's `sort` kind;
 * - each column has its own filter input and the filters combine (a row must
 *   match all of them);
 * - there are two distinct empty states: "nothing came back from the server"
 *   and "rows exist but no filter matches", because silently blanking the
 *   body was the reported bug behind issue #96.
 */

export type SortKind = 'text' | 'number' | 'date'

export interface Column<T> {
  key: string
  header: string
  /** Value used for sorting and filtering. Defaults to the rendered cell text. */
  value?: (row: T) => string | number | null | undefined
  render?: (row: T) => ReactNode
  sort?: SortKind
  filterable?: boolean
  className?: string
}

export interface DataTableProps<T> {
  rows: T[]
  columns: Column<T>[]
  rowKey: (row: T) => string | number
  onRowClick?: (row: T) => void
  emptyMessage?: string
  ariaLabel?: string
}

function rawValue<T>(row: T, column: Column<T>): string | number {
  if (column.value) {
    const value = column.value(row)
    return value === null || value === undefined ? '' : value
  }
  const record = row as unknown as Record<string, unknown>
  const value = record[column.key]
  return value === null || value === undefined ? '' : (value as string | number)
}

function compare<T>(a: T, b: T, column: Column<T>): number {
  const left = rawValue(a, column)
  const right = rawValue(b, column)
  if (column.sort === 'number') return Number(left) - Number(right)
  if (column.sort === 'date') return new Date(String(left)).getTime() - new Date(String(right)).getTime()
  return String(left).localeCompare(String(right))
}

export function DataTable<T>({
  rows,
  columns,
  rowKey,
  onRowClick,
  emptyMessage = 'No items found',
  ariaLabel = 'Data table',
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [direction, setDirection] = useState<'asc' | 'desc'>('asc')
  const [filters, setFilters] = useState<Record<string, string>>({})

  const visible = useMemo(() => {
    const active = Object.entries(filters).filter(([, query]) => query.trim() !== '')
    let result = rows
    if (active.length) {
      result = rows.filter((row) =>
        active.every(([key, query]) => {
          const column = columns.find((c) => c.key === key)
          if (!column) return true
          return String(rawValue(row, column)).toLowerCase().includes(query.trim().toLowerCase())
        }),
      )
    }
    if (sortKey) {
      const column = columns.find((c) => c.key === sortKey)
      if (column) {
        result = [...result].sort((a, b) => (direction === 'asc' ? compare(a, b, column) : compare(b, a, column)))
      }
    }
    return result
  }, [rows, columns, filters, sortKey, direction])

  const toggleSort = (key: string) => {
    if (sortKey === key) {
      setDirection((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setDirection('asc')
    }
  }

  const filtersActive = Object.values(filters).some((q) => q.trim() !== '')

  return (
    <div className="table-responsive">
      <table className="table table-hover align-middle" aria-label={ariaLabel}>
        <thead>
          <tr>
            {columns.map((column) => {
              const sorted = sortKey === column.key
              return (
                <th
                  key={column.key}
                  scope="col"
                  className={column.className}
                  aria-sort={sorted ? (direction === 'asc' ? 'ascending' : 'descending') : 'none'}
                >
                  <button
                    type="button"
                    className="btn btn-link p-0 text-decoration-none fw-semibold text-body"
                    onClick={() => toggleSort(column.key)}
                    aria-label={`Sort by ${column.header}`}
                  >
                    {column.header}
                    {sorted && (
                      <i className={`bi ms-1 bi-caret-${direction === 'asc' ? 'up' : 'down'}-fill`} aria-hidden="true" />
                    )}
                  </button>
                  {column.filterable !== false && (
                    <input
                      type="text"
                      className="form-control form-control-sm mt-1"
                      placeholder={`Filter ${column.header}...`}
                      aria-label={`Filter ${column.header}`}
                      value={filters[column.key] ?? ''}
                      onChange={(event) =>
                        setFilters((current) => ({ ...current, [column.key]: event.target.value }))
                      }
                    />
                  )}
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody>
          {visible.map((row) => (
            <tr
              key={rowKey(row)}
              onClick={onRowClick ? () => onRowClick(row) : undefined}
              onKeyDown={
                onRowClick
                  ? (event) => {
                      if (event.key === 'Enter') onRowClick(row)
                    }
                  : undefined
              }
              tabIndex={onRowClick ? 0 : undefined}
              role={onRowClick ? 'link' : undefined}
              style={onRowClick ? { cursor: 'pointer' } : undefined}
            >
              {columns.map((column) => (
                <td key={column.key} className={column.className}>
                  {column.render ? column.render(row) : String(rawValue(row, column))}
                </td>
              ))}
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td colSpan={columns.length} className="text-center text-muted py-4">
                <i className="bi bi-inbox me-1" aria-hidden="true" />
                {emptyMessage}
              </td>
            </tr>
          )}
          {rows.length > 0 && visible.length === 0 && filtersActive && (
            <tr data-testid="filter-empty">
              <td colSpan={columns.length} className="text-center text-muted py-4" role="status" aria-live="polite">
                No matching records
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
