import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "@/hooks/use-auth"
import { Logo } from "./logo"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { LogOut, User } from "lucide-react"

export function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate("/")
  }

  return (
    <nav className="fixed top-0 z-50 w-full border-b border-border/40 bg-background/60 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Link to="/" className="transition-opacity hover:opacity-80">
          <Logo size="sm" />
        </Link>

        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2 rounded-full border border-border/40 bg-card/50 px-3 py-1.5 text-sm text-foreground transition-colors hover:bg-card">
                  <Avatar className="h-6 w-6">
                    <AvatarFallback className="bg-primary/20 text-xs font-medium text-primary-foreground">
                      {user?.display_name?.[0] ?? user?.username?.[0] ?? "?"}
                    </AvatarFallback>
                  </Avatar>
                  <span className="font-mono text-sm">{user?.display_name ?? user?.username}</span>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem className="gap-2" onClick={() => navigate("/home/profile")}>
                  <User className="h-4 w-4" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem className="gap-2 text-destructive" onClick={handleLogout}>
                  <LogOut className="h-4 w-4" />
                  Sign out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button asChild variant="secondary" size="sm" className="font-mono">
              <Link to="/login">Sign in</Link>
            </Button>
          )}
        </div>
      </div>
    </nav>
  )
}
