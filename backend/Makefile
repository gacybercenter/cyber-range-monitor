APP_ENV ?= dev
PYTHON ?= python3

.PHONY: gen-keys
keys:
	@./scripts/gen_keys.sh

.PHONY: clean
clean:
	docker compose down -v --remove-orphans


.PHONY: format
format:
	uv run ruff format ./server

.PHONY: lint
lint:
	uv run ruff check ./server

.PHONY: db
db:
	uv run -m scripts.seed