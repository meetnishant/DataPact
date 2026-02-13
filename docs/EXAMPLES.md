# DataPact Examples & Best Practices

Comprehensive examples covering all DataPact features including contract providers, validation rules, report sinks, and advanced scenarios.

## Table of Contents

- [Contract Providers](#contract-providers)
  - [DataPact YAML Provider](#datapact-yaml-provider)
  - [ODCS Provider](#odcs-provider)
  - [API Pact Provider](#api-pact-provider)
- [Validation Rules](#validation-rules)
  - [Quality Rules](#quality-rules)
  - [Distribution Validation](#distribution-validation)
  - [SLA Checks](#sla-checks)
- [Advanced Features](#advanced-features)
  - [Schema Drift Policy](#schema-drift-policy)
  - [Custom Rules & Plugins](#custom-rules--plugins)
  - [Policy Packs](#policy-packs)
  - [Flatten & Normalization](#flatten--normalization)
  - [Report Sinks](#report-sinks)
  - [Chunked Validation](#chunked-validation)
  - [Version Migration](#version-migration)

---

## Contract Providers

### DataPact YAML Provider

Native DataPact contract format with full feature support.

**Contract file** (`customer_contract.yaml`):
```yaml
contract:
  name: customer_data
  version: 2.0.0
dataset:
  name: customers
fields:
  - name: customer_id
    type: integer
    required: true
    rules:
      unique: true
  - name: email
    type: string
    required: true
    rules:
      regex: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
      unique: true
  - name: age
    type: integer
    rules:
      min: 0
      max: 120
  - name: score
    type: float
    distribution:
      mean: 50.0
      std: 15.0
      max_drift_pct: 10.0
```

**Validate CSV data**:
```bash
datapact validate --contract customer_contract.yaml --data customers.csv
```

**Validate Parquet data**:
```bash
datapact validate --contract customer_contract.yaml --data customers.parquet
```

**Validate database table**:
```bash
datapact validate --contract customer_contract.yaml \
  --datasource-type postgres \
  --datasource-host localhost \
  --datasource-port 5432 \
  --datasource-user pg_user \
  --datasource-password pg_pass \
  --datasource-db mydb \
  --datasource-table customers
```

### ODCS Provider

Validate Open Data Contract Standard v3.1.0 contracts.

**ODCS contract** (`customer_odcs.yaml`):
```yaml
dataContractSpecification: 1.0.0
apiVersion: v3.1.0
id: customer_odcs
metadata:
  owner: data_team
  description: Customer master dataset

tables:
  - name: customers
    description: Customer dimensional table
    schema:
      - name: customer_id
        type: BIGINT
        description: Unique customer identifier
        contract:
          required: true
      - name: email
        type: STRING
        description: Customer email address
      - name: age
        type: INTEGER
        description: Customer age
```

**Validate ODCS contract**:
```bash
datapact validate --contract customer_odcs.yaml --data customers.csv --contract-format odcs
```

### API Pact Provider

Validate API Pact contracts for REST API responses.

**Pact contract** (`user_api_pact.json`):
```json
{
  "consumer": {
    "name": "web_app"
  },
  "provider": {
    "name": "user_api"
  },
  "interactions": [
    {
      "description": "a request for user by ID",
      "request": {
        "method": "GET",
        "path": "/users/123"
      },
      "response": {
        "status": 200,
        "body": {
          "id": 123,
          "email": "user@example.com",
          "age": 28,
          "name": "John Doe"
        }
      }
    }
  ]
}
```

**Generate a DataPact contract from Pact**:
```bash
datapact init --contract user_api_contract.yaml --data user_api_pact.json --contract-format pact
```

**Validate API Pact response structure**:
```bash
# Use the auto-generated contract against actual API responses
datapact validate --contract user_api_contract.yaml --data api_responses.jsonl
```

---

## Validation Rules

### Quality Rules

Comprehensive data quality checks with per-rule severity configuration.

**Contract with quality rules**:
```yaml
contract:
  name: ecommerce_orders
  version: 2.0.0
dataset:
  name: orders

fields:
  - name: order_id
    type: integer
    required: true
    rules:
      unique: true

  - name: customer_email
    type: string
    required: true
    rules:
      regex: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
      severity: error  # Will fail validation if regex doesn't match
      unique: true
      severity: warn   # Will warn (not fail) on duplicates

  - name: order_amount
    type: float
    required: true
    rules:
      min: 0.01
      max: 999999.99
      severity: error

  - name: order_status
    type: string
    rules:
      enum: ['pending', 'shipped', 'delivered', 'cancelled']
      severity: error

  - name: notes
    type: string
    rules:
      max_null_ratio: 0.1  # Allow up to 10% nulls
      severity: warn
```

**Validate with severity override**:
```bash
# Treat all warnings as errors
datapact validate --contract orders.yaml --data orders.csv --severity-override warn=error

# Override specific rule
datapact validate --contract orders.yaml --data orders.csv \
  --severity-override customer_email.unique=warn
```

### Distribution Validation

Monitor numeric field distributions for data drift.

**Contract with distribution rules**:
```yaml
contract:
  name: sales_metrics
  version: 2.0.0
dataset:
  name: daily_sales

fields:
  - name: sale_amount
    type: float
    distribution:
      mean: 500.0
      std: 150.0
      max_drift_pct: 15.0  # Alert if mean/std drift > 15%
      max_z_score: 4.0     # Alert on outliers beyond 4 std deviations

  - name: item_count
    type: integer
    distribution:
      mean: 5.0
      std: 2.5
      max_drift_pct: 20.0
```

**Validation**:
```bash
datapact validate --contract sales_contract.yaml --data sales_data.csv
```

Distribution violations are reported as **warnings** (non-blocking), helping monitor data quality trends over time.

### SLA Checks

Enforce Service Level Agreements on dataset dimensions.

**Contract with SLA rules**:
```yaml
contract:
  name: event_tracking
  version: 2.0.0
dataset:
  name: page_views

sla:
  min_rows: 1000          # At least 1000 events per day
  max_rows: 10000000      # At most 10M events (detect spikes)

freshness:
  max_age_hours: 24       # Data must be less than 24 hours old
  
fields:
  - name: event_id
    type: integer
    required: true
  - name: timestamp
    type: string
    required: true
  - name: page_url
    type: string
    required: true
```

**Validation**:
```bash
datapact validate --contract event_tracking.yaml --data events.csv

# Example output on SLA violation:
# ERROR: Minimum row count (1000) not met; actual: 500
# WARN: Data freshness > 24 hours (age: 30 hours)
```

---

## Advanced Features

### Schema Drift Policy

Control how unexpected columns are handled.

**Contract with schema drift policy**:
```yaml
contract:
  name: product_data
  version: 2.0.0
dataset:
  name: products
  
schema:
  extra_columns:
    severity: warn      # Warn on extra columns (not error)
    # severity: error   # Or fail validation on extra columns

fields:
  - name: product_id
    type: integer
    required: true
  - name: name
    type: string
    required: true
```

**Behavior**:
- `severity: warn` — Extra columns logged as warnings, validation passes
- `severity: error` — Extra columns cause validation to fail
- Default: error

### Custom Rules & Plugins

Extend validation with custom Python functions via plugins.

**Create a custom validator** (`my_validators.py`):
```python
def validate_business_hours(value):
    """Ensure hour_of_day is between 0-23."""
    return 0 <= value <= 23

def validate_country_code(value):
    """Ensure country_code matches ISO 3166-1 alpha-2."""
    valid_codes = {"US", "CA", "GB", "FR", "DE", "JP", "AU", ...}
    return value in valid_codes
```

**Contract with custom rules**:
```yaml
contract:
  name: analytics_events
  version: 2.0.0
dataset:
  name: events
  
custom_rules:
  plugins: ["my_validators"]

fields:
  - name: hour_of_day
    type: integer
    rules:
      custom:
        function: validate_business_hours
        severity: warn

  - name: country_code
    type: string
    rules:
      custom:
        function: validate_country_code
        severity: error
```

**Validation**:
```bash
datapact validate --contract analytics.yaml --data events.csv --custom-rules my_validators
```

### Policy Packs

Reuse standard rule bundles across contracts.

**Define a policy pack** (`financial_policies.yaml`):
```yaml
policies:
  monetary_fields:
    rules:
      - min: -999999.99
      - max: 999999.99
      - numeric_type: true

  email_fields:
    rules:
      - regex: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
      - unique: true

  date_fields:
    rules:
      - regex: '^\d{4}-\d{2}-\d{2}$'
      - required: true
```

**Apply policies in contract**:
```yaml
contract:
  name: financial_transactions
  version: 2.0.0
dataset:
  name: transactions

policies:
  - financial_policies

fields:
  - name: account_balance
    type: float
    policy: monetary_fields

  - name: account_holder_email
    type: string
    policy: email_fields

  - name: transaction_date
    type: string
    policy: date_fields
```

### Flatten & Normalization

Handle nested/flattened data structures.

**Contract with flatten config** (for nested JSON):
```yaml
contract:
  name: nested_user_data
  version: 2.0.0
dataset:
  name: users

flatten:
  enabled: true
  separator: "__"    # Flatten with double-underscore separator

fields:
  # Nested field: user.profile.email → user__profile__email
  - name: email
    logical_path: user.profile.email
    type: string
    required: true

  # Nested field: user.profile.age → user__profile__age
  - name: age
    logical_path: user.profile.age
    type: integer
    rules:
      min: 0
      max: 150
```

**Sample nested data** (`users.json`):
```json
{
  "user": {
    "id": 1,
    "profile": {
      "email": "john@example.com",
      "age": 28
    }
  }
}
```

**After flatten**:
```
user__id, user__profile__email, user__profile__age
1, john@example.com, 28
```

**Validation**:
```bash
datapact validate --contract nested_user.yaml --data users.json
# Errors reported with lineage: field 'email' (path: user.profile.email, column: user__profile__email)
```

### Report Sinks

Output validation results to different destinations.

**File sink** (default JSON report):
```bash
datapact validate --contract contract.yaml --data data.csv
# Report: ./reports/<timestamp>.json
```

**Webhook sink**:
```bash
datapact validate --contract contract.yaml --data data.csv \
  --report-sink webhook \
  --webhook-url https://api.example.com/validation-results \
  --webhook-method POST \
  --webhook-headers Content-Type=application/json X-API-Key=secret123
  
# POST body:
{
  "passed": false,
  "contract": {"name": "customer_data", "version": "2.0.0"},
  "metadata": {"tool_version": "2.0.0", "timestamp": "2026-02-13T..."},
  "summary": {"error_count": 2, "warning_count": 1},
  "errors": [...]
}
```

**Stdout sink**:
```bash
datapact validate --contract contract.yaml --data data.csv \
  --report-sink stdout
  
# Output:
# === Validation Report ===
# Contract: customer_data (v2.0.0)
# Status: FAILED
# Errors: 2 | Warnings: 1
# 
# Errors:
#   - QUALITY customer_id: 5 duplicate values found
#   - SCHEMA email: type mismatch (expected string, got integer)
```

### Chunked Validation

Process large files in chunks without loading entire dataset into memory.

**Contract for chunked validation**:
```yaml
contract:
  name: large_dataset
  version: 2.0.0
dataset:
  name: events

fields:
  - name: event_id
    type: integer
    required: true
    rules:
      unique: true
  - name: timestamp
    type: string
    required: true
```

**Validate large CSV in chunks**:
```bash
# Process in 10,000 row chunks
datapact validate --contract contract.yaml --data large_events.csv \
  --chunksize 10000

# With sampling (validate random 1% of rows)
datapact validate --contract contract.yaml --data large_events.csv \
  --chunksize 10000 \
  --sample-fraction 0.01
```

**Memory efficiency**: Chunked validation processes file sequentially, ideal for datasets > 1GB.

### Version Migration

Automatically upgrade older contracts to latest schema.

**Old contract** (v1.0.0):
```yaml
contract:
  name: customer_data
  version: 1.0.0
dataset:
  name: customers

fields:
  - name: age
    type: integer
    rules:
      max_null_pct: 5  # Percentage-based (v1.0.0 format)

  - name: score
    type: float
    distribution:
      mean: 50.0
      std: 15.0
      # max_z_score not supported in v1.0.0
```

**After auto-migration to v2.0.0**:
```yaml
contract:
  name: customer_data
  version: 2.0.0  # Updated
dataset:
  name: customers

fields:
  - name: age
    type: integer
    rules:
      max_null_ratio: 0.05  # Converted from percentage to ratio

  - name: score
    type: float
    distribution:
      mean: 50.0
      std: 15.0
      max_z_score: 3.0  # Default added
```

**Validation** (auto-migrates transparently):
```bash
datapact validate --contract old_contract.yaml --data data.csv
# Output: Auto-migrated contract from v1.0.0 to v2.0.0
```

---

## End-to-End Workflow Example

Complete workflow: DataPact provider → Flatten → Validate → Report.

**1. Explore data and infer contract**:
```bash
datapact init --contract inferred.yaml --data raw_data.json
```

**2. Refine contract** with business rules:
```yaml
contract:
  name: customer_orders
  version: 2.0.0
dataset:
  name: orders

flatten:
  enabled: true
  separator: "__"

fields:
  - name: order_id
    logical_path: order.id
    type: integer
    required: true
    rules:
      unique: true

  - name: customer_email
    logical_path: customer.email
    type: string
    required: true
    rules:
      regex: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

  - name: amount
    logical_path: order.total_amount
    type: float
    rules:
      min: 0.01
      max: 1000000.0
    distribution:
      mean: 250.0
      std: 100.0
      max_drift_pct: 20.0

sla:
  min_rows: 100
  max_rows: 1000000
```

**3. Profile baseline distributions**:
```bash
datapact profile --contract customer_orders.yaml --data orders.json
# Outputs: distribution means/stds to update contract
```

**4. Validate against contract**:
```bash
datapact validate --contract customer_orders.yaml --data orders.json \
  --report-sink webhook \
  --webhook-url https://monitoring.example.com/validation
```

**5. Check results**:
```bash
cat reports/20260213_103045.json | jq '.summary'
# {
#   "error_count": 0,
#   "warning_count": 2,
#   "passed": true
# }
```

---

## Best Practices

1. **Start with profiling**: Use `datapact profile` to infer baseline distributions and rule values
2. **Version your contracts**: Always specify version in header and track changes in git
3. **Test incrementally**: Add rules one at a time and validate against sample data first
4. **Use policy packs**: Reuse common rules (emails, monetary amounts, dates) across contracts
5. **Set appropriate severities**: Use WARN for monitoring trends, ERROR for hard constraints
6. **Monitor distribution drift**: Use max_drift_pct to detect data quality degradation
7. **Document breaking changes**: Update docs/VERSIONING.md when adding schema-breaking changes
8. **Chunk large files**: Use --chunksize for datasets > 1GB to avoid memory issues
9. **Integrate pipeline reports**: Send webhook reports to monitoring/alerting systems
10. **Auto-migrate old contracts**: Leverage auto-migration to keep contracts up-to-date

---

## See Also

- [README.md](../README.md) — Project overview
- [docs/VERSIONING.md](./VERSIONING.md) — Contract version history and migration
- [docs/ARCHITECTURE.md](./ARCHITECTURE.md) — System architecture and design
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Developer guide for adding new features
- [FILE_REFERENCE.md](../FILE_REFERENCE.md) — Complete file directory reference
