import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Tv } from "lucide-react"
import { useAuth } from "@/hooks/use-auth"
import { useStreamActions } from "@/hooks/use-streams"
import { StreamRoom } from "@/components/streams/stream-room"
import { Button } from "@/components/ui/button"
import type { Stream } from "@/types"

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api"

export function StreamPage() {
  const { username, slug } = useParams<{ username: string; slug?: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const { joinStream, getLiveStreamByUsername, getLiveStreamBySlug } = useStreamActions()

  const [token, setToken] = useState<string | null>(null)
  const [serverUrl, setServerUrl] = useState<string | null>(null)
  const [stream, setStream] = useState<Stream | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [notLive, setNotLive] = useState(false)

  const isHost = user != null && user.id === stream?.host_id

  useEffect(() => {
    if (!username) return

    let cancelled = false

    async function connect() {
      const liveStream = slug
        ? await getLiveStreamBySlug(username!, slug)
        : await getLiveStreamByUsername(username!)
      if (cancelled) return

      if (!liveStream) {
        setNotLive(true)
        setIsLoading(false)
        return
      }

      // If not logged in and stream isn't public, redirect to login
      if (!user && liveStream.access_level !== "public") {
        navigate("/login", { replace: true })
        return
      }

      const result = await joinStream(liveStream.id, slug ?? undefined)
      if (cancelled) return

      if (!result) {
        setIsLoading(false)
        return
      }

      setToken(result.token)
      setServerUrl(result.livekit_url)
      setStream(result.stream)
      setIsLoading(false)
    }

    connect()
    return () => {
      cancelled = true
    }
  }, [username, slug, user, joinStream, getLiveStreamByUsername, getLiveStreamBySlug, navigate])

  // Confirmation dialog when host tries to close/refresh the tab
  useEffect(() => {
    if (!isHost) return
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault()
    }
    window.addEventListener("beforeunload", handler)
    return () => window.removeEventListener("beforeunload", handler)
  }, [isHost])

  // End the stream when the host's tab closes
  useEffect(() => {
    if (!isHost || !stream) return
    const handler = () => {
      const authToken = localStorage.getItem("mogged_token")
      fetch(`${API_BASE}/streams/${stream.id}/end`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${authToken}`,
        },
        keepalive: true,
      })
    }
    window.addEventListener("pagehide", handler)
    return () => window.removeEventListener("pagehide", handler)
  }, [isHost, stream])

  if (notLive) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="text-center">
          <Tv className="mx-auto mb-4 h-12 w-12 text-muted-foreground/40" />
          <h1 className="font-display text-xl font-semibold text-foreground">
            {username} isn&apos;t live
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Check back later or go find someone who&apos;s actually mogging.
          </p>
          <Button
            variant="outline"
            className="mt-6"
            onClick={() => navigate("/home/feed")}
          >
            Back to feed
          </Button>
        </div>
      </div>
    )
  }

  if (isLoading || !token || !serverUrl || !stream) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="text-center">
          <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Joining stream...</p>
        </div>
      </div>
    )
  }

  return (
    <StreamRoom
      token={token}
      serverUrl={serverUrl}
      stream={stream}
      isHost={isHost}
    />
  )
}
