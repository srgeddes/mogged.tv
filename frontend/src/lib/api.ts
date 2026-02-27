const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api"

function getToken(): string | null {
  return localStorage.getItem("mogged_token")
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) ?? {}),
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  let res: Response
  try {
    res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    })
  } catch {
    throw new ApiError(0, "Can't reach the server — is the backend running?")
  }

  if (!res.ok) {
    const body = await res.json().catch(() => null)
    const message = body?.detail ?? friendlyStatus(res.status)
    throw new ApiError(res.status, message)
  }

  if (res.status === 204) {
    return undefined as T
  }

  return res.json()
}

function friendlyStatus(status: number): string {
  if (status === 401) return "Session expired — please log in again"
  if (status === 403) return "You don't have permission to do that"
  if (status === 404) return "Not found"
  if (status === 409) return "Already exists"
  if (status === 422) return "Invalid input — check your fields"
  if (status === 429) return "Slow down — too many requests"
  if (status >= 500) return "Server error — try again in a sec"
  return "Something went wrong"
}

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

export const api = {
  get: <T>(path: string) => apiFetch<T>(path),
  post: <T>(path: string, body?: unknown) =>
    apiFetch<T>(path, {
      method: "POST",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  patch: <T>(path: string, body?: unknown) =>
    apiFetch<T>(path, {
      method: "PATCH",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(path: string) =>
    apiFetch<T>(path, { method: "DELETE" }),
}
