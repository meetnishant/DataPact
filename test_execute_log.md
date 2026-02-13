# Test Execution Log

**Last Updated:** February 13, 2026  
**Test Run:** Complete test suite execution  
**Environment:** macOS with Python 3.9.6, pytest 8.4.2

## Summary

- **Total Tests:** 149
- **Passed:** 148 ✅
- **Skipped:** 1 (MySQL tests - requires optional dependency)
- **Failed:** 0 ❌
- **Execution Time:** 1.65 seconds

## Command

```bash
source .venv/bin/activate && python -m pytest tests/ -v --tb=short
```

## Test Results

### Test Suite Breakdown

#### Banking & Finance Tests (19 tests)
- ✅ TestDepositsAccountsStrict: 3/3 passed
- ✅ TestDepositsAccountsAggregate: 2/2 passed  
- ✅ TestDepositsTransactions: 3/3 passed
- ✅ TestLendingLoansStrict: 3/3 passed
- ✅ TestLendingLoansAggregate: 1/1 passed
- ✅ TestLendingPayments: 3/3 passed
- ✅ TestComplexConsumption: 2/2 passed
- ✅ TestValidationExceptions: 2/2 passed

#### Chunked Validation Tests (3 tests)
- ✅ test_iter_chunks_csv
- ✅ test_iter_chunks_jsonl
- ✅ test_chunked_unique_across_chunks

#### Concurrency Tests (2 tests)
- ✅ test_concurrent_validators_no_exceptions
- ✅ test_multiprocess_validators_no_exceptions

#### Contract Providers Tests (17 tests)
- ✅ DataPact provider: 4/4 passed
- ✅ ODCS provider: 4/4 passed
- ✅ CLI resolution: 4/4 passed
- ✅ Pact provider: 5/5 passed

#### Custom Rules Tests (2 tests)
- ✅ test_custom_field_rule_plugin
- ✅ test_custom_dataset_rule_plugin

#### Database Source Tests (4 tests)
- ✅ test_sqlite_load_and_infer_schema
- ✅ test_sqlite_iter_chunks
- ✅ test_missing_table_or_query_raises
- ⏭️ test_mysql_load_table (SKIPPED - requires DATAPACT_MYSQL_TESTS=1)

#### Exhaustive Features Tests (36 tests)
- ✅ TestSchemaValidationExhaustive: 7/7 passed
- ✅ TestQualityRulesExhaustive: 11/11 passed
- ✅ TestSeverityExhaustive: 5/5 passed
- ✅ TestDistributionExhaustive: 3/3 passed
- ✅ TestSLAAndFreshnessExhaustive: 7/7 passed
- ✅ TestChunkedAndSamplingExhaustive: 4/4 passed
- ✅ TestCustomRulesExhaustive: 2/2 passed
- ✅ TestPolicyPacksExhaustive: 2/2 passed
- ✅ TestReportSinksExhaustive: 1/1 passed

#### Flatten Normalization Tests (3 tests)
- ✅ test_normalize_dataframe_noop_default
- ✅ test_normalize_dataframe_noop_config
- ✅ test_build_normalization_config_disabled

#### Flattened Field Resolution Tests (4 tests)
- ✅ test_schema_validator_resolves_flattened_columns
- ✅ test_quality_validator_resolves_flattened_columns
- ✅ test_distribution_validator_resolves_flattened_columns
- ✅ test_custom_rule_validator_resolves_flattened_columns

#### ODCS Contract Tests (5 tests)
- ✅ test_odcs_minimal_mapping
- ✅ test_odcs_requires_object_selection_when_multiple
- ✅ test_odcs_invalid_version_rejected
- ✅ test_odcs_quality_sql_custom_warns
- ✅ test_odcs_logical_type_timestamp_warns

#### Policy Packs Tests (2 tests)
- ✅ test_policy_pack_applies_rules
- ✅ test_policy_pack_overrides_rule

#### Profiling Tests (2 tests)
- ✅ test_profile_dataframe_basic
- ✅ test_profile_dataframe_no_distribution

#### Reporting Tests (7 tests)
- ✅ test_file_report_sink_writes_json
- ✅ test_stdout_report_sink_prints_json
- ✅ test_webhook_report_sink_posts_json
- ✅ test_webhook_report_sink_failure
- ✅ test_error_record_with_logical_path
- ✅ test_error_record_to_dict_includes_lineage
- ✅ test_print_summary_with_flattened_column
- ✅ test_print_summary_without_lineage

