# Test Execution Log

Command:

```
DATAPACT_MYSQL_TESTS=1 DATAPACT_MYSQL_PASSWORD=<your-mysql-password> PYTHONPATH=./src python3 -m pytest -v
```

Output:

```
Note: The tool simplified the command to ` DATAPACT_MYSQL_TESTS=1 DATAPACT_MYSQL_PASSWORD=<your-mysql-password> PYTHONPATH=./src python3 -m pytest -v`, and this is the output of running that command instead:
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Library/Develope
r/CommandLineTools/usr/bin/python3                                              cachedir: .pytest_cache
rootdir: /Users/meetnishant/Documents/DataContracts
configfile: pyproject.toml
testpaths: tests
plugins: xdist-3.8.0, cov-7.0.0
collected 118 items                                                            

tests/test_banking_finance.py::TestDepositsAccountsStrict::test_positive_cases P
ASSED [  0%]                                                                    tests/test_banking_finance.py::TestDepositsAccountsStrict::test_negative_cases P
ASSED [  1%]                                                                    tests/test_banking_finance.py::TestDepositsAccountsStrict::test_boundary_cases P
ASSED [  2%]                                                                    tests/test_banking_finance.py::TestDepositsAccountsAggregate::test_aggregate_con
sumer_contract PASSED [  3%]                                                    tests/test_banking_finance.py::TestDepositsAccountsAggregate::test_max_null_rati
o_empty_dataset PASSED [  4%]                                                   tests/test_banking_finance.py::TestDepositsTransactions::test_positive_cases PAS
SED [  5%]                                                                      tests/test_banking_finance.py::TestDepositsTransactions::test_negative_cases PAS
SED [  5%]                                                                      tests/test_banking_finance.py::TestDepositsTransactions::test_boundary_cases PAS
SED [  6%]                                                                      tests/test_banking_finance.py::TestLendingLoansStrict::test_positive_cases PASSE
D [  7%]                                                                        tests/test_banking_finance.py::TestLendingLoansStrict::test_negative_cases PASSE
D [  8%]                                                                        tests/test_banking_finance.py::TestLendingLoansStrict::test_boundary_cases PASSE
D [  9%]                                                                        tests/test_banking_finance.py::TestLendingLoansAggregate::test_aggregate_consume
r_contract PASSED [ 10%]                                                        tests/test_banking_finance.py::TestLendingPayments::test_positive_cases PASSED [
 11%]                                                                           tests/test_banking_finance.py::TestLendingPayments::test_negative_cases PASSED [
 11%]                                                                           tests/test_banking_finance.py::TestLendingPayments::test_boundary_cases PASSED [
 12%]                                                                           tests/test_banking_finance.py::TestComplexConsumption::test_deposits_position_jo
in PASSED [ 13%]                                                                tests/test_banking_finance.py::TestComplexConsumption::test_time_window_aggregat
ion PASSED [ 14%]                                                               tests/test_banking_finance.py::TestValidationExceptions::test_invalid_regex_rule
 PASSED [ 15%]                                                                  tests/test_banking_finance.py::TestValidationExceptions::test_unhashable_enum_ru
le PASSED [ 16%]                                                                tests/test_chunked_validation.py::test_iter_chunks_csv PASSED            [ 16%]
tests/test_chunked_validation.py::test_iter_chunks_jsonl PASSED          [ 17%]
tests/test_chunked_validation.py::test_chunked_unique_across_chunks PASSED [ 18%
]                                                                               tests/test_concurrency.py::test_concurrent_validators_no_exceptions PASSED [ 19%
]                                                                               tests/test_concurrency_mp.py::test_multiprocess_validators_no_exceptions PASSED 
[ 20%]                                                                          tests/test_custom_rules.py::test_custom_field_rule_plugin PASSED         [ 21%]
tests/test_custom_rules.py::test_custom_dataset_rule_plugin PASSED       [ 22%]
tests/test_db_source.py::test_sqlite_load_and_infer_schema PASSED        [ 22%]
tests/test_db_source.py::test_sqlite_iter_chunks PASSED                  [ 23%]
tests/test_db_source.py::test_missing_table_or_query_raises PASSED       [ 24%]
tests/test_db_source.py::test_mysql_load_table PASSED                    [ 25%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_v
alid PASSED [ 26%]                                                              tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_m
issing_required PASSED [ 27%]                                                   tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_t
ype_mismatch PASSED [ 27%]                                                      tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_e
xtra_columns_warn PASSED [ 28%]                                                 tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_d
rift_warn PASSED [ 29%]                                                         tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_d
rift_error PASSED [ 30%]                                                        tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_e
xtra_columns_error PASSED [ 31%]                                                tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_vali
d PASSED [ 32%]                                                                 tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_null
s PASSED [ 33%]                                                                 tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_dupl
icates PASSED [ 33%]                                                            tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minm
ax_boundary PASSED [ 34%]                                                       tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minm
ax_fail PASSED [ 35%]                                                           tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum
_boundary PASSED [ 36%]                                                         tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum
_fail PASSED [ 37%]                                                             tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_rege
x_boundary PASSED [ 38%]                                                        tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_rege
x_fail PASSED [ 38%]                                                            tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_
null_ratio_boundary PASSED [ 39%]                                               tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_
null_ratio_fail PASSED [ 40%]                                                   tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_va
lid PASSED [ 41%]                                                               tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_wa
rn PASSED [ 42%]                                                                tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_ov
erride PASSED [ 43%]                                                            tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_in
valid PASSED [ 44%]                                                             tests/test_exhaustive_features.py::TestSeverityExhaustive::test_invalid_severity
_override_format PASSED [ 44%]                                                  tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution
_valid PASSED [ 45%]                                                            tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution
_drift PASSED [ 46%]                                                            tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution
_boundary PASSED [ 47%]                                                         tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_b
oundary PASSED [ 48%]                                                           tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_b
oundary PASSED [ 49%]                                                           tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_f
ail PASSED [ 50%]                                                               tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_f
ail_warn PASSED [ 50%]                                                          tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness
_ok PASSED [ 51%]                                                               tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness
_boundary PASSED [ 52%]                                                         tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness
_fail PASSED [ 53%]                                                             tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunke
d_size_one PASSED [ 54%]                                                        tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunke
d_empty PASSED [ 55%]                                                           tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampli
ng_rows_deterministic PASSED [ 55%]                                             tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampli
ng_frac_deterministic PASSED [ 56%]                                             tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_m
issing PASSED [ 57%]                                                            tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_i
nvalid_config PASSED [ 58%]                                                     tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_u
nknown PASSED [ 59%]                                                            tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_o
verride_conflict PASSED [ 60%]                                                  tests/test_exhaustive_features.py::TestReportSinksExhaustive::test_webhook_heade
r_invalid PASSED [ 61%]                                                         tests/test_odcs_contract.py::test_odcs_minimal_mapping PASSED            [ 61%]
tests/test_odcs_contract.py::test_odcs_requires_object_selection_when_multiple P
ASSED [ 62%]                                                                    tests/test_odcs_contract.py::test_odcs_invalid_version_rejected PASSED   [ 63%]
tests/test_odcs_contract.py::test_odcs_quality_sql_custom_warns PASSED   [ 64%]
tests/test_odcs_contract.py::test_odcs_logical_type_timestamp_warns PASSED [ 65%
]                                                                               tests/test_policy_packs.py::test_policy_pack_applies_rules PASSED        [ 66%]
tests/test_policy_packs.py::test_policy_pack_overrides_rule PASSED       [ 66%]
tests/test_profiling.py::test_profile_dataframe_basic PASSED             [ 67%]
tests/test_profiling.py::test_profile_dataframe_no_distribution PASSED   [ 68%]
tests/test_reporting.py::test_file_report_sink_writes_json PASSED        [ 69%]
tests/test_reporting.py::test_stdout_report_sink_prints_json PASSED      [ 70%]
tests/test_reporting.py::test_webhook_report_sink_posts_json PASSED      [ 71%]
tests/test_reporting.py::test_webhook_report_sink_failure PASSED         [ 72%]
tests/test_validator.py::TestSchemaValidator::test_valid_schema PASSED   [ 72%]
tests/test_validator.py::TestSchemaValidator::test_missing_required_field PASSED
 [ 73%]                                                                         tests/test_validator.py::TestSchemaValidator::test_extra_columns_error_severity 
PASSED [ 74%]                                                                   tests/test_validator.py::TestQualityValidator::test_valid_data PASSED    [ 75%]
tests/test_validator.py::TestQualityValidator::test_invalid_email_regex PASSED [
 76%]                                                                           tests/test_validator.py::TestQualityValidator::test_null_constraint PASSED [ 77%
]                                                                               tests/test_validator.py::TestQualityValidator::test_enum_constraint PASSED [ 77%
]                                                                               tests/test_validator.py::TestQualityValidator::test_rule_severity_warn PASSED [ 
78%]                                                                            tests/test_validator.py::TestQualityValidator::test_rule_severity_override PASSE
D [ 79%]                                                                        tests/test_validator.py::TestQualityValidator::test_freshness_max_age_hours PASS
ED [ 80%]                                                                       tests/test_validator.py::TestDataSource::test_load_csv PASSED            [ 81%]
tests/test_validator.py::TestDataSource::test_detect_format PASSED       [ 82%]
tests/test_validator.py::TestDataSource::test_infer_schema PASSED        [ 83%]
tests/test_validator.py::TestDistributionValidator::test_normal_distribution PAS
SED [ 83%]                                                                      tests/test_validator.py::TestSLAValidator::test_min_rows_violation PASSED [ 84%]
tests/test_validator.py::TestSLAValidator::test_max_rows_warn_severity PASSED [ 
85%]                                                                            tests/test_versioning.py::TestVersionValidation::test_valid_version PASSED [ 86%
]                                                                               tests/test_versioning.py::TestVersionValidation::test_invalid_version PASSED [ 8
7%]                                                                             tests/test_versioning.py::TestVersionValidation::test_deprecated_version PASSED 
[ 88%]                                                                          tests/test_versioning.py::TestVersionValidation::test_breaking_changes PASSED [ 
88%]                                                                            tests/test_versioning.py::TestToolCompatibility::test_compatible_versions PASSED
 [ 89%]                                                                         tests/test_versioning.py::TestToolCompatibility::test_incompatible_versions PASS
ED [ 90%]                                                                       tests/test_versioning.py::TestToolCompatibility::test_unknown_contract_version P
ASSED [ 91%]                                                                    tests/test_versioning.py::TestVersionMigration::test_no_migration_same_version P
ASSED [ 92%]                                                                    tests/test_versioning.py::TestVersionMigration::test_migrate_1_0_to_1_1 PASSED [
 93%]                                                                           tests/test_versioning.py::TestVersionMigration::test_migrate_1_1_to_2_0 PASSED [
 94%]                                                                           tests/test_versioning.py::TestVersionMigration::test_multi_step_migration PASSED
 [ 94%]                                                                         tests/test_versioning.py::TestVersionMigration::test_unsupported_downgrade PASSE
D [ 95%]                                                                        tests/test_versioning.py::TestContractVersionLoading::test_load_v1_contract PASS
ED [ 96%]                                                                       tests/test_versioning.py::TestContractVersionLoading::test_load_v2_contract PASS
ED [ 97%]                                                                       tests/test_versioning.py::TestContractVersionLoading::test_load_contract_without
_version PASSED [ 98%]                                                          tests/test_versioning.py::TestContractVersionLoading::test_load_contract_with_un
known_version PASSED [ 99%]                                                     tests/test_versioning.py::TestVersionInfo::test_latest_version PASSED    [100%]

=============================== warnings summary ===============================
tests/test_db_source.py::test_mysql_load_table
  /Users/meetnishant/Documents/DataContracts/src/datapact/datasource.py:225: Use
rWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.                                               self.df = pd.read_sql_query(query, conn)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 118 passed, 1 warning in 1.01s ========================
```

