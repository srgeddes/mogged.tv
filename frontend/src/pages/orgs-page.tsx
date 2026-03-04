import { useState } from "react"
import { Building2, Plus, Shield, UserPlus, Crown, UserMinus } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { useOrganizations, useOrgMembers, useOrgActions } from "@/hooks/use-organizations"
import { OrgCard } from "@/components/organizations/org-card"
import { UserSearchDialog } from "@/components/common/user-search-dialog"
import { EmptyState } from "@/components/common/empty-state"
import { useAuth } from "@/hooks/use-auth"
import type { Organization, OrgMember } from "@/types"

export function OrgsPage() {
  const { data: orgs, isLoading, refetch } = useOrganizations()
  const { createOrg } = useOrgActions()
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null)
  const [createOpen, setCreateOpen] = useState(false)

  const handleCreate = async (name: string, slug: string, description: string) => {
    const org = await createOrg({ name, slug, description: description || undefined })
    if (org) {
      setCreateOpen(false)
      refetch()
    }
  }

  return (
    <div className="py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl font-bold text-foreground">Organizations</h1>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button variant="secondary" size="sm" className="gap-2">
              <Plus className="h-4 w-4" />
              Create Org
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Create Organization</DialogTitle>
            </DialogHeader>
            <CreateOrgForm onSubmit={handleCreate} />
          </DialogContent>
        </Dialog>
      </div>

      {selectedOrg ? (
        <OrgDetailView org={selectedOrg} onBack={() => setSelectedOrg(null)} onUpdate={refetch} />
      ) : (
        <div className="space-y-3">
          {isLoading ? (
            <LoadingList count={3} />
          ) : (orgs?.length ?? 0) > 0 ? (
            orgs!.map((org) => (
              <OrgCard key={org.id} org={org} onClick={() => setSelectedOrg(org)} />
            ))
          ) : (
            <EmptyState
              icon={<Building2 className="h-10 w-10" />}
              title="No organizations"
              description="Create one and invite your squad."
            />
          )}
        </div>
      )}
    </div>
  )
}

function CreateOrgForm({ onSubmit }: { onSubmit: (name: string, slug: string, desc: string) => void }) {
  const [name, setName] = useState("")
  const [slug, setSlug] = useState("")
  const [description, setDescription] = useState("")

  const handleNameChange = (value: string) => {
    setName(value)
    setSlug(
      value
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, ""),
    )
  }

  return (
    <form
      className="space-y-4"
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit(name, slug, description)
      }}
    >
      <div className="space-y-2">
        <Label htmlFor="org-name">Name</Label>
        <Input
          id="org-name"
          value={name}
          onChange={(e) => handleNameChange(e.target.value)}
          placeholder="My Squad"
          required
          maxLength={100}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="org-slug">Slug</Label>
        <Input
          id="org-slug"
          value={slug}
          onChange={(e) => setSlug(e.target.value)}
          placeholder="my-squad"
          required
          maxLength={100}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="org-desc">Description</Label>
        <Input
          id="org-desc"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional description"
        />
      </div>
      <Button type="submit" className="w-full" disabled={!name || !slug}>
        Create
      </Button>
    </form>
  )
}

function OrgDetailView({
  org,
  onBack,
  onUpdate,
}: {
  org: Organization
  onBack: () => void
  onUpdate: () => void
}) {
  const { user } = useAuth()
  const { data: members, refetch: refetchMembers } = useOrgMembers(org.id)
  const { addMember, removeMember, updateRole } = useOrgActions()

  const currentMember = members?.find((m) => m.user_id === user?.id)
  const isAdmin = currentMember?.role === "owner" || currentMember?.role === "admin"

  const handleAddMember = async (selectedUser: { id: string }) => {
    const ok = await addMember(org.id, selectedUser.id)
    if (ok) refetchMembers()
  }

  const handleRemove = async (userId: string) => {
    const ok = await removeMember(org.id, userId)
    if (ok) {
      refetchMembers()
      onUpdate()
    }
  }

  const handleRoleChange = async (userId: string, role: string) => {
    const ok = await updateRole(org.id, userId, role)
    if (ok) refetchMembers()
  }

  return (
    <div>
      <button onClick={onBack} className="mb-4 text-sm text-muted-foreground hover:text-foreground">
        &larr; Back to orgs
      </button>

      <div className="mb-6 flex items-center gap-4">
        <Avatar className="h-14 w-14">
          <AvatarFallback className="bg-primary/20 text-xl font-semibold text-primary-foreground">
            {org.name[0]}
          </AvatarFallback>
        </Avatar>
        <div>
          <h2 className="font-display text-xl font-bold text-foreground">{org.name}</h2>
          {org.description && (
            <p className="text-sm text-muted-foreground">{org.description}</p>
          )}
        </div>
      </div>

      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium text-muted-foreground">
          Members ({members?.length ?? 0})
        </h3>
        {isAdmin && (
          <UserSearchDialog
            trigger={
              <Button variant="secondary" size="sm" className="gap-2">
                <UserPlus className="h-4 w-4" />
                Add Member
              </Button>
            }
            title="Add member to org"
            onSelect={handleAddMember}
          />
        )}
      </div>

      <div className="space-y-2">
        {members?.map((member) => (
          <MemberRow
            key={member.id}
            member={member}
            isAdmin={isAdmin}
            isOwner={currentMember?.role === "owner"}
            isSelf={member.user_id === user?.id}
            onRemove={handleRemove}
            onRoleChange={handleRoleChange}
          />
        ))}
      </div>
    </div>
  )
}

function MemberRow({
  member,
  isAdmin,
  isOwner,
  isSelf,
  onRemove,
  onRoleChange,
}: {
  member: OrgMember
  isAdmin: boolean
  isOwner: boolean
  isSelf: boolean
  onRemove: (userId: string) => void
  onRoleChange: (userId: string, role: string) => void
}) {
  const roleIcon =
    member.role === "owner" ? (
      <Crown className="h-3.5 w-3.5 text-amber-400" />
    ) : member.role === "admin" ? (
      <Shield className="h-3.5 w-3.5 text-primary" />
    ) : null

  return (
    <div className="flex items-center justify-between rounded-lg border border-border/40 bg-card/50 px-4 py-3">
      <div className="flex items-center gap-3">
        <Avatar className="h-9 w-9">
          <AvatarFallback className="bg-primary/20 text-xs text-primary-foreground">
            {member.display_name?.[0] ?? member.username[0]}
          </AvatarFallback>
        </Avatar>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-foreground">
              {member.display_name ?? member.username}
            </span>
            {roleIcon}
          </div>
          <span className="font-mono text-xs text-muted-foreground">@{member.username}</span>
        </div>
      </div>
      <div className="flex items-center gap-1">
        {isOwner && !isSelf && member.role !== "owner" && (
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs text-muted-foreground"
            onClick={() =>
              onRoleChange(member.user_id, member.role === "admin" ? "member" : "admin")
            }
          >
            {member.role === "admin" ? "Demote" : "Promote"}
          </Button>
        )}
        {isAdmin && !isSelf && member.role !== "owner" && (
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 text-muted-foreground hover:text-destructive"
            onClick={() => onRemove(member.user_id)}
          >
            <UserMinus className="h-3.5 w-3.5" />
          </Button>
        )}
      </div>
    </div>
  )
}

function LoadingList({ count }: { count: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="h-20 animate-pulse rounded-xl border border-border/20 bg-card/30" />
      ))}
    </>
  )
}
