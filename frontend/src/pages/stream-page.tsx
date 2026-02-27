import { useState, useEffect } from "react"
import { useParams, useLocation, useNavigate } from "react-router-dom"
import { Tv } from "lucide-react"
import { useAuth } from "@/hooks/use-auth"
import { useStreamActions } from "@/hooks/use-streams"
import { StreamRoom } from "@/components/streams/stream-room"
import { Button } from "@/components/ui/button"
import type { Stream } from "@/types"

interface LocationState {
  token?: string
  livekitUrl?: string
  stream?: Stream
}

export function StreamPage() {
  const { username } = useParams<{ username: string }>()
  const location = useLocation()
  const navigate = useNavigate()
  const { user } = useAuth()
  const { joinStream, getLiveStreamByUsername } = useStreamActions()

  const state = location.state as LocationState | null

  const [token, setToken] = useState<string | null>(state?.token ?? null)
  const [serverUrl, setServerUrl] = useState<string | null>(state?.livekitUrl ?? null)
  const [stream, setStream] = useState<Stream | null>(state?.stream ?? null)
  const [isLoading, setIsLoading] = useState(!state?.token)
  const [notLive, setNotLive] = useState(false)

  useEffect(() => {
    if (token && serverUrl && stream) return
    if (!username) return

    let cancelled = false

    async function connect() {
      const liveStream = await getLiveStreamByUsername(username!)
      if (cancelled) return

      if (!liveStream) {
        setNotLive(true)
        setIsLoading(false)
        return
      }

      const result = await joinStream(liveStream.id)
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
  }, [username, token, serverUrl, stream, joinStream, getLiveStreamByUsername])

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

  const isHost = user?.id === stream.host_id

  return (
    <StreamRoom
      token={token}
      serverUrl={serverUrl}
      stream={stream}
      isHost={isHost}
    />
  )
}
