# DataPact

Validate datasets against data contracts to ensure schema compliance, data quality, and distribution health. DataPact supports DataPact YAML, ODCS v3.1.0, and Pact API contracts, with a provider architecture and a CLI designed for CI/CD pipelines.

## Features

- **Schema Validation**: Check columns, types, and required fields
- **Quality Rules**: Validate nulls, uniqueness, ranges, regex patterns, and enums
- **Rule Severity**: Mark rules as WARN or ERROR, with CLI overrides
- **Schema Drift**: Control extra column handling with WARN/ERROR policies
- **Distribution Monitoring**: Detect drift in numeric column statistics
- **Profiling**: Auto-generate rule baselines from data
- **SLA Checks**: Enforce row count and freshness constraints
- **Big Data Support**: Chunked validation with optional sampling
- **Custom Rule Plugins**: Load rule logic from plugin modules
- **Policy Packs**: Apply reusable rule bundles by name
- **Contract Versioning**: Track contract evolution with automatic migration
- **Multiple Formats**: Support CSV, Parquet, and JSON Lines
- **Database Sources**: Validate Postgres, MySQL, and SQLite tables
- **ODCS Support**: Validate Open Data Contract Standard v3.1.0 contracts
- **API Pact Support**: Infer DataPact contracts from Pact API contracts via type inference
- **Contract Providers**: Load DataPact YAML, ODCS, or Pact JSON contracts via provider dispatch
- **Normalization Scaffold**: Contract-aware normalization (flatten config; noop unless enabled)
- **CI/CD Ready**: Exit codes for automation pipelines
- **Detailed Reporting**: JSON reports with machine-readable errors
- **Report Sinks**: Send reports to files, stdout, or webhooks

See [FEATURES.md](FEATURES.md) for a functional feature list with compact examples.

## Installation

```bash
pip install -e .
```

Note: `pact-python` is included as a base dependency so DataPact can ingest Pact JSON contracts for schema inference.

Optional database drivers:

```bash
pip install -e ".[db]"
```

## Quick Start

### Define a Contract (DataPact YAML)

Create `customer_contract.yaml`:

```yaml
contract:
  name: customer_data
  version: 2.0.0
dataset:
  name: customers
fields:
  - name: customer_id
    type: integer
    required: true
    rules:
      unique: true
  - name: email
    type: string
    required: true
    rules:
      regex: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
      unique: true
  - name: age
    type: integer
    rules:
      min: 0
      max: 150
  - name: status
    type: string
    rules:
      enum: [active, inactive, suspended]
  - name: score
    type: float
    distribution:
      mean: 50.0
      std: 15.0
      max_drift_pct: 10.0
```

### Validate Data

```bash
datapact validate --contract customer_contract.yaml --data customers.csv
```

Validate a database table:

```bash
datapact validate \
  --contract customer_contract.yaml \
  --db-type postgres \
  --db-host localhost \
  --db-port 5432 \
  --db-user app \
  --db-password secret \
  --db-name appdb \
  --db-table customers
```

Validate an ODCS contract:

```bash
datapact validate \
  --contract my_contract.odcs.yaml \
  --contract-format odcs \
  --odcs-object customers \
  --data customers.csv
```

Validate a Pact API contract (schema inferred from Pact JSON):

```bash
datapact validate \
  --contract pact_user_api.json \
  --contract-format pact \
  --data api_response.json
```

Type inference happens automatically. Add quality/distribution rules manually to the inferred contract if needed.

### Infer Contract from Data

```bash
datapact init --contract new_contract.yaml --data data.csv
```

### Profile Contract with Rules

```bash
datapact profile --contract new_profile.yaml --data data.csv
```

## Pact Integration

DataPact uses Pact contracts as an input format for schema inference. It consumes Pact JSON contracts commonly produced by pact-python, then maps the response body examples to DataPact fields.

### Pact-Python Features Leveraged by DataPact

- **Pact JSON contract format**: Reads Pact JSON files as the source of truth
- **Consumer/Provider metadata**: Uses `consumer.name` and `provider.name` to build a DataPact contract name
- **Interactions array**: Requires Pact interactions to locate an API response
- **Response body examples**: Infers field names and types from `interactions[0].response.body`
- **Type mapping**: Maps JSON primitives to DataPact types (int → integer, float → float, bool → boolean, str → string)

