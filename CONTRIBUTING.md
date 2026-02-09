# Contributing to DataPact

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
4. Install with dev dependencies: `pip install -e ".[dev]"`

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

## Adding Support for New Data Formats

1. Update `DataSource._detect_format()` with new file extension
2. Implement loading in `DataSource.load()`
3. Add test fixture and test case

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

## Running Tests

```bash
# All tests
pytest

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
