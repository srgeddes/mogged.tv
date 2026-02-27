import { useCallback, useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import { BorderBeam } from "@/components/magicui/border-beam"
import { TriviaTimer } from "./trivia-timer"
import { CorrectAnimation } from "./correct-animation"
import type { TriviaQuestion, SubmitAnswerResponse } from "@/types"

type GameState = "idle" | "loading" | "playing" | "answered"

const DIFFICULTY_COLORS: Record<string, string> = {
  easy: "text-green-400",
  medium: "text-amber-400",
  hard: "text-red-400",
}

const AURA_REWARDS: Record<string, number> = {
  easy: 10,
  medium: 25,
  hard: 50,
}

interface TriviaCardProps {
  categorySlug: string | null
  onAuraEarned: (newBalance: number) => void
  onAnswered: () => void
  getQuestion: (slug?: string) => Promise<TriviaQuestion | null>
  submitAnswer: (questionId: string, answer: string) => Promise<SubmitAnswerResponse | null>
}

export function TriviaCard({
  categorySlug,
  onAuraEarned,
  onAnswered,
  getQuestion,
  submitAnswer,
}: TriviaCardProps) {
  const [state, setState] = useState<GameState>("idle")
  const [question, setQuestion] = useState<TriviaQuestion | null>(null)
  const [result, setResult] = useState<SubmitAnswerResponse | null>(null)
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [timerRunning, setTimerRunning] = useState(false)
  const [exhausted, setExhausted] = useState(false)
  const submittedRef = useRef(false)

  const fetchQuestion = useCallback(async () => {
    setState("loading")
    setResult(null)
    setSelectedAnswer(null)
    setExhausted(false)
    submittedRef.current = false

    const q = await getQuestion(categorySlug ?? undefined)
    if (q) {
      setQuestion(q)
      setState("playing")
      setTimerRunning(true)
    } else {
      setExhausted(true)
      setState("idle")
    }
  }, [categorySlug, getQuestion])

  // Reset when category changes
  useEffect(() => {
    setState("idle")
    setQuestion(null)
    setResult(null)
    setExhausted(false)
  }, [categorySlug])

  const handleAnswer = useCallback(
    async (answer: string) => {
      if (state !== "playing" || submittedRef.current) return
      submittedRef.current = true
      setTimerRunning(false)
      setSelectedAnswer(answer)
      setState("answered")

      const res = await submitAnswer(question!.id, answer)
      if (res) {
        setResult(res)
        if (res.aura_earned > 0) {
          onAuraEarned(res.new_aura_balance)
        }
        onAnswered()
      }
    },
    [state, question, submitAnswer, onAuraEarned, onAnswered],
  )

  const handleTimerExpire = useCallback(() => {
    if (submittedRef.current) return
    // Auto-submit empty answer on timeout
    submittedRef.current = true
    setTimerRunning(false)
    setState("answered")
    setSelectedAnswer(null)

    submitAnswer(question!.id, "").then((res) => {
      if (res) {
        setResult(res)
        onAnswered()
      }
    })
  }, [question, submitAnswer, onAnswered])

  if (state === "idle") {
    return (
      <div className="relative overflow-hidden rounded-xl border border-border/50 bg-card/80 p-8 backdrop-blur">
        <div className="flex flex-col items-center gap-4 text-center">
          {exhausted ? (
            <>
              <p className="text-lg font-medium text-muted-foreground">
                You&apos;ve answered all available questions
                {categorySlug ? " in this category" : ""}!
              </p>
              <p className="text-sm text-muted-foreground/70">
                Check back later for new questions, or try a different category.
              </p>
            </>
          ) : (
            <>
              <p className="text-lg font-medium text-muted-foreground">
                Ready to earn some aura?
              </p>
              <button
                onClick={fetchQuestion}
                className="rounded-lg bg-primary px-6 py-3 font-semibold text-primary-foreground transition-transform hover:scale-105 active:scale-95"
              >
                Start Trivia
              </button>
            </>
          )}
        </div>
      </div>
    )
  }

  if (state === "loading") {
    return (
      <div className="relative overflow-hidden rounded-xl border border-border/50 bg-card/80 p-8 backdrop-blur">
        <div className="flex items-center justify-center py-8">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      </div>
    )
  }

  if (!question) return null

  const auraReward = question.is_brain_rot ? 30 : AURA_REWARDS[question.difficulty] ?? 10

  return (
    <div className="relative overflow-hidden rounded-xl border border-border/50 bg-card/80 backdrop-blur">
      {state === "playing" && <BorderBeam duration={8} size={120} />}
      <CorrectAnimation show={result?.is_correct === true} />

      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/30 px-5 py-3">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-muted-foreground">{question.category_name}</span>
          <span className="text-muted-foreground/40">·</span>
          <span className={cn("font-medium capitalize", DIFFICULTY_COLORS[question.difficulty])}>
            {question.difficulty}
          </span>
        </div>
        <span className="rounded-md bg-primary/10 px-2.5 py-0.5 font-mono text-xs font-bold text-primary">
          +{auraReward} aura
        </span>
      </div>

      {/* Question */}
      <div className="px-5 py-6">
        <h2 className="text-center text-lg font-semibold leading-relaxed sm:text-xl">
          {question.question_text}
        </h2>
      </div>

      {/* Answers */}
      <div className="grid grid-cols-1 gap-3 px-5 sm:grid-cols-2">
        {question.answers.map((answer) => {
          let variant = "default"
          if (state === "answered" && result) {
            if (answer === result.correct_answer) variant = "correct"
            else if (answer === selectedAnswer) variant = "incorrect"
          } else if (state === "answered" && !result) {
            // Still loading result
            if (answer === selectedAnswer) variant = "selected"
          }

          return (
            <motion.button
              key={answer}
              onClick={() => handleAnswer(answer)}
              disabled={state !== "playing"}
              whileHover={state === "playing" ? { scale: 1.02 } : undefined}
              whileTap={state === "playing" ? { scale: 0.98 } : undefined}
              className={cn(
                "rounded-lg border px-4 py-3 text-left text-sm font-medium transition-colors",
                variant === "default" &&
                  "border-border/50 bg-muted/30 hover:border-primary/50 hover:bg-muted/50",
                variant === "selected" && "border-primary bg-primary/20",
                variant === "correct" &&
                  "border-green-500/60 bg-green-500/15 text-green-300",
                variant === "incorrect" &&
                  "border-red-500/60 bg-red-500/15 text-red-300",
                state !== "playing" && variant === "default" && "opacity-50",
              )}
            >
              {answer}
            </motion.button>
          )
        })}
      </div>

      {/* Timer */}
      <div className="px-5 pb-4 pt-5">
        <TriviaTimer
          seconds={question.timer_seconds}
          running={timerRunning}
          onExpire={handleTimerExpire}
        />
      </div>

      {/* Result / Next */}
      {state === "answered" && result && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          className="border-t border-border/30 px-5 py-4"
        >
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">
              {result.is_correct ? (
                <span className="text-green-400">Correct! +{result.aura_earned} aura</span>
              ) : selectedAnswer === null ? (
                <span className="text-muted-foreground">Time&apos;s up!</span>
              ) : (
                <span className="text-red-400">Wrong answer</span>
              )}
            </p>
            <button
              onClick={fetchQuestion}
              className="rounded-lg bg-primary/80 px-4 py-2 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary"
            >
              Next Question
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
