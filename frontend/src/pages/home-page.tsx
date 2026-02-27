import { Navbar } from "@/components/common/navbar"
import { Particles } from "@/components/magicui/particles"

export function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <Particles className="absolute inset-0" quantity={30} color="#4a9eda" staticity={60} />

      <div className="relative z-10 flex min-h-screen items-center justify-center pt-16">
        <div className="text-center">
          <p className="font-display text-4xl font-bold tracking-tight text-foreground">
            You&apos;re in.
          </p>
          <p className="mt-4 text-lg text-muted-foreground">
            Streams coming soon. Hang tight.
          </p>
          <div className="mt-8 inline-flex items-center gap-2 rounded-full border border-border/40 bg-card/50 px-4 py-2 text-sm text-muted-foreground backdrop-blur-sm">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-500 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
            </span>
            Connected
          </div>
        </div>
      </div>
    </div>
  )
}
