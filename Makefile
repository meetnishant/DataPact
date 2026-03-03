PYTHON ?= python3
PYTEST = $(PYTHON) -m pytest
BLACK = $(PYTHON) -m black
RUFF = $(PYTHON) -m ruff
MYPY = $(PYTHON) -m mypy

MYSQL_CONTAINER = datapact-mysql
MYSQL_PORT      = 3307
MYSQL_PASSWORD  = testpass
MYSQL_DB        = datapact_test
MYSQL_TABLE     = customers
MYSQL_ENV       = DATAPACT_MYSQL_TESTS=1 \
                  DATAPACT_MYSQL_HOST=127.0.0.1 \
                  DATAPACT_MYSQL_PORT=$(MYSQL_PORT) \
                  DATAPACT_MYSQL_USER=root \
                  DATAPACT_MYSQL_PASSWORD=$(MYSQL_PASSWORD) \
                  DATAPACT_MYSQL_DB=$(MYSQL_DB) \
                  DATAPACT_MYSQL_TABLE=$(MYSQL_TABLE)

.PHONY: test test-quick test-core test-versioning test-banking test-concurrency performance coverage lint format typecheck clean mysql-up mysql-down

# ── MySQL helpers ─────────────────────────────────────────────────────────────

# Start a fresh MySQL container and seed test data
mysql-up:
	@docker rm -f $(MYSQL_CONTAINER) > /dev/null 2>&1 || true
	@docker run -d --name $(MYSQL_CONTAINER) \
		-e MYSQL_ROOT_PASSWORD=$(MYSQL_PASSWORD) \
		-e MYSQL_DATABASE=$(MYSQL_DB) \
		-p $(MYSQL_PORT):3306 \
		mysql:8.0 --default-authentication-plugin=mysql_native_password > /dev/null
	@echo "Waiting for MySQL to be ready..."
	@for i in $$(seq 1 30); do \
		docker exec $(MYSQL_CONTAINER) mysqladmin ping -h 127.0.0.1 -u root -p$(MYSQL_PASSWORD) --silent 2>/dev/null && echo "MySQL ready." && break; \
		sleep 2; \
	done
	@docker exec $(MYSQL_CONTAINER) mysql -u root -p$(MYSQL_PASSWORD) $(MYSQL_DB) 2>/dev/null -e \
		"CREATE TABLE IF NOT EXISTS customers (id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255) NOT NULL, age INT NOT NULL); \
		 INSERT IGNORE INTO customers (id, email, age) \
		 SELECT n, CONCAT('user',n,'@example.com'), 20+(n%60) \
		 FROM (WITH RECURSIVE nums(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM nums WHERE n<150) SELECT n FROM nums) t;"

# Stop and remove the MySQL container
mysql-down:
	-@docker rm -f $(MYSQL_CONTAINER) > /dev/null 2>&1 && echo "MySQL container removed."

# ── Test targets ──────────────────────────────────────────────────────────────

# Run performance & NFR tests and generate JUnit XML report
performance:
	$(PYTEST) tests/test_performance.py tests/test_performance_extra.py --durations=10 --tb=short --junitxml=performance_report.xml

# Run full test suite: parallel phase (non-perf), then sequential phase (perf).
# MySQL container starts before and is removed after, even on failure.
test: mysql-up
	@trap 'docker rm -f $(MYSQL_CONTAINER) > /dev/null 2>&1 && echo "MySQL container removed."' EXIT; \
	$(MYSQL_ENV) $(PYTEST) -n auto \
		--ignore=tests/test_performance.py \
		--ignore=tests/test_performance_extra.py \
		--cov=src/datapact --cov-report=term-missing -v && \
	$(MYSQL_ENV) $(PYTEST) tests/test_performance.py tests/test_performance_extra.py \
		-v --cov=src/datapact --cov-report=term-missing --cov-append

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
