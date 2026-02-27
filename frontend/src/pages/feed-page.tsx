import { Radio, Clock, Tv } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useLiveStreams, useRecentStreams } from "@/hooks/use-streams"
import { StreamCard } from "@/components/streams/stream-card"
import { GoLiveDialog } from "@/components/streams/go-live-dialog"
import { EmptyState } from "@/components/common/empty-state"

export function FeedPage() {
  const { data: liveStreams, isLoading: liveLoading, refetch: refetchLive } = useLiveStreams()
  const { data: recentStreams, isLoading: recentLoading } = useRecentStreams()

  const orgStreams = liveStreams?.filter((s) => s.access_level === "org_only") ?? []
  const friendStreams = liveStreams?.filter((s) => s.access_level !== "org_only") ?? []

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      {/* Header with Go Live */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-foreground">Feed</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            See who&apos;s live. Or start mogging yourself.
          </p>
        </div>
        <GoLiveDialog
          trigger={
            <Button className="gap-2">
              <Radio className="h-4 w-4" />
              Go Live
            </Button>
          }
          onCreated={refetchLive}
        />
      </div>

      {/* Org streams */}
      <section className="mb-10">
        <div className="mb-4 flex items-center gap-2">
          <Radio className="h-5 w-5 text-primary" />
          <h2 className="font-display text-lg font-semibold text-foreground">In Your Org</h2>
        </div>
        {liveLoading ? (
          <LoadingSkeleton count={2} size="lg" />
        ) : orgStreams.length > 0 ? (
          <div className="grid gap-4 sm:grid-cols-2">
            {orgStreams.map((stream) => (
              <StreamCard key={stream.id} stream={stream} size="lg" />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<Tv className="h-10 w-10" />}
            title="No org streams live"
            description="Nobody from your org is streaming right now. Be the first to mog."
          />
        )}
      </section>

      {/* Friends live */}
      <section className="mb-10">
        <div className="mb-4 flex items-center gap-2">
          <Radio className="h-5 w-5 text-emerald-400" />
          <h2 className="font-display text-lg font-semibold text-foreground">Friends Live</h2>
        </div>
        {liveLoading ? (
          <LoadingSkeleton count={3} size="md" />
        ) : friendStreams.length > 0 ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {friendStreams.map((stream) => (
              <StreamCard key={stream.id} stream={stream} size="md" />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<Tv className="h-10 w-10" />}
            title="No friends live"
            description="Your friends are being mid right now. Check back later."
          />
        )}
      </section>

      {/* Recent streams */}
      <section>
        <div className="mb-4 flex items-center gap-2">
          <Clock className="h-5 w-5 text-muted-foreground" />
          <h2 className="font-display text-lg font-semibold text-foreground">Recent Streams</h2>
        </div>
        {recentLoading ? (
          <LoadingSkeleton count={4} size="sm" />
        ) : (recentStreams?.length ?? 0) > 0 ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {recentStreams!.map((stream) => (
              <StreamCard key={stream.id} stream={stream} size="sm" />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<Clock className="h-10 w-10" />}
            title="No recent streams"
            description="No one's streamed yet. Time to start mogging."
          />
        )}
      </section>
    </div>
  )
}

function LoadingSkeleton({ count, size }: { count: number; size: "sm" | "md" | "lg" }) {
  const heights = { sm: "h-32", md: "h-44", lg: "h-56" }
  const cols = {
    sm: "sm:grid-cols-2 lg:grid-cols-4",
    md: "sm:grid-cols-2 lg:grid-cols-3",
    lg: "sm:grid-cols-2",
  }

  return (
    <div className={`grid gap-4 ${cols[size]}`}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`${heights[size]} animate-pulse rounded-xl border border-border/20 bg-card/30`}
        />
      ))}
    </div>
  )
}