Phase 1 regression gate:

Command:

```
.venv/bin/python -m pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v
```

Output:

```
Note: The tool simplified the command to ` .venv/bin/python -m pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v`, and this is the output of running that command instead:
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Users/meetnishant/Documents/DataContracts/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/meetnishant/Documents/DataContracts
configfile: pyproject.toml
plugins: anyio-4.12.1, cov-7.0.0
collected 63 items

tests/test_validator.py::TestSchemaValidator::test_valid_schema PASSED   [  1%]
tests/test_validator.py::TestSchemaValidator::test_missing_required_field PASSED [  3%]
tests/test_validator.py::TestSchemaValidator::test_extra_columns_error_severity PASSED [  4%]
tests/test_validator.py::TestQualityValidator::test_valid_data PASSED    [  6%]
tests/test_validator.py::TestQualityValidator::test_invalid_email_regex PASSED [  7%]
tests/test_validator.py::TestQualityValidator::test_null_constraint PASSED [  9%]
tests/test_validator.py::TestQualityValidator::test_enum_constraint PASSED [ 11%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_warn PASSED [ 12%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_override PASSED [ 14%]
tests/test_validator.py::TestQualityValidator::test_freshness_max_age_hours PASSED [ 15%]
tests/test_validator.py::TestDataSource::test_load_csv PASSED            [ 17%]
tests/test_validator.py::TestDataSource::test_detect_format PASSED       [ 19%]
tests/test_validator.py::TestDataSource::test_infer_schema PASSED        [ 20%]
tests/test_validator.py::TestDistributionValidator::test_normal_distribution PASSED [ 22%]
tests/test_validator.py::TestSLAValidator::test_min_rows_violation PASSED [ 23%]
tests/test_validator.py::TestSLAValidator::test_max_rows_warn_severity PASSED [ 25%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_valid PASSED [ 26%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_missing_required PASSED [ 28%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_type_mismatch PASSED [ 30%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_warn PASSED [ 31%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_warn PASSED [ 33%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_error PASSED [ 34%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_error PASSED [ 36%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_valid PASSED [ 38%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_nulls PASSED [ 39%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_duplicates PASSED [ 41%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_boundary PASSED [ 42%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_fail PASSED [ 44%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_boundary PASSED [ 46%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_fail PASSED [ 47%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_boundary PASSED [ 49%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_fail PASSED [ 50%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_boundary PASSED [ 52%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_fail PASSED [ 53%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_valid PASSED [ 55%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_warn PASSED [ 57%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_override PASSED [ 58%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_invalid PASSED [ 60%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_invalid_severity_override_format PASSED [ 61%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_valid PASSED [ 63%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_drift PASSED [ 65%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_boundary PASSED [ 66%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_boundary PASSED [ 68%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_boundary PASSED [ 69%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_fail PASSED [ 71%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_fail_warn PASSED [ 73%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_ok PASSED [ 74%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_boundary PASSED [ 76%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_fail PASSED [ 77%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_size_one PASSED [ 79%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_empty PASSED [ 80%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_rows_deterministic PASSED [ 82%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_frac_deterministic PASSED [ 84%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_missing PASSED [ 85%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_invalid_config PASSED [ 87%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_unknown PASSED [ 88%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_override_conflict PASSED [ 90%]
tests/test_exhaustive_features.py::TestReportSinksExhaustive::test_webhook_header_invalid PASSED [ 92%]
tests/test_odcs_contract.py::test_odcs_minimal_mapping PASSED            [ 93%]
tests/test_odcs_contract.py::test_odcs_requires_object_selection_when_multiple PASSED [ 95%]
tests/test_odcs_contract.py::test_odcs_invalid_version_rejected PASSED   [ 96%]
tests/test_odcs_contract.py::test_odcs_quality_sql_custom_warns PASSED   [ 98%]
tests/test_odcs_contract.py::test_odcs_logical_type_timestamp_warns PASSED [100%]

============================== 63 passed in 1.70s ==============================
```

