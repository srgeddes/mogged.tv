import { useCallback } from "react"
import { api, ApiError } from "@/lib/api"
import { showError } from "@/lib/toast"
import type { TriviaCategory, TriviaQuestion, SubmitAnswerResponse, TriviaStats } from "@/types"
import { useApi } from "./use-api"

export function useTriviaCategories() {
  return useApi<TriviaCategory[]>(() => api.get("/trivia/categories"))
}

export function useTriviaStats() {
  return useApi<TriviaStats>(() => api.get("/trivia/stats"))
}

export function useTriviaActions() {
  const getQuestion = useCallback(async (categorySlug?: string) => {
    try {
      const query = categorySlug ? `?category=${categorySlug}` : ""
      return await api.get<TriviaQuestion>(`/trivia/question${query}`)
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        return null
      }
      showError(err instanceof ApiError ? err.message : "Failed to load question")
      return null
    }
  }, [])

  const submitAnswer = useCallback(async (questionId: string, selectedAnswer: string) => {
    try {
      return await api.post<SubmitAnswerResponse>("/trivia/answer", {
        question_id: questionId,
        selected_answer: selectedAnswer,
      })
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to submit answer")
      return null
    }
  }, [])

  return { getQuestion, submitAnswer }
}
