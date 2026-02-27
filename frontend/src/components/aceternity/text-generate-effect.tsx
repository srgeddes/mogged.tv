import { useEffect } from "react"
import { motion, stagger, useAnimate } from "framer-motion"
import { cn } from "@/lib/utils"

interface TextGenerateEffectProps {
  words: string
  className?: string
  filter?: boolean
  duration?: number
}

export function TextGenerateEffect({
  words,
  className,
  filter = true,
  duration = 0.5,
}: TextGenerateEffectProps) {
  const [scope, animate] = useAnimate()
  const wordsArray = words.split(" ")

  useEffect(() => {
    animate(
      "span",
      {
        opacity: 1,
        filter: filter ? "blur(0px)" : "none",
      },
      {
        duration,
        delay: stagger(0.08),
      }
    )
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scope])

  return (
    <div className={cn("font-bold", className)}>
      <div className="mt-4">
        <div ref={scope} className="leading-snug tracking-tight">
          {wordsArray.map((word, idx) => (
            <motion.span
              key={word + idx}
              className="opacity-0"
              style={{
                filter: filter ? "blur(10px)" : "none",
              }}
            >
              {word}{" "}
            </motion.span>
          ))}
        </div>
      </div>
    </div>
  )
}
