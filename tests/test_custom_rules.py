"""Tests for custom rule plugins."""

from pathlib import Path

import pandas as pd

from datapact.contracts import Contract
from datapact.validators import CustomRuleValidator


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_custom_field_rule_plugin():
    contract = Contract.from_yaml(str(FIXTURES_DIR / "custom_rules_contract.yaml"))
    df = pd.read_csv(FIXTURES_DIR / "custom_rules_data.csv")
    validator = CustomRuleValidator(
        contract,
        df,
        ["tests.plugins.sample_plugin"],
    )
    passed, errors = validator.validate()
    assert not passed
    assert any("values > 10" in err for err in errors)


def test_custom_dataset_rule_plugin():
    contract = Contract.from_yaml(str(FIXTURES_DIR / "custom_rules_contract.yaml"))
    df = pd.read_csv(FIXTURES_DIR / "custom_rules_data_ok.csv")
    validator = CustomRuleValidator(
        contract,
        df,
        ["tests.plugins.sample_plugin"],
    )
    passed, errors = validator.validate()
    assert passed
    assert any(err.startswith("WARN") for err in errors)
