# 📚 Complete Index & Navigation Guide

Welcome to the **DataPact** repository! This file helps you navigate all resources.

## 🎯 Start Here

### For Quick Setup
→ [QUICKSTART.md](QUICKSTART.md) - 5-minute setup guide

### For AI Agents (Copilot, Claude, etc.)
→ [.github/copilot-instructions.md](.github/copilot-instructions.md) - Comprehensive AI coding guide

### For End Users
→ [README.md](README.md) - Features, usage, examples

### For Developers
→ [CONTRIBUTING.md](CONTRIBUTING.md) - Development workflow and contribution guidelines

## 📖 Documentation Structure

### Getting Started
- [QUICKSTART.md](QUICKSTART.md) - Installation, running CLI, running tests
- [README.md](README.md) - Full user guide with contract format and examples
- [SETUP_SUMMARY.md](SETUP_SUMMARY.md) - What was created and project overview

### For Development
- [CONTRIBUTING.md](CONTRIBUTING.md) - Developer setup and workflow
- [DEPENDENCIES.md](DEPENDENCIES.md) - Direct dependencies and tooling
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Design decisions and data flow
- [docs/VERSIONING.md](docs/VERSIONING.md) - Contract versioning and migration guide
- [FILE_REFERENCE.md](FILE_REFERENCE.md) - Detailed file-by-file guide
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Visual directory tree

### For AI Agents & Code Assistants
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Complete AI coding guide
- [docs/AI_INSTRUCTIONS_GUIDE.md](docs/AI_INSTRUCTIONS_GUIDE.md) - Template for AI instructions

## 🏗️ Project Structure

```
src/datapact/          Core application
├── contracts.py                       YAML parsing & models
├── datasource.py                      Data loading (CSV/Parquet/JSON)
├── profiling.py                       Contract profiling helpers
├── cli.py                             Command-line interface
├── reporting.py                       Report generation
├── versioning.py                      Contract version management
└── validators/
    ├── schema_validator.py            Structure validation
    ├── quality_validator.py           Content validation
    ├── sla_validator.py               SLA validation
    └── distribution_validator.py      Statistical monitoring

tests/                                 Test suite & fixtures
├── test_validator.py                  Unit tests
├── test_versioning.py                 Version feature tests
├── test_banking_finance.py            Banking/finance scenarios
├── test_concurrency.py                Concurrency validation
├── test_concurrency_mp.py             Multiprocessing concurrency
├── test_chunked_validation.py         Chunked validation tests
├── test_profiling.py                  Profiling tests
└── fixtures/                          Example data & contracts

.github/                               GitHub-specific files
├── copilot-instructions.md            AI coding guide
└── workflows/tests.yml                CI/CD pipeline
```

Full tree: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 🚀 Common Tasks

### I want to...

