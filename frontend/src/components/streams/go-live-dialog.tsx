import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Radio, Globe, Users, Building2, Link2 } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/hooks/use-auth"
import { useStreamActions } from "@/hooks/use-streams"
import { useOrganizations } from "@/hooks/use-organizations"
import { cn } from "@/lib/utils"
import type { StreamAccessLevel } from "@/types"

interface GoLiveDialogProps {
  trigger: React.ReactNode
  onCreated?: () => void
}

const ACCESS_OPTIONS: {
  value: StreamAccessLevel
  label: string
  description: string
  icon: React.ReactNode
}[] = [
  {
    value: "public",
    label: "Public",
    description: "Anyone can join",
    icon: <Globe className="h-4 w-4" />,
  },
  {
    value: "friends",
    label: "Friends Only",
    description: "Only your friends",
    icon: <Users className="h-4 w-4" />,
  },
  {
    value: "org_only",
    label: "Org Only",
    description: "Members of an org",
    icon: <Building2 className="h-4 w-4" />,
  },
  {
    value: "link_only",
    label: "Invite Link",
    description: "Only with a link",
    icon: <Link2 className="h-4 w-4" />,
  },
]

export function GoLiveDialog({ trigger, onCreated }: GoLiveDialogProps) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [accessLevel, setAccessLevel] = useState<StreamAccessLevel>("public")
  const [orgId, setOrgId] = useState<string>("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const navigate = useNavigate()
  const { user } = useAuth()
  const { createStream, startStream } = useStreamActions()
  const { data: orgs } = useOrganizations()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    const stream = await createStream({
      title,
      description: description || undefined,
      access_level: accessLevel,
      org_id: accessLevel === "org_only" && orgId ? orgId : undefined,
    })

    if (stream) {
      const result = await startStream(stream.id)
      if (result) {
        setOpen(false)
        resetForm()
        navigate(`/${user!.username}`, {
          state: {
            token: result.token,
            livekitUrl: result.livekit_url,
            stream: result.stream,
          },
        })
        onCreated?.()
      }
    }

    setIsSubmitting(false)
  }

  const resetForm = () => {
    setTitle("")
    setDescription("")
    setAccessLevel("public")
    setOrgId("")
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        setOpen(v)
        if (!v) resetForm()
      }}
    >
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Radio className="h-5 w-5 text-red-400" />
            Go Live
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="stream-title">Title</Label>
            <Input
              id="stream-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="What are you streaming?"
              required
              maxLength={200}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="stream-desc">Description</Label>
            <Input
              id="stream-desc"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description"
            />
          </div>

          <div className="space-y-2">
            <Label>Who can watch?</Label>
            <div className="grid grid-cols-2 gap-2">
              {ACCESS_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => {
                    setAccessLevel(opt.value)
                    if (opt.value !== "org_only") setOrgId("")
                  }}
                  className={cn(
                    "flex items-center gap-2.5 rounded-lg border px-3 py-2.5 text-left text-sm transition-all",
                    accessLevel === opt.value
                      ? "border-primary/60 bg-primary/10 text-foreground"
                      : "border-border/40 bg-card/30 text-muted-foreground hover:border-border/60",
                  )}
                >
                  <span
                    className={cn(
                      accessLevel === opt.value ? "text-primary-foreground" : "text-muted-foreground",
                    )}
                  >
                    {opt.icon}
                  </span>
                  <div>
                    <p className="font-medium">{opt.label}</p>
                    <p className="text-[11px] text-muted-foreground">{opt.description}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {accessLevel === "org_only" && (
            <div className="space-y-2">
              <Label>Organization</Label>
              {orgs && orgs.length > 0 ? (
                <div className="space-y-1">
                  {orgs.map((org) => (
                    <button
                      key={org.id}
                      type="button"
                      onClick={() => setOrgId(org.id)}
                      className={cn(
                        "flex w-full items-center gap-2 rounded-md border px-3 py-2 text-left text-sm transition-all",
                        orgId === org.id
                          ? "border-primary/60 bg-primary/10 text-foreground"
                          : "border-border/40 text-muted-foreground hover:border-border/60",
                      )}
                    >
                      <Building2 className="h-4 w-4" />
                      {org.name}
                      <span className="ml-auto font-mono text-xs">{org.member_count} members</span>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  You&apos;re not in any orgs yet. Create one first.
                </p>
              )}
            </div>
          )}

          <Button
            type="submit"
            className="w-full gap-2"
            disabled={
              isSubmitting || !title || (accessLevel === "org_only" && !orgId)
            }
          >
            <Radio className="h-4 w-4" />
            {isSubmitting ? "Starting stream..." : "Go Live"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}
