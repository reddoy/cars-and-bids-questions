import { AnimatePresence, motion } from 'motion/react'
import { useEffect, type ReactNode } from 'react'
import { Route, Routes, useLocation } from 'react-router'
import Background from './components/Background'
import { BottomNav, TopNav } from './components/Nav'
import QuestionModal from './components/QuestionModal'
import { ArchiveContext, useArchiveLoader } from './data'
import EpisodePage from './pages/EpisodePage'
import EpisodesPage from './pages/EpisodesPage'
import RandomPage from './pages/RandomPage'
import SearchPage from './pages/SearchPage'
import StatsPage from './pages/StatsPage'

export default function App() {
  const { archive, error } = useArchiveLoader()
  const location = useLocation()

  useEffect(() => {
    window.scrollTo({ top: 0 })
  }, [location.pathname])

  return (
    <div className="grain relative min-h-dvh">
      <Background />
      <TopNav />
      {error ? (
        <p className="mx-auto mt-24 max-w-md text-center text-white/60">{error}. Refresh to try again.</p>
      ) : !archive ? (
        <Loading />
      ) : (
        <ArchiveContext.Provider value={archive}>
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              <Route path="/" element={<Page><SearchPage /></Page>} />
              <Route path="/episodes" element={<Page><EpisodesPage /></Page>} />
              <Route path="/episodes/:id" element={<Page><EpisodePage /></Page>} />
              <Route path="/random" element={<Page><RandomPage /></Page>} />
              <Route path="/stats" element={<Page><StatsPage /></Page>} />
              <Route path="*" element={<Page><SearchPage /></Page>} />
            </Routes>
          </AnimatePresence>
          <QuestionModal />
        </ArchiveContext.Provider>
      )}
      <footer className="mx-auto max-w-6xl px-6 pb-32 pt-16 text-center text-xs text-white/30 md:pb-12">
        A fan project, not affiliated with Cars &amp; Bids. Questions come from each episode's description, and answers from YouTube's
        auto-generated captions. ·{' '}
        <a className="underline-offset-2 hover:text-white/60 hover:underline" href="https://github.com/reddoy/cars-and-bids-questions">
          Source
        </a>
      </footer>
      <BottomNav />
    </div>
  )
}

function Page({ children }: { children: ReactNode }) {
  return (
    <motion.main
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="mx-auto max-w-6xl px-4 sm:px-6"
    >
      {children}
    </motion.main>
  )
}

function Loading() {
  return (
    <div className="grid min-h-[70dvh] place-items-center">
      <motion.img
        src="./img/logo.jpeg"
        alt="Loading"
        className="size-16 rounded-2xl"
        animate={{ rotate: [0, -10, 10, 0], scale: [1, 1.1, 1] }}
        transition={{ duration: 1, repeat: Infinity }}
      />
    </div>
  )
}