### Pact-Python Features NOT Leveraged by DataPact

- **Mock server and stubs**: DataPact validates from files, not live servers
- **Consumer-driven test execution**: DataPact is a validation tool, not a testing framework
- **Provider verification**: No provider verification against a running service
- **Pact Broker integration**: Only local Pact JSON files are supported
- **Matching rules and generators**: Matchers are not evaluated; only example values are used
- **Message Pacts**: Only REST API response bodies are supported
- **CLI tooling for Pact**: DataPact does not invoke pact-python CLI helpers

### Example: Pact JSON to DataPact Fields

Pact contract snippet:

```json
{
  "consumer": {"name": "web-frontend"},
  "provider": {"name": "user-api"},
  "interactions": [
    {
      "response": {
        "status": 200,
        "body": {
          "id": 123,
          "name": "Alice Smith",
          "email": "alice@example.com",
          "age": 30,
          "active": true
        }
      }
    }
  ]
}
```

Inferred DataPact fields:

```yaml
fields:
  - name: id
    type: integer
    required: false
  - name: name
    type: string
    required: false
  - name: email
    type: string
    required: false
  - name: age
    type: integer
    required: false
  - name: active
    type: boolean
    required: false
```

### Manual Additions Required for Pact Contracts

Pact does not define quality or distribution rules. Add those rules manually in DataPact YAML:

```yaml
fields:
  - name: id
    type: integer
    rules:
      unique: true
  - name: email
    type: string
    rules:
      regex: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
  - name: age
    type: integer
    rules:
      min: 0
      max: 150
```

## CLI Usage

### Validate Command

```bash
datapact validate --contract <path/to/contract.yaml> --data <path/to/data> [--format auto|csv|parquet|jsonl] [--output-dir ./reports]
```

**Options:**
- `--contract`: Path to contract file (required). Supports `.yaml` (DataPact/ODCS) or `.json` (Pact)
- `--contract-format`: Contract format (auto, datapact, odcs, pact). Default: auto
- `--odcs-object`: ODCS schema object name or id (required if multiple objects)
- `--data`: Path to data file (required)
- `--format`: Data format. Default: auto-detect from file extension
- `--output-dir`: Directory for JSON report. Default: ./reports
- `--db-type`: Database type (postgres, mysql, sqlite)
- `--db-host`: Database host (RDBMS only)
- `--db-port`: Database port
- `--db-user`: Database user (RDBMS only)
- `--db-password`: Database password (RDBMS only)
- `--db-name`: Database name (RDBMS only)
- `--db-table`: Database table to read
- `--db-query`: SQL query to read (overrides table)
- `--db-path`: SQLite database file path
- `--db-connect-timeout`: DB connection timeout in seconds
- `--db-chunksize`: Chunk size for DB streaming validation
- `--report-sink`: Report sink (file, stdout, webhook). Repeatable
- `--report-webhook-url`: Webhook URL for report sink `webhook`
- `--report-webhook-header`: Webhook header (Key: Value). Repeatable
- `--report-webhook-timeout`: Webhook timeout in seconds
- `--severity-override`: Override rule severity (format: field.rule=warn)
- `--chunksize`: Stream validation in chunks (CSV/JSONL)
- `--sample-rows`: Sample N rows for validation
- `--sample-frac`: Sample fraction for validation
- `--sample-seed`: Random seed for sampling
- `--plugin`: Plugin module path for custom rules (repeatable)

**Exit Codes:**
- `0`: Validation passed
- `1`: Validation failed

### Init Command

```bash
datapact init --contract <path/to/output.yaml> --data <path/to/data>
```

Infers a starter contract from a dataset (columns and types only).

### Profile Command

```bash
datapact profile --contract <path/to/output.yaml> --data <path/to/data>
```

