import type { Episode } from './data'

/** 4316 -> "1:11:56" */
export function clock(seconds: number) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  const mm = h ? String(m).padStart(2, '0') : String(m)
  return `${h ? `${h}:` : ''}${mm}:${String(s).padStart(2, '0')}`
}

/** 156 -> "2m 36s" */
export function span(seconds: number) {
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  return m ? `${m}m ${s}s` : `${s}s`
}

export function date(iso: string) {
  return new Date(`${iso}T12:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

/** Drops the "THIS CAR POD! EP95" suffix from episode titles. */
export function shortTitle(episode: Episode) {
  return episode.title
    .replace(/\s*[|\-–]?\s*THIS\s*CAR\s*POD!?(\s*EP\.?\s?\d+)?\s*$/i, '')
    .replace(/\s*[|\-–]\s*(EP\.?\s?\d+)\s*$/i, '')
    .replace(/[\s|\-–]+$/, '')
    .trim()
}

export const episodeLabel = (episode: Episode) => (episode.number ? `EP ${episode.number}` : 'Special')

export const thumbnail = (videoId: string, size: 'mq' | 'hq' | 'maxres' = 'mq') =>
  `https://i.ytimg.com/vi/${videoId}/${size}default.jpg`

export const youtubeAt = (videoId: string, t: number) => `https://www.youtube.com/watch?v=${videoId}&t=${t}s`
