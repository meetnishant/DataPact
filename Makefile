PYTHON ?= python3
PYTEST = $(PYTHON) -m pytest
BLACK = $(PYTHON) -m black
RUFF = $(PYTHON) -m ruff
MYPY = $(PYTHON) -m mypy

.PHONY: test test-quick test-core test-versioning test-banking test-concurrency performance coverage lint format typecheck clean
# Run performance & NFR tests and generate JUnit XML report
performance:
	$(PYTEST) tests/test_performance.py tests/test_performance_extra.py --durations=10 --tb=short --junitxml=performance_report.xml

# Run full test suite in parallel with coverage
test:
	$(PYTEST) -n auto --cov=src/datapact --cov-report=term-missing -v

# Quick test run (no coverage)
test-quick:
	$(PYTEST) -n auto -q

# Core validator tests
test-core:
	$(PYTEST) tests/test_validator.py -v

# Versioning tests
test-versioning:
	$(PYTEST) tests/test_versioning.py -v

# Banking/finance scenarios
test-banking:
	$(PYTEST) tests/test_banking_finance.py -v --tb=short

# Concurrency tests
test-concurrency:
	$(PYTEST) tests/test_concurrency.py tests/test_concurrency_mp.py -v

# Generate coverage report (uses pytest-cov)
coverage:
	$(PYTEST) -n auto --cov=src/datapact --cov-report=html

# Format, lint, and type check
format:
	$(BLACK) src/ tests/

lint:
	$(RUFF) check src/ tests/

typecheck:
	$(MYPY) src/

clean:
	rm -rf .pytest_cache .cache .mypy_cache .ruff_cache htmlcov .coverage* coverage.xml build dist *.egg-info reports/*.json
