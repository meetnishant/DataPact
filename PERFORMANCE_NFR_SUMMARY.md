# Performance & NFR Test Summary

All performance and non-functional requirement (NFR) tests passed successfully.

## Test Results
- **Total tests:** 7
- **Failures:** 0
- **Errors:** 0
- **Skipped:** 0
- **Total time:** ~38 seconds

### Scenarios Covered
- Large CSV validation time
- Contract parsing speed
- CLI startup time
- Memory usage for large files
- Batch validation throughput
- Concurrent validation throughput
- Performance degradation (scaling)

## How to Run Locally
```bash
PYTHONPATH=src python3 -m pytest tests/test_performance.py tests/test_performance_extra.py --durations=10 --tb=short --junitxml=performance_report.xml
```

## Report
- JUnit XML: `performance_report.xml` (for CI integration)
- Console output: pytest summary with durations

## CI Automation
Performance/NFR tests can be run automatically in CI by adding a job to your GitHub Actions workflow:

```yaml
  performance-nfr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run performance/NFR tests
        run: |
          PYTHONPATH=src python3 -m pytest tests/test_performance.py tests/test_performance_extra.py --durations=10 --tb=short --junitxml=performance_report.xml
      - name: Upload performance report
        uses: actions/upload-artifact@v4
        with:
          name: performance-report
          path: performance_report.xml
```

- Add this job to your `.github/workflows/ci.yml`.
- Artifacts will be available for download after each CI run.
