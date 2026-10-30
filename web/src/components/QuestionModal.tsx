import { Check, ChevronLeft, ChevronRight, Copy, ExternalLink, Link2, X } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import { useEffect } from 'react'
import { Link, useSearchParams } from 'react-router'
import { useArchive } from '../data'
import { clock, date, episodeLabel, shortTitle, span, youtubeAt } from '../format'
import { useCopy, useOpenQuestion } from '../hooks'
import CategoryTag from './CategoryTag'
import Highlight from './Highlight'

export default function QuestionModal() {
  const archive = useArchive()
  const { openId, open, close } = useOpenQuestion()
  const [params] = useSearchParams()
  const { copied, copy } = useCopy()

  const question = openId ? archive.questionById.get(openId) : undefined
  const episode = question && archive.episodeById.get(question.video)
  const siblings = question ? archive.questionsByEpisode.get(question.video) ?? [] : []
  const position = question ? siblings.indexOf(question) : -1
  const prev = siblings[position - 1]
  const next = siblings[position + 1]
  const terms = (params.get('s') ?? '').toLowerCase().split(/\s+/).filter((t) => t.length > 1)
  const transcript = question ? archive.transcripts?.[question.id] : undefined

  useEffect(() => {
    if (!question) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') close()
      if (event.key === 'ArrowRight' && next) open(next.id)
      if (event.key === 'ArrowLeft' && prev) open(prev.id)
    }
    document.addEventListener('keydown', onKey)
    document.documentElement.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.documentElement.style.overflow = ''
    }
  }, [question, next, prev, open, close])

  const shareUrl = question ? `${location.origin}${location.pathname}#/?q=${question.id}` : ''

  return (
    <AnimatePresence>
      {question && episode && (
        <motion.div className="fixed inset-0 z-50 flex items-end justify-center md:items-center md:p-6" initial="hidden" animate="shown" exit="hidden">
          <motion.div
            className="absolute inset-0 bg-black/75 backdrop-blur-md"
            variants={{ hidden: { opacity: 0 }, shown: { opacity: 1 } }}
            onClick={close}
          />
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-label={question.question}
            variants={{ hidden: { opacity: 0, y: 80, scale: 0.97 }, shown: { opacity: 1, y: 0, scale: 1 } }}
            transition={{ type: 'spring', stiffness: 320, damping: 32 }}
            className="relative flex max-h-[94dvh] w-full max-w-6xl flex-col overflow-y-auto rounded-t-3xl border border-line bg-panel shadow-2xl shadow-black md:grid md:max-h-[88vh] md:grid-cols-[1.4fr_1fr] md:overflow-hidden md:rounded-3xl"
          >
            <button
              onClick={close}
              aria-label="Close"
              className="absolute right-3 top-3 z-10 grid size-9 place-items-center rounded-full bg-black/70 text-white/80 backdrop-blur transition hover:rotate-90 hover:bg-white hover:text-black"
            >
              <X className="size-5" />
            </button>

            <div className="flex flex-col md:overflow-y-auto">
              <div className="aspect-video w-full shrink-0 bg-black">
                <iframe
                  key={question.id}
                  className="size-full"
                  src={`https://www.youtube-nocookie.com/embed/${question.video}?start=${question.t}&autoplay=1&rel=0&playsinline=1`}
                  title={question.question}
                  allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
                  allowFullScreen
                />
              </div>

              <AnimatePresence mode="wait">
                <motion.div
                  key={question.id}
                  initial={{ opacity: 0, x: 16 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -16 }}
                  transition={{ duration: 0.25 }}
                  className="flex flex-col gap-4 p-5 sm:p-6"
                >
                  <CategoryTag category={question.category} />
                  <h2 className="font-wide text-2xl font-black leading-tight text-balance sm:text-3xl">
                    <Highlight text={question.question} terms={terms} />
                  </h2>
                  <Link
                    to={`/episodes/${episode.id}`}
                    onClick={close}
                    className="group flex items-center gap-3 rounded-xl border border-line bg-white/[0.03] p-3 transition hover:border-mint/40"
                  >
                    <span className="font-wide shrink-0 rounded-lg bg-mint px-2 py-1 text-xs font-black text-black">{episodeLabel(episode)}</span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-semibold group-hover:text-mint">{shortTitle(episode)}</span>
                      <span className="block text-xs text-white/45">
                        {date(episode.published)} · asked at {clock(question.t)} · {span(question.end - question.t)} answer
                      </span>
                    </span>
                  </Link>

                  <div className="flex flex-wrap gap-2">
                    <ActionButton onClick={() => transcript && copy('answer', transcript)} disabled={!transcript} done={copied === 'answer'} icon={Copy} label="Copy answer" />
                    <ActionButton onClick={() => copy('link', shareUrl)} done={copied === 'link'} icon={Link2} label="Copy link" />
                    <a
                      href={youtubeAt(question.video, question.t)}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-2 rounded-xl border border-line px-3.5 py-2 text-sm font-semibold text-white/80 transition hover:border-white/30 hover:text-white"
                    >
                      <ExternalLink className="size-4" /> YouTube
                    </a>
                  </div>

                  <div className="mt-1 flex items-center justify-between gap-2 border-t border-line pt-4 text-sm">
                    <StepButton question={prev?.question} onClick={() => prev && open(prev.id)} direction="prev" />
                    <span className="shrink-0 text-xs text-white/40">
                      {position + 1} of {siblings.length}
                    </span>
                    <StepButton question={next?.question} onClick={() => next && open(next.id)} direction="next" />
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>

            <aside className="flex min-h-0 flex-col border-t border-line bg-black/30 md:border-l md:border-t-0">
              <div className="flex items-center justify-between px-5 pb-3 pt-5 sm:px-6 md:pr-16">
                <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-white/45">What they said</h3>
                <span className="text-[11px] text-white/30">Auto-generated captions</span>
              </div>
              <div className="min-h-0 flex-1 px-5 pb-6 sm:px-6 md:overflow-y-auto">
                {transcript === undefined && archive.transcripts === null ? (
                  <div className="space-y-3">
                    {[90, 75, 85, 60].map((w, i) => (
                      <div key={i} className="h-3 animate-pulse rounded bg-white/10" style={{ width: `${w}%` }} />
                    ))}
                  </div>
                ) : transcript ? (
                  <motion.div key={question.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-3 text-[15px] leading-relaxed text-white/75">
                    {transcript.split('\n').map((turn, i) => (
                      <p key={i} className={i % 2 ? 'pl-3 text-white/60' : ''}>
                        <Highlight text={turn} terms={terms} />
                      </p>
                    ))}
                  </motion.div>
                ) : (
                  <p className="text-sm text-white/45">No captions for this answer yet. Watch it above.</p>
                )}
              </div>
            </aside>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

function ActionButton({ onClick, done, disabled, icon: Icon, label }: {
  onClick: () => void
  done: boolean
  disabled?: boolean
  icon: typeof Copy
  label: string
}) {
  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      disabled={disabled}
      className={`flex items-center gap-2 rounded-xl px-3.5 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-40 ${
        done ? 'bg-mint text-black' : 'border border-line text-white/80 hover:border-white/30 hover:text-white'
      }`}
    >
      <AnimatePresence mode="wait" initial={false}>
        <motion.span key={String(done)} initial={{ scale: 0.4, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.4, opacity: 0 }}>
          {done ? <Check className="size-4" /> : <Icon className="size-4" />}
        </motion.span>
      </AnimatePresence>
      {done ? 'Copied!' : label}
    </motion.button>
  )
}

function StepButton({ question, onClick, direction }: { question?: string; onClick: () => void; direction: 'prev' | 'next' }) {
  const Icon = direction === 'prev' ? ChevronLeft : ChevronRight
  return (
    <button
      onClick={onClick}
      disabled={!question}
      className={`group flex min-w-0 flex-1 items-center gap-1.5 rounded-lg p-1.5 text-white/60 transition hover:text-white disabled:invisible ${direction === 'next' ? 'flex-row-reverse text-right' : ''}`}
    >
      <Icon className="size-4 shrink-0 transition group-hover:scale-125" />
      <span className="truncate text-xs">{question}</span>
    </button>
  )
}
