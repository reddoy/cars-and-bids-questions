import { ArrowLeft, Play } from 'lucide-react'
import { motion } from 'motion/react'
import { useState } from 'react'
import { Link, useParams } from 'react-router'
import CategoryTag from '../components/CategoryTag'
import { categoryInfo, useArchive } from '../data'
import { clock, date, episodeLabel, shortTitle, span, thumbnail, youtubeAt } from '../format'
import { useOpenQuestion } from '../hooks'

export default function EpisodePage() {
  const { id = '' } = useParams()
  const archive = useArchive()
  const { open } = useOpenQuestion()
  const episode = archive.episodeById.get(id)
  const questions = archive.questionsByEpisode.get(id) ?? []
  const [hovered, setHovered] = useState<string | null>(null)
  const [hero, setHero] = useState(thumbnail(id, 'maxres'))

  if (!episode) return <p className="py-24 text-center text-white/50">That episode isn't in the archive.</p>

  const length = episode.duration ?? Math.max(...questions.map((q) => q.end), 1)

  return (
    <>
      <Link to="/episodes" className="mt-8 inline-flex items-center gap-2 text-sm text-white/50 transition hover:text-white">
        <ArrowLeft className="size-4" /> All episodes
      </Link>

      <section className="relative mt-5 overflow-hidden rounded-3xl border border-line">
        <img src={hero} onError={() => setHero(thumbnail(id, 'hq'))} alt="" className="absolute inset-0 size-full scale-110 object-cover opacity-40 blur-2xl" />
        <div className="relative grid gap-6 bg-gradient-to-r from-black/90 via-black/70 to-black/40 p-5 sm:p-8 md:grid-cols-[1fr_1.1fr] md:items-center">
          <motion.img
            src={hero}
            alt=""
            className="aspect-video w-full rounded-2xl object-cover shadow-2xl shadow-black"
            initial={{ opacity: 0, scale: 0.94 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          />
          <div>
            <span className="font-wide rounded-lg bg-mint px-2.5 py-1 text-sm font-black text-black">{episodeLabel(episode)}</span>
            <h1 className="font-wide mt-4 text-3xl font-black leading-tight text-balance sm:text-4xl">{shortTitle(episode)}</h1>
            <p className="mt-3 text-sm text-white/55">
              {date(episode.published)}
              {episode.duration ? ` · ${Math.round(episode.duration / 60)} min` : ''} · {questions.length} community questions
            </p>
            <a
              href={youtubeAt(episode.id, 0)}
              target="_blank"
              rel="noreferrer"
              className="mt-6 inline-flex items-center gap-2 rounded-full bg-white px-5 py-2.5 text-sm font-bold text-black transition hover:scale-105 hover:bg-mint"
            >
              <Play className="size-4 fill-current" /> Watch the episode
            </a>
          </div>
        </div>

        {questions.length > 0 && (
          <div className="relative border-t border-line bg-black/60 px-5 py-6 sm:px-8">
            <div className="mb-3 flex justify-between text-[11px] font-semibold uppercase tracking-widest text-white/40">
              <span>Start</span>
              <span>Where the questions land</span>
              <span>{clock(length)}</span>
            </div>
            <div className="relative h-3 rounded-full bg-white/10">
              <motion.div
                className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-white/5 to-white/20"
                initial={{ width: 0 }}
                animate={{ width: `${(questions[0].t / length) * 100}%` }}
                transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
              />
              {questions.map((q, i) => (
                <motion.button
                  key={q.id}
                  aria-label={q.question}
                  onClick={() => open(q.id)}
                  onMouseEnter={() => setHovered(q.id)}
                  onMouseLeave={() => setHovered(null)}
                  className="absolute top-1/2 size-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-black"
                  style={{ left: `${(q.t / length) * 100}%`, backgroundColor: categoryInfo(q.category).color }}
                  initial={{ scale: 0 }}
                  animate={{ scale: hovered === q.id ? 1.6 : 1 }}
                  transition={{ delay: hovered ? 0 : 0.4 + i * 0.05, type: 'spring', stiffness: 400, damping: 18 }}
                />
              ))}
            </div>
          </div>
        )}
      </section>

      <ol className="relative mt-10 space-y-3 before:absolute before:bottom-4 before:left-[calc(6.125rem+1px)] before:top-4 before:w-px before:bg-line sm:before:left-[calc(7.875rem+1px)]">
        {questions.map((q, i) => (
          <motion.li
            key={q.id}
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.15 + i * 0.05, ease: [0.16, 1, 0.3, 1] }}
            onMouseEnter={() => setHovered(q.id)}
            onMouseLeave={() => setHovered(null)}
          >
            <button
              onClick={() => open(q.id)}
              className={`group flex w-full items-center gap-4 rounded-2xl border p-3 text-left transition sm:gap-6 sm:p-4 ${
                hovered === q.id ? 'border-mint/40 bg-white/[0.04]' : 'border-transparent'
              }`}
            >
              <span className="w-16 shrink-0 text-right font-mono text-xs text-white/50 sm:w-20 sm:text-sm">{clock(q.t)}</span>
              <span className="relative z-10 size-3 shrink-0 rounded-full ring-4 ring-ink" style={{ backgroundColor: categoryInfo(q.category).color }} />
              <span className="min-w-0 flex-1">
                <span className="font-wide block font-bold leading-snug group-hover:text-mint sm:text-lg">{q.question}</span>
                <span className="mt-2 flex flex-wrap items-center gap-2 text-xs text-white/40">
                  <CategoryTag category={q.category} />
                  {span(q.end - q.t)} answer
                </span>
              </span>
              <Play className="size-5 shrink-0 text-white/30 transition group-hover:scale-125 group-hover:text-mint" />
            </button>
          </motion.li>
        ))}
      </ol>
      {!questions.length && <p className="py-12 text-center text-white/50">No community questions were listed for this episode.</p>}
    </>
  )
}
