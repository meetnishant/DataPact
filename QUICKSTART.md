# Quick Start Guide

## Installation & Setup

### 1. Clone or Download the Repository
```bash
cd /path/to/DataPact
```

### 2. Install Dependencies
```bash
python3 -m pip install --user pyyaml pandas pyarrow pytest pytest-cov
```

Optional: Install dev tools for linting and type checking
```bash
python3 -m pip install --user black ruff mypy
```

Optional: Install database drivers for Postgres/MySQL sources
```bash
python3 -m pip install --user "psycopg2-binary>=2.9" "pymysql>=1.1"
```

### 3. Verify Installation
```bash
PYTHONPATH=./src python3 -c "from datapact import Contract; print('✓ Ready')"
```

## Running the CLI

Set up PYTHONPATH for convenience:
```bash
export PYTHONPATH="$(pwd)/src"
```

### Validate Data
```bash
python3 src/datapact/cli.py validate \
  --contract tests/fixtures/customer_contract.yaml \
  --data tests/fixtures/valid_customers.csv
```

### Validate an ODCS Contract
```bash
python3 src/datapact/cli.py validate \
  --contract tests/fixtures/odcs_minimal.yaml \
  --contract-format odcs \
  --odcs-object customers \
  --data tests/fixtures/valid_customers.csv
```

### Validate an API Pact Contract
```bash
python3 src/datapact/cli.py validate \
  --contract tests/fixtures/pact_user_api.json \
  --contract-format pact \
  --data tests/fixtures/valid_customers.csv
```

**Note:** Pact contracts infer schema from API response bodies. Quality rules must be added manually if needed.

Contract format is auto-detected when not specified.

### Validate a Database Table
```bash
python3 src/datapact/cli.py validate \
  --contract tests/fixtures/customer_contract.yaml \
  --db-type sqlite \
  --db-path ./sample.db \
  --db-table customers
```

### Infer Contract from Data
```bash
python3 src/datapact/cli.py init \
  --contract my_contract.yaml \
  --data my_data.csv
```

### Profile Contract with Rules
```bash
python3 src/datapact/cli.py profile \
  --contract my_profile.yaml \
  --data my_data.csv
```

### Override Rule Severity
```bash
python3 src/datapact/cli.py validate \
  --contract my_contract.yaml \
  --data my_data.csv \
  --severity-override status.not_null=warn
```

### Add SLA and Schema Drift Policy
```yaml
schema:
  extra_columns:
    severity: WARN

sla:
  min_rows: 100
  max_rows:
    value: 100000
    severity: WARN
```

### Add Flatten Metadata (Noop by Default)
```yaml
flatten:
  enabled: false
  separator: "."
```

### Chunked Validation and Sampling
```bash
python3 src/datapact/cli.py validate \
  --contract my_contract.yaml \
  --data my_data.csv \
  --chunksize 50000

python3 src/datapact/cli.py validate \
  --contract my_contract.yaml \
  --data my_data.csv \
  --sample-rows 10000
```

Chunked validation is supported for CSV and JSONL inputs.

### Custom Rule Plugins
```bash
python3 src/datapact/cli.py validate \
  --contract my_contract.yaml \
  --data my_data.csv \
  --plugin mypkg.rules
```

### Policy Packs
```yaml
policies:
  - name: pii_basic
    overrides:
      fields:
        phone:
          rules:
            regex:
              value: '^\\+1[0-9]{10}$'
              severity: WARN
```

### Report Sinks
```bash
python3 src/datapact/cli.py validate \
  --contract my_contract.yaml \
  --data my_data.csv \
  --report-sink file \
  --report-sink stdout
```

```bash
python3 src/datapact/cli.py validate \
  --contract my_contract.yaml \
  --data my_data.csv \
  --report-sink webhook \
  --report-webhook-url https://example.com/hook \
  --report-webhook-header "Authorization: Bearer token"
```

Custom rules run on full data; in streaming mode they run only when sampling is enabled.

## Running Tests

```bash
# Install test dependencies
python3 -m pip install --user pytest pytest-cov

# Run tests
export PYTHONPATH=./src
pytest tests/test_validator.py -v

# Run MySQL-backed tests
export DATAPACT_MYSQL_TESTS=1
export DATAPACT_MYSQL_PASSWORD=<your-mysql-password>
export DATAPACT_MYSQL_HOST=127.0.0.1
export DATAPACT_MYSQL_PORT=3306
export DATAPACT_MYSQL_USER=root
export DATAPACT_MYSQL_DB=datapact_test
export DATAPACT_MYSQL_TABLE=customers
pytest tests/test_db_source.py -v

# Check total coverage percentage
datapact-coverage --min 80
```

## Code Quality

With dev tools installed:

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Viewing Reports

JSON reports are saved to `./reports/` with timestamps:
```bash
cat reports/20260208_044449.json | python3 -m json.tool
```

## Common Issues

**ImportError: No module named 'yaml'**
- Install pyyaml: `python3 -m pip install --user pyyaml`

**PYTHONPATH not set**
- Set it: `export PYTHONPATH="$(pwd)/src"`

**Permission errors on install**
- Use `--user` flag: `python3 -m pip install --user <package>`
- Or use a virtual environment: `python3 -m venv venv && source venv/bin/activate`
