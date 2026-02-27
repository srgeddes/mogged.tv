import { Outlet } from "react-router-dom"
import { Navbar } from "@/components/common/navbar"
import { NavDock } from "@/components/common/nav-dock"

export function HomeLayout() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="pb-24 pt-16">
        <Outlet />
      </main>
      <NavDock />
    </div>
  )
}
