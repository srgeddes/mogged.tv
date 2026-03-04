# claude.md — mogged.tv

## Project overview

mogged.tv is a private, self-hosted live streaming platform for small groups. It uses LiveKit for real-time video/audio/chat, FastAPI for the backend API, React for the frontend, and PostgreSQL for persistence. Target scale is 1-10 concurrent viewers per stream.

## Technology stack

- Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic
- React 18+ with TypeScript
- LiveKit (self-hosted, WebRTC)
- PostgreSQL 16
- Redis (caching, optional)
- Docker / Docker Compose
- uv package manager
- Ruff for linting and formatting
- pytest + pytest-asyncio for testing

## Architecture

Domain-Driven Design. Code is organized by domain, not by technical layer.

Three main pieces:

1. **LiveKit server** — handles all real-time media (video, audio, screen share, chat via data channels). Runs as a Docker container on the VPS.
2. **FastAPI backend** — handles auth, user management, stream metadata, and generates LiveKit access tokens. This is the gatekeeper — LiveKit trusts whatever tokens the backend signs.
3. **React frontend** — the UI. Uses LiveKit's React SDK for the stream/chat view and talks to the FastAPI backend for everything else.

Auth flow: User logs in → requests to join a stream → backend validates and issues a LiveKit JWT → frontend connects to LiveKit with that token.

## Project structure (DDD)

```
backend/
├── src/
│   ├── auth/
│   │   ├── router.py          # auth endpoints
│   │   ├── schemas.py         # pydantic request/response models
│   │   ├── models.py          # sqlalchemy ORM models
│   │   ├── service.py         # business logic
│   │   ├── repository.py      # data access layer
│   │   ├── dependencies.py    # FastAPI Depends() for this domain
│   │   ├── exceptions.py      # domain-specific errors
│   │   └── constants.py
│   ├── streams/
│   │   ├── router.py          # stream CRUD, go-live, join
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── service.py         # token generation, room management
│   │   ├── repository.py
│   │   ├── dependencies.py
│   │   ├── exceptions.py
│   │   └── constants.py
│   ├── users/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   ├── dependencies.py
│   │   └── exceptions.py
│   ├── core/
│   │   ├── config.py          # pydantic-settings, env vars
│   │   ├── database.py        # async engine, session factory
│   │   ├── security.py        # password hashing, JWT
│   │   └── exceptions.py      # base exception classes
│   ├── livekit/
│   │   ├── client.py          # LiveKit server SDK wrapper
│   │   ├── token.py           # access token generation
│   │   └── webhooks.py        # room/participant event handlers
│   └── main.py                # FastAPI app, router registration, middleware
├── alembic/                   # database migrations
├── tests/
│   ├── auth/
│   ├── streams/
│   ├── users/
│   └── conftest.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── .env.example

frontend/                              # See frontend/CLAUDE.md for full details
├── CLAUDE.md                          # Frontend-specific AI instructions
├── Makefile                           # Dev commands (make dev, make generate-client)
├── openapi-ts.config.ts               # Hey API code generation config
├── src/
│   ├── client/                        # AUTO-GENERATED — never edit manually
│   ├── components/
│   │   ├── ui/                        # shadcn/ui components
│   │   ├── magicui/                   # Magic UI components (copy-paste)
│   │   ├── aceternity/                # Aceternity UI components (copy-paste)
│   │   ├── common/                    # Shared app components
│   │   ├── auth/                      # Login, signup forms
│   │   └── landing/                   # Landing page sections
│   ├── contexts/                      # React context providers
│   ├── hooks/                         # Custom React hooks
│   ├── pages/                         # Route-level page components
│   └── types/                         # TypeScript interfaces
├── package.json
└── tsconfig.json
```

## Domain rules

Each domain folder (`auth/`, `streams/`, `users/`) follows the same pattern:

- **router.py** — HTTP concerns only. Thin handlers that call service functions. Never put business logic here.
- **service.py** — all business logic. Coordinates between repository, external services (LiveKit), and domain rules.
- **repository.py** — data access only. All database queries live here. Returns domain models, not raw rows.
- **schemas.py** — Pydantic v2 models for request/response validation. Never use raw dicts.
- **models.py** — SQLAlchemy ORM models for this domain's tables.
- **dependencies.py** — FastAPI `Depends()` callables (get current user, get db session, etc).
- **exceptions.py** — domain-specific exceptions that inherit from a base `MoggedError` class.

Services raise domain exceptions. Routers catch them and map to HTTP responses. The domain layer never imports from FastAPI.

## Key conventions

### FastAPI / Python

- Use `Annotated` types with `Depends()` for all dependency injection.
- `async def` for all API endpoints. No sync route handlers.
- Pydantic v2 models for every request and response body.
- Maximum 30-line function length. Extract helpers with descriptive names.
- Type hints required on all functions. Use `from __future__ import annotations`.
- No mutable default arguments.
- Custom exceptions inherit from `MoggedError` base class.
- LiveKit token generation lives in `src/livekit/token.py`, not inline in routes.
- Config loaded via `pydantic-settings` from environment variables. Never hardcode secrets.
- Use middleware for CORS, request logging, and rate limiting.
- No `__init__.py` files. Use implicit namespace packages.

### Database

- SQLAlchemy 2.0 async with `AsyncSession` injected via `Depends()`.
- Alembic for all migrations. Never modify schema manually.
- UUIDs for primary keys.
- Timestamps in UTC always. Convert to local on the frontend.
- Connection pooling via SQLAlchemy. Don't open connections per request.
- No video/blob storage in Postgres. Use S3, store the URL.
- Keep schema simple: `users`, `streams`, `stream_participants` to start.

