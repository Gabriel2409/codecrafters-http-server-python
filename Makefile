help:
	@echo "Available targets:"
	@echo "  - req: Creates the requirements with uv using Pipfile"
	@echo "  - venv: Creates the virtual env with uv" 
	@echo "  - sync: Sync uv venv with requirements.txt"
	@echo "  - run: Launches the app"
	@echo "  - watch: Launches the app with change detection"

req:
	pipenv requirements --dev | uv pip compile --generate-hashes -o requirements.txt -
venv:
	uv venv
sync:
	uv pip sync requirements.txt
run:
	.venv/bin/python -m app.main
watch: 
	.venv/bin/watchmedo auto-restart -p '*.py' -R  -- .venv/bin/python -m app.main


