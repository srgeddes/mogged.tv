import { useCallback } from "react"
import { api, ApiError } from "@/lib/api"
import { showError, showSuccess } from "@/lib/toast"
import type { JoinStreamResponse, StartStreamResponse, Stream, StreamAccessLevel, UserStatsOverview } from "@/types"
import { useApi } from "./use-api"

export function useLiveStreams() {
  return useApi<Stream[]>(() => api.get("/streams/live"))
}

export function useRecentStreams() {
  return useApi<Stream[]>(() => api.get("/streams/recent"))
}

export function useUserStats() {
  return useApi<UserStatsOverview>(() => api.get("/users/me/stats"))
}

export function useStreamActions() {
  const createStream = useCallback(
    async (data: {
      title: string
      description?: string
      access_level: StreamAccessLevel
      org_id?: string
    }) => {
      try {
        const stream = await api.post<Stream>("/streams", data)
        showSuccess("Stream created")
        return stream
      } catch (err) {
        showError(err instanceof ApiError ? err.message : "Failed to create stream")
        return null
      }
    },
    [],
  )

  const startStream = useCallback(async (streamId: string) => {
    try {
      const result = await api.post<StartStreamResponse>(
        `/streams/${streamId}/start`,
      )
      showSuccess("You're live!")
      return result
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to start stream")
      return null
    }
  }, [])

  const joinStream = useCallback(async (streamId: string, inviteToken?: string) => {
    try {
      const query = inviteToken ? `?invite_token=${encodeURIComponent(inviteToken)}` : ""
      return await api.post<JoinStreamResponse>(`/streams/${streamId}/join${query}`)
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to join stream")
      return null
    }
  }, [])

  const endStream = useCallback(async (streamId: string) => {
    try {
      const stream = await api.post<Stream>(`/streams/${streamId}/end`)
      showSuccess("Stream ended")
      return stream
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to end stream")
      return null
    }
  }, [])

  const getLiveStreamByUsername = useCallback(async (username: string) => {
    try {
      return await api.get<Stream | null>(`/streams/live/u/${username}`)
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to load stream")
      return null
    }
  }, [])

  const getLiveStreamBySlug = useCallback(async (username: string, slug: string) => {
    try {
      return await api.get<Stream | null>(`/streams/live/u/${username}/${slug}`)
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to load stream")
      return null
    }
  }, [])

  return { createStream, startStream, joinStream, endStream, getLiveStreamByUsername, getLiveStreamBySlug }
}
