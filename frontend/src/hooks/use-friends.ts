import { useCallback } from "react"
import { api, ApiError } from "@/lib/api"
import { showError, showSuccess } from "@/lib/toast"
import type { Friend, FriendRequest } from "@/types"
import { useApi } from "./use-api"

export function useFriends() {
  return useApi<Friend[]>(() => api.get("/friends"))
}

export function useIncomingRequests() {
  return useApi<FriendRequest[]>(() => api.get("/friends/requests/incoming"))
}

export function useOutgoingRequests() {
  return useApi<FriendRequest[]>(() => api.get("/friends/requests/outgoing"))
}

export function useFriendActions() {
  const sendRequest = useCallback(async (toUserId: string) => {
    try {
      await api.post("/friends/requests", { to_user_id: toUserId })
      showSuccess("Friend request sent")
      return true
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to send request")
      return false
    }
  }, [])

  const acceptRequest = useCallback(async (requestId: string) => {
    try {
      await api.post<Friend>(`/friends/requests/${requestId}/accept`)
      showSuccess("Friend request accepted")
      return true
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to accept request")
      return false
    }
  }, [])

  const declineRequest = useCallback(async (requestId: string) => {
    try {
      await api.post(`/friends/requests/${requestId}/decline`)
      showSuccess("Friend request declined")
      return true
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to decline request")
      return false
    }
  }, [])

  const cancelRequest = useCallback(async (requestId: string) => {
    try {
      await api.delete(`/friends/requests/${requestId}`)
      showSuccess("Friend request cancelled")
      return true
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to cancel request")
      return false
    }
  }, [])

  const removeFriend = useCallback(async (userId: string) => {
    try {
      await api.delete(`/friends/${userId}`)
      showSuccess("Friend removed")
      return true
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to remove friend")
      return false
    }
  }, [])

  return { sendRequest, acceptRequest, declineRequest, cancelRequest, removeFriend }
}
