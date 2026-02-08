PYTHON ?= python3
PYTEST = $(PYTHON) -m pytest

.PHONY: test test-quick coverage clean

# Run full test suite in parallel with coverage
test:
	$(PYTEST) -n auto --cov=src/data_contract_validator --cov-report=term-missing -v

# Quick test run (no coverage)
test-quick:
	$(PYTEST) -n auto -q

# Generate coverage report (uses pytest-cov)
coverage:
	$(PYTEST) -n auto --cov=src/data_contract_validator --cov-report=html

clean:
	rm -rf .pytest_cache .cache htmlcov .coverage* reports/*.json
