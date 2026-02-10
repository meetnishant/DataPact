# Contract Versioning & Compatibility

## Maintainers & Contributions

This project is maintained by the open-source community. Contributions are welcome via pull requests and issues. Please follow the code style and add tests for new features.

## Overview

The DataPact now includes comprehensive contract versioning support with:

- **Version validation** - Ensure contracts use supported versions
- **Automatic migration** - Auto-upgrade contracts to latest schema
- **Deprecation warnings** - Alert when using outdated versions
- **Compatibility checking** - Validate tool can handle contract version
- **Breaking change tracking** - Know what changed between versions
- **Migration utilities** - Convert contracts between versions

Related features:
- **Profiling**: Auto-generate rule baselines from data (`datapact profile`).
- **Rule Severity**: Rules can declare WARN/ERROR severities with CLI overrides.
- **Schema Drift**: Extra columns can be WARN or ERROR via schema policy.
- **SLA Checks**: Row count and freshness constraints are supported.
- **Chunked Validation**: Stream CSV/JSONL files with optional sampling.
- **Custom Rule Plugins**: Extend validation via plugin modules.
- **Report Sinks**: Write reports to files, stdout, or webhooks.
- **Policy Packs**: Reuse standard rule bundles across contracts.
- **Database Sources**: Validate Postgres, MySQL, and SQLite tables.

## Supported Versions

| Version | Status | Release Date | Notes |
|---------|--------|--------------|-------|
| **1.0.0** | Supported | 2026-01-01 | Initial release |
| **1.1.0** | Supported | 2026-02-01 | Added max_z_score, max_null_ratio |
| **2.0.0** | Current | 2026-03-01 | Breaking changes to null ratio format |

## Version Specification

Always specify version in your contract YAML:

```yaml
contract:
  name: customer_data
  version: 2.0.0  # Required!
dataset:
  name: customers
fields:
  - name: customer_id
    type: integer
```

## Breaking Changes by Version

### v1.1.0 → v2.0.0

- **Removed**: `max_null_pct` (percentage-based)
- **Added**: `max_null_ratio` (ratio-based, 0-1)
- **Changed**: Distribution rule format

**Migration Example:**
```yaml
# v1.1.0
fields:
  - name: age
    rules:
      max_null_pct: 5  # 5% nulls allowed

# v2.0.0 (migrated)
fields:
  - name: age
    rules:
      max_null_ratio: 0.05  # Same as 5%
```

## Auto-Migration

When you load an older contract, it's automatically migrated to the latest version:

```bash
datapact validate --contract old_contract.yaml --data data.csv
# INFO: Auto-migrated contract from v1.0.0 to v2.0.0
```

The migration happens transparently, but you'll see an info message.

## Tool Compatibility

The validator checks if it can handle your contract version:

```
Tool v0.2.0 supports:
  ✓ Contract v1.0.0
  ✓ Contract v1.1.0
  ✓ Contract v2.0.0
```

If a contract version is unsupported:
```
ERROR: Tool v0.2.0 does not support contract v3.0.0
Supported versions: 1.0.0, 1.1.0, 2.0.0
```

## Version in Reports

The JSON report includes version information:

```json
{
  "passed": true,
  "contract": {
    "name": "customer_data",
    "version": "2.0.0"
  },
  "metadata": {
    "tool_version": "0.2.0",
    "timestamp": "2026-02-08T10:30:45"
  },
  "version_info": {
    "breaking_changes": [
      "Removed support for 'max_null_pct' (use 'max_null_ratio' instead)",
      "Changed distribution rule syntax"
    ],
    "migration_available": true
  }
}
```

## Migration Matrix

Supported upgrade paths:

```
1.0.0 → 1.1.0 → 2.0.0
 ↓              ↓
1.1.0 → 2.0.0
 ↓
2.0.0 (latest)
```

- **Forward migration**: Supported (1.0 → 2.0)
- **Backward migration**: Not supported (can't downgrade)
- **Skipping versions**: Supported (1.0 → 2.0 directly)

## Migration Details

### 1.0.0 → 1.1.0

- Adds default `max_z_score: 3.0` to distribution rules
- Preserves all existing fields and rules

### 1.1.0 → 2.0.0

- Converts `max_null_pct` to `max_null_ratio`
  - `5` (percent) → `0.05` (ratio)
  - `100` (percent) → `1.0` (ratio)
- Updates distribution rule syntax

### 1.0.0 → 2.0.0

- Applies both migrations in sequence
- Safe and deterministic

## API Usage

### Check if version is valid

```python
from datapact.versioning import validate_version

if validate_version("2.0.0"):
    print("Version is supported")
```

### Get breaking changes

```python
from datapact.versioning import get_breaking_changes

changes = get_breaking_changes("2.0.0")
for change in changes:
    print(f"- {change}")
```

### Manual migration

```python
from datapact.versioning import VersionMigration

contract_dict = {...}  # Your contract data
migrated = VersionMigration.migrate(contract_dict, "1.0.0", "2.0.0")
```

### Check compatibility

```python
from datapact.versioning import check_tool_compatibility

is_compatible, msg = check_tool_compatibility("0.2.0", "2.0.0")
if not is_compatible:
    print(f"Error: {msg}")
```

## Best Practices

1. **Always specify version**
   ```yaml
   contract:
     version: "2.0.0"  # Don't omit this!
   ```

2. **Use latest version for new contracts**
   - Always use `2.0.0` for new contracts
   - Migrate old contracts when updating tooling

3. **Update contracts when tool updates**
   - Check breaking changes when upgrading validator
   - Run migration if needed

4. **Track version in source control**
   - Version your contracts like source code
   - Use git history to track changes

5. **Document version requirements**
   - In README: "Requires validator v0.2.0+"
   - In contract comments: "v2.0.0 compatible"

## Version History & Roadmap

```
Current: v2.0.0 (Feb 2026)
  - Latest schema format
  - Ratio-based null constraints
  - Z-score outlier detection

Previous: v1.1.0 (Feb 2026)
  - Added z-score support
  - Added ratio constraints

Initial: v1.0.0 (Jan 2026)
  - Basic validation rules
  - Percent-based constraints

Future: v3.0.0 (planned)
  - Custom validators
  - Schema inheritance
  - Conditional rules
```

## Troubleshooting

**Q: "Unknown contract version"**  
A: Update to latest validator or downgrade contract version

**Q: Contract auto-migrated unexpectedly**  
A: This is normal - validator auto-upgrades old contracts

**Q: Where's my `max_null_pct`?**  
A: Converted to `max_null_ratio` during migration (divide by 100)

**Q: Can I use old tool with new contract?**  
A: No - update tool to support latest contract version

---

**Version Status**: Updated February 8, 2026  
**Latest Version**: 2.0.0  
**Tool Version**: 0.2.0+
