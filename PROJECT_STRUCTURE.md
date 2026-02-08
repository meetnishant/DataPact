data-contract-validator/
├── .github/
│   ├── copilot-instructions.md      # AI coding instructions
│   └── workflows/
│       └── tests.yml                # GitHub Actions CI/CD
├── .gitignore
├── README.md                        # Project overview & usage
├── CONTRIBUTING.md                  # Developer guide
├── pyproject.toml                   # Project metadata & dependencies
├── src/
│   └── data_contract_validator/
│       ├── __init__.py              # Package entry point
│       ├── contracts.py             # YAML contract parsing
│       ├── datasource.py            # Data loading (CSV/Parquet/JSON)
│       ├── cli.py                   # CLI: validate, init commands
│       ├── reporting.py             # Report generation
│       └── validators/
│           ├── __init__.py
│           ├── schema_validator.py      # Column/type/required checks
│           ├── quality_validator.py     # Null/unique/range/regex/enum
│           └── distribution_validator.py # Mean/std drift detection
├── tests/
│   ├── test_validator.py            # Pytest test suite
│   └── fixtures/
│       ├── customer_contract.yaml   # Example contract
│       ├── valid_customers.csv      # Valid test data
│       └── invalid_customers.csv    # Invalid test data
└── docs/
    ├── ARCHITECTURE.md              # Design decisions & data flow
    └── AI_INSTRUCTIONS_GUIDE.md     # Guide for writing AI instructions
