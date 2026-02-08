"""
Test cases for multi-table banking/finance data products and consumer-specific contracts.
Covers deposits and lending with strict vs aggregate consumers and multi-table joins.
"""

from pathlib import Path

import pandas as pd
import pytest

from data_contract_validator.contracts import Contract
from data_contract_validator.validators import SchemaValidator, QualityValidator

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def deposits_contract():
    return Contract.from_yaml(str(FIXTURES_DIR / "deposits_contract.yaml"))


@pytest.fixture
def deposits_agg_contract():
    return Contract.from_yaml(str(FIXTURES_DIR / "deposits_accounts_agg_contract.yaml"))


@pytest.fixture
def deposits_txn_contract():
    return Contract.from_yaml(str(FIXTURES_DIR / "deposits_transactions_contract.yaml"))


@pytest.fixture
def lending_contract():
    return Contract.from_yaml(str(FIXTURES_DIR / "lending_contract.yaml"))


@pytest.fixture
def lending_agg_contract():
    return Contract.from_yaml(str(FIXTURES_DIR / "lending_loans_agg_contract.yaml"))


@pytest.fixture
def lending_payments_contract():
    return Contract.from_yaml(str(FIXTURES_DIR / "lending_payments_contract.yaml"))


@pytest.fixture
def deposits_df():
    return pd.read_csv(FIXTURES_DIR / "deposits_data.csv", dtype={"open_date": str})


@pytest.fixture
def deposits_agg_df():
    return pd.read_csv(FIXTURES_DIR / "deposits_accounts_agg.csv", dtype={"open_date": str})


@pytest.fixture
def deposits_txn_df():
    return pd.read_csv(FIXTURES_DIR / "deposits_transactions.csv", dtype={"txn_date": str})


@pytest.fixture
def lending_df():
    return pd.read_csv(FIXTURES_DIR / "lending_data.csv", dtype={"origination_date": str})


@pytest.fixture
def lending_agg_df():
    return pd.read_csv(FIXTURES_DIR / "lending_loans_agg.csv", dtype={"origination_date": str})


@pytest.fixture
def lending_payments_df():
    return pd.read_csv(FIXTURES_DIR / "lending_payments.csv", dtype={"payment_date": str})


class TestDepositsAccountsStrict:
    @pytest.mark.PositiveCases
    def test_positive_cases(self, deposits_contract, deposits_df):
        df = deposits_df.iloc[0:5]
        passed, errors = SchemaValidator(deposits_contract, df).validate()
        assert passed, f"Schema errors: {errors}"
        q_passed, q_errors = QualityValidator(deposits_contract, df).validate()
        assert q_passed, f"Quality errors: {q_errors}"

    @pytest.mark.NegativeCases
    def test_negative_cases(self, deposits_contract, deposits_df):
        df = deposits_df.iloc[5:10]
        passed, errors = SchemaValidator(deposits_contract, df).validate()
        q_passed, q_errors = QualityValidator(deposits_contract, df).validate()
        assert not (passed and q_passed), f"Expected failure, got: {errors + q_errors}"

    @pytest.mark.BoundaryCases
    def test_boundary_cases(self, deposits_contract, deposits_df):
        df = deposits_df.iloc[10:15]
        passed, errors = SchemaValidator(deposits_contract, df).validate()
        q_passed, q_errors = QualityValidator(deposits_contract, df).validate()
        assert passed, f"Boundary schema errors: {errors}"
        assert q_passed, f"Boundary quality errors: {q_errors}"


class TestDepositsAccountsAggregate:
    def test_aggregate_consumer_contract(self, deposits_agg_contract, deposits_agg_df):
        passed, errors = SchemaValidator(deposits_agg_contract, deposits_agg_df).validate()
        assert passed, f"Schema errors: {errors}"
        q_passed, q_errors = QualityValidator(deposits_agg_contract, deposits_agg_df).validate()
        assert q_passed, f"Quality errors: {q_errors}"

        customer = deposits_agg_df["customer_id"]
        null_ratio = customer.isna().sum() / len(customer)
        non_null = customer.dropna()
        unique_ratio = non_null.nunique() / len(non_null)
        assert null_ratio <= 0.01, f"Null ratio too high: {null_ratio:.2%}"
        assert unique_ratio >= 0.99, f"Uniqueness ratio too low: {unique_ratio:.2%}"


class TestDepositsTransactions:
    @pytest.mark.PositiveCases
    def test_positive_cases(self, deposits_txn_contract, deposits_txn_df):
        df = deposits_txn_df.iloc[0:5]
        passed, errors = SchemaValidator(deposits_txn_contract, df).validate()
        assert passed, f"Schema errors: {errors}"
        q_passed, q_errors = QualityValidator(deposits_txn_contract, df).validate()
        assert q_passed, f"Quality errors: {q_errors}"

    @pytest.mark.NegativeCases
    def test_negative_cases(self, deposits_txn_contract, deposits_txn_df):
        df = deposits_txn_df.iloc[5:10]
        passed, errors = SchemaValidator(deposits_txn_contract, df).validate()
        q_passed, q_errors = QualityValidator(deposits_txn_contract, df).validate()
        assert not (passed and q_passed), f"Expected failure, got: {errors + q_errors}"

    @pytest.mark.BoundaryCases
    def test_boundary_cases(self, deposits_txn_contract, deposits_txn_df):
        df = deposits_txn_df.iloc[10:15]
        passed, errors = SchemaValidator(deposits_txn_contract, df).validate()
        q_passed, q_errors = QualityValidator(deposits_txn_contract, df).validate()
        assert passed, f"Boundary schema errors: {errors}"
        assert q_passed, f"Boundary quality errors: {q_errors}"


