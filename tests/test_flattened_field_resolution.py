"""Tests for flatten-aware field resolution in validators."""

import pandas as pd

from datapact.contracts import Contract
from datapact.validators import (
    CustomRuleValidator,
    DistributionValidator,
    QualityValidator,
    SchemaValidator,
)


def test_schema_validator_resolves_flattened_columns() -> None:
    contract_data = {
        "contract": {"name": "flat", "version": "2.0.0"},
        "dataset": {"name": "test"},
        "flatten": {"enabled": True, "separator": "__"},
        "fields": [
            {"name": "user.id", "type": "integer", "required": True},
        ],
    }
    contract = Contract._from_dict(contract_data)
    df = pd.DataFrame({"user__id": [1]})

    validator = SchemaValidator(contract, df)
    passed, errors = validator.validate()

    assert passed
    assert errors == []


def test_quality_validator_resolves_flattened_columns() -> None:
    contract_data = {
        "contract": {"name": "flat", "version": "2.0.0"},
        "dataset": {"name": "test"},
        "flatten": {"enabled": True, "separator": "__"},
        "fields": [
            {
                "name": "user.id",
                "type": "integer",
                "rules": {"not_null": True},
            },
        ],
    }
    contract = Contract._from_dict(contract_data)
    df = pd.DataFrame({"user__id": [None]})

    validator = QualityValidator(contract, df)
    passed, errors = validator.validate()

    assert not passed
    assert any("user.id" in err for err in errors)


def test_distribution_validator_resolves_flattened_columns() -> None:
    contract_data = {
        "contract": {"name": "flat", "version": "2.0.0"},
        "dataset": {"name": "test"},
        "flatten": {"enabled": True, "separator": "__"},
        "fields": [
            {
                "name": "metrics.score",
                "type": "float",
                "distribution": {"mean": 100, "max_drift_pct": 5},
            }
        ],
    }
    contract = Contract._from_dict(contract_data)
    df = pd.DataFrame({"metrics__score": [110.0, 110.0]})

    validator = DistributionValidator(contract, df)
    passed, warnings = validator.validate()

    assert not passed
    assert any("metrics.score" in warn for warn in warnings)


def test_custom_rule_validator_resolves_flattened_columns() -> None:
    contract_data = {
        "contract": {"name": "flat", "version": "2.0.0"},
        "dataset": {"name": "test"},
        "flatten": {"enabled": True, "separator": "__"},
        "fields": [
            {
                "name": "metrics.score",
                "type": "integer",
                "rules": {"custom": {"field_max_value": {"value": 10}}},
            },
        ],
    }
    contract = Contract._from_dict(contract_data)
    df = pd.DataFrame({"metrics__score": [20]})

    validator = CustomRuleValidator(
        contract,
        df,
        [],
    )
    # Manually add rule to avoid module import issues in test
    validator.rules = {
        "field_max_value": lambda series, config, field, df: (
            (
                False,
                f"Field '{field.name}' has {(series > config.get('value')).sum()} "
                f"values > {config.get('value')}",
            )
            if (series > config.get("value")).any()
            else (True, "")
        )
    }
    passed, errors = validator.validate()

    assert not passed
    assert any("values > 10" in err for err in errors)
