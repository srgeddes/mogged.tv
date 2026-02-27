import { motion } from "framer-motion"
import { BorderBeam } from "@/components/magicui/border-beam"
import {
  Heart,
  Volume2,
  Maximize,
  PictureInPicture2,
  LogOut,
  Users,
  Send,
} from "lucide-react"

const fakeChatMessages = [
  { user: "xander", color: "#4a9eda", msg: "yo this stream is fire 🔥🔥🔥" },
  { user: "ghost_404", color: "#e879f9", msg: "the aura is UNMATCHED rn 💀" },
  { user: "nyx", color: "#34d399", msg: "bro just deployed to prod with no tests 😭" },
  { user: "riley", color: "#fb923c", msg: "no cap this is the most skibidi deploy ever 🚀" },
  { user: "devin", color: "#f472b6", msg: "absolute sigma behavior fr fr 🗿" },
  { user: "ash", color: "#a78bfa", msg: "zoom could never 💅 get mogged losers" },
]

export function StreamPreview() {
  return (
    <section className="relative py-32">
      <div className="mx-auto max-w-6xl px-6">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="mb-16 text-center"
        >
          <p className="mb-3 font-mono text-sm uppercase tracking-widest text-primary">
            The Experience
          </p>
          <h2 className="font-display text-4xl font-bold tracking-tight text-foreground md:text-5xl">
            This is what it looks like.
          </h2>
        </motion.div>

        {/* Mock stream UI */}
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.96 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="relative overflow-hidden rounded-2xl border border-border/60 bg-card"
        >
          <BorderBeam
            size={300}
            duration={12}
            colorFrom="#003153"
            colorTo="#4a9eda"
            borderWidth={1}
          />

          <div className="flex flex-col md:flex-row">
            {/* Video area */}
            <div className="relative flex-1">
              {/* Fake video feed — gradient placeholder */}
              <div className="aspect-video bg-gradient-to-br from-background via-card to-primary/10">
                {/* Overlay info */}
                <div className="absolute left-4 top-4 flex items-center gap-2">
                  <div className="flex items-center gap-1.5 rounded-md bg-red-500/90 px-2 py-0.5 text-xs font-semibold text-white">
                    <span className="h-1.5 w-1.5 rounded-full bg-white animate-pulse" />
                    LIVE
                  </div>
                  <div className="flex items-center gap-1 rounded-md bg-black/40 px-2 py-0.5 text-xs text-white/80 backdrop-blur-sm">
                    <Users className="h-3 w-3" />
                    7
                  </div>
                </div>

                {/* Streamer name */}
                <div className="absolute bottom-4 left-4 rounded-md bg-black/40 px-3 py-1 text-sm font-mono text-white/90 backdrop-blur-sm">
                  riley is streaming
                </div>

                {/* Center play indicator */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="flex h-20 w-20 items-center justify-center rounded-full border border-white/10 bg-white/5 backdrop-blur-sm">
                    <svg className="ml-1 h-8 w-8 text-white/60" viewBox="0 0 24 24" fill="currentColor">
                      <polygon points="6,3 20,12 6,21" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Controls bar */}
              <div className="flex items-center justify-center gap-3 border-t border-border/40 bg-card/80 px-4 py-3 backdrop-blur-sm">
                <button className="rounded-lg bg-secondary/50 p-2.5 text-pink-400 transition-colors hover:bg-secondary">
                  <Heart className="h-4 w-4" />
                </button>
                <button className="rounded-lg bg-secondary/50 p-2.5 text-foreground transition-colors hover:bg-secondary">
                  <Volume2 className="h-4 w-4" />
                </button>
                <button className="rounded-lg bg-secondary/50 p-2.5 text-muted-foreground transition-colors hover:bg-secondary">
                  <PictureInPicture2 className="h-4 w-4" />
                </button>
                <button className="rounded-lg bg-secondary/50 p-2.5 text-muted-foreground transition-colors hover:bg-secondary">
                  <Maximize className="h-4 w-4" />
                </button>
                <button className="rounded-lg bg-red-500/20 p-2.5 text-red-400 transition-colors hover:bg-red-500/30">
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Chat sidebar */}
            <div className="flex w-full flex-col border-t border-border/40 md:w-80 md:border-l md:border-t-0">
              {/* Chat header */}
              <div className="flex items-center justify-between border-b border-border/40 px-4 py-3">
                <span className="text-sm font-semibold text-foreground">Chat</span>
                <span className="text-xs text-muted-foreground">7 online</span>
              </div>

              {/* Messages */}
              <div className="flex-1 space-y-2.5 overflow-hidden px-4 py-3">
                {fakeChatMessages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.8 + i * 0.15, duration: 0.3 }}
                    className="text-sm"
                  >
                    <span className="font-mono font-semibold" style={{ color: msg.color }}>
                      {msg.user}
                    </span>
                    <span className="text-muted-foreground">: {msg.msg}</span>
                  </motion.div>
                ))}
              </div>

              {/* Chat input */}
              <div className="border-t border-border/40 p-3">
                <div className="flex items-center gap-2 rounded-lg border border-border/40 bg-background/50 px-3 py-2">
                  <span className="flex-1 text-sm text-muted-foreground/40">
                    Send a message...
                  </span>
                  <Send className="h-4 w-4 text-muted-foreground/30" />
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
