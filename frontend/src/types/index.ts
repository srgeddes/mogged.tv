export interface User {
  id: string
  username: string
  email: string
  display_name: string | null
  avatar_url: string | null
  aura_balance: number
  is_active: boolean
}

export interface AuthTokens {
  access_token: string
  token_type: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  username: string
  email: string
  password: string
  display_name?: string
}

// --- Organizations ---

export type OrgRole = "owner" | "admin" | "member"

export interface Organization {
  id: string
  name: string
  slug: string
  description: string | null
  avatar_url: string | null
  created_by: string
  member_count: number
}

export interface OrgMember {
  id: string
  organization_id: string
  user_id: string
  role: OrgRole
  username: string
  display_name: string | null
  avatar_url: string | null
}

// --- Friends ---

export type FriendRequestStatus = "pending" | "accepted" | "declined"

export interface FriendRequest {
  id: string
  from_user_id: string
  to_user_id: string
  status: FriendRequestStatus
  created_at: string
  from_username: string
  from_display_name: string | null
  from_avatar_url: string | null
  to_username: string
  to_display_name: string | null
  to_avatar_url: string | null
}

export interface Friend {
  user_id: string
  username: string
  display_name: string | null
  avatar_url: string | null
  is_in_shared_org: boolean
}

// --- Streams ---

export type StreamAccessLevel = "public" | "friends" | "org_only" | "link_only"
export type StreamStatus = "scheduled" | "live" | "ended"

export interface Stream {
  id: string
  host_id: string
  title: string
  description: string | null
  status: StreamStatus
  room_name: string
  access_level: StreamAccessLevel
  org_id: string | null
  scheduled_at: string | null
  started_at: string | null
  ended_at: string | null
  thumbnail_url: string | null
  max_viewers: number | null
  host_username: string
  host_display_name: string | null
  host_avatar_url: string | null
}

export interface StartStreamResponse {
  token: string
  livekit_url: string
  stream: Stream
}

export interface JoinStreamResponse {
  token: string
  livekit_url: string
  stream: Stream
}

// --- Users ---

export interface UserProfile {
  id: string
  username: string
  display_name: string | null
  avatar_url: string | null
  bio: string | null
}

export interface UserSearchResult {
  id: string
  username: string
  display_name: string | null
  avatar_url: string | null
}

export interface UserStats {
  total_streams_hosted: number
  total_streams_watched: number
  total_watch_time_seconds: number
  total_stream_time_seconds: number
  total_aura_earned: number
  total_aura_given: number
  total_messages_sent: number
  total_emotes_sent: number
  longest_stream_seconds: number
  biggest_aura_drop: number
}

// --- Trivia ---

export interface TriviaCategory {
  id: string
  name: string
  slug: string
  is_brain_rot: boolean
  icon: string
  question_count: number
}

export interface TriviaQuestion {
  id: string
  category_name: string
  category_slug: string
  is_brain_rot: boolean
  question_text: string
  difficulty: "easy" | "medium" | "hard"
  answers: string[]
  timer_seconds: number
}

export interface SubmitAnswerResponse {
  is_correct: boolean
  correct_answer: string
  aura_earned: number
  new_aura_balance: number
}

export interface TriviaStats {
  total_answered: number
  total_correct: number
  accuracy_percent: number
  total_aura_earned: number
  current_streak: number
}
