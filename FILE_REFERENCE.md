# File Reference Guide

This guide maps each file to its purpose and shows how they fit together.

## Core Application Files

### `src/datapact/__init__.py`
- **Purpose**: Package entry point, exports main classes
- **Exports**: `Contract`, `ValidationReport`, `DataSource`
- **When to modify**: Adding new top-level exports

### `src/datapact/contracts.py`
- **Purpose**: Parse YAML contracts, model validation rules
- **Classes**: `Contract`, `Field`, `FieldRule`, `DistributionRule`, `Dataset`
- **Key methods**: 
  - `Contract.from_yaml(path)` - Load and parse contract file
  - `Contract._parse_rules()` - Extract field validation rules
  - `Contract._parse_distribution()` - Extract distribution rules
- **When to modify**: Adding new rule types or contract metadata

### `src/datapact/datasource.py`
- **Purpose**: Load datasets in multiple formats
- **Classes**: `DataSource`
- **Key methods**:
  - `load()` - Load data into DataFrame
  - `infer_schema()` - Discover column types
  - `_detect_format()` - Auto-detect file format
- **When to modify**: Adding support for new data formats (e.g., Excel)

### `src/datapact/cli.py`
- **Purpose**: Command-line interface and orchestration
- **Functions**: `main()`, `validate_command()`, `init_command()`
- **Commands**: `validate`, `init`
- **When to modify**: Adding new CLI commands or options

### `src/datapact/reporting.py`
- **Purpose**: Generate validation reports
- **Classes**: `ErrorRecord`, `ValidationReport`
- **Key methods**:
  - `to_dict()` - Convert to JSON-serializable format with version info
  - `save_json()` - Write report to `./reports/<timestamp>.json`
  - `print_summary()` - Print human-readable console output
- **When to modify**: Changing report format or adding new metadata

### `src/datapact/versioning.py`
- **Purpose**: Contract version management, migration, and compatibility checking
- **Classes**: `VersionInfo`, `VersionMigration`
- **Functions**: `validate_version()`, `check_tool_compatibility()`, `get_breaking_changes()`, `get_deprecation_message()`
- **Key data**: `VERSION_REGISTRY`, `TOOL_COMPATIBILITY`, `LATEST_VERSION`
- **When to modify**: Adding new contract versions or migration paths

### Validators (Sequential Pipeline)

#### `src/datapact/validators/schema_validator.py`
- **Purpose**: Check structure (columns, types, required fields)
- **Classes**: `SchemaValidator`
- **Runs**: First (blocks if critical issues)
- **Output**: ERROR severity violations
- **When to modify**: Adding new schema checks (e.g., column ordering)

#### `src/datapact/validators/quality_validator.py`
- **Purpose**: Validate data content (nulls, ranges, patterns, etc.)
- **Classes**: `QualityValidator`
- **Runs**: Second (non-blocking)
- **Output**: ERROR or WARN severity violations
- **When to modify**: Adding new validation rules (min, max, regex, enum, etc.)

#### `src/datapact/validators/distribution_validator.py`
- **Purpose**: Monitor numeric distributions (mean, std drift)
- **Classes**: `DistributionValidator`
- **Runs**: Third (always non-blocking)
- **Output**: WARN severity violations
- **When to modify**: Adding new statistical checks (e.g., percentile thresholds)

## Configuration Files

### `pyproject.toml`
- **Purpose**: Project metadata, dependencies, build config
- **Sections**:
  - `[build-system]` - Setuptools config
  - `[project]` - Package metadata
  - `[project.optional-dependencies]` - Dev tools (pytest, black, mypy, ruff)
  - `[project.scripts]` - CLI entry point `datapact`
  - `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]` - Tool configs
- **When to modify**: Updating dependencies, adding new tool config

### `setup.py`
- **Purpose**: Setuptools configuration for editable installs
- **When to modify**: Rarely (pyproject.toml is preferred)

### `.gitignore`
- **Purpose**: Exclude files from git
- **Sections**: Python artifacts, build files, IDE files, test coverage, reports
- **When to modify**: Adding project-specific exclusions

### `.github/workflows/tests.yml`
- **Purpose**: GitHub Actions CI/CD pipeline
- **Jobs**: Lint (ruff, black), type check (mypy), tests (pytest with coverage)
- **Trigger**: Push to main/develop, PR to main/develop
- **When to modify**: Adding new checks, changing Python versions

## Documentation Files

### `README.md`
- **Purpose**: User-facing documentation
- **Sections**: Features, installation, quick start, contract format, CLI usage
- **Audience**: End users and integrators
- **When to modify**: Updating examples, adding features

### `QUICKSTART.md`
- **Purpose**: Get developers running in minutes
- **Sections**: Installation, running CLI, running tests, code quality
- **When to modify**: Changing setup process or common commands