Phase 2 regression gate:

Command:

```
.venv/bin/python -m pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v
```

Output:

```
Note: The tool simplified the command to ` .venv/bin/python -m pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v`, and this is the output of running that command instead:
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Users/meetnishant/Documents/DataContracts/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/meetnishant/Documents/DataContracts
configfile: pyproject.toml
plugins: anyio-4.12.1, cov-7.0.0
collected 63 items

tests/test_validator.py::TestSchemaValidator::test_valid_schema PASSED   [  1%]
tests/test_validator.py::TestSchemaValidator::test_missing_required_field PASSED [  3%]
tests/test_validator.py::TestSchemaValidator::test_extra_columns_error_severity PASSED [  4%]
tests/test_validator.py::TestQualityValidator::test_valid_data PASSED    [  6%]
tests/test_validator.py::TestQualityValidator::test_invalid_email_regex PASSED [  7%]
tests/test_validator.py::TestQualityValidator::test_null_constraint PASSED [  9%]
tests/test_validator.py::TestQualityValidator::test_enum_constraint PASSED [ 11%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_warn PASSED [ 12%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_override PASSED [ 14%]
tests/test_validator.py::TestQualityValidator::test_freshness_max_age_hours PASSED [ 15%]
tests/test_validator.py::TestDataSource::test_load_csv PASSED            [ 17%]
tests/test_validator.py::TestDataSource::test_detect_format PASSED       [ 19%]
tests/test_validator.py::TestDataSource::test_infer_schema PASSED        [ 20%]
tests/test_validator.py::TestDistributionValidator::test_normal_distribution PASSED [ 22%]
tests/test_validator.py::TestSLAValidator::test_min_rows_violation PASSED [ 23%]
tests/test_validator.py::TestSLAValidator::test_max_rows_warn_severity PASSED [ 25%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_valid PASSED [ 26%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_missing_required PASSED [ 28%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_type_mismatch PASSED [ 30%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_warn PASSED [ 31%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_warn PASSED [ 33%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_error PASSED [ 34%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_error PASSED [ 36%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_valid PASSED [ 38%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_nulls PASSED [ 39%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_duplicates PASSED [ 41%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_boundary PASSED [ 42%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_fail PASSED [ 44%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_boundary PASSED [ 46%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_fail PASSED [ 47%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_boundary PASSED [ 49%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_fail PASSED [ 50%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_boundary PASSED [ 52%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_fail PASSED [ 53%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_valid PASSED [ 55%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_warn PASSED [ 57%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_override PASSED [ 58%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_invalid PASSED [ 60%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_invalid_severity_override_format PASSED [ 61%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_valid PASSED [ 63%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_drift PASSED [ 65%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_boundary PASSED [ 66%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_boundary PASSED [ 68%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_boundary PASSED [ 69%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_fail PASSED [ 71%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_fail_warn PASSED [ 73%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_ok PASSED [ 74%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_boundary PASSED [ 76%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_fail PASSED [ 77%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_size_one PASSED [ 79%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_empty PASSED [ 80%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_rows_deterministic PASSED [ 82%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_frac_deterministic PASSED [ 84%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_missing PASSED [ 85%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_invalid_config PASSED [ 87%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_unknown PASSED [ 88%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_override_conflict PASSED [ 90%]
tests/test_exhaustive_features.py::TestReportSinksExhaustive::test_webhook_header_invalid PASSED [ 92%]
tests/test_odcs_contract.py::test_odcs_minimal_mapping PASSED            [ 93%]
tests/test_odcs_contract.py::test_odcs_requires_object_selection_when_multiple PASSED [ 95%]
tests/test_odcs_contract.py::test_odcs_invalid_version_rejected PASSED   [ 96%]
tests/test_odcs_contract.py::test_odcs_quality_sql_custom_warns PASSED   [ 98%]
tests/test_odcs_contract.py::test_odcs_logical_type_timestamp_warns PASSED [100%]

============================== 63 passed in 0.29s ==============================
```

