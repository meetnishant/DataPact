# DataPact 2.0 Phased Checklist (Draft)

This checklist delivers DataPact2.0 by implementing one feature at a time, with explicit Feature Completion and Regression gates before moving forward. Each phase is a single feature with its own tests and regression checks, ensuring stability while adding Pact provider support, flatten normalization, and updated docs/versioning. The plan targets both ODCS and API Pact, keeps Pact external, and uses strict release gates before tagging.

## Phases

### Phase 0 - Release prep and guardrails [DONE]
- Feature: establish baseline and compliance scaffolding.
- Feature Completion Gate:
  - Update dependencies/licensing docs in README.md, DEPENDENCIES.md, CONTRIBUTING.md, and pyproject.toml.
  - Add any required third-party notices.
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v

### Phase 1 - Provider abstraction (DataPact YAML provider) [DONE]
- Feature: contract provider interface + DataPact YAML provider.
- Feature Completion Gate:
  - Add provider modules in src/datapact/providers/ with DataPact implementation.
  - Add tests in tests/test_contract_providers.py.
  - Update FILE_REFERENCE.md with providers/ directory description.
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v

### Phase 2 - ODCS provider migration [DONE]
- Feature: move ODCS mapping behind provider interface.
- Feature Completion Gate:
  - Add ODCS provider in src/datapact/providers/odcs_provider.py.
  - Keep src/datapact/odcs_contracts.py as mapper.
  - Add ODCS provider tests in tests/test_contract_providers.py and keep tests/test_odcs_contract.py green.
  - Update FILE_REFERENCE.md with ODCS provider details.
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v

### Phase 3 - CLI provider dispatch [DONE]
- Feature: CLI uses provider resolution for --contract-format.
- Feature Completion Gate:
  - Refactor src/datapact/cli.py to dispatch providers.
  - Add CLI path tests in tests/test_contract_providers.py or new targeted CLI tests.
  - Update README.md CLI documentation with --contract-format option.
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v

### Phase 4 - Flatten normalization core [DONE]
- Feature: new normalization layer (no behavior change by default).
- Feature Completion Gate:
  - Implement src/datapact/normalization/ with config + noop default.
  - Add tests in tests/test_flatten_normalization.py.
  - Update FILE_REFERENCE.md with normalization/ directory description.
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v

### Phase 5 - Contract model extension for flatten config [DONE]
- Feature: add flatten metadata to internal contract model.
- Feature Completion Gate:
  - Update src/datapact/contracts.py parsing and defaults.
  - Add contract parse tests in tests/test_contract_providers.py.
  - Update FEATURES.md with flatten metadata example.
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v

### Phase 6 - Wire normalization into validation pipeline [DONE]
- Feature: normalize dataframes before validators.
- Feature Completion Gate:
  - Integrate normalization in src/datapact/cli.py.
  - Add integration tests in tests/test_exhaustive_features.py or new normalization-aware tests.
  - Update docs/ARCHITECTURE.md validation semantics section with normalization step.
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v

### Phase 7 - Validator/path alignment for flattened fields [DONE]
- Feature: ensure validators operate correctly with flattened columns.
- Feature Completion Gate:
  - Adjust validators as needed: schema, quality, distribution, custom rules.
  - Add tests in tests/test_flatten_normalization.py.
  - Update FILE_REFERENCE.md with flatten-aware validator descriptions.
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v

### Phase 8 - API Pact provider (external dependency) [DONE]
- Feature: map API Pact contracts to internal Contract.
- Feature Completion Gate:
  - Implement src/datapact/providers/pact_provider.py with warnings for unsupported rules.
  - Add fixtures + tests in tests/test_contract_providers.py.
  - Update README.md (features + CLI options), FEATURES.md (provider examples), FILE_REFERENCE.md (pact_provider details), docs/ARCHITECTURE.md (providers section), QUICKSTART.md (pact example), PROJECT_STRUCTURE.md (pact files).
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v

### Phase 9 - Reporting lineage enhancements
- Feature: include logical path + flattened column in errors.
- Feature Completion Gate:
  - Update src/datapact/reporting.py and related error records.
  - Add tests in tests/test_reporting.py.
  - Update FILE_REFERENCE.md reporting section + docs/ARCHITECTURE.md reporting section.
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v

### Phase 10 - Versioning and migration for 2.0 release
- Feature: tool/contract version updates + migration notes.
- Feature Completion Gate:
  - Update src/datapact/versioning.py and docs/VERSIONING.md.
  - Add tests in tests/test_versioning.py.
  - Update FILE_REFERENCE.md versioning section + README.md version info.
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v

### Phase 11 - Final documentation polish (optional)
- Feature: comprehensive documentation review and examples.
- Feature Completion Gate:
  - Review all docs for completeness and accuracy.
  - Add examples in docs/EXAMPLES.md covering all providers and features.
  - Update CONTRIBUTING.md with new provider pattern guidance.
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v

### Phase 12 - Strict release gate and tagging
- Feature: finalize, then tag.
- Feature Completion Gate:
  - Run: black src/ tests/
  - Run: ruff check src/ tests/
  - Run: mypy src/
  - Run: pytest -n auto --cov=src/datapact --cov-report=term-missing -v
  - Fix issues and update changelog if present.
- Regression Gate:
  - Run: pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v
- Release:
  - Commit, merge to main, tag DataPact2.0, push tag to GitHub, verify with git ls-remote --tags origin DataPact2.0.

## Notes
- External Pact dependency only, no vendoring.
- Both ODCS and API Pact providers in 2.0.
- New flatten normalization layer.
- Strict release gate before tagging.
- **Documentation updates happen immediately after each phase** (included in Feature Completion Gate, not deferred until Phase 11).
  - Affects: README.md, FEATURES.md, FILE_REFERENCE.md, QUICKSTART.md, PROJECT_STRUCTURE.md, docs/ARCHITECTURE.md, CONTRIBUTING.md
  - Timing: Update docs BEFORE moving to the next phase to keep docs in sync with code.

**4) Add a short note in contributing setup**
```diff
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@
 4. Install with dev dependencies: `pip install -e ".[dev]"`
   - Note: `pact-python` is installed with base dependencies for API Pact integration.
```

