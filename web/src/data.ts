import { createContext, useContext, useEffect, useState } from 'react'
import { Banknote, Car, MessageCircle, Sparkles, Telescope, Trophy, type LucideIcon } from 'lucide-react'

export type Category =
  | 'Personal Questions'
  | 'Money & Value'
  | 'Car Brands'
  | 'Rankings & Comparisons'
  | 'Future & Predictions'
  | 'General'

export type Episode = {
  id: string
  number: number | null
  title: string
  published: string
  duration: number | null
  questions: number
}

export type Question = {
  id: string
  video: string
  t: number
  end: number
  question: string
  category: Category
  hasAnswer: boolean
}

export type Archive = {
  episodes: Episode[]
  questions: Question[]
  episodeById: Map<string, Episode>
  questionById: Map<string, Question>
  questionsByEpisode: Map<string, Question[]>
  transcripts: Record<string, string> | null
}

export const CATEGORIES: { name: Category; label: string; color: string; icon: LucideIcon }[] = [
  { name: 'Personal Questions', label: 'Personal', color: '#5fd39b', icon: MessageCircle },
  { name: 'Money & Value', label: 'Money & Value', color: '#ffe14d', icon: Banknote },
  { name: 'Car Brands', label: 'Cars & Brands', color: '#7cc4ff', icon: Car },
  { name: 'Rankings & Comparisons', label: 'Rankings', color: '#ff8a5b', icon: Trophy },
  { name: 'Future & Predictions', label: 'Predictions', color: '#c59bff', icon: Telescope },
  { name: 'General', label: 'General', color: '#a1a1aa', icon: Sparkles },
]

export const categoryInfo = (name: Category) => CATEGORIES.find((c) => c.name === name) ?? CATEGORIES[5]

const url = (file: string) => `${import.meta.env.BASE_URL}data/${file}`

async function getJson<T>(file: string): Promise<T> {
  const response = await fetch(url(file))
  if (!response.ok) throw new Error(`Couldn't load ${file}`)
  return response.json()
}

/** Loads episodes and questions first, then the (much larger) answer transcripts. */
export function useArchiveLoader() {
  const [archive, setArchive] = useState<Archive | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([getJson<Episode[]>('episodes.json'), getJson<Question[]>('questions.json')])
      .then(([episodes, questions]) => {
        if (cancelled) return
        const questionsByEpisode = new Map<string, Question[]>()
        for (const q of questions) {
          const list = questionsByEpisode.get(q.video) ?? []
          list.push(q)
          questionsByEpisode.set(q.video, list)
        }
        for (const list of questionsByEpisode.values()) list.sort((a, b) => a.t - b.t)
        setArchive({
          episodes,
          questions,
          episodeById: new Map(episodes.map((e) => [e.id, e])),
          questionById: new Map(questions.map((q) => [q.id, q])),
          questionsByEpisode,
          transcripts: null,
        })
        return getJson<Record<string, string>>('transcripts.json')
      })
      .then((transcripts) => {
        if (!cancelled && transcripts) setArchive((current) => current && { ...current, transcripts })
      })
      .catch((e: Error) => !cancelled && setError(e.message))
    return () => {
      cancelled = true
    }
  }, [])

  return { archive, error }
}

export const ArchiveContext = createContext<Archive | null>(null)

export function useArchive(): Archive {
  const archive = useContext(ArchiveContext)
  if (!archive) throw new Error('useArchive must be used inside ArchiveContext')
  return archive
}
