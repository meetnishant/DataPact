"""Tests for profiling utilities."""

from pathlib import Path

import pandas as pd

from datapact.profiling import profile_dataframe


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_profile_dataframe_basic():
    df = pd.read_csv(FIXTURES_DIR / "valid_customers.csv")
    contract = profile_dataframe(
        df,
        dataset_name="customers",
        contract_name="customers_profile",
    )

    assert contract["contract"]["name"] == "customers_profile"
    assert contract["dataset"]["name"] == "customers"

    fields = {field["name"]: field for field in contract["fields"]}
    customer_rules = fields["customer_id"]["rules"]
    assert fields["customer_id"]["required"] is True
    assert customer_rules["not_null"] is True
    assert customer_rules["unique"] is True

    signup_rules = fields["signup_date"]["rules"]
    assert signup_rules["regex"] == r"^\d{4}-\d{2}-\d{2}$"

    score_rules = fields["score"]["rules"]
    assert "min" in score_rules
    assert "max" in score_rules


def test_profile_dataframe_no_distribution():
    df = pd.read_csv(FIXTURES_DIR / "valid_customers.csv")
    contract = profile_dataframe(
        df,
        dataset_name="customers",
        contract_name="customers_profile",
        include_distribution=False,
    )

    fields = {field["name"]: field for field in contract["fields"]}
    assert "distribution" not in fields["score"]
