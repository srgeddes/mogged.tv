.PHONY: dev build preview lint clean typecheck generate-client

dev:
	bun run dev

build:
	bun run build

preview:
	bun run preview

lint:
	bun run lint

clean:
	bun run lint -- --fix

typecheck:
	bunx tsc --noEmit

generate-client:
	bunx @hey-api/openapi-ts
