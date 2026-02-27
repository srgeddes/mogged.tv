.PHONY: dev dev-backend dev-frontend \
	sync build lint clean check typecheck format \
	test test-cov generate-client \
	migrate migrate-new \
	docker-up docker-down nuke

# ── Dev servers ──────────────────────────────────────────────

ROOT_DIR := $(shell pwd)

# Start backend + frontend in separate iTerm2 tabs
dev:
	@echo "Opening backend (:8000) and frontend (:3000) in iTerm2 tabs..."
	@osascript \
		-e 'tell application "iTerm2"' \
		-e '  activate' \
		-e '  tell current window' \
		-e '    set backendTab to (create tab with default profile)' \
		-e '    tell current session of backendTab' \
		-e '      write text "cd $(ROOT_DIR)/backend && make dev"' \
		-e '    end tell' \
		-e '    set frontendTab to (create tab with default profile)' \
		-e '    tell current session of frontendTab' \
		-e '      write text "cd $(ROOT_DIR)/frontend && make dev"' \
		-e '    end tell' \
		-e '  end tell' \
		-e 'end tell'

dev-backend:
	$(MAKE) -C backend dev

dev-frontend:
	$(MAKE) -C frontend dev

# ── Dependencies ─────────────────────────────────────────────

sync:
	$(MAKE) -C backend sync
	cd frontend && bun install

# ── Build ────────────────────────────────────────────────────

build:
	$(MAKE) -C frontend build

# ── Lint / Format ────────────────────────────────────────────

# Lint only (no fixes)
lint:
	$(MAKE) -C backend lint
	$(MAKE) -C frontend lint

# Auto-fix + format (run after every edit)
clean:
	$(MAKE) -C backend clean
	$(MAKE) -C frontend clean

# Lint + format check (CI, no modifications)
check:
	$(MAKE) -C backend check

# Format only (backend)
format:
	$(MAKE) -C backend format

# TypeScript type check
typecheck:
	$(MAKE) -C frontend typecheck

# ── Tests ────────────────────────────────────────────────────

test:
	$(MAKE) -C backend test

test-cov:
	$(MAKE) -C backend test-cov

# ── API client ───────────────────────────────────────────────

generate-client:
	$(MAKE) -C frontend generate-client

# ── Database ─────────────────────────────────────────────────

migrate:
	$(MAKE) -C backend migrate

migrate-new:
	$(MAKE) -C backend migrate-new msg="$(msg)"

# ── Docker ───────────────────────────────────────────────────

docker-up:
	$(MAKE) -C backend docker-up

docker-down:
	$(MAKE) -C backend docker-down

# ── Cleanup ──────────────────────────────────────────────────

nuke:
	$(MAKE) -C backend nuke
