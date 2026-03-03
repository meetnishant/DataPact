"""
PII (Personally Identifiable Information) detection validator.

Performs two complementary checks:
  1. Contract-declared PII: validates fields tagged with `pii:` in YAML.
  2. Auto-detection: scans all DataFrame columns using name heuristics
     and regex pattern matching on a value sample.

Auto-detection fires for columns NOT already declared as PII in the contract.
Auto-detection can be disabled with `pii_scan: false` at the contract level.
"""

import re
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

from datapact.contracts import Contract, Field, PIIConfig


# ---------------------------------------------------------------------------
# PII value-pattern catalogue
# Each entry: (category_name, compiled_regex)
# ---------------------------------------------------------------------------
_VALUE_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("email",       re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")),
    ("ssn",         re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("credit_card", re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b")),
    ("phone",       re.compile(r"(?:\+?\d[\s.\-]?){7,15}")),
    ("ip_address",  re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")),
]

# ---------------------------------------------------------------------------
# Column-name keyword heuristics
# Map of keyword -> PII category. Keywords are lower-cased substring matches.
# ---------------------------------------------------------------------------
_NAME_KEYWORDS: Dict[str, str] = {
    "email":           "email",
    "mail":            "email",
    "phone":           "phone",
    "mobile":          "phone",
    "cell":            "phone",
    "ssn":             "ssn",
    "social_security": "ssn",
    "passport":        "ssn",
    "national_id":     "ssn",
    "tax_id":          "ssn",
    "nin":             "ssn",
    "credit_card":     "credit_card",
    "card_number":     "credit_card",
    "cardnum":         "credit_card",
    "name":            "name",
    "firstname":       "name",
    "lastname":        "name",
    "fullname":        "name",
    "address":         "address",
    "street":          "address",
    "zip":             "address",
    "postal":          "address",
    "dob":             "dob",
    "date_of_birth":   "dob",
    "birthdate":       "dob",
    "ip":              "ip_address",
    "ipaddr":          "ip_address",
}

# Default sample size for auto-detection value scanning
_DEFAULT_SAMPLE_SIZE = 500

# Minimum fraction of non-null sampled values that must match a pattern
# before auto-detection flags the column.
_MATCH_THRESHOLD = 0.20


class PIIValidator:
    """
    Validate PII compliance declared in the contract and auto-detect
    undeclared PII columns.

    Pass 1 (declared): emits a notice for every field tagged with `pii:` in
    the contract that is not marked `masked: true`.

    Pass 2 (auto-detect): scans all other columns using column-name keywords
    and regex value-pattern matching; always emits WARN, never ERROR.
    Pass 2 runs only when `contract.pii_scan` is True (the default).
    """

    def __init__(
        self,
        contract: Contract,
        df: pd.DataFrame,
        sample_size: int = _DEFAULT_SAMPLE_SIZE,
        severity_overrides: Optional[dict] = None,
    ) -> None:
        self.contract = contract
        self.df = df
        self.sample_size = sample_size
        self.errors: List[str] = []

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Run both declared-PII and auto-detection checks.
        Returns (no_errors, messages).
        passed=False only when at least one ERROR-level message exists.
        """
        self.errors = []
        declared_cols: Set[str] = set()

        # Pass 1: contract-declared PII fields
        for contract_field in self.contract.fields:
            if contract_field.pii is not None:
                col = self.contract.resolve_column_name(contract_field.name)
                declared_cols.add(col)
                self._check_declared_pii(contract_field, col)

        # Pass 2: auto-detection on undeclared columns
        if self.contract.pii_scan:
            for col in self.df.columns:
                if col not in declared_cols:
                    self._auto_detect_column(col)

        has_errors = any(e.startswith("ERROR") for e in self.errors)
        return not has_errors, self.errors

    # ------------------------------------------------------------------
    # Pass 1 helpers
    # ------------------------------------------------------------------

    def _check_declared_pii(self, contract_field: Field, col: str) -> None:
        """
        Emit a notice for a field explicitly tagged as PII in the contract.
        Silently skips if the column is absent (schema validator covers that)
        or if masked=True.
        """
        pii_cfg: PIIConfig = contract_field.pii  # type: ignore[assignment]
        if col not in self.df.columns or pii_cfg.masked:
            return
        category_label = pii_cfg.category or "pii"
        self.errors.append(
            f"{pii_cfg.severity}: Field '{contract_field.name}' is declared as PII "
            f"(category={category_label}) and contains unmasked data"
        )

    # ------------------------------------------------------------------
    # Pass 2 helpers
    # ------------------------------------------------------------------

    def _auto_detect_column(self, col: str) -> None:
        """
        Scan a single undeclared column for PII signals.
        Checks name heuristic first (fast), then value patterns on a sample.
        Emits at most one WARN per column.
        """
        detected = self._detect_by_name(col)
        if detected:
            self.errors.append(
                f"WARN: Column '{col}' appears to contain PII "
                f"(category={detected}, detected by column name) "
                f"but is not declared in the contract"
            )
            return

        detected = self._detect_by_values(col)
        if detected:
            self.errors.append(
                f"WARN: Column '{col}' appears to contain PII "
                f"(category={detected}, detected by value pattern) "
                f"but is not declared in the contract"
            )

    def _detect_by_name(self, col: str) -> Optional[str]:
        """Check column name against keyword dictionary. Returns category or None."""
        lower = col.lower().replace("-", "_").replace(" ", "_")
        for keyword, category in _NAME_KEYWORDS.items():
            if keyword in lower:
                return category
        return None

    def _detect_by_values(self, col: str) -> Optional[str]:
        """
        Sample up to self.sample_size non-null values and test PII regexes.
        Returns the first matched category at or above _MATCH_THRESHOLD, or None.
        """
        non_null = self.df[col].dropna()
        if len(non_null) == 0:
            return None
        n = min(self.sample_size, len(non_null))
        sample = non_null.sample(n=n, random_state=42).astype(str)
        total = len(sample)
        for category, pattern in _VALUE_PATTERNS:
            match_count = sample.str.contains(pattern, regex=True, na=False).sum()
            if total > 0 and (match_count / total) >= _MATCH_THRESHOLD:
                return category
        return None
