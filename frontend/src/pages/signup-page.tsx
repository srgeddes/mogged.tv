import { useNavigate, Link } from "react-router-dom"
import { useAuth } from "@/hooks/use-auth"
import { api } from "@/lib/api"
import { SignupForm } from "@/components/auth/signup-form"
import { Logo } from "@/components/common/logo"
import { Particles } from "@/components/magicui/particles"
import type { User } from "@/types"

interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export function SignupPage() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSignup = async (username: string, email: string, password: string) => {
    const data = await api.post<AuthResponse>("/auth/signup", { username, email, password })
    login(data.access_token, data.user)
    navigate("/home/feed")
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-background">
      <Particles className="absolute inset-0" quantity={40} color="#4a9eda" staticity={50} />

      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(0,49,83,0.12)_0%,_transparent_60%)]" />

      <div className="relative z-10 flex w-full max-w-sm flex-col items-center px-6 py-12">
        <Link to="/" className="mb-8 transition-opacity hover:opacity-80">
          <Logo size="lg" />
        </Link>
        <SignupForm onSubmit={handleSignup} />
        <p className="mt-6 font-mono text-xs text-muted-foreground/30">
          Your aura journey starts here
        </p>
      </div>
    </div>
  )
}
