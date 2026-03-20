import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider } from "@/contexts/auth-context"
import { useAuth } from "@/hooks/use-auth"
import { LandingPage } from "@/pages/landing-page"
import { LoginPage } from "@/pages/login-page"
import { SignupPage } from "@/pages/signup-page"
import { HomeLayout } from "@/pages/home-layout"
import { FeedPage } from "@/pages/feed-page"
import { StreamPage } from "@/pages/stream-page"
import { StatsPage } from "@/pages/stats-page"
import { FriendsPage } from "@/pages/friends-page"
import { OrgsPage } from "@/pages/orgs-page"
import { ProfilePage } from "@/pages/profile-page"
import { AuraPage } from "@/pages/aura-page"
import { Toaster } from "@/components/ui/sonner"
import { ErrorBoundary } from "@/components/common/error-boundary"
import type { ReactNode } from "react"

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

function PublicRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/home/feed" replace />
  }

  return <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <PublicRoute>
            <LandingPage />
          </PublicRoute>
        }
      />
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      <Route
        path="/signup"
        element={
          <PublicRoute>
            <SignupPage />
          </PublicRoute>
        }
      />
      <Route path="/:username/:slug" element={<StreamPage />} />
      <Route path="/:username" element={<StreamPage />} />
      <Route
        path="/home"
        element={
          <ProtectedRoute>
            <HomeLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/home/feed" replace />} />
        <Route path="feed" element={<FeedPage />} />
        <Route path="aura" element={<AuraPage />} />
        <Route path="stats" element={<StatsPage />} />
        <Route path="friends" element={<FriendsPage />} />
        <Route path="orgs" element={<OrgsPage />} />
        <Route path="profile" element={<ProfilePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
          <Toaster />
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  )
}