Phase 3 regression gate:

Command:

```
.venv/bin/python -m pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v
```

Output:

```
Note: The tool simplified the command to ` .venv/bin/python -m pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v`, and this is the output of running that command instead:
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Users/meetnishant/Documents/DataContracts/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/meetnishant/Documents/DataContracts
configfile: pyproject.toml
plugins: anyio-4.12.1, cov-7.0.0
collected 63 items

tests/test_validator.py::TestSchemaValidator::test_valid_schema PASSED   [  1%]
tests/test_validator.py::TestSchemaValidator::test_missing_required_field PASSED [  3%]
tests/test_validator.py::TestSchemaValidator::test_extra_columns_error_severity PASSED [  4%]
tests/test_validator.py::TestQualityValidator::test_valid_data PASSED    [  6%]
tests/test_validator.py::TestQualityValidator::test_invalid_email_regex PASSED [  7%]
tests/test_validator.py::TestQualityValidator::test_null_constraint PASSED [  9%]
tests/test_validator.py::TestQualityValidator::test_enum_constraint PASSED [ 11%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_warn PASSED [ 12%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_override PASSED [ 14%]
tests/test_validator.py::TestQualityValidator::test_freshness_max_age_hours PASSED [ 15%]
tests/test_validator.py::TestDataSource::test_load_csv PASSED            [ 17%]
tests/test_validator.py::TestDataSource::test_detect_format PASSED       [ 19%]
tests/test_validator.py::TestDataSource::test_infer_schema PASSED        [ 20%]
tests/test_validator.py::TestDistributionValidator::test_normal_distribution PASSED [ 22%]
tests/test_validator.py::TestSLAValidator::test_min_rows_violation PASSED [ 23%]
tests/test_validator.py::TestSLAValidator::test_max_rows_warn_severity PASSED [ 25%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_valid PASSED [ 26%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_missing_required PASSED [ 28%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_type_mismatch PASSED [ 30%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_warn PASSED [ 31%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_warn PASSED [ 33%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_error PASSED [ 34%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_error PASSED [ 36%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_valid PASSED [ 38%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_nulls PASSED [ 39%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_duplicates PASSED [ 41%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_boundary PASSED [ 42%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_fail PASSED [ 44%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_boundary PASSED [ 46%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_fail PASSED [ 47%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_boundary PASSED [ 49%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_fail PASSED [ 50%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_boundary PASSED [ 52%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_fail PASSED [ 53%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_valid PASSED [ 55%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_warn PASSED [ 57%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_override PASSED [ 58%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_invalid PASSED [ 60%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_invalid_severity_override_format PASSED [ 61%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_valid PASSED [ 63%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_drift PASSED [ 65%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_boundary PASSED [ 66%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_boundary PASSED [ 68%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_boundary PASSED [ 69%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_fail PASSED [ 71%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_fail_warn PASSED [ 73%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_ok PASSED [ 74%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_boundary PASSED [ 76%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_fail PASSED [ 77%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_size_one PASSED [ 79%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_empty PASSED [ 80%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_rows_deterministic PASSED [ 82%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_frac_deterministic PASSED [ 84%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_missing PASSED [ 85%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_invalid_config PASSED [ 87%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_unknown PASSED [ 88%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_override_conflict PASSED [ 90%]
tests/test_exhaustive_features.py::TestReportSinksExhaustive::test_webhook_header_invalid PASSED [ 92%]
tests/test_odcs_contract.py::test_odcs_minimal_mapping PASSED            [ 93%]
tests/test_odcs_contract.py::test_odcs_requires_object_selection_when_multiple PASSED [ 95%]
tests/test_odcs_contract.py::test_odcs_invalid_version_rejected PASSED   [ 96%]
tests/test_odcs_contract.py::test_odcs_quality_sql_custom_warns PASSED   [ 98%]
tests/test_odcs_contract.py::test_odcs_logical_type_timestamp_warns PASSED [100%]

============================== 63 passed in 0.31s ==============================
```