**Options:**
- `--max-enum-size`: Max enum size for profiling (default: 20)
- `--max-enum-ratio`: Max enum ratio for profiling (default: 0.2)
- `--unique-threshold`: Unique ratio threshold (default: 0.99)
- `--null-ratio-buffer`: Buffer added to observed null ratio (default: 0.01)
- `--range-buffer-pct`: Buffer added to min/max (default: 0.05)
- `--max-drift-pct`: Drift threshold for distributions (default: 10.0)
- `--max-z-score`: Outlier z-score threshold (default: 3.0)
- `--no-distribution`: Disable distribution profiling
- `--no-date-regex`: Disable date regex inference

## Supported Data Types

In contracts, use:
- `integer` - int32, int64
- `float` - float32, float64
- `string` - text/object columns
- `boolean` - bool

## Validation Rules

### Field Rules

- `not_null`: Required, no nulls allowed
- `unique`: All values must be unique
- `min`: Minimum numeric value
- `max`: Maximum numeric value
- `regex`: Regex pattern match
- `enum`: Value must be in list
- `max_null_ratio`: Tolerate up to X% nulls (0.0 to 1.0)
- `freshness_max_age_hours`: Max age in hours for timestamp fields

Rules can include severity metadata:

```yaml
rules:
  not_null:
    value: true
    severity: WARN
  max:
    value: 100
    severity: ERROR
```

### Distribution Rules

- `mean`: Expected mean for numeric column
- `std`: Expected standard deviation
- `max_drift_pct`: Alert if mean/std changes by >X%
- `max_z_score`: Flag outliers with |z-score| > threshold

### Schema Drift Policy

```yaml
schema:
  extra_columns:
    severity: WARN
```

### Normalization (Flatten Metadata)

```yaml
flatten:
  enabled: false
  separator: "."
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

### SLA Checks

```yaml
sla:
  min_rows: 100
  max_rows:
    value: 100000
    severity: WARN

fields:
  - name: event_time
    type: string
    rules:
      freshness_max_age_hours: 24
```

### Chunked Validation and Sampling

```bash
datapact validate --contract contract.yaml --data data.csv --chunksize 50000
datapact validate --contract contract.yaml --data data.csv --sample-rows 10000
```

Chunked validation is supported for CSV and JSONL inputs.

### Custom Rule Plugins

```yaml
fields:
  - name: score
    type: float
    rules:
      custom:
        field_max_value:
          value: 100
          severity: WARN

custom_rules:
  - name: dataset_min_rows
    config:
      value: 1000
    severity: ERROR
```

```bash
datapact validate --contract contract.yaml --data data.csv --plugin mypkg.rules
```

Custom rules run on full data; in streaming mode they run only when sampling is enabled.

## Report Format

JSON reports are saved to `./reports/<timestamp>.json`:

```json
{
  "passed": false,
  "contract": {
    "name": "customer_data",
    "version": "2.0.0"
  },
  "dataset": {
    "name": "customers"
  },
  "metadata": {
    "timestamp": "2026-02-13T10:30:45.123456",
    "tool_version": "2.0.0"
  },
  "summary": {
    "error_count": 2,
    "warning_count": 1
  },
  "errors": [
    {
      "code": "QUALITY",
      "field": "email",
      "message": "has 1 values not matching regex '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'",
      "severity": "ERROR"
    }
  ]
}
```

## Testing

For scenario coverage details, see [Banking & Finance Test Cases](#banking--finance-test-cases).



### Performance & NFR Tests

Automated performance and non-functional requirements (NFR) tests ensure DataPact is robust and efficient at scale. These tests cover:
- Large dataset validation time (1M+ rows)
- Contract parsing speed (large YAML contracts)
- CLI startup time
- Memory usage for large files
- Batch/concurrent validation throughput
- Performance degradation with increasing data size

See [PERFORMANCE_NFR_SUMMARY.md](PERFORMANCE_NFR_SUMMARY.md) for the latest results, coverage, and CI integration instructions.

Performance/NFR tests are run automatically in CI (see `.github/workflows/ci.yml`). Reports are uploaded as artifacts for every push and pull request.

To run locally:
```bash
PYTHONPATH=src python3 -m pytest tests/test_performance.py tests/test_performance_extra.py --durations=10 --tb=short --junitxml=performance_report.xml
```
This generates a JUnit XML report with timing and pass/fail status for each scenario.

# Run tests
pytest

# Enable MySQL-backed DB source tests
export DATAPACT_MYSQL_TESTS=1
export DATAPACT_MYSQL_PASSWORD=<your-mysql-password>
export DATAPACT_MYSQL_HOST=127.0.0.1
export DATAPACT_MYSQL_PORT=3306
export DATAPACT_MYSQL_USER=root
export DATAPACT_MYSQL_DB=datapact_test
export DATAPACT_MYSQL_TABLE=customers
pytest tests/test_db_source.py -v

# With coverage
pytest --cov=src/datapact

# Coverage check with total percent
datapact-coverage --min 80
```

