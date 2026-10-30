import { Search } from 'lucide-react'
import { motion } from 'motion/react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router'
import { useArchive } from '../data'
import { date, episodeLabel, shortTitle, thumbnail } from '../format'

export default function EpisodesPage() {
  const { episodes } = useArchive()
  const [filter, setFilter] = useState('')

  const shown = useMemo(() => {
    const words = filter.toLowerCase().split(/\s+/).filter(Boolean)
    return episodes.filter((e) => words.every((w) => `${e.title} ep ${e.number}`.toLowerCase().includes(w)))
  }, [episodes, filter])

  return (
    <>
      <header className="flex flex-col gap-5 pb-8 pt-12 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.25em] text-mint">The back catalog</p>
          <h1 className="font-wide mt-2 text-5xl font-black uppercase tracking-tight sm:text-6xl">Every episode</h1>
          <p className="mt-2 text-white/50">{episodes.length} episodes, newest first.</p>
        </div>
        <label className="flex items-center gap-2 rounded-xl border border-line bg-panel px-4 py-2.5 focus-within:border-mint/60 sm:w-72">
          <Search className="size-4 text-white/40" />
          <input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Filter episodes" className="w-full bg-transparent text-sm outline-none placeholder:text-white/30" />
        </label>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {shown.map((episode, i) => (
          <motion.div
            key={episode.id}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-40px' }}
            transition={{ duration: 0.45, delay: (i % 3) * 0.06, ease: [0.16, 1, 0.3, 1] }}
          >
            <Link to={`/episodes/${episode.id}`} className="group relative block overflow-hidden rounded-2xl border border-line bg-panel transition hover:border-mint/40">
              <div className="relative aspect-video overflow-hidden">
                <img src={thumbnail(episode.id, 'hq')} alt="" loading="lazy" className="size-full scale-[1.02] object-cover transition duration-700 group-hover:scale-110" />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent" />
                <div className="font-wide absolute bottom-3 left-4 text-5xl font-black leading-none tracking-tighter text-white drop-shadow-lg transition group-hover:text-mint">
                  {episodeLabel(episode).replace('EP ', '')}
                  <span className="ml-1 align-top text-sm tracking-normal text-white/60">{episode.number ? 'EP' : ''}</span>
                </div>
                <span className="absolute right-3 top-3 rounded-full bg-black/70 px-2.5 py-1 text-xs font-bold backdrop-blur">
                  <span className="text-sun">{episode.questions}</span> questions
                </span>
              </div>
              <div className="p-4">
                <h2 className="line-clamp-2 font-semibold leading-snug">{shortTitle(episode)}</h2>
                <p className="mt-1.5 text-xs text-white/45">{date(episode.published)}</p>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
      {!shown.length && <p className="py-16 text-center text-white/50">No episodes match “{filter}”.</p>}
    </>
  )
}
