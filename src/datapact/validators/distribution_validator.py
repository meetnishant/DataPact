"""
Distribution validation - drift detection for numeric columns.
Checks for mean/std drift and outliers using contract distribution rules.
"""

from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from datapact.contracts import Contract, Field, DistributionRule


class DistributionValidator:
    """
    Validate data distributions against drift thresholds and outlier rules.
    Produces warnings for drift or outlier violations (never errors).
    """

    def __init__(self, contract: Contract, df: pd.DataFrame):
        self.contract = contract
        self.df = df
        self.warnings: List[str] = []

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate distributions for all fields with distribution rules.
        Returns (is_valid, warning_messages).
        """
        self.warnings = []

        for field in self.contract.fields:
            col_name = self.contract.resolve_column_name(field.name)
            if col_name not in self.df.columns:
                continue

            if not field.distribution:
                continue

            column = self.df[col_name].dropna()
            if len(column) == 0:
                continue

            self._check_distribution(field, column)

        return len(self.warnings) == 0, self.warnings

    def _check_distribution(self, field: Field, column: pd.Series) -> None:
        """
        Check drift and outlier rules for a numeric column.
        Appends warnings to self.warnings if thresholds are exceeded.
        """
        dist = field.distribution
        if not dist:
            return

        # Convert to numeric, skip non-numeric columns
        try:
            numeric_col = pd.to_numeric(column)
        except (ValueError, TypeError):
            return

        current_mean = numeric_col.mean()
        current_std = numeric_col.std()

        # Check mean drift
        if dist.mean is not None and dist.max_drift_pct is not None:
            if dist.mean != 0:
                drift_pct = abs(current_mean - dist.mean) / abs(dist.mean) * 100
            elif current_mean != 0:
                # Baseline is zero but current is non-zero: always flag as drifted
                drift_pct = 100.0
            else:
                drift_pct = 0.0
            if drift_pct > dist.max_drift_pct:
                self.warnings.append(
                    f"WARN: Field '{field.name}' mean drift {drift_pct:.2f}% "
                    f"exceeds threshold {dist.max_drift_pct}%"
                )

        # Check std drift
        if dist.std is not None and dist.max_drift_pct is not None:
            if dist.std != 0:
                drift_pct = abs(current_std - dist.std) / abs(dist.std) * 100
            elif current_std != 0:
                # Baseline is zero but current is non-zero: always flag as drifted
                drift_pct = 100.0
            else:
                drift_pct = 0.0
            if drift_pct > dist.max_drift_pct:
                self.warnings.append(
                    f"WARN: Field '{field.name}' std drift {drift_pct:.2f}% "
                    f"exceeds threshold {dist.max_drift_pct}%"
                )

        # Check z-score (simple outlier detection)
        if dist.max_z_score is not None:
            if current_std > 0:
                z_scores = np.abs((numeric_col - current_mean) / current_std)
                outlier_count = (z_scores > dist.max_z_score).sum()
                if outlier_count > 0:
                    self.warnings.append(
                        f"WARN: Field '{field.name}' has {outlier_count} outliers "
                        f"(z-score > {dist.max_z_score})"
                    )


class DistributionAccumulator:
    """
    Accumulate distribution stats across chunks for drift detection.
    """

    def __init__(self, contract: Contract):
        self.contract = contract
        self.stats: Dict[str, dict] = {}
        self.rules: Dict[str, DistributionRule] = {}
        self.column_map: Dict[str, str] = {}

        for field in contract.fields:
            if field.distribution:
                self.rules[field.name] = field.distribution
                self.column_map[field.name] = contract.resolve_column_name(field.name)
                self.stats[field.name] = {
                    "count": 0,
                    "mean": 0.0,
                    "m2": 0.0,
                }

    def process_chunk(self, df: pd.DataFrame) -> None:
        for field_name, dist in self.rules.items():
            col_name = self.column_map.get(field_name, field_name)
            if col_name not in df.columns:
                continue

            column = df[col_name].dropna()
            if len(column) == 0:
                continue

            try:
                numeric_col = pd.to_numeric(column)
            except (ValueError, TypeError):
                continue

            stats = self.stats[field_name]
            # Parallel (Chan's) algorithm for combining mean and M2 across chunks
            chunk_count = len(numeric_col)
            chunk_mean = float(numeric_col.mean())
            chunk_m2 = float(numeric_col.var(ddof=0)) * chunk_count

            prev_count = stats["count"]
            new_count = prev_count + chunk_count
            delta = chunk_mean - stats["mean"]
            stats["mean"] += delta * chunk_count / new_count
            stats["m2"] += chunk_m2 + delta ** 2 * prev_count * chunk_count / new_count
            stats["count"] = new_count

    def finalize_drift(self) -> List[str]:
        warnings: List[str] = []
        for field_name, dist in self.rules.items():
            stats = self.stats[field_name]
            count = stats["count"]
            if count == 0:
                continue

            current_mean = stats["mean"]
            current_std = (stats["m2"] / count) ** 0.5 if count > 0 else 0.0

            if dist.mean is not None and dist.max_drift_pct is not None:
                if dist.mean != 0:
                    drift_pct = abs(current_mean - dist.mean) / abs(dist.mean) * 100
                elif current_mean != 0:
                    drift_pct = 100.0
                else:
                    drift_pct = 0.0
                if drift_pct > dist.max_drift_pct:
                    warnings.append(
                        f"WARN: Field '{field_name}' mean drift {drift_pct:.2f}% "
                        f"exceeds threshold {dist.max_drift_pct}%"
                    )

            if dist.std is not None and dist.max_drift_pct is not None:
                if dist.std != 0:
                    drift_pct = abs(current_std - dist.std) / abs(dist.std) * 100
                elif current_std != 0:
                    drift_pct = 100.0
                else:
                    drift_pct = 0.0
                if drift_pct > dist.max_drift_pct:
                    warnings.append(
                        f"WARN: Field '{field_name}' std drift {drift_pct:.2f}% "
                        f"exceeds threshold {dist.max_drift_pct}%"
                    )

        return warnings

    def needs_outlier_pass(self) -> bool:
        return any(dist.max_z_score is not None for dist in self.rules.values())

    def count_outliers(self, df_iter) -> List[str]:
        warnings: List[str] = []
        for field_name, dist in self.rules.items():
            if dist.max_z_score is None:
                continue

            stats = self.stats[field_name]
            count = stats["count"]
            if count == 0:
                continue

            mean = stats["mean"]
            std = (stats["m2"] / count) ** 0.5 if count > 0 else 0.0
            if std <= 0:
                continue

            outliers = 0
            for chunk in df_iter:
                col_name = self.column_map.get(field_name, field_name)
                if col_name not in chunk.columns:
                    continue
                column = chunk[col_name].dropna()
                if len(column) == 0:
                    continue
                try:
                    numeric_col = pd.to_numeric(column)
                except (ValueError, TypeError):
                    continue
                z_scores = np.abs((numeric_col - mean) / std)
                outliers += (z_scores > dist.max_z_score).sum()

            if outliers > 0:
                warnings.append(
                    f"WARN: Field '{field_name}' has {outliers} outliers "
                    f"(z-score > {dist.max_z_score})"
                )

        return warnings
