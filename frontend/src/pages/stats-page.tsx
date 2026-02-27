import { BarChart3, Tv, Clock, Flame, MessageSquare, Smile, Zap, Trophy } from "lucide-react"
import { useUserStats } from "@/hooks/use-streams"
import { EmptyState } from "@/components/common/empty-state"

export function StatsPage() {
  const { data: stats, isLoading } = useUserStats()

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-8">
        <h1 className="mb-6 font-display text-2xl font-bold text-foreground">Your Stats</h1>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-28 animate-pulse rounded-xl border border-border/20 bg-card/30" />
          ))}
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-8">
        <h1 className="mb-6 font-display text-2xl font-bold text-foreground">Your Stats</h1>
        <EmptyState
          icon={<BarChart3 className="h-10 w-10" />}
          title="No stats yet"
          description="Start streaming or watching to build your stats. Get out there and mog."
        />
      </div>
    )
  }

  const statCards = [
    {
      icon: <Tv className="h-5 w-5" />,
      label: "Streams Hosted",
      value: stats.total_streams_hosted,
      color: "text-primary",
    },
    {
      icon: <Tv className="h-5 w-5" />,
      label: "Streams Watched",
      value: stats.total_streams_watched,
      color: "text-emerald-400",
    },
    {
      icon: <Clock className="h-5 w-5" />,
      label: "Watch Time",
      value: formatDuration(stats.total_watch_time_seconds),
      color: "text-blue-400",
    },
    {
      icon: <Clock className="h-5 w-5" />,
      label: "Stream Time",
      value: formatDuration(stats.total_stream_time_seconds),
      color: "text-purple-400",
    },
    {
      icon: <Flame className="h-5 w-5" />,
      label: "Aura Earned",
      value: stats.total_aura_earned.toLocaleString(),
      color: "text-amber-400",
    },
    {
      icon: <Flame className="h-5 w-5" />,
      label: "Aura Given",
      value: stats.total_aura_given.toLocaleString(),
      color: "text-rose-400",
    },
    {
      icon: <MessageSquare className="h-5 w-5" />,
      label: "Messages Sent",
      value: stats.total_messages_sent.toLocaleString(),
      color: "text-cyan-400",
    },
    {
      icon: <Smile className="h-5 w-5" />,
      label: "Emotes Sent",
      value: stats.total_emotes_sent.toLocaleString(),
      color: "text-pink-400",
    },
    {
      icon: <Trophy className="h-5 w-5" />,
      label: "Longest Stream",
      value: formatDuration(stats.longest_stream_seconds),
      color: "text-yellow-400",
    },
    {
      icon: <Zap className="h-5 w-5" />,
      label: "Biggest Aura Drop",
      value: stats.biggest_aura_drop.toLocaleString(),
      color: "text-orange-400",
    },
  ]

  return (
    <div className="mx-auto max-w-3xl px-6 py-8">
      <h1 className="mb-6 font-display text-2xl font-bold text-foreground">Your Stats</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {statCards.map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-border/40 bg-card/50 p-4"
          >
            <div className={`mb-2 ${stat.color}`}>{stat.icon}</div>
            <p className="font-display text-2xl font-bold text-foreground">{stat.value}</p>
            <p className="text-xs text-muted-foreground">{stat.label}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
}
