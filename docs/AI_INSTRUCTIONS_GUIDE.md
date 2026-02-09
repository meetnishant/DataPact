# Guide to Writing AI-Friendly Instructions

Use this guide to craft AI instructions for DataPact and similar projects.

Use this template for your `.github/copilot-instructions.md` and other AI instruction files.

## Core Principles

1. **Be specific** - Reference actual code files and patterns from your codebase
2. **Explain the why** - Document design decisions and architectural patterns
3. **Show examples** - Use real examples from fixtures or test cases
4. **Cover workflows** - Include build, test, and debug commands
5. **List conventions** - Document project-specific naming and structure patterns
6. **Describe integrations** - Explain how components communicate

## Structure

Organize instructions as:
- Big picture architecture (read multiple files to understand)
- Critical workflows (build, test, debug, deploy)
- Project conventions (naming, patterns, structure)
- Integration points (how components talk)
- External dependencies (what systems it connects to)

## DataPact Feature Notes

- Include **profiling** (`datapact profile`) and `profile_dataframe()` in workflows.
- Document **rule severity** metadata (WARN/ERROR) and CLI overrides.
- Document **schema drift** policy (`schema.extra_columns.severity`).
- Document **SLA checks** (`sla.min_rows`, `sla.max_rows`, and freshness rules).
- Document **chunked validation** options (`--chunksize`, `--sample-rows`, `--sample-frac`).
