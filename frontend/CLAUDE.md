# claude.md — mogged.tv frontend

## Overview

React SPA for mogged.tv — a private, self-hosted live streaming platform. Vite + React 18 + TypeScript.

## Tech stack

- Vite, React 18, TypeScript
- Tailwind CSS v3 + shadcn/ui (New York style)
- Magic UI (copy-paste components in `src/components/magicui/`)
- Aceternity UI (copy-paste components in `src/components/aceternity/`)
- React Router v7
- framer-motion for animations
- bun package manager

## File structure

```
src/
├── main.tsx                    # Entry point
├── App.tsx                     # Router + auth provider
├── index.css                   # Tailwind + CSS variables (dark only)
├── lib/utils.ts                # cn() utility
├── client/                     # AUTO-GENERATED — never edit manually
├── components/
│   ├── ui/                     # shadcn/ui components
│   ├── magicui/                # Magic UI components
│   ├── aceternity/             # Aceternity UI components
│   ├── common/                 # Shared app components
│   ├── auth/                   # Auth-related components
│   └── landing/                # Landing page sections
├── contexts/                   # React context providers
├── hooks/                      # Custom hooks
├── pages/                      # Route-level page components
└── types/                      # TypeScript interfaces
```

## Conventions

### Files & naming
- **kebab-case** for all file names: `loading-button.tsx`, `auth-context.tsx`
- **Named exports** only. No default exports.
- Component files export a single component matching the file name (PascalCase).

### Components
1. Use **shadcn/ui** first (from `components/ui/`)
2. Use **Magic UI** or **Aceternity UI** for effects and animations
3. Build custom only as a last resort
4. Functional components and hooks only — no class components
5. TypeScript required. Props defined with interfaces. No `any`.

### Styling
- **Dark theme only.** No light mode code. `<html class="dark">` is hardcoded.
- Primary color: Prussian blue (#003153)
- Fonts: **Outfit** (display/headings), **JetBrains Mono** (mono/code/tags)
- Use Tailwind classes. CSS modules only if absolutely necessary.
- `cursor: pointer` is applied globally to all clickable elements in `index.css`. Don't add `cursor-pointer` manually.

### Auth
- JWT stored in localStorage
- `AuthProvider` wraps the app in `App.tsx`
- Use `useAuth()` hook to access auth state
- `ProtectedRoute` component guards authenticated pages

### Toasts
- Use `showSuccess`, `showError`, `showInfo`, `showWarning` from `@/lib/toast`
- These work anywhere — components, service functions, event handlers. No hooks needed.
- Never import `toast` from `sonner` directly. Always use the `@/lib/toast` wrappers.
- Sonner `<Toaster>` is mounted in `App.tsx` via `@/components/ui/sonner.tsx`.

### API client
- `src/client/` is auto-generated from the backend OpenAPI spec
- Run `make generate-client` to regenerate (requires backend running)
- **NEVER** edit files in `src/client/` manually

### Branding voice
- Anti-corporate, satirical, fun
- "Zoom is mid. Get mogged." energy
- Microcopy should be punchy and irreverent
- Not pretentious — genuinely fun

## Essential commands

```bash
make dev               # Start Vite dev server (port 3000)
make build             # Production build
make lint              # ESLint check
make clean             # Lint fix
make typecheck         # TypeScript type check
make generate-client   # Generate API client from backend OpenAPI spec
```

## Import alias

`@/` maps to `src/`. Use it everywhere: `import { cn } from "@/lib/utils"`
