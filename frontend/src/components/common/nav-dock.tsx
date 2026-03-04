import { useLocation, useNavigate } from "react-router-dom"
import { Home, Sparkles, BarChart3, Users, Building2 } from "lucide-react"
import { FloatingDock } from "@/components/aceternity/floating-dock"

const NAV_ITEMS = [
  { title: "Home", icon: <Home className="h-full w-full" />, href: "/home/feed" },
  { title: "Aura", icon: <Sparkles className="h-full w-full" />, href: "/home/aura" },
  { title: "Stats", icon: <BarChart3 className="h-full w-full" />, href: "/home/stats" },
  { title: "Friends", icon: <Users className="h-full w-full" />, href: "/home/friends" },
  { title: "Orgs", icon: <Building2 className="h-full w-full" />, href: "/home/orgs" },
]

export function NavDock() {
  const location = useLocation()
  const navigate = useNavigate()

  const items = NAV_ITEMS.map((item) => ({
    ...item,
    active: location.pathname.startsWith(item.href),
  }))

  return (
    <div className="fixed bottom-6 left-1/2 z-50 -translate-x-1/2">
      <FloatingDock items={items} onNavigate={(href) => navigate(href)} />
    </div>
  )
}
