import { useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"

interface TriviaTimerProps {
  seconds: number
  running: boolean
  onExpire: () => void
}

export function TriviaTimer({ seconds, running, onExpire }: TriviaTimerProps) {
  const [progress, setProgress] = useState(1)
  const startTime = useRef<number | null>(null)
  const rafId = useRef<number>(0)
  const expired = useRef(false)

  useEffect(() => {
    if (!running) {
      startTime.current = null
      expired.current = false
      setProgress(1)
      return
    }

    expired.current = false
    startTime.current = performance.now()
    const duration = seconds * 1000

    function tick() {
      if (!startTime.current || expired.current) return
      const elapsed = performance.now() - startTime.current
      const remaining = Math.max(0, 1 - elapsed / duration)
      setProgress(remaining)

      if (remaining <= 0 && !expired.current) {
        expired.current = true
        onExpire()
        return
      }
      rafId.current = requestAnimationFrame(tick)
    }

    rafId.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafId.current)
  }, [running, seconds, onExpire])

  const color =
    progress > 0.5
      ? "rgb(34, 197, 94)"
      : progress > 0.25
        ? "rgb(234, 179, 8)"
        : "rgb(239, 68, 68)"

  const timeLeft = Math.ceil(progress * seconds)

  return (
    <div className="flex items-center gap-3">
      <div className="relative h-2 flex-1 overflow-hidden rounded-full bg-muted/30">
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{ backgroundColor: color, width: `${progress * 100}%` }}
          transition={{ duration: 0.05 }}
        />
      </div>
      <span
        className="w-8 text-right font-mono text-xs font-bold tabular-nums"
        style={{ color }}
      >
        {timeLeft}s
      </span>
    </div>
  )
}