#### Core Validator Tests (13 tests)
- ✅ TestSchemaValidator: 3/3 passed
- ✅ TestQualityValidator: 6/6 passed
- ✅ TestDataSource: 3/3 passed
- ✅ TestDistributionValidator: 1/1 passed
- ✅ TestSLAValidator: 2/2 passed

#### Versioning Tests (17 tests)
- ✅ TestVersionValidation: 4/4 passed
- ✅ TestToolCompatibility: 4/4 passed
- ✅ TestVersionMigration: 5/5 passed
- ✅ TestContractVersionLoading: 4/4 passed
- ✅ TestVersionInfo: 1/1 passed

## Full Test Output

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Users/meetnishant/Documents/DataContracts/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/meetnishant/Documents/DataContracts
configfile: pyproject.toml
plugins: anyio-4.12.1, cov-7.0.0
collecting ... collected 149 items

tests/test_banking_finance.py::TestDepositsAccountsStrict::test_positive_cases PASSED [  0%]
tests/test_banking_finance.py::TestDepositsAccountsStrict::test_negative_cases PASSED [  1%]
tests/test_banking_finance.py::TestDepositsAccountsStrict::test_boundary_cases PASSED [  2%]
tests/test_banking_finance.py::TestDepositsAccountsAggregate::test_aggregate_consumer_contract PASSED [  2%]
tests/test_banking_finance.py::TestDepositsAccountsAggregate::test_max_null_ratio_empty_dataset PASSED [  3%]
tests/test_banking_finance.py::TestDepositsTransactions::test_positive_cases PASSED [  4%]
tests/test_banking_finance.py::TestDepositsTransactions::test_negative_cases PASSED [  4%]
tests/test_banking_finance.py::TestDepositsTransactions::test_boundary_cases PASSED [  5%]
tests/test_banking_finance.py::TestLendingLoansStrict::test_positive_cases PASSED [  6%]
tests/test_banking_finance.py::TestLendingLoansStrict::test_negative_cases PASSED [  6%]
tests/test_banking_finance.py::TestLendingLoansStrict::test_boundary_cases PASSED [  7%]
tests/test_banking_finance.py::TestLendingLoansAggregate::test_aggregate_consumer_contract PASSED [  8%]
tests/test_banking_finance.py::TestLendingPayments::test_positive_cases PASSED [  8%]
tests/test_banking_finance.py::TestLendingPayments::test_negative_cases PASSED [  9%]
tests/test_banking_finance.py::TestLendingPayments::test_boundary_cases PASSED [ 10%]
tests/test_banking_finance.py::TestComplexConsumption::test_deposits_position_join PASSED [ 10%]
tests/test_banking_finance.py::TestComplexConsumption::test_time_window_aggregation PASSED [ 11%]
tests/test_banking_finance.py::TestValidationExceptions::test_invalid_regex_rule PASSED [ 12%]
tests/test_banking_finance.py::TestValidationExceptions::test_unhashable_enum_rule PASSED [ 12%]
tests/test_chunked_validation.py::test_iter_chunks_csv PASSED            [ 13%]
tests/test_chunked_validation.py::test_iter_chunks_jsonl PASSED          [ 14%]
tests/test_chunked_validation.py::test_chunked_unique_across_chunks PASSED [ 14%]
tests/test_concurrency.py::test_concurrent_validators_no_exceptions PASSED [ 15%]
tests/test_concurrency_mp.py::test_multiprocess_validators_no_exceptions PASSED [ 16%]
tests/test_contract_providers.py::test_datapact_provider_can_load_datapact_contract PASSED [ 16%]
tests/test_contract_providers.py::test_datapact_provider_rejects_odcs_contract PASSED [ 17%]
tests/test_contract_providers.py::test_datapact_provider_loads_from_dict PASSED [ 18%]
tests/test_contract_providers.py::test_datapact_provider_loads_from_path PASSED [ 18%]
tests/test_contract_providers.py::test_odcs_provider_can_load_odcs_contract PASSED [ 19%]
tests/test_contract_providers.py::test_odcs_provider_loads_from_dict PASSED [ 20%]
tests/test_contract_providers.py::test_odcs_provider_rejects_invalid_version PASSED [ 20%]
tests/test_contract_providers.py::test_odcs_provider_loads_selected_object PASSED [ 21%]
tests/test_contract_providers.py::test_cli_resolves_datapact_provider PASSED [ 22%]
tests/test_contract_providers.py::test_cli_resolves_odcs_provider PASSED [ 22%]
tests/test_contract_providers.py::test_cli_auto_selects_odcs_provider PASSED [ 23%]
tests/test_contract_providers.py::test_cli_rejects_mismatched_format PASSED [ 24%]
tests/test_contract_providers.py::test_contract_parses_flatten_config PASSED [ 24%]
tests/test_contract_providers.py::test_pact_provider_loads_pact_contract PASSED [ 25%]
tests/test_contract_providers.py::test_pact_provider_infers_field_types PASSED [ 26%]
tests/test_contract_providers.py::test_pact_provider_marks_fields_as_optional PASSED [ 26%]
tests/test_contract_providers.py::test_pact_provider_rejects_missing_response_body PASSED [ 27%]
tests/test_contract_providers.py::test_pact_provider_rejects_non_object_response_body PASSED [ 28%]
tests/test_custom_rules.py::test_custom_field_rule_plugin PASSED         [ 28%]
tests/test_custom_rules.py::test_custom_dataset_rule_plugin PASSED       [ 29%]
tests/test_db_source.py::test_sqlite_load_and_infer_schema PASSED        [ 30%]
tests/test_db_source.py::test_sqlite_iter_chunks PASSED                  [ 30%]
tests/test_db_source.py::test_missing_table_or_query_raises PASSED       [ 31%]
tests/test_db_source.py::test_mysql_load_table SKIPPED (MySQL tests ...) [ 32%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_valid PASSED [ 32%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_missing_required PASSED [ 33%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_type_mismatch PASSED [ 34%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_warn PASSED [ 34%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_warn PASSED [ 35%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_error PASSED [ 36%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_error PASSED [ 36%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_valid PASSED [ 37%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_nulls PASSED [ 38%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_duplicates PASSED [ 38%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_boundary PASSED [ 39%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_fail PASSED [ 40%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_boundary PASSED [ 40%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_fail PASSED [ 41%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_boundary PASSED [ 42%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_fail PASSED [ 42%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_boundary PASSED [ 43%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_fail PASSED [ 44%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_valid PASSED [ 44%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_warn PASSED [ 45%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_override PASSED [ 46%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_invalid PASSED [ 46%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_invalid_severity_override_format PASSED [ 47%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_valid PASSED [ 48%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_drift PASSED [ 48%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_boundary PASSED [ 49%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_boundary PASSED [ 50%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_boundary PASSED [ 51%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_fail PASSED [ 51%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_fail_warn PASSED [ 52%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_ok PASSED [ 53%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_boundary PASSED [ 53%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_fail PASSED [ 54%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_size_one PASSED [ 55%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_empty PASSED [ 55%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_rows_deterministic PASSED [ 56%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_frac_deterministic PASSED [ 57%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_missing PASSED [ 57%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_invalid_config PASSED [ 58%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_unknown PASSED [ 59%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_override_conflict PASSED [ 59%]
tests/test_exhaustive_features.py::TestReportSinksExhaustive::test_webhook_header_invalid PASSED [ 60%]
tests/test_flatten_normalization.py::test_normalize_dataframe_noop_default PASSED [ 61%]
tests/test_flatten_normalization.py::test_normalize_dataframe_noop_config PASSED [ 61%]
tests/test_flatten_normalization.py::test_build_normalization_config_disabled PASSED [ 62%]
tests/test_flatten_normalization.py::test_build_normalization_config_flatten_enabled PASSED [ 63%]
tests/test_flattened_field_resolution.py::test_schema_validator_resolves_flattened_columns PASSED [ 63%]
tests/test_flattened_field_resolution.py::test_quality_validator_resolves_flattened_columns PASSED [ 64%]
tests/test_flattened_field_resolution.py::test_distribution_validator_resolves_flattened_columns PASSED [ 65%]
tests/test_flattened_field_resolution.py::test_custom_rule_validator_resolves_flattened_columns PASSED [ 65%]
tests/test_odcs_contract.py::test_odcs_minimal_mapping PASSED            [ 66%]
tests/test_odcs_contract.py::test_odcs_requires_object_selection_when_multiple PASSED [ 67%]
tests/test_odcs_contract.py::test_odcs_invalid_version_rejected PASSED   [ 67%]
tests/test_odcs_contract.py::test_odcs_quality_sql_custom_warns PASSED   [ 68%]
tests/test_odcs_contract.py::test_odcs_logical_type_timestamp_warns PASSED [ 69%]
tests/test_policy_packs.py::test_policy_pack_applies_rules PASSED        [ 69%]
tests/test_policy_packs.py::test_policy_pack_overrides_rule PASSED       [ 70%]
tests/test_profiling.py::test_profile_dataframe_basic PASSED             [ 71%]
tests/test_profiling.py::test_profile_dataframe_no_distribution PASSED   [ 71%]
tests/test_reporting.py::test_file_report_sink_writes_json PASSED        [ 72%]
tests/test_reporting.py::test_stdout_report_sink_prints_json PASSED      [ 73%]
tests/test_reporting.py::test_webhook_report_sink_posts_json PASSED      [ 73%]
tests/test_reporting.py::test_webhook_report_sink_failure PASSED         [ 74%]
tests/test_reporting.py::test_error_record_with_logical_path PASSED      [ 75%]
tests/test_reporting.py::test_error_record_to_dict_includes_lineage PASSED [ 75%]
tests/test_reporting.py::test_print_summary_with_flattened_column PASSED [ 76%]
tests/test_reporting.py::test_print_summary_without_lineage PASSED       [ 77%]
tests/test_validator.py::TestSchemaValidator::test_valid_schema PASSED   [ 77%]
tests/test_validator.py::TestSchemaValidator::test_missing_required_field PASSED [ 78%]
tests/test_validator.py::TestSchemaValidator::test_extra_columns_error_severity PASSED [ 79%]
tests/test_validator.py::TestQualityValidator::test_valid_data PASSED    [ 79%]
tests/test_validator.py::TestQualityValidator::test_invalid_email_regex PASSED [ 80%]
tests/test_validator.py::TestQualityValidator::test_null_constraint PASSED [ 81%]
tests/test_validator.py::TestQualityValidator::test_enum_constraint PASSED [ 81%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_warn PASSED [ 82%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_override PASSED [ 83%]
tests/test_validator.py::TestQualityValidator::test_freshness_max_age_hours PASSED [ 83%]
tests/test_validator.py::TestDataSource::test_load_csv PASSED            [ 84%]
tests/test_validator.py::TestDataSource::test_detect_format PASSED       [ 85%]
tests/test_validator.py::TestDataSource::test_infer_schema PASSED        [ 85%]
tests/test_validator.py::TestDistributionValidator::test_normal_distribution PASSED [ 86%]
tests/test_validator.py::TestSLAValidator::test_min_rows_violation PASSED [ 87%]
tests/test_validator.py::TestSLAValidator::test_max_rows_warn_severity PASSED [ 87%]
tests/test_versioning.py::TestVersionValidation::test_valid_version PASSED [ 88%]
tests/test_versioning.py::TestVersionValidation::test_invalid_version PASSED [ 89%]
tests/test_versioning.py::TestVersionValidation::test_deprecated_version PASSED [ 89%]
tests/test_versioning.py::TestVersionValidation::test_breaking_changes PASSED [ 90%]
tests/test_versioning.py::TestToolCompatibility::test_compatible_versions PASSED [ 91%]
tests/test_versioning.py::TestToolCompatibility::test_incompatible_versions PASSED [ 91%]
tests/test_versioning.py::TestToolCompatibility::test_unknown_contract_version PASSED [ 92%]
tests/test_versioning.py::TestToolCompatibility::test_tool_2_0_0_compatibility PASSED [ 93%]
tests/test_versioning.py::TestVersionMigration::test_no_migration_same_version PASSED [ 93%]
tests/test_versioning.py::TestVersionMigration::test_migrate_1_0_to_1_1 PASSED [ 94%]
tests/test_versioning.py::TestVersionMigration::test_migrate_1_1_to_2_0 PASSED [ 95%]
tests/test_versioning.py::TestVersionMigration::test_multi_step_migration PASSED [ 95%]
tests/test_versioning.py::TestVersionMigration::test_unsupported_downgrade PASSED [ 96%]
tests/test_versioning.py::TestContractVersionLoading::test_load_v1_contract PASSED [ 97%]
tests/test_versioning.py::TestContractVersionLoading::test_load_v2_contract PASSED [ 97%]
tests/test_versioning.py::TestContractVersionLoading::test_load_contract_without_version PASSED [ 98%]
tests/test_versioning.py::TestContractVersionLoading::test_load_contract_with_unknown_version PASSED [ 99%]
tests/test_versioning.py::TestVersionInfo::test_latest_version PASSED    [100%]

======================== 148 passed, 1 skipped in 1.65s ========================
```

## Notes

- All core tests passing successfully
- MySQL test skipped (requires `DATAPACT_MYSQL_TESTS=1` environment variable)
- Test execution is fast (1.65 seconds for 149 tests)
- All features validated: schema, quality, distribution, versioning, ODCS, Pact providers, custom rules, policy packs, reporting, concurrency, flattening, and database sources
