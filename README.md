# Data Contract Validator

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
  version: 1.0.0
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
dcv validate --contract customer_contract.yaml --data customers.csv
```

### Infer Contract from Data

```bash
dcv init --contract new_contract.yaml --data data.csv
```

## CLI Usage

### Validate Command

```bash
dcv validate --contract <path/to/contract.yaml> --data <path/to/data> [--format auto|csv|parquet|jsonl] [--output-dir ./reports]
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
dcv init --contract <path/to/output.yaml> --data <path/to/data>
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
    "version": "1.0.0"
  },
  "dataset": {
    "name": "customers"
  },
  "metadata": {
    "timestamp": "2024-01-15T10:30:45.123456",
    "tool_version": "0.1.0"
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

```bash
# Run tests
pytest

# With coverage
pytest --cov=src/data_contract_validator
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
src/data_contract_validator/
├── __init__.py           # Package exports
├── contracts.py          # Contract parsing (YAML → Pydantic models)
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
├── test_validator.py     # Test suite
├── test_versioning.py    # Version feature tests
└── fixtures/             # Sample contracts and data
```

## Contract Versioning

The validator supports multiple contract versions with automatic migration and compatibility checking:

- **Current Version**: 2.0.0
- **Supported Versions**: 1.0.0, 1.1.0, 2.0.0
- **Auto-Migration**: Old contracts automatically upgrade to the latest version
- **Breaking Changes**: Tracked and reported in validation output

See [docs/VERSIONING.md](docs/VERSIONING.md) for detailed version history, migration guide, and breaking changes.

## Contract Versioning

The validator supports multiple contract versions with automatic migration and compatibility checking:

- **Current Version**: 2.0.0
- **Supported Versions**: 1.0.0, 1.1.0, 2.0.0
- **Auto-Migration**: Old contracts automatically upgrade to the latest version
- **Breaking Changes**: Tracked and reported in validation output

See [docs/VERSIONING.md](docs/VERSIONING.md) for detailed version history, migration guide, and breaking changes.

## License

MIT
