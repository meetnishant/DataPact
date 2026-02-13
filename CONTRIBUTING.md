# Contributing to DataPact

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
4. Install with dev dependencies: `pip install -e ".[dev]"`
   - Note: `pact-python` is installed with base dependencies for API Pact integration.

## Code Standards

- **Formatting**: Black (88 char line length)
- **Linting**: Ruff
- **Type Hints**: Full type annotations
- **Tests**: Pytest with >80% coverage

## Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and add tests
3. Run checks:
   ```bash
   black src/ tests/
   ruff check src/ tests/
   mypy src/
   pytest
   ```
4. Commit with clear messages
5. Push and open a pull request

## Adding a New Validator

1. Create `src/datapact/validators/your_validator.py`
2. Implement validator class with `validate()` method returning `(bool, List[str])`
3. Add tests in `tests/test_validator.py`
4. Export from `validators/__init__.py`
5. Integrate into `cli.py`

## Adding Support for New Contract Providers

DataPact supports multiple contract formats via provider abstraction. To add a new provider:

1. Create `src/datapact/providers/your_format_provider.py` implementing `ContractProvider` interface:
   ```python
   from datapact.providers import ContractProvider
   from datapact.contracts import Contract
   
   class YourFormatProvider(ContractProvider):
       def can_load(self, file_path: str) -> bool:
           """Return True if this provider can load the file."""
           return file_path.endswith('.your_format')
       
       def load(self, file_path: str, *args, **kwargs) -> Contract:
           """Load contract and return Contract object."""
           # Parse your format → Contract dataclass
           pass
   ```

2. Export from `src/datapact/providers/__init__.py`:
   ```python
   from datapact.providers.your_format_provider import YourFormatProvider
   ```

3. Register in provider dispatch (auto-discoverable via `can_load()`)

4. Add fixtures in `tests/fixtures/your_format_sample.*`

5. Add tests in `tests/test_contract_providers.py`:
   - Test `can_load()` detection
   - Test `load()` with valid and invalid inputs
   - Test field inference (type mapping)
   - Test error handling

6. Update `README.md` and `docs/EXAMPLES.md` with usage examples

**Example**: See `src/datapact/providers/odcs_provider.py` and `pact_provider.py` for reference implementations.

---

## Adding Support for New Data Formats

1. Update `DataSource._detect_format()` with new file extension
2. Implement loading in `DataSource.load()`
3. Add test fixture and test case

## Adding Support for New Database Sources

1. Update `DatabaseSource._connect()` in `src/datapact/datasource.py`
2. Wire CLI flags in `src/datapact/cli.py`
3. Add tests in `tests/test_db_source.py`

## Rule Severities and Profiling

- Rule severities can be specified per rule (WARN/ERROR) in YAML.
- CLI overrides are supported via `--severity-override field.rule=warn`.
- Profiling uses `datapact profile` and `profile_dataframe()` for rule baselines.
- Schema drift policy is configured in `schema.extra_columns.severity`.
- SLA checks are configured in `sla.min_rows` and `sla.max_rows`.
- Chunked validation is available via `--chunksize` with optional sampling.
- Custom rule plugins are configured via `rules.custom` and `custom_rules`.
- Report sinks are configured via `--report-sink` and webhook options.
- Policy packs are configured via `policies` entries in contracts.

## Adding Support for New Contract Versions

1. Add version info to `VERSION_REGISTRY` in `src/datapact/versioning.py`
2. Implement migration path in `VersionMigration._migrate_step()` method
3. Update `TOOL_COMPATIBILITY` matrix if needed
4. Add test fixtures in `tests/fixtures/`
5. Add test cases in `tests/test_versioning.py`
6. Update `docs/VERSIONING.md` with:
   - Version release notes
   - Breaking changes list
   - Migration guide
   - Examples

## Adding or Extending ODCS Support

1. Update `src/datapact/odcs_contracts.py` with new ODCS fields or mappings
2. Add fixtures under `tests/fixtures/` (use `.odcs.yaml` extension when possible)
3. Add tests in `tests/test_odcs_contract.py`
4. Update README/QUICKSTART to document new ODCS mappings and CLI flags

## Running Tests

```bash
# All tests
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

# Specific test file
pytest tests/test_validator.py -v
pytest tests/test_versioning.py -v

# With coverage
pytest --cov=src/datapact
```

## Versioning Strategy

- Contracts use semantic versioning (major.minor.patch)
- Tool version tracks compatibility (currently 0.2.0)
- Always maintain backward compatibility with auto-migration
- Document breaking changes clearly in VERSIONING.md
