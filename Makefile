



dev:
	source .venv/bin/activate && uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.12 langgraph dev --allow-blocking



test: 	
	uv run pytest -v -s


backend: 
	@echo "Starting backend server on http://localhost:8004"
	source .venv/bin/activate && uvicorn src.main:app --reload --port 8004
