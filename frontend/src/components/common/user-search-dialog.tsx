import { useState } from "react"
import { Search } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { useUserSearch } from "@/hooks/use-user-search"
import type { UserSearchResult } from "@/types"

interface UserSearchDialogProps {
  trigger: React.ReactNode
  title?: string
  onSelect: (user: UserSearchResult) => void
}

export function UserSearchDialog({
  trigger,
  title = "Search users",
  onSelect,
}: UserSearchDialogProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")
  const { results, isSearching, search } = useUserSearch()

  const handleSearch = (value: string) => {
    setQuery(value)
    search(value)
  }

  const handleSelect = (user: UserSearchResult) => {
    onSelect(user)
    setOpen(false)
    setQuery("")
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by name..."
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="max-h-64 space-y-1 overflow-y-auto">
          {isSearching && (
            <p className="py-4 text-center text-sm text-muted-foreground">Searching...</p>
          )}
          {!isSearching && query.length > 0 && results.length === 0 && (
            <p className="py-4 text-center text-sm text-muted-foreground">No users found</p>
          )}
          {results.map((user) => (
            <Button
              key={user.id}
              variant="ghost"
              className="w-full justify-start gap-3 px-3"
              onClick={() => handleSelect(user)}
            >
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-primary/20 text-xs text-primary-foreground">
                  {user.display_name?.[0] ?? user.username[0]}
                </AvatarFallback>
              </Avatar>
              <div className="text-left">
                <p className="text-sm font-medium">{user.display_name ?? user.username}</p>
                <p className="font-mono text-xs text-muted-foreground">@{user.username}</p>
              </div>
            </Button>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  )
}
