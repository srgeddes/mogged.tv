import { cn } from "@/lib/utils"

const sizes = {
  sm: { icon: 24, text: "text-lg" },
  md: { icon: 32, text: "text-xl" },
  lg: { icon: 48, text: "text-3xl" },
} as const

interface LogoProps {
  size?: keyof typeof sizes
  className?: string
  showText?: boolean
}

export function Logo({ size = "md", className, showText = true }: LogoProps) {
  const { icon, text } = sizes[size]

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <svg
        width={icon}
        height={icon}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0"
      >
        <defs>
          <linearGradient id="logo-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#003153" />
            <stop offset="50%" stopColor="#0066aa" />
            <stop offset="100%" stopColor="#003153" />
          </linearGradient>
        </defs>
        {/* Abstract "M" — two overlapping peaks with a glow */}
        <rect width="48" height="48" rx="10" fill="url(#logo-gradient)" />
        <path
          d="M10 36V16L18 28L24 18L30 28L38 16V36"
          stroke="white"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
        {/* Subtle broadcast signal arc */}
        <path
          d="M20 12C22 10 26 10 28 12"
          stroke="white"
          strokeWidth="1.5"
          strokeLinecap="round"
          opacity="0.6"
        />
        <path
          d="M17 9C21 6 27 6 31 9"
          stroke="white"
          strokeWidth="1.5"
          strokeLinecap="round"
          opacity="0.3"
        />
      </svg>
      {showText && (
        <span className={cn("font-display font-bold tracking-tight text-foreground", text)}>
          mogged<span className="text-primary">.tv</span>
        </span>
      )}
    </div>
  )
}