## Development

Dependencies are documented in [DEPENDENCIES.md](DEPENDENCIES.md).

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Project Structure

```
src/datapact/
├── __init__.py           # Package exports
├── contracts.py          # Contract parsing (YAML → dataclass models)
├── datasource.py         # Data loading and schema inference
├── cli.py                # CLI entry point
├── reporting.py          # Report generation and serialization
├── versioning.py         # Version management and migration
└── validators/
    ├── __init__.py
    ├── schema_validator.py      # Column/type/required checks
    ├── quality_validator.py     # Null/unique/range/regex/enum checks
    └── distribution_validator.py # Mean/std drift detection
tests/
├── test_validator.py     # Core validator tests
├── test_versioning.py    # Version feature tests
├── test_banking_finance.py # Banking/finance scenarios
├── test_concurrency.py   # Concurrency validation
├── test_concurrency_mp.py # Multiprocessing concurrency
└── fixtures/             # Sample contracts and data
```

## Contract Versioning

The validator supports multiple contract versions with automatic migration and compatibility checking:

- **Current Version**: 2.0.0
- **Supported Versions**: 1.0.0, 1.1.0, 2.0.0
- **Auto-Migration**: Old contracts automatically upgrade to the latest version
- **Breaking Changes**: Tracked and reported in validation output

See [docs/VERSIONING.md](docs/VERSIONING.md) for detailed version history, migration guide, and breaking changes.

## Documentation

- **[docs/EXAMPLES.md](docs/EXAMPLES.md)** — Comprehensive examples for all providers and features (YAML, ODCS, API Pact, quality rules, distributions, custom rules, report sinks, etc.)
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — System architecture and design patterns
- **[FEATURES.md](FEATURES.md)** — Feature checklist with compact examples
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Developer guide including provider pattern

## License

MIT

---

# Banking & Finance Test Cases

## Overview
The test suite covers multi-table data products for commercial banking and institutional finance, with deposits and lending modeled as accounts/loans plus transactions/payments. It also reflects consumer-specific contract needs (strict vs aggregate) to validate schema and quality expectations across different consumption patterns.

## Test Categories

- **PositiveCases**: Valid data rows that should pass all schema and quality checks. These represent typical, correct records for deposits and lending products.
- **NegativeCases**: Rows intentionally containing errors (e.g., missing required fields, invalid dates, negative balances, out-of-range values, or type mismatches). These ensure the validator catches real-world data quality issues.
- **BoundaryCases**: Edge-case rows that test the limits of contract rules (e.g., zero balances, maximum allowed values, dates at the edge of valid ranges). These confirm the validator's correct handling of contract boundaries.

## Example Scenarios

### Deposits
- **Accounts (strict)**: Unique, non-null customer_id and account_id; valid product/status enums; balances within allowed range.
- **Accounts (aggregate)**: customer_id may be 1% null with 99% uniqueness, while other fields remain strict.
- **Transactions**: Valid txn_type/channel enums, valid dates, and amounts within limits (including withdrawals/fees).

### Lending
- **Loans (strict)**: Non-null loan_id and customer_id, valid product/status enums, balances within limits, rates in [0, 0.25].
- **Loans (aggregate)**: customer_id may be 1% null with 99% uniqueness, other fields remain strict.
- **Payments**: Valid payment_status enums, non-negative amounts, and valid dates.

## Usage
Test cases are tagged using `@pytest.mark.PositiveCases`, `@pytest.mark.NegativeCases`, and `@pytest.mark.BoundaryCases` for easy filtering and reporting. See `tests/test_banking_finance.py` for implementation details and `tests/fixtures/` for sample data and contracts.
