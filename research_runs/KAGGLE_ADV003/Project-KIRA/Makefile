.PHONY: help setup gate run dev api brain fixtures test lint fmt frontend docker clean
.DEFAULT_GOAL := help

SCALE ?= tiny
PY    ?= python

help:
	@echo "make setup            install deps (uv if present, else pip)"
	@echo "make gate N=0         run gate N (0..7) or N=all"
	@echo "make run SCALE=tiny   full pipeline: tiny | small | full"
	@echo "make dev              FastAPI :8000 + Vite :5173"
	@echo "make brain            regenerate brain/PROJECT_CONTEXT.md"
	@echo "make frontend         npm build + force-add dist (do this before deploying)"
	@echo "make test / lint / fmt"

setup:
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -e ".[dev]"; \
	else \
		$(PY) -m pip install -e ".[dev]"; \
	fi

# `make gate 0` and `make gate N=0` both work.
gate:
	@$(PY) -m tools.gates $(if $(N),$(N),$(filter-out gate,$(MAKECMDGOALS)))
	@$(PY) -m tools.brain_update
%:
	@:

fixtures:
	@$(PY) -m mcdl.fixtures

run:
	@MCDL_SCALE=$(SCALE) $(PY) -m tools.run_pipeline

api:
	@$(PY) -m uvicorn api.main:app --reload --port 8000

dev:
	@echo "API  -> http://localhost:8000/api/health"
	@echo "UI   -> http://localhost:5173"
	@$(PY) -m uvicorn api.main:app --reload --port 8000 & \
	 cd frontend && npm run dev

brain:
	@$(PY) -m tools.brain_update

frontend:
	cd frontend && npm ci && npm run build
	git add -f frontend/dist
	@echo "dist built and staged. Commit, then push to the Space remote."

test:
	@$(PY) -m pytest -m "not slow"

lint:
	@$(PY) -m ruff check .

fmt:
	@$(PY) -m ruff format . && $(PY) -m ruff check --fix .

docker:
	docker build -t mcdl . && docker run --rm -p 7860:7860 mcdl

clean:
	@rm -rf artifacts/run_* artifacts/gates.json artifacts/LATEST
	@find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
