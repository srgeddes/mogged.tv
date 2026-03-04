import { useCallback, useState } from "react"
import { useAuth } from "@/hooks/use-auth"
import { useTriviaCategories, useTriviaStats, useTriviaActions } from "@/hooks/use-trivia"
import { AuraDisplay } from "@/components/trivia/aura-display"
import { CategorySelector } from "@/components/trivia/category-selector"
import { TriviaCard } from "@/components/trivia/trivia-card"

export function AuraPage() {
  const { user, updateUser } = useAuth()
  const { data: categories } = useTriviaCategories()
  const { data: stats, refetch: refetchStats } = useTriviaStats()
  const { getQuestion, submitAnswer } = useTriviaActions()

  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [auraBalance, setAuraBalance] = useState<number | null>(null)

  // Use live balance if updated, otherwise fall back to user profile
  const displayBalance = auraBalance ?? user?.aura_balance ?? 0

  const handleAuraEarned = useCallback((newBalance: number) => {
    setAuraBalance(newBalance)
    updateUser({ aura_balance: newBalance })
  }, [updateUser])

  const handleAnswered = useCallback(() => {
    refetchStats()
  }, [refetchStats])

  return (
    <div className="py-10">
      {/* Aura Display */}
      <div className="mb-10 text-center">
        <h1 className="mb-6 font-display text-sm font-medium uppercase tracking-widest text-muted-foreground">
          Aura Farming
        </h1>
        <AuraDisplay
          balance={displayBalance}
          totalAnswered={stats?.total_answered ?? 0}
          accuracy={stats?.accuracy_percent ?? 0}
          streak={stats?.current_streak ?? 0}
        />
      </div>

      {/* Category Selector */}
      {categories && categories.length > 0 && (
        <div className="mb-8">
          <CategorySelector
            categories={categories}
            selected={selectedCategory}
            onSelect={setSelectedCategory}
          />
        </div>
      )}

      {/* Trivia Card */}
      <div className="mx-auto max-w-xl">
      <TriviaCard
        categorySlug={selectedCategory}
        onAuraEarned={handleAuraEarned}
        onAnswered={handleAnswered}
        getQuestion={getQuestion}
        submitAnswer={submitAnswer}
      />
      </div>
    </div>
  )
}
