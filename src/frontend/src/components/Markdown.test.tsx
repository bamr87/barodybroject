import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { Markdown } from './Markdown'

describe('Markdown', () => {
  it('renders headings, paragraphs and lists', () => {
    render(<Markdown text={'# Title\n\nA paragraph.\n\n- one\n- two'} />)

    expect(screen.getByRole('heading', { name: 'Title' })).toBeInTheDocument()
    expect(screen.getByText('A paragraph.')).toBeInTheDocument()
    expect(screen.getAllByRole('listitem')).toHaveLength(2)
  })

  it('renders inline emphasis and code', () => {
    const { container } = render(<Markdown text="Some **bold**, some *italic*, some `code`." />)

    expect(container.querySelector('strong')).toHaveTextContent('bold')
    expect(container.querySelector('em')).toHaveTextContent('italic')
    expect(container.querySelector('code')).toHaveTextContent('code')
  })

  it('never injects model output as HTML', () => {
    // The text comes from a language model, so markup in it must be shown as
    // text rather than parsed into elements.
    const { container } = render(<Markdown text={'<img src=x onerror="alert(1)">'} />)

    expect(container.querySelector('img')).toBeNull()
    expect(container.textContent).toContain('<img src=x onerror="alert(1)">')
  })

  it('keeps fenced code blocks intact', () => {
    const { container } = render(<Markdown text={'```\nline one\nline two\n```'} />)

    expect(container.querySelector('pre code')?.textContent).toBe('line one\nline two')
  })

  it('says so when there is nothing to show', () => {
    render(<Markdown text="   " />)
    expect(screen.getByText('No content yet.')).toBeInTheDocument()
  })
})
