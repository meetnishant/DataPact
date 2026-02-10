# AI Coding Instructions for DataPact

## Project Overview

**DataPact** is a Python framework that validates datasets (CSV, Parquet, JSON, and database tables) against YAML-defined "data contracts" containing schema, quality, and distribution rules. It produces JSON reports and non-zero exit codes for CI/CD integration.

**Key Goal**: Enable data quality checks in pipelines via a CLI tool (`datapact validate`).

## Architecture at a Glance

The validation pipeline is **modular and sequential**:

1. **Contract Parsing** (`contracts.py`): Load YAML → typed Python models (Contract, Field, FieldRule, DistributionRule)
2. **Data Loading** (`datasource.py`): CSV/Parquet/JSON/DB → pandas DataFrame; auto-detect format
3. **Schema Validation** (`validators/schema_validator.py`): Check columns exist, types match, required fields present
4. **Quality Validation** (`validators/quality_validator.py`): Check nulls, uniqueness, ranges, regex, enums
5. **Distribution Validation** (`validators/distribution_validator.py`): Drift detection (mean/std changes)
6. **Reporting** (`reporting.py`): Aggregate errors/warnings into JSON + console summary
7. **CLI** (`cli.py`): Parse args, orchestrate pipeline, set exit code

**Critical Design**: Schema validation runs first and is blocking (if required columns missing, stop early). Quality and distribution checks are non-blocking (record errors but continue). Only ERRORs trigger non-zero exit code.

## Key Files & Their Responsibilities

| File | Purpose | Example |
|------|---------|---------|
| `src/datapact/contracts.py` | Parse YAML contracts into dataclass models | `Contract.from_yaml("contract.yaml")` returns Contract with fields, rules |
| `src/datapact/datasource.py` | Load data + infer schema | `DataSource("data.csv").load()` returns DataFrame |
| `src/datapact/validators/schema_validator.py` | Column/type/required checks | Fails if required field missing or type mismatch |
| `src/datapact/validators/quality_validator.py` | Null, unique, range, regex, enum checks | `rules.not_null=True` → error if nulls found |
| `src/datapact/validators/distribution_validator.py` | Mean/std drift, outliers | Warnings only (never blocks) |
| `src/datapact/versioning.py` | Contract version management, migration, compatibility | Supports v1.0.0, v1.1.0, v2.0.0; auto-migrates old contracts |
| `src/datapact/reporting.py` | ErrorRecord model + JSON/console output | Saves to `./reports/<timestamp>.json`; includes version info |
| `src/datapact/cli.py` | Entry point (`datapact` command) | `datapact validate --contract c.yaml --data d.csv` with version checks |

## Contract YAML Format

```yaml
contract:
  name: my_data
  version: 1.0.0
dataset:
  name: source_system
fields:
  - name: user_id
    type: integer
    required: true
    rules:
      unique: true
  - name: email
    type: string
    required: true
    rules:
      regex: '^[a-z]+@[a-z]+\.[a-z]+$'
      unique: true
  - name: age
    type: integer
    rules:
      min: 0
      max: 150
  - name: score
    type: float
    distribution:
      mean: 50.0
      std: 15.0
      max_drift_pct: 10.0
```

Supported types: `integer`, `float`, `string`, `boolean`.  
Supported rules: `not_null`, `unique`, `min`, `max`, `regex`, `enum`, `max_null_ratio`.  
Distribution rules: `mean`, `std`, `max_drift_pct`, `max_z_score`.

Supported data inputs: CSV, Parquet, JSON Lines, and database tables (Postgres, MySQL, SQLite).

## Common Workflows

### Run validation
```bash
datapact validate --contract tests/fixtures/customer_contract.yaml --data tests/fixtures/valid_customers.csv
```
- Prints summary to console
- Saves JSON to `./reports/<timestamp>.json`
- Exit code 0 if no ERRORs, 1 otherwise

### Infer contract from data
```bash
datapact init --contract new_contract.yaml --data data.csv
```
Outputs YAML template with columns and inferred types (useful starting point).

### Run tests
```bash
pytest tests/test_validator.py -v
```
Tests live in `tests/test_validator.py` using fixtures in `tests/fixtures/`.

### Type check & lint
```bash
mypy src/
ruff check src/ tests/
black src/ tests/ --check
```

### Install for development
```bash
pip install -e ".[dev]"
```

## Project Conventions & Patterns

### Error Messages
All validators return `(bool, List[str])`. Error strings follow pattern:
```
"ERROR: <field>: <description>" or "WARN: <field>: <description>"
```
Parser extracts severity prefix; include it in message.

### Validator Interface
Each validator in `validators/` must implement:
```python
def validate(self) -> Tuple[bool, List[str]]:
    """Return (is_valid, error_messages)."""
```

### Type Mapping
pandas dtype → contract type:
- `int*` → `integer`
- `float*` → `float`
- `object`, `string` → `string`
- `bool` → `boolean`

### Exit Codes
- `0`: Validation passed (no ERRORs)
- `1`: Validation failed (ERRORs present) or exception

### Report Location
JSON reports always saved to `./reports/<timestamp>.json` with ISO timestamp format.

## Integration Points

- **Input**: YAML files (contracts) + data files (CSV/Parquet/JSON) or database sources
- **Output**: JSON reports, console summary, exit codes
- **Dependencies**: pandas (data loading), pyyaml (contract parsing), pyarrow (parquet support), optional psycopg2-binary/pymysql for DBs
- **No external APIs**: Purely local validation, no network calls

## When Adding New Features

1. **New rule type**: Add field to `FieldRule` or `DistributionRule`, parse in `Contract._parse_rules()`, check in corresponding validator
2. **New validator**: Create in `validators/new_validator.py`, import in `cli.py`, integrate into validation pipeline
3. **New data format**: Update `DataSource._detect_format()` and `load()` method
4. **New CLI command**: Add to argument parser in `cli.py`, implement command function

Always:
- Add type hints
- Include docstrings
- Add test cases in `tests/test_validator.py` with fixtures
- Use dataclasses for data models (not dicts)
- Keep error messages specific (field name, threshold, actual value)