### `CONTRIBUTING.md`
- **Purpose**: Developer guide for contributions
- **Sections**: Setup, code standards, workflow, adding validators/formats
- **When to modify**: Updating contribution guidelines

### `ARCHITECTURE.md`
- **Purpose**: Design documentation
- **Sections**: Component overview, validation semantics, error handling, extensibility
- **When to modify**: Major architectural changes

### `docs/VERSIONING.md`
- **Purpose**: Contract versioning guide and reference
- **Sections**: Version history, breaking changes, migration guide, API usage, best practices
- **Audience**: Developers working with contract versions
- **When to modify**: Adding new contract versions or migration paths

### `.github/copilot-instructions.md`
- **Purpose**: Guide for AI agents (Copilot, Claude, etc.)
- **Sections**: Project overview, architecture, key files, contract format, versioning, workflows, conventions
- **When to modify**: New features, design changes, new patterns
- **Note**: This is auto-generated/updated from project structure

### `SETUP_SUMMARY.md`
- **Purpose**: This file - provide overview of what was created
- **When to modify**: After major restructuring

### `DASHBOARD.md`
- **Purpose**: Project overview dashboard with stats and quick references
- **When to modify**: Updating counts, versions, or quick links

### `DELIVERY_SUMMARY.md`
- **Purpose**: Delivery summary for stakeholders
- **When to modify**: Updating scope, counts, or release status

### `PROJECT_STRUCTURE.md`
- **Purpose**: Visual project tree
- **When to modify**: Adding or removing files/folders

### `INDEX.md`
- **Purpose**: Navigation guide for all docs
- **When to modify**: Adding new docs or cross-references

### `COMPLETION_CHECKLIST.md`
- **Purpose**: Feature and QA checklist
- **When to modify**: Updating scope or release status

### `DEPENDENCIES.md`
- **Purpose**: Direct dependency list and tool descriptions
- **When to modify**: Updating dependencies or tooling

### `SEQUENCE_DIAGRAM_GUIDE.md`
- **Purpose**: Guide for Mermaid sequence diagrams
- **When to modify**: Diagram location or viewing changes

### `VERSIONING_IMPLEMENTATION.md`
- **Purpose**: Versioning implementation notes and test summary
- **When to modify**: Versioning changes or test count updates

## Test Files

### `tests/test_validator.py`
- **Purpose**: Unit tests for validators and core functionality
- **Test classes**: `TestSchemaValidator`, `TestQualityValidator`, `TestDataSource`, `TestDistributionValidator`
- **Fixtures**: `customer_contract`, `valid_df`, `invalid_df`
- **When to modify**: Adding new test cases for features

### `tests/test_versioning.py`
- **Purpose**: Unit tests for contract versioning, migration, and compatibility
- **Test classes**: `TestVersionValidation`, `TestToolCompatibility`, `TestVersionMigration`, `TestContractVersionLoading`, `TestVersionInfo`
- **Total tests**: 17 test cases covering all versioning scenarios
- **When to modify**: Adding new contract versions or migration logic

### `tests/test_banking_finance.py`
- **Purpose**: Multi-table banking/finance validation scenarios with consumer-specific contracts
- **Test classes**: `TestDepositsAccountsStrict`, `TestDepositsAccountsAggregate`, `TestDepositsTransactions`, `TestLendingLoansStrict`, `TestLendingLoansAggregate`, `TestLendingPayments`, `TestComplexConsumption`
- **When to modify**: Adding banking/finance rules, fixtures, or scenario coverage

### `tests/test_concurrency.py`
- **Purpose**: Concurrency validation using threads
- **When to modify**: Changing concurrency behavior or validation safety checks

### `tests/test_concurrency_mp.py`
- **Purpose**: Concurrency validation using multiprocessing
- **When to modify**: Changing multiprocessing behavior or validation safety checks

### `tests/fixtures/customer_contract.yaml`
- **Purpose**: Example contract with all rule types (v2.0.0)
- **Usage**: Test reference and template for new contracts
- **When to modify**: Adding examples of new rule types

### `tests/fixtures/customer_contract_v1.yaml`
- **Purpose**: Example contract in v1.0.0 format for testing auto-migration
- **When to modify**: Testing legacy version support

### `tests/fixtures/customer_contract_v2.yaml`
- **Purpose**: Example contract in v2.0.0 format with advanced rules
- **When to modify**: Adding examples of new v2.0.0 features

### `tests/fixtures/valid_customers.csv`
- **Purpose**: Sample data that passes all validation rules
- **When to modify**: Adding test data for new rules

