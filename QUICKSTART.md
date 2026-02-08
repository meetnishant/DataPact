# Quick Start Guide

## Installation & Setup

### 1. Clone or Download the Repository
```bash
cd /Users/meetnishant/Documents/DataContracts
```

### 2. Install Dependencies
```bash
python3 -m pip install --user pyyaml pandas pyarrow pytest pytest-cov
```

Optional: Install dev tools for linting and type checking
```bash
python3 -m pip install --user black ruff mypy
```

### 3. Verify Installation
```bash
PYTHONPATH=./src python3 -c "from data_contract_validator import Contract; print('✓ Ready')"
```

## Running the CLI

Set up PYTHONPATH for convenience:
```bash
export PYTHONPATH=/Users/meetnishant/Documents/DataContracts/src
```

### Validate Data
```bash
python3 src/data_contract_validator/cli.py validate \
  --contract tests/fixtures/customer_contract.yaml \
  --data tests/fixtures/valid_customers.csv
```

### Infer Contract from Data
```bash
python3 src/data_contract_validator/cli.py init \
  --contract my_contract.yaml \
  --data my_data.csv
```

## Running Tests

```bash
# Install test dependencies
python3 -m pip install --user pytest pytest-cov

# Run tests
export PYTHONPATH=./src
pytest tests/test_validator.py -v

# Check total coverage percentage
dcv-coverage --min 80
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
- Set it: `export PYTHONPATH=/Users/meetnishant/Documents/DataContracts/src`

**Permission errors on install**
- Use `--user` flag: `python3 -m pip install --user <package>`
- Or use a virtual environment: `python3 -m venv venv && source venv/bin/activate`
