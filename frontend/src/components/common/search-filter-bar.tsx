import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

interface FilterOption {
  value: string
  label: string
}

interface SearchFilterBarProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  activeFilter: string
  onFilterChange: (filter: string) => void
  filterOptions: FilterOption[]
  placeholder?: string
}

export function SearchFilterBar({
  searchQuery,
  onSearchChange,
  activeFilter,
  onFilterChange,
  filterOptions,
  placeholder = "Search...",
}: SearchFilterBarProps) {
  return (
    <div className="flex max-w-2xl flex-col gap-3 sm:flex-row sm:items-center">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder={placeholder}
          className="pl-9"
        />
      </div>
      <div className="flex flex-wrap gap-2">
        {filterOptions.map((opt) => (
          <button
            key={opt.value}
            onClick={() => onFilterChange(opt.value)}
            className={cn(
              "rounded-full px-3 py-1 text-xs font-medium transition-colors",
              activeFilter === opt.value
                ? "bg-primary/20 text-foreground"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  )
}
