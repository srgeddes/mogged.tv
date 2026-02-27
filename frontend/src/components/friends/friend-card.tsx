import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { UserMinus } from "lucide-react"
import type { Friend } from "@/types"

interface FriendCardProps {
  friend: Friend
  onRemove: (userId: string) => void
}

export function FriendCard({ friend, onRemove }: FriendCardProps) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-border/40 bg-card/50 px-4 py-3">
      <div className="flex items-center gap-3">
        <Avatar className="h-10 w-10">
          <AvatarFallback className="bg-primary/20 text-sm text-primary-foreground">
            {friend.display_name?.[0] ?? friend.username[0]}
          </AvatarFallback>
        </Avatar>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-foreground">
              {friend.display_name ?? friend.username}
            </span>
            {friend.is_in_shared_org && (
              <span className="rounded-sm bg-primary/20 px-1.5 py-0.5 font-mono text-[10px] font-medium text-primary-foreground">
                ORG
              </span>
            )}
          </div>
          <span className="font-mono text-xs text-muted-foreground">@{friend.username}</span>
        </div>
      </div>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 text-muted-foreground hover:text-destructive"
        onClick={() => onRemove(friend.user_id)}
      >
        <UserMinus className="h-4 w-4" />
      </Button>
    </div>
  )
}