class TestLendingLoansStrict:
    @pytest.mark.PositiveCases
    def test_positive_cases(self, lending_contract, lending_df):
        df = lending_df.iloc[0:5]
        passed, errors = SchemaValidator(lending_contract, df).validate()
        assert passed, f"Schema errors: {errors}"
        q_passed, q_errors = QualityValidator(lending_contract, df).validate()
        assert q_passed, f"Quality errors: {q_errors}"

    @pytest.mark.NegativeCases
    def test_negative_cases(self, lending_contract, lending_df):
        df = lending_df.iloc[5:10]
        passed, errors = SchemaValidator(lending_contract, df).validate()
        q_passed, q_errors = QualityValidator(lending_contract, df).validate()
        assert not (passed and q_passed), f"Expected failure, got: {errors + q_errors}"

    @pytest.mark.BoundaryCases
    def test_boundary_cases(self, lending_contract, lending_df):
        df = lending_df.iloc[10:15]
        passed, errors = SchemaValidator(lending_contract, df).validate()
        q_passed, q_errors = QualityValidator(lending_contract, df).validate()
        assert passed, f"Boundary schema errors: {errors}"
        assert q_passed, f"Boundary quality errors: {q_errors}"


class TestLendingLoansAggregate:
    def test_aggregate_consumer_contract(self, lending_agg_contract, lending_agg_df):
        passed, errors = SchemaValidator(lending_agg_contract, lending_agg_df).validate()
        assert passed, f"Schema errors: {errors}"
        q_passed, q_errors = QualityValidator(lending_agg_contract, lending_agg_df).validate()
        assert q_passed, f"Quality errors: {q_errors}"

        customer = lending_agg_df["customer_id"]
        null_ratio = customer.isna().sum() / len(customer)
        non_null = customer.dropna()
        unique_ratio = non_null.nunique() / len(non_null)
        assert null_ratio <= 0.01, f"Null ratio too high: {null_ratio:.2%}"
        assert unique_ratio >= 0.99, f"Uniqueness ratio too low: {unique_ratio:.2%}"


class TestLendingPayments:
    @pytest.mark.PositiveCases
    def test_positive_cases(self, lending_payments_contract, lending_payments_df):
        df = lending_payments_df.iloc[0:5]
        passed, errors = SchemaValidator(lending_payments_contract, df).validate()
        assert passed, f"Schema errors: {errors}"
        q_passed, q_errors = QualityValidator(lending_payments_contract, df).validate()
        assert q_passed, f"Quality errors: {q_errors}"

    @pytest.mark.NegativeCases
    def test_negative_cases(self, lending_payments_contract, lending_payments_df):
        df = lending_payments_df.iloc[5:10]
        passed, errors = SchemaValidator(lending_payments_contract, df).validate()
        q_passed, q_errors = QualityValidator(lending_payments_contract, df).validate()
        assert not (passed and q_passed), f"Expected failure, got: {errors + q_errors}"

    @pytest.mark.BoundaryCases
    def test_boundary_cases(self, lending_payments_contract, lending_payments_df):
        df = lending_payments_df.iloc[10:15]
        passed, errors = SchemaValidator(lending_payments_contract, df).validate()
        q_passed, q_errors = QualityValidator(lending_payments_contract, df).validate()
        assert passed, f"Boundary schema errors: {errors}"
        assert q_passed, f"Boundary quality errors: {q_errors}"


class TestComplexConsumption:
    def test_deposits_position_join(self, deposits_df, deposits_txn_df):
        accounts = deposits_df[deposits_df["account_id"].notna()]
        valid_txns = pd.concat([deposits_txn_df.iloc[0:5], deposits_txn_df.iloc[10:15]], ignore_index=True)
        merged = valid_txns.merge(accounts, on=["account_id", "customer_id"], how="left")
        assert merged["balance"].notna().all(), "Unmatched transactions found"

    def test_time_window_aggregation(self, deposits_txn_df):
        valid_txns = pd.concat([deposits_txn_df.iloc[0:5], deposits_txn_df.iloc[10:15]], ignore_index=True)
        valid_txns["txn_date"] = pd.to_datetime(valid_txns["txn_date"], errors="coerce")
        valid_txns = valid_txns.dropna(subset=["txn_date"]).sort_values(["customer_id", "txn_date"])

        rolling = (
            valid_txns.set_index("txn_date")
            .groupby("customer_id")["amount"]
            .rolling("30D", min_periods=1)
            .sum()
            .reset_index(level=0, drop=True)
        )
        valid_txns["rolling_30d_sum"] = rolling.values
        assert valid_txns["rolling_30d_sum"].isna().sum() < len(valid_txns)
