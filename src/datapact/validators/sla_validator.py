"""
SLA validation - dataset-level checks like row count constraints.
"""

from typing import List, Tuple
import pandas as pd
from datapact.contracts import Contract


class SLAValidator:
    """
    Validate dataset SLAs such as row count thresholds.
    Produces WARN or ERROR severity violations.
    """

    def __init__(self, contract: Contract, df: pd.DataFrame):
        self.contract = contract
        self.df = df
        self.errors: List[str] = []

    def validate(self) -> Tuple[bool, List[str]]:
        self.errors = []

        total_rows = len(self.df)
        sla = self.contract.sla

        if sla.min_rows is not None and total_rows < sla.min_rows:
            self.errors.append(
                f"{sla.min_rows_severity}: SLA min_rows={sla.min_rows} "
                f"violated (found {total_rows})"
            )

        if sla.max_rows is not None and total_rows > sla.max_rows:
            self.errors.append(
                f"{sla.max_rows_severity}: SLA max_rows={sla.max_rows} "
                f"violated (found {total_rows})"
            )

        has_errors = any(err.startswith("ERROR") for err in self.errors)
        return not has_errors, self.errors