Phase 4 regression gate:

Command:

```
.venv/bin/python -m pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v
```

Output:

```
Note: The tool simplified the command to ` .venv/bin/python -m pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v`, and this is the output of running that command instead:
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Users/meetnishant/Documents/DataContracts/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/meetnishant/Documents/DataContracts
configfile: pyproject.toml
plugins: anyio-4.12.1, cov-7.0.0
collected 63 items

tests/test_validator.py::TestSchemaValidator::test_valid_schema PASSED   [  1%]
tests/test_validator.py::TestSchemaValidator::test_missing_required_field PASSED [  3%]
tests/test_validator.py::TestSchemaValidator::test_extra_columns_error_severity PASSED [  4%]
tests/test_validator.py::TestQualityValidator::test_valid_data PASSED    [  6%]
tests/test_validator.py::TestQualityValidator::test_invalid_email_regex PASSED [  7%]
tests/test_validator.py::TestQualityValidator::test_null_constraint PASSED [  9%]
tests/test_validator.py::TestQualityValidator::test_enum_constraint PASSED [ 11%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_warn PASSED [ 12%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_override PASSED [ 14%]
tests/test_validator.py::TestQualityValidator::test_freshness_max_age_hours PASSED [ 15%]
tests/test_validator.py::TestDataSource::test_load_csv PASSED            [ 17%]
tests/test_validator.py::TestDataSource::test_detect_format PASSED       [ 19%]
tests/test_validator.py::TestDataSource::test_infer_schema PASSED        [ 20%]
tests/test_validator.py::TestDistributionValidator::test_normal_distribution PASSED [ 22%]
tests/test_validator.py::TestSLAValidator::test_min_rows_violation PASSED [ 23%]
tests/test_validator.py::TestSLAValidator::test_max_rows_warn_severity PASSED [ 25%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_valid PASSED [ 26%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_missing_required PASSED [ 28%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_type_mismatch PASSED [ 30%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_warn PASSED [ 31%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_warn PASSED [ 33%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_error PASSED [ 34%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_error PASSED [ 36%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_valid PASSED [ 38%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_nulls PASSED [ 39%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_duplicates PASSED [ 41%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_boundary PASSED [ 42%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_fail PASSED [ 44%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_boundary PASSED [ 46%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_fail PASSED [ 47%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_boundary PASSED [ 49%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_fail PASSED [ 50%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_boundary PASSED [ 52%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_fail PASSED [ 53%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_valid PASSED [ 55%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_warn PASSED [ 57%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_override PASSED [ 58%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_invalid PASSED [ 60%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_invalid_severity_override_format PASSED [ 61%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_valid PASSED [ 63%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_drift PASSED [ 65%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_boundary PASSED [ 66%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_boundary PASSED [ 68%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_boundary PASSED [ 69%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_fail PASSED [ 71%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_fail_warn PASSED [ 73%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_ok PASSED [ 74%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_boundary PASSED [ 76%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_fail PASSED [ 77%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_size_one PASSED [ 79%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_empty PASSED [ 80%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_rows_deterministic PASSED [ 82%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_frac_deterministic PASSED [ 84%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_missing PASSED [ 85%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_invalid_config PASSED [ 87%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_unknown PASSED [ 88%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_override_conflict PASSED [ 90%]
tests/test_exhaustive_features.py::TestReportSinksExhaustive::test_webhook_header_invalid PASSED [ 92%]
tests/test_odcs_contract.py::test_odcs_minimal_mapping PASSED            [ 93%]
tests/test_odcs_contract.py::test_odcs_requires_object_selection_when_multiple PASSED [ 95%]
tests/test_odcs_contract.py::test_odcs_invalid_version_rejected PASSED   [ 96%]
tests/test_odcs_contract.py::test_odcs_quality_sql_custom_warns PASSED   [ 98%]
tests/test_odcs_contract.py::test_odcs_logical_type_timestamp_warns PASSED [100%]

============================== 63 passed in 0.30s ==============================
```

