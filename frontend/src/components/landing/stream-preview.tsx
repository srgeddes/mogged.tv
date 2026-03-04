import { useState, useEffect, useRef, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { BorderBeam } from "@/components/magicui/border-beam"
import {
  Heart,
  Volume2,
  Mic,
  Users,
  Send,
  Radio,
  Camera,
  MonitorUp,
  Flame,
} from "lucide-react"
import { cn } from "@/lib/utils"

// --- Data ---

interface ChatMsg {
  id: number
  user: string
  color: string
  msg: string
  type: "text" | "aura" | "system"
}

const USERS = [
  { name: "riley", color: "#fb923c" },
  { name: "xander", color: "#4a9eda" },
  { name: "ghost_404", color: "#e879f9" },
  { name: "nyx", color: "#34d399" },
  { name: "devin", color: "#f472b6" },
  { name: "ash", color: "#a78bfa" },
  { name: "kai", color: "#fbbf24" },
]

const BOT_MESSAGES: { user: string; msg: string; type: "text" | "aura" }[] = [
  { user: "xander", msg: "yo this standup is actually fire for once", type: "text" },
  { user: "ghost_404", msg: "wait who broke staging", type: "text" },
  { user: "nyx", msg: "just shipped the fix, we're good", type: "text" },
  { user: "devin", msg: "the aura is unmatched rn", type: "text" },
  { user: "ash", msg: "our zoom replacement is literally streaming lmao", type: "text" },
  { user: "kai", msg: "this is way better than a google meet", type: "text" },
  { user: "xander", msg: "someone demo the new dashboard", type: "text" },
  { user: "ghost_404", msg: "riley's screen share is clean", type: "text" },
  { user: "nyx", msg: "+50 aura to riley for that deploy", type: "aura" },
  { user: "devin", msg: "can we do all standups like this", type: "text" },
  { user: "ash", msg: "this is the future of meetings fr", type: "text" },
  { user: "kai", msg: "zoom could literally never", type: "text" },
  { user: "xander", msg: "+25 aura to nyx for the hotfix", type: "aura" },
  { user: "ghost_404", msg: "we're actually getting things done lol", type: "text" },
  { user: "nyx", msg: "shipping while streaming, peak productivity", type: "text" },
  { user: "devin", msg: "the vibes in here are immaculate", type: "text" },
]

const SPEAKING_CYCLE_MS = 2000

// --- Fake code for the "screen share" ---

const CODE_LINES = [
  "async def deploy_to_prod(service: str):",
  '    log.info(f"deploying {service}...")',
  "    build = await run_build(service)",
  "    if not build.success:",
  '        raise DeployError("build failed")',
  "",
  "    await push_image(build.tag)",
  "    await rollout(service, build.tag)",
  '    log.info(f"{service} deployed ✓")',
  "",
  "    notify_team(",
  '        channel="#deploys",',
  '        msg=f"{service} is live 🚀",',
  "    )",
  "    return build",
]

// --- Components ---

function FakeCodeEditor() {
  const [visibleLines, setVisibleLines] = useState(0)

  useEffect(() => {
    if (visibleLines >= CODE_LINES.length) {
      const timeout = setTimeout(() => setVisibleLines(0), 3000)
      return () => clearTimeout(timeout)
    }
    const timeout = setTimeout(
      () => setVisibleLines((v) => v + 1),
      150 + Math.random() * 250,
    )
    return () => clearTimeout(timeout)
  }, [visibleLines])

  return (
    <div className="absolute inset-0 flex flex-col bg-[#0d1117]">
      {/* Editor title bar */}
      <div className="flex items-center gap-2 border-b border-white/5 px-4 py-2">
        <div className="flex gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-red-500/60" />
          <span className="h-2.5 w-2.5 rounded-full bg-yellow-500/60" />
          <span className="h-2.5 w-2.5 rounded-full bg-green-500/60" />
        </div>
        <span className="ml-2 font-mono text-[10px] text-white/30">
          deploy.py — mogged-infra
        </span>
      </div>

      {/* Code area */}
      <div className="flex-1 overflow-hidden px-4 py-3">
        <pre className="font-mono text-[11px] leading-relaxed md:text-xs">
          {CODE_LINES.slice(0, visibleLines).map((line, i) => (
            <div key={i} className="flex">
              <span className="mr-4 inline-block w-4 select-none text-right text-white/15">
                {i + 1}
              </span>
              <span className="text-[#c9d1d9]">
                {colorize(line)}
              </span>
            </div>
          ))}
          {visibleLines < CODE_LINES.length && (
            <div className="flex">
              <span className="mr-4 inline-block w-4 select-none text-right text-white/15">
                {visibleLines + 1}
              </span>
              <span className="inline-block h-4 w-1.5 animate-pulse bg-primary/70" />
            </div>
          )}
        </pre>
      </div>
    </div>
  )
}

function colorize(line: string) {
  // Very simple syntax highlighting
  return line
    .split(/(def |async |await |if |not |return |raise |f"|"[^"]*"|#[^ ]*|\b(?:True|False|None)\b)/)
    .map((part, i) => {
      if (/^(def |async |await |if |not |return |raise )$/.test(part))
        return <span key={i} className="text-[#ff7b72]">{part}</span>
      if (/^f"/.test(part) || /^"/.test(part))
        return <span key={i} className="text-[#a5d6ff]">{part}</span>
      if (/^#/.test(part))
        return <span key={i} className="text-[#7ee787]">{part}</span>
      return <span key={i}>{part}</span>
    })
}

function ParticipantPills() {
  const [speakingIdx, setSpeakingIdx] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setSpeakingIdx(Math.floor(Math.random() * USERS.length))
    }, SPEAKING_CYCLE_MS)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="border-b border-border/40 px-4 py-2">
      <div className="flex flex-wrap gap-1.5">
        {USERS.map((u, i) => (
          <span
            key={u.name}
            className={cn(
              "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium transition-all duration-300",
              i === speakingIdx
                ? "bg-success/20 text-success"
                : "bg-white/5 text-muted-foreground",
            )}
          >
            {i === speakingIdx && <Mic className="h-2.5 w-2.5" />}
            {u.name}
          </span>
        ))}
      </div>
    </div>
  )
}

function HeartBurst({ x, y }: { x: number; y: number }) {
  return (
    <motion.div
      initial={{ opacity: 1, scale: 0.5, x, y }}
      animate={{ opacity: 0, scale: 1.5, y: y - 60 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.7, ease: "easeOut" }}
      className="pointer-events-none absolute z-20"
    >
      <Heart className="h-5 w-5 fill-pink-400 text-pink-400" />
    </motion.div>
  )
}

function LiveChat() {
  const [messages, setMessages] = useState<ChatMsg[]>([])
  const [input, setInput] = useState("")
  const msgCounter = useRef(0)
  const botIdx = useRef(0)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll on new messages
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" })
  }, [messages.length])

  // Bot message loop
  useEffect(() => {
    const interval = setInterval(() => {
      const botMsg = BOT_MESSAGES[botIdx.current % BOT_MESSAGES.length]
      const user = USERS.find((u) => u.name === botMsg.user) ?? USERS[0]
      const id = ++msgCounter.current
      setMessages((prev) => [
        ...prev.slice(-30),
        { id, user: user.name, color: user.color, msg: botMsg.msg, type: botMsg.type },
      ])
      botIdx.current++
    }, 2500 + Math.random() * 1500)
    return () => clearInterval(interval)
  }, [])

  const handleSend = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault()
      const text = input.trim()
      if (!text) return
      setInput("")
      const id = ++msgCounter.current
      setMessages((prev) => [
        ...prev.slice(-30),
        { id, user: "you", color: "#4a9eda", msg: text, type: "text" },
      ])
    },
    [input],
  )

  return (
    <div className="flex w-full flex-col border-t border-border/40 md:w-80 md:border-l md:border-t-0">
      {/* Chat header */}
      <div className="flex items-center justify-between border-b border-border/40 px-4 py-3">
        <span className="text-sm font-semibold text-foreground">Chat</span>
        <span className="text-xs text-muted-foreground">{USERS.length} online</span>
      </div>

      {/* Participant pills */}
      <ParticipantPills />

      {/* Messages */}
      <div ref={scrollRef} className="h-56 flex-1 overflow-y-auto px-4 py-3 md:h-auto">
        <div className="space-y-2">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="text-sm"
              >
                {msg.type === "aura" ? (
                  <span className="flex items-center gap-1 text-xs text-amber-400/80">
                    <Flame className="h-3 w-3" />
                    <span className="font-mono font-semibold" style={{ color: msg.color }}>
                      {msg.user}
                    </span>
                    <span className="text-amber-400/60">: {msg.msg}</span>
                  </span>
                ) : (
                  <>
                    <span className="font-mono font-semibold" style={{ color: msg.color }}>
                      {msg.user}
                    </span>
                    <span className="text-muted-foreground">: {msg.msg}</span>
                  </>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* Chat input — actually works */}
      <form onSubmit={handleSend} className="border-t border-border/40 p-3">
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Try sending a message..."
            maxLength={200}
            className="h-8 flex-1 rounded-lg border border-border/40 bg-background/50 px-3 text-xs text-foreground placeholder:text-muted-foreground/40 focus:border-primary/50 focus:outline-none"
          />
          <button
            type="submit"
            disabled={!input.trim()}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/20 text-primary transition-colors hover:bg-primary/30 disabled:opacity-30"
          >
            <Send className="h-3.5 w-3.5" />
          </button>
        </div>
      </form>
    </div>
  )
}

