import { motion } from "framer-motion"

const EMOJIS = ["✨", "🔥", "💎", "⚡", "🎯"]

interface CorrectAnimationProps {
  show: boolean
}

export function CorrectAnimation({ show }: CorrectAnimationProps) {
  if (!show) return null

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {EMOJIS.map((emoji, i) => (
        <motion.span
          key={i}
          initial={{
            opacity: 1,
            scale: 0,
            x: `${20 + i * 15}%`,
            y: "60%",
          }}
          animate={{
            opacity: [1, 1, 0],
            scale: [0, 1.4, 0.8],
            y: [`60%`, `${10 + i * 8}%`],
            x: `${15 + i * 18}%`,
          }}
          transition={{
            duration: 0.9,
            delay: i * 0.06,
            ease: "easeOut",
          }}
          className="absolute text-2xl"
        >
          {emoji}
        </motion.span>
      ))}
    </div>
  )
}
