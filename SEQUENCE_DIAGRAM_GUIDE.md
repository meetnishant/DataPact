# Sequence Diagram Documentation - Added

This guide covers the DataPact validation sequence diagrams.

## ✅ What Was Added

Two comprehensive Mermaid sequence diagrams have been added to the documentation showing the complete validation flow.

## 📍 Locations

### 1. **DASHBOARD.md**
- **Section**: "Sequence Diagram: Validation Flow"
- **Purpose**: Visual overview for project managers and stakeholders
- **Location**: After "Architecture Overview" section

### 2. **docs/ARCHITECTURE.md**
- **Section**: "Validation Sequence Diagram"
- **Purpose**: Detailed technical reference for developers
- **Location**: Before "Error Aggregation" section

## 📊 Diagram Details

### What the Sequence Diagram Shows

```
User/CLI Request
    ↓
1. CLI Interface (receives command)
    ↓
2. Contract Parser (parses YAML)
    ↓
3. Data Loader (loads CSV/Parquet/JSON)
    ↓
4. VALIDATION PIPELINE (5 sequential validators):
    • Schema Validator (columns, types, required fields)
    • Quality Validator (nulls, unique, ranges, regex, enum)
    • SLA Validator (row count thresholds)
    • Custom Rule Validator (plugin-defined rules)
    • Distribution Validator (mean, std, drift)
    ↓
5. Report Generator (aggregates results)
    ↓
6. Output Generator (JSON + console + report sinks)
    ↓
Exit Code (0 or 1)
```

### Features

✅ **Autonumbered steps** (1-11) for easy reference  
✅ **All 9 components** shown with proper activation  
✅ **Validation pipeline highlighted** in colored box  
✅ **Message flow** clearly labeled with parameters  
✅ **Return values** shown for each component  
✅ **Error handling** included (errors, warnings, OK status)  
✅ **Rule severity** (WARN/ERROR) reflected in quality validation  
✅ **SLA validator** shown as part of the pipeline  
✅ **Profiling command** documented outside the validate flow  
✅ **Chunked validation** supported via CLI options for large files  
✅ **Custom rule plugins** supported via CLI module loading  
✅ **Report sinks** supported for file, stdout, or webhook output  
✅ **Policy packs** applied during contract parsing  
✅ **Database sources** supported for Postgres, MySQL, and SQLite  
✅ **ODCS compatibility** supported via `--contract-format odcs`  
✅ **Report generation** and output demonstrated  
✅ **Exit code** shown at the end  

## 🎯 How to View

### In VS Code
1. Open `DASHBOARD.md` or `docs/ARCHITECTURE.md`
2. Preview the file (Cmd+Shift+V)
3. Scroll to the sequence diagram section
4. The Mermaid diagram renders automatically

### Key Insights from the Diagram

1. **Sequential Processing**: Each component processes and passes results to the next
2. **Non-Blocking Nature**: Quality and Distribution validators continue even on errors
3. **Report Aggregation**: All findings are collected before reporting
4. **Deterministic Output**: Always produces JSON report + console summary

## 📚 Reference

- **Mermaid Diagram Type**: `sequenceDiagram`
- **Syntax**: Follows Mermaid sequence diagram standard
- **Auto-rendering**: Supported in GitHub, GitLab, VS Code, and Markdown viewers

## Quick Reference: Which Doc to Read

| If you want to... | Read this section |
|-------------------|-------------------|
| Quick visual overview | [DASHBOARD.md → Sequence Diagram: Validation Flow](DASHBOARD.md#sequence-diagram-validation-flow) |
| Technical details | [docs/ARCHITECTURE.md → Validation Sequence Diagram](docs/ARCHITECTURE.md#validation-sequence-diagram) |
| Full architecture | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Component details | [FILE_REFERENCE.md](FILE_REFERENCE.md) |

---

**Added**: February 8, 2026  
**Format**: Mermaid Sequence Diagrams  
**Status**: ✅ Complete and validated
