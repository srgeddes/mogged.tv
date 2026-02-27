import { useState } from "react"
import { useAuth } from "@/hooks/use-auth"
import { useUserStats } from "@/hooks/use-streams"
import { api, ApiError } from "@/lib/api"
import { showSuccess, showError } from "@/lib/toast"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import {
  Tv,
  Clock,
  Flame,
  MessageSquare,
  Pencil,
  X,
  Check,
  LogOut,
  Trophy,
} from "lucide-react"
import type { User } from "@/types"

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
}

export function ProfilePage() {
  const { user, login, token, logout } = useAuth()
  const { data: stats } = useUserStats()
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [displayName, setDisplayName] = useState(user?.display_name ?? "")
  const [bio, setBio] = useState("")

  const handleSave = async () => {
    setIsSaving(true)
    try {
      const updated = await api.patch<User>("/users/me", {
        display_name: displayName || null,
        bio: bio || null,
      })
      if (token) {
        login(token, updated)
      }
      showSuccess("Profile updated")
      setIsEditing(false)
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to update profile")
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    setDisplayName(user?.display_name ?? "")
    setIsEditing(false)
  }

  const initials = user?.display_name?.[0] ?? user?.username?.[0] ?? "?"

  const quickStats = stats
    ? [
        { icon: <Tv className="h-4 w-4" />, label: "Streams", value: stats.total_streams_hosted, color: "text-primary" },
        { icon: <Clock className="h-4 w-4" />, label: "Watch time", value: formatDuration(stats.total_watch_time_seconds), color: "text-blue-400" },
        { icon: <Flame className="h-4 w-4" />, label: "Aura", value: stats.total_aura_earned.toLocaleString(), color: "text-amber-400" },
        { icon: <MessageSquare className="h-4 w-4" />, label: "Messages", value: stats.total_messages_sent.toLocaleString(), color: "text-cyan-400" },
        { icon: <Trophy className="h-4 w-4" />, label: "Longest stream", value: formatDuration(stats.longest_stream_seconds), color: "text-yellow-400" },
      ]
    : null

  return (
    <div className="mx-auto max-w-2xl px-6 py-8">
      {/* Profile header */}
      <div className="flex items-start gap-6">
        <Avatar className="h-20 w-20 border-2 border-border/40">
          <AvatarFallback className="bg-primary/20 text-2xl font-bold text-primary-foreground">
            {initials}
          </AvatarFallback>
        </Avatar>

        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="font-display text-2xl font-bold text-foreground">
              {user?.display_name ?? user?.username}
            </h1>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              >
                <Pencil className="h-4 w-4" />
              </button>
            )}
          </div>
          <p className="font-mono text-sm text-muted-foreground">@{user?.username}</p>
          <p className="mt-1 text-sm text-muted-foreground/60">{user?.email}</p>
        </div>
      </div>

      {/* Edit form */}
      {isEditing && (
        <div className="mt-6 rounded-xl border border-border/40 bg-card/50 p-5">
          <h3 className="mb-4 font-display text-sm font-semibold text-foreground">Edit Profile</h3>
          <div className="space-y-4">
            <div>
              <Label htmlFor="display-name" className="text-xs text-muted-foreground">
                Display Name
              </Label>
              <Input
                id="display-name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder={user?.username}
                className="mt-1"
                maxLength={50}
              />
            </div>
            <div>
              <Label htmlFor="bio" className="text-xs text-muted-foreground">
                Bio
              </Label>
              <Input
                id="bio"
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                placeholder="tell the people who you are"
                className="mt-1"
                maxLength={160}
              />
              <p className="mt-1 text-right text-xs text-muted-foreground/40">
                {bio.length}/160
              </p>
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2">
            <Button size="sm" onClick={handleSave} disabled={isSaving}>
              <Check className="mr-1.5 h-3.5 w-3.5" />
              {isSaving ? "Saving..." : "Save"}
            </Button>
            <Button size="sm" variant="ghost" onClick={handleCancel} disabled={isSaving}>
              <X className="mr-1.5 h-3.5 w-3.5" />
              Cancel
            </Button>
          </div>
        </div>
      )}

      <Separator className="my-8 opacity-40" />

      {/* Quick stats */}
      <div>
        <h2 className="mb-4 font-display text-lg font-semibold text-foreground">Stats</h2>
        {quickStats ? (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            {quickStats.map((stat) => (
              <div
                key={stat.label}
                className="rounded-xl border border-border/40 bg-card/50 p-3 text-center"
              >
                <div className={`mx-auto mb-1.5 flex h-8 w-8 items-center justify-center rounded-lg bg-secondary/50 ${stat.color}`}>
                  {stat.icon}
                </div>
                <p className="font-display text-lg font-bold text-foreground">{stat.value}</p>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-xl border border-border/20 bg-card/30 py-8 text-center">
            <p className="text-sm text-muted-foreground">No stats yet. Go stream something.</p>
          </div>
        )}
      </div>

      <Separator className="my-8 opacity-40" />

      {/* Account section */}
      <div>
        <h2 className="mb-4 font-display text-lg font-semibold text-foreground">Account</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-xl border border-border/40 bg-card/50 p-4">
            <div>
              <p className="text-sm font-medium text-foreground">Username</p>
              <p className="font-mono text-sm text-muted-foreground">@{user?.username}</p>
            </div>
          </div>
          <div className="flex items-center justify-between rounded-xl border border-border/40 bg-card/50 p-4">
            <div>
              <p className="text-sm font-medium text-foreground">Email</p>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="flex w-full items-center gap-2 rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm font-medium text-red-400 transition-colors hover:bg-red-500/10"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </div>
    </div>
  )
}
