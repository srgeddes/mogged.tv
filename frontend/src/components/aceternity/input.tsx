import { forwardRef, useState } from "react"
import { motion, useMotionTemplate, useMotionValue } from "framer-motion"
import { cn } from "@/lib/utils"

export interface AceternityInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

export const AceternityInput = forwardRef<HTMLInputElement, AceternityInputProps>(
  ({ className, type, ...props }, ref) => {
    const radius = 100
    const [visible, setVisible] = useState(false)

    const mouseX = useMotionValue(0)
    const mouseY = useMotionValue(0)

    function handleMouseMove({
      currentTarget,
      clientX,
      clientY,
    }: React.MouseEvent<HTMLDivElement>) {
      const { left, top } = currentTarget.getBoundingClientRect()
      mouseX.set(clientX - left)
      mouseY.set(clientY - top)
    }

    return (
      <motion.div
        style={{
          background: useMotionTemplate`
            radial-gradient(
              ${visible ? radius + "px" : "0px"} circle at ${mouseX}px ${mouseY}px,
              hsl(205 100% 40%),
              transparent 80%
            )
          `,
        }}
        onMouseMove={handleMouseMove}
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
        className="group/input rounded-lg p-[2px] transition duration-300"
      >
        <input
          type={type}
          className={cn(
            "flex h-10 w-full rounded-md border-none bg-zinc-900 px-3 py-2 text-sm text-foreground shadow-[0px_0px_1px_1px_var(--border)] transition duration-400 file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground/50 focus-visible:outline-none focus-visible:ring-[2px] focus-visible:ring-primary/50 disabled:cursor-not-allowed disabled:opacity-50 group-hover/input:shadow-none",
            className,
          )}
          ref={ref}
          {...props}
        />
      </motion.div>
    )
  },
)
AceternityInput.displayName = "AceternityInput"
