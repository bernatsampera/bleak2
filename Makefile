# ===============================
# Project Makefile
# ===============================

PYTHON_VERSION = 3.12
BACKEND_PORT = 8004
FRONTEND_PORT = 5173
VENV = .venv/bin/activate
BACKEND_CMD = uvicorn src.main:app --reload --port $(BACKEND_PORT)
FRONTEND_CMD = cd frontend && npm run dev


# ===============================
# Development
# ===============================

## Start backend and frontend
dev: 
	@echo "Starting backend (http://localhost:$(BACKEND_PORT)) and frontend (http://localhost:$(FRONTEND_PORT))..."
	make kill && \
	make run-both

## Start backend only
backend:
	@echo "Starting backend on http://localhost:$(BACKEND_PORT)"
	@source $(VENV) && $(BACKEND_CMD)

## Start frontend only
frontend:
	@echo "Starting frontend on http://localhost:$(FRONTEND_PORT)"
	@$(FRONTEND_CMD)

## Run backend and frontend together
run-both:
	@trap 'kill %1 %2 2>/dev/null || true' EXIT; \
	(source $(VENV) && $(BACKEND_CMD) &) && \
	($(FRONTEND_CMD) &) && \
	wait


# ===============================
# Testing & Tools
# ===============================

## Run tests
test:
	@uv run pytest -v -s

## Launch LangGraph Studio
lgstudio:
	@source $(VENV) && \
	uvx --refresh --from "langgraph-cli[inmem]" \
		--with-editable . \
		--python $(PYTHON_VERSION) \
		langgraph dev --allow-blocking


# ===============================
# Utilities
# ===============================

kill:
	make kill-backend && make kill-frontend

## Kill backend process
kill-backend:
	@echo "Stopping backend server..."
	@pkill -f "uvicorn src.main:app" || true
	@sleep 1
	@pkill -9 -f "uvicorn src.main:app" || true

## Kill frontend process
kill-frontend:
	@pkill -f "npm run dev" || true

## Show available commands
help:
	@echo "Available commands:"
	@grep -E '^##' Makefile | sed -e 's/## //'
