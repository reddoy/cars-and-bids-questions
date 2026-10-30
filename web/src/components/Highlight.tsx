import { termPattern } from '../search'

export default function Highlight({ text, terms }: { text: string; terms?: string[] }) {
  const pattern = terms?.length ? termPattern(terms) : null
  if (!pattern) return <>{text}</>
  return (
    <>
      {text.split(pattern).map((part, i) => (i % 2 ? <mark key={i}>{part}</mark> : part))}
    </>
  )
}
