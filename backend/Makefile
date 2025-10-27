APP_ENV ?= dev
PYTHON ?= python3

.PHONY: gen-keys
keys:
	@./scripts/gen_keys.sh

.PHONY: clean
clean:
	docker compose down -v --remove-orphans


