# Dependencies

This document summarizes the direct dependencies declared in `pyproject.toml`.

## Build system dependencies
- setuptools >= 45 - Packaging/build backend used by `pyproject.toml`.
- wheel - Builds wheel distributions for installation.

## Runtime dependencies
- pandas >= 1.5.0 - DataFrame engine for loading and validating datasets.
- pyyaml >= 6.0 - YAML parsing for data contracts.
- pyarrow >= 10.0.0 - Parquet support and Arrow-based I/O.
- pact-python >= 2.0.0 - External API Pact integration (provider adapter).

## Development dependencies (optional)
- pytest >= 7.0 - Test runner.
- pytest-cov >= 4.0 - Coverage reporting for pytest.
- ruff >= 0.1.0 - Linting and static checks.
- black >= 23.0 - Code formatter.
- mypy >= 1.0 - Static type checker.

## Database dependencies (optional)
- psycopg2-binary >= 2.9 - Postgres driver for DB sources.
- pymysql >= 1.1 - MySQL driver for DB sources.

## Notes on open source usage
- The project depends on the open source libraries listed above.
- Transitive dependencies are not listed here and are resolved by your package manager.
- Licenses for direct and transitive dependencies may vary; verify them via PyPI metadata or your environment as needed.

## Feature Notes
- Profiling uses pandas statistics to infer rule baselines.
- Rule severity metadata and overrides are handled in core validation logic (no new dependencies).
- Schema drift and SLA checks are handled in core validation logic (no new dependencies).
- Chunked validation and sampling use pandas chunked readers (no new dependencies).
- Custom rule plugins are loaded via Python import modules (no new dependencies).
- Report sinks use the Python standard library for JSON and HTTP (no new dependencies).
- Policy packs use in-repo configuration (no new dependencies).
- Database sources use optional drivers for Postgres/MySQL (SQLite uses stdlib).
- ODCS compatibility relies on existing YAML parsing (no new dependencies).
- API Pact integration relies on pact-python (external dependency).
