import { Dices, Play } from 'lucide-react'
import { animate, AnimatePresence, motion, useMotionValue } from 'motion/react'
import { useCallback, useEffect, useState } from 'react'
import CategoryTag from '../components/CategoryTag'
import { CATEGORIES, useArchive, type Category, type Question } from '../data'
import { clock, episodeLabel, shortTitle } from '../format'
import { useOpenQuestion } from '../hooks'

const ROW = 88
const REEL = 28

const pick = <T,>(items: T[]) => items[Math.floor(Math.random() * items.length)]

export default function RandomPage() {
  const archive = useArchive()
  const { open } = useOpenQuestion()
  const [category, setCategory] = useState<Category | null>(null)
  const [reel, setReel] = useState<Question[]>(() => [pick(archive.questions)])
  const [spinning, setSpinning] = useState(false)
  const [landed, setLanded] = useState<Question | null>(null)
  const y = useMotionValue(0)

  const spin = useCallback(() => {
    if (spinning) return
    const pool = category ? archive.questions.filter((q) => q.category === category) : archive.questions
    const nextReel = [reel[reel.length - 1], ...Array.from({ length: REEL }, () => pick(pool))]
    setReel(nextReel)
    setLanded(null)
    setSpinning(true)
    y.set(0)
    animate(y, -(nextReel.length - 1) * ROW, {
      duration: 2.6,
      ease: [0.12, 0.75, 0.18, 1],
      onComplete: () => {
        setSpinning(false)
        setLanded(nextReel[nextReel.length - 1])
      },
    })
  }, [spinning, category, archive.questions, reel, y])

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.code === 'Space' && !(event.target instanceof HTMLInputElement)) {
        event.preventDefault()
        spin()
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [spin])

  const episode = landed && archive.episodeById.get(landed.video)

  return (
    <section className="mx-auto max-w-3xl pb-8 pt-12 text-center">
      <p className="text-xs font-bold uppercase tracking-[0.25em] text-mint">Feeling lucky?</p>
      <h1 className="font-wide mt-2 text-5xl font-black uppercase tracking-tight sm:text-7xl">
        Spin the <span className="text-sun">pod</span>
      </h1>
      <p className="mt-3 text-white/50">Land on a random question and watch the answer. Press space to spin.</p>

      <div className="no-scrollbar -mx-4 mt-8 overflow-x-auto px-4 pb-1">
        <div className="mx-auto flex w-max gap-2">
        {[null, ...CATEGORIES.map((c) => c.name)].map((name) => {
          const info = name ? CATEGORIES.find((c) => c.name === name)! : null
          const active = category === name
          return (
            <button
              key={name ?? 'all'}
              onClick={() => setCategory(name)}
              className="shrink-0 rounded-full border px-3.5 py-1.5 text-xs font-semibold transition"
              style={{ borderColor: active ? (info?.color ?? '#fff') : 'rgb(255 255 255 / 0.1)', backgroundColor: active ? (info?.color ?? '#fff') : 'transparent', color: active ? '#000' : 'rgb(255 255 255 / 0.7)' }}
            >
              {info?.label ?? 'Anything'}
            </button>
          )
        })}
        </div>
      </div>

      <div className="relative mx-auto mt-8 overflow-hidden rounded-3xl border border-white/15 bg-panel shadow-2xl shadow-mint/10" style={{ height: ROW * 3 }}>
        <div className="pointer-events-none absolute inset-x-0 top-0 z-10 h-24 bg-gradient-to-b from-panel to-transparent" />
        <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10 h-24 bg-gradient-to-t from-panel to-transparent" />
        <div className="pointer-events-none absolute inset-x-3 z-0 rounded-2xl border-2 border-mint/60 bg-mint/5" style={{ top: ROW, height: ROW }} />
        <motion.div style={{ y, paddingTop: ROW }}>
          {reel.map((q, i) => (
            <div key={`${q.id}-${i}`} className="flex items-center justify-center px-8" style={{ height: ROW }}>
              <span className={`font-wide line-clamp-2 text-lg font-extrabold leading-tight sm:text-2xl ${spinning ? 'blur-[1px]' : ''}`}>{q.question}</span>
            </div>
          ))}
        </motion.div>
      </div>

      <motion.button
        onClick={spin}
        disabled={spinning}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.94 }}
        className="font-wide mt-8 inline-flex items-center gap-3 rounded-full bg-mint px-8 py-4 text-lg font-black uppercase text-black shadow-xl shadow-mint/30 disabled:opacity-60"
      >
        <motion.span animate={spinning ? { rotate: 360 } : { rotate: 0 }} transition={spinning ? { repeat: Infinity, duration: 0.5, ease: 'linear' } : {}}>
          <Dices className="size-6" />
        </motion.span>
        {spinning ? 'Spinning…' : landed ? 'Spin again' : 'Spin'}
      </motion.button>

      <AnimatePresence>
        {landed && episode && (
          <motion.div
            key={landed.id}
            initial={{ opacity: 0, y: 30, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ type: 'spring', stiffness: 260, damping: 22 }}
            className="mx-auto mt-10 flex max-w-xl flex-col items-center gap-4 rounded-3xl border border-line bg-white/[0.03] p-6"
          >
            <CategoryTag category={landed.category} />
            <p className="text-sm text-white/55">
              <span className="font-wide font-black text-white">{episodeLabel(episode)}</span> · {shortTitle(episode)} · {clock(landed.t)}
            </p>
            <button onClick={() => open(landed.id)} className="inline-flex items-center gap-2 rounded-full bg-white px-5 py-2.5 text-sm font-bold text-black transition hover:scale-105 hover:bg-sun">
              <Play className="size-4 fill-current" /> Watch the answer
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  )
}
