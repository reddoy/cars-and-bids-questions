import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'

/** The question open in the detail panel lives in the URL (?q=…), so it can be shared. */
export function useOpenQuestion() {
  const [params, setParams] = useSearchParams()
  const open = useCallback(
    (id: string) =>
      setParams((current) => {
        const next = new URLSearchParams(current)
        next.set('q', id)
        return next
      }),
    [setParams],
  )
  const close = useCallback(
    () =>
      setParams((current) => {
        const next = new URLSearchParams(current)
        next.delete('q')
        return next
      }),
    [setParams],
  )
  return { openId: params.get('q'), open, close }
}

export function useCopy(timeout = 1600) {
  const [copied, setCopied] = useState<string | null>(null)
  useEffect(() => {
    if (!copied) return
    const timer = setTimeout(() => setCopied(null), timeout)
    return () => clearTimeout(timer)
  }, [copied, timeout])
  const copy = useCallback(async (key: string, text: string) => {
    await navigator.clipboard.writeText(text)
    setCopied(key)
  }, [])
  return { copied, copy }
}