Phase 5 regression gate:

Command:

```
.venv/bin/python -m pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v
```

Output:

```
Note: The tool simplified the command to ` .venv/bin/python -m pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v`, and this is the output of running that command instead:
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Users/meetnishant/Documents/DataContracts/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/meetnishant/Documents/DataContracts
configfile: pyproject.toml
plugins: anyio-4.12.1, cov-7.0.0
collected 63 items

tests/test_validator.py::TestSchemaValidator::test_valid_schema PASSED   [  1%]
tests/test_validator.py::TestSchemaValidator::test_missing_required_field PASSED [  3%]
tests/test_validator.py::TestSchemaValidator::test_extra_columns_error_severity PASSED [  4%]
tests/test_validator.py::TestQualityValidator::test_valid_data PASSED    [  6%]
tests/test_validator.py::TestQualityValidator::test_invalid_email_regex PASSED [  7%]
tests/test_validator.py::TestQualityValidator::test_null_constraint PASSED [  9%]
tests/test_validator.py::TestQualityValidator::test_enum_constraint PASSED [ 11%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_warn PASSED [ 12%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_override PASSED [ 14%]
tests/test_validator.py::TestQualityValidator::test_freshness_max_age_hours PASSED [ 15%]
tests/test_validator.py::TestDataSource::test_load_csv PASSED            [ 17%]
tests/test_validator.py::TestDataSource::test_detect_format PASSED       [ 19%]
tests/test_validator.py::TestDataSource::test_infer_schema PASSED        [ 20%]
tests/test_validator.py::TestDistributionValidator::test_normal_distribution PASSED [ 22%]
tests/test_validator.py::TestSLAValidator::test_min_rows_violation PASSED [ 23%]
tests/test_validator.py::TestSLAValidator::test_max_rows_warn_severity PASSED [ 25%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_valid PASSED [ 26%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_missing_required PASSED [ 28%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_type_mismatch PASSED [ 30%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_warn PASSED [ 31%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_warn PASSED [ 33%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_error PASSED [ 34%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_error PASSED [ 36%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_valid PASSED [ 38%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_nulls PASSED [ 39%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_duplicates PASSED [ 41%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_boundary PASSED [ 42%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_fail PASSED [ 44%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_boundary PASSED [ 46%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_fail PASSED [ 47%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_boundary PASSED [ 49%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_fail PASSED [ 50%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_boundary PASSED [ 52%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_fail PASSED [ 53%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_valid PASSED [ 55%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_warn PASSED [ 57%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_override PASSED [ 58%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_invalid PASSED [ 60%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_invalid_severity_override_format PASSED [ 61%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_valid PASSED [ 63%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_drift PASSED [ 65%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_boundary PASSED [ 66%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_boundary PASSED [ 68%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_boundary PASSED [ 69%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_fail PASSED [ 71%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_fail_warn PASSED [ 73%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_ok PASSED [ 74%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_boundary PASSED [ 76%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_fail PASSED [ 77%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_size_one PASSED [ 79%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_empty PASSED [ 80%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_rows_deterministic PASSED [ 82%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_frac_deterministic PASSED [ 84%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_missing PASSED [ 85%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_invalid_config PASSED [ 87%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_unknown PASSED [ 88%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_override_conflict PASSED [ 90%]
tests/test_exhaustive_features.py::TestReportSinksExhaustive::test_webhook_header_invalid PASSED [ 92%]
tests/test_odcs_contract.py::test_odcs_minimal_mapping PASSED            [ 93%]
tests/test_odcs_contract.py::test_odcs_requires_object_selection_when_multiple PASSED [ 95%]
tests/test_odcs_contract.py::test_odcs_invalid_version_rejected PASSED   [ 96%]
tests/test_odcs_contract.py::test_odcs_quality_sql_custom_warns PASSED   [ 98%]
tests/test_odcs_contract.py::test_odcs_logical_type_timestamp_warns PASSED [100%]

============================== 63 passed in 0.51s ==============================
```

