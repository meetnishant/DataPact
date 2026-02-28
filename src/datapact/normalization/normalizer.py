"""Normalization entry point for dataframes."""

from typing import Optional
import logging
import warnings

import pandas as pd

from datapact.normalization.config import NormalizationConfig

logger = logging.getLogger(__name__)

# Modes that are defined in the config but not yet implemented.
_NOT_IMPLEMENTED_MODES = {"flatten"}


def normalize_dataframe(
    df: pd.DataFrame,
    config: Optional[NormalizationConfig] = None,
) -> pd.DataFrame:
    """Return a normalized dataframe.

    Currently only 'none' mode is supported. Other modes (e.g. 'flatten')
    are defined but not yet implemented and will emit a warning.
    """
    if config is None or config.mode == "none":
        return df

    if config.mode in _NOT_IMPLEMENTED_MODES:
        warnings.warn(
            f"Normalization mode '{config.mode}' is not yet implemented. "
            "Data will be returned unchanged. "
            "Track progress at: https://github.com/meetnishant/DataPact/issues",
            UserWarning,
            stacklevel=2,
        )
        return df

    logger.warning("Unknown normalization mode '%s'; returning data unchanged.", config.mode)
    return df
