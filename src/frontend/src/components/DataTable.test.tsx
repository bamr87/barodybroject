/**
 * Behaviour the old `table_utils.js` carried, now pinned in the component that
 * replaced it. Each test below was a regression in the Django implementation
 * (issues #96 and the sortable-header contract), so they are kept deliberately.
 */

import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { Column, DataTable } from './DataTable'

interface Row {
  id: number
  username: string
  joined: string
}

// Ids chosen so numeric and lexicographic ordering disagree: as text the order
// is 1, 10, 2; as numbers it is 1, 2, 10.
const ROWS: Row[] = [
  { id: 2, username: 'bravo', joined: '2024-02-01T00:00:00Z' },
  { id: 10, username: 'charlie', joined: '2023-01-01T00:00:00Z' },
  { id: 1, username: 'alpha', joined: '2025-03-01T00:00:00Z' },
]

const COLUMNS: Column<Row>[] = [
  { key: 'id', header: 'ID', sort: 'number' },
  { key: 'username', header: 'Username' },
  { key: 'joined', header: 'Joined', sort: 'date' },
]

function renderTable(rows: Row[] = ROWS) {
  return render(<DataTable rows={rows} columns={COLUMNS} rowKey={(row) => row.id} />)
}

function bodyValues(columnIndex: number): string[] {
  const body = screen.getAllByRole('rowgroup')[1]
  return within(body)
    .getAllByRole('row')
    .filter((row) => row.querySelectorAll('td').length === COLUMNS.length)
    .map((row) => row.querySelectorAll('td')[columnIndex].textContent?.trim() ?? '')
}

describe('DataTable sorting', () => {
  it('sorts a text column and toggles direction', async () => {
    const user = userEvent.setup()
    renderTable()

    await user.click(screen.getByRole('button', { name: 'Sort by Username' }))
    expect(bodyValues(1)).toEqual(['alpha', 'bravo', 'charlie'])

    await user.click(screen.getByRole('button', { name: 'Sort by Username' }))
    expect(bodyValues(1)).toEqual(['charlie', 'bravo', 'alpha'])
  })

  it('sorts numeric columns by value, not lexicographically', async () => {
    const user = userEvent.setup()
    renderTable()

    await user.click(screen.getByRole('button', { name: 'Sort by ID' }))

    // Lexicographic ordering would give 1, 10, 2.
    expect(bodyValues(0)).toEqual(['1', '2', '10'])
  })

  it('sorts date columns chronologically', async () => {
    const user = userEvent.setup()
    renderTable()

    await user.click(screen.getByRole('button', { name: 'Sort by Joined' }))

    expect(bodyValues(1)).toEqual(['charlie', 'bravo', 'alpha'])
  })

  it('sorting a second column clears the first', async () => {
    const user = userEvent.setup()
    renderTable()

    await user.click(screen.getByRole('button', { name: 'Sort by Username' }))
    await user.click(screen.getByRole('button', { name: 'Sort by ID' }))

    expect(screen.getByRole('columnheader', { name: /Username/ })).toHaveAttribute('aria-sort', 'none')
    expect(screen.getByRole('columnheader', { name: /ID/ })).toHaveAttribute('aria-sort', 'ascending')
  })

  it('announces the sorted column to assistive technology', async () => {
    const user = userEvent.setup()
    renderTable()

    const header = screen.getByRole('columnheader', { name: /Username/ })
    expect(header).toHaveAttribute('aria-sort', 'none')

    await user.click(screen.getByRole('button', { name: 'Sort by Username' }))
    expect(header).toHaveAttribute('aria-sort', 'ascending')
  })
})

describe('DataTable filtering', () => {
  it('narrows a column and restores when cleared', async () => {
    const user = userEvent.setup()
    renderTable()

    const filter = screen.getByLabelText('Filter Username')
    await user.type(filter, 'al')
    expect(bodyValues(1)).toEqual(['alpha'])

    await user.clear(filter)
    expect(bodyValues(1).sort()).toEqual(['alpha', 'bravo', 'charlie'])
  })

  it('filters case-insensitively', async () => {
    const user = userEvent.setup()
    renderTable()

    await user.type(screen.getByLabelText('Filter Username'), 'ALPHA')
    expect(bodyValues(1)).toEqual(['alpha'])
  })

  it('combines filters across columns', async () => {
    const user = userEvent.setup()
    renderTable()

    await user.type(screen.getByLabelText('Filter Username'), 'alpha')
    await user.type(screen.getByLabelText('Filter ID'), '2')

    // alpha is id 1, so requiring both leaves nothing.
    expect(screen.getByTestId('filter-empty')).toBeInTheDocument()
  })

  it('re-evaluates the remaining filters when one is cleared', async () => {
    const user = userEvent.setup()
    renderTable()

    const username = screen.getByLabelText('Filter Username')
    const ident = screen.getByLabelText('Filter ID')
    await user.type(username, 'alpha')
    await user.type(ident, '2')
    expect(screen.getByTestId('filter-empty')).toBeInTheDocument()

    await user.clear(ident)

    // Clearing one filter must not reveal rows the other still excludes.
    expect(bodyValues(1)).toEqual(['alpha'])
  })
})

describe('DataTable empty states', () => {
  it('shows the server empty state when nothing came back', () => {
    renderTable([])
    expect(screen.getByText('No items found')).toBeInTheDocument()
    expect(screen.queryByTestId('filter-empty')).not.toBeInTheDocument()
  })

  it('explains an empty filter result instead of blanking silently', async () => {
    const user = userEvent.setup()
    renderTable()

    await user.type(screen.getByLabelText('Filter Username'), 'zzzzzz')

    const message = screen.getByTestId('filter-empty')
    expect(message).toHaveTextContent('No matching records')
    // It replaces content that would otherwise vanish without a word, so a
    // screen-reader user has to hear about it too.
    expect(within(message).getByRole('status')).toHaveAttribute('aria-live', 'polite')
  })

  it('never stacks the two empty states', async () => {
    const user = userEvent.setup()
    renderTable([])

    await user.type(screen.getByLabelText('Filter Username'), 'zzzzzz')

    expect(screen.getByText('No items found')).toBeInTheDocument()
    expect(screen.queryByTestId('filter-empty')).not.toBeInTheDocument()
  })
})
