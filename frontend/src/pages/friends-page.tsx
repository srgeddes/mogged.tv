import { useState } from "react"
import { UserPlus, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useFriends, useIncomingRequests, useOutgoingRequests, useFriendActions } from "@/hooks/use-friends"
import { FriendCard } from "@/components/friends/friend-card"
import { IncomingRequestCard, OutgoingRequestCard } from "@/components/friends/friend-request-card"
import { UserSearchDialog } from "@/components/common/user-search-dialog"
import { EmptyState } from "@/components/common/empty-state"
import { cn } from "@/lib/utils"

type Tab = "friends" | "requests"

export function FriendsPage() {
  const [tab, setTab] = useState<Tab>("friends")
  const { data: friends, isLoading: friendsLoading, refetch: refetchFriends } = useFriends()
  const {
    data: incoming,
    isLoading: incomingLoading,
    refetch: refetchIncoming,
  } = useIncomingRequests()
  const {
    data: outgoing,
    isLoading: outgoingLoading,
    refetch: refetchOutgoing,
  } = useOutgoingRequests()
  const { sendRequest, acceptRequest, declineRequest, cancelRequest, removeFriend } =
    useFriendActions()

  const handleAccept = async (requestId: string) => {
    const ok = await acceptRequest(requestId)
    if (ok) {
      refetchFriends()
      refetchIncoming()
    }
  }

  const handleDecline = async (requestId: string) => {
    const ok = await declineRequest(requestId)
    if (ok) refetchIncoming()
  }

  const handleCancel = async (requestId: string) => {
    const ok = await cancelRequest(requestId)
    if (ok) refetchOutgoing()
  }

  const handleRemove = async (userId: string) => {
    const ok = await removeFriend(userId)
    if (ok) refetchFriends()
  }

  const handleAddFriend = async (user: { id: string }) => {
    const ok = await sendRequest(user.id)
    if (ok) refetchOutgoing()
  }

  const requestCount = (incoming?.length ?? 0) + (outgoing?.length ?? 0)

  return (
    <div className="py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="font-display text-2xl font-bold text-foreground">Friends</h1>
        <UserSearchDialog
          trigger={
            <Button variant="secondary" size="sm" className="gap-2">
              <UserPlus className="h-4 w-4" />
              Add Friend
            </Button>
          }
          title="Add a friend"
          onSelect={handleAddFriend}
        />
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-lg border border-border/40 bg-card/30 p-1">
        <button
          onClick={() => setTab("friends")}
          className={cn(
            "flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors",
            tab === "friends"
              ? "bg-primary/20 text-foreground"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          Friends {friends?.length ? `(${friends.length})` : ""}
        </button>
        <button
          onClick={() => setTab("requests")}
          className={cn(
            "flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors",
            tab === "requests"
              ? "bg-primary/20 text-foreground"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          Requests {requestCount > 0 ? `(${requestCount})` : ""}
        </button>
      </div>

      {/* Friends tab */}
      {tab === "friends" && (
        <div className="space-y-2">
          {friendsLoading ? (
            <LoadingList count={5} />
          ) : (friends?.length ?? 0) > 0 ? (
            friends!.map((friend) => (
              <FriendCard key={friend.user_id} friend={friend} onRemove={handleRemove} />
            ))
          ) : (
            <EmptyState
              icon={<Users className="h-10 w-10" />}
              title="No friends yet"
              description="Add some people. Don't be a loner."
              action={
                <UserSearchDialog
                  trigger={
                    <Button variant="secondary" size="sm" className="gap-2">
                      <UserPlus className="h-4 w-4" />
                      Find people
                    </Button>
                  }
                  title="Add a friend"
                  onSelect={handleAddFriend}
                />
              }
            />
          )}
        </div>
      )}

      {/* Requests tab */}
      {tab === "requests" && (
        <div className="space-y-6">
          <section>
            <h3 className="mb-3 text-sm font-medium text-muted-foreground">Received</h3>
            <div className="space-y-2">
              {incomingLoading ? (
                <LoadingList count={2} />
              ) : (incoming?.length ?? 0) > 0 ? (
                incoming!.map((req) => (
                  <IncomingRequestCard
                    key={req.id}
                    request={req}
                    onAccept={handleAccept}
                    onDecline={handleDecline}
                  />
                ))
              ) : (
                <p className="py-4 text-center text-sm text-muted-foreground">
                  No incoming requests
                </p>
              )}
            </div>
          </section>
          <section>
            <h3 className="mb-3 text-sm font-medium text-muted-foreground">Sent</h3>
            <div className="space-y-2">
              {outgoingLoading ? (
                <LoadingList count={2} />
              ) : (outgoing?.length ?? 0) > 0 ? (
                outgoing!.map((req) => (
                  <OutgoingRequestCard key={req.id} request={req} onCancel={handleCancel} />
                ))
              ) : (
                <p className="py-4 text-center text-sm text-muted-foreground">
                  No outgoing requests
                </p>
              )}
            </div>
          </section>
        </div>
      )}
    </div>
  )
}

function LoadingList({ count }: { count: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="h-16 animate-pulse rounded-lg border border-border/20 bg-card/30" />
      ))}
    </>
  )
}
