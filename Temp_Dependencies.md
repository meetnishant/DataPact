--- a/pyproject.toml
+++ b/pyproject.toml
@@
 dependencies = [
     "pandas>=1.5.0",
     "pyyaml>=6.0",
     "pyarrow>=10.0.0",
+    "pact-python>=2.0.0",
 ]
--- a/DEPENDENCIES.md
+++ b/DEPENDENCIES.md
@@
 ## Runtime dependencies
 - pandas >= 1.5.0 - DataFrame engine for loading and validating datasets.
 - pyyaml >= 6.0 - YAML parsing for data contracts.
 - pyarrow >= 10.0.0 - Parquet support and Arrow-based I/O.
+- pact-python >= 2.0.0 - External API Pact integration (provider adapter).
@@
 - ODCS compatibility relies on existing YAML parsing (no new dependencies).
+- API Pact integration relies on pact-python (external dependency).
@@
 Optional database drivers:

 ```bash
 pip install -e ".[db]"
```