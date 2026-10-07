/**
 * Behaviour issue #3 asked for, pinned in the component that replaced the form
 * it was filed against.
 *
 * `ContentItemForm.__init__` (`src/parodynews/forms.py`, deleted by #183) could
 * not tell a brand-new form from a saved `ContentItem` whose nullable
 * `assistant` FK was NULL: `self.initial` reports `assistant: None` for both.
 * It answered that ambiguity with `Assistant.objects.order_by("?").first()`, so
 * opening an existing NULL-assistant item pre-selected a RANDOM assistant — a
 * different one on each reload — and saving any unrelated edit persisted it.
 * `ContentItem.assistant` is `on_delete=SET_NULL`, so items reach that state on
 * their own whenever an assistant is deleted.
 *
 * The React rewrite does not carry the defect: the select is bound straight to
 * the record. These tests keep it that way — each one fails if the seeding
 * behaviour is ever reintroduced.
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { Assistant, ContentDetail, ContentItem } from '../api/types'

vi.mock('../api/endpoints', () => ({
  content: {
    get: vi.fn(),
    update: vi.fn(),
    create: vi.fn(),
    remove: vi.fn(),
    generate: vi.fn(),
    createThread: vi.fn(),
  },
  assistants: { list: vi.fn() },
  assistantGroups: { list: vi.fn() },
}))

const ASSISTANTS = [
  { id: 'asst_alpha', name: 'Alpha', model_detail: null },
  { id: 'asst_bravo', name: 'Bravo', model_detail: null },
  { id: 'asst_charlie', name: 'Charlie', model_detail: null },
] as unknown as Assistant[]

function item(overrides: Partial<ContentItem> = {}): ContentItem {
  return {
    id: 1,
    detail: 7,
    line_number: 1,
    content_type: 'post',
    content_text: 'In a shocking turn of events...',
    assistant: null,
    assistant_name: '',
    prompt: 'Write an opening paragraph',
    ...overrides,
  }
}

function detail(overrides: Partial<ContentDetail> = {}): ContentDetail {
  return {
    id: 7,
    title: 'Local Cat Declares Independence',
    description: 'Satirical article about feline autonomy',
    author: 'ParodyNews Staff',
    published_at: '2024-01-15T00:00:00Z',
    slug: 'cat-independence',
    keywords: [],
    user: null,
    items: [item()],
    ...overrides,
  }
}

async function renderDetail(id: string, saved: ContentDetail | null) {
  const { ContentDetailPage } = await import('./Content')
  const endpoints = await import('../api/endpoints')

  vi.mocked(endpoints.assistants.list).mockResolvedValue(ASSISTANTS)
  vi.mocked(endpoints.assistantGroups.list).mockResolvedValue([])
  vi.mocked(endpoints.content.get).mockResolvedValue(saved as ContentDetail)

  render(
    <MemoryRouter initialEntries={[`/content/${id}`]}>
      <Routes>
        <Route path="/content/:id" element={<ContentDetailPage />} />
      </Routes>
    </MemoryRouter>,
  )

  // The select renders before the assistant list resolves; wait for the options.
  await screen.findByRole('option', { name: 'Alpha' })
  return { endpoints, select: screen.getByLabelText('Assistant') as HTMLSelectElement }
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('the assistant select on an existing content item', () => {
  it('pre-selects nothing when the item has no assistant', async () => {
    const { select } = await renderDetail('7', detail())

    await waitFor(() => expect(select.value).toBe(''))
    const blank = screen.getByRole('option', { name: 'Select an assistant' }) as HTMLOptionElement
    expect(blank.selected).toBe(true)
  })

  it('is stable across renders when the item has no assistant', async () => {
    // The defect was non-deterministic: `.order_by("?")` could pick a different
    // assistant each load. Asserting "empty" rather than "not Alpha" is what
    // makes this test able to fail.
    const { select } = await renderDetail('7', detail())
    await waitFor(() => expect(select.value).toBe(''))

    const seen = new Set<string>()
    for (let i = 0; i < 5; i += 1) seen.add(select.value)
    expect([...seen]).toEqual([''])
  })

  it("shows the item's own assistant when it has one", async () => {
    const { select } = await renderDetail('7', detail({ items: [item({ assistant: 'asst_bravo' })] }))

    await waitFor(() => expect(select.value).toBe('asst_bravo'))
  })

  it('saves NULL rather than silently reassigning an unmodified item', async () => {
    const { endpoints, select } = await renderDetail('7', detail())
    await waitFor(() => expect(select.value).toBe(''))
    vi.mocked(endpoints.content.update).mockResolvedValue(detail())

    await userEvent.click(screen.getByRole('button', { name: /save changes/i }))

    await waitFor(() => expect(endpoints.content.update).toHaveBeenCalled())
    const [, payload] = vi.mocked(endpoints.content.update).mock.calls[0]
    expect(payload.assistant).toBeNull()
  })

  it('saves the assistant the user picks', async () => {
    const { endpoints, select } = await renderDetail('7', detail())
    await waitFor(() => expect(select.value).toBe(''))
    vi.mocked(endpoints.content.update).mockResolvedValue(detail())

    await userEvent.selectOptions(select, 'asst_charlie')
    await userEvent.click(screen.getByRole('button', { name: /save changes/i }))

    await waitFor(() => expect(endpoints.content.update).toHaveBeenCalled())
    const [, payload] = vi.mocked(endpoints.content.update).mock.calls[0]
    expect(payload.assistant).toBe('asst_charlie')
  })
})

describe('the assistant select on a new content item', () => {
  it('starts empty and asks for an explicit choice', async () => {
    const { endpoints, select } = await renderDetail('new', null)

    expect(select.value).toBe('')
    // A new form must not be fetched, so there is no instance to confuse with.
    expect(endpoints.content.get).not.toHaveBeenCalled()
  })
})
