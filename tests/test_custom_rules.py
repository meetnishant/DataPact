"""Tests for custom rule plugins."""

import pandas as pd

from datapact.contracts import Contract
from datapact.validators import CustomRuleValidator


def test_custom_field_rule_plugin():
    contract_data = {
        "contract": {"name": "test", "version": "2.0.0"},
        "dataset": {"name": "test"},
        "fields": [
            {
                "name": "score",
                "type": "float",
                "rules": {
                    "custom": {
                        "field_max_value": {"value": 10}
                    }
                },
            }
        ],
    }
    contract = Contract._from_dict(contract_data)
    df = pd.DataFrame({"score": [5, 12]})

    validator = CustomRuleValidator(
        contract,
        df,
        ["tests.plugins.sample_plugin"],
    )
    passed, errors = validator.validate()
    assert not passed
    assert any("values > 10" in err for err in errors)


def test_custom_dataset_rule_plugin():
    contract_data = {
        "contract": {"name": "test", "version": "2.0.0"},
        "dataset": {"name": "test"},
        "custom_rules": [
            {
                "name": "dataset_min_rows",
                "config": {"value": 3},
                "severity": "WARN",
            }
        ],
        "fields": [
            {"name": "id", "type": "integer", "required": True},
        ],
    }
    contract = Contract._from_dict(contract_data)
    df = pd.DataFrame({"id": [1, 2]})

    validator = CustomRuleValidator(
        contract,
        df,
        ["tests.plugins.sample_plugin"],
    )
    passed, errors = validator.validate()
    assert passed
    assert any(err.startswith("WARN") for err in errors)
