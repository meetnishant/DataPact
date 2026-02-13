"""Tests for normalization scaffolding."""

import pandas as pd

from datapact.cli import _build_normalization_config
from datapact.contracts import Contract
from datapact.normalization import NormalizationConfig, normalize_dataframe


def test_normalize_dataframe_noop_default() -> None:
    df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})

    result = normalize_dataframe(df)

    assert result.equals(df)


def test_normalize_dataframe_noop_config() -> None:
    df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
    config = NormalizationConfig()

    result = normalize_dataframe(df, config)

    assert result.equals(df)


def test_build_normalization_config_disabled() -> None:
    data = {
        "contract": {"name": "norm", "version": "2.0.0"},
        "dataset": {"name": "customers"},
        "fields": [{"name": "id", "type": "integer"}],
    }
    contract = Contract._from_dict(data)

    config = _build_normalization_config(contract)

    assert config.mode == "none"


def test_build_normalization_config_flatten_enabled() -> None:
    data = {
        "contract": {"name": "norm", "version": "2.0.0"},
        "dataset": {"name": "customers"},
        "flatten": {"enabled": True, "separator": "__"},
        "fields": [{"name": "id", "type": "integer"}],
    }
    contract = Contract._from_dict(data)

    config = _build_normalization_config(contract)

    assert config.mode == "flatten"
    assert config.flatten_separator == "__"
