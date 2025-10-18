# ===============================
# Project Makefile
# ===============================

PYTHON_VERSION = 3.12
FRONTEND_PORT = 5173
VENV = .venv/bin/activate
LGSTUDIO_CMD = uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python $(PYTHON_VERSION) langgraph dev --allow-blocking
FRONTEND_CMD = cd frontend && npm run dev


# ===============================
# Development
# ===============================

## Start LangGraph Studio and frontend
dev:
	@echo "Starting LangGraph Studio and frontend (http://localhost:$(FRONTEND_PORT))..."
	make run-both


## Start frontend only
frontend:
	@echo "Starting frontend on http://localhost:$(FRONTEND_PORT)"
	@$(FRONTEND_CMD)

## Run LangGraph Studio and frontend together
run-both:
	@trap 'kill %1 %2 2>/dev/null || true' EXIT; \
	(source $(VENV) && $(LGSTUDIO_CMD) &) && \
	($(FRONTEND_CMD) &) && \
	wait


# ===============================
# Testing & Tools
# ===============================

## Run tests
test:
	@uv run pytest -v -s




## Show available commands
help:
	@echo "Available commands:"
	@grep -E '^##' Makefile | sed -e 's/## //'
