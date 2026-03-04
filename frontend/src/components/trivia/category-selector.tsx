import { cn } from "@/lib/utils"
import type { TriviaCategory } from "@/types"

interface CategorySelectorProps {
  categories: TriviaCategory[]
  selected: string | null
  onSelect: (slug: string | null) => void
}

export function CategorySelector({ categories, selected, onSelect }: CategorySelectorProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      <button
        onClick={() => onSelect(null)}
        className={cn(
          "shrink-0 rounded-full px-4 py-1.5 text-sm font-medium transition-colors",
          selected === null
            ? "bg-primary text-primary-foreground"
            : "bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground",
        )}
      >
        All
      </button>
      {categories.map((cat) => (
        <button
          key={cat.slug}
          onClick={() => onSelect(cat.slug)}
          className={cn(
            "shrink-0 rounded-full px-4 py-1.5 text-sm font-medium transition-colors",
            selected === cat.slug
              ? cat.is_brain_rot
                ? "bg-amber-500/20 text-amber-300 ring-1 ring-amber-500/40"
                : "bg-primary text-primary-foreground"
              : "bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground",
            cat.is_brain_rot && selected !== cat.slug && "text-amber-400/70",
          )}
        >
          {cat.is_brain_rot && "🧠 "}{cat.name}
        </button>
      ))}
    </div>
  )
}