### `tests/fixtures/invalid_customers.csv`
- **Purpose**: Sample data with intentional violations (missing fields, invalid email, etc.)
- **When to modify**: Adding test cases for new rules

### `tests/fixtures/deposits_contract.yaml`
- **Purpose**: Banking deposits contract with schema and quality rules
- **When to modify**: Adjusting deposits validation rules or schema

### `tests/fixtures/lending_contract.yaml`
- **Purpose**: Banking lending contract with schema and quality rules
- **When to modify**: Adjusting lending validation rules or schema

### `tests/fixtures/deposits_data.csv`
- **Purpose**: Deposits accounts data (positive/negative/boundary cases)
- **When to modify**: Expanding deposits accounts coverage

### `tests/fixtures/lending_data.csv`
- **Purpose**: Lending loans data (positive/negative/boundary cases)
- **When to modify**: Expanding lending loans coverage

### `tests/fixtures/deposits_accounts_agg_contract.yaml`
- **Purpose**: Aggregate consumer contract for deposits accounts
- **When to modify**: Adjusting aggregate consumer requirements

### `tests/fixtures/lending_loans_agg_contract.yaml`
- **Purpose**: Aggregate consumer contract for lending loans
- **When to modify**: Adjusting aggregate consumer requirements

### `tests/fixtures/deposits_transactions_contract.yaml`
- **Purpose**: Deposits transactions contract
- **When to modify**: Adjusting transaction validation rules

### `tests/fixtures/lending_payments_contract.yaml`
- **Purpose**: Lending payments contract
- **When to modify**: Adjusting payments validation rules

### `tests/fixtures/deposits_transactions.csv`
- **Purpose**: Deposits transactions data (positive/negative/boundary cases)
- **When to modify**: Expanding transaction coverage

### `tests/fixtures/lending_payments.csv`
- **Purpose**: Lending payments data (positive/negative/boundary cases)
- **When to modify**: Expanding payments coverage

### `tests/fixtures/deposits_accounts_agg.csv`
- **Purpose**: Aggregate deposits accounts data with relaxed customer_id constraints
- **When to modify**: Adjusting aggregate dataset mix

### `tests/fixtures/lending_loans_agg.csv`
- **Purpose**: Aggregate lending loans data with relaxed customer_id constraints
- **When to modify**: Adjusting aggregate dataset mix

## File Dependency Graph

```
cli.py (entry point)
  ↓
  ├→ contracts.py (parse YAML + version validation)
  │  └→ versioning.py (auto-migration, compatibility)
  ├→ datasource.py (load data)
  └→ validators/ (3-step pipeline)
      ├→ schema_validator.py
      ├→ quality_validator.py
      └→ distribution_validator.py
  └→ reporting.py (aggregate results + version info)

Tests:
  test_validator.py (core tests: 10)
    ↓ uses
    ├→ fixtures/customer_contract.yaml (v2.0.0)
    ├→ fixtures/valid_customers.csv
    └→ fixtures/invalid_customers.csv

  test_versioning.py (versioning tests: 17)
    ↓ uses
    ├→ fixtures/customer_contract_v1.yaml (v1.0.0)
    └→ fixtures/customer_contract_v2.yaml (v2.0.0)

  test_banking_finance.py (banking/finance tests: 16)
    ↓ uses
    ├→ fixtures/deposits_contract.yaml
    ├→ fixtures/lending_contract.yaml
    ├→ fixtures/deposits_data.csv
    ├→ fixtures/lending_data.csv
    ├→ fixtures/deposits_accounts_agg_contract.yaml
    ├→ fixtures/lending_loans_agg_contract.yaml
    ├→ fixtures/deposits_transactions_contract.yaml
    ├→ fixtures/lending_payments_contract.yaml
    ├→ fixtures/deposits_transactions.csv
    ├→ fixtures/lending_payments.csv
    ├→ fixtures/deposits_accounts_agg.csv
    └→ fixtures/lending_loans_agg.csv

  test_concurrency.py (threaded concurrency)
  test_concurrency_mp.py (multiprocessing concurrency)
```

## Adding a New Feature

1. **New validation rule** → Modify `FieldRule` in `contracts.py`, check in `quality_validator.py`, add test to `tests/test_validator.py`
2. **New data format** → Modify `DataSource._detect_format()` and `load()`, add test fixture
3. **New CLI command** → Add to argument parser in `cli.py`, create command function, document in `README.md`
4. **New validator type** → Create `validators/new_validator.py`, import in `cli.py`, call in `validate_command()`, document in `.github/copilot-instructions.md`
5. **New contract version** → Add to `VERSION_REGISTRY` in `versioning.py`, create migration path from previous version, add test fixtures in `tests/fixtures/`, add tests to `tests/test_versioning.py`, update `docs/VERSIONING.md`
