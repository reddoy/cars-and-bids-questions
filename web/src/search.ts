import MiniSearch, { type SearchResult } from 'minisearch'
import type { Archive } from './data'

export type Hit = { id: string; terms: string[]; inAnswer: boolean; inQuestion: boolean }

/** Indexes the questions, episode titles and (once loaded) the hosts' answers. */
export function buildIndex(archive: Archive) {
  const index = new MiniSearch({
    fields: ['question', 'episode', 'answer'],
    searchOptions: {
      boost: { question: 5, episode: 1.5, answer: 1 },
      prefix: (term) => term.length > 2,
      fuzzy: (term) => (term.length > 4 ? 0.2 : false),
    },
  })
  index.addAll(
    archive.questions.map((q) => ({
      id: q.id,
      question: q.question,
      episode: archive.episodeById.get(q.video)?.title ?? '',
      answer: archive.transcripts?.[q.id] ?? '',
    })),
  )
  return index
}

export function search(index: MiniSearch, query: string): Hit[] {
  let results: SearchResult[] = index.search(query, { combineWith: 'AND' })
  if (!results.length) results = index.search(query, { combineWith: 'OR' })
  return results.map((r) => {
    const fields = new Set(Object.values(r.match).flat())
    return { id: String(r.id), terms: r.terms, inAnswer: fields.has('answer'), inQuestion: fields.has('question') }
  })
}

const escape = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

export function termPattern(terms: string[]) {
  const words = [...new Set(terms)].filter(Boolean).sort((a, b) => b.length - a.length)
  return words.length ? new RegExp(`(${words.map(escape).join('|')})`, 'gi') : null
}

/** A short piece of the answer around the first matching word. */
export function snippet(text: string, terms: string[], radius = 70) {
  const pattern = termPattern(terms)
  const flat = text.replace(/\n/g, ' ')
  const at = pattern ? flat.search(pattern) : -1
  if (at < 0) return null
  const start = Math.max(0, at - radius)
  const end = Math.min(flat.length, at + radius * 1.6)
  return `${start ? '…' : ''}${flat.slice(start, end).trim()}${end < flat.length ? '…' : ''}`
}
