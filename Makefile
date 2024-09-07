help:
	@echo "Available targets:"
	@echo "  - req: Creates the requirements with uv using Pipfile"
	@echo "  - venv: Creates the virtual env with uv" 
	@echo "  - sync: Sync uv venv with requirements.txt"
	@echo "  - run: Launches the app"
	@echo "  - watch: Launches the app with change detection"
	@echo "  - test: Launches the tests"

req:
	pipenv requirements --dev | uv pip compile  -o requirements.txt -
venv:
	uv venv
sync:
	uv pip sync requirements.txt
run:
	uv run -- python -m app.main --directory /tmp/
watch: 
	uv run -- watchmedo auto-restart -p '*.py' -R  -- python -m app.main --directory /tmp/
test: 
	uv run -- pytest -rA


