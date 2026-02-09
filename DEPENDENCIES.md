# Dependencies

This document summarizes the direct dependencies declared in `pyproject.toml`.

## Build system dependencies
- setuptools >= 45
- wheel

## Runtime dependencies
- pandas >= 1.5.0
- pyyaml >= 6.0
- pyarrow >= 10.0.0

## Development dependencies (optional)
- pytest >= 7.0
- pytest-cov >= 4.0
- ruff >= 0.1.0
- black >= 23.0
- mypy >= 1.0

## Notes on open source usage
- The project depends on the open source libraries listed above.
- Transitive dependencies are not listed here and are resolved by your package manager.
- Licenses for direct and transitive dependencies may vary; verify them via PyPI metadata or your environment as needed.
