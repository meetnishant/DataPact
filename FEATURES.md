# DataPact Features

This document lists the functional capabilities provided by DataPact with compact, practical examples.

## Core Validation

### Validate schema, quality, and distribution
Check that a dataset matches a contract definition and produce a report.

```bash
datapact validate --contract contracts/customer.yaml --data data/customers.csv
```

### Enforce required columns and types
Fail when required fields are missing or types do not match.

```yaml
fields:
  - name: customer_id
    type: integer
    required: true
  - name: email
    type: string
    required: true
```

## Quality Rules

### Null and uniqueness rules
Prevent nulls and duplicate values.

```yaml
fields:
  - name: email
    type: string
    rules:
      not_null: true
      unique: true
```

### Range and enum rules
Constrain numeric values and limit categories.

```yaml
fields:
  - name: age
    type: integer
    rules:
      min: 0
      max: 150
  - name: status
    type: string
    rules:
      enum: [active, inactive, suspended]
```

### Regex validation
Validate string formats such as emails or IDs.

```yaml
fields:
  - name: email
    type: string
    rules:
      regex: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
```

## Severity and Policy

### Rule severity per rule
Control whether a violation is a warning or an error.

```yaml
fields:
  - name: score
    type: float
    rules:
      max:
        value: 100
        severity: WARN
```

### Override severity from CLI
Adjust severities without editing contracts.

```bash
datapact validate --contract c.yaml --data d.csv --severity-override score.max=warn
```

### Schema drift policy
Decide how extra columns are treated.

```yaml
schema:
  extra_columns:
    severity: WARN
```

## Distribution Monitoring

### Drift checks for numeric fields
Detect shifts in mean or standard deviation.

```yaml
fields:
  - name: score
    type: float
    distribution:
      mean: 50.0
      std: 15.0
      max_drift_pct: 10.0
```

## SLA and Freshness

### Row count constraints
Enforce minimum or maximum rows.

```yaml
sla:
  min_rows: 100
  max_rows:
    value: 100000
    severity: WARN
```

### Freshness rule
Ensure timestamp fields are not too old.

```yaml
fields:
  - name: event_time
    type: string
    rules:
      freshness_max_age_hours: 24
```

## Profiling

### Generate a baseline contract from data
Create a contract template from observed data.

```bash
datapact init --contract new_contract.yaml --data data.csv
```

### Profile rules and distributions
Generate rule baselines from data statistics.

```bash
datapact profile --contract profile.yaml --data data.csv
```

## Streaming and Sampling

### Chunked validation for large files
Validate CSV or JSONL in streaming mode.

```bash
datapact validate --contract c.yaml --data big.jsonl --chunksize 50000
```

### Sample rows or fractions
Validate a representative subset.

```bash
datapact validate --contract c.yaml --data big.csv --sample-rows 10000 --sample-seed 42
```

## Custom Rules

### Field-level custom rules
Plug in custom validation logic per field.

```yaml
fields:
  - name: amount
    type: float
    rules:
      custom:
        rule: positive_amount
        severity: ERROR
```

```bash
datapact validate --contract c.yaml --data d.csv --plugin tests.plugins.sample_plugin
```

### Dataset-level custom rules
Run checks that use the whole dataset.

```yaml
custom_rules:
  - rule: total_balance_positive
    severity: WARN
```

## Contract Versioning

### Versioned contracts with auto-migration
Keep contracts compatible as schemas evolve.

```yaml
contract:
  name: customer_data
  version: 2.0.0
```

## Policy Packs

### Apply reusable rule bundles
Use named policy packs to add standard rules across contracts.

```yaml
policies:
  - name: pii_basic
    overrides:
      fields:
        phone:
          rules:
            regex:
              value: '^\\+1[0-9]{10}$'
              severity: WARN
```

## Reporting

### JSON reports for CI/CD
Reports are stored under the configured output directory.

```bash
datapact validate --contract c.yaml --data d.csv --output-dir ./reports
```

### Report sinks
Send reports to files, stdout, or webhooks.

```bash
datapact validate --contract c.yaml --data d.csv --report-sink file --report-sink stdout
```

```bash
datapact validate --contract c.yaml --data d.csv \
  --report-sink webhook \
  --report-webhook-url https://example.com/hook \
  --report-webhook-header "Authorization: Bearer token"
```

## Supported Data Formats

### CSV, Parquet, and JSON Lines
Auto-detect input formats or specify explicitly.

```bash
datapact validate --contract c.yaml --data data.parquet --format parquet
```
