import { useState, useEffect, type ComponentPropsWithoutRef, type ReactNode } from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface HoverBorderGradientProps extends ComponentPropsWithoutRef<"button"> {
  children: ReactNode
  containerClassName?: string
  className?: string
  as?: "button" | "a" | "div"
  duration?: number
  clockwise?: boolean
}

export function HoverBorderGradient({
  children,
  containerClassName,
  className,
  as: Tag = "button",
  duration = 1,
  clockwise = true,
  ...props
}: HoverBorderGradientProps) {
  const [hovered, setHovered] = useState(false)
  const [direction, setDirection] = useState<string>("TOP")

  const rotateDirection = (currentDirection: string) => {
    const directions = ["TOP", "LEFT", "BOTTOM", "RIGHT"]
    const currentIndex = directions.indexOf(currentDirection)
    const nextIndex = clockwise
      ? (currentIndex - 1 + directions.length) % directions.length
      : (currentIndex + 1) % directions.length
    return directions[nextIndex]
  }

  const movingMap: Record<string, string> = {
    TOP: "radial-gradient(20.7% 50% at 50% 0%, hsl(205, 100%, 25%) 0%, rgba(0, 49, 83, 0) 100%)",
    LEFT: "radial-gradient(16.6% 43.1% at 0% 50%, hsl(205, 100%, 25%) 0%, rgba(0, 49, 83, 0) 100%)",
    BOTTOM: "radial-gradient(20.7% 50% at 50% 100%, hsl(205, 100%, 25%) 0%, rgba(0, 49, 83, 0) 100%)",
    RIGHT: "radial-gradient(16.6% 43.1% at 100% 50%, hsl(205, 100%, 25%) 0%, rgba(0, 49, 83, 0) 100%)",
  }

  const highlight = "radial-gradient(75% 181.16% at 50% 50%, hsl(205, 80%, 30%) 0%, rgba(0, 49, 83, 0) 100%)"

  useEffect(() => {
    if (!hovered) {
      const interval = setInterval(() => {
        setDirection((prevState) => rotateDirection(prevState))
      }, duration * 1000)
      return () => clearInterval(interval)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hovered])

  return (
    <Tag
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className={cn(
        "relative flex h-min w-fit cursor-pointer flex-col items-center justify-center overflow-visible rounded-full border bg-card p-px transition duration-500",
        containerClassName
      )}
      {...(props as Record<string, unknown>)}
    >
      <div className={cn("z-10 w-auto rounded-[inherit] bg-card px-4 py-2 text-sm text-foreground", className)}>
        {children}
      </div>
      <motion.div
        className="absolute inset-0 z-0 flex-none overflow-hidden rounded-[inherit]"
        style={{
          filter: "blur(2px)",
          width: "100%",
          height: "100%",
        }}
        initial={{ background: movingMap[direction] }}
        animate={{
          background: hovered ? [movingMap[direction], highlight] : movingMap[direction],
        }}
        transition={{ ease: "linear", duration }}
      />
      <div className="absolute inset-[2px] z-[1] flex-none rounded-[inherit] bg-card" />
    </Tag>
  )
}
