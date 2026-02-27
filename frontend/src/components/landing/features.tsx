import { motion } from "framer-motion"
import { BentoGrid, BentoCard } from "@/components/magicui/bento-grid"
import {
  Video,
  MessageSquare,
  Monitor,
  Smile,
  Flame,
  Link2,
} from "lucide-react"

const features = [
  {
    icon: <Video className="h-6 w-6" />,
    name: "Live HD Streaming",
    description:
      "WebRTC-powered. Sub-second latency. Not that buffering garbage you're used to.",
    className: "md:col-span-1",
  },
  {
    icon: <MessageSquare className="h-6 w-6" />,
    name: "Built-in Chat",
    description:
      "Real-time chat baked right in. No Slack tab, no Discord sidebar. Just talk.",
    className: "md:col-span-1",
  },
  {
    icon: <Monitor className="h-6 w-6" />,
    name: "Screen Sharing",
    description:
      "Share your screen, your code, your memes. One click, zero friction.",
    className: "md:col-span-1",
  },
  {
    icon: <Smile className="h-6 w-6" />,
    name: "Custom Emotes",
    description:
      "Upload your own emotes. Express yourself beyond boring emoji reactions.",
    className: "md:col-span-1",
  },
  {
    icon: <Flame className="h-6 w-6" />,
    name: "Aura System",
    description:
      "Earn aura for streaming and chatting. Gamified clout. Flex your numbers.",
    className: "md:col-span-1",
  },
  {
    icon: <Link2 className="h-6 w-6" />,
    name: "Invite Links",
    description:
      "Private by default. Share links with your crew. Not everyone gets in.",
    className: "md:col-span-1",
  },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" as const } },
}

export function Features() {
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
            Features
          </p>
          <h2 className="font-display text-4xl font-bold tracking-tight text-foreground md:text-5xl">
            Everything. Nothing extra.
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Built for people who actually want to hang out, not attend a meeting.
          </p>
        </motion.div>

        {/* Bento grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
        >
          <BentoGrid className="auto-rows-[16rem] md:grid-cols-3">
            {features.map((feature) => (
              <motion.div key={feature.name} variants={itemVariants}>
                <BentoCard
                  {...feature}
                  className={feature.className + " h-full"}
                />
              </motion.div>
            ))}
          </BentoGrid>
        </motion.div>
      </div>
    </section>
  )
}
