DataPact/
├── .github/
│   ├── copilot-instructions.md      # AI coding instructions
│   └── workflows/
│       └── tests.yml                # GitHub Actions CI/CD
├── .gitignore
├── README.md                        # Project overview & usage
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
│       ├── datasource.py            # Data loading (CSV/Parquet/JSON)
│       ├── profiling.py             # Contract profiling helpers
│       ├── cli.py                   # CLI: validate, init, profile commands
│       ├── reporting.py             # Report generation
│       └── validators/
│           ├── __init__.py
│           ├── schema_validator.py      # Column/type/required checks
│           ├── quality_validator.py     # Null/unique/range/regex/enum
│           └── distribution_validator.py # Mean/std drift detection
├── tests/
│   ├── test_validator.py            # Core validator tests
│   ├── test_versioning.py           # Versioning tests
│   ├── test_banking_finance.py      # Banking/finance scenarios
│   ├── test_concurrency.py          # Concurrency validation
│   ├── test_concurrency_mp.py       # Multiprocessing concurrency
│   ├── test_profiling.py            # Profiling tests
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
│       └── lending_loans_agg.csv               # Aggregate lending data
└── docs/
    ├── ARCHITECTURE.md              # Design decisions & data flow
    ├── VERSIONING.md                # Versioning guide
    └── AI_INSTRUCTIONS_GUIDE.md     # Guide for writing AI instructions
