import { Link } from "react-router-dom"
import { motion } from "framer-motion"
import { Marquee } from "@/components/magicui/marquee"
import { HoverBorderGradient } from "@/components/aceternity/hover-border-gradient"
import { ArrowRight } from "lucide-react"

const marqueeItems = [
  "No more boring meetings",
  "Zoom is mid",
  "Get mogged",
  "Stream like you mean it",
  "Your aura is showing",
  "Built different",
  "Private by default",
  "WebRTC supremacy",
]

export function CTA() {
  return (
    <section className="relative overflow-hidden py-32">
      {/* Marquee background */}
      <div className="pointer-events-none absolute inset-0 flex items-center opacity-[0.03]">
        <Marquee className="[--duration:30s]" repeat={6}>
          {marqueeItems.map((item) => (
            <span
              key={item}
              className="mx-8 font-display text-7xl font-black uppercase tracking-tight text-foreground"
            >
              {item}
            </span>
          ))}
        </Marquee>
      </div>

      <div className="relative mx-auto max-w-4xl px-6 text-center">
        {/* Ambient glow */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-64 w-64 rounded-full bg-primary/10 blur-[120px]" />

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7 }}
        >
          <h2 className="font-display text-5xl font-black tracking-tight text-foreground md:text-6xl lg:text-7xl">
            Stop being boring.
          </h2>
          <p className="mt-6 text-lg text-muted-foreground md:text-xl">
            Your friends are waiting. Your stream is ready. The only thing missing is you.
          </p>

          <div className="mt-12 flex justify-center">
            <Link to="/login">
              <HoverBorderGradient
                containerClassName="rounded-full"
                className="flex items-center gap-2 bg-card px-8 py-3 font-display text-base font-semibold"
              >
                Get Started
                <ArrowRight className="h-4 w-4" />
              </HoverBorderGradient>
            </Link>
          </div>

          <p className="mt-16 font-mono text-xs tracking-widest text-muted-foreground/30 uppercase">
            Built because Zoom is mid
          </p>
        </motion.div>
      </div>
    </section>
  )
}
