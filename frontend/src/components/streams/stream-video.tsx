import {
  useTracks,
  VideoTrack,
  FocusLayout,
} from "@livekit/components-react"
import { Track } from "livekit-client"
import { Tv } from "lucide-react"

interface StreamVideoProps {
  isHost: boolean
}

export function StreamVideo({ isHost }: StreamVideoProps) {
  const tracks = useTracks(
    [
      { source: Track.Source.Camera, withPlaceholder: true },
      { source: Track.Source.ScreenShare, withPlaceholder: false },
    ],
    { onlySubscribed: false },
  )

  const screenTrack = tracks.find(
    (t) => t.source === Track.Source.ScreenShare && t.publication?.track,
  )
  const cameraTrack = tracks.find(
    (t) => t.source === Track.Source.Camera && t.publication?.track,
  )

  const activeTrack = screenTrack ?? cameraTrack

  if (!activeTrack?.publication?.track) {
    return (
      <div className="flex h-full items-center justify-center bg-black/40">
        <div className="text-center">
          <Tv className="mx-auto mb-3 h-12 w-12 text-muted-foreground/40" />
          <p className="text-sm text-muted-foreground/60">
            {isHost ? "Turn on your camera to start streaming" : "Waiting for video..."}
          </p>
        </div>
      </div>
    )
  }

  // Screen share active + camera available: show screen share as main, camera as PiP
  if (screenTrack?.publication?.track && cameraTrack?.publication?.track) {
    return (
      <div className="relative h-full w-full bg-black">
        <FocusLayout
          trackRef={screenTrack}
          className="h-full w-full"
        />
        <div className="absolute bottom-4 right-4 h-32 w-48 overflow-hidden rounded-lg border-2 border-white/20 shadow-2xl">
          <VideoTrack
            trackRef={cameraTrack}
            className="h-full w-full object-cover"
          />
        </div>
      </div>
    )
  }

  return (
    <div className="relative h-full w-full bg-black">
      <FocusLayout
        trackRef={activeTrack}
        className="h-full w-full"
      />
    </div>
  )
}
