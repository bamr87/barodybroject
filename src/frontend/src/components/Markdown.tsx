import { useMemo } from 'react'

/**
 * Render a small, safe subset of Markdown.
 *
 * Deliberately not `dangerouslySetInnerHTML` with a Markdown library: this
 * text comes back from a language model, so it is untrusted input rendered
 * into an authenticated page. Everything below produces React elements, which
 * escape their content, so no model output can inject markup.
 */

type Block =
  | { kind: 'heading'; level: number; text: string }
  | { kind: 'paragraph'; text: string }
  | { kind: 'list'; items: string[] }
  | { kind: 'code'; text: string }
  | { kind: 'quote'; text: string }

function parse(markdown: string): Block[] {
  const blocks: Block[] = []
  const lines = (markdown ?? '').replace(/\r\n/g, '\n').split('\n')
  let paragraph: string[] = []
  let list: string[] = []
  let code: string[] | null = null

  const flushParagraph = () => {
    if (paragraph.length) {
      blocks.push({ kind: 'paragraph', text: paragraph.join(' ') })
      paragraph = []
    }
  }
  const flushList = () => {
    if (list.length) {
      blocks.push({ kind: 'list', items: list })
      list = []
    }
  }

  for (const line of lines) {
    if (line.trimStart().startsWith('```')) {
      if (code === null) {
        flushParagraph()
        flushList()
        code = []
      } else {
        blocks.push({ kind: 'code', text: code.join('\n') })
        code = null
      }
      continue
    }
    if (code !== null) {
      code.push(line)
      continue
    }
    const heading = /^(#{1,6})\s+(.*)$/.exec(line)
    if (heading) {
      flushParagraph()
      flushList()
      blocks.push({ kind: 'heading', level: heading[1].length, text: heading[2] })
      continue
    }
    const item = /^\s*[-*+]\s+(.*)$/.exec(line)
    if (item) {
      flushParagraph()
      list.push(item[1])
      continue
    }
    const quote = /^\s*>\s?(.*)$/.exec(line)
    if (quote) {
      flushParagraph()
      flushList()
      blocks.push({ kind: 'quote', text: quote[1] })
      continue
    }
    if (line.trim() === '') {
      flushParagraph()
      flushList()
      continue
    }
    flushList()
    paragraph.push(line.trim())
  }
  if (code !== null) blocks.push({ kind: 'code', text: code.join('\n') })
  flushParagraph()
  flushList()
  return blocks
}

/** Split inline `**bold**`, `*italic*` and `` `code` `` into React nodes. */
function inline(text: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = []
  const pattern = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g
  let lastIndex = 0
  let match: RegExpExecArray | null
  let key = 0
  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) nodes.push(text.slice(lastIndex, match.index))
    const token = match[0]
    if (token.startsWith('**')) nodes.push(<strong key={key++}>{token.slice(2, -2)}</strong>)
    else if (token.startsWith('`')) nodes.push(<code key={key++}>{token.slice(1, -1)}</code>)
    else nodes.push(<em key={key++}>{token.slice(1, -1)}</em>)
    lastIndex = match.index + token.length
  }
  if (lastIndex < text.length) nodes.push(text.slice(lastIndex))
  return nodes
}

export function Markdown({ text, className }: { text: string; className?: string }) {
  const blocks = useMemo(() => parse(text), [text])
  if (!text?.trim()) return <p className="text-muted mb-0">No content yet.</p>
  return (
    <div className={className}>
      {blocks.map((block, index) => {
        switch (block.kind) {
          case 'heading': {
            const Tag = `h${Math.min(block.level + 1, 6)}` as 'h2'
            return <Tag key={index}>{inline(block.text)}</Tag>
          }
          case 'list':
            return (
              <ul key={index}>
                {block.items.map((item, i) => (
                  <li key={i}>{inline(item)}</li>
                ))}
              </ul>
            )
          case 'code':
            return (
              <pre key={index} className="bg-body-tertiary p-3 rounded">
                <code>{block.text}</code>
              </pre>
            )
          case 'quote':
            return (
              <blockquote key={index} className="blockquote border-start ps-3 text-muted">
                {inline(block.text)}
              </blockquote>
            )
          default:
            return <p key={index}>{inline(block.text)}</p>
        }
      })}
    </div>
  )
}
