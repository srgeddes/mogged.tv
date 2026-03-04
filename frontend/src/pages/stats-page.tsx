import { BarChart3, Clock, Eye, Flame, MessageSquare, Radio, Smile, Tv, Users, Zap } from "lucide-react"
import { useUserStats } from "@/hooks/use-streams"
import { EmptyState } from "@/components/common/empty-state"
import type { HostedStreamItem, WatchedStreamItem } from "@/types"

export function StatsPage() {
  const { data: stats, isLoading } = useUserStats()

  if (isLoading) {
    return (
      <div className="py-8">
        <h1 className="mb-6 font-display text-2xl font-bold text-foreground">Your Stats</h1>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-28 animate-pulse rounded-xl border border-border/20 bg-card/30" />
          ))}
        </div>
        <div className="mt-8 h-48 animate-pulse rounded-xl border border-border/20 bg-card/30" />
        <div className="mt-8 h-48 animate-pulse rounded-xl border border-border/20 bg-card/30" />
        <div className="mt-8 h-32 animate-pulse rounded-xl border border-border/20 bg-card/30" />
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="py-8">
        <h1 className="mb-6 font-display text-2xl font-bold text-foreground">Your Stats</h1>
        <EmptyState
          icon={<BarChart3 className="h-10 w-10" />}
          title="No stats yet"
          description="Start streaming or watching to build your stats. Get out there and mog."
        />
      </div>
    )
  }

  const allZeroes =
    stats.hosting.total_streams_hosted === 0 &&
    stats.watching.total_streams_watched === 0 &&
    stats.engagement.total_messages_sent === 0

  if (allZeroes) {
    return (
      <div className="py-8">
        <h1 className="mb-6 font-display text-2xl font-bold text-foreground">Your Stats</h1>
        <EmptyState
          icon={<BarChart3 className="h-10 w-10" />}
          title="No stats yet"
          description="Start streaming or watching to build your stats. Get out there and mog."
        />
      </div>
    )
  }

  return (
    <div className="py-8">
      <h1 className="mb-6 font-display text-2xl font-bold text-foreground">Your Stats</h1>

      {/* Section 1 — Overview cards */}
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        <OverviewCard
          icon={<Tv className="h-5 w-5" />}
          label="Streams Hosted"
          value={stats.hosting.total_streams_hosted}
          color="text-live"
        />
        <OverviewCard
          icon={<Eye className="h-5 w-5" />}
          label="Streams Watched"
          value={stats.watching.total_streams_watched}
          color="text-primary"
        />
        <OverviewCard
          icon={<Clock className="h-5 w-5" />}
          label="Time Live"
          value={formatDuration(stats.hosting.total_stream_time_seconds)}
          color="text-purple-400"
        />
        <OverviewCard
          icon={<Clock className="h-5 w-5" />}
          label="Watch Time"
          value={formatDuration(stats.watching.total_watch_time_seconds)}
          color="text-blue-400"
        />
      </div>

      {/* Section 2 — Hosting */}
      <section className="mt-10">
        <div className="mb-4 flex items-center gap-2">
          <Radio className="h-5 w-5 text-live" />
          <h2 className="font-display text-lg font-semibold text-foreground">Hosting</h2>
        </div>

        {stats.hosting.total_streams_hosted > 0 ? (
          <>
            <div className="mb-4 flex flex-wrap gap-2">
              <StatPill label="Avg Duration" value={formatDuration(stats.hosting.avg_stream_duration_seconds)} />
              <StatPill label="Longest Stream" value={formatDuration(stats.hosting.longest_stream_seconds)} />
              <StatPill label="Avg Viewers" value={stats.hosting.avg_peak_viewers.toFixed(1)} />
              <StatPill label="Peak Viewers" value={stats.hosting.total_peak_viewers} />
              {stats.hosting.last_stream_ended_at && (
                <StatPill label="Last Streamed" value={formatRelativeDate(stats.hosting.last_stream_ended_at)} />
              )}
            </div>

            {stats.hosted_streams.length > 0 && (
              <div>
                <h3 className="mb-2 text-sm font-medium text-muted-foreground">Recent Streams</h3>
                <div className="space-y-2">
                  {stats.hosted_streams.map((stream) => (
                    <HostedStreamRow key={stream.id} stream={stream} />
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <p className="rounded-xl border border-border/20 bg-card/30 py-6 text-center text-sm text-muted-foreground">
            You haven't hosted any streams yet. Time to mog.
          </p>
        )}
      </section>

      {/* Section 3 — Watching */}
      <section className="mt-10">
        <div className="mb-4 flex items-center gap-2">
          <Eye className="h-5 w-5 text-primary" />
          <h2 className="font-display text-lg font-semibold text-foreground">Watching</h2>
        </div>

        {stats.watching.total_streams_watched > 0 ? (
          <>
            <div className="mb-4 flex flex-wrap gap-2">
              <StatPill label="Avg Watch Time" value={formatDuration(stats.watching.avg_watch_time_seconds)} />
              {stats.watching.last_watched_at && (
                <StatPill label="Last Watched" value={formatRelativeDate(stats.watching.last_watched_at)} />
              )}
              {stats.watching.favorite_host_username && (
                <StatPill
                  label="Favorite Host"
                  value={stats.watching.favorite_host_display_name ?? stats.watching.favorite_host_username}
                />
              )}
            </div>

            {stats.watched_streams.length > 0 && (
              <div>
                <h3 className="mb-2 text-sm font-medium text-muted-foreground">Streams Watched</h3>
                <div className="space-y-2">
                  {stats.watched_streams.map((stream) => (
                    <WatchedStreamRow key={stream.stream_id} stream={stream} />
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <p className="rounded-xl border border-border/20 bg-card/30 py-6 text-center text-sm text-muted-foreground">
            No streams watched yet. Go support your homies.
          </p>
        )}
      </section>

      {/* Section 4 — Engagement */}
      <section className="mt-10">
        <div className="mb-4 flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-cyan-400" />
          <h2 className="font-display text-lg font-semibold text-foreground">Engagement</h2>
        </div>

        <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-5">
          <EngagementCard icon={<MessageSquare className="h-4 w-4" />} label="Messages Sent" value={stats.engagement.total_messages_sent} color="text-cyan-400" />
          <EngagementCard icon={<Smile className="h-4 w-4" />} label="Emotes Sent" value={stats.engagement.total_emotes_sent} color="text-pink-400" />
          <EngagementCard icon={<Flame className="h-4 w-4" />} label="Aura Earned" value={stats.engagement.total_aura_earned} color="text-primary" />
          <EngagementCard icon={<Flame className="h-4 w-4" />} label="Aura Given" value={stats.engagement.total_aura_given} color="text-rose-400" />
          <EngagementCard icon={<Zap className="h-4 w-4" />} label="Biggest Drop" value={stats.engagement.biggest_aura_drop} color="text-orange-400" />
        </div>
      </section>
    </div>
  )
}

// --- Sub-components ---

function OverviewCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string | number; color: string }) {
  return (
    <div className="rounded-xl border border-border/40 bg-card/50 p-4">
      <div className={`mb-2 ${color}`}>{icon}</div>
      <p className="font-display text-2xl font-bold text-foreground">{typeof value === "number" ? value.toLocaleString() : value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  )
}

function StatPill({ label, value }: { label: string; value: string | number }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-border/30 bg-card/40 px-3 py-1 text-xs">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-semibold text-foreground">{typeof value === "number" ? value.toLocaleString() : value}</span>
    </span>
  )
}

function EngagementCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: number; color: string }) {
  return (
    <div className="rounded-xl border border-border/40 bg-card/50 p-3 text-center">
      <div className={`mx-auto mb-1.5 flex h-8 w-8 items-center justify-center rounded-lg bg-secondary/50 ${color}`}>
        {icon}
      </div>
      <p className="font-display text-lg font-bold text-foreground">{value.toLocaleString()}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  )
}

function HostedStreamRow({ stream }: { stream: HostedStreamItem }) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-border/20 bg-card/30 px-4 py-3">
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-foreground">{stream.title}</p>
        <p className="text-xs text-muted-foreground">
          {stream.ended_at ? formatRelativeDate(stream.ended_at) : "—"}
        </p>
      </div>
      <div className="ml-4 flex items-center gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {formatDuration(stream.duration_seconds)}
        </span>
        {stream.max_viewers != null && (
          <span className="flex items-center gap-1">
            <Users className="h-3 w-3" />
            {stream.max_viewers}
          </span>
        )}
      </div>
    </div>
  )
}

function WatchedStreamRow({ stream }: { stream: WatchedStreamItem }) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-border/20 bg-card/30 px-4 py-3">
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-foreground">{stream.title}</p>
        <p className="text-xs text-muted-foreground">
          {stream.host_display_name ?? stream.host_username} &middot; {formatRelativeDate(stream.joined_at)}
        </p>
      </div>
      <div className="ml-4 flex items-center gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {formatDuration(stream.watch_time_seconds)}
        </span>
      </div>
    </div>
  )
}

// --- Helpers ---

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
}

function formatRelativeDate(isoString: string): string {
  const now = Date.now()
  const then = new Date(isoString).getTime()
  const diffSeconds = Math.floor((now - then) / 1000)

  if (diffSeconds < 60) return "just now"
  const diffMinutes = Math.floor(diffSeconds / 60)
  if (diffMinutes < 60) return `${diffMinutes}m ago`
  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d ago`
  const diffWeeks = Math.floor(diffDays / 7)
  if (diffWeeks < 5) return `${diffWeeks}w ago`
  const diffMonths = Math.floor(diffDays / 30)
  if (diffMonths < 12) return `${diffMonths}mo ago`
  const diffYears = Math.floor(diffDays / 365)
  return `${diffYears}y ago`
}
