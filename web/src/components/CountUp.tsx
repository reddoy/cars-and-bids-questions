import { animate, useInView } from 'motion/react'
import { useEffect, useRef } from 'react'

const commas = (n: number) => Math.round(n).toLocaleString()

export default function CountUp({ value, duration = 1.4, format = commas }: {
  value: number
  duration?: number
  format?: (n: number) => string
}) {
  const ref = useRef<HTMLSpanElement>(null)
  const formatRef = useRef(format)
  formatRef.current = format
  const inView = useInView(ref, { once: true })

  useEffect(() => {
    if (!inView || !ref.current) return
    const node = ref.current
    const controls = animate(0, value, {
      duration,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (n) => (node.textContent = formatRef.current(n)),
    })
    return () => controls.stop()
  }, [inView, value, duration])

  return <span ref={ref}>{format(0)}</span>
}
