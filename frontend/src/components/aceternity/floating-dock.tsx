import { cn } from "@/lib/utils"
import {
  AnimatePresence,
  MotionValue,
  motion,
  useMotionValue,
  useSpring,
  useTransform,
} from "framer-motion"
import { useRef, useState, type ReactNode } from "react"

export interface FloatingDockItem {
  title: string
  icon: ReactNode
  href: string
  active?: boolean
}

interface FloatingDockProps {
  items: FloatingDockItem[]
  className?: string
  onNavigate?: (href: string) => void
}

export function FloatingDock({ items, className, onNavigate }: FloatingDockProps) {
  const mouseX = useMotionValue(Infinity)

  return (
    <motion.div
      onMouseMove={(e) => mouseX.set(e.pageX)}
      onMouseLeave={() => mouseX.set(Infinity)}
      className={cn(
        "mx-auto flex h-14 items-end gap-3 rounded-2xl border border-border/40 bg-card/80 px-4 pb-2.5 backdrop-blur-xl",
        className,
      )}
    >
      {items.map((item) => (
        <DockIcon
          key={item.title}
          mouseX={mouseX}
          item={item}
          onNavigate={onNavigate}
        />
      ))}
    </motion.div>
  )
}

function DockIcon({
  mouseX,
  item,
  onNavigate,
}: {
  mouseX: MotionValue
  item: FloatingDockItem
  onNavigate?: (href: string) => void
}) {
  const ref = useRef<HTMLDivElement>(null)
  const [hovered, setHovered] = useState(false)

  const distance = useTransform(mouseX, (val) => {
    const bounds = ref.current?.getBoundingClientRect() ?? { x: 0, width: 0 }
    return val - bounds.x - bounds.width / 2
  })

  const widthTransform = useTransform(distance, [-150, 0, 150], [36, 56, 36])
  const heightTransform = useTransform(distance, [-150, 0, 150], [36, 56, 36])
  const iconSizeTransform = useTransform(distance, [-150, 0, 150], [18, 28, 18])

  const width = useSpring(widthTransform, { mass: 0.1, stiffness: 200, damping: 15 })
  const height = useSpring(heightTransform, { mass: 0.1, stiffness: 200, damping: 15 })
  const iconSize = useSpring(iconSizeTransform, { mass: 0.1, stiffness: 200, damping: 15 })

  const handleClick = () => {
    if (onNavigate) {
      onNavigate(item.href)
    }
  }

  return (
    <motion.div
      ref={ref}
      style={{ width, height }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={handleClick}
      className={cn(
        "relative flex aspect-square cursor-pointer items-center justify-center rounded-full",
        item.active
          ? "bg-primary/20 text-primary-foreground"
          : "text-muted-foreground hover:text-foreground",
      )}
    >
      <AnimatePresence>
        {hovered && (
          <motion.div
            initial={{ opacity: 0, y: 10, x: "-50%" }}
            animate={{ opacity: 1, y: 0, x: "-50%" }}
            exit={{ opacity: 0, y: 2, x: "-50%" }}
            className="absolute -top-8 left-1/2 w-fit whitespace-pre rounded-md border border-border/40 bg-card px-2 py-0.5 text-xs text-foreground"
          >
            {item.title}
          </motion.div>
        )}
      </AnimatePresence>
      <motion.div
        style={{ width: iconSize, height: iconSize }}
        className="flex items-center justify-center"
      >
        {item.icon}
      </motion.div>
      {item.active && (
        <span className="absolute -bottom-1 h-1 w-1 rounded-full bg-primary" />
      )}
    </motion.div>
  )
}
