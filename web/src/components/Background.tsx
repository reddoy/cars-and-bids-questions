import { motion } from 'motion/react'

export default function Background() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="road-grid absolute inset-0" />
      <motion.div
        className="absolute -top-48 left-[calc(50%-19rem)] h-[38rem] w-[38rem] rounded-full bg-mint/20 blur-[140px]"
        animate={{ x: [-80, 80, -80], y: [0, 40, 0] }}
        transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute -right-40 top-1/3 h-[28rem] w-[28rem] rounded-full bg-sun/10 blur-[140px]"
        animate={{ y: [0, -60, 0] }}
        transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
      />
    </div>
  )
}
