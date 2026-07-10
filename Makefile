# CI local del proyecto. En Windows sin make, usar check.bat (equivalente).
PY = venv_build/Scripts/python.exe

check: lint fmt-check test

lint:
	$(PY) -m ruff check .

fmt:
	$(PY) -m ruff format .

fmt-check:
	$(PY) -m ruff format --check .

test:
	$(PY) -m pytest -q

hooks:
	$(PY) scripts/install_hooks.py

.PHONY: check lint fmt fmt-check test hooks
