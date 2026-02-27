import { useState, useCallback } from "react"
import { api } from "@/lib/api"
import type { UserSearchResult } from "@/types"

export function useUserSearch() {
  const [results, setResults] = useState<UserSearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)

  const search = useCallback(async (query: string) => {
    if (query.length < 1) {
      setResults([])
      return
    }
    setIsSearching(true)
    try {
      const data = await api.get<UserSearchResult[]>(
        `/users/search?q=${encodeURIComponent(query)}`,
      )
      setResults(data)
    } catch {
      setResults([])
    } finally {
      setIsSearching(false)
    }
  }, [])

  const clear = useCallback(() => setResults([]), [])

  return { results, isSearching, search, clear }
}
