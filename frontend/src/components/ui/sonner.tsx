import { Toaster as SonnerToaster } from "sonner"

export function Toaster() {
  return (
    <SonnerToaster
      position="bottom-right"
      toastOptions={{
        unstyled: true,
        classNames: {
          toast:
            "flex items-center gap-3 w-full rounded-md border px-4 py-3 shadow-lg text-sm font-medium",
          title: "text-sm font-semibold",
          description: "text-sm opacity-80",
          success:
            "border-emerald-500/20 bg-emerald-950/60 text-emerald-200",
          error:
            "border-red-500/20 bg-red-950/60 text-red-200",
          info: "border-sky-500/20 bg-sky-950/60 text-sky-200",
          warning:
            "border-amber-500/20 bg-amber-950/60 text-amber-200",
          default:
            "border-border bg-card text-foreground",
        },
      }}
    />
  )
}
