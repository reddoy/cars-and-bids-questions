import { Play } from 'lucide-react'
import { motion } from 'motion/react'
import { forwardRef } from 'react'
import type { Episode, Question } from '../data'
import { clock, episodeLabel, shortTitle, span, thumbnail } from '../format'
import CategoryTag from './CategoryTag'
import Highlight from './Highlight'

type Props = {
  question: Question
  episode: Episode
  onOpen: (id: string) => void
  terms?: string[]
  answerSnippet?: string | null
  index?: number
}

const QuestionCard = forwardRef<HTMLButtonElement, Props>(function QuestionCard(
  { question, episode, onOpen, terms, answerSnippet, index = 0 },
  ref,
) {
  return (
    <motion.button
      ref={ref}
      layout
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.96, transition: { duration: 0.15 } }}
      transition={{ duration: 0.4, delay: Math.min(index % 48, 14) * 0.03, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -4 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onOpen(question.id)}
      className="group relative flex flex-col overflow-hidden rounded-2xl border border-line bg-panel text-left shadow-lg shadow-black/30 transition-colors hover:border-mint/40"
    >
      <div className="relative aspect-[16/7] overflow-hidden">
        <img
          src={thumbnail(question.video)}
          alt=""
          loading="lazy"
          className="size-full object-cover opacity-80 transition duration-700 group-hover:scale-110 group-hover:opacity-100"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-panel via-panel/40 to-transparent" />
        <span className="font-wide absolute left-3 top-3 rounded-md bg-black/70 px-2 py-1 text-[11px] font-black tracking-wide backdrop-blur">
          {episodeLabel(episode)}
        </span>
        <span className="absolute bottom-2 right-3 flex items-center gap-1.5 rounded-full bg-mint px-2.5 py-1 text-xs font-bold text-black shadow-lg shadow-mint/30 transition-transform group-hover:scale-110">
          <Play className="size-3 fill-current" />
          {clock(question.t)}
        </span>
      </div>

      <div className="flex flex-1 flex-col gap-3 p-4 pt-2">
        <CategoryTag category={question.category} />
        <h3 className="font-wide text-[17px] font-extrabold leading-snug text-balance">
          <Highlight text={question.question} terms={terms} />
        </h3>
        {answerSnippet && (
          <p className="line-clamp-3 border-l-2 border-sun/50 pl-3 text-sm leading-relaxed text-white/60">
            <Highlight text={answerSnippet} terms={terms} />
          </p>
        )}
        <div className="mt-auto flex items-center justify-between gap-3 pt-1 text-xs text-white/40">
          <span className="truncate">{shortTitle(episode)}</span>
          <span className="shrink-0">{span(question.end - question.t)}</span>
        </div>
      </div>
    </motion.button>
  )
})

export default QuestionCard
