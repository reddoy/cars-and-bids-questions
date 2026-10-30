import { motion } from 'motion/react'
import { useMemo, useState, type ReactNode } from 'react'
import { useNavigate } from 'react-router'
import CountUp from '../components/CountUp'
import { CATEGORIES, useArchive, type Question } from '../data'
import { episodeLabel, shortTitle, span } from '../format'
import { useOpenQuestion } from '../hooks'

const BRANDS: [string, RegExp][] = [
  ['Porsche', /porsche|911|cayenne|cayman|boxster|carrera|gt3|taycan|macan/],
  ['Ferrari', /ferrari|f40|enzo/],
  ['BMW', /\bbmw\b|\bm[2-8]\b|e30|e46/],
  ['Tesla', /tesla|cybertruck|model [3sxyq]/],
  ['Toyota', /toyota|supra|land cruiser|4runner|tacoma|sequoia|gr86/],
  ['Mercedes', /mercedes|\bamg\b|g.?wagon|\bbenz\b|c63/],
  ['Lamborghini', /lambo|urus|countach/],
  ['Ford', /\bford\b|mustang|bronco|raptor|\bgt40\b/],
  ['Honda', /honda|civic|\bnsx\b|prelude|s2000/],
  ['Audi', /\baudi\b|\brs\s?\d|\bquattro\b/],
  ['Chevrolet', /chev|corvette|camaro/],
  ['McLaren', /mclaren/],
  ['Rivian', /rivian/],
  ['Mazda', /mazda|miata/],
]