// --- Main ---

export function StreamPreview() {
  const [hearts, setHearts] = useState<{ id: number; x: number; y: number }[]>([])
  const [viewerCount, setViewerCount] = useState(7)
  const heartCounter = useRef(0)

  // Fluctuate viewer count
  useEffect(() => {
    const interval = setInterval(() => {
      setViewerCount((v) => {
        const delta = Math.random() > 0.5 ? 1 : -1
        return Math.max(5, Math.min(12, v + delta))
      })
    }, 4000)
    return () => clearInterval(interval)
  }, [])

  const spawnHeart = useCallback((e: React.MouseEvent) => {
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
    const x = e.clientX - rect.left - 10
    const y = e.clientY - rect.top - 10
    const id = ++heartCounter.current
    setHearts((prev) => [...prev, { id, x, y }])
    setTimeout(() => setHearts((prev) => prev.filter((h) => h.id !== id)), 800)
  }, [])

  return (
    <section id="demo" className="relative py-32 scroll-mt-8">
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
            Try it. This is real.
          </h2>
          <p className="mt-3 text-sm text-muted-foreground">
            Type in the chat. It works.
          </p>
        </motion.div>

        {/* Interactive stream UI */}
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
            {/* Video / screen share area */}
            <div className="relative flex-1">
              <div className="relative aspect-video overflow-hidden">
                <FakeCodeEditor />

                {/* Overlay — header bar */}
                <div className="absolute inset-x-0 top-0 z-10 flex items-center justify-between bg-gradient-to-b from-black/60 to-transparent px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/30 text-[10px] font-bold text-primary-foreground">
                      R
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-white">Sprint Demo — Deploy Pipeline</p>
                      <p className="text-[10px] text-white/50">riley</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="flex items-center gap-1 text-[10px] text-white/60">
                      <Users className="h-3 w-3" />
                      {viewerCount}
                    </span>
                    <span className="flex items-center gap-1.5 rounded-full bg-live px-2 py-0.5 text-[10px] font-semibold text-live-foreground">
                      <Radio className="h-2.5 w-2.5 animate-pulse" />
                      LIVE
                    </span>
                  </div>
                </div>

                {/* Heart bursts */}
                <AnimatePresence>
                  {hearts.map((h) => (
                    <HeartBurst key={h.id} x={h.x} y={h.y} />
                  ))}
                </AnimatePresence>
              </div>

              {/* Controls bar */}
              <div className="flex items-center justify-center gap-2 border-t border-border/40 bg-card/80 px-4 py-2.5 backdrop-blur-sm">
                <button className="rounded-full bg-white/10 p-2 text-white/70 transition-colors hover:bg-white/20">
                  <Camera className="h-4 w-4" />
                </button>
                <button className="rounded-full bg-white/10 p-2 text-white/70 transition-colors hover:bg-white/20">
                  <Mic className="h-4 w-4" />
                </button>
                <button className="rounded-full bg-white/10 p-2 text-white/70 transition-colors hover:bg-white/20">
                  <MonitorUp className="h-4 w-4" />
                </button>
                <button className="rounded-full bg-white/10 p-2 text-white/70 transition-colors hover:bg-white/20">
                  <Volume2 className="h-4 w-4" />
                </button>
                <button
                  onClick={spawnHeart}
                  className="relative rounded-full bg-white/10 p-2 text-pink-400 transition-colors hover:bg-pink-500/20"
                >
                  <Heart className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Live interactive chat */}
            <LiveChat />
          </div>
        </motion.div>
      </div>
    </section>
  )
}
