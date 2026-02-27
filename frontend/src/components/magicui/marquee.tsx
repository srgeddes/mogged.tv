import type { ComponentPropsWithoutRef } from "react"
import { cn } from "@/lib/utils"

interface MarqueeProps extends ComponentPropsWithoutRef<"div"> {
  reverse?: boolean
  pauseOnHover?: boolean
  vertical?: boolean
  repeat?: number
  className?: string
}

export function Marquee({
  className,
  reverse = false,
  pauseOnHover = false,
  vertical = false,
  repeat = 4,
  children,
  ...props
}: MarqueeProps) {
  return (
    <div
      {...props}
      className={cn(
        "group flex overflow-hidden p-2 [--duration:40s] [--gap:1rem] [gap:var(--gap)]",
        vertical ? "flex-col" : "flex-row",
        className
      )}
    >
      {Array.from({ length: repeat }).map((_, i) => (
        <div
          key={i}
          className={cn("flex shrink-0 justify-around [gap:var(--gap)]", vertical ? "flex-col" : "flex-row", vertical ? "animate-marquee-vertical" : "animate-marquee", pauseOnHover && "group-hover:[animation-play-state:paused]", reverse && "[animation-direction:reverse]")}
        >
          {children}
        </div>
      ))}
    </div>
  )
}
