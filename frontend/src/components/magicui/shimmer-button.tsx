import type { CSSProperties, ComponentPropsWithoutRef } from "react"
import { cn } from "@/lib/utils"

interface ShimmerButtonProps extends ComponentPropsWithoutRef<"button"> {
  shimmerColor?: string
  shimmerSize?: string
  borderRadius?: string
  shimmerDuration?: string
  background?: string
  className?: string
}

export function ShimmerButton({
  shimmerColor = "#003153",
  shimmerSize = "0.1em",
  shimmerDuration = "2s",
  borderRadius = "100px",
  background = "rgba(0, 49, 83, 0.15)",
  className,
  children,
  ...props
}: ShimmerButtonProps) {
  return (
    <button
      style={
        {
          "--shimmer-color": shimmerColor,
          "--radius": borderRadius,
          "--speed": shimmerDuration,
          "--cut": shimmerSize,
          "--bg": background,
        } as CSSProperties
      }
      className={cn(
        "group relative z-0 flex cursor-pointer items-center justify-center overflow-hidden whitespace-nowrap border border-white/10 px-6 py-3 [background:var(--bg)] [border-radius:var(--radius)]",
        "transform-gpu transition-transform duration-300 ease-in-out active:translate-y-px",
        className
      )}
      {...props}
    >
      <div className="absolute inset-0 overflow-hidden [border-radius:var(--radius)]">
        <span className="absolute inset-[-100%] animate-shimmer [background:linear-gradient(90deg,transparent,var(--shimmer-color),transparent)] [background-size:200%_100%] opacity-30" />
      </div>
      <span className="relative z-10 flex items-center gap-2 text-sm font-semibold text-white/90">{children}</span>
    </button>
  )
}
