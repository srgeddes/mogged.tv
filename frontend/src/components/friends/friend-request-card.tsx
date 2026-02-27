import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Check, X } from "lucide-react"
import type { FriendRequest } from "@/types"

interface IncomingRequestCardProps {
  request: FriendRequest
  onAccept: (requestId: string) => void
  onDecline: (requestId: string) => void
}

export function IncomingRequestCard({ request, onAccept, onDecline }: IncomingRequestCardProps) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-border/40 bg-card/50 px-4 py-3">
      <div className="flex items-center gap-3">
        <Avatar className="h-10 w-10">
          <AvatarFallback className="bg-primary/20 text-sm text-primary-foreground">
            {request.from_display_name?.[0] ?? request.from_username?.[0] ?? "?"}
          </AvatarFallback>
        </Avatar>
        <div>
          <span className="text-sm font-medium text-foreground">
            {request.from_display_name ?? request.from_username}
          </span>
          <p className="font-mono text-xs text-muted-foreground">@{request.from_username}</p>
        </div>
      </div>
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-emerald-400 hover:bg-emerald-500/10 hover:text-emerald-400"
          onClick={() => onAccept(request.id)}
        >
          <Check className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-muted-foreground hover:text-destructive"
          onClick={() => onDecline(request.id)}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

interface OutgoingRequestCardProps {
  request: FriendRequest
  onCancel: (requestId: string) => void
}

export function OutgoingRequestCard({ request, onCancel }: OutgoingRequestCardProps) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-border/40 bg-card/50 px-4 py-3">
      <div className="flex items-center gap-3">
        <Avatar className="h-10 w-10">
          <AvatarFallback className="bg-primary/20 text-sm text-primary-foreground">
            {request.to_display_name?.[0] ?? request.to_username?.[0] ?? "?"}
          </AvatarFallback>
        </Avatar>
        <div>
          <span className="text-sm font-medium text-foreground">
            {request.to_display_name ?? request.to_username}
          </span>
          <p className="font-mono text-xs text-muted-foreground">@{request.to_username}</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground">Pending</span>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-muted-foreground hover:text-destructive"
          onClick={() => onCancel(request.id)}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
