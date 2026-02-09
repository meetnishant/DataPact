"""
Distribution validation - drift detection for numeric columns.
Checks for mean/std drift and outliers using contract distribution rules.
"""

from typing import List, Tuple
import pandas as pd
import numpy as np
from datapact.contracts import Contract, Field


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
            if field.name not in self.df.columns:
                continue

            if not field.distribution:
                continue

            column = self.df[field.name].dropna()
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
            else:
                drift_pct = 0
            if drift_pct > dist.max_drift_pct:
                self.warnings.append(
                    f"WARN: Field '{field.name}' mean drift {drift_pct:.2f}% "
                    f"exceeds threshold {dist.max_drift_pct}%"
                )

        # Check std drift
        if dist.std is not None and dist.max_drift_pct is not None:
            if dist.std != 0:
                drift_pct = abs(current_std - dist.std) / abs(dist.std) * 100
            else:
                drift_pct = 0
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
