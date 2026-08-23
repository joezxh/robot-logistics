# Unified quality + build gate for the robot-logic monorepo.
#
# Modeled on robot-control-stack's top-level Makefile (gcccompile/clangcompile +
# lint/format/test). For a Python-first monorepo the equivalent gate is ruff
# (lint+format) + pytest across all subprojects, plus an editable install of the
# shared contract so cross-subproject imports resolve.

PYTHON ?= python
SUBPROJECTS = shared/python rcs robot-app vla-training simulation/backend

.PHONY: install
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install ruff pytest
	$(PYTHON) -m pip install -e shared/python
	$(PYTHON) -m pip install -r simulation/backend/requirements.txt
	$(PYTHON) -m pip install -r rcs/requirements.txt
	$(PYTHON) -m pip install -r robot-app/requirements.txt

.PHONY: lint
lint:
	$(PYTHON) -m ruff check $(SUBPROJECTS)

.PHONY: format
format:
	$(PYTHON) -m ruff format $(SUBPROJECTS)
	$(PYTHON) -m ruff check --fix $(SUBPROJECTS)

.PHONY: test
test:
	cd shared/python && $(PYTHON) -m pytest tests -q
	cd rcs && $(PYTHON) -m pytest tests -q
	cd robot-app && $(PYTHON) -m pytest tests -q
	cd simulation/backend && $(PYTHON) -m pytest tests -q
	cd vla-training && $(PYTHON) -m pytest -q

.PHONY: test-integration
test-integration:
	cd vla-training && $(PYTHON) -m pytest tests/test_integration_rcs.py -q

.PHONY: clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
