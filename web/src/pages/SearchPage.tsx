import { ArrowDownWideNarrow, Search, X } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import { useDeferredValue, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigationType, useSearchParams } from 'react-router'
import CountUp from '../components/CountUp'
import QuestionCard from '../components/QuestionCard'
import { CATEGORIES, useArchive, type Category } from '../data'
import { useOpenQuestion } from '../hooks'
import { buildIndex, search, snippet } from '../search'

const PAGE = 48
const EXAMPLES = ["Doug's favorite Porsche", 'best car under $20k', 'Filippo 911', 'manual transmission', 'Carrera GT', 'what would you daily']

export default function SearchPage() {
  const archive = useArchive()
  const { open } = useOpenQuestion()
  const [params, setParams] = useSearchParams()
  const [query, setQuery] = useState(() => params.get('s') ?? '')
  const category = params.get('cat') as Category | null
  const sort = params.get('sort') === 'oldest' ? 'oldest' : 'newest'
  const deferredQuery = useDeferredValue(query.trim())
  const [limit, setLimit] = useState(PAGE)
  const inputRef = useRef<HTMLInputElement>(null)

  const index = useMemo(() => buildIndex(archive), [archive])

  const setParam = (key: string, value: string | null) =>
    setParams(
      (current) => {
        const next = new URLSearchParams(current)
        if (value) next.set(key, value)
        else next.delete(key)
        return next
      },
      { replace: true },
    )

  const results = useMemo(() => {
    const base = deferredQuery
      ? search(index, deferredQuery).map((hit) => ({ question: archive.questionById.get(hit.id)!, hit }))
      : archive.questions.map((question) => ({ question, hit: undefined }))
    const filtered = category ? base.filter((r) => r.question.category === category) : base
    if (!deferredQuery && sort === 'oldest') return [...filtered].reverse()
    return filtered
  }, [deferredQuery, index, archive, category, sort])

  useEffect(() => {
    setLimit(PAGE)
  }, [deferredQuery, category, sort])

  // The box keeps its own state so fast typing never drops letters; a search that arrives
  // through the URL (a shared link, the back button) replaces it.
  const urlQuery = params.get('s') ?? ''
  const navigationType = useNavigationType()
  useEffect(() => {
    if (navigationType !== 'REPLACE') setQuery(urlQuery)
  }, [urlQuery, navigationType])
  useEffect(() => {
    const timer = setTimeout(() => {
      // This page stays mounted while it animates out, and writing then would navigate back here.
      if ((location.hash.slice(1) || '/').split('?')[0] === '/') setParam('s', query.trim() || null)
    }, 300)
    return () => clearTimeout(timer)
  }, [query])
  const changeQuery = setQuery

  const sentinel = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const node = sentinel.current
    if (!node) return
    const observer = new IntersectionObserver(([entry]) => entry.isIntersecting && setLimit((n) => n + PAGE), { rootMargin: '600px' })
    observer.observe(node)
    return () => observer.disconnect()
  }, [results])

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === '/' && document.activeElement !== inputRef.current) {
        event.preventDefault()
        inputRef.current?.focus()
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [])

  const [example, setExample] = useState(0)
  useEffect(() => {
    const timer = setInterval(() => setExample((i) => (i + 1) % EXAMPLES.length), 2800)
    return () => clearInterval(timer)
  }, [])

  const answered = archive.questions.filter((q) => q.hasAnswer).length
  const hours = archive.questions.reduce((sum, q) => sum + (q.end - q.t), 0) / 3600

  return (
    <>
      <section className={`relative text-center transition-[padding] duration-500 ${query ? 'pb-6 pt-8' : 'pb-8 pt-12 sm:pt-20'}`}>
        <AnimatePresence initial={false}>
          {!query && (
            <motion.div
              key="hero"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
              className="overflow-hidden"
            >
              <motion.img
                src="./img/hosts.png"
                alt="The THIS CAR POD hosts"
                className="mx-auto -mb-3 w-56 drop-shadow-[0_20px_40px_rgba(95,211,155,0.25)] sm:w-72"
                initial={{ y: 40, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ type: 'spring', stiffness: 120, damping: 14, delay: 0.1 }}
              />
              <motion.h1
                className="font-wide text-[13vw] font-black uppercase leading-[0.85] tracking-tighter sm:text-8xl"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
              >
                Has it been <span className="relative inline-block text-mint">
                  asked?
                  <motion.span
                    className="absolute -bottom-1 left-0 h-2 rounded-full bg-sun sm:h-3"
                    initial={{ width: 0 }}
                    animate={{ width: '100%' }}
                    transition={{ duration: 0.8, delay: 0.7, ease: [0.16, 1, 0.3, 1] }}
                  />
                </span>
              </motion.h1>
              <motion.p
                className="mx-auto mt-6 max-w-xl text-balance text-white/60 sm:text-lg"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.45 }}
              >
                Every community question from THIS CAR POD, the Cars &amp; Bids podcast. Search the questions and what Doug and the crew
                actually said, then jump straight to the answer.
              </motion.p>
            </motion.div>
          )}
        </AnimatePresence>

        <motion.div
          className="group relative mx-auto mt-8 max-w-2xl"
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, type: 'spring', stiffness: 200, damping: 20 }}
        >
          <div className="absolute -inset-1 rounded-[1.4rem] bg-gradient-to-r from-mint via-sun to-mint opacity-25 blur-lg transition duration-500 group-focus-within:opacity-70" />
          <div className="relative flex items-center gap-3 rounded-2xl border border-white/15 bg-panel px-5 py-4 transition group-focus-within:border-mint/60">
            <Search className="size-5 shrink-0 text-mint" />
            <input
              ref={inputRef}
              value={query}
              onChange={(e) => changeQuery(e.target.value)}
              placeholder={`Try "${EXAMPLES[example]}"`}
              className="min-w-0 flex-1 bg-transparent text-lg outline-none placeholder:text-white/30"
              aria-label="Search questions and answers"
            />
            {query ? (
              <button onClick={() => changeQuery('')} aria-label="Clear search" className="rounded-full p-1 text-white/50 hover:bg-white/10 hover:text-white">
                <X className="size-4" />
              </button>
            ) : (
              <kbd className="hidden rounded-md border border-line px-2 py-0.5 text-xs text-white/40 sm:block">/</kbd>
            )}
          </div>
        </motion.div>

        <motion.div
          className="flex flex-wrap justify-center gap-2 overflow-hidden text-sm"
          initial={{ opacity: 0 }}
          animate={query ? { opacity: 0, height: 0, marginTop: 0 } : { opacity: 1, height: 'auto', marginTop: 24 }}
          transition={{ duration: 0.4, delay: query ? 0 : 0.2 }}
        >
          <Stat value={archive.questions.length} label="questions" />
          <Stat value={archive.episodes.length} label="episodes" />
          <Stat value={answered} label="answers transcribed" />
          <Stat value={hours} label="hours of Q&A" format={(n) => n.toFixed(1)} />
        </motion.div>
      </section>

      <div className="sticky top-16 z-30 -mx-4 mb-6 border-b border-line bg-ink/80 px-4 py-3 backdrop-blur-xl sm:-mx-6 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="no-scrollbar -my-1 flex flex-1 gap-2 overflow-x-auto py-1">
            <Chip active={!category} onClick={() => setParam('cat', null)} label="All" color="#ffffff" />
            {CATEGORIES.map((c) => (
              <Chip key={c.name} active={category === c.name} onClick={() => setParam('cat', category === c.name ? null : c.name)} label={c.label} color={c.color} icon={c.icon} />
            ))}
          </div>
          {!deferredQuery && (
            <button
              onClick={() => setParam('sort', sort === 'newest' ? 'oldest' : null)}
              className="flex shrink-0 items-center gap-1.5 rounded-full border border-line px-3 py-1.5 text-xs font-semibold text-white/70 hover:text-white"
            >
              <ArrowDownWideNarrow className={`size-3.5 transition ${sort === 'oldest' ? 'rotate-180' : ''}`} />
              {sort === 'newest' ? 'Newest' : 'Oldest'}
            </button>
          )}
        </div>
      </div>

      <div className="mb-4 flex items-baseline justify-between text-sm text-white/50">
        <motion.span key={`${results.length}-${deferredQuery}`} initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }}>
          {deferredQuery ? (
            <>
              <span className="font-bold text-white">{results.length}</span> {results.length === 1 ? 'match' : 'matches'} for “{deferredQuery}”
            </>
          ) : (
            <>
              <span className="font-bold text-white">{results.length}</span> questions
            </>
          )}
        </motion.span>
        {deferredQuery && <span className="text-xs">{archive.transcripts ? 'Searching questions and answers' : 'Loading answers…'}</span>}
      </div>

      {results.length ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <AnimatePresence mode="popLayout">
            {results.slice(0, limit).map(({ question, hit }, i) => (
              <QuestionCard
                key={question.id}
                index={i}
                question={question}
                episode={archive.episodeById.get(question.video)!}
                onOpen={open}
                terms={hit?.terms}
                answerSnippet={hit?.inAnswer && !hit.inQuestion ? snippet(archive.transcripts?.[question.id] ?? '', hit.terms) : null}
              />
            ))}
          </AnimatePresence>
        </div>
      ) : (
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="rounded-3xl border border-dashed border-white/15 px-6 py-16 text-center">
          <div className="font-wide text-3xl font-black">Nobody's asked that yet.</div>
          <p className="mx-auto mt-3 max-w-md text-white/55">That means it could be your question on next week's pod. Ask it in the comments of the latest episode.</p>
          <a
            href="https://www.youtube.com/playlist?list=PLRsapyZqDs1oR-egCLXRK-qmdPIZf1y5-"
            target="_blank"
            rel="noreferrer"
            className="mt-6 inline-block rounded-full bg-mint px-5 py-2.5 text-sm font-bold text-black transition hover:scale-105"
          >
            Go to the latest episode
          </a>
        </motion.div>
      )}
      {limit < results.length && <div ref={sentinel} className="h-px" />}
    </>
  )
}

function Stat({ value, label, format }: { value: number; label: string; format?: (n: number) => string }) {
  return (
    <span className="rounded-full border border-line bg-white/[0.03] px-3.5 py-1.5 text-white/55">
      <span className="font-wide font-black text-sun">
        <CountUp value={value} format={format} />
      </span>{' '}
      {label}
    </span>
  )
}

function Chip({ active, onClick, label, color, icon: Icon }: {
  active: boolean
  onClick: () => void
  label: string
  color: string
  icon?: (typeof CATEGORIES)[number]['icon']
}) {
  return (
    <motion.button
      whileTap={{ scale: 0.92 }}
      onClick={onClick}
      className="relative flex shrink-0 items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-xs font-semibold transition-colors"
      style={{ borderColor: active ? color : 'rgb(255 255 255 / 0.1)', color: active ? '#000' : 'rgb(255 255 255 / 0.7)' }}
    >
      {active && <motion.span layoutId="chip-bg" className="absolute inset-0 rounded-full" style={{ backgroundColor: color }} transition={{ type: 'spring', stiffness: 500, damping: 35 }} />}
      {Icon && <Icon className="relative size-3.5" style={{ color: active ? '#000' : color }} />}
      <span className="relative">{label}</span>
    </motion.button>
  )
}