Phase 6 regression gate:

Command:

```
.venv/bin/python -m pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v
```

Output:

```
Note: The tool simplified the command to ` .venv/bin/python -m pytest tests/test_validator.py tests/test_exhaustive_features.py tests/test_odcs_contract.py -v`, and this is the output of running that command instead:
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Users/meetnishant/Documents/DataContracts/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/meetnishant/Documents/DataContracts
configfile: pyproject.toml
plugins: anyio-4.12.1, cov-7.0.0
collected 63 items

tests/test_validator.py::TestSchemaValidator::test_valid_schema PASSED   [  1%]
tests/test_validator.py::TestSchemaValidator::test_missing_required_field PASSED [  3%]
tests/test_validator.py::TestSchemaValidator::test_extra_columns_error_severity PASSED [  4%]
tests/test_validator.py::TestQualityValidator::test_valid_data PASSED    [  6%]
tests/test_validator.py::TestQualityValidator::test_invalid_email_regex PASSED [  7%]
tests/test_validator.py::TestQualityValidator::test_null_constraint PASSED [  9%]
tests/test_validator.py::TestQualityValidator::test_enum_constraint PASSED [ 11%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_warn PASSED [ 12%]
tests/test_validator.py::TestQualityValidator::test_rule_severity_override PASSED [ 14%]
tests/test_validator.py::TestQualityValidator::test_freshness_max_age_hours PASSED [ 15%]
tests/test_validator.py::TestDataSource::test_load_csv PASSED            [ 17%]
tests/test_validator.py::TestDataSource::test_detect_format PASSED       [ 19%]
tests/test_validator.py::TestDataSource::test_infer_schema PASSED        [ 20%]
tests/test_validator.py::TestDistributionValidator::test_normal_distribution PASSED [ 22%]
tests/test_validator.py::TestSLAValidator::test_min_rows_violation PASSED [ 23%]
tests/test_validator.py::TestSLAValidator::test_max_rows_warn_severity PASSED [ 25%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_valid PASSED [ 26%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_missing_required PASSED [ 28%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_type_mismatch PASSED [ 30%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_warn PASSED [ 31%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_warn PASSED [ 33%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_drift_error PASSED [ 34%]
tests/test_exhaustive_features.py::TestSchemaValidationExhaustive::test_schema_extra_columns_error PASSED [ 36%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_valid PASSED [ 38%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_nulls PASSED [ 39%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_duplicates PASSED [ 41%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_boundary PASSED [ 42%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_minmax_fail PASSED [ 44%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_boundary PASSED [ 46%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_enum_fail PASSED [ 47%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_boundary PASSED [ 49%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_regex_fail PASSED [ 50%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_boundary PASSED [ 52%]
tests/test_exhaustive_features.py::TestQualityRulesExhaustive::test_quality_max_null_ratio_fail PASSED [ 53%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_valid PASSED [ 55%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_warn PASSED [ 57%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_override PASSED [ 58%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_rule_severity_invalid PASSED [ 60%]
tests/test_exhaustive_features.py::TestSeverityExhaustive::test_invalid_severity_override_format PASSED [ 61%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_valid PASSED [ 63%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_drift PASSED [ 65%]
tests/test_exhaustive_features.py::TestDistributionExhaustive::test_distribution_boundary PASSED [ 66%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_boundary PASSED [ 68%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_boundary PASSED [ 69%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_min_fail PASSED [ 71%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_sla_max_fail_warn PASSED [ 73%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_ok PASSED [ 74%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_boundary PASSED [ 76%]
tests/test_exhaustive_features.py::TestSLAAndFreshnessExhaustive::test_freshness_fail PASSED [ 77%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_size_one PASSED [ 79%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_chunked_empty PASSED [ 80%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_rows_deterministic PASSED [ 82%]
tests/test_exhaustive_features.py::TestChunkedAndSamplingExhaustive::test_sampling_frac_deterministic PASSED [ 84%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_missing PASSED [ 85%]
tests/test_exhaustive_features.py::TestCustomRulesExhaustive::test_custom_rule_invalid_config PASSED [ 87%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_unknown PASSED [ 88%]
tests/test_exhaustive_features.py::TestPolicyPacksExhaustive::test_policy_pack_override_conflict PASSED [ 90%]
tests/test_exhaustive_features.py::TestReportSinksExhaustive::test_webhook_header_invalid PASSED [ 92%]
tests/test_odcs_contract.py::test_odcs_minimal_mapping PASSED            [ 93%]
tests/test_odcs_contract.py::test_odcs_requires_object_selection_when_multiple PASSED [ 95%]
tests/test_odcs_contract.py::test_odcs_invalid_version_rejected PASSED   [ 96%]
tests/test_odcs_contract.py::test_odcs_quality_sql_custom_warns PASSED   [ 98%]
tests/test_odcs_contract.py::test_odcs_logical_type_timestamp_warns PASSED [100%]

============================== 63 passed in 0.30s ==============================
```
