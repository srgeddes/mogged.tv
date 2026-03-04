import { useState, useMemo } from "react"
import { Radio, Clock, Tv } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useLiveStreams, useRecentStreams } from "@/hooks/use-streams"
import { useAuth } from "@/hooks/use-auth"
import { StreamCard } from "@/components/streams/stream-card"
import { GoLiveDialog } from "@/components/streams/go-live-dialog"
import { SearchFilterBar } from "@/components/common/search-filter-bar"
import { BorderBeam } from "@/components/magicui/border-beam"
import type { Stream, StreamAccessLevel } from "@/types"

type FilterValue = "all" | StreamAccessLevel

const FILTER_OPTIONS = [
  { value: "all", label: "All" },
  { value: "public", label: "Public" },
  { value: "friends", label: "Friends" },
  { value: "org_only", label: "Org" },
  { value: "link_only", label: "Private" },
]

const EMPTY_QUIPS = [
  "Everyone's touching grass. Go live and mog them.",
]

function getRandomQuip() {
  return EMPTY_QUIPS[Math.floor(Math.random() * EMPTY_QUIPS.length)]
}

function filterStreams(
  streams: Stream[],
  searchQuery: string,
  activeFilter: FilterValue,
): Stream[] {
  let filtered = streams

  if (activeFilter !== "all") {
    filtered = filtered.filter((s) => s.access_level === activeFilter)
  }

  if (searchQuery.trim()) {
    const q = searchQuery.toLowerCase()
    filtered = filtered.filter(
      (s) =>
        s.title.toLowerCase().includes(q) ||
        (s.host_display_name?.toLowerCase().includes(q) ?? false) ||
        (s.host_username?.toLowerCase().includes(q) ?? false) ||
        (s.description?.toLowerCase().includes(q) ?? false),
    )
  }

  return filtered
}

const PAST_PAGE_SIZE = 8

export function FeedPage() {
  const { data: liveStreams, isLoading: liveLoading, refetch: refetchLive } = useLiveStreams()
  const { data: recentStreams, isLoading: recentLoading } = useRecentStreams()
  const { user } = useAuth()

  const [searchQuery, setSearchQuery] = useState("")
  const [activeFilter, setActiveFilter] = useState<FilterValue>("all")
  const [showCount, setShowCount] = useState(PAST_PAGE_SIZE)

  const myActiveStream = liveStreams?.find((s) => s.host_id === user?.id)

  const allLive = liveStreams ?? []
  const allRecent = recentStreams ?? []

  const filteredLive = useMemo(
    () => filterStreams(allLive, searchQuery, activeFilter),
    [allLive, searchQuery, activeFilter],
  )

  const filteredRecent = useMemo(
    () => filterStreams(allRecent, searchQuery, activeFilter),
    [allRecent, searchQuery, activeFilter],
  )

  const visibleRecent = filteredRecent.slice(0, showCount)
  const hasMoreRecent = filteredRecent.length > showCount

  const greeting = user?.display_name ?? user?.username ?? "anon"
  const hasFilters = searchQuery.trim() !== "" || activeFilter !== "all"

  return (
    <div className="py-8">
      {/* Hero Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-foreground">
            Sup, {greeting}
          </h1>
        </div>
        {myActiveStream ? (
          <Button
            className="gap-2 bg-live text-live-foreground hover:bg-live/90"
            onClick={() => window.open(`/${user!.username}`, "mogged-stream")}
          >
            <Radio className="h-4 w-4 animate-pulse" />
            View Stream
          </Button>
        ) : (
          <GoLiveDialog
            trigger={
              <Button className="gap-2">
                <Radio className="h-4 w-4" />
                Go Live
              </Button>
            }
            onCreated={refetchLive}
          />
        )}
      </div>

      {/* Live Now / Empty State */}
      <section className="mb-10">
        {liveLoading ? (
          <>
            <div className="mb-4 flex items-center gap-2">
              <Radio className="h-5 w-5 text-live" />
              <h2 className="font-display text-lg font-semibold text-foreground">Live Now</h2>
            </div>
            <LoadingSkeleton count={2} size="lg" />
          </>
        ) : allLive.length > 0 ? (
          <>
            <div className="mb-4 flex items-center gap-2">
              <Radio className="h-5 w-5 animate-pulse text-live" />
              <h2 className="font-display text-lg font-semibold text-foreground">Live Now</h2>
              <span className="rounded-full bg-live/20 px-2 py-0.5 text-xs font-medium text-live">
                {filteredLive.length}
              </span>
            </div>
            {filteredLive.length > 0 ? (
              <div className="grid gap-4 sm:grid-cols-2">
                {filteredLive.map((stream) => (
                  <div key={stream.id} className="relative overflow-hidden rounded-xl">
                    <StreamCard stream={stream} size="lg" openInNewWindow={stream.host_id === user?.id} />
                    <BorderBeam
                      colorFrom="hsl(0 84% 60%)"
                      colorTo="hsl(0 84% 40%)"
                      duration={8}
                      size={150}
                    />
                  </div>
                ))}
              </div>
            ) : (
              <p className="py-6 text-center text-sm text-muted-foreground">
                No live streams match your filters.
              </p>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center justify-center rounded-xl bg-card/30 py-14 text-center">
            <Tv className="mb-4 h-12 w-12 text-muted-foreground/30" />
            <h3 className="font-display text-lg font-semibold text-foreground">It's quiet... too quiet.</h3>
            <p className="mt-1 max-w-sm text-sm text-muted-foreground">{getRandomQuip()}</p>
            {!myActiveStream && (
              <div className="mt-5">
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
            )}
          </div>
        )}
      </section>

      {/* Search & Filter */}
      <div className="mb-6">
        <SearchFilterBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          activeFilter={activeFilter}
          onFilterChange={(f) => {
            setActiveFilter(f as FilterValue)
            setShowCount(PAST_PAGE_SIZE)
          }}
          filterOptions={FILTER_OPTIONS}
          placeholder="Search by title, host, or description..."
        />
      </div>

      {/* Past Streams */}
      <section>
        <div className="mb-4 flex items-center gap-2">
          <Clock className="h-5 w-5 text-muted-foreground" />
          <h2 className="font-display text-lg font-semibold text-foreground">Past Streams</h2>
          {!recentLoading && (
            <span className="text-xs text-muted-foreground">({filteredRecent.length})</span>
          )}
        </div>

        {recentLoading ? (
          <LoadingSkeleton count={4} size="sm" />
        ) : visibleRecent.length > 0 ? (
          <>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {visibleRecent.map((stream) => (
                <StreamCard key={stream.id} stream={stream} size="sm" />
              ))}
            </div>
            {hasMoreRecent && (
              <div className="mt-6 flex justify-center">
                <Button
                  variant="outline"
                  onClick={() => setShowCount((c) => c + PAST_PAGE_SIZE)}
                >
                  Show more
                </Button>
              </div>
            )}
          </>
        ) : hasFilters ? (
          <p className="py-10 text-center text-sm text-muted-foreground">
            No streams match your search.
          </p>
        ) : (
          <p className="py-10 text-center text-sm text-muted-foreground">
            No one&apos;s streamed yet. Time to start mogging.
          </p>
        )}
      </section>
    </div>
  )
}

function LoadingSkeleton({ count, size }: { count: number; size: "sm" | "lg" }) {
  const heights = { sm: "h-32", lg: "h-56" }
  const cols = { sm: "sm:grid-cols-2 lg:grid-cols-3", lg: "sm:grid-cols-2" }

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