#### Use the tool
1. Read [QUICKSTART.md](QUICKSTART.md) for setup
2. See examples in [README.md](README.md#quick-start)
3. Check [tests/fixtures/customer_contract.yaml](tests/fixtures/customer_contract.yaml) for contract format

#### Understand the architecture
1. Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for design overview
2. Check [FILE_REFERENCE.md](FILE_REFERENCE.md) for file-by-file guide
3. Review [.github/copilot-instructions.md](.github/copilot-instructions.md) for big picture
4. See [docs/VERSIONING.md](docs/VERSIONING.md) for version management details

#### Work with contract versions
1. Read [docs/VERSIONING.md](docs/VERSIONING.md) for version history and migration guide
2. Check examples in [tests/fixtures/customer_contract_v1.yaml](tests/fixtures/customer_contract_v1.yaml) and [tests/fixtures/customer_contract_v2.yaml](tests/fixtures/customer_contract_v2.yaml)
3. Run versioning tests: `pytest tests/test_versioning.py -v`

#### Add a new feature
1. Read [CONTRIBUTING.md](CONTRIBUTING.md#adding-a-new-validator)
2. Check [FILE_REFERENCE.md](FILE_REFERENCE.md#adding-a-new-feature)
3. Look at existing validator in [src/datapact/validators/](src/datapact/validators/)

#### Write a validation rule
1. See examples in [tests/fixtures/customer_contract.yaml](tests/fixtures/customer_contract.yaml)
2. Read [README.md#validation-rules](README.md#validation-rules) for all rule types
3. Check [tests/test_validator.py](tests/test_validator.py) for test examples

#### Run tests
1. Follow [QUICKSTART.md#running-tests](QUICKSTART.md#running-tests)
2. See test structure in [tests/test_validator.py](tests/test_validator.py)

#### Get AI assistance
1. Share [.github/copilot-instructions.md](.github/copilot-instructions.md) with your AI agent
2. Reference specific files from [FILE_REFERENCE.md](FILE_REFERENCE.md)

## 📋 File Legend

| Audience | Purpose | Files |
|----------|---------|-------|
| **End Users** | How to use the tool | README.md, QUICKSTART.md |
| **Developers** | How to develop features | CONTRIBUTING.md, ARCHITECTURE.md, FILE_REFERENCE.md |
| **AI Agents** | How to code in this project | copilot-instructions.md, ARCHITECTURE.md |
| **Project Leads** | Project overview & structure | SETUP_SUMMARY.md, PROJECT_STRUCTURE.md |

## 🔑 Key Concepts

- **Contract** - YAML file defining validation rules for a dataset
- **Contract Version** - Semantic version (1.0.0, 1.1.0, 2.0.0) with migration support
- **Validator** - Python class that checks one aspect (schema, quality, or distribution)
- **ErrorRecord** - Individual validation finding with severity (ERROR or WARN)
- **ValidationReport** - Complete validation result (JSON + console summary)
- **Exit Code** - Non-zero if ERRORs present (for CI/CD integration)
- **Auto-Migration** - Automatic upgrade of old contracts to latest version
- **Profiling** - Auto-generate rule baselines from data
- **Rule Severity** - WARN/ERROR per rule with CLI overrides
- **Schema Drift** - Control extra columns via WARN/ERROR policy
- **SLA Checks** - Enforce row count and freshness constraints
- **Chunked Validation** - Stream large files with optional sampling

## ✨ Project Statistics

- **12** Python source files (~1000+ lines including SLA and profiling)
- **17** Documentation files
- **17** Test fixture files
- **59** Test cases (19 core + 17 versioning + 19 banking/finance + 2 concurrency + 2 profiling)
- **1** GitHub Actions workflow
- **100%** Type hints in core modules
- **66%+** Code coverage achieved

## 🔗 Cross-References

### Architecture
- [Contract parsing flow](docs/ARCHITECTURE.md#high-level-design)
- [Validation pipeline](docs/ARCHITECTURE.md#key-components)
- [Error aggregation](docs/ARCHITECTURE.md#error-aggregation)
- [Version management](docs/VERSIONING.md#contract-versioning)

### Implementation
- [Validator interface](FILE_REFERENCE.md#core-application-files)
- [Version registry](docs/VERSIONING.md#version-registry)
- [Migration engine](docs/VERSIONING.md#migration-paths)
- [Type mapping](README.md#supported-data-types)
- [Error message format](.github/copilot-instructions.md#error-messages)

### Testing
- [Test fixtures](tests/fixtures/)
- [Versioning tests](tests/test_versioning.py)
- [Test examples](tests/test_validator.py)
- [Running tests](QUICKSTART.md#running-tests)

## 📞 Support & Questions

- **Setup issues?** → Check [QUICKSTART.md](QUICKSTART.md#common-issues)
- **Architecture questions?** → Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Development questions?** → See [CONTRIBUTING.md](CONTRIBUTING.md)
- **File-specific questions?** → Check [FILE_REFERENCE.md](FILE_REFERENCE.md)
- **AI-assisted development?** → Use [.github/copilot-instructions.md](.github/copilot-instructions.md)

---

**Last Updated**: February 8, 2026  
**Project Version**: 0.2.0  
**Status**: ✅ Ready for development
