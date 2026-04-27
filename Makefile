# Sensei — contributor convenience Makefile.
#
# All targets shell out to .venv/bin/<tool> so local checks match what CI
# runs. See docs/operations/release-playbook.md § Pre-release gate for the
# venv discipline this captures.
#
# CI does NOT use this Makefile — verify.yml invokes pytest/ruff/mypy
# directly. The Makefile is for humans.

VENV     := .venv
PY       := $(VENV)/bin/python
PIP      := $(VENV)/bin/pip
PYTEST   := $(VENV)/bin/pytest
RUFF     := $(VENV)/bin/ruff
MYPY     := $(VENV)/bin/mypy

.PHONY: help setup test lint typecheck validators gate clean

help:
	@echo "Sensei contributor targets:"
	@echo "  make setup       — create .venv and install with dev extras"
	@echo "  make test        — run pytest (full suite, with coverage gate)"
	@echo "  make lint        — run ruff check"
	@echo "  make typecheck   — run mypy --strict"
	@echo "  make validators  — run all ci/check_*.py validators"
	@echo "  make gate        — run lint + typecheck + test + validators"
	@echo "  make clean       — remove .venv, build artifacts, caches"

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e '.[dev]'

setup: $(VENV)
	@echo "Sensei dev environment ready at $(VENV)/"

test: $(VENV)
	$(PYTEST)

lint: $(VENV)
	$(RUFF) check .

typecheck: $(VENV)
	$(MYPY)

validators: $(VENV)
	$(PY) ci/check_foundations.py
	$(PY) ci/check_links.py
	$(PY) ci/check_links.py --root src/sensei/engine
	$(PY) ci/check_changelog_links.py
	$(PY) ci/check_plan_completion.py
	$(PY) ci/check_adr_immutability.py

gate: lint typecheck test validators
	@echo "All local pre-merge gates green."

clean:
	rm -rf $(VENV) build dist src/sensei_tutor.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage
