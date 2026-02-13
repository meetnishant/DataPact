"""
Profiling utilities for generating contract rules from data.
"""

from typing import Any, Dict, List
import re

import pandas as pd

from datapact.versioning import LATEST_VERSION

_DATE_REGEX = r"^\d{4}-\d{2}-\d{2}$"


def profile_dataframe(
    df: pd.DataFrame,
    dataset_name: str,
    contract_name: str = "profiled_contract",
    version: str = LATEST_VERSION,
    max_enum_size: int = 20,
    max_enum_ratio: float = 0.2,
    unique_threshold: float = 0.99,
    null_ratio_buffer: float = 0.01,
    range_buffer_pct: float = 0.05,
    include_distribution: bool = True,
    max_drift_pct: float = 10.0,
    max_z_score: float = 3.0,
    infer_date_regex: bool = True,
) -> Dict[str, Any]:
    """
    Generate a contract dictionary by profiling a DataFrame.
    """
    fields: List[Dict[str, Any]] = []

    for column_name in df.columns:
        series = df[column_name]
        col_type = _infer_contract_type(str(series.dtype))
        total = len(series)
        null_count = series.isna().sum()
        non_null = series.dropna()

        field: Dict[str, Any] = {
            "name": column_name,
            "type": col_type,
            "required": False,
        }
        rules: Dict[str, Any] = {}

        if total > 0 and null_count == 0:
            field["required"] = True
            rules["not_null"] = True

        if total > 0 and null_count > 0:
            null_ratio = null_count / total
            rules["max_null_ratio"] = min(1.0, round(null_ratio + null_ratio_buffer, 4))

        if total > 0 and len(non_null) > 0:
            unique_ratio = non_null.nunique() / len(non_null)
            if unique_ratio >= unique_threshold and _looks_like_identifier(column_name):
                rules["unique"] = True

        if col_type == "string" and infer_date_regex:
            if len(non_null) > 0:
                as_str = non_null.astype(str).str.strip()
                if as_str.str.fullmatch(_DATE_REGEX).all():
                    rules["regex"] = _DATE_REGEX

        if col_type == "string":
            unique_values = list(pd.unique(non_null.astype(str)))
            unique_count = len(unique_values)
            if len(non_null) > 0 and unique_count <= max_enum_size:
                ratio = unique_count / len(non_null)
                if ratio <= max_enum_ratio:
                    rules["enum"] = sorted(unique_values)

        if col_type in ("integer", "float") and len(non_null) > 0:
            numeric = pd.to_numeric(non_null, errors="coerce").dropna()
            if len(numeric) > 0:
                min_val = numeric.min()
                max_val = numeric.max()
                min_buffer = abs(min_val) * range_buffer_pct
                max_buffer = abs(max_val) * range_buffer_pct
                rules["min"] = float(min_val - min_buffer)
                rules["max"] = float(max_val + max_buffer)

        if rules:
            field["rules"] = rules

        if include_distribution and col_type in ("integer", "float"):
            numeric = pd.to_numeric(non_null, errors="coerce").dropna()
            if len(numeric) > 0:
                field["distribution"] = {
                    "mean": float(numeric.mean()),
                    "std": float(numeric.std()),
                    "max_drift_pct": max_drift_pct,
                    "max_z_score": max_z_score,
                }

        fields.append(field)

    return {
        "contract": {
            "name": contract_name,
            "version": version,
        },
        "dataset": {
            "name": dataset_name,
        },
        "fields": fields,
    }


def _infer_contract_type(dtype: str) -> str:
    if dtype.startswith("int"):
        return "integer"
    if dtype.startswith("float"):
        return "float"
    if dtype == "object" or dtype.startswith("string"):
        return "string"
    if dtype == "bool":
        return "boolean"
    return "string"


def _looks_like_identifier(column_name: str) -> bool:
    return re.search(r"(^|_)id$", column_name.strip().lower()) is not None