### Color palette

Semantic color tokens are defined as CSS variables in `frontend/src/index.css` and mapped in `frontend/tailwind.config.js`. **Always use these semantic tokens — never use raw Tailwind colors for these purposes.**

| Token | CSS Variable | Usage |
|-------|-------------|-------|
| `live` | `--live` (red) | LIVE badges, end stream button, active recording, anything "live" |
| `live-foreground` | `--live-foreground` | Text on live backgrounds |
| `success` | `--success` (emerald) | Online indicators, speaking state, success toasts |
| `success-foreground` | `--success-foreground` | Text on success backgrounds |
| `warning` | `--warning` (amber) | Reconnecting state, caution indicators |
| `warning-foreground` | `--warning-foreground` | Text on warning backgrounds |

Usage: `bg-live`, `text-live`, `bg-live/20`, `text-success`, `bg-warning`, etc.

Existing shadcn tokens (`primary`, `destructive`, `muted`, etc.) remain for UI chrome. The tokens above are for **streaming-specific semantic states**.

### React / Frontend

- Functional components and hooks only. No class components.
- TypeScript required. Define prop types with interfaces. No `any`.
- Co-locate component files (styles, tests, helpers) next to the component.
- `useState` / `useReducer` for local state. No state library unless prop drilling is genuinely painful.
- Named exports over default exports.
- `useEffect` cleanup functions for all subscriptions and timers.
- Use `@livekit/components-react` SDK. Lean on pre-built components before building custom.
- Handle loading and error states explicitly on every async operation.
- **Dark theme only.** No light mode code anywhere. Prussian blue (#003153) primary.
- **Toasts:** Use `showSuccess`, `showError`, `showInfo`, `showWarning` from `@/lib/toast`. These can be called from anywhere — components, service functions, callbacks. No hooks needed. Never import `toast` from `sonner` directly; always use the `@/lib/toast` wrappers.
- **`cursor: pointer` is global.** All clickable elements (buttons, links, roles, inputs) get `cursor: pointer` via `index.css`. Don't add `cursor-pointer` classes manually.
- Component hierarchy: shadcn/ui → Magic UI / Aceternity UI → custom only as last resort.
- `src/client/` is auto-generated by Hey API — **never edit manually**, run `make generate-client`.
- bun as the package manager. Vite for bundling. Frontend runs on port 3000.

### Brand voice

- Anti-corporate, satirical, fun. "Zoom is mid. Get mogged." energy.
- Microcopy should be punchy and irreverent. Not pretentious.
- Landing page, error messages, and UI copy should feel like talking to a friend, not reading a TOS.

### LiveKit

- Self-host always. Docker container with pinned versions.
- Short-lived tokens (15 min to 1 hour max).
- Granular permissions: streamers get `canPublish: true`, viewers get `canSubscribe: true` only.
- Use data channels for chat instead of a separate WebSocket server.
- Handle participant events (join, leave, mute, unmute) on the frontend.
- Egress service for recordings to S3. Never capture video client-side.
- Webhook integration for room state monitoring.

### Testing

- pytest + pytest-asyncio with `asyncio_mode = "auto"`.
- Tests mirror the domain structure (`tests/auth/`, `tests/streams/`, etc).
- Write tests for auth flows and token generation first — security-critical paths.
- Integration tests run against real Postgres via Docker in CI.
- Mock external services (LiveKit) in unit tests. Test against real instances in integration tests.

### General

- Docker Compose for local dev — one file spins up LiveKit, Postgres, Redis, and the backend.
- `.env.example` with all required environment variables documented.
- Conventional commits: `feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`.
- **Use the Makefile.** Always prefer `make <target>` over running raw commands. All common operations have a make target. Never write out long `uv run ...` or `npx ...` commands when a make target exists — it's harder to read and easier to get wrong. Check the Makefile first.
- uv for package management. `make sync` to install.
- Ruff for linting and formatting. Single tool, no Black/isort/flake8 separately.
- **Always run `cd backend && make clean` after making any edits to Python files.** No exceptions.
- Don't over-engineer. This is an MVP for 10 people. Ship it, then iterate.
- Keep dependencies minimal. Every library is maintenance burden.
- Structured JSON logging in production. `loguru` for local dev.

## Essential commands

### Backend (run from `backend/`)

```bash
make sync                            # install dependencies
make dev                             # start API server with hot reload
make test                            # run tests
make test-cov                        # run tests with coverage
make lint                            # lint (no fixes)
make format                          # format only
make clean                             # lint auto-fix + format (run after every edit)
make check                           # lint + format check (CI, no modifications)
make migrate                         # run all migrations
make migrate-new msg="description"   # create a new migration
make docker-up                       # start local dev environment
make docker-down                     # stop local dev environment
make nuke                            # remove build artifacts and caches
```

### Frontend (run from `frontend/`)

```bash
make dev                             # start Vite dev server (port 3000)
make build                           # production build
make lint                            # ESLint check
make clean                           # lint fix
make typecheck                       # TypeScript type check
make generate-client                 # generate API client from backend OpenAPI spec
```

## Environment variables

```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mogged
REDIS_URL=redis://localhost:6379
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
JWT_SECRET_KEY=your-256-bit-secret
CORS_ORIGINS=http://localhost:3000
S3_BUCKET=mogged-recordings
LOG_LEVEL=INFO
```
