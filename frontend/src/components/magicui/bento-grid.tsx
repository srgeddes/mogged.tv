import type { ComponentPropsWithoutRef, ReactNode } from "react"
import { cn } from "@/lib/utils"

interface BentoGridProps extends ComponentPropsWithoutRef<"div"> {
  children: ReactNode
}

export function BentoGrid({ children, className, ...props }: BentoGridProps) {
  return (
    <div className={cn("grid w-full auto-rows-[22rem] grid-cols-3 gap-4", className)} {...props}>
      {children}
    </div>
  )
}

interface BentoCardProps extends ComponentPropsWithoutRef<"div"> {
  name: string
  description: string
  icon: ReactNode
  className?: string
  background?: ReactNode
}

export function BentoCard({ name, description, icon, className, background, ...props }: BentoCardProps) {
  return (
    <div
      className={cn(
        "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-xl",
        "bg-card border border-border",
        "transform-gpu transition-all duration-300 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5",
        className
      )}
      {...props}
    >
      {background && <div className="pointer-events-none absolute inset-0 opacity-60 transition-opacity duration-300 group-hover:opacity-80">{background}</div>}
      <div className="pointer-events-none z-10 flex transform-gpu flex-col gap-1 p-6 transition-all duration-300">
        <div className="mb-2 text-primary">{icon}</div>
        <h3 className="text-lg font-semibold text-foreground">{name}</h3>
        <p className="max-w-lg text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  )
}
