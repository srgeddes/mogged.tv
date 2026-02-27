import { Navbar } from "@/components/common/navbar"
import { Hero } from "@/components/landing/hero"
import { Features } from "@/components/landing/features"
import { StreamPreview } from "@/components/landing/stream-preview"
import { CTA } from "@/components/landing/cta"

export function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <Hero />
      <Features />
      <StreamPreview />
      <CTA />

      {/* Footer */}
      <footer className="border-t border-border/30 py-8">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <p className="font-mono text-xs text-muted-foreground/40">
            mogged.tv &mdash; Zoom is mid. Get mogged.
          </p>
        </div>
      </footer>
    </div>
  )
}
