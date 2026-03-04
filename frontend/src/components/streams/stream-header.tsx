import { Radio, Users } from "lucide-react"
import {
  useParticipants,
  useConnectionState,
  ConnectionQualityIndicator,
  useRemoteParticipants,
} from "@livekit/components-react"
import { ConnectionState } from "livekit-client"
import { AnimatePresence, motion } from "framer-motion"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import type { Stream } from "@/types"

interface StreamHeaderProps {
  stream: Stream
}

export function StreamHeader({ stream }: StreamHeaderProps) {
  const participants = useParticipants()
  const remoteParticipants = useRemoteParticipants()
  const connectionState = useConnectionState()
  const viewerCount = remoteParticipants.length

  const hostParticipant = participants.find(
    (p) => p.identity === stream.host_id,
  )

  return (
    <div className="absolute inset-x-0 top-0 z-10 flex items-center justify-between bg-gradient-to-b from-black/70 to-transparent px-5 py-4">
      <div className="flex items-center gap-3">
        <Avatar className="h-8 w-8">
          <AvatarFallback className="bg-primary/30 text-xs text-primary-foreground">
            {stream.host_display_name?.[0] ?? stream.host_username?.[0] ?? "?"}
          </AvatarFallback>
        </Avatar>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-sm font-semibold text-white">{stream.title}</h1>
            {hostParticipant && (
              <ConnectionQualityIndicator
                participant={hostParticipant}
                className="text-white/60 [&_svg]:h-3.5 [&_svg]:w-3.5"
              />
            )}
          </div>
          <p className="text-xs text-white/60">
            {stream.host_display_name ?? stream.host_username}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <span className="flex items-center gap-1.5 text-xs text-white/70">
          <Users className="h-3.5 w-3.5" />
          <AnimatePresence mode="popLayout" initial={false}>
            <motion.span
              key={viewerCount}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
            >
              {viewerCount}
            </motion.span>
          </AnimatePresence>
        </span>
        {connectionState === ConnectionState.Connected && (
          <span className="flex items-center gap-1.5 rounded-full bg-live px-2.5 py-1 text-xs font-semibold text-live-foreground">
            <Radio className="h-3 w-3 animate-pulse" />
            LIVE
          </span>
        )}
      </div>
    </div>
  )
}
