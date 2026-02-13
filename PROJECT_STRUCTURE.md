DataPact/
├── .github/
│   ├── copilot-instructions.md      # AI coding instructions
│   └── workflows/
│       └── tests.yml                # GitHub Actions CI/CD
├── .gitignore
├── README.md                        # Project overview & usage
├── FEATURES.md                      # Feature list with examples
├── QUICKSTART.md                    # Setup & quick usage
├── CONTRIBUTING.md                  # Developer guide
├── FILE_REFERENCE.md                # File-by-file responsibilities
├── INDEX.md                         # Navigation guide
├── DASHBOARD.md                     # Project overview dashboard
├── SETUP_SUMMARY.md                 # Setup summary
├── DELIVERY_SUMMARY.md              # Delivery summary
├── COMPLETION_CHECKLIST.md          # Feature & QA checklist
├── SEQUENCE_DIAGRAM_GUIDE.md        # Sequence diagram guide
├── VERSIONING_IMPLEMENTATION.md     # Versioning implementation notes
├── pyproject.toml                   # Project metadata & dependencies
├── src/
│   └── datapact/
│       ├── __init__.py              # Package entry point
│       ├── contracts.py             # YAML contract parsing
│       ├── providers/               # Contract providers (datapact, odcs)
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── datapact_provider.py
│       │   └── odcs_provider.py
│       ├── odcs_contracts.py         # ODCS parsing & mapping
│       ├── datasource.py            # Data loading (CSV/Parquet/JSON/DB)
│       ├── policies.py              # Policy pack registry
│       ├── profiling.py             # Contract profiling helpers
│       ├── normalization/           # Normalization scaffolding
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── normalizer.py
│       ├── cli.py                   # CLI: validate, init, profile commands
│       ├── reporting.py             # Report generation
│       └── validators/
│           ├── __init__.py
│           ├── schema_validator.py      # Column/type/required checks
│           ├── quality_validator.py     # Null/unique/range/regex/enum
│           ├── sla_validator.py         # SLA row count checks
│           ├── custom_rule_validator.py # Custom plugin rules
│           └── distribution_validator.py # Mean/std drift detection
├── tests/
│   ├── test_validator.py            # Core validator tests
│   ├── test_versioning.py           # Versioning tests
│   ├── test_banking_finance.py      # Banking/finance scenarios
│   ├── test_concurrency.py          # Concurrency validation
│   ├── test_concurrency_mp.py       # Multiprocessing concurrency
│   ├── test_chunked_validation.py   # Chunked validation and sampling
│   ├── test_custom_rules.py         # Custom rule plugin tests
│   ├── test_profiling.py            # Profiling tests
│   ├── test_reporting.py            # Report sink tests
│   ├── test_policy_packs.py         # Policy pack tests
│   ├── test_exhaustive_features.py  # Exhaustive feature tests
│   ├── test_db_source.py            # Database source tests
│   ├── test_odcs_contract.py         # ODCS contract tests
│   ├── test_contract_providers.py   # Provider dispatch tests
│   ├── test_flatten_normalization.py # Normalization scaffold tests
│   ├── plugins/
│   │   └── sample_plugin.py          # Custom rule plugin example
│   └── fixtures/
│       ├── customer_contract.yaml   # Example contract
│       ├── customer_contract_v1.yaml # Legacy contract
│       ├── customer_contract_v2.yaml # Current contract
│       ├── valid_customers.csv      # Valid test data
│       ├── invalid_customers.csv    # Invalid test data
│       ├── deposits_contract.yaml   # Deposits contract
│       ├── lending_contract.yaml    # Lending contract
│       ├── deposits_data.csv        # Deposits data
│       ├── lending_data.csv         # Lending data
│       ├── deposits_accounts_agg_contract.yaml # Aggregate deposits contract
│       ├── lending_loans_agg_contract.yaml    # Aggregate lending contract
│       ├── deposits_transactions_contract.yaml # Deposits transactions contract
│       ├── lending_payments_contract.yaml      # Lending payments contract
│       ├── deposits_transactions.csv           # Deposits transactions data
│       ├── lending_payments.csv                # Lending payments data
│       ├── deposits_accounts_agg.csv           # Aggregate deposits data
│       ├── lending_loans_agg.csv               # Aggregate lending data
│       ├── policy_pack_contract.yaml           # Policy pack contract
│       ├── odcs_minimal.yaml                   # ODCS contract fixture
│       ├── odcs_multi_object.yaml             # ODCS multi-object fixture
│       ├── odcs_invalid_version.yaml          # ODCS invalid version fixture
│       ├── odcs_quality_sql_custom.yaml       # ODCS quality rule fixture
│       ├── odcs_logical_type_timestamp.yaml   # ODCS logical type fixture
│       └── schema_*/quality_*/sla_*/distribution_* # Exhaustive fixtures
└── docs/
    ├── ARCHITECTURE.md              # Design decisions & data flow
    ├── sequenceDiagram.mmd          # Mermaid sequence diagram
    ├── VERSIONING.md                # Versioning guide
    └── AI_INSTRUCTIONS_GUIDE.md     # Guide for writing AI instructions
