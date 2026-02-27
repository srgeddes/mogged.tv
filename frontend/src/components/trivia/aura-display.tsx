import { useEffect, useRef, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { AuroraText } from "@/components/magicui/aurora-text"

interface AuraDisplayProps {
  balance: number
  totalAnswered: number
  accuracy: number
  streak: number
}

interface FloatingText {
  id: number
  amount: number
}

export function AuraDisplay({ balance, totalAnswered, accuracy, streak }: AuraDisplayProps) {
  const [displayBalance, setDisplayBalance] = useState(balance)
  const [floatingTexts, setFloatingTexts] = useState<FloatingText[]>([])
  const prevBalance = useRef(balance)
  const nextId = useRef(0)

  useEffect(() => {
    const diff = balance - prevBalance.current
    if (diff > 0) {
      const id = nextId.current++
      setFloatingTexts((prev) => [...prev, { id, amount: diff }])
      setTimeout(() => {
        setFloatingTexts((prev) => prev.filter((t) => t.id !== id))
      }, 1200)
    }
    prevBalance.current = balance

    // Animate the number counting up
    const start = displayBalance
    const end = balance
    if (start === end) return
    const duration = 400
    const startTime = performance.now()

    function tick(now: number) {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setDisplayBalance(Math.round(start + (end - start) * eased))
      if (progress < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [balance])

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative">
        <AuroraText
          className="font-display text-5xl font-black tracking-tight sm:text-6xl"
          colors={["#003153", "#0066aa", "#ffffff", "#0099dd"]}
          speed={2}
        >
          {displayBalance.toLocaleString()}
        </AuroraText>
        <AnimatePresence>
          {floatingTexts.map((ft) => (
            <motion.span
              key={ft.id}
              initial={{ opacity: 1, y: 0, scale: 1 }}
              animate={{ opacity: 0, y: -40, scale: 1.3 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="pointer-events-none absolute -right-4 -top-2 font-mono text-lg font-bold text-green-400"
            >
              +{ft.amount}
            </motion.span>
          ))}
        </AnimatePresence>
      </div>
      <p className="text-sm text-muted-foreground">
        {totalAnswered > 0 ? (
          <>
            {totalAnswered} answered · {accuracy}% accuracy
            {streak > 0 && (
              <span className="ml-1 text-amber-400"> · {streak} streak</span>
            )}
          </>
        ) : (
          "Answer trivia to earn aura"
        )}
      </p>
    </div>
  )
}
