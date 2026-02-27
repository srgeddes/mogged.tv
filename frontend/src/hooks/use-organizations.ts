import { useCallback } from "react"
import { api, ApiError } from "@/lib/api"
import { showError, showSuccess } from "@/lib/toast"
import type { Organization, OrgMember } from "@/types"
import { useApi } from "./use-api"

export function useOrganizations() {
  return useApi<Organization[]>(() => api.get("/orgs"))
}

export function useOrgMembers(orgId: string | null) {
  return useApi<OrgMember[]>(
    () => (orgId ? api.get(`/orgs/${orgId}/members`) : Promise.resolve([])),
    [orgId],
  )
}

export function useOrgActions() {
  const createOrg = useCallback(
    async (data: { name: string; slug: string; description?: string }) => {
      try {
        const org = await api.post<Organization>("/orgs", data)
        showSuccess("Organization created")
        return org
      } catch (err) {
        showError(err instanceof ApiError ? err.message : "Failed to create org")
        return null
      }
    },
    [],
  )

  const addMember = useCallback(async (orgId: string, userId: string) => {
    try {
      await api.post(`/orgs/${orgId}/members`, { user_id: userId })
      showSuccess("Member added")
      return true
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to add member")
      return false
    }
  }, [])

  const removeMember = useCallback(async (orgId: string, userId: string) => {
    try {
      await api.delete(`/orgs/${orgId}/members/${userId}`)
      showSuccess("Member removed")
      return true
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to remove member")
      return false
    }
  }, [])

  const updateRole = useCallback(
    async (orgId: string, userId: string, role: string) => {
      try {
        await api.patch(`/orgs/${orgId}/members/${userId}/role`, { role })
        showSuccess("Role updated")
        return true
      } catch (err) {
        showError(err instanceof ApiError ? err.message : "Failed to update role")
        return false
      }
    },
    [],
  )

  return { createOrg, addMember, removeMember, updateRole }
}
