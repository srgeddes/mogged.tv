import { useEffect } from "react"
import { Link } from "react-router-dom"
import { motion, stagger, useAnimate } from "framer-motion"
import { Spotlight } from "@/components/aceternity/spotlight"
import { AuroraText } from "@/components/magicui/aurora-text"
import { Particles } from "@/components/magicui/particles"
import { ShimmerButton } from "@/components/magicui/shimmer-button"
import { ArrowRight } from "lucide-react"

const headlineWords = ["Your", "meetings", "don't", "have", "to", "suck."]

function Headline() {
  const [scope, animate] = useAnimate()

  useEffect(() => {
    animate(
      "span.word",
      { opacity: 1, filter: "blur(0px)" },
      { duration: 0.4, delay: stagger(0.08) }
    )
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scope])

  return (
    <div className="font-display text-5xl font-black tracking-tight text-foreground md:text-7xl lg:text-8xl">
      <div className="mt-4">
        <div ref={scope} className="leading-snug tracking-tight">
          {headlineWords.map((word, idx) => (
            <motion.span
              key={word + idx}
              className="word opacity-0"
              style={{ filter: "blur(10px)" }}
            >
              {word === "suck." ? (
                <AuroraText
                  colors={["#003153", "#4a9eda", "#ffffff", "#6bb8f0"]}
                  speed={1}
                >
                  suck.
                </AuroraText>
              ) : (
                word
              )}{" "}
            </motion.span>
          ))}
        </div>
      </div>
    </div>
  )
}

export function Hero() {
  return (
    <section className="relative flex min-h-screen items-center justify-center overflow-hidden">
      {/* Background layers */}
      <Spotlight className="-top-40 left-0 md:-top-20 md:left-60" />
      <Particles
        className="absolute inset-0"
        quantity={60}
        color="#4a9eda"
        staticity={30}
      />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(0,49,83,0.15)_0%,_transparent_70%)]" />

      {/* Content */}
      <div className="relative z-10 mx-auto max-w-5xl px-6 text-center">
        {/* Tag */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mb-8 inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/50 px-4 py-1.5 text-sm text-muted-foreground backdrop-blur-sm"
        >
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
          </span>
          Now in private beta
        </motion.div>

        {/* Headline */}
        <Headline />

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.2 }}
          className="mx-auto mt-8 max-w-2xl font-display text-lg text-muted-foreground md:text-xl"
        >
          Live streaming that&apos;s actually fun. No corporate bloat, no 47-person Zoom grids,
          no &quot;you&apos;re on mute.&quot; Just you, your people, and vibes.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.5 }}
          className="mt-12 flex flex-col items-center justify-center gap-4 sm:flex-row"
        >
          <Link to="/login">
            <ShimmerButton
              shimmerColor="#4a9eda"
              shimmerSize="0.05em"
              background="rgba(0, 49, 83, 0.4)"
              className="h-12 px-8 text-base"
            >
              Get Started
              <ArrowRight className="h-4 w-4" />
            </ShimmerButton>
          </Link>
          <button className="group flex h-12 items-center gap-2 rounded-full px-8 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">
            <div className="flex h-8 w-8 items-center justify-center rounded-full border border-border/60 bg-card/50 transition-colors group-hover:border-primary/40">
              <svg className="ml-0.5 h-3 w-3" viewBox="0 0 12 12" fill="currentColor">
                <polygon points="3,1 11,6 3,11" />
              </svg>
            </div>
            Watch Demo
          </button>
        </motion.div>

        {/* Bottom tagline */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 2 }}
          className="mt-20 font-mono text-xs tracking-widest text-muted-foreground/50 uppercase"
        >
          Zoom is mid. Get mogged.
        </motion.p>
      </div>
    </section>
  )
}
