"""Normalization entry point for dataframes."""

from typing import Optional

import pandas as pd

from datapact.normalization.config import NormalizationConfig


def normalize_dataframe(
    df: pd.DataFrame,
    config: Optional[NormalizationConfig] = None,
) -> pd.DataFrame:
    """Return a normalized dataframe (noop for now)."""
    if config is None or config.mode == "none":
        return df

    # Placeholder for future modes (e.g., flatten).
    return df
