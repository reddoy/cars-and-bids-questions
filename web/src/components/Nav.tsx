import { BarChart3, Dices, Search, Tv } from 'lucide-react'
import { motion } from 'motion/react'
import { NavLink, useLocation } from 'react-router'

export const LINKS = [
  { to: '/', label: 'Search', icon: Search },
  { to: '/episodes', label: 'Episodes', icon: Tv },
  { to: '/random', label: 'Random', icon: Dices },
  { to: '/stats', label: 'Stats', icon: BarChart3 },
]

function useActive() {
  const { pathname } = useLocation()
  return (to: string) => (to === '/' ? pathname === '/' : pathname.startsWith(to))
}

export function TopNav() {
  const isActive = useActive()
  return (
    <header className="sticky top-0 z-40 border-b border-line bg-ink/70 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <NavLink to="/" className="group flex items-center gap-3">
          <motion.img
            src="./img/logo.jpeg"
            alt=""
            className="size-9 rounded-xl"
            whileHover={{ rotate: -8, scale: 1.08 }}
            transition={{ type: 'spring', stiffness: 400, damping: 15 }}
          />
          <div className="leading-none">
            <div className="font-wide text-[15px] font-black tracking-tight">THIS CAR POD</div>
            <div className="mt-1 text-[11px] font-medium uppercase tracking-[0.2em] text-white/45">Q&amp;A Archive</div>
          </div>
        </NavLink>

        <nav className="hidden items-center gap-1 rounded-full border border-line bg-white/[0.03] p-1 md:flex">
          {LINKS.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className="relative rounded-full px-4 py-2 text-sm font-semibold">
              {isActive(to) && (
                <motion.span
                  layoutId="nav-pill"
                  className="absolute inset-0 rounded-full bg-mint"
                  transition={{ type: 'spring', stiffness: 500, damping: 38 }}
                />
              )}
              <span className={`relative flex items-center gap-2 ${isActive(to) ? 'text-black' : 'text-white/70 hover:text-white'}`}>
                <Icon className="size-4" />
                {label}
              </span>
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}

export function BottomNav() {
  const isActive = useActive()
  return (
    <nav className="fixed inset-x-3 bottom-3 z-40 flex justify-around rounded-2xl border border-line bg-panel/85 p-1.5 pb-[max(0.375rem,env(safe-area-inset-bottom))] shadow-2xl shadow-black/60 backdrop-blur-xl md:hidden">
      {LINKS.map(({ to, label, icon: Icon }) => (
        <NavLink key={to} to={to} className="relative flex flex-1 flex-col items-center gap-1 rounded-xl py-2 text-[11px] font-semibold">
          {isActive(to) && (
            <motion.span
              layoutId="tab-pill"
              className="absolute inset-0 rounded-xl bg-mint/15"
              transition={{ type: 'spring', stiffness: 500, damping: 38 }}
            />
          )}
          <Icon className={`relative size-5 ${isActive(to) ? 'text-mint' : 'text-white/50'}`} />
          <span className={`relative ${isActive(to) ? 'text-mint' : 'text-white/50'}`}>{label}</span>
        </NavLink>
      ))}
    </nav>
  )
}
