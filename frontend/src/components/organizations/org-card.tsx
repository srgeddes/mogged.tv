import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Users } from "lucide-react"
import type { Organization } from "@/types"

interface OrgCardProps {
  org: Organization
  onClick: () => void
}

export function OrgCard({ org, onClick }: OrgCardProps) {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center gap-4 rounded-xl border border-border/40 bg-card/50 p-4 text-left transition-all hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5"
    >
      <Avatar className="h-12 w-12">
        <AvatarFallback className="bg-primary/20 text-lg font-semibold text-primary-foreground">
          {org.name[0]}
        </AvatarFallback>
      </Avatar>
      <div className="flex-1">
        <h3 className="font-display text-sm font-semibold text-foreground">{org.name}</h3>
        {org.description && (
          <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">{org.description}</p>
        )}
      </div>
      <div className="flex items-center gap-1.5 text-muted-foreground">
        <Users className="h-4 w-4" />
        <span className="font-mono text-xs">{org.member_count}</span>
      </div>
    </button>
  )
}