export default function StatsPage() {
  const archive = useArchive()
  const { open } = useOpenQuestion()
  const navigate = useNavigate()
  const { questions, episodes } = archive

  const stats = useMemo(() => {
    const length = (q: Question) => q.end - q.t
    const answerTime = questions.reduce((sum, q) => sum + length(q), 0)
    // The pipeline caps answers it can't find an end for at 20 minutes, so those can't hold records.
    const byLength = questions.filter((q) => length(q) < 20 * 60).sort((a, b) => length(b) - length(a))
    const chronological = [...episodes].reverse()
    const busiest = [...episodes].sort((a, b) => b.questions - a.questions)[0]
    const longestText = [...questions].sort((a, b) => b.question.length - a.question.length)[0]
    const categories = CATEGORIES.map((c) => ({ ...c, count: questions.filter((q) => q.category === c.name).length })).sort((a, b) => b.count - a.count)
    const brands = BRANDS.map(([name, pattern]) => ({ name, count: questions.filter((q) => pattern.test(q.question.toLowerCase())).length }))
      .filter((b) => b.count)
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)
    return { answerTime, longest: byLength[0], shortest: byLength.at(-1)!, chronological, busiest, longestText, categories, brands }
  }, [questions, episodes])

  const maxPerEpisode = Math.max(...episodes.map((e) => e.questions))
  const [hoverBar, setHoverBar] = useState<number | null>(null)
  const hovered = hoverBar === null ? null : stats.chronological[hoverBar]

  return (
    <>
      <header className="pb-10 pt-12">
        <p className="text-xs font-bold uppercase tracking-[0.25em] text-mint">By the numbers</p>
        <h1 className="font-wide mt-2 text-5xl font-black uppercase tracking-tight sm:text-6xl">Pod stats</h1>
      </header>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <BigStat label="Questions answered" value={questions.length} />
        <BigStat label="Episodes" value={episodes.length} />
        <BigStat label="Hours of answers" value={stats.answerTime / 3600} format={(n) => n.toFixed(1)} />
        <BigStat label="Average answer" value={stats.answerTime / questions.length} format={(n) => span(n)} />
      </div>

      <Card title="Questions per episode" aside={hovered ? `${episodeLabel(hovered)} · ${hovered.questions} questions` : 'Hover a bar'}>
        <div className="flex h-48 items-end gap-[2px]" onMouseLeave={() => setHoverBar(null)}>
          {stats.chronological.map((e, i) => (
            <motion.button
              key={e.id}
              aria-label={`${episodeLabel(e)}: ${e.questions} questions`}
              onMouseEnter={() => setHoverBar(i)}
              onClick={() => navigate(`/episodes/${e.id}`)}
              className={`flex-1 origin-bottom rounded-t-sm transition-colors ${hoverBar === i ? 'bg-sun' : 'bg-mint/70 hover:bg-mint'}`}
              style={{ height: `${Math.max(2, (e.questions / maxPerEpisode) * 100)}%` }}
              initial={{ scaleY: 0 }}
              whileInView={{ scaleY: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.006, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            />
          ))}
        </div>
        <div className="mt-2 flex justify-between text-[11px] text-white/35">
          <span>{episodeLabel(stats.chronological[0])}</span>
          <span>{episodeLabel(stats.chronological.at(-1)!)}</span>
        </div>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="What people ask about">
          <Bars rows={stats.categories.map((c) => ({ label: c.label, count: c.count, color: c.color }))} total={questions.length} />
        </Card>
        <Card title="Most asked-about brands">
          <Bars rows={stats.brands.map((b, i) => ({ label: b.name, count: b.count, color: i === 0 ? '#ffe14d' : '#7cc4ff' }))} total={stats.brands[0]?.count ?? 1} relative />
        </Card>
      </div>

      <h2 className="font-wide mb-4 mt-12 text-2xl font-black uppercase">Record holders</h2>
      <div className="grid gap-3 sm:grid-cols-2">
        <Record label="Longest answer" value={span(stats.longest.end - stats.longest.t)} detail={stats.longest.question} onClick={() => open(stats.longest.id)} />
        <Record label="Quickest answer" value={span(stats.shortest.end - stats.shortest.t)} detail={stats.shortest.question} onClick={() => open(stats.shortest.id)} />
        <Record
          label="Most questions in one episode"
          value={`${stats.busiest.questions} questions`}
          detail={`${episodeLabel(stats.busiest)} · ${shortTitle(stats.busiest)}`}
          onClick={() => navigate(`/episodes/${stats.busiest.id}`)}
        />
        <Record label="Wordiest question" value={`${stats.longestText.question.length} characters`} detail={stats.longestText.question} onClick={() => open(stats.longestText.id)} />
      </div>
    </>
  )
}

function BigStat({ label, value, format }: { label: string; value: number; format?: (n: number) => string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="rounded-2xl border border-line bg-panel p-5"
    >
      <div className="font-wide text-3xl font-black text-sun sm:text-4xl">
        <CountUp value={value} format={format} />
      </div>
      <div className="mt-1 text-xs font-semibold uppercase tracking-wider text-white/45">{label}</div>
    </motion.div>
  )
}

function Card({ title, aside, children }: { title: string; aside?: string; children: ReactNode }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="mt-4 rounded-3xl border border-line bg-panel p-5 sm:p-6"
    >
      <div className="mb-5 flex items-baseline justify-between gap-4">
        <h2 className="text-sm font-bold uppercase tracking-[0.18em] text-white/60">{title}</h2>
        {aside && <span className="truncate text-xs text-white/40">{aside}</span>}
      </div>
      {children}
    </motion.section>
  )
}

function Bars({ rows, total, relative }: { rows: { label: string; count: number; color: string }[]; total: number; relative?: boolean }) {
  return (
    <div className="space-y-3">
      {rows.map((row, i) => (
        <div key={row.label}>
          <div className="mb-1 flex justify-between text-sm">
            <span className="font-semibold">{row.label}</span>
            <span className="text-white/45">{relative ? row.count : `${Math.round((row.count / total) * 100)}%`}</span>
          </div>
          <div className="h-2.5 overflow-hidden rounded-full bg-white/5">
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: row.color }}
              initial={{ width: 0 }}
              whileInView={{ width: `${(row.count / total) * 100}%` }}
              viewport={{ once: true }}
              transition={{ duration: 0.9, delay: i * 0.07, ease: [0.16, 1, 0.3, 1] }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

function Record({ label, value, detail, onClick }: { label: string; value: string; detail: string; onClick: () => void }) {
  return (
    <motion.button
      whileHover={{ y: -3 }}
      onClick={onClick}
      className="rounded-2xl border border-line bg-panel p-5 text-left transition hover:border-mint/40"
    >
      <div className="text-xs font-semibold uppercase tracking-wider text-white/45">{label}</div>
      <div className="font-wide mt-2 text-2xl font-black text-mint">{value}</div>
      <div className="mt-2 line-clamp-2 text-sm text-white/65">{detail}</div>
    </motion.button>
  )
}
