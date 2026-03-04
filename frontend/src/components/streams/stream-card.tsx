import { useNavigate } from "react-router-dom"
import { cn } from "@/lib/utils"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Radio } from "lucide-react"
import type { Stream } from "@/types"

interface StreamCardProps {
  stream: Stream
  size?: "sm" | "md" | "lg"
  onClick?: () => void
  openInNewWindow?: boolean
}

export function StreamCard({ stream, size = "md", onClick, openInNewWindow }: StreamCardProps) {
  const navigate = useNavigate()
  const isLive = stream.status === "live"

  const sizeClasses = {
    sm: "h-32",
    md: "h-44",
    lg: "h-56",
  }

  return (
    <button
      onClick={() => {
        if (onClick) {
          onClick()
        } else if (stream.status === "live") {
          if (openInNewWindow) {
            window.open(`/${stream.host_username}`, "mogged-stream")
          } else {
            navigate(`/${stream.host_username}`)
          }
        }
      }}
      className={cn(
        "group relative w-full overflow-hidden rounded-xl border border-border/40 bg-card/50 text-left transition-all hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5",
        sizeClasses[size],
      )}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent" />

      <div className="relative flex h-full flex-col justify-between p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3
              className={cn(
                "font-display font-semibold text-foreground",
                size === "lg" ? "text-lg" : "text-sm",
              )}
            >
              {stream.title}
            </h3>
            {stream.description && size !== "sm" && (
              <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                {stream.description}
              </p>
            )}
          </div>
          {isLive && (
            <span className="flex items-center gap-1.5 rounded-full bg-live/20 px-2 py-0.5 text-xs font-medium text-live">
              <Radio className="h-3 w-3" />
              LIVE
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Avatar className="h-6 w-6">
            <AvatarFallback className="bg-primary/20 text-[10px] text-primary-foreground">
              {stream.host_display_name?.[0] ?? stream.host_username?.[0] ?? "?"}
            </AvatarFallback>
          </Avatar>
          <span className="font-mono text-xs text-muted-foreground">
            {stream.host_display_name ?? stream.host_username}
          </span>
          <span className="ml-auto rounded-full border border-border/40 px-2 py-0.5 text-[10px] text-muted-foreground">
            {stream.access_level === "friends"
              ? "Friends"
              : stream.access_level === "org_only"
                ? "Org Only"
                : "Private"}
          </span>
        </div>
      </div>
    </button>
  )
}
