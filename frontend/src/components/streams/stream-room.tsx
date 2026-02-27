import {
  LiveKitRoom,
  RoomAudioRenderer,
  StartAudio,
  useConnectionState,
} from "@livekit/components-react"
import "@livekit/components-styles"
import { ConnectionState } from "livekit-client"
import { useNavigate } from "react-router-dom"
import { Wifi, WifiOff } from "lucide-react"
import { StreamHeader } from "./stream-header"
import { StreamVideo } from "./stream-video"
import { StreamControls } from "./stream-controls"
import { StreamChat } from "./stream-chat"
import type { Stream } from "@/types"

interface StreamRoomProps {
  token: string
  serverUrl: string
  stream: Stream
  isHost: boolean
}

function ConnectionOverlay() {
  const connectionState = useConnectionState()

  if (connectionState === ConnectionState.Connected) return null

  return (
    <div className="absolute inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="text-center">
        {connectionState === ConnectionState.Reconnecting ? (
          <>
            <WifiOff className="mx-auto mb-3 h-8 w-8 animate-pulse text-yellow-400" />
            <p className="text-sm font-medium text-yellow-400">Reconnecting...</p>
            <p className="mt-1 text-xs text-muted-foreground">Hold tight, we're getting you back in.</p>
          </>
        ) : (
          <>
            <Wifi className="mx-auto mb-3 h-8 w-8 animate-pulse text-muted-foreground" />
            <p className="text-sm font-medium text-foreground">Connecting...</p>
          </>
        )}
      </div>
    </div>
  )
}

export function StreamRoom({ token, serverUrl, stream, isHost }: StreamRoomProps) {
  const navigate = useNavigate()

  return (
    <LiveKitRoom
      token={token}
      serverUrl={serverUrl}
      connect={true}
      audio={isHost}
      video={isHost}
      onDisconnected={() => navigate("/home/feed")}
      className="relative flex h-screen w-screen bg-background"
    >
      {/* LiveKit built-ins: renders all remote audio, handles autoplay policy */}
      <RoomAudioRenderer />
      <StartAudio label="Click to enable audio" className="absolute left-1/2 top-4 z-50 -translate-x-1/2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-lg" />
      <ConnectionOverlay />

      {/* Video area */}
      <div className="relative flex flex-1 flex-col overflow-hidden">
        <StreamHeader stream={stream} />
        <div className="flex-1">
          <StreamVideo isHost={isHost} />
        </div>
        {isHost && <StreamControls streamId={stream.id} />}
      </div>

      {/* Chat sidebar */}
      <div className="w-80 shrink-0">
        <StreamChat />
      </div>
    </LiveKitRoom>
  )
}
