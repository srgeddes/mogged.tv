import {
  TrackToggle,
  useLocalParticipant,
} from "@livekit/components-react"
import { Track } from "livekit-client"
import { useNavigate } from "react-router-dom"
import { motion } from "framer-motion"
import { Camera, CameraOff, Mic, MicOff, MonitorUp, MonitorOff, PhoneOff } from "lucide-react"
import { useStreamActions } from "@/hooks/use-streams"

interface StreamControlsProps {
  streamId: string
}

const toggleBase =
  "flex h-10 w-10 items-center justify-center rounded-full backdrop-blur-sm transition-colors lk-button-icon"

const toggleActiveClass = `${toggleBase} bg-primary/40 text-white`

const toggleInactiveClass = `${toggleBase} bg-white/8 text-white/60 hover:bg-white/15 hover:text-white`

const springTransition = { type: "spring" as const, stiffness: 400, damping: 22 }

function DisabledDot() {
  return (
    <span className="absolute -right-0.5 -top-0.5 flex h-2.5 w-2.5 items-center justify-center">
      <span className="h-2.5 w-2.5 rounded-full bg-live ring-2 ring-background" />
    </span>
  )
}

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
      <motion.div
        className="relative"
        whileHover={{ scale: 1.06 }}
        whileTap={{ scale: 0.92 }}
        transition={springTransition}
      >
        <TrackToggle
          source={Track.Source.Camera}
          showIcon={false}
          className={isCameraEnabled ? toggleActiveClass : toggleInactiveClass}
        >
          {isCameraEnabled ? <Camera className="h-5 w-5" /> : <CameraOff className="h-5 w-5" />}
        </TrackToggle>
        {!isCameraEnabled && <DisabledDot />}
      </motion.div>

      <motion.div
        className="relative"
        whileHover={{ scale: 1.06 }}
        whileTap={{ scale: 0.92 }}
        transition={springTransition}
      >
        <TrackToggle
          source={Track.Source.Microphone}
          showIcon={false}
          className={isMicrophoneEnabled ? toggleActiveClass : toggleInactiveClass}
        >
          {isMicrophoneEnabled ? <Mic className="h-5 w-5" /> : <MicOff className="h-5 w-5" />}
        </TrackToggle>
        {!isMicrophoneEnabled && <DisabledDot />}
      </motion.div>

      <motion.div
        className="relative"
        whileHover={{ scale: 1.06 }}
        whileTap={{ scale: 0.92 }}
        transition={springTransition}
      >
        <TrackToggle
          source={Track.Source.ScreenShare}
          showIcon={false}
          className={isScreenShareEnabled ? toggleActiveClass : toggleInactiveClass}
        >
          {isScreenShareEnabled ? <MonitorOff className="h-5 w-5" /> : <MonitorUp className="h-5 w-5" />}
        </TrackToggle>
      </motion.div>

      <motion.button
        onClick={handleEndStream}
        whileHover={{ scale: 1.04 }}
        whileTap={{ scale: 0.95 }}
        className="flex items-center gap-2 rounded-full bg-live px-4 py-2 text-sm font-medium text-live-foreground backdrop-blur-sm transition-colors hover:bg-live/90"
      >
        <PhoneOff className="h-4 w-4" />
        End Stream
      </motion.button>
    </div>
  )
}
