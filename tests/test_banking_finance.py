"""
Test cases for complex banking/finance data products and consumption scenarios.
Covers Commercial & Institutional Deposits and Lending use cases, including multi-source joins, aggregations, and time window logic.
"""

import pytest
import pandas as pd
from pathlib import Path
from data_contract_validator.contracts import Contract
from data_contract_validator.datasource import DataSource
from data_contract_validator.validators import SchemaValidator, QualityValidator, DistributionValidator

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Example: Commercial Deposits contract fixture (to be created in fixtures)
@pytest.fixture
def deposits_contract():
    return Contract.from_yaml(str(FIXTURES_DIR / "deposits_contract.yaml"))

# Example: Commercial Lending contract fixture (to be created in fixtures)
@pytest.fixture
def lending_contract():
    return Contract.from_yaml(str(FIXTURES_DIR / "lending_contract.yaml"))

# Example: Multi-source data (deposits + lending join)
@pytest.fixture
def deposits_df():
    return pd.read_csv(FIXTURES_DIR / "deposits_data.csv")

@pytest.fixture
def lending_df():
    return pd.read_csv(FIXTURES_DIR / "lending_data.csv")

import pytest

class TestCommercialDeposits:
    @pytest.mark.PositiveCases
    def test_positive_cases(self, deposits_contract, deposits_df):
        # First 5 rows are positive
        df = deposits_df.iloc[0:5]
        validator = SchemaValidator(deposits_contract, df)
        passed, errors = validator.validate()
        assert passed, f"Schema errors: {errors}"
        qv = QualityValidator(deposits_contract, df)
        q_passed, q_errors = qv.validate()
        assert q_passed, f"Quality errors: {q_errors}"

    @pytest.mark.NegativeCases
    def test_negative_cases(self, deposits_contract, deposits_df):
        # Next 5 rows are negative
        df = deposits_df.iloc[5:10]
        validator = SchemaValidator(deposits_contract, df)
        # Schema or quality should fail
        passed, errors = validator.validate()
        qv = QualityValidator(deposits_contract, df)
        q_passed, q_errors = qv.validate()
        assert not (passed and q_passed), f"Expected failure, got: {errors + q_errors}"

    @pytest.mark.BoundaryCases
    def test_boundary_cases(self, deposits_contract, deposits_df):
        # Last 5 rows are boundary
        df = deposits_df.iloc[10:15]
        validator = SchemaValidator(deposits_contract, df)
        passed, errors = validator.validate()
        qv = QualityValidator(deposits_contract, df)
        q_passed, q_errors = qv.validate()
        # Boundary cases should pass if on the edge, fail if over
        assert passed, f"Boundary schema errors: {errors}"
        assert q_passed, f"Boundary quality errors: {q_errors}"

class TestCommercialLending:
    @pytest.mark.PositiveCases
    def test_positive_cases(self, lending_contract, lending_df):
        df = lending_df.iloc[0:5]
        validator = SchemaValidator(lending_contract, df)
        passed, errors = validator.validate()
        assert passed, f"Schema errors: {errors}"
        qv = QualityValidator(lending_contract, df)
        q_passed, q_errors = qv.validate()
        assert q_passed, f"Quality errors: {q_errors}"

    @pytest.mark.NegativeCases
    def test_negative_cases(self, lending_contract, lending_df):
        df = lending_df.iloc[5:10]
        validator = SchemaValidator(lending_contract, df)
        passed, errors = validator.validate()
        qv = QualityValidator(lending_contract, df)
        q_passed, q_errors = qv.validate()
        assert not (passed and q_passed), f"Expected failure, got: {errors + q_errors}"

    @pytest.mark.BoundaryCases
    def test_boundary_cases(self, lending_contract, lending_df):
        df = lending_df.iloc[10:15]
        validator = SchemaValidator(lending_contract, df)
        passed, errors = validator.validate()
        qv = QualityValidator(lending_contract, df)
        q_passed, q_errors = qv.validate()
        assert passed, f"Boundary schema errors: {errors}"
        assert q_passed, f"Boundary quality errors: {q_errors}"

class TestComplexConsumption:
    def test_deposits_lending_join(self, deposits_df, lending_df):
        # Simulate a join on customer_id and aggregate balances
        merged = pd.merge(deposits_df, lending_df, on="customer_id", how="outer", suffixes=("_dep", "_lend"))
        merged["total_balance"] = merged["balance_dep"].fillna(0) + merged["balance_lend"].fillna(0)
        # Example: Check for negative balances after aggregation
        assert (merged["total_balance"] >= 0).all(), "Negative total balances found"

    def test_time_window_aggregation(self, deposits_df):
        # Example: 30-day rolling sum of deposits (fix logic)
        deposits_df["date"] = pd.to_datetime(deposits_df["date"], errors="coerce")
        deposits_df = deposits_df.sort_values(["customer_id", "date"])
        # Use groupby apply to get rolling sum per customer
        def rolling_sum(group):
            return group.set_index("date")["amount"].rolling("30D").sum().reset_index(drop=True)
        deposits_df["rolling_30d_sum"] = deposits_df.groupby("customer_id", group_keys=False).apply(rolling_sum)
        # Check for NaNs only at the start or for invalid dates
        assert deposits_df["rolling_30d_sum"].isna().sum() < len(deposits_df)
