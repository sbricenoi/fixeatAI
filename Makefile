PY=python3
PIP=pip

.PHONY: venv install run api mcp kb lint fmt test

venv:
	$(PY) -m venv .venv
	. .venv/bin/activate && $(PIP) install --upgrade pip
	. .venv/bin/activate && $(PIP) install -e .

install:
	. .venv/bin/activate && $(PIP) install -e .

run:
	. .venv/bin/activate && uvicorn app.main:app --reload --port 8000 --env-file .env

mcp:
	. .venv/bin/activate && uvicorn mcp.server_demo:app --reload --port 7070 --env-file .env

kb:
	. .venv/bin/activate && $(PY) services/kb/demo_kb.py

lint:
	. .venv/bin/activate && ruff check .

fmt:
	. .venv/bin/activate && isort . && black .

test:
	. .venv/bin/activate && pytest -q


