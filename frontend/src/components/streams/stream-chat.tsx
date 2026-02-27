import { useState, useRef, useEffect } from "react"
import {
  useChat,
  useParticipants,
  useSpeakingParticipants,
} from "@livekit/components-react"
import { Send, Mic } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

function ParticipantList() {
  const participants = useParticipants()
  const speakingParticipants = useSpeakingParticipants()
  const speakingIds = new Set(speakingParticipants.map((p) => p.identity))

  return (
    <div className="border-b border-border/40 px-4 py-2">
      <div className="flex flex-wrap gap-1.5">
        {participants.map((p) => (
          <span
            key={p.identity}
            className={cn(
              "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium transition-colors",
              speakingIds.has(p.identity)
                ? "bg-emerald-500/20 text-emerald-400"
                : "bg-white/5 text-muted-foreground",
            )}
          >
            {speakingIds.has(p.identity) && <Mic className="h-2.5 w-2.5" />}
            {p.name || p.identity}
          </span>
        ))}
      </div>
    </div>
  )
}

export function StreamChat() {
  const { chatMessages, send, isSending } = useChat()
  const [message, setMessage] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [chatMessages.length])

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    const text = message.trim()
    if (!text) return
    setMessage("")
    await send(text)
  }

  return (
    <div className="flex h-full flex-col border-l border-border/40 bg-card/30">
      <div className="border-b border-border/40 px-4 py-3">
        <h2 className="text-sm font-semibold text-foreground">Chat</h2>
      </div>

      <ParticipantList />

      <div className="flex-1 overflow-y-auto px-4 py-3">
        {chatMessages.length === 0 ? (
          <p className="text-center text-xs text-muted-foreground/50">
            No messages yet. Say something.
          </p>
        ) : (
          <div className="space-y-2">
            {chatMessages.map((msg, i) => (
              <div key={i} className="text-sm">
                <span className="font-mono text-xs font-medium text-primary-foreground/80">
                  {msg.from?.name || msg.from?.identity || "anon"}
                </span>
                <span className="ml-2 text-xs text-muted-foreground">
                  {new Date(msg.timestamp).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
                <p className="mt-0.5 break-words text-xs text-foreground/80">{msg.message}</p>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <form onSubmit={handleSend} className="border-t border-border/40 p-3">
        <div className="flex gap-2">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Send a message..."
            className="h-8 text-xs"
            maxLength={500}
          />
          <Button
            type="submit"
            size="icon"
            disabled={isSending || !message.trim()}
            className="h-8 w-8 shrink-0"
          >
            <Send className="h-3.5 w-3.5" />
          </Button>
        </div>
      </form>
    </div>
  )
}
