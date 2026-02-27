import {
  TrackToggle,
  DisconnectButton,
  useLocalParticipant,
} from "@livekit/components-react"
import { Track } from "livekit-client"
import { Camera, CameraOff, Mic, MicOff, MonitorUp, MonitorOff, PhoneOff } from "lucide-react"
import { useStreamActions } from "@/hooks/use-streams"
import { useNavigate } from "react-router-dom"

interface StreamControlsProps {
  streamId: string
}

const toggleClass =
  "flex h-10 w-10 items-center justify-center rounded-full bg-white/10 text-white backdrop-blur-sm transition-colors hover:bg-white/20 lk-button-icon"

const toggleActiveClass =
  "flex h-10 w-10 items-center justify-center rounded-full bg-white/20 text-white backdrop-blur-sm transition-colors hover:bg-white/30 lk-button-icon"

export function StreamControls({ streamId }: StreamControlsProps) {
  const { isCameraEnabled, isMicrophoneEnabled, isScreenShareEnabled } =
    useLocalParticipant()
  const { endStream } = useStreamActions()
  const navigate = useNavigate()

  const handleEndStream = async () => {
    await endStream(streamId)
    navigate("/home/feed")
  }

  return (
    <div className="absolute inset-x-0 bottom-0 z-10 flex items-center justify-center gap-2 bg-gradient-to-t from-black/70 to-transparent px-5 py-4">
      <TrackToggle
        source={Track.Source.Camera}
        className={isCameraEnabled ? toggleActiveClass : toggleClass}
      >
        {isCameraEnabled ? <Camera className="h-5 w-5" /> : <CameraOff className="h-5 w-5" />}
      </TrackToggle>

      <TrackToggle
        source={Track.Source.Microphone}
        className={isMicrophoneEnabled ? toggleActiveClass : toggleClass}
      >
        {isMicrophoneEnabled ? <Mic className="h-5 w-5" /> : <MicOff className="h-5 w-5" />}
      </TrackToggle>

      <TrackToggle
        source={Track.Source.ScreenShare}
        className={isScreenShareEnabled ? toggleActiveClass : toggleClass}
      >
        {isScreenShareEnabled ? <MonitorOff className="h-5 w-5" /> : <MonitorUp className="h-5 w-5" />}
      </TrackToggle>

      <DisconnectButton
        onClick={handleEndStream}
        className="flex h-10 w-10 items-center justify-center rounded-full bg-red-500/80 text-white backdrop-blur-sm transition-colors hover:bg-red-500"
      >
        <PhoneOff className="h-5 w-5" />
      </DisconnectButton>
    </div>
  )
}
