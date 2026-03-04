import { Outlet } from "react-router-dom"
import { Navbar } from "@/components/common/navbar"
import { NavDock } from "@/components/common/nav-dock"

export function HomeLayout() {
  return (
    <div className="min-h-screen overscroll-none bg-background">
      <Navbar />
      <main className="mx-auto max-w-7xl px-6 pb-24 pt-16">
        <Outlet />
      </main>
      <NavDock />
    </div>
  )
}
