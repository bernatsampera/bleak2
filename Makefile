# Start LangGraph Studio and frontend
dev:
	@echo "Starting LangGraph Studio and frontend[](http://localhost:5173)..."
	@source .venv/bin/activate && uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.12 langgraph dev --allow-blocking & cd frontend && npm run dev & wait

# Start frontend only
frontend:
	@echo "Starting frontend on http://localhost:5173"
	@cd frontend && npm run dev

# Run tests
test:
	@uv run pytest -v -s
