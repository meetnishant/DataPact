# DataPact

Validate datasets against YAML-based data contracts to ensure data quality, schema compliance, and distribution health.

## Features

- **Schema Validation**: Check columns, types, and required fields
- **Quality Rules**: Validate nulls, uniqueness, ranges, regex patterns, and enums
- **Distribution Monitoring**: Detect drift in numeric column statistics
- **Contract Versioning**: Track contract evolution with automatic migration
- **Multiple Formats**: Support CSV, Parquet, and JSON Lines
- **CI/CD Ready**: Exit codes for automation pipelines
- **Detailed Reporting**: JSON reports with machine-readable errors

## Installation

```bash
pip install -e .
```

## Quick Start

### Define a Contract

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

### Infer Contract from Data

```bash
datapact init --contract new_contract.yaml --data data.csv
```

## CLI Usage

### Validate Command

```bash
datapact validate --contract <path/to/contract.yaml> --data <path/to/data> [--format auto|csv|parquet|jsonl] [--output-dir ./reports]
```

**Options:**
- `--contract`: Path to contract YAML file (required)
- `--data`: Path to data file (required)
- `--format`: Data format. Default: auto-detect from file extension
- `--output-dir`: Directory for JSON report. Default: ./reports

**Exit Codes:**
- `0`: Validation passed
- `1`: Validation failed

### Init Command

```bash
datapact init --contract <path/to/output.yaml> --data <path/to/data>
```

Infers a starter contract from a dataset (columns and types only).

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

### Distribution Rules

- `mean`: Expected mean for numeric column
- `std`: Expected standard deviation
- `max_drift_pct`: Alert if mean/std changes by >X%
- `max_z_score`: Flag outliers with |z-score| > threshold

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
    "timestamp": "2026-02-08T10:30:45.123456",
    "tool_version": "0.2.0"
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

```bash
# Run tests
pytest

# With coverage
pytest --cov=src/datapact

# Coverage check with total percent
datapact-coverage --min 80
```

## Development

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
